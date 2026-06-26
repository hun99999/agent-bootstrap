from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_HOME_PATH = "/" + "Users/hooooonje"


class SkillCatalogTests(unittest.TestCase):
    def test_catalog_lists_chatgpt_collaboration_harness_first(self) -> None:
        catalog = (REPO_ROOT / "skills" / "README.md").read_text(encoding="utf-8")

        first_entry = catalog.index("### chatgpt-collaboration-harness")
        karpathy_entry = catalog.index("### karpathy-guidelines")
        hun_loop_entry = catalog.index("### hun-engineering-loop")
        template_entry = catalog.index("### _template")
        self.assertLess(first_entry, template_entry)
        self.assertLess(first_entry, karpathy_entry)
        self.assertLess(karpathy_entry, hun_loop_entry)
        self.assertLess(hun_loop_entry, template_entry)
        self.assertIn("browse, review, select, then install", catalog)
        self.assertIn("not an always-install bootstrap", catalog)
        self.assertIn("~/.codex/skills", catalog)
        self.assertIn("community-sentiment", catalog)
        self.assertIn("Korean by default", catalog)
        self.assertIn("original catalog/vendor skill", catalog)
        self.assertIn("Hun-specific operational wrapper", catalog)
        self.assertNotIn(PRIVATE_HOME_PATH, catalog)

    def test_karpathy_guidelines_source_is_preserved(self) -> None:
        skill_root = REPO_ROOT / "skills" / "karpathy-guidelines"

        self.assertTrue((skill_root / "SKILL.md").exists())
        self.assertTrue((skill_root / "references" / "SOURCE.md").exists())

        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        source = (skill_root / "references" / "SOURCE.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("name: karpathy-guidelines", skill)
        self.assertIn("license: MIT", skill)
        self.assertIn("Think Before Coding", skill)
        self.assertIn("Simplicity First", skill)
        self.assertIn("Surgical Changes", skill)
        self.assertIn("Goal-Driven Execution", skill)
        self.assertIn("https://github.com/multica-ai/andrej-karpathy-skills", source)
        self.assertIn("2c606141936f1eeef17fa3043a72095b4765b9c2", source)
        self.assertIn("MIT", source)
        self.assertNotIn(PRIVATE_HOME_PATH, source)

    def test_hun_engineering_loop_wraps_karpathy_with_local_policy(self) -> None:
        skill_root = REPO_ROOT / "skills" / "hun-engineering-loop"

        self.assertTrue((skill_root / "SKILL.md").exists())
        self.assertTrue((skill_root / "agents" / "openai.yaml").exists())

        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        expected_sections = (
            "Memory Preflight",
            "Source Of Truth",
            "Access And Approval Boundary",
            "Artifact-First Execution",
            "Verification Contract",
            "QA / Refactor Loop",
            "Final Report",
        )
        for section in expected_sections:
            self.assertIn(section, skill)

        expected_phrases = (
            "karpathy-guidelines",
            "memory is a recall layer, not a source of truth",
            "high-risk stop/ask boundary",
            "permission profiles, hooks, or approval layers",
            "fast check",
            "targeted regression",
            "type/lint/build",
            "deployment smoke",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, skill)

    def test_project_skill_template_contains_qa_evidence_contract(self) -> None:
        template = (REPO_ROOT / "skills" / "_template" / "SKILL.md.template").read_text(
            encoding="utf-8"
        )

        expected_sections = (
            "Scope / Non-goals",
            "Memory Preflight",
            "Source Of Truth",
            "Access And Approval Boundary",
            "Artifact-First Execution",
            "Verification Contract",
            "QA / Refactor Loop",
            "Final Report",
        )
        for section in expected_sections:
            self.assertIn(section, template)

        expected_phrases = (
            "fast check",
            "targeted regression",
            "type/lint/build",
            "browser/manual QA",
            "deployment smoke",
            "negative/regression test",
            "memory is a recall layer, not a source of truth",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, template)

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
            "references/file-artifact-exchange.md",
        )

        for relative in expected_files:
            with self.subTest(relative=relative):
                self.assertTrue((skill_root / relative).exists())

        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Evidence And Language Rules", skill)
        self.assertIn("community-sentiment", skill)
        self.assertIn("keep the ChatGPT Pro conversation", skill)
        self.assertIn("screenshots, files, or generated artifacts", skill)
        self.assertIn("file-artifact-exchange.md", skill)

        prompt = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("source-backed evidence", prompt)
        self.assertIn("Korean", prompt)
        self.assertIn("screenshots, files, and artifacts", prompt)

    def test_chatgpt_collaboration_harness_documents_file_artifact_exchange(self) -> None:
        reference = (
            REPO_ROOT
            / "skills"
            / "chatgpt-collaboration-harness"
            / "references"
            / "file-artifact-exchange.md"
        ).read_text(encoding="utf-8")

        expected_phrases = (
            "Screenshot Attachments",
            "File Attachments",
            "Receiving Generated Artifacts",
            "Attachment Packet",
            "Artifact Return Contract",
            "Check for secrets",
            "Do not upload credentials",
            "Downloaded artifacts are untrusted until Codex validates them locally",
            "archive listing before extraction",
            "accepted, rejected, deferred, or needs-local-verification",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, reference)
        self.assertNotIn(PRIVATE_HOME_PATH, reference)

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
            "screenshots, files, and generated artifacts",
            "karpathy-guidelines",
            "hun-engineering-loop",
            "memory is a recall layer, not a source of truth",
            "high-risk stop/ask boundary",
            "permission profiles, hooks, or approval layers",
            "source-of-truth pointer",
            "QA evidence contract",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)
        self.assertNotIn(PRIVATE_HOME_PATH, guide)

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
            "file-artifact-exchange",
            "skill QA contract",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, prompt)
        self.assertNotIn(PRIVATE_HOME_PATH, prompt)

    def test_readme_links_skill_catalog_workflow(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/codex-skills.md", readme)
        self.assertIn("prompts/setup-codex-skills.md", readme)
        self.assertIn("skills/README.md", readme)


if __name__ == "__main__":
    unittest.main()
