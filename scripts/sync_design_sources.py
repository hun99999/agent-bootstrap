#!/usr/bin/env python3

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple

from check_design_sources import compare_source_tree, path_is_in_scope
from check_private_paths import scan_repository_paths
from design_stack import (
    ValidationError,
    load_json,
    parse_skill_frontmatter,
    sha256_file,
    validate_lock,
    validate_provenance,
    validate_registry,
    validate_repository,
)


MAX_ARCHIVE_FILE_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_TOTAL_BYTES = 512 * 1024 * 1024
HIGH_CONFIDENCE_SECRET_PATTERNS = (
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


def _safe_archive_name(name: str, is_directory: bool) -> str:
    if "\\" in name:
        raise ValidationError(f"archive path uses a backslash: {name}")
    canonical_input = name.rstrip("/") if is_directory else name
    if not canonical_input:
        raise ValidationError("archive contains an empty path")
    path = PurePosixPath(canonical_input)
    if (
        path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or path.as_posix() != canonical_input
    ):
        raise ValidationError(f"unsafe or non-canonical archive path: {name}")
    return canonical_input


def extract_reviewed_tar(
    archive_path: Path,
    destination: Path,
    source_id: str,
    revision: str,
    mode_inventory: Optional[Dict[str, str]] = None,
) -> Path:
    if not archive_path.is_file():
        raise ValidationError(f"explicit local archive does not exist: {archive_path}")
    expected_root = f"{source_id}-{revision}"
    destination.mkdir(parents=True, exist_ok=True)
    extracted_root = destination / expected_root
    seen: Set[str] = set()
    total_bytes = 0

    try:
        archive = tarfile.open(archive_path, mode="r:*")
    except (tarfile.TarError, OSError) as error:
        raise ValidationError(f"invalid tar archive: {archive_path}: {error}") from error

    with archive:
        for member in archive:
            canonical_name = _safe_archive_name(member.name, member.isdir())
            if canonical_name in seen:
                raise ValidationError(f"duplicate archive member: {canonical_name}")
            seen.add(canonical_name)
            if canonical_name == expected_root:
                if not member.isdir():
                    raise ValidationError("archive revision prefix must be a directory")
                extracted_root.mkdir(parents=True, exist_ok=True)
                continue
            prefix = expected_root + "/"
            if not canonical_name.startswith(prefix):
                raise ValidationError(
                    f"archive member is outside expected source/revision prefix {expected_root}: "
                    f"{canonical_name}"
                )
            relative_name = canonical_name[len(prefix) :]
            relative_path = PurePosixPath(relative_name)
            target = extracted_root.joinpath(*relative_path.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise ValidationError(
                    f"archive links and special member types are not allowed: {canonical_name}"
                )
            if member.size < 0 or member.size > MAX_ARCHIVE_FILE_BYTES:
                raise ValidationError(f"archive member size is not allowed: {canonical_name}")
            total_bytes += member.size
            if total_bytes > MAX_ARCHIVE_TOTAL_BYTES:
                raise ValidationError("archive exceeds the reviewed import size limit")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValidationError(f"cannot read archive member: {canonical_name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as output:
                shutil.copyfileobj(stream, output)
            target.chmod(0o644)
            if mode_inventory is not None:
                mode_inventory[relative_name] = f"{member.mode & 0o7777:04o}"

    if not extracted_root.is_dir():
        raise ValidationError(
            f"archive is missing expected source/revision prefix: {expected_root}"
        )
    return extracted_root


def _run_git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValidationError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def _origin_default_branch(repo_root: Path) -> Optional[str]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "symbolic-ref",
            "--quiet",
            "--short",
            "refs/remotes/origin/HEAD",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 1:
        return None
    if result.returncode != 0:
        raise ValidationError(
            result.stderr.strip() or "cannot resolve the origin default branch"
        )
    reference = result.stdout.strip()
    prefix = "origin/"
    if not reference.startswith(prefix) or reference == prefix:
        raise ValidationError(f"invalid origin default branch reference: {reference}")
    return reference[len(prefix) :]


def require_clean_task_branch(repo_root: Path) -> str:
    branch = _run_git(repo_root, "branch", "--show-current")
    default_branches = {"main", "master", "trunk", "develop"}
    origin_default = _origin_default_branch(repo_root)
    if origin_default is not None:
        default_branches.add(origin_default)
    if not branch or branch in default_branches:
        raise ValidationError("design sync requires a non-default task branch")
    status = _run_git(repo_root, "status", "--porcelain", "--untracked-files=all")
    if status:
        raise ValidationError("design sync requires a clean task branch")
    return branch


def _source_by_id(registry: Mapping[str, Any], source_id: str) -> Mapping[str, Any]:
    for source in registry["sources"]:
        if source["id"] == source_id:
            return source
    raise ValidationError(f"unknown source: {source_id}")


def _locked_source_by_id(lock: Mapping[str, Any], source_id: str) -> Dict[str, Any]:
    for source in lock["sources"]:
        if source["id"] == source_id:
            return source
    raise ValidationError(f"source is missing from lock: {source_id}")


def _selected_files(
    extracted_root: Path,
    source: Mapping[str, Any],
) -> List[Path]:
    selected = []
    for path in sorted(extracted_root.rglob("*")):
        if not path.is_file():
            continue
        relative_path = path.relative_to(extracted_root).as_posix()
        if path_is_in_scope(relative_path, source):
            selected.append(path)
    notice_path = extracted_root / source["license"]["notice_path"]
    if source["license"]["status"] == "verified" and notice_path not in selected:
        raise ValidationError(
            f"archive is missing required license notice: {source['license']['notice_path']}"
        )
    if not selected:
        raise ValidationError(f"archive contains no files in scope for {source['id']}")
    return selected


def _file_records(
    paths: Iterable[Path],
    root: Path,
    mode_inventory: Mapping[str, str],
) -> List[Dict[str, Any]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "mode": mode_inventory[path.relative_to(root).as_posix()],
            "sha256": sha256_file(path),
        }
        for path in paths
    ]


def _assign_materialization(
    source: Mapping[str, Any],
    lock: Mapping[str, Any],
    provenance: Mapping[str, Any],
    files: Iterable[Dict[str, Any]],
) -> None:
    decisions = {
        (record["source_id"], record["upstream_path"]): record["decision"]
        for record in provenance["records"]
    }
    evidence_paths = _contract_paths(lock, source["id"])
    if source["license"]["notice_path"]:
        evidence_paths.add(source["license"]["notice_path"])
    for file_record in files:
        path = file_record["path"]
        decision = decisions.get((source["id"], path))
        if path in evidence_paths:
            file_record["materialization"] = "vendored"
        elif decision == "included":
            file_record["materialization"] = "vendored"
        else:
            file_record["materialization"] = "metadata-only"


def _catalog_for_source(
    source_id: str,
    extracted_root: Path,
    files: Iterable[Mapping[str, Any]],
) -> Optional[Tuple[str, List[Dict[str, Any]]]]:
    file_map = {record["path"]: record for record in files}
    if source_id == "mengto-skills":
        entries: List[Dict[str, Any]] = []
        names: Set[str] = set()
        for relative_path in sorted(
            path for path in file_map if path.endswith("/SKILL.md")
        ):
            metadata = parse_skill_frontmatter(
                (extracted_root / relative_path).read_text(encoding="utf-8"),
                relative_path,
            )
            name = metadata["name"]
            if name in names:
                raise ValidationError(f"duplicate skill name in archive: {name}")
            names.add(name)
            entries.append(
                {
                    "source_id": source_id,
                    "name": name,
                    "description": metadata["description"],
                    "path": relative_path,
                    "sha256": file_map[relative_path]["sha256"],
                }
            )
        if not entries:
            raise ValidationError("MengTo archive is missing required SKILL.md files")
        return "mengto_skills", entries
    if source_id == "awesome-design-md":
        entries = []
        names = set()
        for relative_path in sorted(
            path for path in file_map if path.endswith("/DESIGN.md")
        ):
            name = Path(relative_path).parent.name
            if name in names:
                raise ValidationError(f"duplicate DESIGN.md name in archive: {name}")
            names.add(name)
            entries.append(
                {
                    "source_id": source_id,
                    "name": name,
                    "path": relative_path,
                    "sha256": file_map[relative_path]["sha256"],
                    "authority": "third-party-analysis",
                }
            )
        if not entries:
            raise ValidationError("Awesome DESIGN.md archive is missing DESIGN.md files")
        return "design_md", entries
    return None


def _contract_paths(lock: Mapping[str, Any], source_id: str) -> Set[str]:
    paths: Set[str] = set()
    for contract in lock.get("contracts", {}).values():
        if contract.get("source_id") == source_id:
            paths.add(contract["path"])
    return paths


def _enforce_provenance_gate(
    source: Mapping[str, Any],
    lock: Mapping[str, Any],
    provenance: Mapping[str, Any],
    files: Iterable[Mapping[str, Any]],
) -> None:
    records = {
        (record["source_id"], record["upstream_path"]): record
        for record in provenance["records"]
    }
    evidence_paths = _contract_paths(lock, source["id"])
    if source["license"]["notice_path"]:
        evidence_paths.add(source["license"]["notice_path"])
    for file_record in files:
        path = file_record["path"]
        if path in evidence_paths:
            continue
        record = records.get((source["id"], path))
        if record is None:
            raise ValidationError(f"imported file is missing provenance: {path}")
        if record["sha256"] != file_record["sha256"]:
            raise ValidationError(f"imported file SHA-256 differs from provenance: {path}")
        if record["decision"] not in {"included", "mapped-to-official"}:
            raise ValidationError(
                f"imported file is not approved for distribution by provenance: {path}"
            )


def _copy_selected_files(
    selected_files: Iterable[Path],
    extracted_root: Path,
    destination: Path,
) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for source_path in selected_files:
        relative = source_path.relative_to(extracted_root)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target)
        target.chmod(0o644)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _run_renderer(repo_root: Path, staged_repo: Path) -> None:
    renderer = repo_root / "scripts/render_frontend_design_plugin.py"
    if not renderer.is_file():
        raise ValidationError(
            "frontend design renderer is required before approved source sync"
        )
    plugin_root = staged_repo / "plugins/frontend-design-pack"
    result = subprocess.run(
        [
            sys.executable,
            str(renderer),
            "--repo-root",
            str(staged_repo),
            "--plugin-root",
            str(plugin_root),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValidationError(
            "frontend design plugin render failed: "
            + (result.stdout + result.stderr).strip()
        )


def _regular_files(root: Path) -> List[Path]:
    if not root.is_dir():
        raise ValidationError(f"missing rendered plugin directory: {root}")
    files: List[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValidationError(f"rendered plugin must not contain symlinks: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValidationError(f"rendered plugin contains a special file: {path}")
        files.append(path)
    return files


def _validate_plugin_output(staged_repo: Path) -> None:
    plugin_root = staged_repo / "plugins/frontend-design-pack"
    _regular_files(plugin_root)
    manifests = []
    for relative_path in (
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
    ):
        manifest_path = plugin_root / relative_path
        manifest = load_json(manifest_path)
        if manifest.get("name") != "frontend-design-pack":
            raise ValidationError(
                f"rendered plugin manifest has an invalid name: {manifest_path}"
            )
        if not isinstance(manifest.get("version"), str) or not manifest["version"]:
            raise ValidationError(
                f"rendered plugin manifest is missing a version: {manifest_path}"
            )
        manifests.append(manifest)
    if manifests[0]["version"] != manifests[1]["version"]:
        raise ValidationError("Codex and Claude plugin versions must match")
    native_skills = sorted(plugin_root.glob("skills/*/SKILL.md"))
    nested_skill_files = sorted(plugin_root.rglob("SKILL.md"))
    if len(native_skills) != 1 or native_skills != nested_skill_files:
        raise ValidationError(
            "rendered plugin must contain exactly one native SKILL.md"
        )
    metadata = parse_skill_frontmatter(
        native_skills[0].read_text(encoding="utf-8"),
        native_skills[0].relative_to(plugin_root).as_posix(),
    )
    if metadata["name"] != "frontend-design":
        raise ValidationError("rendered native skill must be named frontend-design")


def _validate_staged_safety(staged_repo: Path) -> None:
    roots = [
        staged_repo / "design-stack",
        staged_repo / "plugins/frontend-design-pack",
    ]
    paths = [path for root in roots for path in _regular_files(root)]
    private_findings = scan_repository_paths(staged_repo, paths)
    if private_findings:
        first = private_findings[0]
        raise ValidationError(
            f"staged private-path or secret-assignment safety scan failed: "
            f"{first.path}:{first.line}: {first.label}"
        )
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in HIGH_CONFIDENCE_SECRET_PATTERNS:
            if pattern.search(text):
                raise ValidationError(
                    f"staged high-confidence secret safety scan failed: {path}"
                )


def _validate_staged_outputs(staged_repo: Path) -> None:
    validate_repository(staged_repo, metadata_only=False)
    _validate_plugin_output(staged_repo)
    _validate_staged_safety(staged_repo)


def _remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def _safe_transaction_path(root: Path, relative_path: str) -> Path:
    posix_path = PurePosixPath(relative_path)
    if (
        posix_path.is_absolute()
        or ".." in posix_path.parts
        or "." in posix_path.parts
        or posix_path.as_posix() != relative_path
    ):
        raise ValidationError(f"unsafe transaction path: {relative_path}")
    target = root.joinpath(*posix_path.parts)
    root_resolved = root.resolve()
    target_resolved = target.resolve(strict=False)
    if target_resolved != root_resolved and root_resolved not in target_resolved.parents:
        raise ValidationError(f"transaction path escapes its allowed root: {relative_path}")
    return target


def _mark_transaction_committed(transaction_root: Path) -> None:
    marker = transaction_root / "committed"
    descriptor = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, b"committed\n")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _recover_incomplete_transaction(
    transaction_root: Path,
    allowed_root: Path,
) -> None:
    journal_path = transaction_root / "journal.json"
    if not transaction_root.exists():
        return
    committed_marker = transaction_root / "committed"
    if committed_marker.is_symlink() or (
        committed_marker.exists() and not committed_marker.is_file()
    ):
        raise ValidationError(
            f"design sync commit marker must be a real file: {committed_marker}"
        )
    if not journal_path.exists():
        if committed_marker.exists():
            committed_marker.unlink()
        if any(transaction_root.iterdir()):
            raise ValidationError(
                f"design sync transaction journal is missing: {journal_path}"
            )
        transaction_root.rmdir()
        return
    journal = load_json(journal_path)
    if journal.get("schema_version") != 1 or not isinstance(
        journal.get("targets"), list
    ):
        raise ValidationError(f"invalid design sync transaction journal: {journal_path}")
    committed = committed_marker.exists()
    for state in reversed(journal["targets"]):
        if not isinstance(state, dict) or not isinstance(state.get("had_target"), bool):
            raise ValidationError(f"invalid transaction target in {journal_path}")
        target = _safe_transaction_path(allowed_root, state.get("target", ""))
        backup = _safe_transaction_path(
            transaction_root, state.get("backup", "")
        )
        if backup.is_symlink():
            raise ValidationError(f"transaction backup must not be a symlink: {backup}")
        if committed:
            if not (target.exists() or target.is_symlink()):
                raise ValidationError(f"committed sync target is missing: {target}")
        else:
            if state["had_target"]:
                if backup.exists():
                    _remove_path(target)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(backup, target)
                elif not (target.exists() or target.is_symlink()):
                    raise ValidationError(
                        f"cannot recover missing target and backup: {target}"
                    )
            else:
                _remove_path(target)
    backups_root = transaction_root / "backups"
    if backups_root.is_symlink():
        raise ValidationError(f"transaction backups must not be a symlink: {backups_root}")
    if backups_root.exists():
        if not backups_root.is_dir():
            raise ValidationError(
                f"transaction backups must be a directory: {backups_root}"
            )
        shutil.rmtree(backups_root)
    journal_path.unlink(missing_ok=True)
    committed_marker.unlink(missing_ok=True)
    transaction_root.rmdir()


def _replace_paths_atomically(
    replacements: Iterable[Tuple[Path, Path]],
    transaction_root: Path,
    allowed_root: Path,
) -> None:
    if transaction_root.exists():
        _recover_incomplete_transaction(transaction_root, allowed_root)
    states: List[Dict[str, Any]] = []
    replacement_list = list(replacements)
    for index, (_, target) in enumerate(replacement_list):
        target_relative = target.resolve(strict=False).relative_to(
            allowed_root.resolve()
        ).as_posix()
        states.append(
            {
                "target": target_relative,
                "backup": f"backups/{index}",
                "had_target": target.exists() or target.is_symlink(),
            }
        )
    transaction_root.mkdir(parents=True)
    _write_json(
        transaction_root / "journal.json",
        {"schema_version": 1, "targets": states},
    )
    try:
        for state, (_, target) in zip(states, replacement_list):
            target.parent.mkdir(parents=True, exist_ok=True)
            backup = _safe_transaction_path(transaction_root, state["backup"])
            backup.parent.mkdir(parents=True, exist_ok=True)
            if state["had_target"]:
                os.replace(target, backup)
        for staged, target in replacement_list:
            os.replace(staged, target)
        _mark_transaction_committed(transaction_root)
    except BaseException:
        _recover_incomplete_transaction(transaction_root, allowed_root)
        raise
    _recover_incomplete_transaction(transaction_root, allowed_root)


def sync_sources(
    repo_root: Path,
    archive_paths: Mapping[str, Path],
) -> Dict[str, Any]:
    if not archive_paths:
        raise ValidationError("design sync requires at least one source archive")
    git_transaction_path = Path(
        _run_git(repo_root, "rev-parse", "--git-path", "frontend-design-sync")
    )
    transaction_root = (
        git_transaction_path
        if git_transaction_path.is_absolute()
        else repo_root / git_transaction_path
    )
    _recover_incomplete_transaction(transaction_root, repo_root)
    require_clean_task_branch(repo_root)
    registry = load_json(repo_root / "design-stack/sources.json")
    lock = load_json(repo_root / "design-stack/sources.lock.json")
    provenance = load_json(repo_root / "design-stack/provenance.json")
    validate_registry(registry)
    validate_lock(registry, lock, metadata_only=True)
    validate_provenance(registry, lock, provenance)
    sources = {
        source_id: _source_by_id(registry, source_id)
        for source_id in archive_paths
    }
    for source_id, source in sources.items():
        if source["distribution"] != "vendored":
            raise ValidationError(
                f"source is not approved for vendored sync: {source_id}"
            )

    with tempfile.TemporaryDirectory(
        prefix="frontend-design-sync-", dir=str(repo_root.parent)
    ) as temp_dir:
        temp_root = Path(temp_dir)
        new_lock = copy.deepcopy(lock)
        prepared: Dict[str, Dict[str, Any]] = {}
        for source_id in sorted(archive_paths):
            source = sources[source_id]
            mode_inventory: Dict[str, str] = {}
            extracted_root = extract_reviewed_tar(
                archive_paths[source_id],
                temp_root / "extracted" / source_id,
                source_id,
                source["revision"],
                mode_inventory,
            )
            change_report = compare_source_tree(
                repo_root,
                source_id,
                extracted_root,
                mode_overrides=mode_inventory,
            )
            selected_files = _selected_files(extracted_root, source)
            file_records = _file_records(
                selected_files,
                extracted_root,
                mode_inventory,
            )
            _assign_materialization(source, new_lock, provenance, file_records)
            locked_source = _locked_source_by_id(new_lock, source_id)
            locked_source["files"] = file_records
            catalog = _catalog_for_source(
                source_id, extracted_root, file_records
            )
            if catalog is not None:
                catalog_name, entries = catalog
                new_lock["catalogs"][catalog_name] = entries
            _enforce_provenance_gate(
                source, new_lock, provenance, file_records
            )
            prepared[source_id] = {
                "source": source,
                "extracted_root": extracted_root,
                "selected_files": selected_files,
                "file_records": file_records,
                "changes": change_report,
            }
        validate_lock(registry, new_lock, metadata_only=True)
        validate_provenance(registry, new_lock, provenance)

        staged_repo = temp_root / "staged-repo"
        shutil.copytree(repo_root / "design-stack", staged_repo / "design-stack")
        if (repo_root / "plugins").is_dir():
            shutil.copytree(repo_root / "plugins", staged_repo / "plugins")
        staged_vendors: Dict[str, Path] = {}
        for source_id in sorted(prepared):
            item = prepared[source_id]
            source = item["source"]
            extracted_root = item["extracted_root"]
            file_records = item["file_records"]
            materialized_paths = {
                record["path"]
                for record in file_records
                if record["materialization"] == "vendored"
            }
            staged_vendor = staged_repo / source["destination"]
            _copy_selected_files(
                [
                    path
                    for path in item["selected_files"]
                    if path.relative_to(extracted_root).as_posix()
                    in materialized_paths
                ],
                extracted_root,
                staged_vendor,
            )
            staged_vendors[source_id] = staged_vendor
        staged_lock = staged_repo / "design-stack/sources.lock.json"
        _write_json(staged_lock, new_lock)
        validate_repository(staged_repo, metadata_only=False)
        _run_renderer(repo_root, staged_repo)
        _validate_staged_outputs(staged_repo)
        plugin_rendered = True

        replacements: List[Tuple[Path, Path]] = [
            (staged_lock, repo_root / "design-stack/sources.lock.json"),
        ]
        replacements.extend(
            (
                staged_vendors[source_id],
                repo_root / prepared[source_id]["source"]["destination"],
            )
            for source_id in sorted(prepared)
        )
        replacements.append(
            (
                staged_repo / "plugins/frontend-design-pack",
                repo_root / "plugins/frontend-design-pack",
            )
        )
        _replace_paths_atomically(
            replacements,
            transaction_root,
            repo_root,
        )

    return {
        "sources": [
            {
                "source_id": source_id,
                "revision": prepared[source_id]["source"]["revision"],
                "files": len(prepared[source_id]["file_records"]),
                "changes": prepared[source_id]["changes"],
            }
            for source_id in sorted(prepared)
        ],
        "plugin_rendered": plugin_rendered,
    }


def sync_source(
    repo_root: Path,
    source_id: str,
    archive_path: Path,
) -> Dict[str, Any]:
    batch_report = sync_sources(repo_root, {source_id: archive_path})
    report = dict(batch_report["sources"][0])
    report["plugin_rendered"] = batch_report["plugin_rendered"]
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a reviewed immutable tar archive into the frontend design stack."
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="Source id. Repeat with --archive for an atomic batch bootstrap.",
    )
    parser.add_argument(
        "--archive",
        action="append",
        required=True,
        help="Explicit local tar archive paired by position with --source.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = (
        Path(args.repo_root).expanduser().resolve()
        if args.repo_root
        else Path(__file__).resolve().parents[1]
    )
    try:
        if len(args.source) != len(args.archive):
            raise ValidationError(
                "every --source must have one positionally paired --archive"
            )
        if len(set(args.source)) != len(args.source):
            raise ValidationError("duplicate --source values are not allowed")
        report = sync_sources(
            repo_root,
            {
                source_id: Path(archive).expanduser().resolve()
                for source_id, archive in zip(args.source, args.archive)
            },
        )
    except (OSError, ValidationError) as error:
        print(f"Design source sync failed: {error}")
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
