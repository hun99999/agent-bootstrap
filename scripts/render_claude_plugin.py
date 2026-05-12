#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
LOCAL_INCLUDE_LINE = "@local.md"
PLUGIN_ROOT = Path("plugins/process-first-agents")
METADATA_PATH = Path("shared/agent-metadata.json")
PLUGIN_AUTHOR = {"name": "Hun", "email": "48903443+hun99999@users.noreply.github.com"}
PLUGIN_REPOSITORY = "https://github.com/hun99999/agent-bootstrap"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the Claude Code plugin package from the shared prompt corpus."
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root. Defaults to the parent of this script directory.",
    )
    parser.add_argument(
        "--partner-name",
        default="Partner",
        help='Partner name to render into the Claude plugin bundle. Defaults to "Partner".',
    )
    parser.add_argument(
        "--plugin-root",
        default=None,
        help="Plugin package root. Defaults to plugins/process-first-agents under the repo root.",
    )
    return parser.parse_args()


def render_template(content: str, replacements: dict[str, str], source: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in replacements:
            raise ValueError(f"unknown placeholder '{key}' in {source}")
        return replacements[key]

    return PLACEHOLDER_PATTERN.sub(replace, content)


def strip_local_include(content: str) -> str:
    lines = [line for line in content.splitlines() if line.strip() != LOCAL_INCLUDE_LINE]
    return "\n".join(lines).rstrip() + "\n"


def load_agent_metadata(repo_root: Path) -> dict[str, dict[str, object]]:
    metadata_path = repo_root / METADATA_PATH
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def serialize_frontmatter(fields: list[tuple[str, object]]) -> str:
    lines = ["---"]
    for key, value in fields:
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(f"  - {item}" for item in value)
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def build_agent_markdown(
    repo_root: Path,
    agent_source: Path,
    partner_name: str,
    metadata_map: dict[str, dict[str, object]],
) -> str:
    metadata = metadata_map.get(agent_source.stem)
    if metadata is None:
        raise ValueError(f"missing Claude metadata for agent '{agent_source.stem}'")

    replacements = {"PARTNER_NAME": partner_name}
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

    frontmatter_fields: list[tuple[str, object]] = [
        ("name", agent_source.stem),
        ("description", metadata["description"]),
    ]
    claude_metadata = metadata.get("claude", {})
    if not isinstance(claude_metadata, dict):
        raise ValueError(f"invalid Claude metadata for agent '{agent_source.stem}'")
    for key in ["model", "disallowedTools", "isolation"]:
        if key in claude_metadata:
            frontmatter_fields.append((key, claude_metadata[key]))

    frontmatter = serialize_frontmatter(frontmatter_fields)
    return "\n\n".join(
        [
            frontmatter,
            strip_local_include(constitution).strip(),
            role_body.strip(),
        ]
    ) + "\n"


def render_marketplace(repo_root: Path) -> None:
    marketplace_dir = repo_root / ".claude-plugin"
    marketplace_dir.mkdir(parents=True, exist_ok=True)
    marketplace = {
        "name": "agent-bootstrap",
        "description": "Marketplace for process-first Claude Code agents",
        "plugins": [
            {
                "name": "process-first-agents",
                "description": "Process-first shared agents for Claude Code",
                "version": "1.0.0",
                "source": "./plugins/process-first-agents",
            }
        ],
    }
    (marketplace_dir / "marketplace.json").write_text(
        json.dumps(marketplace, indent=2) + "\n",
        encoding="utf-8",
    )


def render_plugin_bundle(repo_root: Path, plugin_root: Path, partner_name: str) -> None:
    metadata_map = load_agent_metadata(repo_root)
    plugin_root.mkdir(parents=True, exist_ok=True)
    (plugin_root / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (plugin_root / "agents").mkdir(parents=True, exist_ok=True)

    manifest = {
        "name": "process-first-agents",
        "description": "Process-first shared agents for Claude Code",
        "version": "1.0.0",
        "author": PLUGIN_AUTHOR,
        "repository": PLUGIN_REPOSITORY,
        "license": "MIT",
        "keywords": ["claude-code", "agents", "process-first", "superpowers"],
    }
    (plugin_root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    (plugin_root / "settings.json").write_text(
        json.dumps({"agent": "eng-lead"}, indent=2) + "\n",
        encoding="utf-8",
    )

    for agent_source in sorted((repo_root / "agents").glob("*.md")):
        rendered = build_agent_markdown(repo_root, agent_source, partner_name, metadata_map)
        (plugin_root / "agents" / agent_source.name).write_text(rendered, encoding="utf-8")


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
        else (repo_root / PLUGIN_ROOT)
    )

    render_marketplace(repo_root)
    render_plugin_bundle(repo_root, plugin_root, args.partner_name)
    print(f"Rendered Claude plugin bundle at {plugin_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
