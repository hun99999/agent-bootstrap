#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Mapping

from design_stack import (
    ValidationError,
    load_json,
    parse_skill_frontmatter,
    sha256_file,
    validate_repository,
)


PLUGIN_NAME = "frontend-design-pack"
PLUGIN_VERSION = "0.1.0"
PLUGIN_DESCRIPTION = (
    "One evidence-first frontend design router with reviewed MengTo procedures, "
    "official quality guidance, and labeled DESIGN.md inspiration."
)
PLUGIN_AUTHOR = {
    "name": "Hun",
    "email": "48903443+hun99999@users.noreply.github.com",
}
PLUGIN_REPOSITORY = "https://github.com/hun99999/agent-bootstrap"
PLUGIN_KEYWORDS = [
    "frontend-design",
    "product-design",
    "user-interface",
    "user-experience",
    "accessibility",
    "responsive-design",
    "design-system",
]
CODEX_INTERFACE = {
    "displayName": "Frontend Design Pack",
    "shortDescription": "Evidence-first frontend design workflows",
    "longDescription": (
        "Shape, explore, implement, review, write, and harden frontend experiences "
        "with one evidence-first router and a reviewed reference corpus."
    ),
    "developerName": "Hun",
    "category": "Creativity",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": [
        "Shape a frontend brief and choose the right design workflow",
        "Explore three evidence-backed visual directions",
        "Review this frontend for UX, accessibility, and polish",
    ],
}
PLUGIN_ROOT = Path("plugins/frontend-design-pack")
SKILL_ROOT_DEPENDENCY_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_:/.-])"
    r"(?:<skill-root>/|<skills-root>/[A-Za-z0-9._-]+/)"
    r"((?:references|scripts|assets)/[A-Za-z0-9._/-]+)"
)
REFERENCE_DEPENDENCY_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_:/.-])(references/[A-Za-z0-9._/-]+)"
)
MARKDOWN_DEPENDENCY_PATTERN = re.compile(
    r"\]\(((?:references|scripts|assets)/[A-Za-z0-9._/-]+)\)"
)
MIT_LICENSE = """MIT License

Copyright (c) 2026 Hun

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the reviewed frontend design corpus as one dual-runtime plugin."
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root. Defaults to the parent of this script directory.",
    )
    parser.add_argument(
        "--plugin-root",
        default=None,
        help="Output root. Defaults to plugins/frontend-design-pack in the repository.",
    )
    return parser.parse_args()


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    path.chmod(0o644)


def _write_text(path: Path, content: str) -> None:
    _write_bytes(path, content.encode("utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    _write_text(
        path,
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )


def _prepare_empty_output(repo_root: Path, plugin_root: Path) -> None:
    if plugin_root.is_symlink():
        raise ValidationError(f"plugin output must not be a symlink: {plugin_root}")
    if plugin_root.resolve() == repo_root.resolve():
        raise ValidationError("plugin output must not replace the repository root")
    if plugin_root.exists():
        if not plugin_root.is_dir():
            raise ValidationError(f"plugin output is not a directory: {plugin_root}")
        if any(plugin_root.iterdir()):
            raise ValidationError(f"staged plugin output must be empty: {plugin_root}")
        return
    plugin_root.mkdir(parents=True)


def _remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def _validated_output_path(repo_root: Path, requested_root: Path) -> Path:
    requested_root = requested_root.expanduser()
    if requested_root.is_symlink():
        raise ValidationError(f"plugin output must not be a symlink: {requested_root}")
    if not requested_root.is_absolute():
        requested_root = Path.cwd() / requested_root
    plugin_root = requested_root.resolve(strict=False)
    if plugin_root == repo_root or plugin_root in repo_root.parents:
        raise ValidationError("plugin output must not be the repository root or an ancestor")
    try:
        plugin_root.relative_to(repo_root)
    except ValueError:
        return plugin_root
    approved_root = (repo_root / PLUGIN_ROOT).resolve(strict=False)
    if plugin_root != approved_root:
        raise ValidationError(
            f"in-repository output must use the approved plugin destination: {approved_root}"
        )
    return plugin_root


def _transaction_root(plugin_root: Path) -> Path:
    return plugin_root.parent / f".{plugin_root.name}.render-transaction"


def _mark_render_transaction_committed(transaction_root: Path) -> None:
    marker = transaction_root / "committed"
    descriptor = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, b"committed\n")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _recover_render_transaction(plugin_root: Path) -> None:
    transaction_root = _transaction_root(plugin_root)
    if not transaction_root.exists() and not transaction_root.is_symlink():
        return
    if transaction_root.is_symlink() or not transaction_root.is_dir():
        raise ValidationError(
            f"render transaction must be a real directory: {transaction_root}"
        )
    journal_path = transaction_root / "journal.json"
    committed_marker = transaction_root / "committed"
    if committed_marker.is_symlink() or (
        committed_marker.exists() and not committed_marker.is_file()
    ):
        raise ValidationError(
            f"render commit marker must be a real file: {committed_marker}"
        )
    if not journal_path.exists():
        if committed_marker.exists():
            if not plugin_root.is_dir():
                raise ValidationError(
                    f"committed plugin output is missing: {plugin_root}"
                )
            committed_marker.unlink()
        if any(transaction_root.iterdir()):
            raise ValidationError(
                f"render transaction journal is missing: {journal_path}"
            )
        transaction_root.rmdir()
        return
    journal = load_json(journal_path)
    if (
        journal.get("schema_version") != 1
        or journal.get("target") != plugin_root.name
        or not isinstance(journal.get("had_target"), bool)
    ):
        raise ValidationError(f"invalid frontend design render journal: {journal_path}")
    backup = transaction_root / "backup"
    if backup.is_symlink():
        raise ValidationError(f"render backup must not be a symlink: {backup}")
    if backup.exists() and not backup.is_dir():
        raise ValidationError(f"render backup must be a directory: {backup}")
    if committed_marker.exists():
        if not plugin_root.is_dir():
            raise ValidationError(f"committed plugin output is missing: {plugin_root}")
    else:
        if journal["had_target"]:
            if backup.exists():
                _remove_path(plugin_root)
                os.replace(backup, plugin_root)
            elif not plugin_root.exists():
                raise ValidationError(
                    f"cannot recover missing plugin output and backup: {plugin_root}"
                )
        else:
            _remove_path(plugin_root)
    if backup.exists():
        shutil.rmtree(backup)
    journal_path.unlink(missing_ok=True)
    committed_marker.unlink(missing_ok=True)
    transaction_root.rmdir()


def _replace_output_atomically(staged_root: Path, plugin_root: Path) -> None:
    transaction_root = _transaction_root(plugin_root)
    if transaction_root.exists() or transaction_root.is_symlink():
        _recover_render_transaction(plugin_root)
    transaction_root.mkdir(mode=0o700)
    had_target = plugin_root.exists()
    _write_json(
        transaction_root / "journal.json",
        {
            "schema_version": 1,
            "target": plugin_root.name,
            "had_target": had_target,
        },
    )
    backup = transaction_root / "backup"
    try:
        if had_target:
            os.replace(plugin_root, backup)
        os.replace(staged_root, plugin_root)
        _mark_render_transaction_committed(transaction_root)
    except BaseException:
        _recover_render_transaction(plugin_root)
        raise
    _recover_render_transaction(plugin_root)


def _manifest(include_skills: bool) -> Dict[str, Any]:
    manifest: Dict[str, Any] = {
        "name": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "description": PLUGIN_DESCRIPTION,
        "author": PLUGIN_AUTHOR,
        "homepage": PLUGIN_REPOSITORY,
        "repository": PLUGIN_REPOSITORY,
        "license": "MIT",
        "keywords": PLUGIN_KEYWORDS,
    }
    if include_skills:
        manifest["skills"] = "./skills/"
        manifest["interface"] = CODEX_INTERFACE
    return manifest


def _source_map(registry: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    return {source["id"]: source for source in registry["sources"]}


def _provenance_map(
    provenance: Mapping[str, Any],
) -> Dict[tuple[str, str], Mapping[str, Any]]:
    return {
        (record["source_id"], record["upstream_path"]): record
        for record in provenance["records"]
    }


def _locked_file_map(lock: Mapping[str, Any]) -> Dict[tuple[str, str], Mapping[str, Any]]:
    return {
        (source["id"], file_record["path"]): file_record
        for source in lock["sources"]
        for file_record in source["files"]
    }


def _safe_dependency_path(value: str, context: str) -> PurePosixPath:
    if "\\" in value:
        raise ValidationError(f"{context} must use POSIX path separators: {value}")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or ".." in path.parts
        or "." in path.parts
        or path.as_posix() != value
    ):
        raise ValidationError(f"{context} is not a safe relative path: {value}")
    return path


def _declared_local_dependencies(content: str) -> set[str]:
    return (
        set(SKILL_ROOT_DEPENDENCY_PATTERN.findall(content))
        | set(REFERENCE_DEPENDENCY_PATTERN.findall(content))
        | set(MARKDOWN_DEPENDENCY_PATTERN.findall(content))
    )


def _dependency_map(
    dependencies: Mapping[str, Any],
) -> tuple[
    Dict[str, list[Mapping[str, Any]]],
    Dict[str, list[Mapping[str, Any]]],
]:
    if dependencies.get("schema_version") != 1:
        raise ValidationError("MengTo dependency map must use schema version 1")
    procedures = dependencies.get("procedures")
    if not isinstance(procedures, list):
        raise ValidationError("MengTo dependency procedures must be an array")
    mapped: Dict[str, list[Mapping[str, Any]]] = {}
    external: Dict[str, list[Mapping[str, Any]]] = {}
    for procedure in procedures:
        if not isinstance(procedure, dict):
            raise ValidationError("MengTo dependency procedure must be an object")
        source_path = procedure.get("source_path")
        raw_dependencies = procedure.get("dependencies")
        raw_external = procedure.get("external_runtime_requirements", [])
        if not isinstance(source_path, str) or not isinstance(raw_dependencies, list):
            raise ValidationError("MengTo dependency procedure is malformed")
        if not isinstance(raw_external, list):
            raise ValidationError("MengTo external runtime requirements must be an array")
        _safe_dependency_path(source_path, "MengTo procedure source path")
        if source_path in mapped:
            raise ValidationError(f"duplicate MengTo dependency procedure: {source_path}")
        seen_targets: set[str] = set()
        checked: list[Mapping[str, Any]] = []
        for dependency in raw_dependencies:
            if not isinstance(dependency, dict):
                raise ValidationError(f"MengTo dependency is malformed: {source_path}")
            if set(dependency) != {"target_path", "source_id", "source_path"}:
                raise ValidationError(
                    f"MengTo dependency fields are invalid: {source_path}: {dependency}"
                )
            target_path = dependency["target_path"]
            dependency_source = dependency["source_id"]
            dependency_path = dependency["source_path"]
            if not all(
                isinstance(value, str) and value
                for value in (target_path, dependency_source, dependency_path)
            ):
                raise ValidationError(f"MengTo dependency values are invalid: {source_path}")
            _safe_dependency_path(target_path, "MengTo dependency target path")
            _safe_dependency_path(dependency_path, "MengTo dependency source path")
            if target_path in seen_targets:
                raise ValidationError(
                    f"duplicate MengTo dependency target: {source_path}:{target_path}"
                )
            seen_targets.add(target_path)
            checked.append(dependency)
        mapped[source_path] = checked
        checked_external: list[Mapping[str, Any]] = []
        for requirement in raw_external:
            if not isinstance(requirement, dict) or set(requirement) != {
                "capability",
                "required_file",
                "resolution",
            }:
                raise ValidationError(
                    f"MengTo external runtime requirement is malformed: {source_path}"
                )
            if not all(
                isinstance(requirement.get(field), str) and requirement[field]
                for field in ("capability", "required_file", "resolution")
            ):
                raise ValidationError(
                    f"MengTo external runtime requirement is incomplete: {source_path}"
                )
            _safe_dependency_path(
                requirement["required_file"],
                "MengTo external runtime file",
            )
            if requirement["resolution"] != "discover-installed-plugin":
                raise ValidationError(
                    f"MengTo external runtime resolution is unsupported: {source_path}"
                )
            checked_external.append(requirement)
        if checked_external:
            external[source_path] = checked_external
    return mapped, external


def _safe_reference_name(value: str, context: str) -> str:
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in {"", ".", ".."}
        or "\\" in value
    ):
        raise ValidationError(f"{context} is not a safe reference name: {value}")
    return value


def _copy_mengto_references(
    repo_root: Path,
    skill_root: Path,
    registry: Mapping[str, Any],
    lock: Mapping[str, Any],
    provenance: Mapping[str, Any],
    dependencies: Mapping[str, Any],
) -> list[Dict[str, Any]]:
    provenance_by_path = _provenance_map(provenance)
    locked_files = _locked_file_map(lock)
    source_by_id = _source_map(registry)
    dependencies_by_procedure, external_by_procedure = _dependency_map(dependencies)
    vendor_root = repo_root / "design-stack/vendor/mengto-skills"
    entries = []
    resolved_procedures: set[str] = set()
    for catalog_entry in lock["catalogs"]["mengto_skills"]:
        source_path = catalog_entry["path"]
        record = provenance_by_path[("mengto-skills", source_path)]
        entry: Dict[str, Any] = {
            "source_id": "mengto-skills",
            "name": catalog_entry["name"],
            "source_path": source_path,
            "sha256": record["sha256"],
            "decision": record["decision"],
            "authority": record["authority"],
        }
        if record["decision"] == "included":
            source_parts = PurePosixPath(source_path).parts
            category = _safe_reference_name(source_parts[1], "MengTo category")
            name = _safe_reference_name(catalog_entry["name"], "MengTo skill name")
            procedure_root = PurePosixPath("references", "mengto", category, name)
            reference_path = (procedure_root / "procedure.md").as_posix()
            procedure_bytes = (vendor_root / source_path).read_bytes()
            _write_bytes(
                skill_root / reference_path,
                procedure_bytes,
            )
            entry["reference_path"] = reference_path
            supporting_files = []
            dependency_markdown = []
            mapped_dependencies = dependencies_by_procedure.get(source_path, [])
            mapped_targets = {
                dependency["target_path"] for dependency in mapped_dependencies
            }
            for dependency in mapped_dependencies:
                dependency_source_id = dependency["source_id"]
                dependency_source_path = dependency["source_path"]
                dependency_target = _safe_dependency_path(
                    dependency["target_path"],
                    "MengTo dependency target path",
                )
                dependency_key = (dependency_source_id, dependency_source_path)
                dependency_record = provenance_by_path.get(dependency_key)
                locked_dependency = locked_files.get(dependency_key)
                dependency_source = source_by_id.get(dependency_source_id)
                if (
                    dependency_record is None
                    or dependency_record.get("decision") != "included"
                    or locked_dependency is None
                    or locked_dependency.get("materialization") != "vendored"
                    or dependency_source is None
                    or dependency_source.get("distribution") != "vendored"
                ):
                    raise ValidationError(
                        f"MengTo dependency is not approved and vendored: {dependency_key}"
                    )
                dependency_bytes = (
                    repo_root
                    / dependency_source["destination"]
                    / dependency_source_path
                ).read_bytes()
                if sha256_file(
                    repo_root
                    / dependency_source["destination"]
                    / dependency_source_path
                ) != locked_dependency["sha256"]:
                    raise ValidationError(
                        f"MengTo dependency hash differs: {dependency_key}"
                    )
                packaged_dependency = procedure_root.joinpath(
                    *dependency_target.parts
                ).as_posix()
                _write_bytes(skill_root / packaged_dependency, dependency_bytes)
                if dependency_target.suffix.lower() == ".md":
                    dependency_markdown.append(dependency_bytes.decode("utf-8"))
                supporting_files.append(
                    {
                        "source_id": dependency_source_id,
                        "source_path": dependency_source_path,
                        "target_path": dependency_target.as_posix(),
                        "reference_path": packaged_dependency,
                        "sha256": locked_dependency["sha256"],
                        "authority": dependency_record["authority"],
                        "role": dependency_record["role"],
                    }
                )
            declared_dependencies = _declared_local_dependencies(
                procedure_bytes.decode("utf-8")
            )
            for dependency_content in dependency_markdown:
                declared_dependencies.update(
                    _declared_local_dependencies(dependency_content)
                )
            if declared_dependencies != mapped_targets:
                raise ValidationError(
                    f"MengTo dependency map differs for {source_path}; "
                    f"missing={sorted(declared_dependencies - mapped_targets)}; "
                    f"unexpected={sorted(mapped_targets - declared_dependencies)}"
                )
            if supporting_files:
                entry["supporting_files"] = supporting_files
            external_requirements = external_by_procedure.get(source_path, [])
            if external_requirements:
                entry["external_runtime_requirements"] = external_requirements
            resolved_procedures.add(source_path)
        elif record["decision"] == "mapped-to-official":
            entry["reason"] = record["reason"]
            entry["official_mapping"] = record["official_mapping"]
        else:
            raise ValidationError(
                f"approved MengTo catalog entry has unsupported decision: {source_path}"
            )
        entries.append(entry)
    unexpected_procedures = sorted(
        (set(dependencies_by_procedure) | set(external_by_procedure))
        - resolved_procedures
    )
    if unexpected_procedures:
        raise ValidationError(
            f"MengTo dependency map references unavailable procedures: {unexpected_procedures}"
        )
    return entries


def _copy_design_md_references(
    repo_root: Path,
    skill_root: Path,
    lock: Mapping[str, Any],
) -> list[Dict[str, Any]]:
    vendor_root = repo_root / "design-stack/vendor/awesome-design-md"
    entries = []
    for catalog_entry in lock["catalogs"]["design_md"]:
        name = _safe_reference_name(catalog_entry["name"], "DESIGN.md name")
        reference_path = f"references/design-md/{name}.md"
        _write_bytes(
            skill_root / reference_path,
            (vendor_root / catalog_entry["path"]).read_bytes(),
        )
        entries.append(
            {
                "source_id": "awesome-design-md",
                "name": catalog_entry["name"],
                "source_path": catalog_entry["path"],
                "reference_path": reference_path,
                "sha256": catalog_entry["sha256"],
                "authority": "third-party-analysis",
            }
        )
    return entries


def _copy_authored_router(repo_root: Path, skill_root: Path) -> None:
    design_stack = repo_root / "design-stack"
    _write_bytes(
        skill_root / "SKILL.md",
        (design_stack / "router/SKILL.md").read_bytes(),
    )
    for filename in ("source-precedence.md", "quality-gates.md"):
        _write_bytes(
            skill_root / "references" / filename,
            (design_stack / "router/references" / filename).read_bytes(),
        )
    routing = load_json(design_stack / "routing.json")
    packaged_references: Dict[str, str] = {}
    for key, raw_path in routing.get("references", {}).items():
        if not isinstance(key, str) or not isinstance(raw_path, str):
            raise ValidationError("routing references must map strings to paths")
        source_path = PurePosixPath(raw_path)
        if (
            source_path.is_absolute()
            or "\\" in raw_path
            or ".." in source_path.parts
            or "." in source_path.parts
            or source_path.parts[:1] != ("router",)
        ):
            raise ValidationError(f"unsafe authored routing reference: {key}={raw_path}")
        packaged_path = PurePosixPath(*source_path.parts[1:])
        if not packaged_path.parts:
            raise ValidationError(f"empty packaged routing reference: {key}")
        local_path = skill_root.joinpath(*packaged_path.parts)
        if not local_path.is_file():
            raise ValidationError(
                f"packaged routing reference is missing: {key}={packaged_path}"
            )
        packaged_references[key] = packaged_path.as_posix()
    routing["references"] = packaged_references
    _write_json(skill_root / "references/routing.json", routing)
    for template in sorted((design_stack / "templates").iterdir()):
        if template.is_file():
            _write_bytes(
                skill_root / "references/templates" / template.name,
                template.read_bytes(),
            )


def _copy_contracts_and_official_guidance(
    repo_root: Path,
    skill_root: Path,
    lock: Mapping[str, Any],
) -> Dict[str, Any]:
    locked_files = _locked_file_map(lock)
    google_contract = lock["contracts"]["google_design_md_cli"]
    google_reference = "references/contracts/google-design-md-cli-package.json"
    _write_bytes(
        skill_root / google_reference,
        (
            repo_root
            / "design-stack/vendor/google-design-md"
            / google_contract["path"]
        ).read_bytes(),
    )
    vercel_reference = "references/vercel/web-interface-guidelines.md"
    _write_bytes(
        skill_root / vercel_reference,
        (
            repo_root
            / "design-stack/vendor/vercel-web-interface-guidelines/command.md"
        ).read_bytes(),
    )
    return {
        "google_design_md": {
            "source_id": google_contract["source_id"],
            "source_path": google_contract["path"],
            "reference_path": google_reference,
            "sha256": google_contract["sha256"],
            "version": google_contract["version"],
            "authority": "official-contract",
        },
        "vercel_interface": {
            "source_id": "vercel-web-interface-guidelines",
            "source_path": "command.md",
            "reference_path": vercel_reference,
            "sha256": locked_files[
                ("vercel-web-interface-guidelines", "command.md")
            ]["sha256"],
            "authority": "official",
        },
    }


def _copy_notices(
    repo_root: Path,
    plugin_root: Path,
    registry: Mapping[str, Any],
) -> None:
    source_by_id = _source_map(registry)
    lines = [
        "# Third-Party Notices",
        "",
        "This plugin contains reviewed reference material copied from immutable revisions.",
        "Third-party DESIGN.md files are analyses of public interfaces, not owner guidance.",
        "Mapped-to-official entries copy no upstream MengTo bytes into the plugin.",
        "",
    ]
    for source_id in sorted(source_by_id):
        source = source_by_id[source_id]
        if source["distribution"] != "vendored":
            continue
        notice_source = (
            repo_root
            / source["destination"]
            / source["license"]["notice_path"]
        )
        notice_destination = plugin_root / "licenses" / f"{source_id}.txt"
        _write_bytes(notice_destination, notice_source.read_bytes())
        lines.extend(
            [
                f"## {source_id}",
                "",
                f"- Repository: {source['repository']}",
                f"- Revision: {source['revision']}",
                f"- License: {source['license']['spdx']}",
                f"- Local notice: licenses/{source_id}.txt",
                "",
            ]
        )
    _write_text(plugin_root / "THIRD_PARTY_NOTICES.md", "\n".join(lines))


def _render_plugin_tree(repo_root: Path, plugin_root: Path) -> None:
    validate_repository(repo_root, metadata_only=False)
    registry = load_json(repo_root / "design-stack/sources.json")
    lock = load_json(repo_root / "design-stack/sources.lock.json")
    provenance = load_json(repo_root / "design-stack/provenance.json")
    dependencies = load_json(repo_root / "design-stack/mengto-dependencies.json")

    _prepare_empty_output(repo_root, plugin_root)
    _write_json(plugin_root / ".codex-plugin/plugin.json", _manifest(True))
    _write_json(plugin_root / ".claude-plugin/plugin.json", _manifest(False))
    _write_text(plugin_root / "LICENSE", MIT_LICENSE)

    skill_root = plugin_root / "skills/frontend-design"
    _copy_authored_router(repo_root, skill_root)
    catalog: Dict[str, Any] = {
        "schema_version": 1,
        "mengto_skills": _copy_mengto_references(
            repo_root,
            skill_root,
            registry,
            lock,
            provenance,
            dependencies,
        ),
        "design_md": _copy_design_md_references(repo_root, skill_root, lock),
    }
    catalog.update(
        _copy_contracts_and_official_guidance(repo_root, skill_root, lock)
    )
    _write_json(skill_root / "references/reference-catalog.json", catalog)
    _copy_notices(repo_root, plugin_root, registry)
    validate_plugin_tree(plugin_root)


def render_plugin(repo_root: Path, plugin_root: Path) -> None:
    repo_root = repo_root.expanduser().resolve()
    plugin_root = _validated_output_path(repo_root, plugin_root)
    plugin_root.parent.mkdir(parents=True, exist_ok=True)
    _recover_render_transaction(plugin_root)
    if plugin_root.exists() and not plugin_root.is_dir():
        raise ValidationError(f"plugin output is not a directory: {plugin_root}")
    staged_root = Path(
        tempfile.mkdtemp(
            prefix=f".{plugin_root.name}.render-",
            dir=plugin_root.parent,
        )
    )
    try:
        _render_plugin_tree(repo_root, staged_root)
        _replace_output_atomically(staged_root, plugin_root)
    finally:
        if staged_root.exists() or staged_root.is_symlink():
            _remove_path(staged_root)


def _plugin_files(root: Path) -> Dict[str, Path]:
    if not root.is_dir():
        raise ValidationError(f"plugin root does not exist: {root}")
    files: Dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValidationError(f"plugin must not contain symlinks: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValidationError(f"plugin contains a special file: {relative}")
        files[relative] = path
    return files


def validate_plugin_tree(plugin_root: Path) -> None:
    files = _plugin_files(plugin_root)
    required = {
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        "skills/frontend-design/SKILL.md",
        "skills/frontend-design/references/reference-catalog.json",
        "THIRD_PARTY_NOTICES.md",
        "LICENSE",
    }
    missing = sorted(required - set(files))
    if missing:
        raise ValidationError(f"plugin is missing required files: {missing}")
    codex = load_json(plugin_root / ".codex-plugin/plugin.json")
    claude = load_json(plugin_root / ".claude-plugin/plugin.json")
    if codex.get("name") != PLUGIN_NAME or claude.get("name") != PLUGIN_NAME:
        raise ValidationError("plugin manifests must use frontend-design-pack")
    if codex.get("version") != claude.get("version") or not codex.get("version"):
        raise ValidationError("plugin manifest versions must match")
    if codex.get("skills") != "./skills/":
        raise ValidationError("Codex plugin manifest must declare ./skills/")
    skill_files = sorted(path for path in files if path.endswith("/SKILL.md"))
    if skill_files != ["skills/frontend-design/SKILL.md"]:
        raise ValidationError(
            f"plugin must contain exactly one native frontend-design skill: {skill_files}"
        )
    metadata = parse_skill_frontmatter(
        files["skills/frontend-design/SKILL.md"].read_text(encoding="utf-8"),
        "skills/frontend-design/SKILL.md",
    )
    if metadata["name"] != "frontend-design":
        raise ValidationError("plugin skill must be named frontend-design")

    skill_root = plugin_root / "skills/frontend-design"
    routing = load_json(skill_root / "references/routing.json")
    routing_references = routing.get("references")
    if not isinstance(routing_references, dict):
        raise ValidationError("packaged routing references must be an object")
    for key, raw_path in routing_references.items():
        if not isinstance(key, str) or not isinstance(raw_path, str):
            raise ValidationError("packaged routing references must map strings to paths")
        path = PurePosixPath(raw_path)
        if (
            path.is_absolute()
            or "\\" in raw_path
            or ".." in path.parts
            or "." in path.parts
        ):
            raise ValidationError(f"routing reference '{key}' is unsafe: {raw_path}")
        if not skill_root.joinpath(*path.parts).is_file():
            raise ValidationError(f"routing reference '{key}' is missing: {raw_path}")

    catalog = load_json(skill_root / "references/reference-catalog.json")
    for section in ("mengto_skills", "design_md"):
        for entry in catalog[section]:
            reference_path = entry.get("reference_path")
            if reference_path is None:
                if entry.get("decision") != "mapped-to-official":
                    raise ValidationError(
                        f"catalog entry has no self-contained resolution: {entry}"
                    )
                continue
            path = PurePosixPath(reference_path)
            if path.is_absolute() or ".." in path.parts or "." in path.parts:
                raise ValidationError(
                    f"catalog contains an unsafe reference path: {reference_path}"
                )
            local_path = skill_root.joinpath(*path.parts)
            if not local_path.is_file():
                raise ValidationError(f"catalog reference is missing: {reference_path}")
            if sha256_file(local_path) != entry["sha256"]:
                raise ValidationError(f"catalog reference hash differs: {reference_path}")
            if section != "mengto_skills":
                continue
            if local_path.name != "procedure.md":
                raise ValidationError(
                    f"MengTo procedure must be packaged as procedure.md: {reference_path}"
                )
            supporting_files = entry.get("supporting_files", [])
            if not isinstance(supporting_files, list):
                raise ValidationError(
                    f"MengTo supporting files must be an array: {entry['source_path']}"
                )
            supporting_targets: set[str] = set()
            dependency_markdown: list[str] = []
            for supporting_file in supporting_files:
                if not isinstance(supporting_file, dict):
                    raise ValidationError(
                        f"MengTo supporting file is malformed: {entry['source_path']}"
                    )
                for field in (
                    "source_id",
                    "source_path",
                    "target_path",
                    "reference_path",
                    "sha256",
                    "authority",
                    "role",
                ):
                    if not isinstance(supporting_file.get(field), str) or not supporting_file[field]:
                        raise ValidationError(
                            f"MengTo supporting file is missing {field}: {entry['source_path']}"
                        )
                target_path = _safe_dependency_path(
                    supporting_file["target_path"],
                    "MengTo packaged dependency target",
                )
                supporting_reference = _safe_dependency_path(
                    supporting_file["reference_path"],
                    "MengTo packaged dependency reference",
                )
                expected_reference = path.parent.joinpath(*target_path.parts)
                if supporting_reference != expected_reference:
                    raise ValidationError(
                        f"MengTo dependency path mismatch: {entry['source_path']}: "
                        f"{supporting_file['target_path']}"
                    )
                if target_path.as_posix() in supporting_targets:
                    raise ValidationError(
                        f"duplicate MengTo dependency target: {entry['source_path']}: "
                        f"{target_path}"
                    )
                supporting_targets.add(target_path.as_posix())
                supporting_path = skill_root.joinpath(*supporting_reference.parts)
                if not supporting_path.is_file():
                    raise ValidationError(
                        f"MengTo local dependency is missing for {entry['source_path']}: "
                        f"{target_path}"
                    )
                if sha256_file(supporting_path) != supporting_file["sha256"]:
                    raise ValidationError(
                        f"MengTo local dependency hash differs for {entry['source_path']}: "
                        f"{target_path}"
                    )
                if supporting_path.suffix.lower() == ".md":
                    dependency_markdown.append(
                        supporting_path.read_text(encoding="utf-8")
                    )
            declared_dependencies = _declared_local_dependencies(
                local_path.read_text(encoding="utf-8")
            )
            for dependency_content in dependency_markdown:
                declared_dependencies.update(
                    _declared_local_dependencies(dependency_content)
                )
            missing_dependencies = sorted(
                declared_dependencies - supporting_targets
            )
            unexpected_dependencies = sorted(
                supporting_targets - declared_dependencies
            )
            if missing_dependencies:
                raise ValidationError(
                    f"MengTo local dependency is missing for {entry['source_path']}: "
                    f"{missing_dependencies}"
                )
            if unexpected_dependencies:
                raise ValidationError(
                    f"MengTo supporting dependency is undeclared for {entry['source_path']}: "
                    f"{unexpected_dependencies}"
                )
            external_requirements = entry.get("external_runtime_requirements", [])
            if not isinstance(external_requirements, list):
                raise ValidationError(
                    f"MengTo external runtime requirements must be an array: "
                    f"{entry['source_path']}"
                )
            for requirement in external_requirements:
                if not isinstance(requirement, dict) or set(requirement) != {
                    "capability",
                    "required_file",
                    "resolution",
                }:
                    raise ValidationError(
                        f"MengTo external runtime requirement is malformed: "
                        f"{entry['source_path']}"
                    )
                if not all(
                    isinstance(requirement.get(field), str) and requirement[field]
                    for field in ("capability", "required_file", "resolution")
                ):
                    raise ValidationError(
                        f"MengTo external runtime requirement is incomplete: "
                        f"{entry['source_path']}"
                    )
                _safe_dependency_path(
                    requirement["required_file"],
                    "MengTo external runtime file",
                )
                if requirement["resolution"] != "discover-installed-plugin":
                    raise ValidationError(
                        f"MengTo external runtime resolution is unsupported: "
                        f"{entry['source_path']}"
                    )

    for catalog_key in ("google_design_md", "vercel_interface"):
        reference = catalog.get(catalog_key)
        if not isinstance(reference, dict):
            raise ValidationError(f"catalog is missing {catalog_key}")
        raw_path = reference.get("reference_path")
        digest = reference.get("sha256")
        if not isinstance(raw_path, str) or not isinstance(digest, str):
            raise ValidationError(f"catalog {catalog_key} reference is incomplete")
        path = _safe_dependency_path(raw_path, f"catalog {catalog_key} reference")
        local_path = skill_root.joinpath(*path.parts)
        if not local_path.is_file():
            raise ValidationError(f"catalog {catalog_key} reference is missing: {raw_path}")
        if sha256_file(local_path) != digest:
            raise ValidationError(f"catalog {catalog_key} hash differs: {raw_path}")


def validate_runtime_copy(
    expected_root: Path,
    runtime_root: Path,
    label: str,
) -> None:
    expected = _plugin_files(expected_root)
    actual = _plugin_files(runtime_root)
    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    changed = sorted(
        path
        for path in set(expected) & set(actual)
        if sha256_file(expected[path]) != sha256_file(actual[path])
    )
    if missing or changed or unexpected:
        raise ValidationError(
            f"{label} runtime plugin mismatch; missing={missing}; "
            f"changed={changed}; unexpected={unexpected}"
        )
    validate_plugin_tree(runtime_root)


def validate_tracked_plugin(repo_root: Path, plugin_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="frontend-design-render-") as temp_dir:
        expected_root = Path(temp_dir) / PLUGIN_NAME
        render_plugin(repo_root, expected_root)
        validate_runtime_copy(expected_root, plugin_root, "Tracked")


def main() -> int:
    args = parse_args()
    repo_root = (
        Path(args.repo_root).expanduser().resolve()
        if args.repo_root
        else Path(__file__).resolve().parents[1]
    )
    plugin_root = (
        Path(args.plugin_root).expanduser()
        if args.plugin_root
        else repo_root / PLUGIN_ROOT
    )
    try:
        render_plugin(repo_root, plugin_root)
    except (OSError, ValidationError, KeyError, ValueError) as error:
        print(f"Frontend design plugin render failed: {error}")
        return 1
    print(f"Rendered frontend design plugin at {plugin_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
