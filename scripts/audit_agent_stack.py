#!/usr/bin/env python3
"""Audit local AI agent tooling for drift without modifying the system."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


CLI_CHECKS = (
    ("codex", ("codex", "--version"), "@openai/codex", True),
    ("claude", ("claude", "--version"), "@anthropic-ai/claude-code", True),
)

FAILING_STATUSES = {"dirty", "error", "update-available"}
VERSION_PATTERN = re.compile(r"\d+(?:\.\d+)+(?:[-+][0-9A-Za-z.-]+)?")
CLAUDE_PLUGIN_ROOT = Path("plugins/process-first-agents")


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    required: bool
    installed: str | None = None
    latest: str | None = None
    detail: str | None = None


def run_command(
    command: list[str] | tuple[str, ...],
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def parse_version(output: str) -> str | None:
    match = VERSION_PATTERN.search(output)
    if match is None:
        return None
    return match.group(0)


def version_key(version: str) -> tuple[int, ...]:
    numeric = version.split("-", 1)[0].split("+", 1)[0]
    return tuple(int(part) for part in numeric.split("."))


def compare_versions(installed: str, latest: str) -> int:
    installed_key = version_key(installed)
    latest_key = version_key(latest)
    max_length = max(len(installed_key), len(latest_key))
    padded_installed = installed_key + (0,) * (max_length - len(installed_key))
    padded_latest = latest_key + (0,) * (max_length - len(latest_key))
    if padded_installed < padded_latest:
        return -1
    if padded_installed > padded_latest:
        return 1
    return 0


def read_npm_latest(package_name: str) -> str | None:
    if shutil.which("npm") is None:
        return None

    result = run_command(("npm", "view", package_name, "version"))
    if result.returncode != 0:
        return None
    return parse_version(result.stdout)


def check_cli(
    name: str,
    command: tuple[str, ...],
    package_name: str | None,
    required: bool,
    online: bool,
) -> CheckResult:
    executable = command[0]
    if shutil.which(executable) is None:
        return CheckResult(
            name=name,
            status="missing",
            required=required,
            detail=f"{executable} is not installed or not on PATH",
        )

    version_result = run_command(command)
    if version_result.returncode != 0:
        return CheckResult(
            name=name,
            status="error",
            required=required,
            detail=(version_result.stderr or version_result.stdout).strip(),
        )

    installed = parse_version(version_result.stdout)
    if installed is None:
        return CheckResult(
            name=name,
            status="error",
            required=required,
            detail=f"Could not parse version from: {version_result.stdout.strip()}",
        )

    if not online or package_name is None:
        return CheckResult(
            name=name,
            status="ok",
            required=required,
            installed=installed,
        )

    latest = read_npm_latest(package_name)
    if latest is None:
        return CheckResult(
            name=name,
            status="error",
            required=required,
            installed=installed,
            detail=f"Could not read latest npm version for {package_name}",
        )

    if compare_versions(installed, latest) < 0:
        return CheckResult(
            name=name,
            status="update-available",
            required=required,
            installed=installed,
            latest=latest,
            detail=f"Update {package_name} from {installed} to {latest}",
        )

    detail = None
    if compare_versions(installed, latest) > 0:
        detail = f"Installed version {installed} is newer than npm latest {latest}"

    return CheckResult(
        name=name,
        status="ok",
        required=required,
        installed=installed,
        latest=latest,
        detail=detail,
    )


def parse_ls_remote_head(output: str) -> str | None:
    first_line = output.splitlines()[0] if output.splitlines() else ""
    parts = first_line.split()
    if not parts:
        return None
    return parts[0]


def read_offline_origin_head(path: Path) -> str | None:
    for ref in ("refs/remotes/origin/HEAD^{commit}", "origin/main^{commit}"):
        result = run_command(("git", "-C", str(path), "rev-parse", "--verify", ref))
        if result.returncode == 0:
            return result.stdout.strip()
    return None


def read_online_origin_head(path: Path) -> str | None:
    result = run_command(("git", "-C", str(path), "ls-remote", "origin", "HEAD"))
    if result.returncode != 0:
        return None
    return parse_ls_remote_head(result.stdout)


def check_superpowers_symlink(superpowers_path: Path, agents_home: Path) -> str | None:
    link_path = agents_home.expanduser() / "skills" / "superpowers"
    expected_target = superpowers_path.expanduser() / "skills"

    if not link_path.exists():
        return f"skills symlink is missing: {link_path}"
    if not link_path.is_symlink():
        return f"skills path exists but is not a symlink: {link_path}"
    if link_path.resolve() != expected_target.resolve():
        return (
            f"skills symlink points to {link_path.resolve()} "
            f"instead of {expected_target.resolve()}"
        )
    return None


def check_superpowers(superpowers_path: Path, agents_home: Path, online: bool) -> CheckResult:
    path = superpowers_path.expanduser()
    if not path.exists():
        return CheckResult(
            name="superpowers",
            status="missing",
            required=True,
            detail=f"{path} does not exist",
        )

    if shutil.which("git") is None:
        return CheckResult(
            name="superpowers",
            status="error",
            required=True,
            detail="git is not installed or not on PATH",
        )

    status_result = run_command(("git", "-C", str(path), "status", "--short"))
    if status_result.returncode != 0:
        return CheckResult(
            name="superpowers",
            status="error",
            required=True,
            detail=(status_result.stderr or status_result.stdout).strip(),
        )
    if status_result.stdout.strip():
        return CheckResult(
            name="superpowers",
            status="dirty",
            required=True,
            detail=f"{path} has uncommitted changes",
        )

    symlink_error = check_superpowers_symlink(path, agents_home)
    if symlink_error is not None:
        return CheckResult(
            name="superpowers",
            status="error",
            required=True,
            detail=symlink_error,
        )

    local_result = run_command(("git", "-C", str(path), "rev-parse", "HEAD"))
    if local_result.returncode != 0:
        return CheckResult(
            name="superpowers",
            status="error",
            required=True,
            detail=(local_result.stderr or local_result.stdout).strip(),
        )

    local_sha = local_result.stdout.strip()
    remote_sha = read_online_origin_head(path) if online else read_offline_origin_head(path)
    if remote_sha is None:
        return CheckResult(
            name="superpowers",
            status="ok",
            required=True,
            installed=local_sha,
            detail="Could not read origin HEAD; checked local cleanliness and skills symlink only",
        )

    if local_sha != remote_sha:
        return CheckResult(
            name="superpowers",
            status="update-available",
            required=True,
            installed=local_sha,
            latest=remote_sha,
            detail="Fast-forward ~/.codex/superpowers to origin/HEAD",
        )

    return CheckResult(
        name="superpowers",
        status="ok",
        required=True,
        installed=local_sha,
        latest=remote_sha,
    )


def load_renderer_module(repo_root: Path):
    renderer_path = repo_root / "scripts" / "render_claude_plugin.py"
    spec = importlib.util.spec_from_file_location("render_claude_plugin_for_audit", renderer_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load renderer module from {renderer_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative_file_map(root: Path) -> dict[Path, Path]:
    return {
        path.relative_to(root): path
        for path in root.rglob("*")
        if path.is_file()
    }


def compare_file_trees(expected_root: Path, actual_root: Path) -> list[str]:
    expected_files = relative_file_map(expected_root)
    actual_files = relative_file_map(actual_root)
    differences = []

    for relative in sorted(expected_files.keys() - actual_files.keys()):
        differences.append(f"missing {relative}")
    for relative in sorted(actual_files.keys() - expected_files.keys()):
        differences.append(f"unexpected {relative}")
    for relative in sorted(expected_files.keys() & actual_files.keys()):
        if expected_files[relative].read_bytes() != actual_files[relative].read_bytes():
            differences.append(f"changed {relative}")

    return differences


def check_claude_generated_bundle(repo_root: Path) -> CheckResult:
    actual_root = repo_root / CLAUDE_PLUGIN_ROOT
    if not actual_root.exists():
        return CheckResult(
            name="claude-generated-bundle",
            status="missing",
            required=True,
            detail=f"{actual_root} does not exist",
        )

    try:
        renderer = load_renderer_module(repo_root)
        with tempfile.TemporaryDirectory() as tmpdir:
            expected_root = Path(tmpdir) / "process-first-agents"
            renderer.render_plugin_bundle(repo_root, expected_root, "Hun")
            differences = compare_file_trees(expected_root, actual_root)
    except Exception as err:
        return CheckResult(
            name="claude-generated-bundle",
            status="error",
            required=True,
            detail=str(err),
        )

    if differences:
        preview = ", ".join(differences[:5])
        if len(differences) > 5:
            preview = f"{preview}, and {len(differences) - 5} more"
        return CheckResult(
            name="claude-generated-bundle",
            status="error",
            required=True,
            detail=f"generated Claude plugin bundle is stale: {preview}",
        )

    return CheckResult(
        name="claude-generated-bundle",
        status="ok",
        required=True,
    )


def run_audit(
    repo_root: Path,
    superpowers_path: Path,
    agents_home: Path,
    online: bool,
    repo_only: bool = False,
) -> list[CheckResult]:
    if repo_only:
        return [check_claude_generated_bundle(repo_root)]

    checks = [
        check_cli(name, command, package_name, required, online)
        for name, command, package_name, required in CLI_CHECKS
    ]
    checks.append(check_superpowers(superpowers_path, agents_home, online))
    checks.append(check_claude_generated_bundle(repo_root))
    return checks


def should_fail(checks: list[CheckResult], strict: bool) -> bool:
    for check in checks:
        if check.status in FAILING_STATUSES:
            return True
        if check.status == "missing" and (strict or check.required):
            return True
    return False


def render_text(checks: list[CheckResult]) -> str:
    lines = ["Agent stack audit:"]
    for check in checks:
        requirement = "required" if check.required else "optional"
        version_bits = [requirement]
        if check.installed is not None:
            version_bits.append(f"installed {check.installed}")
        if check.latest is not None:
            version_bits.append(f"latest {check.latest}")

        suffix = f" ({', '.join(version_bits)})"
        if check.detail:
            suffix = f"{suffix} - {check.detail}"

        lines.append(f"- {check.name}: {check.status}{suffix}")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root. Defaults to the parent of this script directory.",
    )
    parser.add_argument(
        "--superpowers-path",
        default="~/.codex/superpowers",
        help="Path to the local obra/superpowers checkout.",
    )
    parser.add_argument(
        "--agents-home",
        default="~/.agents",
        help="Path to the local agents home that contains skills/superpowers.",
    )
    parser.add_argument(
        "--online",
        action="store_true",
        help="Fetch latest package/git metadata from npm and remote git endpoints.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of text.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat missing optional tools as failures.",
    )
    parser.add_argument(
        "--repo-only",
        action="store_true",
        help="Skip local CLI and user-home checks; verify repository-generated artifacts only.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo_root = (
        Path(args.repo_root).expanduser().resolve()
        if args.repo_root
        else Path(__file__).resolve().parents[1]
    )
    checks = run_audit(
        repo_root,
        Path(args.superpowers_path),
        Path(args.agents_home),
        args.online,
        args.repo_only,
    )
    failed = should_fail(checks, args.strict)

    if args.json:
        payload = {
            "ok": not failed,
            "online": args.online,
            "repo_only": args.repo_only,
            "checks": [asdict(check) for check in checks],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(checks))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
