#!/usr/bin/env python3
"""Scan tracked text files for concrete private paths and secret assignments."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


MAC_USER_PREFIX = "/" + "Users/"
WINDOWS_USER_PREFIX = "C:" + "\\Users\\"

PRIVATE_PATTERNS = (
    (
        "private-user-path",
        re.compile(
            rf"({re.escape(MAC_USER_PREFIX)}[^\s`'\"<>]+|{re.escape(WINDOWS_USER_PREFIX)}[^\s`'\"<>]+)"
        ),
    ),
    (
        "secret-assignment",
        re.compile(
            r"(?i)\b[A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|API_KEY|AUTH_COOKIE)\b\s*[:=]\s*['\"]?[^'\"\s]+"
        ),
    ),
)
DEFAULT_EXCLUDED_SUFFIXES = {
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".zip",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    label: str
    excerpt: str


def tracked_files(repo_root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [repo_root / line for line in result.stdout.splitlines() if line.strip()]


def should_scan(path: Path) -> bool:
    if path.suffix.lower() in DEFAULT_EXCLUDED_SUFFIXES:
        return False
    return True


def scan_text(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for label, pattern in PRIVATE_PATTERNS:
            if pattern.search(line):
                findings.append(
                    Finding(
                        path=str(path),
                        line=line_number,
                        label=label,
                        excerpt=line.strip()[:160],
                    )
                )
    return findings


def scan_paths(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        if not should_scan(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        findings.extend(scan_text(path, text))
    return findings


def render_findings(findings: list[Finding]) -> str:
    if not findings:
        return "Private path scan: ok"
    lines = ["Private path scan: findings"]
    for finding in findings:
        lines.append(f"- {finding.path}:{finding.line}: {finding.label}: {finding.excerpt}")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root. Defaults to the current directory.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    findings = scan_paths(tracked_files(repo_root))
    print(render_findings(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
