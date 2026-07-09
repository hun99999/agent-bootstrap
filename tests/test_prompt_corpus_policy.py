from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP_PROMPT_PATHS = (
    REPO_ROOT / "prompts" / "fresh-install.md",
    REPO_ROOT / "prompts" / "setup-codex-current-harness.md",
)


class PromptCorpusPolicyTests(unittest.TestCase):
    def test_setup_prompts_ask_identity_and_inherit_runtime_model_entitlements(self):
        expected_phrases = (
            "Ask the user what name",
            "Inspect the active Codex and Claude runtimes",
            "models and reasoning levels they actually support",
            "Do not promise or hard-code a particular model",
            "If support cannot be discovered, ask the user rather than guessing",
            "Do not commit the chosen partner name",
        )

        for path in SETUP_PROMPT_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                prompt = path.read_text(encoding="utf-8")

                for phrase in expected_phrases:
                    self.assertIn(phrase, prompt)
                self.assertNotIn("Hun", prompt)
                self.assertNotRegex(prompt, r"\b(?:gpt-\d|claude-(?:opus|sonnet|haiku))")

    def test_root_prompt_scopes_clarification_and_host_capabilities(self):
        root_prompt = (REPO_ROOT / "AGENTS.md").read_text()

        self.assertNotIn(
            "YOU MUST ALWAYS STOP and ask for clarification",
            root_prompt,
        )
        self.assertIn(
            "Ask for clarification only when ambiguity would change scope, safety, architecture, destructive actions, or correctness",
            root_prompt,
        )
        self.assertIn("current host/runtime provides the capability", root_prompt)
        self.assertIn(
            "Use the host's journal or memory mechanism when available",
            root_prompt,
        )
        self.assertNotIn("The last assistant was a sycophant", root_prompt)

    def test_codex_home_prompt_matches_root_prompt(self):
        root_prompt = (REPO_ROOT / "AGENTS.md").read_text()
        codex_home_prompt = (REPO_ROOT / "codex-home" / "AGENTS.md").read_text()

        self.assertEqual(root_prompt, codex_home_prompt)

    def test_codex_home_agents_match_shared_agents(self):
        shared_agents_dir = REPO_ROOT / "agents"
        codex_home_agents_dir = REPO_ROOT / "codex-home" / "agents"

        for shared_agent_path in shared_agents_dir.glob("*.md"):
            with self.subTest(agent=shared_agent_path.name):
                codex_home_agent_path = codex_home_agents_dir / shared_agent_path.name

                self.assertTrue(
                    codex_home_agent_path.exists(),
                    f"Missing codex-home agent: {codex_home_agent_path}",
                )
                self.assertEqual(
                    shared_agent_path.read_text(),
                    codex_home_agent_path.read_text(),
                )

    def test_delegation_roles_are_host_capability_gated(self):
        for agent_name in ("eng-lead.md", "worker.md"):
            with self.subTest(agent=agent_name):
                agent_text = (REPO_ROOT / "agents" / agent_name).read_text()

                self.assertIn("current host/runtime provides", agent_text)

    def test_debugger_can_continue_when_fix_requested(self):
        debugger_text = (REPO_ROOT / "agents" / "debugger.md").read_text()

        self.assertIn(
            "If {{PARTNER_NAME}} asked you to fix the issue",
            debugger_text,
        )
        self.assertIn("continue into TDD implementation", debugger_text)

    def test_root_prompt_contains_structure_guardrails(self):
        root_prompt = (REPO_ROOT / "AGENTS.md").read_text()

        expected_phrases = (
            "Structure and coupling guardrails",
            "Search for existing helpers, types, shapes, and public APIs before creating new ones",
            "Keep error handling at explicit boundaries",
            "Do not silently swallow errors",
            "Mocks belong at external boundaries",
            "Use guard clauses or early returns",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, root_prompt)

    def test_root_prompt_contains_access_and_memory_boundaries(self):
        root_prompt = (REPO_ROOT / "AGENTS.md").read_text()

        expected_phrases = (
            "Access and approval boundary",
            "Broad filesystem or tool access is operational capability, not blanket approval",
            "High-risk actions require an explicit stop and ask",
            "delete data, prune history, rotate credentials, change permissions",
            "production, deployment, billing, external accounts, secrets, auth state, browser profiles",
            "Memory is a recall layer, not a source of truth",
            "repo docs, scripts, tests, AGENTS files, and observed runtime output win",
            "Project-specific operating knowledge belongs in project docs or project skills",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, root_prompt)

    def test_root_prompt_contains_skill_creation_qa_contract(self):
        root_prompt = (REPO_ROOT / "AGENTS.md").read_text()

        expected_phrases = (
            "Skill creation and QA",
            "When creating or editing a skill, treat the skill as tested process code",
            "Start with a failing test or explicit pressure scenario",
            "run the skill validator",
            "check for private paths and secrets",
            "verify any runtime copy separately from the repo catalog source",
            "Do not claim a skill is ready only because the Markdown looks reasonable",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, root_prompt)

    def test_role_agents_include_guardrail_responsibilities(self):
        expectations = {
            "planner.md": (
                "module boundaries",
                "SSOT",
                "dependency direction",
                "edge cases",
            ),
            "worker.md": (
                "search for existing helpers",
                "pre-write lens",
                "TDD",
                "silent fallback",
            ),
            "reviewer.md": (
                "hidden coupling",
                "duplicate replacement",
                "swallowed errors",
                "fan-in",
                "fan-out",
                "internal behavior",
            ),
            "verifier.md": (
                "pristine test output",
                ".audit/",
                "local evidence artifacts",
            ),
        }

        for agent_name, phrases in expectations.items():
            with self.subTest(agent=agent_name):
                agent_text = (REPO_ROOT / "agents" / agent_name).read_text()
                for phrase in phrases:
                    self.assertIn(phrase, agent_text)

    def test_specialist_implementation_agents_include_write_gate_guardrails(self):
        specialist_agents = (
            "backend-engineer.md",
            "data-engineer.md",
            "frontend-engineer.md",
            "integrations-engineer.md",
            "performance-engineer.md",
            "platform-engineer.md",
            "security-engineer.md",
            "skill-author.md",
        )
        expected_phrases = (
            "pre-write lens",
            "search for existing helpers",
            "TDD",
            "silent fallback",
        )

        for agent_name in specialist_agents:
            with self.subTest(agent=agent_name):
                agent_text = (REPO_ROOT / "agents" / agent_name).read_text()
                for phrase in expected_phrases:
                    self.assertIn(phrase, agent_text)


if __name__ == "__main__":
    unittest.main()
