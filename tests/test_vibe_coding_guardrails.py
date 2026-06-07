import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class VibeCodingGuardrailsDocsTests(unittest.TestCase):
    def test_gitignore_ignores_local_audit_artifacts(self) -> None:
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn(".audit/", gitignore)

    def test_public_guardrail_guide_covers_cross_platform_workflow(self) -> None:
        guide_path = REPO_ROOT / "docs" / "vibe-coding-guardrails.md"

        self.assertTrue(guide_path.exists(), f"missing guide: {guide_path}")
        guide = guide_path.read_text(encoding="utf-8")

        expected_phrases = (
            "Pre-write lens",
            "Write gate",
            "Post-write review",
            "macOS",
            "Windows PowerShell",
            "Codex",
            "Claude Code",
            "OpenCode",
            "Lumin Repo Lens",
            "Obsidian",
            ".audit/",
            "Do not commit personal vault paths",
            "external boundaries",
            "silent fallback",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)

    def test_global_guardrail_setup_explains_user_home_and_project_scope(self) -> None:
        guide_path = REPO_ROOT / "docs" / "global-guardrail-setup.md"

        self.assertTrue(guide_path.exists(), f"missing guide: {guide_path}")
        guide = guide_path.read_text(encoding="utf-8")

        expected_phrases = (
            "Global guardrail setup",
            "~/.codex",
            "~/.config/opencode",
            "Claude Code plugin",
            "user-level defaults",
            "project-local knowledge",
            "new sessions",
            "existing sessions",
            "restart",
            "macOS",
            "Windows PowerShell",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)

    def test_global_guardrail_setup_explains_optional_tool_install_rules(self) -> None:
        guide_path = REPO_ROOT / "docs" / "global-guardrail-setup.md"

        self.assertTrue(guide_path.exists(), f"missing guide: {guide_path}")
        guide = guide_path.read_text(encoding="utf-8")

        expected_phrases = (
            "Optional Tooling Decision Rules",
            "Inventory first",
            "Recommend",
            "Ask before installing",
            "Skip installation",
            "Obsidian",
            "Lumin Repo Lens",
            "macOS check",
            "Windows PowerShell check",
            "brew install --cask obsidian",
            "winget search Obsidian",
            "Never install a tool just because a guide mentions it",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)

    def test_local_project_knowledge_template_captures_operational_index(self) -> None:
        template_path = REPO_ROOT / "docs" / "local-project-knowledge-template.md"

        self.assertTrue(template_path.exists(), f"missing template: {template_path}")
        template = template_path.read_text(encoding="utf-8")

        expected_headings = (
            "Project Purpose",
            "Architecture Map",
            "Source Of Truth",
            "Module Boundaries",
            "Dependency Direction",
            "Public APIs And Re-Exports",
            "Test Strategy",
            "Error Boundaries",
            "Known Hotspots",
            "Commands",
            "Decisions",
        )
        for heading in expected_headings:
            self.assertIn(heading, template)

        self.assertNotIn("/Users/", template)
        self.assertNotIn("C:\\Users\\", template)

    def test_copy_paste_prompts_cover_apply_and_start_workflows(self) -> None:
        prompt_paths = (
            REPO_ROOT / "prompts" / "apply-vibe-coding-guardrails.md",
            REPO_ROOT / "prompts" / "start-with-vibe-coding-guardrails.md",
        )

        for prompt_path in prompt_paths:
            with self.subTest(prompt=prompt_path.name):
                self.assertTrue(prompt_path.exists(), f"missing prompt: {prompt_path}")
                prompt = prompt_path.read_text(encoding="utf-8")
                self.assertIn("pre-write", prompt.lower())
                self.assertIn("post-write", prompt.lower())
                self.assertIn("TDD", prompt)
                self.assertIn("edge cases", prompt)
                self.assertIn("do not commit", prompt.lower())

    def test_apply_prompt_requires_optional_tool_inventory_before_install(self) -> None:
        prompt_path = REPO_ROOT / "prompts" / "apply-vibe-coding-guardrails.md"

        self.assertTrue(prompt_path.exists(), f"missing prompt: {prompt_path}")
        prompt = prompt_path.read_text(encoding="utf-8")

        expected_phrases = (
            "docs/global-guardrail-setup.md",
            "inventory optional tools",
            "Obsidian",
            "Lumin Repo Lens",
            "ask before installing",
            "do not install",
            "macOS",
            "Windows PowerShell",
            "verify the package name",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, prompt)


if __name__ == "__main__":
    unittest.main()
