from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class PromptCorpusPolicyTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
