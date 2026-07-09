#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import binascii
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
RECEIPT_SCHEMA_VERSION = 2
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
RAW_TREE_ENTRY_TYPES = {
    b"40000": ("040000", "tree"),
    b"100644": ("100644", "blob"),
    b"100755": ("100755", "blob"),
    b"120000": ("120000", "blob"),
    b"160000": ("160000", "commit"),
}


class OpenDesignError(ValueError):
    pass


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _git_blob_sha1(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()


def _git_tree_sha1(body: bytes) -> str:
    header = f"tree {len(body)}\0".encode("ascii")
    return hashlib.sha1(header + body, usedforsecurity=False).hexdigest()


def _parse_raw_tree(body: bytes) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen: set[bytes] = set()
    cursor = 0
    while cursor < len(body):
        space = body.find(b" ", cursor)
        terminator = body.find(b"\0", space + 1)
        if space <= cursor or terminator <= space + 1 or terminator + 21 > len(body):
            raise OpenDesignError("Open Design raw Git tree is malformed")
        raw_mode = body[cursor:space]
        name = body[space + 1 : terminator]
        raw_oid = body[terminator + 1 : terminator + 21]
        if raw_mode not in RAW_TREE_ENTRY_TYPES:
            raise OpenDesignError("Open Design raw Git tree mode is invalid")
        if not name or name in {b".", b".."} or b"/" in name:
            raise OpenDesignError("Open Design raw Git tree name is invalid")
        if name in seen:
            raise OpenDesignError("Open Design raw Git tree has a duplicate name")
        seen.add(name)
        mode, object_type = RAW_TREE_ENTRY_TYPES[raw_mode]
        entries.append(
            {
                "name": name,
                "mode": mode,
                "type": object_type,
                "oid": raw_oid.hex(),
            }
        )
        cursor = terminator + 21
    return entries


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
            fetched_revision = _run_git(
                ["-C", str(self.path), "rev-parse", "FETCH_HEAD"]
            )
            if fetched_revision != self.provider["revision"]:
                raise OpenDesignError(
                    f"fetched Open Design revision differs: {fetched_revision}"
                )
            object_type = _run_git(
                ["-C", str(self.path), "cat-file", "-t", "FETCH_HEAD"]
            )
            if object_type != "commit":
                raise OpenDesignError(
                    "pinned Open Design revision must resolve to a commit"
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


def _build_tree_proof(
    repository: Path,
    package_source_root: str,
    source_paths: Sequence[str],
) -> list[dict[str, Any]]:
    directory_paths = {""}
    for source_path in source_paths:
        parts = PurePosixPath(source_path).parts
        for depth in range(1, len(parts)):
            directory_paths.add("/".join(parts[:depth]))

    proof_by_path: dict[str, dict[str, Any]] = {}

    def load_tree(directory_path: str) -> list[dict[str, Any]]:
        existing = proof_by_path.get(directory_path)
        if existing is not None:
            return existing["parsed_entries"]
        tree_spec = (
            "FETCH_HEAD^{tree}"
            if not directory_path
            else f"FETCH_HEAD:{directory_path}"
        )
        tree_oid = _run_git(
            ["-C", str(repository), "rev-parse", tree_spec]
        )
        if not isinstance(tree_oid, str) or HEX_40.fullmatch(tree_oid) is None:
            raise OpenDesignError(
                f"Open Design proof path is not a Git tree: {directory_path or '.'}"
            )
        body = _run_git(
            ["-C", str(repository), "cat-file", "tree", tree_oid],
            binary=True,
        )
        assert isinstance(body, bytes)
        _parse_raw_tree(body)
        if _git_tree_sha1(body) != tree_oid:
            raise OpenDesignError(
                f"Open Design proof tree differs: {directory_path or '.'}"
            )
        parsed_entries = _parse_raw_tree(body)
        proof_by_path[directory_path] = {
            "path": directory_path,
            "tree": tree_oid,
            "body_base64": base64.b64encode(body).decode("ascii"),
            "parsed_entries": parsed_entries,
        }
        return parsed_entries

    for directory_path in directory_paths:
        load_tree(directory_path)

    pending = [package_source_root]
    visited: set[str] = set()
    while pending:
        directory_path = pending.pop()
        if directory_path in visited:
            continue
        visited.add(directory_path)
        for entry in load_tree(directory_path):
            if entry["mode"] != "040000":
                continue
            try:
                name = entry["name"].decode("utf-8")
            except UnicodeDecodeError as error:
                raise OpenDesignError(
                    "Open Design selected package tree has a non-UTF-8 path"
                ) from error
            child_path = f"{directory_path}/{name}"
            _safe_relative_path(child_path, "Open Design selected package tree path")
            pending.append(child_path)

    proof: list[dict[str, Any]] = []
    for directory_path in sorted(
        proof_by_path,
        key=lambda value: (len(PurePosixPath(value).parts), value.encode("utf-8")),
    ):
        node = dict(proof_by_path[directory_path])
        node.pop("parsed_entries")
        proof.append(node)
    return proof


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


def _proof_path_sort_key(value: str) -> tuple[int, bytes]:
    return (len(PurePosixPath(value).parts), value.encode("utf-8"))


def _load_tree_proof(
    provider: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    raw_proof = receipt.get("tree_proof")
    if not isinstance(raw_proof, list) or not raw_proof:
        raise OpenDesignError("Open Design cache tree proof is missing")
    if len(raw_proof) > provider["limits"]["max_files"] * 2 + 16:
        raise OpenDesignError("Open Design cache tree proof has too many nodes")

    nodes: dict[str, dict[str, Any]] = {}
    total_body_bytes = 0
    paths: list[str] = []
    for index, raw_node in enumerate(raw_proof):
        if not isinstance(raw_node, Mapping) or set(raw_node) != {
            "path",
            "tree",
            "body_base64",
        }:
            raise OpenDesignError(f"Open Design cache tree proof node {index} is invalid")
        path = raw_node["path"]
        if path != "":
            path = _safe_relative_path(path, "cache tree proof path")
        if path in nodes:
            raise OpenDesignError(f"duplicate Open Design cache tree proof path: {path}")
        tree_oid = raw_node["tree"]
        if HEX_40.fullmatch(str(tree_oid)) is None:
            raise OpenDesignError(f"Open Design cache tree proof OID is invalid: {path}")
        encoded_body = raw_node["body_base64"]
        if not isinstance(encoded_body, str) or not encoded_body:
            raise OpenDesignError(f"Open Design cache tree proof body is invalid: {path}")
        try:
            body = base64.b64decode(encoded_body, validate=True)
        except (ValueError, binascii.Error) as error:
            raise OpenDesignError(
                f"Open Design cache tree proof body is invalid: {path}"
            ) from error
        total_body_bytes += len(body)
        if total_body_bytes > provider["limits"]["max_total_bytes"]:
            raise OpenDesignError("Open Design cache tree proof exceeds the size limit")
        if _git_tree_sha1(body) != tree_oid:
            raise OpenDesignError(f"Open Design cache tree proof hash differs: {path}")
        entries = _parse_raw_tree(body)
        nodes[path] = {
            "tree": tree_oid,
            "entries": entries,
            "entries_by_name": {entry["name"]: entry for entry in entries},
        }
        paths.append(path)

    if paths != sorted(paths, key=_proof_path_sort_key):
        raise OpenDesignError("Open Design cache tree proof paths are not canonical")
    root = nodes.get("")
    if root is None or root["tree"] != provider["root_tree"]:
        raise OpenDesignError("Open Design cache tree proof is not pinned to the root tree")
    return nodes


def _linked_tree_node(
    nodes: Mapping[str, Mapping[str, Any]],
    directory_path: str,
    visited: set[str],
) -> Mapping[str, Any]:
    current_path = ""
    current = nodes.get(current_path)
    if current is None:
        raise OpenDesignError("Open Design cache root tree proof is missing")
    visited.add(current_path)
    if not directory_path:
        return current

    _safe_relative_path(directory_path, "cache tree proof directory")
    for component in PurePosixPath(directory_path).parts:
        entry = current["entries_by_name"].get(component.encode("utf-8"))
        if entry is None or entry["mode"] != "040000" or entry["type"] != "tree":
            raise OpenDesignError(
                f"Open Design cache tree proof path is not anchored: {directory_path}"
            )
        current_path = (
            component if not current_path else f"{current_path}/{component}"
        )
        child = nodes.get(current_path)
        if child is None:
            raise OpenDesignError(
                f"Open Design cache child tree proof is missing: {current_path}"
            )
        if child["tree"] != entry["oid"]:
            raise OpenDesignError(
                f"Open Design cache child tree proof differs: {current_path}"
            )
        visited.add(current_path)
        current = child
    return current


def _anchored_blob_oid(
    nodes: Mapping[str, Mapping[str, Any]],
    source_path: str,
    visited: set[str],
) -> str:
    source_path = _safe_relative_path(source_path, "cache proof source path")
    parts = PurePosixPath(source_path).parts
    parent_path = "/".join(parts[:-1])
    parent = _linked_tree_node(nodes, parent_path, visited)
    entry = parent["entries_by_name"].get(parts[-1].encode("utf-8"))
    if entry is None or entry["mode"] != "100644" or entry["type"] != "blob":
        raise OpenDesignError(
            f"Open Design cache file is not an anchored regular blob: {source_path}"
        )
    return entry["oid"]


def _walk_anchored_package(
    nodes: Mapping[str, Mapping[str, Any]],
    package_source_root: str,
    visited: set[str],
) -> tuple[str, dict[str, str]]:
    package_node = _linked_tree_node(nodes, package_source_root, visited)
    package_files: dict[str, str] = {}

    def walk(directory_path: str, node: Mapping[str, Any]) -> None:
        for entry in node["entries"]:
            try:
                name = entry["name"].decode("utf-8")
            except UnicodeDecodeError as error:
                raise OpenDesignError(
                    "Open Design selected package proof has a non-UTF-8 path"
                ) from error
            source_path = f"{directory_path}/{name}"
            _safe_relative_path(source_path, "selected package proof path")
            if entry["mode"] == "040000" and entry["type"] == "tree":
                child = nodes.get(source_path)
                if child is None:
                    raise OpenDesignError(
                        f"Open Design selected package child proof is missing: {source_path}"
                    )
                if child["tree"] != entry["oid"]:
                    raise OpenDesignError(
                        f"Open Design selected package child proof differs: {source_path}"
                    )
                visited.add(source_path)
                walk(source_path, child)
            elif entry["mode"] == "100644" and entry["type"] == "blob":
                package_files[source_path] = entry["oid"]
            else:
                raise OpenDesignError(
                    "Open Design selected package proof contains a non-regular entry: "
                    f"{source_path}"
                )

    walk(package_source_root, package_node)
    return package_node["tree"], package_files


def _anchored_expected_files(
    provider: Mapping[str, Any],
    slug: str,
    receipt: Mapping[str, Any],
) -> dict[str, dict[str, str]]:
    nodes = _load_tree_proof(provider, receipt)
    visited: set[str] = set()
    package_source_root = f"{provider['package_root']}/{slug}"
    package_tree, package_files = _walk_anchored_package(
        nodes,
        package_source_root,
        visited,
    )
    if receipt.get("package_tree") != package_tree:
        raise OpenDesignError("Open Design cache package tree differs from its proof")

    source_oids = {
        provider["license"]["path"]: _anchored_blob_oid(
            nodes,
            provider["license"]["path"],
            visited,
        ),
        provider["package_index_path"]: _anchored_blob_oid(
            nodes,
            provider["package_index_path"],
            visited,
        ),
    }
    for source_path, oid in package_files.items():
        if source_path in source_oids:
            raise OpenDesignError(
                f"duplicate Open Design anchored source path: {source_path}"
            )
        source_oids[source_path] = oid
    if set(nodes) != visited:
        raise OpenDesignError("Open Design cache tree proof contains unused nodes")

    expected: dict[str, dict[str, str]] = {}
    for source_path, oid in source_oids.items():
        destination = _destination_path(provider, slug, source_path)
        if destination in expected:
            raise OpenDesignError(
                f"duplicate Open Design anchored destination: {destination}"
            )
        expected[destination] = {
            "source_path": source_path,
            "git_blob_sha1": oid,
        }
    return expected


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
        "schema_version": RECEIPT_SCHEMA_VERSION,
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
    expected_receipt_fields = set(expected_receipt_values) | {
        "package_tree",
        "retrieved_at",
        "license",
        "files",
        "tree_proof",
    }
    if set(receipt) != expected_receipt_fields:
        raise OpenDesignError("Open Design cache receipt fields are not recognized")
    for field, expected in expected_receipt_values.items():
        if receipt.get(field) != expected:
            raise OpenDesignError(f"Open Design cache receipt {field} differs")
    if HEX_40.fullmatch(str(receipt.get("package_tree", ""))) is None:
        raise OpenDesignError("Open Design cache receipt package tree is invalid")
    if not isinstance(receipt.get("retrieved_at"), str) or not receipt["retrieved_at"]:
        raise OpenDesignError("Open Design cache receipt retrieval time is missing")
    if receipt.get("license") != provider["license"]:
        raise OpenDesignError("Open Design cache receipt license differs")
    anchored_files = _anchored_expected_files(provider, slug, receipt)
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
        source_path = _safe_relative_path(
            record["source_path"],
            "cache receipt source path",
        )
        if relative_path in expected_files:
            raise OpenDesignError(f"duplicate Open Design cache receipt path: {relative_path}")
        anchored = anchored_files.get(relative_path)
        if anchored is None:
            raise OpenDesignError(
                f"Open Design cache receipt path is outside the anchored file set: {relative_path}"
            )
        if source_path != anchored["source_path"]:
            raise OpenDesignError(
                f"Open Design cache receipt source path differs: {relative_path}"
            )
        if record["mode"] != "100644":
            raise OpenDesignError(f"Open Design cache mode differs: {relative_path}")
        if not isinstance(record["size"], int) or record["size"] < 0:
            raise OpenDesignError(f"Open Design cache size is invalid: {relative_path}")
        if HEX_40.fullmatch(str(record["git_blob_sha1"])) is None:
            raise OpenDesignError(f"Open Design cache blob hash is invalid: {relative_path}")
        if record["git_blob_sha1"] != anchored["git_blob_sha1"]:
            raise OpenDesignError(
                f"Open Design cache blob hash differs from its tree proof: {relative_path}"
            )
        if SHA256.fullmatch(str(record["sha256"])) is None:
            raise OpenDesignError(f"Open Design cache SHA-256 is invalid: {relative_path}")
        expected_files[relative_path] = record
    missing_records = sorted(set(anchored_files) - set(expected_files))
    if missing_records:
        raise OpenDesignError(
            f"Open Design cache receipt is missing anchored files: {missing_records}"
        )

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
    total_size = 0
    for relative_path, record in expected_files.items():
        path = actual_files[relative_path]
        mode = path.stat().st_mode
        if not stat.S_ISREG(mode) or mode & 0o111:
            raise OpenDesignError(f"Open Design cache mode differs: {relative_path}")
        content = path.read_bytes()
        total_size += len(content)
        if len(content) != record["size"]:
            raise OpenDesignError(f"Open Design cache size differs: {relative_path}")
        if _sha256(content) != record["sha256"]:
            raise OpenDesignError(f"Open Design cache hash differs: {relative_path}")
        if _git_blob_sha1(content) != record["git_blob_sha1"]:
            raise OpenDesignError(f"Open Design cache blob hash differs: {relative_path}")
        if relative_path == "_provider/LICENSE" and (
            len(content) != provider["license"]["size"]
            or _sha256(content) != provider["license"]["sha256"]
        ):
            raise OpenDesignError(
                "Open Design cached license differs from the pinned provider hash"
            )
    if len(expected_files) > provider["limits"]["max_files"]:
        raise OpenDesignError("Open Design cache exceeds the file-count limit")
    if total_size > provider["limits"]["max_total_bytes"]:
        raise OpenDesignError("Open Design cache exceeds the total-size limit")
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
        package_source_root = f"{provider['package_root']}/{slug}"
        tree_proof = _build_tree_proof(
            repository,
            package_source_root,
            [record["source_path"] for record in files],
        )
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
                "schema_version": RECEIPT_SCHEMA_VERSION,
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
                "tree_proof": tree_proof,
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
