import json
import tempfile
import unittest
from pathlib import Path

from scripts import inventory_optional_tools


class OptionalToolInventoryTests(unittest.TestCase):
    def test_inventory_classifies_ts_js_structure_tools_without_installing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "package.json").write_text(
                json.dumps(
                    {
                        "scripts": {
                            "lint": "eslint .",
                            "deps": "dependency-cruiser src",
                        },
                        "devDependencies": {
                            "dependency-cruiser": "^16.0.0",
                            "eslint": "^9.0.0",
                        },
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / "tsconfig.json").write_text(
                json.dumps({"compilerOptions": {"strict": True}}),
                encoding="utf-8",
            )
            (repo_root / "src").mkdir()
            (repo_root / "src" / "index.ts").write_text("export const ok = true;\n", encoding="utf-8")

            results = inventory_optional_tools.build_inventory(
                repo_root,
                command_lookup=lambda command: None,
                path_exists=lambda path: False,
                platform_name="Darwin",
            )
            by_name = {result.name: result for result in results}

        self.assertEqual(by_name["lumin-repo-lens"].decision, "recommended")
        self.assertEqual(by_name["dependency-lint"].decision, "recommended")
        self.assertEqual(by_name["strict-type-checks"].decision, "recommended")
        self.assertEqual(by_name["cycle-detection"].decision, "recommended")
        self.assertEqual(by_name["complexity-limits"].decision, "recommended")
        self.assertEqual(by_name["obsidian"].decision, "optional")
        for result in results:
            self.assertEqual(result.install_status, "not installed by this script")

    def test_json_output_reports_required_decision_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            results = inventory_optional_tools.build_inventory(
                repo_root,
                command_lookup=lambda command: None,
                path_exists=lambda path: False,
                platform_name="Linux",
            )

        payload = json.loads(inventory_optional_tools.render_json(results))
        first = payload["tools"][0]

        self.assertEqual(payload["schema"], "agent-bootstrap.optional-tool-inventory.v1")
        self.assertIn("name", first)
        self.assertIn("detected_state", first)
        self.assertIn("decision", first)
        self.assertIn("reason", first)
        self.assertIn("install_status", first)

    def test_lumin_inventory_reports_existing_audit_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            audit_dir = repo_root / ".audit"
            audit_dir.mkdir()
            (audit_dir / "manifest.json").write_text("{}", encoding="utf-8")
            (audit_dir / "audit-summary.latest.md").write_text("# audit\n", encoding="utf-8")
            (audit_dir / "pre-write-advisory.latest.json").write_text(
                "{}", encoding="utf-8"
            )
            (audit_dir / "post-write-delta.latest.json").write_text(
                "{}", encoding="utf-8"
            )
            (repo_root / "package.json").write_text("{}", encoding="utf-8")

            results = inventory_optional_tools.build_inventory(
                repo_root,
                command_lookup=lambda command: None,
                path_exists=lambda path: False,
                platform_name="Linux",
            )
            lumin = next(result for result in results if result.name == "lumin-repo-lens")

        self.assertIn(".audit/manifest.json exists", lumin.evidence)
        self.assertIn(".audit/audit-summary.latest.md exists", lumin.evidence)
        self.assertIn(".audit/pre-write-advisory.latest.json exists", lumin.evidence)
        self.assertIn(".audit/post-write-delta.latest.json exists", lumin.evidence)


if __name__ == "__main__":
    unittest.main()
