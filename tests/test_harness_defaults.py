import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class HarnessDefaultTests(unittest.TestCase):
    def test_main_readme_has_supported_surface_scope(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Current Supported Surfaces", readme)
        self.assertIn("Codex and Claude Code are the only first-class setup targets", readme)
        self.assertIn("OpenCode and OpenClaw are legacy/reference material", readme)
        self.assertIn("prompts/setup-codex-current-harness.md", readme)
        self.assertIn("prompts/setup-claude-current-harness.md", readme)
        self.assertNotIn("prompts/setup-opencode-current-harness.md", readme)
        self.assertNotIn("prompts/setup-openclaw-acp.md", readme)

    def test_harness_docs_define_current_first_class_defaults(self) -> None:
        codex_doc = (REPO_ROOT / "docs" / "README.codex.md").read_text(encoding="utf-8")
        claude_doc = (REPO_ROOT / "docs" / "README.claude.md").read_text(encoding="utf-8")

        self.assertIn("current-harness-only", codex_doc)
        self.assertIn("standing delegation preference", codex_doc)
        self.assertIn("current-harness-only", claude_doc)

    def test_legacy_docs_are_marked_non_default(self) -> None:
        opencode_doc = (REPO_ROOT / "docs" / "README.opencode.md").read_text(
            encoding="utf-8"
        )
        openclaw_doc = (REPO_ROOT / "docs" / "README.openclaw.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("legacy/reference material", opencode_doc)
        self.assertIn("not a current first-class setup target", opencode_doc)
        self.assertIn("Do not run the OpenCode installer for a fresh setup", opencode_doc)
        self.assertIn("legacy/reference material", openclaw_doc)
        self.assertIn("not a current first-class bootstrap target", openclaw_doc)
        self.assertIn("Use ACP only when the user explicitly asks for ACP", openclaw_doc)

    def test_current_harness_setup_prompts_exist(self) -> None:
        codex_prompt = (REPO_ROOT / "prompts" / "setup-codex-current-harness.md").read_text(
            encoding="utf-8"
        )
        claude_prompt = (
            REPO_ROOT / "prompts" / "setup-claude-current-harness.md"
        ).read_text(encoding="utf-8")

        self.assertIn("current-harness-only", codex_prompt)
        self.assertIn("current-harness-only", claude_prompt)
        self.assertIn("Do not configure another harness unless the user explicitly asks.", codex_prompt)
        self.assertIn("Do not configure another harness unless the user explicitly asks.", claude_prompt)

    def test_legacy_setup_prompts_stop_without_explicit_request(self) -> None:
        opencode_prompt = (
            REPO_ROOT / "prompts" / "setup-opencode-current-harness.md"
        ).read_text(encoding="utf-8")
        openclaw_shared = (
            REPO_ROOT / "prompts" / "setup-openclaw-shared-core.md"
        ).read_text(encoding="utf-8")
        openclaw_acp = (REPO_ROOT / "prompts" / "setup-openclaw-acp.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("legacy OpenCode prompt", opencode_prompt)
        self.assertIn("Proceed only if Hun explicitly asked", opencode_prompt)
        self.assertIn("legacy OpenClaw shared-core prompt", openclaw_shared)
        self.assertIn("Proceed only if Hun explicitly asked", openclaw_shared)
        self.assertIn("legacy OpenClaw ACP integration prompt", openclaw_acp)
        self.assertIn("Use this mode only if Hun explicitly asks for ACP integration", openclaw_acp)


if __name__ == "__main__":
    unittest.main()
