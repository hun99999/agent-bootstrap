import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.frontend_design_test_support import (
    load_script_module,
    sha256_bytes,
    snapshot_tree,
    write_files,
    write_json,
)


source_check = load_script_module("check_design_sources.py")


OLD_SKILL = b"---\nname: fixture\ndescription: Old description.\n---\n\n# Old instructions\n"
NEW_SKILL = b"---\nname: fixture\ndescription: New description.\n---\n\n# New instructions\nhttps://api.example.invalid/v2\n"
LICENSE = b"fixture license\n"


def write_check_fixture(repo_root: Path, candidate_root: Path) -> None:
    source = {
        "id": "mengto-skills",
        "repository": "https://example.invalid/source",
        "revision": "a" * 40,
        "authority": "procedural-guidance",
        "scope": ["skills/**"],
        "license": {
            "spdx": "MIT",
            "status": "verified",
            "notice_path": "LICENSE",
            "notice_sha256": sha256_bytes(LICENSE),
        },
        "role": "fixture",
        "update_method": "reviewed-local-tar",
        "distribution": "vendored",
        "destination": "design-stack/vendor/mengto-skills",
    }
    registry = {
        "schema_version": 1,
        "google_design_md_cli_version": "0.3.0",
        "sources": [source],
    }
    lock = {
        "schema_version": 1,
        "sources": [
            {
                "id": "mengto-skills",
                "revision": "a" * 40,
                "tree": "b" * 40,
                "files": [
                    {
                        "path": "LICENSE",
                        "size": len(LICENSE),
                        "mode": "0644",
                        "sha256": sha256_bytes(LICENSE),
                        "materialization": "vendored",
                    },
                    {
                        "path": "skills/fixture/SKILL.md",
                        "size": len(OLD_SKILL),
                        "mode": "0644",
                        "sha256": sha256_bytes(OLD_SKILL),
                        "materialization": "vendored",
                    },
                    {
                        "path": "skills/old-name.txt",
                        "size": len(b"renamed\n"),
                        "mode": "0644",
                        "sha256": sha256_bytes(b"renamed\n"),
                        "materialization": "vendored",
                    },
                ],
            }
        ],
        "catalogs": {
            "mengto_skills": [
                {
                    "source_id": "mengto-skills",
                    "name": "fixture",
                    "description": "Old description.",
                    "path": "skills/fixture/SKILL.md",
                    "sha256": sha256_bytes(OLD_SKILL),
                }
            ],
            "design_md": [],
        },
    }
    provenance = {
        "schema_version": 1,
        "records": [
            {
                "source_id": "mengto-skills",
                "upstream_path": "skills/fixture/SKILL.md",
                "revision": "a" * 40,
                "authority": "procedural-guidance",
                "catalog": "mengto_skills",
                "role": "fixture",
                "license": copy.deepcopy(source["license"]),
                "origin": {
                    "repository": source["repository"],
                    "path": "skills/fixture/SKILL.md",
                    "revision": "a" * 40,
                    "content_sha256": sha256_bytes(OLD_SKILL),
                    "basis": "fixture",
                    "introduced_revision": "a" * 40,
                    "publisher": "Fixture",
                },
                "sha256": sha256_bytes(OLD_SKILL),
                "decision": "included",
            }
        ],
    }
    write_json(repo_root / "design-stack/sources.json", registry)
    write_json(repo_root / "design-stack/sources.lock.json", lock)
    write_json(repo_root / "design-stack/provenance.json", provenance)
    write_files(
        repo_root / source["destination"],
        {
            "LICENSE": LICENSE,
            "skills/fixture/SKILL.md": OLD_SKILL,
            "skills/old-name.txt": b"renamed\n",
        },
    )
    write_files(
        candidate_root,
        {
            "LICENSE": b"changed license\n",
            "skills/fixture/SKILL.md": NEW_SKILL,
            "skills/new-name.txt": b"renamed\n",
            "skills/fixture/scripts/deploy.sh": (
                b"curl https://deploy.example.invalid --data token\nchmod +x output\n"
            ),
            "skills/fixture/assets/preview.png": b"png",
            "skills/fixture/package.json": (
                b'{"dependencies":{"example":"1.0.0"}}\n'
            ),
        },
    )


class FrontendDesignSourceCheckTests(unittest.TestCase):
    def test_source_check_reports_structural_and_semantic_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            candidate_root = root / "candidate"
            write_check_fixture(repo_root, candidate_root)

            report = source_check.compare_source_tree(
                repo_root, "mengto-skills", candidate_root
            )

        self.assertIn("skills/fixture/scripts/deploy.sh", report["added"])
        self.assertIn("skills/fixture/assets/preview.png", report["added"])
        self.assertIn("skills/old-name.txt", report["removed"])
        self.assertEqual(
            report["renamed"],
            [{"from": "skills/old-name.txt", "to": "skills/new-name.txt"}],
        )
        self.assertEqual(
            report["description_changes"][0]["before"], "Old description."
        )
        self.assertEqual(
            report["description_changes"][0]["after"], "New description."
        )
        self.assertIn("skills/fixture/SKILL.md", report["instruction_changes"])
        self.assertIn("skills/fixture/scripts/deploy.sh", report["scripts"])
        self.assertIn("skills/fixture/assets/preview.png", report["assets"])
        self.assertIn("skills/fixture/package.json", report["dependencies"])
        self.assertTrue(any("api.example.invalid" in url for url in report["urls"]))
        self.assertTrue(report["permissions"])
        self.assertTrue(report["services"])
        self.assertTrue(report["side_effects"])
        self.assertIn("LICENSE", report["license_changes"])
        self.assertIn("skills/fixture/SKILL.md", report["provenance_changes"])

    def test_source_check_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            candidate_root = root / "candidate"
            write_check_fixture(repo_root, candidate_root)
            before_repo = snapshot_tree(repo_root)
            before_candidate = snapshot_tree(candidate_root)

            source_check.compare_source_tree(repo_root, "mengto-skills", candidate_root)

            self.assertEqual(snapshot_tree(repo_root), before_repo)
            self.assertEqual(snapshot_tree(candidate_root), before_candidate)

    def test_source_check_reports_clean_matching_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            candidate_root = root / "candidate"
            write_check_fixture(repo_root, candidate_root)
            source = json.loads(
                (repo_root / "design-stack/sources.json").read_text(encoding="utf-8")
            )["sources"][0]
            old_root = repo_root / source["destination"]

            report = source_check.compare_source_tree(
                repo_root, "mengto-skills", old_root
            )

        self.assertFalse(report["changed"])
        self.assertFalse(report["added"])
        self.assertFalse(report["removed"])
        self.assertFalse(report["renamed"])

    def test_source_check_reports_permission_only_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            initial_candidate = root / "initial-candidate"
            candidate_root = root / "candidate"
            write_check_fixture(repo_root, initial_candidate)
            source = json.loads(
                (repo_root / "design-stack/sources.json").read_text(encoding="utf-8")
            )["sources"][0]
            shutil.copytree(repo_root / source["destination"], candidate_root)
            changed_path = candidate_root / "skills/fixture/SKILL.md"
            changed_path.chmod(0o755)

            report = source_check.compare_source_tree(
                repo_root, "mengto-skills", candidate_root
            )

        self.assertFalse(report["changed"])
        self.assertEqual(
            report["mode_changes"],
            [
                {
                    "path": "skills/fixture/SKILL.md",
                    "before": "0644",
                    "after": "0755",
                }
            ],
        )
        self.assertIn("skills/fixture/SKILL.md", report["provenance_changes"])

    def test_unknown_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            candidate_root = root / "candidate"
            write_check_fixture(repo_root, candidate_root)
            with self.assertRaisesRegex(ValueError, "unknown source"):
                source_check.compare_source_tree(repo_root, "missing", candidate_root)

    def test_human_report_names_each_review_category(self) -> None:
        report = {
            "source_id": "mengto-skills",
            "locked_revision": "a" * 40,
            "added": ["skills/new/SKILL.md"],
            "removed": [],
            "changed": ["skills/fixture/SKILL.md"],
            "mode_changes": [],
            "renamed": [],
            "description_changes": [],
            "instruction_changes": ["skills/fixture/SKILL.md"],
            "parse_errors": [],
            "scripts": ["skills/new/scripts/run.py"],
            "assets": [],
            "dependencies": [],
            "urls": ["https://example.invalid"],
            "permissions": [],
            "services": [],
            "side_effects": [],
            "license_changes": [],
            "provenance_changes": ["skills/new/SKILL.md"],
        }

        rendered = source_check.format_human_report(report)

        self.assertIn("Source: mengto-skills", rendered)
        for label in (
            "Added",
            "Removed",
            "Changed",
            "Modes",
            "Renamed",
            "Descriptions",
            "Instructions",
            "Parse errors",
            "Scripts",
            "Assets",
            "Dependencies",
            "URLs",
            "Permissions",
            "Services",
            "Side effects",
            "Licenses",
            "Provenance",
        ):
            self.assertIn(f"{label}:", rendered)


if __name__ == "__main__":
    unittest.main()
