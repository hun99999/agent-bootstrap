#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from design_stack import ValidationError, validate_repository
from render_frontend_design_plugin import (
    PLUGIN_ROOT,
    validate_runtime_copy,
    validate_tracked_plugin,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the frontend design source registry, lock, and provenance ledger."
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root. Defaults to the parent of this script directory.",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Validate reviewed metadata without requiring vendored source bytes.",
    )
    parser.add_argument(
        "--codex-runtime-root",
        default=None,
        help="Optional installed Codex plugin root to compare with the tracked plugin.",
    )
    parser.add_argument(
        "--claude-runtime-root",
        default=None,
        help="Optional installed Claude plugin root to compare with the tracked plugin.",
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
        validate_repository(repo_root, metadata_only=args.metadata_only)
        if not args.metadata_only:
            tracked_plugin = repo_root / PLUGIN_ROOT
            validate_tracked_plugin(repo_root, tracked_plugin)
            if args.codex_runtime_root:
                validate_runtime_copy(
                    tracked_plugin,
                    Path(args.codex_runtime_root).expanduser().resolve(),
                    "Codex",
                )
            if args.claude_runtime_root:
                validate_runtime_copy(
                    tracked_plugin,
                    Path(args.claude_runtime_root).expanduser().resolve(),
                    "Claude",
                )
    except ValidationError as error:
        print(f"Frontend design stack validation failed: {error}")
        return 1
    mode = "metadata" if args.metadata_only else "full"
    print(f"Frontend design stack {mode} validation: ok")
    if args.codex_runtime_root:
        print("Codex runtime plugin validation: ok")
    if args.claude_runtime_root:
        print("Claude runtime plugin validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
