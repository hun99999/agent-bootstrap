#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from design_stack import ValidationError, validate_repository


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
    except ValidationError as error:
        print(f"Frontend design stack validation failed: {error}")
        return 1
    mode = "metadata" if args.metadata_only else "full"
    print(f"Frontend design stack {mode} validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
