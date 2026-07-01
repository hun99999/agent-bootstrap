import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class SharedCoreScopeTests(unittest.TestCase):
    def test_main_readme_routes_unclear_harness_to_confirmation(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(
            "If no supported harness is clear, stop and ask which supported harness to configure.",
            readme,
        )
        self.assertIn("prompts/setup-shared-core.md", readme)
        self.assertNotIn("prompts/setup-openclaw-shared-core.md", readme)

    def test_openclaw_doc_is_legacy_reference_only(self) -> None:
        openclaw_doc = (REPO_ROOT / "docs" / "README.openclaw.md").read_text(encoding="utf-8")

        self.assertIn("OpenClaw is legacy/reference material", openclaw_doc)
        self.assertIn("Path A: legacy shared-core-only", openclaw_doc)
        self.assertIn("Path B: ACP integration", openclaw_doc)
        self.assertIn("do not choose Codex-first", openclaw_doc)

    def test_setup_prompts_exist_for_shared_core_and_legacy_openclaw(self) -> None:
        shared_core = (REPO_ROOT / "prompts" / "setup-shared-core.md").read_text(encoding="utf-8")
        openclaw_shared = (
            REPO_ROOT / "prompts" / "setup-openclaw-shared-core.md"
        ).read_text(encoding="utf-8")
        openclaw_acp = (REPO_ROOT / "prompts" / "setup-openclaw-acp.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("shared-core-only", shared_core)
        self.assertIn("Do not choose a harness unless the user explicitly asks for one.", shared_core)
        self.assertIn("legacy OpenClaw shared-core prompt", openclaw_shared)
        self.assertIn("Do not choose Codex-first", openclaw_shared)
        self.assertIn("legacy OpenClaw ACP integration prompt", openclaw_acp)
        self.assertIn("Use this mode only if Hun explicitly asks for ACP integration", openclaw_acp)


if __name__ == "__main__":
    unittest.main()
