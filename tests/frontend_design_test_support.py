import importlib.util
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_script_module(script_name: str):
    script_path = REPO_ROOT / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load script module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(script_path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(script_path.parent))
    return module


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sha256_bytes(content: bytes) -> str:
    import hashlib

    return hashlib.sha256(content).hexdigest()


def write_files(root: Path, files: Mapping[str, bytes]) -> None:
    for relative_path, content in files.items():
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)


def snapshot_tree(root: Path) -> Dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


def run_git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def init_git_repo(root: Path, branch: str = "main") -> None:
    root.mkdir(parents=True, exist_ok=True)
    run_git(root, "init", "--initial-branch", branch)
    run_git(root, "config", "user.name", "Frontend Design Tests")
    run_git(root, "config", "user.email", "frontend-design-tests@example.com")


def commit_all(root: Path, message: str = "fixture") -> str:
    run_git(root, "add", ".")
    run_git(root, "commit", "-m", message)
    return run_git(root, "rev-parse", "HEAD")


def write_tar(
    archive_path: Path,
    root_name: str,
    files: Mapping[str, bytes],
    modes: Optional[Mapping[str, int]] = None,
    extra_members: Iterable[tarfile.TarInfo] = (),
) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "w") as archive:
        root_info = tarfile.TarInfo(root_name)
        root_info.type = tarfile.DIRTYPE
        root_info.mode = 0o755
        archive.addfile(root_info)
        for relative_path, content in files.items():
            info = tarfile.TarInfo(f"{root_name}/{relative_path}")
            info.size = len(content)
            info.mode = (modes or {}).get(relative_path, 0o644)
            archive.addfile(info, io.BytesIO(content))
        for member in extra_members:
            archive.addfile(member)
