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
    "role",
    "license",
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


def source_record() -> dict:
    return {
        "id": "fixture-source",
        "repository": "https://example.invalid/source",
        "revision": "a" * 40,
        "authority": "procedural-guidance",
        "scope": ["skills/**/SKILL.md"],
        "license": {
            "spdx": "MIT",
            "status": "verified",
            "notice_path": "LICENSE",
        },
        "role": "test-reference",
        "update_method": "reviewed-local-tar",
        "distribution": "vendored",
        "destination": "design-stack/vendor/fixture-source",
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
                "id": "fixture-source",
                "revision": "a" * 40,
                "tree": "b" * 40,
                "files": [
                    {
                        "path": "skills/fixture/SKILL.md",
                        "size": len(content),
                        "sha256": sha256_bytes(content),
                    }
                ],
            }
        ],
        "catalogs": {
            "mengto_skills": [
                {
                    "source_id": "fixture-source",
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
                "source_id": "fixture-source",
                "upstream_path": "skills/fixture/SKILL.md",
                "revision": "a" * 40,
                "authority": "procedural-guidance",
                "role": "test-reference",
                "license": {
                    "spdx": "MIT",
                    "status": "verified",
                    "notice_path": "LICENSE",
                },
                "sha256": sha256_bytes(content),
                "decision": "included",
            }
        ],
    }


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

    def test_lock_rejects_revision_that_does_not_match_registry(self) -> None:
        lock = lock_payload()
        lock["sources"][0]["revision"] = "c" * 40
        with self.assertRaisesRegex(design_stack.ValidationError, "revision"):
            design_stack.validate_lock(registry_payload(), lock, metadata_only=True)

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
                / "design-stack/vendor/fixture-source/skills/fixture/SKILL.md"
            )
            vendored_file.parent.mkdir(parents=True)
            vendored_file.write_bytes(b"changed\n")

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
                / "design-stack/vendor/fixture-source/skills/fixture/SKILL.md"
            )
            vendored_file.parent.mkdir(parents=True)
            vendored_file.write_bytes(content)

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
                }
                if decision == "mapped-to-official":
                    record["reason"] = "Use a reviewed official equivalent."
                    record["official_mapping"] = {
                        "source": "official-runtime",
                        "path": "skills/fixture/SKILL.md",
                        "content_sha256": "c" * 64,
                    }
                with self.assertRaisesRegex(design_stack.ValidationError, "license"):
                    design_stack.validate_provenance(
                        registry_payload(), lock_payload(), provenance
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
                }
                design_stack.validate_provenance(
                    registry_payload(), lock_payload(), provenance
                )

    def test_non_included_decisions_require_reason(self) -> None:
        provenance = provenance_payload()
        provenance["records"][0]["decision"] = "blocked"
        provenance["records"][0]["license"] = {
            "spdx": "NOASSERTION",
            "status": "unresolved",
            "notice_path": None,
        }
        with self.assertRaisesRegex(design_stack.ValidationError, "reason"):
            design_stack.validate_provenance(
                registry_payload(), lock_payload(), provenance
            )

    def test_mapped_decision_requires_content_addressed_official_mapping(self) -> None:
        provenance = provenance_payload()
        record = provenance["records"][0]
        record["decision"] = "mapped-to-official"
        record["reason"] = "Use a reviewed official equivalent."
        with self.assertRaisesRegex(design_stack.ValidationError, "official_mapping"):
            design_stack.validate_provenance(
                registry_payload(), lock_payload(), provenance
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
                if record["decision"] != "included":
                    self.assertTrue(record.get("reason"))

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

    def test_reviewed_runtime_equivalents_are_mapped_and_unlicensed_design_is_blocked(self) -> None:
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
        }
        for path in sorted(mapped_paths):
            with self.subTest(path=path):
                self.assertEqual(decisions[path]["decision"], "mapped-to-official")
                self.assertEqual(decisions[path]["license"]["spdx"], "Apache-2.0")
                self.assertIn("official_mapping", decisions[path])

        frontend_design = decisions["agent-skills/ui/frontend-design/SKILL.md"]
        self.assertEqual(frontend_design["decision"], "blocked")
        self.assertEqual(frontend_design["license"]["status"], "unresolved")


if __name__ == "__main__":
    unittest.main()
