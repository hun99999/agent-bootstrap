from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class SkillCatalogTests(unittest.TestCase):
    def test_catalog_lists_chatgpt_collaboration_harness_first(self) -> None:
        catalog = (REPO_ROOT / "skills" / "README.md").read_text(encoding="utf-8")

        first_entry = catalog.index("### chatgpt-collaboration-harness")
        template_entry = catalog.index("### _template")
        self.assertLess(first_entry, template_entry)
        self.assertIn("browse, review, select, then install", catalog)
        self.assertIn("not an always-install bootstrap", catalog)
        self.assertIn("~/.codex/skills", catalog)
        self.assertIn("community-sentiment", catalog)
        self.assertIn("Korean by default", catalog)
        self.assertNotIn("/Users/hooooonje", catalog)

    def test_chatgpt_collaboration_harness_source_is_cataloged(self) -> None:
        skill_root = REPO_ROOT / "skills" / "chatgpt-collaboration-harness"
        expected_files = (
            "SKILL.md",
            "agents/openai.yaml",
            "references/goal-harness.md",
            "references/feedback-loop.md",
            "references/chrome-chatgpt-pro.md",
            "references/delegated-work.md",
            "references/search-deep-research.md",
        )

        for relative in expected_files:
            with self.subTest(relative=relative):
                self.assertTrue((skill_root / relative).exists())

        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Evidence And Language Rules", skill)
        self.assertIn("community-sentiment", skill)
        self.assertIn("keep the ChatGPT Pro conversation", skill)

        prompt = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("source-backed evidence", prompt)
        self.assertIn("Korean", prompt)

    def test_skill_setup_guide_documents_selective_install_flow(self) -> None:
        guide = (REPO_ROOT / "docs" / "codex-skills.md").read_text(encoding="utf-8")

        expected_phrases = (
            "Skill Catalog",
            "browse, review, select, install",
            "repo copy is the catalog source",
            "installed copy is the runtime copy",
            "Do not install every skill automatically",
            "git status --short --branch",
            "quick_validate.py",
            "PyYAML",
            "community-sentiment",
            "one ChatGPT work tab or conversation per project",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)
        self.assertNotIn("/Users/hooooonje", guide)

    def test_setup_prompt_keeps_installation_approval_gated(self) -> None:
        prompt = (REPO_ROOT / "prompts" / "setup-codex-skills.md").read_text(
            encoding="utf-8"
        )

        expected_phrases = (
            "Review and optionally install Codex skills from this repository.",
            "git status --short --branch",
            "skills/README.md",
            "docs/codex-skills.md",
            "chatgpt-collaboration-harness",
            "Compare the catalog copy with the installed runtime copy",
            "Ask before installing or overwriting",
            "quick_validate.py",
            "Do not copy private paths, credentials, MCP endpoints, auth state, or browser profiles",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, prompt)
        self.assertNotIn("/Users/hooooonje", prompt)

    def test_readme_links_skill_catalog_workflow(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/codex-skills.md", readme)
        self.assertIn("prompts/setup-codex-skills.md", readme)
        self.assertIn("skills/README.md", readme)


if __name__ == "__main__":
    unittest.main()
