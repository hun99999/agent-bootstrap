#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from design_stack import ValidationError, load_json, parse_skill_frontmatter, sha256_file


SCRIPT_SUFFIXES = {".js", ".mjs", ".cjs", ".py", ".sh", ".ts", ".tsx"}
ASSET_SUFFIXES = {
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".otf",
    ".png",
    ".svg",
    ".ttf",
    ".webp",
    ".woff",
    ".woff2",
}
DEPENDENCY_NAMES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "bun.lockb",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
}
URL_PATTERN = re.compile(r"https?://[^\s)\]}>\"']+")
PERMISSION_PATTERN = re.compile(
    r"\b(?:chmod|chown|permission|sudo|osascript|accessibility|screen recording)\b",
    re.IGNORECASE,
)
SERVICE_PATTERN = re.compile(
    r"\b(?:api|deploy|netlify|vercel|gmail|email|slack|github|external service)\b",
    re.IGNORECASE,
)
SIDE_EFFECT_PATTERN = re.compile(
    r"\b(?:deploy|publish|post|email|delete|remove|write|upload|authenticate|chmod)\b|curl\s+[^\n]*--data",
    re.IGNORECASE,
)


def _source_map(registry: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    return {source["id"]: source for source in registry["sources"]}


def _locked_source_map(lock: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    return {source["id"]: source for source in lock["sources"]}


def path_is_in_scope(path: str, source: Mapping[str, Any]) -> bool:
    if path == source["license"]["notice_path"]:
        return True
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in source["scope"])


def _snapshot_candidate(
    candidate_root: Path,
    source: Mapping[str, Any],
) -> Dict[str, Dict[str, Any]]:
    if not candidate_root.is_dir():
        raise ValidationError(f"candidate source tree does not exist: {candidate_root}")
    records: Dict[str, Dict[str, Any]] = {}
    for path in sorted(candidate_root.rglob("*")):
        relative = path.relative_to(candidate_root)
        if not path.is_file() or ".git" in relative.parts:
            continue
        relative_path = relative.as_posix()
        if not path_is_in_scope(relative_path, source):
            continue
        records[relative_path] = {
            "path": relative_path,
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    return records


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def _renames(
    removed: Iterable[str],
    added: Iterable[str],
    old: Mapping[str, Mapping[str, Any]],
    new: Mapping[str, Mapping[str, Any]],
) -> List[Dict[str, str]]:
    available_added = set(added)
    renames: List[Dict[str, str]] = []
    for old_path in sorted(removed):
        candidates = sorted(
            path
            for path in available_added
            if new[path]["sha256"] == old[old_path]["sha256"]
        )
        if not candidates:
            continue
        new_path = candidates[0]
        available_added.remove(new_path)
        renames.append({"from": old_path, "to": new_path})
    return renames


def compare_source_tree(
    repo_root: Path,
    source_id: str,
    candidate_root: Path,
) -> Dict[str, Any]:
    registry = load_json(repo_root / "design-stack/sources.json")
    lock = load_json(repo_root / "design-stack/sources.lock.json")
    provenance = load_json(repo_root / "design-stack/provenance.json")
    sources = _source_map(registry)
    source = sources.get(source_id)
    if source is None:
        raise ValidationError(f"unknown source: {source_id}")
    locked_source = _locked_source_map(lock).get(source_id)
    if locked_source is None:
        raise ValidationError(f"source is missing from lock: {source_id}")

    old = {record["path"]: record for record in locked_source["files"]}
    new = _snapshot_candidate(candidate_root, source)
    old_paths = set(old)
    new_paths = set(new)
    added = sorted(new_paths - old_paths)
    removed = sorted(old_paths - new_paths)
    changed = sorted(
        path
        for path in old_paths & new_paths
        if old[path]["sha256"] != new[path]["sha256"]
    )
    affected = sorted(set(added) | set(changed))
    old_catalog = {
        entry["path"]: entry
        for entries in lock["catalogs"].values()
        for entry in entries
        if entry["source_id"] == source_id
    }

    description_changes: List[Dict[str, str]] = []
    instruction_changes: List[str] = []
    parse_errors: List[Dict[str, str]] = []
    for relative_path in affected:
        if not relative_path.endswith("/SKILL.md"):
            continue
        candidate_path = candidate_root / relative_path
        try:
            metadata = parse_skill_frontmatter(
                candidate_path.read_text(encoding="utf-8"), relative_path
            )
        except (OSError, UnicodeDecodeError, ValidationError) as error:
            parse_errors.append({"path": relative_path, "error": str(error)})
            continue
        previous = old_catalog.get(relative_path)
        if previous is not None and previous.get("description") != metadata["description"]:
            description_changes.append(
                {
                    "path": relative_path,
                    "before": previous.get("description", ""),
                    "after": metadata["description"],
                }
            )
        if relative_path in changed:
            instruction_changes.append(relative_path)

    texts = {
        path: _read_text(candidate_root / path)
        for path in affected
        if (candidate_root / path).is_file()
    }
    urls = sorted({url for text in texts.values() for url in URL_PATTERN.findall(text)})

    provenance_records = {
        (record["source_id"], record["upstream_path"]): record
        for record in provenance["records"]
    }
    provenance_changes = sorted(
        path
        for path in (set(affected) | set(removed))
        if (source_id, path) not in provenance_records
        or path in removed
        or provenance_records[(source_id, path)]["sha256"]
        != new.get(path, {}).get("sha256")
    )
    license_changes = sorted(
        path
        for path in (set(affected) | set(removed))
        if Path(path).name.lower().startswith(("license", "notice"))
    )

    return {
        "source_id": source_id,
        "locked_revision": source["revision"],
        "added": added,
        "removed": removed,
        "changed": changed,
        "renamed": _renames(removed, added, old, new),
        "description_changes": description_changes,
        "instruction_changes": instruction_changes,
        "parse_errors": parse_errors,
        "scripts": sorted(
            path
            for path in affected
            if "/scripts/" in f"/{path}" or Path(path).suffix in SCRIPT_SUFFIXES
        ),
        "assets": sorted(
            path
            for path in affected
            if "/assets/" in f"/{path}" or Path(path).suffix.lower() in ASSET_SUFFIXES
        ),
        "dependencies": sorted(
            path
            for path in affected
            if Path(path).name in DEPENDENCY_NAMES
            or Path(path).name.startswith("requirements")
        ),
        "urls": urls,
        "permissions": sorted(
            path for path, text in texts.items() if PERMISSION_PATTERN.search(text)
        ),
        "services": sorted(
            path for path, text in texts.items() if SERVICE_PATTERN.search(text)
        ),
        "side_effects": sorted(
            path for path, text in texts.items() if SIDE_EFFECT_PATTERN.search(text)
        ),
        "license_changes": license_changes,
        "provenance_changes": provenance_changes,
    }


def format_human_report(report: Mapping[str, Any]) -> str:
    categories = (
        ("Added", "added"),
        ("Removed", "removed"),
        ("Changed", "changed"),
        ("Renamed", "renamed"),
        ("Descriptions", "description_changes"),
        ("Instructions", "instruction_changes"),
        ("Parse errors", "parse_errors"),
        ("Scripts", "scripts"),
        ("Assets", "assets"),
        ("Dependencies", "dependencies"),
        ("URLs", "urls"),
        ("Permissions", "permissions"),
        ("Services", "services"),
        ("Side effects", "side_effects"),
        ("Licenses", "license_changes"),
        ("Provenance", "provenance_changes"),
    )
    lines = [
        f"Source: {report['source_id']}",
        f"Locked revision: {report['locked_revision']}",
    ]
    for label, key in categories:
        values = report.get(key, [])
        lines.append(f"{label}: {len(values)}")
        for value in values:
            if isinstance(value, str):
                rendered = value
            else:
                rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
            lines.append(f"  - {rendered}")
    return "\n".join(lines)


def check_remote_head(repository: str) -> str:
    result = subprocess.run(
        ["git", "ls-remote", repository, "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValidationError(
            result.stderr.strip() or f"git ls-remote failed for {repository}"
        )
    fields = result.stdout.strip().split()
    if not fields:
        raise ValidationError(f"git ls-remote returned no HEAD for {repository}")
    return fields[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only check for changes in a locked frontend design source."
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source", required=True)
    parser.add_argument("--candidate-root", default=None)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = (
        Path(args.repo_root).expanduser().resolve()
        if args.repo_root
        else Path(__file__).resolve().parents[1]
    )
    try:
        if args.candidate_root:
            report = compare_source_tree(
                repo_root,
                args.source,
                Path(args.candidate_root).expanduser().resolve(),
            )
        else:
            registry = load_json(repo_root / "design-stack/sources.json")
            source = _source_map(registry).get(args.source)
            if source is None:
                raise ValidationError(f"unknown source: {args.source}")
            report = {
                "source_id": args.source,
                "locked_revision": source["revision"],
                "remote_head": check_remote_head(source["repository"]),
            }
    except ValidationError as error:
        print(f"Design source check failed: {error}")
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        if "remote_head" in report:
            print(f"Source: {report['source_id']}")
            print(f"Locked revision: {report['locked_revision']}")
            print(f"Remote HEAD: {report['remote_head']}")
        else:
            print(format_human_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
