#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple


SCHEMA_VERSION = 1
SOURCE_FIELDS = {
    "id",
    "repository",
    "revision",
    "authority",
    "scope",
    "license",
    "role",
    "update_method",
    "distribution",
    "destination",
}
PROVENANCE_FIELDS = {
    "source_id",
    "upstream_path",
    "revision",
    "authority",
    "role",
    "license",
    "sha256",
    "decision",
}
DECISIONS = {"included", "mapped-to-official", "excluded", "blocked"}
VERIFIED_LICENSE_DECISIONS = {"included", "mapped-to-official"}
HEX_40_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ValidationError(ValueError):
    """Raised when design-stack metadata is unsafe or internally inconsistent."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValidationError(f"missing required file: {path}") from error
    except json.JSONDecodeError as error:
        raise ValidationError(f"invalid JSON in {path}: {error}") from error


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _require_mapping(value: Any, context: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{context} must be an object")
    return value


def _require_list(value: Any, context: str) -> List[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{context} must be a list")
    return value


def _require_nonempty_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{context} must be a non-empty string")
    return value


def _require_sha256(value: Any, context: str) -> str:
    value = _require_nonempty_string(value, context)
    if SHA256_PATTERN.fullmatch(value) is None:
        raise ValidationError(f"{context} must be a lowercase SHA-256 digest")
    return value


def _require_revision(value: Any, context: str) -> str:
    value = _require_nonempty_string(value, context)
    if HEX_40_PATTERN.fullmatch(value) is None:
        raise ValidationError(f"{context} must be an immutable 40-character Git revision")
    return value


def _require_safe_relative_path(value: Any, context: str) -> str:
    value = _require_nonempty_string(value, context)
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or path.as_posix() != value
    ):
        raise ValidationError(f"{context} must be a safe relative POSIX path")
    if "\\" in value:
        raise ValidationError(f"{context} must use POSIX path separators")
    return value


def _require_schema(payload: Mapping[str, Any], context: str) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValidationError(
            f"{context}.schema_version must be {SCHEMA_VERSION}"
        )


def _validate_license(value: Any, context: str) -> Mapping[str, Any]:
    license_record = _require_mapping(value, context)
    for field in ("spdx", "status", "notice_path"):
        if field not in license_record:
            raise ValidationError(f"{context} is missing required field '{field}'")
    _require_nonempty_string(license_record["spdx"], f"{context}.spdx")
    status = _require_nonempty_string(license_record["status"], f"{context}.status")
    if status not in {"verified", "unresolved"}:
        raise ValidationError(f"{context}.status must be verified or unresolved")
    notice_path = license_record["notice_path"]
    if notice_path is not None:
        _require_safe_relative_path(notice_path, f"{context}.notice_path")
    return license_record


def validate_registry(registry: Mapping[str, Any]) -> None:
    registry = _require_mapping(registry, "registry")
    _require_schema(registry, "registry")
    _require_nonempty_string(
        registry.get("google_design_md_cli_version"),
        "registry.google_design_md_cli_version",
    )
    sources = _require_list(registry.get("sources"), "registry.sources")
    if not sources:
        raise ValidationError("registry.sources must not be empty")

    source_ids: Set[str] = set()
    destinations: Set[str] = set()
    for index, raw_source in enumerate(sources):
        context = f"registry.sources[{index}]"
        source = _require_mapping(raw_source, context)
        for field in sorted(SOURCE_FIELDS):
            if field not in source:
                raise ValidationError(f"{context} is missing required field '{field}'")

        source_id = _require_nonempty_string(source["id"], f"{context}.id")
        if source_id in source_ids:
            raise ValidationError(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
        _require_nonempty_string(source["repository"], f"{context}.repository")
        _require_revision(source["revision"], f"{context}.revision")
        _require_nonempty_string(source["authority"], f"{context}.authority")
        scope = _require_list(source["scope"], f"{context}.scope")
        if not scope:
            raise ValidationError(f"{context}.scope must not be empty")
        for scope_index, pattern in enumerate(scope):
            _require_nonempty_string(pattern, f"{context}.scope[{scope_index}]")
        _validate_license(source["license"], f"{context}.license")
        _require_nonempty_string(source["role"], f"{context}.role")
        _require_nonempty_string(source["update_method"], f"{context}.update_method")

        distribution = _require_nonempty_string(
            source["distribution"], f"{context}.distribution"
        )
        if distribution not in {"vendored", "on-demand", "reference-only"}:
            raise ValidationError(
                f"{context}.distribution must be vendored, on-demand, or reference-only"
            )
        destination = source["destination"]
        if distribution == "vendored":
            destination = _require_safe_relative_path(
                destination, f"{context}.destination"
            )
            if destination in destinations:
                raise ValidationError(f"duplicate source destination: {destination}")
            destinations.add(destination)
        elif destination is not None:
            raise ValidationError(
                f"{context}.destination must be null for a non-vendored source"
            )


def _source_map(registry: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    return {source["id"]: source for source in registry["sources"]}


def _validate_catalogs(
    catalogs: Any,
    locked_files: Mapping[Tuple[str, str], Mapping[str, Any]],
) -> Set[Tuple[str, str]]:
    catalogs = _require_mapping(catalogs, "lock.catalogs")
    expected_catalogs = {"mengto_skills", "design_md"}
    if set(catalogs) != expected_catalogs:
        raise ValidationError(
            "lock.catalogs must contain exactly mengto_skills and design_md"
        )

    catalog_keys: Set[Tuple[str, str]] = set()
    for catalog_name in sorted(expected_catalogs):
        entries = _require_list(catalogs[catalog_name], f"lock.catalogs.{catalog_name}")
        names: Set[str] = set()
        paths: Set[Tuple[str, str]] = set()
        for index, raw_entry in enumerate(entries):
            context = f"lock.catalogs.{catalog_name}[{index}]"
            entry = _require_mapping(raw_entry, context)
            for field in ("source_id", "name", "path", "sha256"):
                if field not in entry:
                    raise ValidationError(f"{context} is missing required field '{field}'")
            source_id = _require_nonempty_string(
                entry["source_id"], f"{context}.source_id"
            )
            name = _require_nonempty_string(entry["name"], f"{context}.name")
            path = _require_safe_relative_path(entry["path"], f"{context}.path")
            digest = _require_sha256(entry["sha256"], f"{context}.sha256")
            key = (source_id, path)
            if name in names:
                raise ValidationError(f"duplicate {catalog_name} name: {name}")
            if key in paths:
                raise ValidationError(f"duplicate {catalog_name} path: {source_id}:{path}")
            names.add(name)
            paths.add(key)
            catalog_keys.add(key)
            locked_file = locked_files.get(key)
            if locked_file is None:
                raise ValidationError(
                    f"{context} does not resolve to a locked source file: {source_id}:{path}"
                )
            if digest != locked_file["sha256"]:
                raise ValidationError(f"{context}.sha256 does not match the source lock")
            if catalog_name == "mengto_skills":
                _require_nonempty_string(
                    entry.get("description"), f"{context}.description"
                )
            else:
                authority = _require_nonempty_string(
                    entry.get("authority"), f"{context}.authority"
                )
                if authority != "third-party-analysis":
                    raise ValidationError(
                        f"{context}.authority must be third-party-analysis"
                    )
    return catalog_keys


def validate_lock(
    registry: Mapping[str, Any],
    lock: Mapping[str, Any],
    repo_root: Optional[Path] = None,
    metadata_only: bool = False,
) -> Set[Tuple[str, str]]:
    validate_registry(registry)
    lock = _require_mapping(lock, "lock")
    _require_schema(lock, "lock")
    sources = _require_list(lock.get("sources"), "lock.sources")
    registry_sources = _source_map(registry)
    locked_source_ids: Set[str] = set()
    locked_files: Dict[Tuple[str, str], Mapping[str, Any]] = {}

    for source_index, raw_locked_source in enumerate(sources):
        context = f"lock.sources[{source_index}]"
        locked_source = _require_mapping(raw_locked_source, context)
        for field in ("id", "revision", "tree", "files"):
            if field not in locked_source:
                raise ValidationError(f"{context} is missing required field '{field}'")
        source_id = _require_nonempty_string(locked_source["id"], f"{context}.id")
        if source_id in locked_source_ids:
            raise ValidationError(f"duplicate locked source id: {source_id}")
        locked_source_ids.add(source_id)
        source = registry_sources.get(source_id)
        if source is None:
            raise ValidationError(f"lock contains unknown source id: {source_id}")
        revision = _require_revision(locked_source["revision"], f"{context}.revision")
        if revision != source["revision"]:
            raise ValidationError(
                f"{context}.revision does not match registry source '{source_id}'"
            )
        _require_revision(locked_source["tree"], f"{context}.tree")
        files = _require_list(locked_source["files"], f"{context}.files")
        seen_paths: Set[str] = set()
        for file_index, raw_file in enumerate(files):
            file_context = f"{context}.files[{file_index}]"
            file_record = _require_mapping(raw_file, file_context)
            for field in ("path", "size", "sha256"):
                if field not in file_record:
                    raise ValidationError(
                        f"{file_context} is missing required field '{field}'"
                    )
            path = _require_safe_relative_path(
                file_record["path"], f"{file_context}.path"
            )
            if path in seen_paths:
                raise ValidationError(f"duplicate locked file path: {source_id}:{path}")
            seen_paths.add(path)
            size = file_record["size"]
            if not isinstance(size, int) or isinstance(size, bool) or size < 0:
                raise ValidationError(f"{file_context}.size must be a non-negative integer")
            digest = _require_sha256(
                file_record["sha256"], f"{file_context}.sha256"
            )
            locked_files[(source_id, path)] = file_record

            if not metadata_only and source["distribution"] == "vendored":
                if repo_root is None:
                    raise ValidationError("repo_root is required for full lock validation")
                local_path = repo_root / source["destination"] / Path(path)
                if not local_path.is_file():
                    raise ValidationError(f"missing vendored file: {local_path}")
                if local_path.stat().st_size != size:
                    raise ValidationError(f"size mismatch for vendored file: {local_path}")
                if sha256_file(local_path) != digest:
                    raise ValidationError(f"SHA-256 mismatch for vendored file: {local_path}")

    if locked_source_ids != set(registry_sources):
        missing = sorted(set(registry_sources) - locked_source_ids)
        extra = sorted(locked_source_ids - set(registry_sources))
        raise ValidationError(f"lock source set mismatch; missing={missing}, extra={extra}")
    return _validate_catalogs(lock.get("catalogs"), locked_files)


def validate_provenance(
    registry: Mapping[str, Any],
    lock: Mapping[str, Any],
    provenance: Mapping[str, Any],
) -> None:
    catalog_keys = validate_lock(registry, lock, metadata_only=True)
    provenance = _require_mapping(provenance, "provenance")
    _require_schema(provenance, "provenance")
    records = _require_list(provenance.get("records"), "provenance.records")
    registry_sources = _source_map(registry)
    locked_files = {
        (source["id"], file_record["path"]): file_record
        for source in lock["sources"]
        for file_record in source["files"]
    }
    seen: Set[Tuple[str, str]] = set()

    for index, raw_record in enumerate(records):
        context = f"provenance.records[{index}]"
        record = _require_mapping(raw_record, context)
        for field in sorted(PROVENANCE_FIELDS):
            if field not in record:
                raise ValidationError(f"{context} is missing required field '{field}'")
        source_id = _require_nonempty_string(
            record["source_id"], f"{context}.source_id"
        )
        source = registry_sources.get(source_id)
        if source is None:
            raise ValidationError(f"{context} references unknown source '{source_id}'")
        upstream_path = _require_safe_relative_path(
            record["upstream_path"], f"{context}.upstream_path"
        )
        key = (source_id, upstream_path)
        if key in seen:
            raise ValidationError(f"duplicate provenance record: {source_id}:{upstream_path}")
        seen.add(key)
        revision = _require_revision(record["revision"], f"{context}.revision")
        if revision != source["revision"]:
            raise ValidationError(f"{context}.revision does not match the registry")
        _require_nonempty_string(record["authority"], f"{context}.authority")
        _require_nonempty_string(record["role"], f"{context}.role")
        license_record = _validate_license(record["license"], f"{context}.license")
        digest = _require_sha256(record["sha256"], f"{context}.sha256")
        locked_file = locked_files.get(key)
        if locked_file is None:
            raise ValidationError(f"{context} does not resolve to a locked file")
        if digest != locked_file["sha256"]:
            raise ValidationError(f"{context}.sha256 does not match the source lock")

        decision = _require_nonempty_string(record["decision"], f"{context}.decision")
        if decision not in DECISIONS:
            raise ValidationError(
                f"{context}.decision must be one of {sorted(DECISIONS)}"
            )
        if decision != "included":
            _require_nonempty_string(record.get("reason"), f"{context}.reason")
        if decision in VERIFIED_LICENSE_DECISIONS:
            if license_record["status"] != "verified" or not license_record["notice_path"]:
                raise ValidationError(
                    f"{context}.license must be verified and name a notice for {decision} material"
                )
        if decision == "mapped-to-official":
            mapping = _require_mapping(
                record.get("official_mapping"), f"{context}.official_mapping"
            )
            for field in ("source", "path", "content_sha256"):
                if field not in mapping:
                    raise ValidationError(
                        f"{context}.official_mapping is missing required field '{field}'"
                    )
            _require_nonempty_string(mapping["source"], f"{context}.official_mapping.source")
            _require_safe_relative_path(mapping["path"], f"{context}.official_mapping.path")
            _require_sha256(
                mapping["content_sha256"],
                f"{context}.official_mapping.content_sha256",
            )

    missing_catalog_records = sorted(catalog_keys - seen)
    if missing_catalog_records:
        raise ValidationError(
            f"catalog entries missing provenance records: {missing_catalog_records}"
        )


def _strip_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValidationError(f"invalid quoted frontmatter value: {value}") from error
        if not isinstance(decoded, str):
            raise ValidationError(f"frontmatter value must be a string: {value}")
        return decoded
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def parse_skill_frontmatter(content: str, source: str) -> Dict[str, str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValidationError(f"{source} must start with a YAML frontmatter delimiter")
    try:
        closing_index = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as error:
        raise ValidationError(f"{source} is missing the closing frontmatter delimiter") from error

    fields: Dict[str, str] = {}
    for line_number, line in enumerate(lines[1:closing_index], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            raise ValidationError(
                f"{source}:{line_number} uses unsupported frontmatter syntax"
            )
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key or key in fields:
            raise ValidationError(f"{source}:{line_number} has an invalid or duplicate key")
        fields[key] = _strip_yaml_scalar(raw_value)

    for field in ("name", "description"):
        if not fields.get(field, "").strip():
            raise ValidationError(f"{source} frontmatter requires non-empty {field}")
    return fields


def validate_repository(repo_root: Path, metadata_only: bool = False) -> None:
    design_root = repo_root / "design-stack"
    registry = load_json(design_root / "sources.json")
    lock = load_json(design_root / "sources.lock.json")
    provenance = load_json(design_root / "provenance.json")
    validate_registry(registry)
    validate_lock(
        registry,
        lock,
        repo_root=repo_root,
        metadata_only=metadata_only,
    )
    validate_provenance(registry, lock, provenance)
