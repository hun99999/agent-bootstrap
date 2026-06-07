import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LANGUAGE_SWITCHER = "[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)"


class ReadmeDocsTests(unittest.TestCase):
    def test_main_readme_has_language_switcher_and_value_props(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(LANGUAGE_SWITCHER, readme)
        self.assertIn("Codex, Claude Code, and OpenCode", readme)
        self.assertIn("superpowers", readme)
        self.assertIn("subagents", readme)
        self.assertIn("token-efficient", readme)

    def test_translated_readmes_exist_with_language_switcher(self) -> None:
        for relative in ("README.ko.md", "README.ja.md", "README.zh-CN.md"):
            contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(LANGUAGE_SWITCHER, contents)

    def test_repo_metadata_doc_exists(self) -> None:
        metadata = (REPO_ROOT / "docs" / "repo-metadata.md").read_text(encoding="utf-8")

        self.assertIn("Repository description", metadata)
        self.assertIn("Topics", metadata)
        self.assertIn("Social preview", metadata)

    def test_codex_superpowers_docs_explain_plugin_and_manual_modes(self) -> None:
        expected_phrases = (
            "Codex App curated Superpowers plugin",
            "manual ~/.codex/superpowers fallback",
            "duplicate skill entries",
        )

        for relative in ("README.md", "docs/README.codex.md", ".codex/INSTALL.md"):
            contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
            for phrase in expected_phrases:
                self.assertIn(phrase, contents)

    def test_docs_explain_agent_stack_audit_command(self) -> None:
        for relative in (
            "README.md",
            "README.ko.md",
            "README.ja.md",
            "README.zh-CN.md",
            "docs/README.codex.md",
            "docs/README.claude.md",
            "docs/README.opencode.md",
        ):
            contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("scripts/audit_agent_stack.py", contents)

    def test_translated_readmes_mention_duplicate_superpowers_discovery(self) -> None:
        expected_phrases = {
            "README.ko.md": "중복 skill 항목",
            "README.ja.md": "重複する skill 項目",
            "README.zh-CN.md": "重复的 skill 条目",
        }

        for relative, phrase in expected_phrases.items():
            contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(phrase, contents)

    def test_readme_links_vibe_coding_guardrails(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/vibe-coding-guardrails.md", readme)
        self.assertIn("prompts/apply-vibe-coding-guardrails.md", readme)
        self.assertIn("prompts/start-with-vibe-coding-guardrails.md", readme)


if __name__ == "__main__":
    unittest.main()
