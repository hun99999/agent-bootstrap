#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
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
ROLE_REASONING_EFFORT_PATTERN = re.compile(
    r'(?m)^\s*model_reasoning_effort\s*=\s*"(none|minimal|low|medium|high|xhigh|max|ultra)"\s*$'
)
TOML_HEADER_PATTERN = re.compile(r"^\s*(\[\[?[^\]]+\]\]?)\s*(?:#.*)?$")
TOML_KEY_PART = r'(?:[A-Za-z0-9_-]+|"(?:\\.|[^"\\])*"|\'[^\']*\')'
TOML_ASSIGNMENT_PATTERN = re.compile(
    rf"^\s*({TOML_KEY_PART}(?:\s*\.\s*{TOML_KEY_PART})*)\s*="
)
TOML_KEY_PART_PATTERN = re.compile(TOML_KEY_PART)


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
        default="skip",
        help="Control the optional manual Superpowers checkout and symlink. Defaults to skip.",
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


def existing_role_reasoning_efforts(
    target_root: Path,
    relative_paths: list[Path],
) -> dict[Path, str]:
    efforts: dict[Path, str] = {}
    for relative in relative_paths:
        if relative.parent != Path("agents") or relative.suffix != ".toml":
            continue
        destination = target_root / relative
        if not destination.is_file():
            continue
        match = ROLE_REASONING_EFFORT_PATTERN.search(destination.read_text(encoding="utf-8"))
        if match is not None:
            efforts[relative] = match.group(1)
    return efforts


def apply_role_reasoning_effort(rendered: str, effort: str | None) -> str:
    if effort is None:
        return rendered
    without_existing = ROLE_REASONING_EFFORT_PATTERN.sub("", rendered).rstrip()
    return f'{without_existing}\nmodel_reasoning_effort = "{effort}"\n'


def existing_machine_local_config(target_root: Path) -> str | None:
    config_path = target_root / "config.toml"
    if not config_path.is_file():
        return None
    return config_path.read_text(encoding="utf-8")


def split_toml_sections(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    preamble: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current_header: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        match = TOML_HEADER_PATTERN.match(line)
        if match is not None:
            if current_header is None:
                preamble.extend(current_lines)
            else:
                sections.append((current_header, current_lines))
            current_header = match.group(1)
            current_lines = [line]
            continue
        current_lines.append(line)

    if current_header is None:
        preamble.extend(current_lines)
    else:
        sections.append((current_header, current_lines))
    return preamble, sections


def canonical_toml_key(raw_key: str) -> tuple[str, ...]:
    parts: list[str] = []
    for match in TOML_KEY_PART_PATTERN.finditer(raw_key):
        part = match.group(0)
        if part.startswith('"'):
            parts.append(ast.literal_eval(part))
        elif part.startswith("'"):
            parts.append(part[1:-1])
        else:
            parts.append(part)
    return tuple(parts)


def assignment_chunks(lines: list[str]) -> list[tuple[tuple[str, ...], list[str]]]:
    chunks: list[tuple[tuple[str, ...], list[str]]] = []
    current_key: tuple[str, ...] | None = None
    current_lines: list[str] = []

    for line in lines:
        match = TOML_ASSIGNMENT_PATTERN.match(line)
        if match is not None:
            if current_key is not None:
                chunks.append((current_key, current_lines))
            current_key = canonical_toml_key(match.group(1))
            current_lines = [line]
            continue
        if current_key is not None:
            current_lines.append(line)

    if current_key is not None:
        chunks.append((current_key, current_lines))
    return chunks


def merge_assignment_bodies(template_lines: list[str], existing_lines: list[str]) -> list[str]:
    template_chunks = assignment_chunks(template_lines)
    template_keys = {key for key, _ in template_chunks}
    existing_chunks = [
        lines
        for key, lines in assignment_chunks(existing_lines)
        if key not in template_keys
    ]
    merged = [line for _, lines in template_chunks for line in lines]
    if merged and existing_chunks and merged[-1].strip():
        merged.append("")
    for index, lines in enumerate(existing_chunks):
        if index and merged and merged[-1].strip():
            merged.append("")
        merged.extend(lines)
    return merged


def apply_machine_local_config(
    rendered: str,
    existing: str | None,
) -> str:
    if existing is None:
        return rendered

    template_preamble, template_sections = split_toml_sections(rendered)
    existing_preamble, existing_sections = split_toml_sections(existing)
    merged_preamble = merge_assignment_bodies(template_preamble, existing_preamble)

    existing_by_header: dict[str, list[list[str]]] = {}
    for header, lines in existing_sections:
        existing_by_header.setdefault(header, []).append(lines)

    merged_sections: list[list[str]] = []
    for header, template_lines in template_sections:
        matching = existing_by_header.pop(header, [])
        if header.startswith("[[") or not matching:
            merged_sections.append(template_lines)
            continue
        existing_lines = matching[0]
        merged_body = merge_assignment_bodies(
            template_lines[1:],
            existing_lines[1:],
        )
        merged_sections.append([template_lines[0], *merged_body])
        if len(matching) > 1:
            merged_sections.extend(matching[1:])

    for _, sections in existing_by_header.items():
        merged_sections.extend(sections)

    blocks = ["\n".join(merged_preamble).strip()]
    blocks.extend("\n".join(lines).strip() for lines in merged_sections)
    return "\n\n".join(block for block in blocks if block).rstrip() + "\n"


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
        ["git", "rev-parse", "--show-toplevel"],
        cwd=path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False
    return Path(result.stdout.strip()).resolve() == path.resolve()


def require_clean_superpowers_checkout(superpowers_root: Path) -> None:
    status = git_stdout("status", "--short", cwd=superpowers_root)
    if status.strip():
        raise RuntimeError(f"dirty superpowers checkout: {superpowers_root}")


def superpowers_remote_head_branch(superpowers_root: Path) -> str:
    git_stdout("fetch", "origin", cwd=superpowers_root)
    git_stdout("remote", "set-head", "origin", "-a", cwd=superpowers_root)
    remote_head = git_stdout(
        "symbolic-ref",
        "refs/remotes/origin/HEAD",
        "--short",
        cwd=superpowers_root,
    ).strip()
    return remote_head.split("/", maxsplit=1)[1]


def require_superpowers_checkout_on_remote_head(superpowers_root: Path) -> str:
    branch_name = superpowers_remote_head_branch(superpowers_root)
    current_branch = git_stdout("branch", "--show-current", cwd=superpowers_root).strip()
    if current_branch != branch_name:
        raise RuntimeError(
            f"superpowers checkout is on {current_branch}, expected {branch_name}"
        )
    return branch_name


def require_superpowers_checkout_can_fast_forward(superpowers_root: Path, branch_name: str) -> None:
    remote_ref = f"origin/{branch_name}"
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", "HEAD", remote_ref],
        cwd=superpowers_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cannot fast-forward superpowers checkout: {superpowers_root} to {remote_ref}"
        )


def preflight_superpowers_install(
    target_root: Path,
    agents_home: Path,
    remote: str,
    mode: str,
) -> None:
    if mode != "manual":
        return

    superpowers_root = target_root / "superpowers"
    if superpowers_root.exists():
        if not path_is_git_repo(superpowers_root):
            raise RuntimeError(f"refusing to replace existing superpowers path: {superpowers_root}")

        current_remote = git_stdout("remote", "get-url", "origin", cwd=superpowers_root).strip()
        if current_remote != remote:
            raise RuntimeError(
                f"superpowers remote mismatch: expected {remote}, found {current_remote}"
            )

        require_clean_superpowers_checkout(superpowers_root)
        branch_name = require_superpowers_checkout_on_remote_head(superpowers_root)
        require_superpowers_checkout_can_fast_forward(superpowers_root, branch_name)

    link_path = agents_home / "skills" / "superpowers"
    target = target_root / "superpowers" / "skills"
    if link_path.is_symlink() and link_path.resolve() == target.resolve():
        return
    if link_path.exists() or link_path.is_symlink():
        raise RuntimeError(
            f"refusing to replace existing superpowers skills path: {link_path}"
        )


def prepare_superpowers_checkout(target_root: Path, remote: str) -> Path | None:
    superpowers_root = target_root / "superpowers"
    if not superpowers_root.exists():
        return None

    if not path_is_git_repo(superpowers_root):
        raise RuntimeError(f"refusing to replace existing superpowers path: {superpowers_root}")

    current_remote = git_stdout("remote", "get-url", "origin", cwd=superpowers_root).strip()
    if current_remote != remote:
        raise RuntimeError(
            f"superpowers remote mismatch: expected {remote}, found {current_remote}"
        )

    require_clean_superpowers_checkout(superpowers_root)
    return None


def sync_superpowers_repo(target_root: Path, remote: str) -> tuple[Path | None, str]:
    superpowers_root = target_root / "superpowers"
    backup_root = prepare_superpowers_checkout(target_root, remote)

    if not superpowers_root.exists():
        target_root.mkdir(parents=True, exist_ok=True)
        git_stdout("clone", "--depth", "1", remote, str(superpowers_root))
    else:
        branch_name = require_superpowers_checkout_on_remote_head(superpowers_root)
        require_superpowers_checkout_can_fast_forward(superpowers_root, branch_name)
        git_stdout("merge", "--ff-only", f"origin/{branch_name}", cwd=superpowers_root)

    commit = verify_superpowers_install(target_root, remote)
    return backup_root, commit


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
    role_reasoning_efforts = existing_role_reasoning_efforts(target_root, relative_paths)
    machine_local_config = existing_machine_local_config(target_root)

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

    preflight_superpowers_install(
        target_root,
        agents_home,
        args.superpowers_remote,
        args.superpowers_mode,
    )

    backup_root = backup_existing_paths(target_root, managed_paths)

    for source, relative in managed_sources:
        destination = target_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        rendered = render_template(source.read_text(encoding="utf-8"), replacements, source)
        rendered = apply_role_reasoning_effort(
            rendered,
            role_reasoning_efforts.get(relative),
        )
        if relative == Path("config.toml"):
            rendered = apply_machine_local_config(
                rendered,
                machine_local_config,
            )
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
    if machine_local_config is None:
        print("Runtime policy: inherited target defaults; the public template pins no model or effort")
    else:
        print("Runtime policy: preserved target model, effort, profiles, and unmanaged settings")
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
