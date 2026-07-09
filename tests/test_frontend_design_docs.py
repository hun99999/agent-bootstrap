import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_READMES = (
    "README.md",
    "README.ko.md",
    "README.ja.md",
    "README.zh-CN.md",
)


class FrontendDesignDocumentationTests(unittest.TestCase):
    def test_every_public_readme_links_the_frontend_design_setup_guide(self) -> None:
        for relative_path in PUBLIC_READMES:
            with self.subTest(readme=relative_path):
                contents = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("docs/frontend-design-stack.md", contents)

    def test_setup_guide_documents_public_install_update_and_evidence_contract(self) -> None:
        guide = (REPO_ROOT / "docs/frontend-design-stack.md").read_text(
            encoding="utf-8"
        )
        expected_phrases = (
            "Ask the user what partner name",
            "inherit the models and reasoning levels",
            "frontend-design-pack@agent-bootstrap",
            "Ask before installing, updating, or replacing",
            "tracked plugin",
            "runtime copy",
            "fresh Codex task",
            "fresh Claude Code session",
            "report whether Figma is available",
            "Do not authenticate Figma",
            "successful build is not visual verification",
            "HTTP 200 is not visual verification",
            "source inspection is not visual verification",
            "Open Design is on-demand",
            "third-party analysis",
            "check_design_sources.py",
            "sync_design_sources.py",
            "human diff review",
            "semantic version",
            "Rollback",
            "git -c tar.umask=0022 archive",
            "npx -y skills@latest add vercel-labs/agent-skills",
            "vercel-react-best-practices",
            "vercel-composition-patterns",
            "vercel-react-view-transitions",
            "npx -y skills@latest update",
            "Do not guess their runtime paths",
            "new Codex task",
            "open_design_cache.py list --explicit-demand",
            "open_design_cache.py fetch --explicit-demand",
            "open_design_cache.py verify --explicit-demand",
            "fail without deleting or overwriting",
            "package-level provenance",
            "Preview HTML",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)

    def test_setup_prompts_keep_identity_models_plugins_and_figma_approval_gated(self) -> None:
        for relative_path in (
            "prompts/fresh-install.md",
            "prompts/setup-codex-current-harness.md",
        ):
            contents = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(prompt=relative_path):
                for phrase in (
                    "Ask the user what name",
                    "inherits its supported selection and account ceiling",
                    "frontend-design-pack",
                    "Ask before installing or replacing",
                    "tracked plugin",
                    "runtime copy",
                    "fresh task",
                    "Figma",
                    "Do not authenticate",
                ):
                    self.assertIn(phrase, contents)
                self.assertNotIn('--partner-name "Hun"', contents)
                self.assertIsNone(re.search(r"\bgpt-[0-9]", contents))
                self.assertIsNone(re.search(r"\bclaude-[0-9]", contents))

    def test_codex_docs_do_not_pin_private_identity_or_model_entitlement(self) -> None:
        for relative_path in ("docs/README.codex.md", ".codex/INSTALL.md"):
            contents = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(document=relative_path):
                self.assertNotIn('--partner-name "Hun"', contents)
                self.assertIsNone(re.search(r"\bgpt-[0-9]", contents))
                self.assertIn("docs/frontend-design-stack.md", contents)
                self.assertIn("frontend-design-pack", contents)

    def test_frontend_design_is_distributed_only_through_the_plugin(self) -> None:
        self.assertFalse((REPO_ROOT / "skills/frontend-design").exists())
        self.assertTrue(
            (
                REPO_ROOT
                / "plugins/frontend-design-pack/skills/frontend-design/SKILL.md"
            ).is_file()
        )


if __name__ == "__main__":
    unittest.main()
