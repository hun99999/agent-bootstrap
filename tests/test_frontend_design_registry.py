import copy
import json
import tempfile
import unittest
from pathlib import Path

from tests.frontend_design_test_support import (
    REPO_ROOT,
    load_script_module,
    sha256_bytes,
)


design_stack = load_script_module("design_stack.py")


REQUIRED_SOURCE_FIELDS = {
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
REQUIRED_PROVENANCE_FIELDS = {
    "source_id",
    "upstream_path",
    "revision",
    "authority",
    "catalog",
    "role",
    "license",
    "origin",
    "sha256",
    "decision",
}
KNOWN_MENGTO_PROVENANCE_GAPS = {
    "agent-skills/codex/pdf/SKILL.md",
    "agent-skills/codex/playwright-interactive/SKILL.md",
    "agent-skills/codex/playwright/SKILL.md",
    "agent-skills/codex/screenshot/SKILL.md",
    "agent-skills/ui/frontend-design/SKILL.md",
}
FIXTURE_LICENSE = b"fixture license\n"


def source_record() -> dict:
    return {
        "id": "mengto-skills",
        "repository": "https://example.invalid/source",
        "revision": "a" * 40,
        "authority": "procedural-guidance",
        "scope": ["skills/**/SKILL.md"],
        "license": {
            "spdx": "MIT",
            "status": "verified",
            "notice_path": "LICENSE",
            "notice_sha256": sha256_bytes(FIXTURE_LICENSE),
        },
        "role": "test-reference",
        "update_method": "reviewed-local-tar",
        "distribution": "vendored",
        "destination": "design-stack/vendor/mengto-skills",
    }


def registry_payload() -> dict:
    return {
        "schema_version": 1,
        "google_design_md_cli_version": "0.3.0",
        "sources": [source_record()],
    }


def lock_payload(content: bytes = b"fixture\n") -> dict:
    return {
        "schema_version": 1,
        "sources": [
            {
                "id": "mengto-skills",
                "revision": "a" * 40,
                "tree": "b" * 40,
                "files": [
                    {
                        "path": "LICENSE",
                        "size": len(FIXTURE_LICENSE),
                        "mode": "0644",
                        "sha256": sha256_bytes(FIXTURE_LICENSE),
                        "materialization": "vendored",
                    },
                    {
                        "path": "skills/fixture/SKILL.md",
                        "size": len(content),
                        "mode": "0644",
                        "sha256": sha256_bytes(content),
                        "materialization": "vendored",
                    }
                ],
            }
        ],
        "catalogs": {
            "mengto_skills": [
                {
                    "source_id": "mengto-skills",
                    "name": "fixture",
                    "description": "Fixture skill.",
                    "path": "skills/fixture/SKILL.md",
                    "sha256": sha256_bytes(content),
                }
            ],
            "design_md": [],
        },
    }


def provenance_payload(content: bytes = b"fixture\n") -> dict:
    return {
        "schema_version": 1,
        "records": [
            {
                "source_id": "mengto-skills",
                "upstream_path": "skills/fixture/SKILL.md",
                "revision": "a" * 40,
                "authority": "procedural-guidance",
                "catalog": "mengto_skills",
                "role": "test-reference",
                "license": {
                    "spdx": "MIT",
                    "status": "verified",
                    "notice_path": "LICENSE",
                    "notice_sha256": sha256_bytes(FIXTURE_LICENSE),
                },
                "origin": {
                    "repository": "https://example.invalid/source",
                    "path": "skills/fixture/SKILL.md",
                    "revision": "a" * 40,
                    "content_sha256": sha256_bytes(content),
                    "basis": "reviewed-git-introduction",
                    "introduced_revision": "b" * 40,
                    "publisher": "Fixture Publisher",
                },
                "sha256": sha256_bytes(content),
                "decision": "included",
            }
        ],
    }


def set_skill_materialization(lock: dict, value: str) -> dict:
    skill_record = next(
        record
        for record in lock["sources"][0]["files"]
        if record["path"] == "skills/fixture/SKILL.md"
    )
    skill_record["materialization"] = value
    return lock


class FrontendDesignRegistryUnitTests(unittest.TestCase):
    def test_registry_accepts_complete_source_contract(self) -> None:
        design_stack.validate_registry(registry_payload())

    def test_registry_rejects_each_missing_required_source_field(self) -> None:
        for field in sorted(REQUIRED_SOURCE_FIELDS):
            with self.subTest(field=field):
                registry = registry_payload()
                del registry["sources"][0][field]
                with self.assertRaisesRegex(design_stack.ValidationError, field):
                    design_stack.validate_registry(registry)

    def test_registry_requires_destination_only_for_vendored_sources(self) -> None:
        registry = registry_payload()
        for distribution in ("on-demand", "reference-only"):
            with self.subTest(distribution=distribution):
                registry["sources"][0]["distribution"] = distribution
                registry["sources"][0]["destination"] = None
                design_stack.validate_registry(registry)

        registry["sources"][0]["distribution"] = "vendored"
        with self.assertRaisesRegex(design_stack.ValidationError, "destination"):
            design_stack.validate_registry(registry)

    def test_registry_rejects_unsafe_destination(self) -> None:
        registry = registry_payload()
        registry["sources"][0]["destination"] = "../outside"
        with self.assertRaisesRegex(design_stack.ValidationError, "destination"):
            design_stack.validate_registry(registry)

    def test_registry_rejects_unsafe_source_ids(self) -> None:
        for source_id in ("../source", "Source", "source/name", ".source", "source_name"):
            with self.subTest(source_id=source_id):
                registry = registry_payload()
                registry["sources"][0]["id"] = source_id
                with self.assertRaisesRegex(design_stack.ValidationError, "id"):
                    design_stack.validate_registry(registry)

    def test_lock_rejects_revision_that_does_not_match_registry(self) -> None:
        lock = lock_payload()
        lock["sources"][0]["revision"] = "c" * 40
        with self.assertRaisesRegex(design_stack.ValidationError, "revision"):
            design_stack.validate_lock(registry_payload(), lock, metadata_only=True)

    def test_lock_rejects_invalid_source_mode(self) -> None:
        for mode in ("755", "100755", "09ff", 0o755):
            with self.subTest(mode=mode):
                lock = lock_payload()
                lock["sources"][0]["files"][0]["mode"] = mode
                with self.assertRaisesRegex(design_stack.ValidationError, "mode"):
                    design_stack.validate_lock(
                        registry_payload(), lock, metadata_only=True
                    )

    def test_lock_binds_each_verified_source_license_notice(self) -> None:
        registry = registry_payload()
        registry["sources"][0]["license"]["notice_sha256"] = "e" * 64
        with self.assertRaisesRegex(
            design_stack.ValidationError, "source license|license notice"
        ):
            design_stack.validate_lock(registry, lock_payload(), metadata_only=True)

    def test_lock_rejects_duplicate_or_unsafe_file_paths(self) -> None:
        for invalid_path in (
            "../outside",
            "/absolute",
            "./inside",
            "inside//file",
            "inside\\file",
        ):
            with self.subTest(path=invalid_path):
                lock = lock_payload()
                lock["sources"][0]["files"][0]["path"] = invalid_path
                with self.assertRaisesRegex(design_stack.ValidationError, "path"):
                    design_stack.validate_lock(registry_payload(), lock, metadata_only=True)

        lock = lock_payload()
        lock["sources"][0]["files"].append(copy.deepcopy(lock["sources"][0]["files"][0]))
        with self.assertRaisesRegex(design_stack.ValidationError, "duplicate"):
            design_stack.validate_lock(registry_payload(), lock, metadata_only=True)

    def test_lock_rejects_file_hash_that_does_not_match_vendored_bytes(self) -> None:
        content = b"fixture\n"
        registry = registry_payload()
        lock = lock_payload(content)
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            vendored_file = (
                repo_root
                / "design-stack/vendor/mengto-skills/skills/fixture/SKILL.md"
            )
            vendored_file.parent.mkdir(parents=True)
            vendored_file.write_bytes(b"changed\n")
            (repo_root / "design-stack/vendor/mengto-skills/LICENSE").write_bytes(
                FIXTURE_LICENSE
            )

            with self.assertRaisesRegex(design_stack.ValidationError, "SHA-256"):
                design_stack.validate_lock(
                    registry,
                    lock,
                    repo_root=repo_root,
                    metadata_only=False,
                )

    def test_lock_accepts_matching_vendored_bytes(self) -> None:
        content = b"fixture\n"
        registry = registry_payload()
        lock = lock_payload(content)
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            vendored_file = (
                repo_root
                / "design-stack/vendor/mengto-skills/skills/fixture/SKILL.md"
            )
            vendored_file.parent.mkdir(parents=True)
            vendored_file.write_bytes(content)
            (repo_root / "design-stack/vendor/mengto-skills/LICENSE").write_bytes(
                FIXTURE_LICENSE
            )

            design_stack.validate_lock(
                registry,
                lock,
                repo_root=repo_root,
                metadata_only=False,
            )

    def test_lock_rejects_materialized_metadata_only_file(self) -> None:
        content = b"fixture\n"
        registry = registry_payload()
        lock = lock_payload(content)
        skill_record = next(
            record
            for record in lock["sources"][0]["files"]
            if record["path"] == "skills/fixture/SKILL.md"
        )
        skill_record["materialization"] = "metadata-only"
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            vendor = repo_root / "design-stack/vendor/mengto-skills"
            (vendor / "skills/fixture").mkdir(parents=True)
            (vendor / "LICENSE").write_bytes(FIXTURE_LICENSE)
            (vendor / "skills/fixture/SKILL.md").write_bytes(content)
            with self.assertRaisesRegex(
                design_stack.ValidationError, "metadata-only"
            ):
                design_stack.validate_lock(
                    registry,
                    lock,
                    repo_root=repo_root,
                    metadata_only=False,
                )

    def test_lock_allows_missing_metadata_only_file(self) -> None:
        content = b"fixture\n"
        registry = registry_payload()
        lock = lock_payload(content)
        skill_record = next(
            record
            for record in lock["sources"][0]["files"]
            if record["path"] == "skills/fixture/SKILL.md"
        )
        skill_record["materialization"] = "metadata-only"
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            vendor = repo_root / "design-stack/vendor/mengto-skills"
            vendor.mkdir(parents=True)
            (vendor / "LICENSE").write_bytes(FIXTURE_LICENSE)
            design_stack.validate_lock(
                registry,
                lock,
                repo_root=repo_root,
                metadata_only=False,
            )

    def test_provenance_requires_complete_record_contract(self) -> None:
        for field in sorted(REQUIRED_PROVENANCE_FIELDS):
            with self.subTest(field=field):
                provenance = provenance_payload()
                del provenance["records"][0][field]
                with self.assertRaisesRegex(design_stack.ValidationError, field):
                    design_stack.validate_provenance(
                        registry_payload(), lock_payload(), provenance
                    )

    def test_origin_requires_immutable_reviewed_and_introduction_evidence(self) -> None:
        required_origin_fields = {
            "repository": "https://example.invalid/source",
            "path": "skills/fixture/SKILL.md",
            "revision": "a" * 40,
            "content_sha256": sha256_bytes(b"fixture\n"),
            "basis": "reviewed-git-introduction",
            "introduced_revision": "b" * 40,
            "publisher": "Fixture Publisher",
        }
        for missing_field in sorted(required_origin_fields):
            with self.subTest(field=missing_field):
                provenance = provenance_payload()
                provenance["records"][0]["origin"] = dict(required_origin_fields)
                del provenance["records"][0]["origin"][missing_field]
                with self.assertRaisesRegex(design_stack.ValidationError, missing_field):
                    design_stack.validate_provenance(
                        registry_payload(), lock_payload(), provenance
                    )

    def test_included_or_mapped_material_requires_verified_license_notice(self) -> None:
        for decision in ("included", "mapped-to-official"):
            with self.subTest(decision=decision):
                provenance = provenance_payload()
                record = provenance["records"][0]
                record["decision"] = decision
                record["license"] = {
                    "spdx": "NOASSERTION",
                    "status": "unresolved",
                    "notice_path": None,
                    "notice_sha256": None,
                }
                if decision == "mapped-to-official":
                    record["reason"] = "Use a reviewed official equivalent."
                    record["official_mapping"] = {
                        "repository": "https://example.invalid/official",
                        "revision": "e" * 40,
                        "tree": "f" * 40,
                        "path": "skills/fixture/SKILL.md",
                        "content_sha256": "c" * 64,
                        "license_path": "skills/fixture/LICENSE.txt",
                        "license_sha256": "b" * 64,
                    }
                lock = lock_payload()
                if decision == "mapped-to-official":
                    set_skill_materialization(lock, "metadata-only")
                with self.assertRaisesRegex(design_stack.ValidationError, "license"):
                    design_stack.validate_provenance(
                        registry_payload(), lock, provenance
                    )

    def test_included_material_license_matches_its_locked_source_notice(self) -> None:
        provenance = provenance_payload()
        provenance["records"][0]["license"]["notice_sha256"] = "e" * 64
        with self.assertRaisesRegex(
            design_stack.ValidationError, "source license|license notice"
        ):
            design_stack.validate_provenance(
                registry_payload(), lock_payload(), provenance
            )

    def test_included_material_license_matches_the_registry_license(self) -> None:
        provenance = provenance_payload()
        record = provenance["records"][0]
        record["license"] = {
            "spdx": "Apache-2.0",
            "status": "verified",
            "notice_path": "skills/fixture/SKILL.md",
            "notice_sha256": sha256_bytes(b"fixture\n"),
        }
        with self.assertRaisesRegex(design_stack.ValidationError, "source license"):
            design_stack.validate_provenance(
                registry_payload(), lock_payload(), provenance
            )

    def test_origin_repository_and_path_match_the_registry_record(self) -> None:
        for field, value in (
            ("repository", "https://example.invalid/unrelated"),
            ("path", "skills/unrelated/SKILL.md"),
        ):
            with self.subTest(field=field):
                provenance = provenance_payload()
                provenance["records"][0]["origin"][field] = value
                with self.assertRaisesRegex(design_stack.ValidationError, field):
                    design_stack.validate_provenance(
                        registry_payload(), lock_payload(), provenance
                    )

    def test_catalog_rejects_an_entry_from_the_wrong_source(self) -> None:
        registry = registry_payload()
        registry["sources"][0]["id"] = "awesome-design-md"
        lock = lock_payload()
        lock["sources"][0]["id"] = "awesome-design-md"
        lock["catalogs"]["mengto_skills"][0]["source_id"] = "awesome-design-md"
        with self.assertRaisesRegex(design_stack.ValidationError, "mengto-skills"):
            design_stack.validate_lock(registry, lock, metadata_only=True)

    def test_included_skill_provenance_cannot_be_omitted_from_catalog(self) -> None:
        lock = lock_payload()
        lock["catalogs"]["mengto_skills"] = []
        with self.assertRaisesRegex(design_stack.ValidationError, "catalog"):
            design_stack.validate_provenance(
                registry_payload(), lock, provenance_payload()
            )

    def test_cataloged_material_cannot_opt_out_by_becoming_blocked(self) -> None:
        provenance = provenance_payload()
        record = provenance["records"][0]
        record["catalog"] = None
        record["decision"] = "blocked"
        record["reason"] = "Fixture block."
        record["license"] = {
            "spdx": "NOASSERTION",
            "status": "unresolved",
            "notice_path": None,
            "notice_sha256": None,
        }
        lock = set_skill_materialization(lock_payload(), "metadata-only")
        with self.assertRaisesRegex(design_stack.ValidationError, "catalog"):
            design_stack.validate_provenance(
                registry_payload(), lock, provenance
            )

    def test_unresolved_material_is_allowed_only_when_blocked_or_excluded(self) -> None:
        for decision in ("blocked", "excluded"):
            with self.subTest(decision=decision):
                provenance = provenance_payload()
                record = provenance["records"][0]
                record["decision"] = decision
                record["reason"] = "Redistribution evidence is unresolved."
                record["license"] = {
                    "spdx": "NOASSERTION",
                    "status": "unresolved",
                    "notice_path": None,
                    "notice_sha256": None,
                }
                lock = set_skill_materialization(lock_payload(), "metadata-only")
                design_stack.validate_provenance(
                    registry_payload(), lock, provenance
                )

    def test_non_included_decisions_require_reason(self) -> None:
        provenance = provenance_payload()
        provenance["records"][0]["decision"] = "blocked"
        provenance["records"][0]["license"] = {
            "spdx": "NOASSERTION",
            "status": "unresolved",
            "notice_path": None,
            "notice_sha256": None,
        }
        lock = set_skill_materialization(lock_payload(), "metadata-only")
        with self.assertRaisesRegex(design_stack.ValidationError, "reason"):
            design_stack.validate_provenance(
                registry_payload(), lock, provenance
            )

    def test_mapped_decision_requires_content_addressed_official_mapping(self) -> None:
        provenance = provenance_payload()
        record = provenance["records"][0]
        record["decision"] = "mapped-to-official"
        record["reason"] = "Use a reviewed official equivalent."
        lock = set_skill_materialization(lock_payload(), "metadata-only")
        with self.assertRaisesRegex(design_stack.ValidationError, "official_mapping"):
            design_stack.validate_provenance(
                registry_payload(), lock, provenance
            )

    def test_mapped_decision_cannot_materialize_the_upstream_duplicate(self) -> None:
        lock = lock_payload()
        provenance = provenance_payload()
        record = provenance["records"][0]
        record["decision"] = "mapped-to-official"
        record["reason"] = "Use the official replacement."
        record["license"] = {
            "spdx": "Apache-2.0",
            "status": "verified",
            "notice_path": "skills/fixture/LICENSE.txt",
            "notice_sha256": "b" * 64,
        }
        record["official_mapping"] = {
            "repository": "https://example.invalid/official",
            "revision": "e" * 40,
            "tree": "f" * 40,
            "path": "skills/fixture/SKILL.md",
            "content_sha256": "c" * 64,
            "license_path": "skills/fixture/LICENSE.txt",
            "license_sha256": "b" * 64,
        }
        with self.assertRaisesRegex(design_stack.ValidationError, "materialization"):
            design_stack.validate_provenance(
                registry_payload(), lock, provenance
            )

    def test_mapped_decision_requires_immutable_official_source_and_notice(self) -> None:
        required_mapping_fields = {
            "repository": "https://example.invalid/official",
            "revision": "e" * 40,
            "tree": "f" * 40,
            "path": "skills/fixture/SKILL.md",
            "content_sha256": "c" * 64,
            "license_path": "skills/fixture/LICENSE.txt",
            "license_sha256": "b" * 64,
        }
        for missing_field in sorted(required_mapping_fields):
            with self.subTest(field=missing_field):
                provenance = provenance_payload()
                record = provenance["records"][0]
                record["decision"] = "mapped-to-official"
                record["reason"] = "Use a reviewed official equivalent."
                record["official_mapping"] = dict(required_mapping_fields)
                del record["official_mapping"][missing_field]
                lock = set_skill_materialization(lock_payload(), "metadata-only")
                with self.assertRaisesRegex(
                    design_stack.ValidationError, missing_field
                ):
                    design_stack.validate_provenance(
                        registry_payload(), lock, provenance
                    )

    def test_google_cli_contract_parses_hash_locked_manifest(self) -> None:
        matching_content = b'{"name":"@google/design.md","version":"0.3.0"}\n'
        mismatching_content = b'{"name":"@google/design.md","version":"0.2.0"}\n'

        for content, should_pass in (
            (matching_content, True),
            (mismatching_content, False),
        ):
            with self.subTest(content=content):
                registry = registry_payload()
                source = registry["sources"][0]
                source["id"] = "google-design-md"
                source["destination"] = "design-stack/vendor/google-design-md"
                lock = lock_payload(content)
                locked_source = lock["sources"][0]
                locked_source["id"] = "google-design-md"
                manifest_record = next(
                    record
                    for record in locked_source["files"]
                    if record["path"] == "skills/fixture/SKILL.md"
                )
                manifest_record["path"] = "packages/cli/package.json"
                lock["catalogs"] = {"mengto_skills": [], "design_md": []}
                lock["contracts"] = {
                    "google_design_md_cli": {
                        "source_id": "google-design-md",
                        "path": "packages/cli/package.json",
                        "sha256": sha256_bytes(content),
                        "version": "0.3.0",
                    }
                }
                with tempfile.TemporaryDirectory() as temp_dir:
                    repo_root = Path(temp_dir)
                    manifest = (
                        repo_root
                        / "design-stack/vendor/google-design-md/packages/cli/package.json"
                    )
                    manifest.parent.mkdir(parents=True)
                    manifest.write_bytes(content)
                    (
                        repo_root / "design-stack/vendor/google-design-md/LICENSE"
                    ).write_bytes(FIXTURE_LICENSE)

                    if should_pass:
                        design_stack.validate_lock(
                            registry,
                            lock,
                            repo_root=repo_root,
                            metadata_only=False,
                        )
                    else:
                        with self.assertRaisesRegex(
                            design_stack.ValidationError, "0.2.0"
                        ):
                            design_stack.validate_lock(
                                registry,
                                lock,
                                repo_root=repo_root,
                                metadata_only=False,
                            )

    def test_frontmatter_parser_requires_delimiters_name_and_description(self) -> None:
        parsed = design_stack.parse_skill_frontmatter(
            "---\nname: fixture\ndescription: Fixture skill.\nmetadata:\n  version: 1.0\n---\n\n# Fixture\n",
            "fixture/SKILL.md",
        )
        self.assertEqual(parsed["name"], "fixture")
        self.assertEqual(parsed["description"], "Fixture skill.")

        invalid_cases = (
            "name: fixture\ndescription: Missing delimiters.\n",
            "---\ndescription: Missing name.\n---\n",
            "---\nname: fixture\n---\n",
        )
        for content in invalid_cases:
            with self.subTest(content=content):
                with self.assertRaises(design_stack.ValidationError):
                    design_stack.parse_skill_frontmatter(content, "fixture/SKILL.md")


class FrontendDesignCommittedRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(
            (REPO_ROOT / "design-stack/sources.json").read_text(encoding="utf-8")
        )
        cls.lock = json.loads(
            (REPO_ROOT / "design-stack/sources.lock.json").read_text(encoding="utf-8")
        )
        cls.provenance = json.loads(
            (REPO_ROOT / "design-stack/provenance.json").read_text(encoding="utf-8")
        )

    def test_committed_metadata_contract_is_valid(self) -> None:
        design_stack.validate_repository(REPO_ROOT, metadata_only=True)

    def test_committed_registry_contains_all_locked_sources(self) -> None:
        sources = self.registry["sources"]
        self.assertEqual(len(sources), 7)
        self.assertEqual(
            {source["id"] for source in sources},
            {
                "anthropic-frontend-design",
                "awesome-design-md",
                "google-design-md",
                "mengto-skills",
                "open-design",
                "vercel-agent-skills",
                "vercel-web-interface-guidelines",
            },
        )
        for source in sources:
            with self.subTest(source=source["id"]):
                self.assertLessEqual(REQUIRED_SOURCE_FIELDS, set(source))

    def test_every_verified_source_notice_is_hash_locked(self) -> None:
        lock_by_id = {source["id"]: source for source in self.lock["sources"]}
        for source in self.registry["sources"]:
            if source["license"]["status"] != "verified":
                continue
            with self.subTest(source=source["id"]):
                notice_path = source["license"]["notice_path"]
                notice_hash = source["license"]["notice_sha256"]
                locked_notice = next(
                    record
                    for record in lock_by_id[source["id"]]["files"]
                    if record["path"] == notice_path
                )
                self.assertEqual(locked_notice["sha256"], notice_hash)

    def test_committed_catalog_inventories_95_mengto_skills(self) -> None:
        skills = self.lock["catalogs"]["mengto_skills"]
        self.assertEqual(len(skills), 95)
        self.assertEqual(len({entry["name"] for entry in skills}), 95)
        self.assertEqual(len({entry["path"] for entry in skills}), 95)

    def test_committed_catalog_indexes_74_design_md_references(self) -> None:
        references = self.lock["catalogs"]["design_md"]
        self.assertEqual(len(references), 74)
        self.assertEqual(len({entry["name"] for entry in references}), 74)
        self.assertTrue(all(entry["authority"] == "third-party-analysis" for entry in references))

    def test_meta_and_vercel_design_md_are_labeled_third_party_analysis(self) -> None:
        by_name = {
            entry["name"]: entry for entry in self.lock["catalogs"]["design_md"]
        }
        self.assertEqual(by_name["meta"]["authority"], "third-party-analysis")
        self.assertEqual(by_name["vercel"]["authority"], "third-party-analysis")

    def test_open_design_is_on_demand_and_not_vendored(self) -> None:
        source = next(
            source
            for source in self.registry["sources"]
            if source["id"] == "open-design"
        )
        self.assertEqual(source["distribution"], "on-demand")
        self.assertIsNone(source["destination"])
        self.assertFalse((REPO_ROOT / "design-stack/vendor/open-design").exists())

    def test_google_design_md_cli_version_is_pinned(self) -> None:
        self.assertEqual(self.registry["google_design_md_cli_version"], "0.3.0")
        contract = self.lock["contracts"]["google_design_md_cli"]
        self.assertEqual(contract["source_id"], "google-design-md")
        self.assertEqual(contract["path"], "packages/cli/package.json")
        self.assertEqual(contract["version"], "0.3.0")
        google_lock = next(
            source
            for source in self.lock["sources"]
            if source["id"] == "google-design-md"
        )
        manifest = next(
            record
            for record in google_lock["files"]
            if record["path"] == contract["path"]
        )
        self.assertEqual(manifest["sha256"], contract["sha256"])

    def test_anthropic_frontend_design_skill_and_license_are_hash_locked(self) -> None:
        source = next(
            source
            for source in self.registry["sources"]
            if source["id"] == "anthropic-frontend-design"
        )
        self.assertEqual(source["license"]["spdx"], "Apache-2.0")
        self.assertEqual(source["license"]["status"], "verified")
        locked_source = next(
            source
            for source in self.lock["sources"]
            if source["id"] == "anthropic-frontend-design"
        )
        self.assertEqual(
            {record["path"] for record in locked_source["files"]},
            {
                "skills/frontend-design/LICENSE.txt",
                "skills/frontend-design/SKILL.md",
            },
        )

    def test_every_catalog_entry_has_one_provenance_decision(self) -> None:
        expected = {
            (entry["source_id"], entry["path"])
            for catalog in self.lock["catalogs"].values()
            for entry in catalog
        }
        records = self.provenance["records"]
        actual = {(record["source_id"], record["upstream_path"]) for record in records}
        self.assertLessEqual(expected, actual)
        self.assertEqual(
            len(
                [
                    record
                    for record in records
                    if (record["source_id"], record["upstream_path"]) in expected
                ]
            ),
            len(expected),
        )
        for record in records:
            with self.subTest(path=record["upstream_path"]):
                self.assertLessEqual(REQUIRED_PROVENANCE_FIELDS, set(record))
                self.assertEqual(record["origin"]["content_sha256"], record["sha256"])
                self.assertEqual(record["origin"]["revision"], record["revision"])
                if record["source_id"] == "mengto-skills":
                    self.assertRegex(
                        record["origin"]["introduced_revision"],
                        r"^[0-9a-f]{40}$",
                    )
                    self.assertTrue(record["origin"]["publisher"])
                if record["decision"] != "included":
                    self.assertTrue(record.get("reason"))

    def test_committed_materialization_matches_provenance_decisions(self) -> None:
        locked_files = {
            (source["id"], record["path"]): record
            for source in self.lock["sources"]
            for record in source["files"]
        }
        for record in self.provenance["records"]:
            with self.subTest(path=record["upstream_path"]):
                locked = locked_files[(record["source_id"], record["upstream_path"])]
                expected = (
                    "vendored" if record["decision"] == "included" else "metadata-only"
                )
                self.assertEqual(locked["materialization"], expected)

    def test_known_mengto_provenance_gaps_are_not_silently_included(self) -> None:
        decisions = {
            record["upstream_path"]: record
            for record in self.provenance["records"]
            if record["source_id"] == "mengto-skills"
        }
        self.assertLessEqual(KNOWN_MENGTO_PROVENANCE_GAPS, set(decisions))
        for path in sorted(KNOWN_MENGTO_PROVENANCE_GAPS):
            with self.subTest(path=path):
                self.assertIn(
                    decisions[path]["decision"],
                    {"mapped-to-official", "blocked"},
                )

    def test_reviewed_official_equivalents_are_immutably_mapped(self) -> None:
        decisions = {
            record["upstream_path"]: record
            for record in self.provenance["records"]
            if record["source_id"] == "mengto-skills"
        }
        mapped_paths = {
            "agent-skills/codex/pdf/SKILL.md",
            "agent-skills/codex/playwright-interactive/SKILL.md",
            "agent-skills/codex/playwright/SKILL.md",
            "agent-skills/codex/screenshot/SKILL.md",
            "agent-skills/ui/frontend-design/SKILL.md",
        }
        for path in sorted(mapped_paths):
            with self.subTest(path=path):
                self.assertEqual(decisions[path]["decision"], "mapped-to-official")
                self.assertEqual(decisions[path]["license"]["spdx"], "Apache-2.0")
                self.assertIn("official_mapping", decisions[path])
                mapping = decisions[path]["official_mapping"]
                self.assertRegex(mapping["revision"], r"^[0-9a-f]{40}$")
                self.assertRegex(mapping["tree"], r"^[0-9a-f]{40}$")
                self.assertRegex(mapping["license_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
