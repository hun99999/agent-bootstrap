#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CODEX_TEMPLATE_ROOT = ".codex/templates"
PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
DEFAULT_SUPERPOWERS_REMOTE = "https://github.com/obra/superpowers.git"
BACKUP_NAMESPACE = ("backups", "agent-bootstrap", "codex")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render and install the managed Codex dotfiles from this repository."
    )
    parser.add_argument(
        "--partner-name",
        required=True,
        help="Name Codex should use when addressing the user.",
    )
    parser.add_argument(
        "--codex-home",
        default="~/.codex",
        help="Target Codex home directory. Defaults to ~/.codex.",
    )
    parser.add_argument(
        "--agents-home",
        default="~/.agents",
        help="Target shared agents home directory. Defaults to ~/.agents.",
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
    parser.add_argument(
        "--superpowers-remote",
        default=DEFAULT_SUPERPOWERS_REMOTE,
        help="Git remote to sync into ~/.codex/superpowers. Defaults to obra/superpowers.",
    )
    parser.add_argument(
        "--superpowers-mode",
        choices=("manual", "skip"),
        default="manual",
        help="Control manual Superpowers checkout and symlink installation. Defaults to manual.",
    )
    return parser.parse_args()


def render_template(content: str, replacements: dict[str, str], source: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in replacements:
            raise ValueError(f"unknown placeholder '{key}' in {source}")
        return replacements[key]

    return PLACEHOLDER_PATTERN.sub(replace, content)


def shared_source_files(repo_root: Path) -> list[tuple[Path, Path]]:
    template_root = repo_root / CODEX_TEMPLATE_ROOT
    files: list[tuple[Path, Path]] = [
        (repo_root / "AGENTS.md", Path("AGENTS.md")),
        (template_root / "local.md", Path("local.md")),
        (template_root / "config.toml", Path("config.toml")),
    ]
    files.extend(
        (agent_path, Path("agents") / agent_path.name)
        for agent_path in sorted((repo_root / "agents").glob("*.md"))
    )
    files.extend(
        (agent_path, Path("agents") / agent_path.name)
        for agent_path in sorted((template_root / "agents").glob("*.toml"))
    )
    return files


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


def verify_install(
    target_root: Path,
    codex_home_abs: str,
    expected_prompt_paths: list[Path],
    expected_role_config_paths: list[Path],
) -> None:
    required_files = [
        target_root / "AGENTS.md",
        target_root / "local.md",
        target_root / "config.toml",
        *expected_prompt_paths,
        *expected_role_config_paths,
    ]
    missing = [path for path in required_files if not path.exists()]
    if missing:
        missing_str = ", ".join(str(path) for path in missing)
        raise RuntimeError(f"missing installed files: {missing_str}")

    config_text = (target_root / "config.toml").read_text(encoding="utf-8")
    for role_config_path in expected_role_config_paths:
        expected = f'config_file = "agents/{role_config_path.name}"'
        if expected not in config_text:
            raise RuntimeError(f"config.toml is missing expected role config: {expected}")

        role_config_text = role_config_path.read_text(encoding="utf-8")
        prompt_name = f"{role_config_path.stem}.md"
        expected_instruction = f'model_instructions_file = "{codex_home_abs}/agents/{prompt_name}"'
        if expected_instruction not in role_config_text:
            raise RuntimeError(
                f"{role_config_path} is missing expected model instructions file: {expected_instruction}"
            )
        if re.search(r"(?m)^\s*model\s*=", role_config_text):
            raise RuntimeError(f"{role_config_path} must not set role-level model")


def verify_superpowers_symlink(codex_home: Path, agents_home: Path) -> None:
    target = (codex_home / "superpowers" / "skills").resolve()
    link_path = agents_home / "skills" / "superpowers"
    if not link_path.is_symlink():
        raise RuntimeError(f"missing superpowers skills symlink: {link_path}")
    if link_path.resolve() != target:
        raise RuntimeError(
            f"superpowers skills symlink mismatch: expected {target}, found {link_path.resolve()}"
        )


def verify_superpowers_install(target_root: Path, expected_remote: str) -> str:
    superpowers_root = target_root / "superpowers"
    if not superpowers_root.is_dir():
        raise RuntimeError(f"missing installed superpowers repo: {superpowers_root}")

    current_remote = git_stdout(
        "remote",
        "get-url",
        "origin",
        cwd=superpowers_root,
    ).strip()
    if current_remote != expected_remote:
        raise RuntimeError(
            f"superpowers remote mismatch: expected {expected_remote}, found {current_remote}"
        )

    return git_stdout("rev-parse", "HEAD", cwd=superpowers_root).strip()


def print_install_plan(
    target_root: Path,
    agents_home: Path,
    relative_paths: list[Path],
    partner_name: str,
    superpowers_remote: str,
    superpowers_mode: str,
) -> None:
    print(f"Dry run: would install managed Codex files into {target_root}")
    print(f"Partner name: {partner_name}")
    print(f"Superpowers mode: {superpowers_mode}")
    print(f"Superpowers remote: {superpowers_remote}")
    print("Managed files:")
    for relative in relative_paths:
        print(f"- {target_root / relative}")
    if superpowers_mode == "manual":
        print(f"- {target_root / 'superpowers'}")
        print(f"- {agents_home / 'skills' / 'superpowers'}")


def git_stdout(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def path_is_git_repo(path: Path) -> bool:
    if not path.is_dir():
        return False
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=path,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def backup_superpowers_dir(target_root: Path, superpowers_root: Path) -> Path:
    backup_root = (
        target_root
        / Path(*BACKUP_NAMESPACE)
        / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    copy_to_backup(superpowers_root, backup_root / "superpowers")
    return backup_root


def require_clean_superpowers_checkout(superpowers_root: Path) -> None:
    status = git_stdout("status", "--short", cwd=superpowers_root)
    if status.strip():
        raise RuntimeError(f"dirty superpowers checkout: {superpowers_root}")


def prepare_superpowers_checkout(target_root: Path, remote: str) -> Path | None:
    superpowers_root = target_root / "superpowers"
    if not superpowers_root.exists():
        return None

    if not path_is_git_repo(superpowers_root):
        backup_root = backup_superpowers_dir(target_root, superpowers_root)
        remove_existing_path(superpowers_root)
        return backup_root

    current_remote = git_stdout("remote", "get-url", "origin", cwd=superpowers_root).strip()
    if current_remote != remote:
        backup_root = backup_superpowers_dir(target_root, superpowers_root)
        remove_existing_path(superpowers_root)
        return backup_root

    require_clean_superpowers_checkout(superpowers_root)
    return None


def sync_superpowers_repo(target_root: Path, remote: str) -> tuple[Path | None, str]:
    superpowers_root = target_root / "superpowers"
    backup_root = prepare_superpowers_checkout(target_root, remote)

    if not superpowers_root.exists():
        target_root.mkdir(parents=True, exist_ok=True)
        git_stdout("clone", "--depth", "1", remote, str(superpowers_root))
    else:
        git_stdout("fetch", "origin", cwd=superpowers_root)
        git_stdout("remote", "set-head", "origin", "-a", cwd=superpowers_root)
        remote_head = git_stdout(
            "symbolic-ref",
            "refs/remotes/origin/HEAD",
            "--short",
            cwd=superpowers_root,
        ).strip()
        branch_name = remote_head.split("/", maxsplit=1)[1]
        current_branch = git_stdout("branch", "--show-current", cwd=superpowers_root).strip()
        if current_branch != branch_name:
            raise RuntimeError(
                f"superpowers checkout is on {current_branch}, expected {branch_name}"
            )
        git_stdout("merge", "--ff-only", f"origin/{branch_name}", cwd=superpowers_root)

    commit = verify_superpowers_install(target_root, remote)
    return backup_root, commit


def remove_existing_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def ensure_superpowers_symlink(codex_home: Path, agents_home: Path) -> None:
    link_path = agents_home / "skills" / "superpowers"
    target = codex_home / "superpowers" / "skills"
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if link_path.is_symlink() and link_path.resolve() == target.resolve():
        return
    if link_path.exists() or link_path.is_symlink():
        raise RuntimeError(
            f"refusing to replace existing superpowers skills path: {link_path}"
        )
    link_path.symlink_to(target)


def main() -> int:
    args = parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    template_root = repo_root / CODEX_TEMPLATE_ROOT
    if not template_root.is_dir():
        raise SystemExit(f"template root not found: {template_root}")

    target_root = Path(args.codex_home).expanduser().resolve()
    agents_home = Path(args.agents_home).expanduser().resolve()
    replacements = {
        "PARTNER_NAME": args.partner_name,
        "CODEX_HOME_ABS": str(target_root),
    }

    managed_sources = shared_source_files(repo_root)
    files = [source for source, _ in managed_sources]
    relative_paths = [relative for _, relative in managed_sources]
    managed_paths = [target_root / relative for relative in relative_paths]

    if args.dry_run:
        print_install_plan(
            target_root,
            agents_home,
            relative_paths,
            args.partner_name,
            args.superpowers_remote,
            args.superpowers_mode,
        )
        return 0

    backup_root = backup_existing_paths(target_root, managed_paths)

    for source, relative in managed_sources:
        destination = target_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        rendered = render_template(source.read_text(encoding="utf-8"), replacements, source)
        destination.write_text(rendered, encoding="utf-8")

    superpowers_backup_root = None
    superpowers_commit = None
    if args.superpowers_mode == "manual":
        superpowers_backup_root, superpowers_commit = sync_superpowers_repo(
            target_root,
            args.superpowers_remote,
        )
        ensure_superpowers_symlink(target_root, agents_home)

    prompt_paths = [
        target_root / path
        for path in relative_paths
        if path.parts and path.parts[0] == "agents" and path.suffix == ".md"
    ]
    role_config_paths = [
        target_root / path
        for path in relative_paths
        if path.parts and path.parts[0] == "agents" and path.suffix == ".toml"
    ]
    verify_install(target_root, str(target_root), prompt_paths, role_config_paths)
    if args.superpowers_mode == "manual":
        verify_superpowers_symlink(target_root, agents_home)

    print(f"Installed managed Codex files into {target_root}")
    print(f"Partner name: {args.partner_name}")
    if backup_root is None and superpowers_backup_root is None:
        print("Backup: no existing managed files were present")
    else:
        print("Backup:")
        if backup_root is not None:
            print(f"- managed files: {backup_root}")
        if superpowers_backup_root is not None:
            print(f"- superpowers replacement: {superpowers_backup_root}")
    if args.superpowers_mode == "manual":
        print(f"Superpowers:")
        print(f"- remote: {args.superpowers_remote}")
        print(f"- path: {target_root / 'superpowers'}")
        print(f"- commit: {superpowers_commit}")
        print(f"- skills symlink: {agents_home / 'skills' / 'superpowers'}")
    else:
        print("Superpowers: skipped manual checkout and symlink")
    print("Managed files:")
    for relative in relative_paths:
        print(f"- {target_root / relative}")
    if args.superpowers_mode == "manual":
        print(f"- {target_root / 'superpowers'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as err:  # pragma: no cover
        print(f"install failed: {err}", file=sys.stderr)
        raise SystemExit(1)
