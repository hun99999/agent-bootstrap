#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


RECEIPT_NAME = ".frontend-design-receipt.json"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class OpenDesignError(ValueError):
    pass


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _git_blob_sha1(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()


def _safe_relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenDesignError(f"{label} must be a non-empty relative path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or "\\" in value
        or ".." in path.parts
        or "." in path.parts
        or path.as_posix() != value
        or any(not part for part in path.parts)
        or any(ord(character) < 32 for character in value)
    ):
        raise OpenDesignError(f"{label} is not a safe canonical relative path: {value}")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OpenDesignError(f"{label} must be a non-empty string")
    return value


def _validate_provider(provider: Mapping[str, Any]) -> None:
    if not isinstance(provider, Mapping) or provider.get("schema_version") != 1:
        raise OpenDesignError("Open Design provider schema_version must be 1")
    required = {
        "schema_version",
        "provider_id",
        "repository",
        "revision",
        "root_tree",
        "package_root",
        "package_index_path",
        "scope",
        "authority",
        "distribution",
        "license",
        "slug_pattern",
        "required_files",
        "manifest_contract",
        "network_policy",
        "cache_write_policy",
        "corrupt_cache_policy",
        "cache_namespace",
        "limits",
    }
    if set(provider) != required:
        raise OpenDesignError("Open Design provider fields are incomplete or unsupported")
    if provider["provider_id"] != "open-design":
        raise OpenDesignError("Open Design provider_id must be open-design")
    _require_string(provider["repository"], "provider.repository")
    if HEX_40.fullmatch(str(provider["revision"])) is None:
        raise OpenDesignError("provider.revision must be a full Git commit")
    if HEX_40.fullmatch(str(provider["root_tree"])) is None:
        raise OpenDesignError("provider.root_tree must be a full Git tree")
    package_root = _safe_relative_path(provider["package_root"], "provider.package_root")
    index_path = _safe_relative_path(
        provider["package_index_path"], "provider.package_index_path"
    )
    if not index_path.startswith(package_root + "/"):
        raise OpenDesignError("provider package index must be inside package_root")
    if provider["authority"] != "optional-provider":
        raise OpenDesignError("provider authority must be optional-provider")
    if provider["distribution"] != "on-demand":
        raise OpenDesignError("provider distribution must be on-demand")
    if provider["network_policy"] != "explicit-demand-only":
        raise OpenDesignError("provider network policy must be explicit-demand-only")
    if provider["cache_write_policy"] != "selected-package-only":
        raise OpenDesignError("provider cache policy must be selected-package-only")
    if provider["corrupt_cache_policy"] != "fail-without-mutation":
        raise OpenDesignError("provider corrupt cache policy must fail without mutation")
    if provider["cache_namespace"] != "open-design":
        raise OpenDesignError("provider cache namespace must be open-design")
    if provider["slug_pattern"] != "^[a-z0-9]+(?:-[a-z0-9]+)*$":
        raise OpenDesignError("provider slug pattern is not approved")
    required_files = provider["required_files"]
    if required_files != ["manifest.json", "DESIGN.md", "tokens.css"]:
        raise OpenDesignError("provider required files are not the approved set")
    for path in required_files:
        _safe_relative_path(path, "provider required file")
    manifest_contract = provider["manifest_contract"]
    if manifest_contract != {
        "schema_version": "od-design-system-project/v1",
        "design": "DESIGN.md",
        "tokens": "tokens.css",
    }:
        raise OpenDesignError("provider manifest contract is not approved")
    license_record = provider["license"]
    if not isinstance(license_record, Mapping) or set(license_record) != {
        "spdx",
        "status",
        "path",
        "sha256",
        "size",
    }:
        raise OpenDesignError("provider license contract is incomplete")
    if license_record["spdx"] != "Apache-2.0" or license_record["status"] != "verified":
        raise OpenDesignError("provider root license must remain verified Apache-2.0")
    _safe_relative_path(license_record["path"], "provider license path")
    if SHA256.fullmatch(str(license_record["sha256"])) is None:
        raise OpenDesignError("provider license SHA-256 is invalid")
    if not isinstance(license_record["size"], int) or license_record["size"] <= 0:
        raise OpenDesignError("provider license size is invalid")
    limits = provider["limits"]
    if not isinstance(limits, Mapping) or set(limits) != {
        "max_files",
        "max_file_bytes",
        "max_total_bytes",
    }:
        raise OpenDesignError("provider limits are incomplete")
    for field in ("max_files", "max_file_bytes", "max_total_bytes"):
        if not isinstance(limits[field], int) or limits[field] <= 0:
            raise OpenDesignError(f"provider limit {field} must be positive")


def _validate_slug(provider: Mapping[str, Any], slug: str) -> str:
    if not isinstance(slug, str) or re.fullmatch(provider["slug_pattern"], slug) is None:
        raise OpenDesignError(f"invalid Open Design package slug: {slug!r}")
    return slug


def _run_git(arguments: Sequence[str], *, binary: bool = False) -> str | bytes:
    environment = os.environ.copy()
    environment["GIT_TERMINAL_PROMPT"] = "0"
    result = subprocess.run(
        ["git", *arguments],
        capture_output=True,
        env=environment,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise OpenDesignError(message or f"git command failed: {' '.join(arguments)}")
    if binary:
        return result.stdout
    try:
        return result.stdout.decode("utf-8").strip()
    except UnicodeDecodeError as error:
        raise OpenDesignError("git output contains a non-UTF-8 path") from error


class _FetchedRepository:
    def __init__(self, provider: Mapping[str, Any]) -> None:
        self.provider = provider
        self._temporary: tempfile.TemporaryDirectory[str] | None = None
        self.path: Path | None = None

    def __enter__(self) -> Path:
        self._temporary = tempfile.TemporaryDirectory(prefix="open-design-fetch-")
        self.path = Path(self._temporary.name) / "source.git"
        try:
            _run_git(["init", "--bare", str(self.path)])
            _run_git(
                [
                    "-C",
                    str(self.path),
                    "fetch",
                    "--depth=1",
                    "--filter=blob:none",
                    "--no-tags",
                    self.provider["repository"],
                    self.provider["revision"],
                ]
            )
            root_tree = _run_git(
                ["-C", str(self.path), "rev-parse", "FETCH_HEAD^{tree}"]
            )
            if root_tree != self.provider["root_tree"]:
                raise OpenDesignError(
                    f"pinned Open Design root tree differs: {root_tree}"
                )
        except BaseException:
            self._temporary.cleanup()
            self._temporary = None
            self.path = None
            raise
        return self.path

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self._temporary is not None:
            self._temporary.cleanup()


def _direct_package_slugs(
    repository: Path,
    provider: Mapping[str, Any],
) -> list[str]:
    raw = _run_git(
        [
            "-C",
            str(repository),
            "ls-tree",
            "-z",
            f"FETCH_HEAD:{provider['package_root']}",
        ],
        binary=True,
    )
    assert isinstance(raw, bytes)
    slugs: list[str] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, name_bytes = record.split(b"\t", 1)
            mode, object_type, _ = metadata.decode("ascii").split()
            name = name_bytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as error:
            raise OpenDesignError("malformed Open Design package tree entry") from error
        if object_type != "tree" or mode != "040000":
            continue
        if re.fullmatch(provider["slug_pattern"], name):
            slugs.append(name)
    return sorted(slugs)


def list_packages(provider: Mapping[str, Any]) -> dict[str, Any]:
    _validate_provider(provider)
    with _FetchedRepository(provider) as repository:
        packages = _direct_package_slugs(repository, provider)
    return {
        "provider_id": provider["provider_id"],
        "revision": provider["revision"],
        "root_tree": provider["root_tree"],
        "packages": packages,
    }


def _parse_tree_files(raw: bytes) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, path_bytes = record.split(b"\t", 1)
            mode_bytes, type_bytes, oid_bytes, size_bytes = metadata.split()
            mode = mode_bytes.decode("ascii")
            object_type = type_bytes.decode("ascii")
            oid = oid_bytes.decode("ascii")
            size_text = size_bytes.decode("ascii")
            source_path = path_bytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as error:
            raise OpenDesignError("malformed Open Design Git tree entry") from error
        _safe_relative_path(source_path, "Open Design source path")
        if source_path in seen:
            raise OpenDesignError(f"duplicate Open Design source path: {source_path}")
        seen.add(source_path)
        if mode != "100644" or object_type != "blob":
            raise OpenDesignError(
                f"Open Design entries must be regular non-executable files; "
                f"found mode {mode} type {object_type}: {source_path}"
            )
        if HEX_40.fullmatch(oid) is None or not size_text.isdigit():
            raise OpenDesignError(f"invalid Open Design blob metadata: {source_path}")
        files.append(
            {
                "source_path": source_path,
                "mode": mode,
                "git_blob_sha1": oid,
                "size": int(size_text),
            }
        )
    return files


def _selected_tree_files(
    repository: Path,
    provider: Mapping[str, Any],
    slug: str,
) -> tuple[str, list[dict[str, Any]]]:
    package_source_root = f"{provider['package_root']}/{slug}"
    package_tree = _run_git(
        ["-C", str(repository), "rev-parse", f"FETCH_HEAD:{package_source_root}"]
    )
    if not isinstance(package_tree, str) or HEX_40.fullmatch(package_tree) is None:
        raise OpenDesignError(f"Open Design package is not a Git tree: {slug}")
    raw = _run_git(
        [
            "-C",
            str(repository),
            "ls-tree",
            "-r",
            "-z",
            "--long",
            "--full-tree",
            "FETCH_HEAD",
            "--",
            provider["license"]["path"],
            provider["package_index_path"],
            package_source_root,
        ],
        binary=True,
    )
    assert isinstance(raw, bytes)
    files = _parse_tree_files(raw)
    allowed_exact = {
        provider["license"]["path"],
        provider["package_index_path"],
    }
    package_prefix = package_source_root + "/"
    for file_record in files:
        source_path = file_record["source_path"]
        if source_path not in allowed_exact and not source_path.startswith(
            package_prefix
        ):
            raise OpenDesignError(f"unexpected Open Design source path: {source_path}")
    limits = provider["limits"]
    if len(files) > limits["max_files"]:
        raise OpenDesignError("Open Design package exceeds the file-count limit")
    total_size = 0
    for file_record in files:
        if file_record["size"] > limits["max_file_bytes"]:
            raise OpenDesignError(
                f"Open Design file exceeds the size limit: {file_record['source_path']}"
            )
        total_size += file_record["size"]
    if total_size > limits["max_total_bytes"]:
        raise OpenDesignError("Open Design package exceeds the total-size limit")
    return package_tree, files


def _destination_path(
    provider: Mapping[str, Any],
    slug: str,
    source_path: str,
) -> str:
    if source_path == provider["license"]["path"]:
        return "_provider/LICENSE"
    if source_path == provider["package_index_path"]:
        return "_provider/README.md"
    prefix = f"{provider['package_root']}/{slug}/"
    if not source_path.startswith(prefix):
        raise OpenDesignError(f"source path is outside selected package: {source_path}")
    relative = source_path[len(prefix) :]
    _safe_relative_path(relative, "Open Design package-relative path")
    return f"package/{relative}"


def _validate_manifest(
    provider: Mapping[str, Any],
    slug: str,
    package_root: Path,
) -> None:
    missing = [
        path for path in provider["required_files"] if not (package_root / path).is_file()
    ]
    if missing:
        raise OpenDesignError(f"Open Design package is missing required files: {missing}")
    manifest_path = package_root / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OpenDesignError("Open Design manifest is not valid UTF-8 JSON") from error
    if not isinstance(manifest, dict):
        raise OpenDesignError("Open Design manifest must be an object")
    contract = provider["manifest_contract"]
    if manifest.get("schemaVersion") != contract["schema_version"]:
        raise OpenDesignError("Open Design manifest schema is not approved")
    if manifest.get("id") != slug:
        raise OpenDesignError("Open Design manifest id does not match the selected slug")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise OpenDesignError("Open Design manifest files must be an object")
    if files.get("design") != contract["design"] or files.get("tokens") != contract[
        "tokens"
    ]:
        raise OpenDesignError("Open Design manifest canonical files are not approved")


def _ensure_real_directory(path: Path, label: str) -> None:
    if path.is_symlink():
        raise OpenDesignError(f"{label} must not be a symlink: {path}")
    if path.exists() and not path.is_dir():
        raise OpenDesignError(f"{label} must be a directory: {path}")


def _cache_revision_root(
    provider: Mapping[str, Any],
    cache_root: Path,
    *,
    create: bool,
) -> Path:
    cache_root = cache_root.expanduser()
    components = (
        (cache_root, "Open Design cache root"),
        (cache_root / provider["provider_id"], "Open Design cache namespace"),
        (
            cache_root / provider["provider_id"] / provider["revision"],
            "Open Design revision cache",
        ),
    )
    for path, label in components:
        _ensure_real_directory(path, label)
        if create:
            path.mkdir(parents=True, exist_ok=True)
            _ensure_real_directory(path, label)
        elif not path.is_dir():
            raise OpenDesignError(f"{label} is missing: {path}")
    return components[-1][0]


def _receipt_result(
    provider: Mapping[str, Any],
    slug: str,
    cache_path: Path,
    status: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "provider_id": provider["provider_id"],
        "revision": provider["revision"],
        "slug": slug,
        "authority": provider["authority"],
        "cache_path": str(cache_path.resolve()),
        "package_root": str((cache_path / "package").resolve()),
        "receipt_path": str((cache_path / RECEIPT_NAME).resolve()),
    }


def _verify_cache_path(
    provider: Mapping[str, Any],
    slug: str,
    cache_path: Path,
) -> dict[str, Any]:
    if cache_path.is_symlink() or not cache_path.is_dir():
        raise OpenDesignError(f"Open Design cache is missing or unsafe: {cache_path}")
    receipt_path = cache_path / RECEIPT_NAME
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise OpenDesignError("Open Design cache receipt is missing or unsafe")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OpenDesignError("Open Design cache receipt is invalid") from error
    expected_receipt_values = {
        "schema_version": 1,
        "provider_id": provider["provider_id"],
        "repository": provider["repository"],
        "revision": provider["revision"],
        "root_tree": provider["root_tree"],
        "package_slug": slug,
        "authority": provider["authority"],
        "scope": f"{provider['package_root']}/{slug}/**",
        "package_root": "package",
        "attribution_path": "_provider/README.md",
    }
    if not isinstance(receipt, dict):
        raise OpenDesignError("Open Design cache receipt must be an object")
    for field, expected in expected_receipt_values.items():
        if receipt.get(field) != expected:
            raise OpenDesignError(f"Open Design cache receipt {field} differs")
    if HEX_40.fullmatch(str(receipt.get("package_tree", ""))) is None:
        raise OpenDesignError("Open Design cache receipt package tree is invalid")
    if not isinstance(receipt.get("retrieved_at"), str) or not receipt["retrieved_at"]:
        raise OpenDesignError("Open Design cache receipt retrieval time is missing")
    if receipt.get("license") != provider["license"]:
        raise OpenDesignError("Open Design cache receipt license differs")
    file_records = receipt.get("files")
    if not isinstance(file_records, list) or not file_records:
        raise OpenDesignError("Open Design cache receipt file list is missing")
    expected_files: dict[str, Mapping[str, Any]] = {}
    for index, record in enumerate(file_records):
        if not isinstance(record, Mapping) or set(record) != {
            "path",
            "source_path",
            "mode",
            "size",
            "git_blob_sha1",
            "sha256",
        }:
            raise OpenDesignError(f"Open Design cache file record {index} is invalid")
        relative_path = _safe_relative_path(record["path"], "cache receipt path")
        _safe_relative_path(record["source_path"], "cache receipt source path")
        if relative_path in expected_files:
            raise OpenDesignError(f"duplicate Open Design cache receipt path: {relative_path}")
        if record["mode"] != "100644":
            raise OpenDesignError(f"Open Design cache mode differs: {relative_path}")
        if not isinstance(record["size"], int) or record["size"] < 0:
            raise OpenDesignError(f"Open Design cache size is invalid: {relative_path}")
        if HEX_40.fullmatch(str(record["git_blob_sha1"])) is None:
            raise OpenDesignError(f"Open Design cache blob hash is invalid: {relative_path}")
        if SHA256.fullmatch(str(record["sha256"])) is None:
            raise OpenDesignError(f"Open Design cache SHA-256 is invalid: {relative_path}")
        expected_files[relative_path] = record

    actual_files: dict[str, Path] = {}
    for path in cache_path.rglob("*"):
        relative = path.relative_to(cache_path).as_posix()
        if path.is_symlink():
            raise OpenDesignError(f"Open Design cache contains a symlink: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise OpenDesignError(f"Open Design cache contains a special file: {relative}")
        if relative == RECEIPT_NAME:
            continue
        actual_files[relative] = path
    missing = sorted(set(expected_files) - set(actual_files))
    unexpected = sorted(set(actual_files) - set(expected_files))
    if missing or unexpected:
        raise OpenDesignError(
            f"Open Design cache file set differs; missing={missing}, unexpected={unexpected}"
        )
    for relative_path, record in expected_files.items():
        path = actual_files[relative_path]
        mode = path.stat().st_mode
        if not stat.S_ISREG(mode) or mode & 0o111:
            raise OpenDesignError(f"Open Design cache mode differs: {relative_path}")
        content = path.read_bytes()
        if len(content) != record["size"]:
            raise OpenDesignError(f"Open Design cache size differs: {relative_path}")
        if _sha256(content) != record["sha256"]:
            raise OpenDesignError(f"Open Design cache hash differs: {relative_path}")
        if _git_blob_sha1(content) != record["git_blob_sha1"]:
            raise OpenDesignError(f"Open Design cache blob hash differs: {relative_path}")
    _validate_manifest(provider, slug, cache_path / "package")
    return receipt


def verify_package(
    provider: Mapping[str, Any],
    slug: str,
    cache_root: Path,
) -> dict[str, Any]:
    _validate_provider(provider)
    _validate_slug(provider, slug)
    revision_root = _cache_revision_root(
        provider,
        Path(cache_root),
        create=False,
    )
    target = revision_root / slug
    _verify_cache_path(provider, slug, target)
    return _receipt_result(provider, slug, target, "verified")


def fetch_package(
    provider: Mapping[str, Any],
    slug: str,
    cache_root: Path,
) -> dict[str, Any]:
    _validate_provider(provider)
    _validate_slug(provider, slug)
    cache_root = Path(cache_root).expanduser()
    revision_root = _cache_revision_root(provider, cache_root, create=True)
    target = revision_root / slug
    if target.exists() or target.is_symlink():
        _verify_cache_path(provider, slug, target)
        return _receipt_result(provider, slug, target, "reused")

    with _FetchedRepository(provider) as repository:
        packages = _direct_package_slugs(repository, provider)
        if slug not in packages:
            raise OpenDesignError(f"Open Design package slug does not exist: {slug}")
        package_tree, files = _selected_tree_files(repository, provider, slug)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{slug}.staging-", dir=revision_root)
        )
        try:
            records: list[dict[str, Any]] = []
            for file_record in files:
                content = _run_git(
                    [
                        "-C",
                        str(repository),
                        "cat-file",
                        "blob",
                        file_record["git_blob_sha1"],
                    ],
                    binary=True,
                )
                assert isinstance(content, bytes)
                if len(content) != file_record["size"]:
                    raise OpenDesignError(
                        f"Open Design blob size differs: {file_record['source_path']}"
                    )
                if _git_blob_sha1(content) != file_record["git_blob_sha1"]:
                    raise OpenDesignError(
                        f"Open Design blob hash differs: {file_record['source_path']}"
                    )
                destination_relative = _destination_path(
                    provider,
                    slug,
                    file_record["source_path"],
                )
                destination = staging.joinpath(*PurePosixPath(destination_relative).parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
                destination.chmod(0o644)
                records.append(
                    {
                        "path": destination_relative,
                        "source_path": file_record["source_path"],
                        "mode": file_record["mode"],
                        "size": len(content),
                        "git_blob_sha1": file_record["git_blob_sha1"],
                        "sha256": _sha256(content),
                    }
                )
            license_record = next(
                record
                for record in records
                if record["source_path"] == provider["license"]["path"]
            )
            if (
                license_record["sha256"] != provider["license"]["sha256"]
                or license_record["size"] != provider["license"]["size"]
            ):
                raise OpenDesignError("Open Design root license hash or size differs")
            _validate_manifest(provider, slug, staging / "package")
            receipt = {
                "schema_version": 1,
                "provider_id": provider["provider_id"],
                "repository": provider["repository"],
                "revision": provider["revision"],
                "root_tree": provider["root_tree"],
                "package_slug": slug,
                "package_tree": package_tree,
                "authority": provider["authority"],
                "scope": f"{provider['package_root']}/{slug}/**",
                "license": provider["license"],
                "attribution_path": "_provider/README.md",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "package_root": "package",
                "files": sorted(records, key=lambda record: record["path"]),
            }
            receipt_path = staging / RECEIPT_NAME
            receipt_path.write_text(
                json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            receipt_path.chmod(0o600)
            _verify_cache_path(provider, slug, staging)
            if target.exists() or target.is_symlink():
                _verify_cache_path(provider, slug, target)
                return _receipt_result(provider, slug, target, "reused")
            os.rename(staging, target)
            return _receipt_result(provider, slug, target, "fetched")
        finally:
            if staging.exists() or staging.is_symlink():
                if staging.is_dir() and not staging.is_symlink():
                    shutil.rmtree(staging)
                else:
                    staging.unlink()


def default_cache_root() -> Path:
    override = os.environ.get("FRONTEND_DESIGN_CACHE_ROOT")
    if override:
        return Path(override).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library/Caches/frontend-design"
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg).expanduser() / "frontend-design"
    return Path.home() / ".cache/frontend-design"


def _load_packaged_provider() -> Mapping[str, Any]:
    path = Path(__file__).resolve().parent.parent / "references/open-design-provider.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OpenDesignError(f"cannot load packaged Open Design provider: {path}") from error
    if not isinstance(payload, Mapping):
        raise OpenDesignError("packaged Open Design provider must be an object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List, fetch, or verify one pinned Open Design package."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("list", "fetch", "verify"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument(
            "--explicit-demand",
            action="store_true",
            help="Acknowledge that the user explicitly requested Open Design.",
        )
        subparser.add_argument("--json", action="store_true")
        if command in {"fetch", "verify"}:
            subparser.add_argument("--slug", required=True)
            subparser.add_argument("--cache-root", type=Path)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not args.explicit_demand:
        parser.error("explicit demand acknowledgement is required")
    provider = _load_packaged_provider()
    if args.command == "list":
        result = list_packages(provider)
    elif args.command == "fetch":
        result = fetch_package(
            provider,
            args.slug,
            args.cache_root or default_cache_root(),
        )
    else:
        result = verify_package(
            provider,
            args.slug,
            args.cache_root or default_cache_root(),
        )
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OpenDesignError as error:
        print(f"Open Design cache error: {error}", file=sys.stderr)
        raise SystemExit(1)
