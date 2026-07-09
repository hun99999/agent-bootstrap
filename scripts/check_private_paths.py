#!/usr/bin/env python3
"""Scan tracked text files for concrete private paths and secret assignments."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


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
BASELINE_PATH = Path("design-stack/vendor-scan-baseline.json")
BASELINE_ALLOWED_PREFIXES = (
    "design-stack/vendor/",
    "plugins/frontend-design-pack/skills/frontend-design/references/mengto/",
    "plugins/frontend-design-pack/skills/frontend-design/references/design-md/",
    "plugins/frontend-design-pack/skills/frontend-design/references/vercel/",
    "plugins/frontend-design-pack/skills/frontend-design/references/contracts/",
    "plugins/frontend-design-pack/licenses/",
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    label: str
    excerpt: str


class BaselineError(ValueError):
    """Raised when a private-scan baseline is malformed or exceeds its scope."""


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


def _load_baseline(repo_root: Path) -> dict[str, dict[str, object]]:
    path = repo_root / BASELINE_PATH
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise BaselineError(f"invalid private-scan baseline JSON: {error}") from error
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise BaselineError("private-scan baseline schema_version must be 1")
    if set(payload) != {"schema_version", "entries"}:
        raise BaselineError("private-scan baseline has an unrecognized field")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise BaselineError("private-scan baseline entries must be a list")

    baseline: dict[str, dict[str, object]] = {}
    for index, raw_entry in enumerate(entries):
        context = f"private-scan baseline entry {index}"
        if not isinstance(raw_entry, dict):
            raise BaselineError(f"{context} must be an object")
        if set(raw_entry) != {"path", "sha256", "findings"}:
            raise BaselineError(f"{context} has an unrecognized field")
        relative_path = raw_entry.get("path")
        if not isinstance(relative_path, str) or not relative_path:
            raise BaselineError(f"{context} path must be a non-empty string")
        parsed_path = PurePosixPath(relative_path)
        if (
            parsed_path.is_absolute()
            or ".." in parsed_path.parts
            or "." in parsed_path.parts
            or parsed_path.as_posix() != relative_path
        ):
            raise BaselineError(f"{context} path must be a safe relative path")
        if not relative_path.startswith(BASELINE_ALLOWED_PREFIXES):
            raise BaselineError(f"{context} path is outside the baseline scope")
        if relative_path in baseline:
            raise BaselineError(f"duplicate private-scan baseline path: {relative_path}")
        digest = raw_entry.get("sha256")
        if not isinstance(digest, str) or SHA256_PATTERN.fullmatch(digest) is None:
            raise BaselineError(f"{context} SHA-256 must be a lowercase digest")
        raw_findings = raw_entry.get("findings")
        if not isinstance(raw_findings, list):
            raise BaselineError(f"{context} findings must be a list")
        normalized_findings: set[tuple[str, int, str]] = set()
        for finding_index, raw_finding in enumerate(raw_findings):
            finding_context = f"{context} finding {finding_index}"
            if not isinstance(raw_finding, dict):
                raise BaselineError(f"{finding_context} must be an object")
            if set(raw_finding) != {"label", "line", "excerpt"}:
                raise BaselineError(f"{finding_context} has an unrecognized field")
            label = raw_finding.get("label")
            line = raw_finding.get("line")
            excerpt = raw_finding.get("excerpt")
            if not isinstance(label, str) or not label:
                raise BaselineError(f"{finding_context} label is invalid")
            if not isinstance(line, int) or isinstance(line, bool) or line < 1:
                raise BaselineError(f"{finding_context} line is invalid")
            if not isinstance(excerpt, str):
                raise BaselineError(f"{finding_context} excerpt is invalid")
            key = (label, line, excerpt)
            if key in normalized_findings:
                raise BaselineError(f"duplicate {finding_context}")
            normalized_findings.add(key)
        baseline[relative_path] = {
            "sha256": digest,
            "findings": normalized_findings,
        }
    return baseline


def _relative_scanned_paths(repo_root: Path, paths: list[Path]) -> dict[str, Path]:
    root = repo_root.resolve()
    relative_paths: dict[str, Path] = {}
    for path in paths:
        resolved = path.resolve()
        try:
            relative = resolved.relative_to(root).as_posix()
        except ValueError as error:
            raise BaselineError(f"scan path is outside the repository: {path}") from error
        relative_paths[relative] = path
    return relative_paths


def scan_repository_paths(repo_root: Path, paths: list[Path]) -> list[Finding]:
    repo_root = repo_root.resolve()
    scanned_paths = _relative_scanned_paths(repo_root, paths)
    baseline = _load_baseline(repo_root)
    raw_findings = scan_paths(
        [
            path
            for relative, path in scanned_paths.items()
            if relative != BASELINE_PATH.as_posix()
        ]
    )
    findings_by_path: dict[str, list[Finding]] = {}
    for finding in raw_findings:
        relative = Path(finding.path).resolve().relative_to(repo_root).as_posix()
        findings_by_path.setdefault(relative, []).append(finding)

    retained = list(raw_findings)
    baseline_errors: list[Finding] = []
    for relative_path, entry in baseline.items():
        target = repo_root / relative_path
        if not target.is_file():
            baseline_errors.append(
                Finding(relative_path, 0, "baseline-error", "baseline target is missing")
            )
            continue
        if relative_path not in scanned_paths:
            baseline_errors.append(
                Finding(relative_path, 0, "baseline-error", "baseline target was not scanned")
            )
            continue
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            baseline_errors.append(
                Finding(relative_path, 0, "baseline-error", "baseline SHA-256 differs")
            )
            continue
        expected = entry["findings"]
        actual = {
            (finding.label, finding.line, finding.excerpt)
            for finding in findings_by_path.get(relative_path, [])
        }
        missing_expected = expected - actual
        if missing_expected:
            baseline_errors.append(
                Finding(
                    relative_path,
                    0,
                    "baseline-error",
                    "recorded baseline finding no longer matches",
                )
            )
        retained = [
            finding
            for finding in retained
            if not (
                Path(finding.path).resolve().relative_to(repo_root).as_posix()
                == relative_path
                and (finding.label, finding.line, finding.excerpt) in expected
            )
        ]
    return retained + baseline_errors


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
    try:
        findings = scan_repository_paths(repo_root, tracked_files(repo_root))
    except BaselineError as error:
        print(f"Private path scan: invalid baseline: {error}")
        return 1
    print(render_findings(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
