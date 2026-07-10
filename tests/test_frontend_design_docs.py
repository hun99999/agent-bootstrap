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
            "If the live Codex root is the tracked plugin root",
            "install or update only a distinct cached runtime after approval",
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
            "receipt is not an authority",
            "pinned root-tree Merkle proof",
            "receipt schema v1",
            "package-level provenance",
            "Preview HTML",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)

    def test_open_design_reference_documents_the_offline_trust_anchor(self) -> None:
        reference = (
            REPO_ROOT / "design-stack/router/references/open-design.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "receipt is an untrusted witness",
            "pinned root tree",
            "receipt schema v1",
            "fail without mutation",
        ):
            self.assertIn(phrase, reference)

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

    def test_claude_onboarding_uses_the_public_identity_and_design_contract(self) -> None:
        prompt = (REPO_ROOT / "prompts/setup-claude-current-harness.md").read_text(
            encoding="utf-8"
        )
        guide = (REPO_ROOT / "docs/README.claude.md").read_text(encoding="utf-8")
        for contents in (prompt, guide):
            for phrase in (
                "Ask the user what name",
                "<chosen-name>",
                "frontend-design-pack",
                "docs/frontend-design-stack.md",
                "validate_frontend_design_stack.py",
                "fresh Claude Code session",
                "models and reasoning",
                "Do not hard-code",
                "Keep the chosen name local",
                "do not commit",
            ):
                self.assertIn(phrase, contents)
            self.assertNotIn('--partner-name "Hun"', contents)
            self.assertIsNone(re.search(r"\bclaude-[0-9]", contents))

    def test_update_prompt_covers_tracked_and_installed_design_runtime_updates(self) -> None:
        prompt = (REPO_ROOT / "prompts/update-agent-bootstrap.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "design-stack/",
            "scripts/render_frontend_design_plugin.py",
            "python3 scripts/render_frontend_design_plugin.py --repo-root .",
            "plugins/frontend-design-pack/",
            "validate_frontend_design_stack.py",
            "resolve each live runtime root",
            "local Codex marketplace may resolve to the tracked plugin root",
            "a cached install may be distinct",
            "replacing a distinct stale cached install",
            "fresh task or session",
            "vercel-react-best-practices",
            "vercel-composition-patterns",
            "vercel-react-view-transitions",
            ".claude-plugin/marketplace.json",
            "marketplace metadata belongs in scripts/render_claude_plugin.py",
        ):
            self.assertIn(phrase, prompt)

    def test_first_class_guides_never_render_a_public_default_partner_name(self) -> None:
        for relative_path in (
            "docs/global-guardrail-setup.md",
            "docs/agent-setup-playbook.md",
            "docs/vibe-coding-guardrails.md",
        ):
            with self.subTest(document=relative_path):
                contents = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("Ask the user what name", contents)
                self.assertIn("<chosen-name>", contents)
                self.assertIn("models and reasoning", contents)
                self.assertIn("Keep the chosen name local", contents)
                self.assertIn("do not commit", contents)
                self.assertNotIn('--partner-name "Hun"', contents)
                self.assertNotIn("Hun explicitly", contents)
                self.assertNotIn("Hun's personal", contents)

    def test_public_readme_update_sections_route_installed_design_runtime_updates(self) -> None:
        headings = {
            "README.md": "## Pull And Update Workflow",
            "README.ko.md": "## Pull And Update Workflow",
            "README.ja.md": "Existing clone update:",
            "README.zh-CN.md": "Existing clone update:",
        }
        for relative_path, heading in headings.items():
            with self.subTest(readme=relative_path):
                contents = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                update_section = contents[contents.index(heading) :]
                for phrase in (
                    "docs/frontend-design-stack.md",
                    "prompts/update-agent-bootstrap.md",
                    "live runtime root",
                    "local Codex marketplace",
                    "cached install",
                    "fresh",
                ):
                    self.assertIn(phrase, update_section)

    def test_public_readmes_keep_rendered_identity_local_and_user_scoped(self) -> None:
        expected_identity_boundaries = {
            "README.md": "Do not commit the chosen name or rendered files that contain it.",
            "README.ko.md": "선택한 이름이나 그 이름이 들어간 렌더 결과는 커밋하지 마라.",
            "README.ja.md": "選択した名前や、その名前を含む render 結果を commit しないでください。",
            "README.zh-CN.md": "不要提交所选名称或包含该名称的 render 结果。",
        }
        for relative_path, expected in expected_identity_boundaries.items():
            with self.subTest(readme=relative_path):
                contents = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(expected, contents)
                self.assertNotIn("Hun explicitly", contents)

    def test_setup_guide_includes_copyable_router_usage_and_claude_companions(self) -> None:
        guide = (REPO_ROOT / "docs/frontend-design-stack.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "## Use The Frontend Design Router",
            "frontend-design skill",
            "review mode",
            "implement and then harden",
            "shape mode",
            "explore mode",
            "Figma URL",
            "exact Open Design slug",
            "--agent claude-code",
            "claude plugin list --json",
            "live runtime root",
            "may be the tracked plugin root",
        ):
            self.assertIn(phrase, guide)
        self.assertNotIn("and Ask before", guide)

    def test_structure_and_public_readmes_map_the_design_source_and_plugin(self) -> None:
        structure = (REPO_ROOT / "docs/agent-bootstrap-structure.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "design-stack/",
            "plugins/frontend-design-pack/",
            "scripts/render_frontend_design_plugin.py",
            "scripts/validate_frontend_design_stack.py",
            "resolve the live Codex and Claude runtime roots",
            "local Codex marketplace may resolve to the tracked plugin root",
            "cached install may be distinct",
            "Validate each resolved live root",
        ):
            self.assertIn(phrase, structure)
        for relative_path in PUBLIC_READMES:
            with self.subTest(readme=relative_path):
                contents = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("design-stack/", contents)
                self.assertIn("plugins/frontend-design-pack/", contents)

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
