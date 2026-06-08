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

        self.assertNotIn("/" + "Users/", template)
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

    def test_agent_setup_playbook_gives_agents_executable_setup_guidance(self) -> None:
        playbook_path = REPO_ROOT / "docs" / "agent-setup-playbook.md"

        self.assertTrue(playbook_path.exists(), f"missing playbook: {playbook_path}")
        playbook = playbook_path.read_text(encoding="utf-8")

        expected_phrases = (
            "Agent Setup Playbook",
            "Success Criteria",
            "Discovery Pass",
            "Scope Decision",
            "Environment Inventory",
            "Required, Recommended, Optional, Skipped",
            "Installation Approval Gate",
            "Setup Paths",
            "Verification Matrix",
            "Existing Sessions",
            "Final Report Template",
            "Do not claim completion",
            "No private paths",
            "macOS",
            "Windows PowerShell",
            "Codex",
            "Claude Code",
            "OpenCode",
            "Obsidian",
            "Lumin Repo Lens",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, playbook)

    def test_readmes_point_master_prompt_at_agent_setup_playbook(self) -> None:
        for relative in ("README.md", "README.ko.md", "README.ja.md", "README.zh-CN.md"):
            with self.subTest(relative=relative):
                readme = (REPO_ROOT / relative).read_text(encoding="utf-8")
                master_prompt = readme.split("```", maxsplit=2)[1]

                self.assertIn("docs/agent-setup-playbook.md", master_prompt)

    def test_playbook_points_agents_at_optional_tool_inventory_script(self) -> None:
        playbook = (REPO_ROOT / "docs" / "agent-setup-playbook.md").read_text(
            encoding="utf-8"
        )

        expected_phrases = (
            "python3 scripts/inventory_optional_tools.py",
            "python3 scripts/inventory_optional_tools.py --json",
            "read-only",
            "does not install tools",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, playbook)

    def test_playbook_covers_lumin_evidence_backed_workflow(self) -> None:
        playbook = (REPO_ROOT / "docs" / "agent-setup-playbook.md").read_text(
            encoding="utf-8"
        )

        expected_phrases = (
            "No structural claim without evidence",
            "No absence claim without scan range",
            "pre-write intent",
            "names, shapes, files, dependencies, plannedTypeEscapes",
            "invocation-specific advisory",
            "post-write delta",
            "silent-new",
            "canon draft",
            "living audit",
            "docs/current/audit/lumin-structural-audit.md",
            "Obsidian or private wiki",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, playbook)

    def test_vibe_coding_guide_covers_lumin_structural_claim_contract(self) -> None:
        guide = (REPO_ROOT / "docs" / "vibe-coding-guardrails.md").read_text(
            encoding="utf-8"
        )

        expected_phrases = (
            "Lumin Evidence Lifecycle",
            "quick, full, ci",
            "manifest.json",
            "audit-summary.latest.md",
            "grounded, degraded, unknown",
            "not observed is not does not exist",
            "scan range",
            "false-positive",
            "pre-write-advisory",
            "post-write-delta",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)

    def test_lumin_docs_do_not_overclaim_machine_post_write_outputs(self) -> None:
        checked_paths = (
            REPO_ROOT / "docs" / "agent-setup-playbook.md",
            REPO_ROOT / "docs" / "vibe-coding-guardrails.md",
            REPO_ROOT / "prompts" / "apply-vibe-coding-guardrails.md",
            REPO_ROOT / "prompts" / "start-with-vibe-coding-guardrails.md",
        )

        for path in checked_paths:
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertNotIn("silent-new helpers", content)

        guide = (REPO_ROOT / "docs" / "vibe-coding-guardrails.md").read_text(
            encoding="utf-8"
        )
        lifecycle = guide.split("## Lumin Evidence Lifecycle", maxsplit=1)[1].split(
            "## Local Wiki Or Obsidian Index",
            maxsplit=1,
        )[0]

        self.assertIn(
            "Lumin post-write machine evidence covers `silent-new` type escapes",
            lifecycle,
        )
        self.assertIn(
            "Manual post-write review still covers duplicate helpers",
            lifecycle,
        )
        self.assertNotIn("changed dependencies, and degraded scan confidence", lifecycle)

    def test_lumin_canon_sources_are_limited_to_upstream_sources(self) -> None:
        guide = (REPO_ROOT / "docs" / "vibe-coding-guardrails.md").read_text(
            encoding="utf-8"
        )
        playbook = (REPO_ROOT / "docs" / "agent-setup-playbook.md").read_text(
            encoding="utf-8"
        )

        expected_phrases = (
            "Lumin canon sources are limited to type ownership, helper registry, topology, and naming.",
            "Use living audit or project docs for boundary policy, public API policy, dependency direction, and re-export policy.",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)
            self.assertIn(phrase, playbook)

    def test_local_project_knowledge_template_indexes_structural_evidence(self) -> None:
        template = (REPO_ROOT / "docs" / "local-project-knowledge-template.md").read_text(
            encoding="utf-8"
        )

        expected_phrases = (
            "Structural Evidence Index",
            ".audit/manifest.json",
            ".audit/audit-summary.latest.md",
            ".audit/pre-write-advisory",
            ".audit/post-write-delta",
            "docs/current/audit/lumin-structural-audit.md",
            "Canon or source-of-truth docs",
            "scan range",
            "Last refreshed",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, template)

    def test_vibe_coding_guide_maps_original_problem_checklist_to_repo_artifacts(self) -> None:
        guide = (REPO_ROOT / "docs" / "vibe-coding-guardrails.md").read_text(
            encoding="utf-8"
        )

        expected_phrases = (
            "Applied Checklist Mapping",
            "agent memory is not continuous",
            "hidden coupling",
            "weak tests",
            "edge cases",
            "god functions",
            "circular dependencies",
            "re-export",
            "silent fallback",
            "flat directories",
            "docs/agent-setup-playbook.md",
            "scripts/inventory_optional_tools.py",
            "scripts/check_private_paths.py",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)


if __name__ == "__main__":
    unittest.main()
