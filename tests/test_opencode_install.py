import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / ".opencode" / "install.py"


def load_installer_module():
    spec = importlib.util.spec_from_file_location("opencode_install", INSTALLER)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load OpenCode installer from {INSTALLER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_agent_metadata() -> dict[str, dict[str, object]]:
    return json.loads((REPO_ROOT / "shared" / "agent-metadata.json").read_text(encoding="utf-8"))


class OpenCodeInstallTests(unittest.TestCase):
    def run_installer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(INSTALLER),
                "--repo-root",
                str(REPO_ROOT),
                *args,
            ],
            capture_output=True,
            text=True,
        )

    def test_dry_run_reports_opencode_targets_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            opencode_home = Path(tmpdir) / "opencode"
            result = self.run_installer(
                "--partner-name",
                "Hun",
                "--opencode-home",
                str(opencode_home),
                "--dry-run",
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("Dry run:", result.stdout)
            self.assertIn(str(opencode_home.resolve() / "opencode.json"), result.stdout)
            self.assertIn(str(opencode_home.resolve() / "agents" / "eng-lead.md"), result.stdout)
            self.assertFalse(opencode_home.exists())

    def test_install_writes_config_and_rendered_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            opencode_home = Path(tmpdir) / "opencode"
            result = self.run_installer(
                "--partner-name",
                "Hun",
                "--opencode-home",
                str(opencode_home),
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            config = json.loads((opencode_home / "opencode.json").read_text(encoding="utf-8"))
            self.assertEqual(config["$schema"], "https://opencode.ai/config.json")
            self.assertEqual(
                config["plugin"],
                ["superpowers@git+https://github.com/obra/superpowers.git"],
            )
            self.assertEqual(config["default_agent"], "eng-lead")

            eng_lead = (opencode_home / "agents" / "eng-lead.md").read_text(encoding="utf-8")
            reviewer = (opencode_home / "agents" / "reviewer.md").read_text(encoding="utf-8")
            self.assertIn("description: Primary lead for day-to-day work", eng_lead)
            self.assertIn("mode: primary", eng_lead)
            self.assertIn("Hun", eng_lead)
            self.assertIn("description: Review-only work focused on bugs", reviewer)
            self.assertIn("mode: subagent", reviewer)
            self.assertIn("edit: deny", reviewer)

    def test_install_renders_all_agents_from_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            opencode_home = Path(tmpdir) / "opencode"
            result = self.run_installer(
                "--partner-name",
                "Hun",
                "--opencode-home",
                str(opencode_home),
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            rendered_agents = {
                path.stem
                for path in (opencode_home / "agents").glob("*.md")
            }
            self.assertEqual(rendered_agents, set(load_agent_metadata()))

    def test_install_applies_read_only_permissions_from_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            opencode_home = Path(tmpdir) / "opencode"
            result = self.run_installer(
                "--partner-name",
                "Hun",
                "--opencode-home",
                str(opencode_home),
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            for agent_name, metadata in load_agent_metadata().items():
                with self.subTest(agent=agent_name):
                    agent_text = (opencode_home / "agents" / f"{agent_name}.md").read_text(
                        encoding="utf-8"
                    )
                    if metadata["read_only"]:
                        self.assertIn("permission:\n  edit: deny", agent_text)
                    else:
                        self.assertNotIn("permission:\n  edit: deny", agent_text)

    def test_build_frontmatter_rejects_invalid_opencode_mode(self) -> None:
        installer = load_installer_module()

        with self.assertRaisesRegex(ValueError, "invalid opencode_mode"):
            installer.build_frontmatter(
                "worker",
                {
                    "worker": {
                        "description": "Worker",
                        "opencode_mode": "sub-agent",
                        "read_only": False,
                    }
                },
            )

    def test_build_frontmatter_rejects_non_boolean_read_only(self) -> None:
        installer = load_installer_module()

        with self.assertRaisesRegex(ValueError, "invalid read_only"):
            installer.build_frontmatter(
                "worker",
                {
                    "worker": {
                        "description": "Worker",
                        "opencode_mode": "subagent",
                        "read_only": "false",
                    }
                },
            )


if __name__ == "__main__":
    unittest.main()
