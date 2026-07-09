import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.frontend_design_test_support import (
    load_script_module,
    sha256_bytes,
    snapshot_tree,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins/frontend-design-pack"
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


renderer = load_script_module("render_frontend_design_plugin.py")


class FrontendDesignPluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(
            (REPO_ROOT / "design-stack/sources.json").read_text(encoding="utf-8")
        )
        cls.lock = json.loads(
            (REPO_ROOT / "design-stack/sources.lock.json").read_text(
                encoding="utf-8"
            )
        )
        cls.provenance = json.loads(
            (REPO_ROOT / "design-stack/provenance.json").read_text(
                encoding="utf-8"
            )
        )

    def test_renderer_is_deterministic_and_tracked_output_is_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first"
            second = root / "second"

            renderer.render_plugin(REPO_ROOT, first)
            renderer.render_plugin(REPO_ROOT, second)

            first_snapshot = snapshot_tree(first)
            self.assertEqual(first_snapshot, snapshot_tree(second))
            self.assertEqual(first_snapshot, snapshot_tree(PLUGIN_ROOT))

    def test_codex_and_claude_manifests_share_name_and_semver(self) -> None:
        codex = json.loads(
            (PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        claude = json.loads(
            (PLUGIN_ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )
        marketplace = json.loads(
            (REPO_ROOT / ".claude-plugin/marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        marketplace_entry = {
            entry["name"]: entry for entry in marketplace["plugins"]
        }["frontend-design-pack"]

        self.assertEqual(codex["name"], "frontend-design-pack")
        self.assertEqual(claude["name"], "frontend-design-pack")
        self.assertEqual(codex["version"], claude["version"])
        self.assertEqual(codex["version"], marketplace_entry["version"])
        self.assertRegex(codex["version"], SEMVER_PATTERN)
        self.assertEqual(codex["skills"], "./skills/")
        self.assertEqual(
            marketplace_entry["source"], "./plugins/frontend-design-pack"
        )

    def test_codex_manifest_includes_required_interface_metadata(self) -> None:
        codex = json.loads(
            (PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            codex["interface"],
            {
                "capabilities": ["Interactive", "Read", "Write"],
                "category": "Creativity",
                "defaultPrompt": [
                    "Shape a frontend brief and choose the right design workflow",
                    "Explore three evidence-backed visual directions",
                    "Review this frontend for UX, accessibility, and polish",
                ],
                "developerName": "Hun",
                "displayName": "Frontend Design Pack",
                "longDescription": (
                    "Shape, explore, implement, review, write, and harden frontend "
                    "experiences with one evidence-first router and a reviewed "
                    "reference corpus."
                ),
                "shortDescription": "Evidence-first frontend design workflows",
            },
        )

    def test_plugin_contains_exactly_one_native_self_contained_skill(self) -> None:
        skill_files = sorted(PLUGIN_ROOT.rglob("SKILL.md"))
        self.assertEqual(
            [path.relative_to(PLUGIN_ROOT).as_posix() for path in skill_files],
            ["skills/frontend-design/SKILL.md"],
        )
        self.assertFalse(any(path.is_symlink() for path in PLUGIN_ROOT.rglob("*")))
        skill_text = skill_files[0].read_text(encoding="utf-8")
        self.assertNotIn("../", skill_text)
        for relative_path in (
            "references/source-precedence.md",
            "references/quality-gates.md",
            "references/routing.json",
            "references/reference-catalog.json",
        ):
            self.assertTrue(
                (PLUGIN_ROOT / "skills/frontend-design" / relative_path).is_file(),
                relative_path,
            )

    def test_reference_catalog_resolves_every_approved_source_decision(self) -> None:
        skill_root = PLUGIN_ROOT / "skills/frontend-design"
        catalog = json.loads(
            (skill_root / "references/reference-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        provenance = {
            (record["source_id"], record["upstream_path"]): record
            for record in self.provenance["records"]
        }
        mengto_entries = catalog["mengto_skills"]
        self.assertEqual(len(mengto_entries), 95)
        for entry in mengto_entries:
            source_key = (entry["source_id"], entry["source_path"])
            decision = provenance[source_key]
            with self.subTest(path=entry["source_path"]):
                self.assertEqual(entry["decision"], decision["decision"])
                if entry["decision"] == "included":
                    reference_path = skill_root / entry["reference_path"]
                    self.assertTrue(reference_path.is_file())
                    self.assertEqual(
                        sha256_bytes(reference_path.read_bytes()), decision["sha256"]
                    )
                else:
                    self.assertEqual(entry["decision"], "mapped-to-official")
                    self.assertNotIn("reference_path", entry)
                    self.assertEqual(
                        entry["official_mapping"], decision["official_mapping"]
                    )

        design_entries = catalog["design_md"]
        self.assertEqual(len(design_entries), 74)
        self.assertTrue(
            all(
                (skill_root / entry["reference_path"]).is_file()
                and entry["authority"] == "third-party-analysis"
                for entry in design_entries
            )
        )
        self.assertTrue(
            (skill_root / catalog["vercel_interface"]["reference_path"]).is_file()
        )
        self.assertTrue(
            (skill_root / catalog["google_design_md"]["reference_path"]).is_file()
        )

    def test_plugin_carries_required_notices_for_every_copied_source(self) -> None:
        notices = (PLUGIN_ROOT / "THIRD_PARTY_NOTICES.md").read_text(
            encoding="utf-8"
        )
        sources = {
            source["id"]: source
            for source in self.registry["sources"]
            if source["distribution"] == "vendored"
        }
        for source_id, source in sources.items():
            with self.subTest(source=source_id):
                self.assertIn(source["repository"], notices)
                self.assertIn(source["revision"], notices)
                notice_copy = PLUGIN_ROOT / "licenses" / f"{source_id}.txt"
                self.assertTrue(notice_copy.is_file())
                self.assertEqual(
                    sha256_bytes(notice_copy.read_bytes()),
                    source["license"]["notice_sha256"],
                )

    def test_runtime_copy_validation_reports_missing_changed_and_unexpected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_root = Path(temp_dir) / "runtime"
            shutil.copytree(PLUGIN_ROOT, runtime_root)
            renderer.validate_runtime_copy(PLUGIN_ROOT, runtime_root, "Codex")

            missing = runtime_root / "skills/frontend-design/SKILL.md"
            missing.unlink()
            with self.assertRaisesRegex(ValueError, "Codex.*missing"):
                renderer.validate_runtime_copy(PLUGIN_ROOT, runtime_root, "Codex")

            shutil.copy2(
                PLUGIN_ROOT / "skills/frontend-design/SKILL.md", missing
            )
            missing.write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Codex.*changed"):
                renderer.validate_runtime_copy(PLUGIN_ROOT, runtime_root, "Codex")

            shutil.copy2(
                PLUGIN_ROOT / "skills/frontend-design/SKILL.md", missing
            )
            (runtime_root / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Codex.*unexpected"):
                renderer.validate_runtime_copy(PLUGIN_ROOT, runtime_root, "Codex")

    def test_cli_validates_codex_and_claude_runtime_roots_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            codex_root = root / "codex"
            claude_root = root / "claude"
            shutil.copytree(PLUGIN_ROOT, codex_root)
            shutil.copytree(PLUGIN_ROOT, claude_root)
            result = subprocess.run(
                [
                    "python3",
                    "scripts/validate_frontend_design_stack.py",
                    "--repo-root",
                    str(REPO_ROOT),
                    "--codex-runtime-root",
                    str(codex_root),
                    "--claude-runtime-root",
                    str(claude_root),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Codex runtime", result.stdout)
        self.assertIn("Claude runtime", result.stdout)


if __name__ == "__main__":
    unittest.main()
