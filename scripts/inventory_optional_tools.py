#!/usr/bin/env python3
"""Inventory optional guardrail tools without installing anything."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable


SCHEMA = "agent-bootstrap.optional-tool-inventory.v1"
INSTALL_STATUS = "not installed by this script"
CommandLookup = Callable[[str], str | None]
PathExists = Callable[[Path], bool]


@dataclass(frozen=True)
class ToolInventory:
    name: str
    detected_state: str
    decision: str
    reason: str
    evidence: list[str]
    install_status: str = INSTALL_STATUS


def default_command_lookup(command: str) -> str | None:
    return shutil.which(command)


def default_path_exists(path: Path) -> bool:
    return path.expanduser().exists()


def load_package_json(repo_root: Path) -> dict[str, object]:
    package_path = repo_root / "package.json"
    if not package_path.exists():
        return {}
    try:
        data = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def read_package_sections(package: dict[str, object]) -> dict[str, str]:
    values: dict[str, str] = {}
    for section_name in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        section = package.get(section_name)
        if isinstance(section, dict):
            for key, value in section.items():
                values[str(key)] = str(value)
    return values


def read_package_scripts(package: dict[str, object]) -> dict[str, str]:
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return {}
    return {str(key): str(value) for key, value in scripts.items()}


def repo_has_ts_js(repo_root: Path) -> bool:
    if (repo_root / "package.json").exists() or (repo_root / "tsconfig.json").exists():
        return True
    for pattern in ("*.ts", "*.tsx", "*.js", "*.jsx", "*.mjs", "*.cjs"):
        if any(repo_root.rglob(pattern)):
            return True
    return False


def dependency_or_script_mentions(
    package: dict[str, object],
    names: tuple[str, ...],
) -> bool:
    dependencies = read_package_sections(package)
    scripts = read_package_scripts(package)
    lowered_names = tuple(name.lower() for name in names)

    for dependency in dependencies:
        if dependency.lower() in lowered_names:
            return True
    script_text = "\n".join(scripts.values()).lower()
    return any(name in script_text for name in lowered_names)


def classify_obsidian(
    command_lookup: CommandLookup,
    path_exists: PathExists,
    platform_name: str,
) -> ToolInventory:
    evidence = []
    detected = False

    if command_lookup("obsidian") is not None:
        detected = True
        evidence.append("obsidian command is on PATH")
    if platform_name == "Darwin" and path_exists(Path("/Applications/Obsidian.app")):
        detected = True
        evidence.append("/Applications/Obsidian.app exists")

    if not evidence:
        evidence.append("No Obsidian command or documented app path was detected")

    return ToolInventory(
        name="obsidian",
        detected_state="installed" if detected else "missing",
        decision="optional",
        reason="Obsidian is useful for private cross-project knowledge, but it is not required for guardrails.",
        evidence=evidence,
    )


def classify_lumin_repo_lens(
    repo_root: Path,
    command_lookup: CommandLookup,
    path_exists: PathExists,
) -> ToolInventory:
    evidence = []
    detected = False
    ts_js = repo_has_ts_js(repo_root)

    if path_exists(Path("~/.codex/lumin-repo-lens")):
        detected = True
        evidence.append("~/.codex/lumin-repo-lens exists")
    if command_lookup("lumin-repo-lens") is not None:
        detected = True
        evidence.append("lumin-repo-lens command is on PATH")
    evidence.append("Target repository appears TS/JS-heavy" if ts_js else "No TS/JS repository signal detected")
    for artifact_name in (
        "manifest.json",
        "audit-summary.latest.md",
        "pre-write-advisory.latest.json",
        "post-write-delta.latest.json",
    ):
        artifact_path = repo_root / ".audit" / artifact_name
        if artifact_path.exists():
            evidence.append(f".audit/{artifact_name} exists")

    return ToolInventory(
        name="lumin-repo-lens",
        detected_state="installed" if detected else "missing",
        decision="recommended" if ts_js else "skipped",
        reason=(
            "TS/JS structure evidence can help catch duplicate helpers, hidden coupling, re-export drift, and fan-in/fan-out hotspots."
            if ts_js
            else "Lumin Repo Lens is TS/JS-focused, and this repository does not show TS/JS signals."
        ),
        evidence=evidence,
    )


def classify_dependency_lint(repo_root: Path, package: dict[str, object]) -> ToolInventory:
    ts_js = repo_has_ts_js(repo_root)
    detected = dependency_or_script_mentions(
        package,
        ("dependency-cruiser", "eslint-plugin-boundaries", "madge"),
    )
    evidence = []
    if detected:
        evidence.append("package.json dependencies or scripts mention dependency boundary tooling")
    else:
        evidence.append("No package.json dependency boundary tooling signal detected")

    return ToolInventory(
        name="dependency-lint",
        detected_state="installed" if detected else "missing",
        decision="recommended" if ts_js and detected else ("optional" if ts_js else "skipped"),
        reason=(
            "The repo already has dependency boundary tooling signals; tightening existing checks is low-risk."
            if ts_js and detected
            else "Dependency lint is useful, but adding new tooling requires user approval."
            if ts_js
            else "No TS/JS dependency graph signal was found."
        ),
        evidence=evidence,
    )


def classify_strict_type_checks(repo_root: Path, package: dict[str, object]) -> ToolInventory:
    tsconfig_path = repo_root / "tsconfig.json"
    evidence = []
    strict_enabled = False
    if tsconfig_path.exists():
        try:
            tsconfig = json.loads(tsconfig_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            tsconfig = {}
        compiler_options = tsconfig.get("compilerOptions") if isinstance(tsconfig, dict) else None
        strict_enabled = isinstance(compiler_options, dict) and compiler_options.get("strict") is True
        evidence.append("tsconfig.json exists")
        if strict_enabled:
            evidence.append("compilerOptions.strict is true")
    else:
        evidence.append("No tsconfig.json detected")

    has_type_script = dependency_or_script_mentions(package, ("typescript", "tsc")) or tsconfig_path.exists()
    return ToolInventory(
        name="strict-type-checks",
        detected_state="installed" if strict_enabled else ("missing" if has_type_script else "not applicable"),
        decision="recommended" if strict_enabled else ("optional" if has_type_script else "skipped"),
        reason=(
            "Strict TypeScript checking is already enabled."
            if strict_enabled
            else "TypeScript appears present, but strict checking was not confirmed."
            if has_type_script
            else "No TypeScript type-checking signal was detected."
        ),
        evidence=evidence,
    )


def classify_cycle_detection(repo_root: Path, package: dict[str, object]) -> ToolInventory:
    ts_js = repo_has_ts_js(repo_root)
    detected = dependency_or_script_mentions(package, ("madge", "dependency-cruiser", "circular"))
    evidence = [
        "package.json dependencies or scripts mention cycle detection"
        if detected
        else "No cycle detection signal detected"
    ]

    return ToolInventory(
        name="cycle-detection",
        detected_state="installed" if detected else "missing",
        decision="recommended" if ts_js and detected else ("optional" if ts_js else "skipped"),
        reason=(
            "Cycle detection appears available through existing repo tooling."
            if ts_js and detected
            else "Cycle detection could help, but adding new tooling requires user approval."
            if ts_js
            else "No TS/JS import graph signal was found."
        ),
        evidence=evidence,
    )


def classify_complexity_limits(repo_root: Path, package: dict[str, object]) -> ToolInventory:
    ts_js = repo_has_ts_js(repo_root)
    detected = dependency_or_script_mentions(package, ("eslint", "complexity", "max-depth", "max-lines"))
    evidence = [
        "package.json dependencies or scripts mention lint or complexity-related tooling"
        if detected
        else "No complexity limit signal detected"
    ]

    return ToolInventory(
        name="complexity-limits",
        detected_state="installed" if detected else "missing",
        decision="recommended" if ts_js and detected else ("optional" if ts_js else "skipped"),
        reason=(
            "Existing lint tooling can host complexity, depth, and size limits."
            if ts_js and detected
            else "Complexity limits are useful, but adding new tooling requires user approval."
            if ts_js
            else "No relevant lint tooling signal was found."
        ),
        evidence=evidence,
    )


def build_inventory(
    repo_root: Path,
    command_lookup: CommandLookup = default_command_lookup,
    path_exists: PathExists = default_path_exists,
    platform_name: str | None = None,
) -> list[ToolInventory]:
    root = repo_root.expanduser().resolve()
    package = load_package_json(root)
    current_platform = platform_name or platform.system()
    return [
        classify_obsidian(command_lookup, path_exists, current_platform),
        classify_lumin_repo_lens(root, command_lookup, path_exists),
        classify_dependency_lint(root, package),
        classify_strict_type_checks(root, package),
        classify_cycle_detection(root, package),
        classify_complexity_limits(root, package),
    ]


def render_text(results: list[ToolInventory]) -> str:
    lines = ["Optional tool inventory:"]
    for result in results:
        lines.append(f"- {result.name}: {result.decision} ({result.detected_state})")
        lines.append(f"  reason: {result.reason}")
        lines.append(f"  install: {result.install_status}")
        for evidence in result.evidence:
            lines.append(f"  evidence: {evidence}")
    return "\n".join(lines)


def render_json(results: list[ToolInventory]) -> str:
    payload = {
        "schema": SCHEMA,
        "tools": [asdict(result) for result in results],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root to inspect. Defaults to the current directory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of text.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    results = build_inventory(Path(args.repo_root))
    if args.json:
        print(render_json(results))
    else:
        print(render_text(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
