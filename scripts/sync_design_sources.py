#!/usr/bin/env python3

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple

from check_design_sources import compare_source_tree, path_is_in_scope
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


def require_clean_task_branch(repo_root: Path) -> str:
    branch = _run_git(repo_root, "branch", "--show-current")
    if not branch or branch in {"main", "master"}:
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


def _file_records(paths: Iterable[Path], root: Path) -> List[Dict[str, Any]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
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


def _run_renderer_if_present(repo_root: Path, staged_repo: Path) -> bool:
    renderer = repo_root / "scripts/render_frontend_design_plugin.py"
    if not renderer.is_file():
        return False
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
    return True


def _remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def _replace_paths_atomically(
    replacements: Iterable[Tuple[Path, Path]],
    backup_root: Path,
) -> None:
    backup_root.mkdir(parents=True, exist_ok=True)
    states: List[Dict[str, Any]] = []
    try:
        for index, (staged, target) in enumerate(replacements):
            target.parent.mkdir(parents=True, exist_ok=True)
            backup = backup_root / str(index)
            if target.exists() or target.is_symlink():
                os.replace(target, backup)
            else:
                backup = None
            state = {"target": target, "backup": backup, "installed": False}
            states.append(state)
            os.replace(staged, target)
            state["installed"] = True
    except Exception:
        for state in reversed(states):
            target = state["target"]
            backup = state["backup"]
            if state["installed"]:
                _remove_path(target)
            if backup is not None and backup.exists():
                _remove_path(target)
                os.replace(backup, target)
        raise


def sync_source(
    repo_root: Path,
    source_id: str,
    archive_path: Path,
) -> Dict[str, Any]:
    require_clean_task_branch(repo_root)
    registry = load_json(repo_root / "design-stack/sources.json")
    lock = load_json(repo_root / "design-stack/sources.lock.json")
    provenance = load_json(repo_root / "design-stack/provenance.json")
    validate_registry(registry)
    source = _source_by_id(registry, source_id)
    if source["distribution"] != "vendored":
        raise ValidationError(f"source is not approved for vendored sync: {source_id}")

    with tempfile.TemporaryDirectory(
        prefix="frontend-design-sync-", dir=str(repo_root.parent)
    ) as temp_dir:
        temp_root = Path(temp_dir)
        extracted_root = extract_reviewed_tar(
            archive_path,
            temp_root / "extracted",
            source_id,
            source["revision"],
        )
        change_report = compare_source_tree(repo_root, source_id, extracted_root)
        selected_files = _selected_files(extracted_root, source)
        file_records = _file_records(selected_files, extracted_root)
        _assign_materialization(source, lock, provenance, file_records)
        new_lock = copy.deepcopy(lock)
        locked_source = _locked_source_by_id(new_lock, source_id)
        locked_source["files"] = file_records
        catalog = _catalog_for_source(
            source_id, extracted_root, file_records
        )
        if catalog is not None:
            catalog_name, entries = catalog
            new_lock["catalogs"][catalog_name] = entries
        _enforce_provenance_gate(source, new_lock, provenance, file_records)
        validate_lock(registry, new_lock, metadata_only=True)
        validate_provenance(registry, new_lock, provenance)

        staged_repo = temp_root / "staged-repo"
        shutil.copytree(repo_root / "design-stack", staged_repo / "design-stack")
        if (repo_root / "plugins").is_dir():
            shutil.copytree(repo_root / "plugins", staged_repo / "plugins")
        staged_vendor = staged_repo / source["destination"]
        materialized_paths = {
            record["path"]
            for record in file_records
            if record["materialization"] == "vendored"
        }
        _copy_selected_files(
            [
                path
                for path in selected_files
                if path.relative_to(extracted_root).as_posix() in materialized_paths
            ],
            extracted_root,
            staged_vendor,
        )
        staged_lock = staged_repo / "design-stack/sources.lock.json"
        _write_json(staged_lock, new_lock)
        validate_repository(staged_repo, metadata_only=False)
        plugin_rendered = _run_renderer_if_present(repo_root, staged_repo)

        replacements: List[Tuple[Path, Path]] = [
            (staged_lock, repo_root / "design-stack/sources.lock.json"),
            (staged_vendor, repo_root / source["destination"]),
        ]
        if plugin_rendered:
            replacements.append(
                (
                    staged_repo / "plugins/frontend-design-pack",
                    repo_root / "plugins/frontend-design-pack",
                )
            )
        _replace_paths_atomically(replacements, temp_root / "rollback")

    return {
        "source_id": source_id,
        "revision": source["revision"],
        "files": len(file_records),
        "plugin_rendered": plugin_rendered,
        "changes": change_report,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a reviewed immutable tar archive into the frontend design stack."
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source", required=True)
    parser.add_argument("--archive", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = (
        Path(args.repo_root).expanduser().resolve()
        if args.repo_root
        else Path(__file__).resolve().parents[1]
    )
    try:
        report = sync_source(
            repo_root,
            args.source,
            Path(args.archive).expanduser().resolve(),
        )
    except (OSError, ValidationError) as error:
        print(f"Design source sync failed: {error}")
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
