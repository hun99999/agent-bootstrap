#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

TEMPLATE_ROOT = ".opencode/templates"
METADATA_PATH = Path("shared/agent-metadata.json")
PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
BACKUP_NAMESPACE = ("backups", "agent-bootstrap", "opencode")
CONFIG_RELATIVE_PATH = Path("opencode.json")
LOCAL_INCLUDE_LINE = "@local.md"
DEFAULT_PLUGIN = "superpowers@git+https://github.com/obra/superpowers.git"
DEFAULT_AGENT = "eng-lead"
OPENCODE_MODES = {"primary", "subagent"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render and install the managed OpenCode files from this repository."
    )
    parser.add_argument(
        "--partner-name",
        required=True,
        help="Name the agents should use when addressing the user.",
    )
    parser.add_argument(
        "--opencode-home",
        default="~/.config/opencode",
        help="Target OpenCode config directory. Defaults to ~/.config/opencode.",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root. Defaults to the parent of this script directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the install plan without writing or backing up files.",
    )
    return parser.parse_args()


def render_template(content: str, replacements: dict[str, str], source: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in replacements:
            raise ValueError(f"unknown placeholder '{key}' in {source}")
        return replacements[key]

    return PLACEHOLDER_PATTERN.sub(replace, content)


def copy_to_backup(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def backup_existing_paths(target_root: Path, managed_paths: list[Path]) -> Path | None:
    existing = [path for path in managed_paths if path.exists()]
    if not existing:
        return None

    backup_root = (
        target_root
        / Path(*BACKUP_NAMESPACE)
        / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    for source in existing:
        destination = backup_root / source.relative_to(target_root)
        copy_to_backup(source, destination)
    return backup_root


def list_agent_sources(repo_root: Path) -> list[Path]:
    return sorted((repo_root / "agents").glob("*.md"))


def load_agent_metadata(repo_root: Path) -> dict[str, dict[str, object]]:
    metadata_path = repo_root / METADATA_PATH
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def validate_agent_metadata(agent_name: str, metadata: dict[str, object]) -> None:
    if not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
        raise ValueError(f"invalid description for OpenCode agent '{agent_name}'")
    if metadata.get("opencode_mode") not in OPENCODE_MODES:
        raise ValueError(f"invalid opencode_mode for OpenCode agent '{agent_name}'")
    if not isinstance(metadata.get("read_only"), bool):
        raise ValueError(f"invalid read_only for OpenCode agent '{agent_name}'")


def strip_local_include(content: str) -> str:
    lines = [line for line in content.splitlines() if line.strip() != LOCAL_INCLUDE_LINE]
    return "\n".join(lines).rstrip() + "\n"


def build_frontmatter(agent_name: str, metadata_map: dict[str, dict[str, object]]) -> str:
    metadata = metadata_map.get(agent_name)
    if metadata is None:
        raise ValueError(f"missing OpenCode metadata for agent '{agent_name}'")
    validate_agent_metadata(agent_name, metadata)

    lines = [
        "---",
        f"description: {metadata['description']}",
        f"mode: {metadata['opencode_mode']}",
    ]
    if metadata.get("read_only"):
        lines.append("permission:")
        lines.append("  edit: deny")
    lines.append("---")
    return "\n".join(lines)


def compose_agent_markdown(
    repo_root: Path,
    agent_source: Path,
    replacements: dict[str, str],
    metadata_map: dict[str, dict[str, object]],
) -> str:
    constitution = render_template(
        (repo_root / "AGENTS.md").read_text(encoding="utf-8"),
        replacements,
        repo_root / "AGENTS.md",
    )
    role_body = render_template(
        agent_source.read_text(encoding="utf-8"),
        replacements,
        agent_source,
    )
    return "\n\n".join(
        [
            build_frontmatter(agent_source.stem, metadata_map),
            strip_local_include(constitution).strip(),
            role_body.strip(),
        ]
    ) + "\n"


def print_install_plan(target_root: Path, managed_paths: list[Path], partner_name: str) -> None:
    print(f"Dry run: would install managed OpenCode files into {target_root}")
    print(f"Partner name: {partner_name}")
    print("Managed files:")
    for path in managed_paths:
        print(f"- {path}")


def verify_install(target_root: Path, agent_targets: list[Path]) -> None:
    config_path = target_root / CONFIG_RELATIVE_PATH
    required_paths = [config_path, *agent_targets]
    missing = [path for path in required_paths if not path.exists()]
    if missing:
        missing_str = ", ".join(str(path) for path in missing)
        raise RuntimeError(f"missing installed files: {missing_str}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("$schema") != "https://opencode.ai/config.json":
        raise RuntimeError("opencode.json is missing the expected schema URL")
    if config.get("plugin") != [DEFAULT_PLUGIN]:
        raise RuntimeError("opencode.json is missing the expected superpowers plugin")
    if config.get("default_agent") != DEFAULT_AGENT:
        raise RuntimeError("opencode.json is missing the expected default_agent")


def main() -> int:
    args = parse_args()

    repo_root = (
        Path(args.repo_root).expanduser().resolve()
        if args.repo_root
        else Path(__file__).resolve().parents[1]
    )
    template_root = repo_root / TEMPLATE_ROOT
    if not template_root.is_dir():
        raise SystemExit(f"template root not found: {template_root}")

    target_root = Path(args.opencode_home).expanduser().resolve()
    replacements = {"PARTNER_NAME": args.partner_name}
    metadata_map = load_agent_metadata(repo_root)

    config_source = template_root / "opencode.json"
    agent_sources = list_agent_sources(repo_root)
    agent_targets = [target_root / "agents" / agent_source.name for agent_source in agent_sources]
    managed_paths = [target_root / CONFIG_RELATIVE_PATH, *agent_targets]

    if args.dry_run:
        print_install_plan(target_root, managed_paths, args.partner_name)
        return 0

    backup_root = backup_existing_paths(target_root, managed_paths)
    target_root.mkdir(parents=True, exist_ok=True)

    rendered_config = render_template(
        config_source.read_text(encoding="utf-8"),
        replacements,
        config_source,
    )
    (target_root / CONFIG_RELATIVE_PATH).write_text(rendered_config, encoding="utf-8")

    for agent_source, destination in zip(agent_sources, agent_targets):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            compose_agent_markdown(repo_root, agent_source, replacements, metadata_map),
            encoding="utf-8",
        )

    verify_install(target_root, agent_targets)

    print(f"Installed managed OpenCode files into {target_root}")
    print(f"Partner name: {args.partner_name}")
    if backup_root is None:
        print("Backup: no existing managed files were present")
    else:
        print(f"Backup: {backup_root}")
    print("Managed files:")
    for path in managed_paths:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as err:  # pragma: no cover
        print(f"install failed: {err}", file=sys.stderr)
        raise SystemExit(1)
