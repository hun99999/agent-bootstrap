#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import stat
import subprocess
import tarfile
import urllib.request
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = REPO_ROOT / "benchmarks" / "skill-up.lock.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install the pinned skill-up binary locally.")
    parser.add_argument(
        "--destination",
        type=Path,
        help="Binary path. Defaults to .tools/skill-up/<version>/skill-up.",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing binary.")
    return parser.parse_args()


def platform_key() -> str:
    systems = {"darwin": "darwin", "linux": "linux", "windows": "windows"}
    machines = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
    system = systems.get(platform.system().casefold())
    machine = machines.get(platform.machine().casefold())
    if system is None or machine is None:
        raise RuntimeError(f"unsupported platform: {platform.system()} {platform.machine()}")
    return f"{system}-{machine}"


def load_lock() -> dict[str, object]:
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def default_destination(version: str, target_platform: str) -> Path:
    executable = "skill-up.exe" if target_platform.startswith("windows-") else "skill-up"
    return REPO_ROOT / ".tools" / "skill-up" / version / executable


def extract_binary(archive: bytes, filename: str) -> bytes:
    if filename.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            candidates = [name for name in bundle.namelist() if Path(name).name in {"skill-up", "skill-up.exe"}]
            if len(candidates) != 1:
                raise RuntimeError("release archive does not contain exactly one skill-up binary")
            return bundle.read(candidates[0])

    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
        candidates = [member for member in bundle.getmembers() if member.isfile() and Path(member.name).name == "skill-up"]
        if len(candidates) != 1:
            raise RuntimeError("release archive does not contain exactly one skill-up binary")
        extracted = bundle.extractfile(candidates[0])
        if extracted is None:
            raise RuntimeError("failed to read skill-up binary from release archive")
        return extracted.read()


def main() -> int:
    args = parse_args()
    lock = load_lock()
    version = str(lock["version"])
    target_platform = platform_key()
    destination = args.destination or default_destination(version, target_platform)
    destination = destination.expanduser().resolve()

    if destination.exists() and not args.force:
        result = subprocess.run([str(destination), "--version"], capture_output=True, text=True)
        if result.returncode == 0 and version in result.stdout + result.stderr:
            print(destination)
            return 0
        raise RuntimeError(f"existing binary is not skill-up {version}: {destination}")

    asset = lock["assets"][target_platform]
    filename = str(asset["file"])
    url = f'{lock["release_base_url"]}/{filename}'
    with urllib.request.urlopen(url, timeout=60) as response:
        archive = response.read()
    actual_sha = hashlib.sha256(archive).hexdigest()
    if actual_sha != asset["sha256"]:
        raise RuntimeError(f"checksum mismatch for {filename}: {actual_sha}")

    binary = extract_binary(archive, filename)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_bytes(binary)
    temporary.chmod(temporary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    os.replace(temporary, destination)

    result = subprocess.run([str(destination), "--version"], capture_output=True, text=True)
    if result.returncode != 0 or version not in result.stdout + result.stderr:
        raise RuntimeError(f"installed binary did not report version {version}")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
