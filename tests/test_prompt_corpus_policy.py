from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT_PROMPT_PATH = REPO_ROOT / "AGENTS.md"
CANONICAL_ROLE_DIR = REPO_ROOT / "agents"
SETUP_PROMPT_PATHS = (
    REPO_ROOT / "prompts" / "fresh-install.md",
    REPO_ROOT / "prompts" / "setup-codex-current-harness.md",
)
ROOT_PROMPT_MAX_WORDS = 850
ROOT_PROMPT_MAX_BYTES = 6656
DEFAULT_ROLE_MAX_WORDS = 200
ROLE_MAX_WORDS = {
    "eng-lead.md": 300,
}
LEGACY_ABSOLUTE_MANDATES = (
    "Rule #1:",
    "Violating the letter of the rules is violating the spirit",
    "NEVER skip steps or take shortcuts",
    "FOR EVERY NEW FEATURE OR BUGFIX",
    "ALL TEST FAILURES ARE YOUR RESPONSIBILITY",
    "Tests MUST comprehensively cover ALL functionality",
    'The "trivial task" exception does NOT apply',
    "Always complete ALL steps including reviews even for small changes",
    "YOU MUST ALWAYS find the root cause",
    "Test output MUST BE PRISTINE TO PASS",
)
DIRECT_PROCESS_REFERENCE_PATTERNS = (
    r"\bsuperpowers?\b",
    r"\btdd\b",
    r"\btest-driven-development\b",
    r"\bsystematic-debugging\b",
    r"\bverification-before-completion\b",
    r"\brequesting-code-review\b",
    r"\breceiving-code-review\b",
    r"\bfinishing-a-development-branch\b",
    r"\bwriting-skills\b",
    r"\busing-git-worktrees\b",
    r"\buse brainstorming\b",
    r"\buse writing-plans\b",
)


def normalize_semantic_text(text: str) -> str:
    return " ".join(re.sub(r"[-–—]", " ", text.lower()).split())


def full_regression_policy_lines(text: str) -> list[str]:
    return [
        normalize_semantic_text(line)
        for line in text.splitlines()
        if "full regression" in normalize_semantic_text(line)
    ]


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

    def test_root_prompt_stays_within_compact_size_budget(self):
        root_prompt = ROOT_PROMPT_PATH.read_text(encoding="utf-8")

        self.assertLessEqual(
            len(root_prompt.split()),
            ROOT_PROMPT_MAX_WORDS,
            "shared AGENTS policy exceeded the word budget",
        )
        self.assertLessEqual(
            len(root_prompt.encode("utf-8")),
            ROOT_PROMPT_MAX_BYTES,
            "shared AGENTS policy exceeded the byte budget",
        )

    def test_root_prompt_keeps_local_include_final(self):
        root_prompt = ROOT_PROMPT_PATH.read_text(encoding="utf-8")
        nonempty_lines = [line.strip() for line in root_prompt.splitlines() if line.strip()]

        self.assertEqual(
            nonempty_lines[-1],
            "@local.md",
            "@local.md must remain the final nonblank line",
        )
        self.assertEqual(nonempty_lines.count("@local.md"), 1)

    def test_root_prompt_uses_compact_semantic_sections(self):
        root_prompt = ROOT_PROMPT_PATH.read_text(encoding="utf-8")
        headings = [
            normalize_semantic_text(line.lstrip("#").strip())
            for line in root_prompt.splitlines()
            if line.startswith("#")
        ]
        expected_heading_terms = {
            "core contract": ("core",),
            "source of truth and memory": ("source of truth", "memory"),
            "scope and approval": ("scope", "approval"),
            "implementation discipline": ("implementation",),
            "testing, debugging, and completion": ("testing", "completion"),
            "git and worktree safety": ("git", "worktree"),
            "skills, delegation, and local extension": ("skills", "delegation"),
        }
        missing_sections = [
            section
            for section, terms in expected_heading_terms.items()
            if not any(all(term in heading for term in terms) for heading in headings)
        ]

        self.assertEqual(missing_sections, [])

    def test_root_prompt_preserves_compact_semantic_contract(self):
        root_prompt = ROOT_PROMPT_PATH.read_text(encoding="utf-8")
        normalized = normalize_semantic_text(root_prompt)
        expected_anchors = (
            "clarification",
            "host/runtime",
            "journal or memory",
            "context compaction",
            "source of truth",
            "high risk",
            "explicit approval",
            "preserve unrelated work",
            "smallest reasonable change",
            "explicit boundaries",
            "swallow errors",
            "root cause",
            "invalidated evidence",
            "skill validator",
            "private paths",
            "runtime copy",
        )
        missing_anchors = [
            anchor for anchor in expected_anchors if anchor not in normalized
        ]

        self.assertEqual(missing_anchors, [])
        self.assertNotIn("you must always stop and ask for clarification", normalized)
        self.assertNotIn("The last assistant was a sycophant", root_prompt)

    def test_root_prompt_never_claims_unrun_checks(self):
        root_prompt = ROOT_PROMPT_PATH.read_text(encoding="utf-8")
        normalized = normalize_semantic_text(root_prompt)
        self.assertRegex(
            normalized,
            (
                r"(?:never|do not) claim[^.]{0,160}"
                r"(?:(?:unrun|not run|did not run)[^.]{0,80}checks?"
                r"|checks?[^.]{0,80}(?:unrun|not run|did not run|ran when they did not))"
            ),
        )

    def test_codex_home_prompt_matches_root_prompt(self):
        root_prompt = ROOT_PROMPT_PATH.read_text()
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
        self.assertIn("cause is proven", debugger_text)
        self.assertIn("continue into implementation", debugger_text)

    def test_root_prompt_limits_full_regression_to_wider_risk(self):
        root_prompt = ROOT_PROMPT_PATH.read_text(encoding="utf-8")
        policy_lines = full_regression_policy_lines(root_prompt)

        self.assertNotEqual(policy_lines, [], "missing full-regression scope policy")
        policy = " ".join(policy_lines)
        expected_criteria = (
            "only",
            "broad",
            "cross cutting",
            "high risk",
            "release",
            "wider impact",
        )
        missing_criteria = [
            criterion for criterion in expected_criteria if criterion not in policy
        ]

        self.assertEqual(missing_criteria, [])

    def test_root_prompt_omits_legacy_absolute_mandates(self):
        root_prompt = ROOT_PROMPT_PATH.read_text(encoding="utf-8")
        legacy_hits = [
            mandate for mandate in LEGACY_ABSOLUTE_MANDATES if mandate in root_prompt
        ]

        self.assertEqual(legacy_hits, [])

    def test_root_prompt_omits_direct_process_skill_names(self):
        root_prompt = ROOT_PROMPT_PATH.read_text(encoding="utf-8")
        lowered = root_prompt.lower()
        direct_reference_hits = [
            pattern
            for pattern in DIRECT_PROCESS_REFERENCE_PATTERNS
            if re.search(pattern, lowered)
        ]
        self.assertEqual(direct_reference_hits, [])

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
                "failure paths",
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
            "edge cases",
            "side effects",
            "silent fallback",
        )

        for agent_name in specialist_agents:
            with self.subTest(agent=agent_name):
                agent_text = (REPO_ROOT / "agents" / agent_name).read_text()
                for phrase in expected_phrases:
                    self.assertIn(phrase, agent_text)

    def test_canonical_role_prompts_omit_direct_process_skill_names(self):
        violations = {}
        for agent_path in sorted(CANONICAL_ROLE_DIR.glob("*.md")):
            agent_text = agent_path.read_text(encoding="utf-8").lower()
            hits = [
                pattern
                for pattern in DIRECT_PROCESS_REFERENCE_PATTERNS
                if re.search(pattern, agent_text)
            ]
            if hits:
                violations[agent_path.name] = hits

        self.assertEqual(violations, {})

    def test_canonical_role_prompts_stay_within_pragmatic_word_budgets(self):
        violations = {}
        for agent_path in sorted(CANONICAL_ROLE_DIR.glob("*.md")):
            agent_text = agent_path.read_text(encoding="utf-8")
            word_limit = ROLE_MAX_WORDS.get(agent_path.name, DEFAULT_ROLE_MAX_WORDS)
            word_count = len(agent_text.split())
            if word_count > word_limit:
                violations[agent_path.name] = {
                    "actual": word_count,
                    "limit": word_limit,
                }

        self.assertEqual(violations, {})

    def test_verifier_tracks_invalidated_evidence(self):
        verifier_text = (CANONICAL_ROLE_DIR / "verifier.md").read_text(encoding="utf-8")
        normalized = normalize_semantic_text(verifier_text)
        expected_anchors = (
            "pristine test output",
            ".audit/",
            "local evidence artifacts",
            "invalidated evidence",
        )
        missing_anchors = [
            anchor for anchor in expected_anchors if anchor not in normalized
        ]

        self.assertEqual(missing_anchors, [])

    def test_verifier_scopes_full_regression(self):
        verifier_text = (CANONICAL_ROLE_DIR / "verifier.md").read_text(encoding="utf-8")
        policy_lines = full_regression_policy_lines(verifier_text)
        self.assertNotEqual(policy_lines, [], "verifier is missing full-regression criteria")
        policy = " ".join(policy_lines)
        expected_criteria = (
            "only",
            "broad",
            "cross cutting",
            "high risk",
            "release",
            "wider impact",
        )
        missing_criteria = [
            criterion for criterion in expected_criteria if criterion not in policy
        ]

        self.assertEqual(missing_criteria, [])


if __name__ == "__main__":
    unittest.main()
