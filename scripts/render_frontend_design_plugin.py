#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
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


def _prepare_output(repo_root: Path, plugin_root: Path) -> None:
    if plugin_root.is_symlink():
        raise ValidationError(f"plugin output must not be a symlink: {plugin_root}")
    if plugin_root.resolve() == repo_root.resolve():
        raise ValidationError("plugin output must not replace the repository root")
    if plugin_root.exists():
        if not plugin_root.is_dir():
            raise ValidationError(f"plugin output is not a directory: {plugin_root}")
        shutil.rmtree(plugin_root)
    plugin_root.mkdir(parents=True)


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
    lock: Mapping[str, Any],
    provenance: Mapping[str, Any],
) -> list[Dict[str, Any]]:
    provenance_by_path = _provenance_map(provenance)
    vendor_root = repo_root / "design-stack/vendor/mengto-skills"
    entries = []
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
            reference_path = f"references/mengto/{category}/{name}.md"
            _write_bytes(
                skill_root / reference_path,
                (vendor_root / source_path).read_bytes(),
            )
            entry["reference_path"] = reference_path
        elif record["decision"] == "mapped-to-official":
            entry["reason"] = record["reason"]
            entry["official_mapping"] = record["official_mapping"]
        else:
            raise ValidationError(
                f"approved MengTo catalog entry has unsupported decision: {source_path}"
            )
        entries.append(entry)
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
    _write_bytes(
        skill_root / "references/routing.json",
        (design_stack / "routing.json").read_bytes(),
    )
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


def render_plugin(repo_root: Path, plugin_root: Path) -> None:
    repo_root = repo_root.resolve()
    plugin_root = plugin_root.resolve()
    validate_repository(repo_root, metadata_only=False)
    registry = load_json(repo_root / "design-stack/sources.json")
    lock = load_json(repo_root / "design-stack/sources.lock.json")
    provenance = load_json(repo_root / "design-stack/provenance.json")

    _prepare_output(repo_root, plugin_root)
    _write_json(plugin_root / ".codex-plugin/plugin.json", _manifest(True))
    _write_json(plugin_root / ".claude-plugin/plugin.json", _manifest(False))
    _write_text(plugin_root / "LICENSE", MIT_LICENSE)

    skill_root = plugin_root / "skills/frontend-design"
    _copy_authored_router(repo_root, skill_root)
    catalog: Dict[str, Any] = {
        "schema_version": 1,
        "mengto_skills": _copy_mengto_references(
            repo_root, skill_root, lock, provenance
        ),
        "design_md": _copy_design_md_references(repo_root, skill_root, lock),
    }
    catalog.update(
        _copy_contracts_and_official_guidance(repo_root, skill_root, lock)
    )
    _write_json(skill_root / "references/reference-catalog.json", catalog)
    _copy_notices(repo_root, plugin_root, registry)
    validate_plugin_tree(plugin_root)


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
        Path(args.plugin_root).expanduser().resolve()
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
