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
LOCAL_PROMPT_PATHS = (
    REPO_ROOT / ".codex" / "templates" / "local.md",
    REPO_ROOT / "codex-home" / "local.md",
)
ROOT_PROMPT_MAX_WORDS = 550
ROOT_PROMPT_MAX_BYTES = 5120
DEFAULT_ROLE_MAX_WORDS = 200
LEGACY_ABSOLUTE_MANDATES = (
    "Rule #1:",
    "NEVER skip steps or take shortcuts",
    "FOR EVERY NEW FEATURE OR BUGFIX",
    "ALL TEST FAILURES ARE YOUR RESPONSIBILITY",
    "Tests MUST comprehensively cover ALL functionality",
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
)


def normalize_semantic_text(text: str) -> str:
    return " ".join(re.sub(r"[-–—]", " ", text.lower()).split())


def full_regression_policy_lines(text: str) -> list[str]:
    normalized = normalize_semantic_text(text)
    start = normalized.find("full regression")
    if start < 0:
        return []
    end = normalized.find(".", start)
    return [normalized[start:] if end < 0 else normalized[start:end]]


class PromptCorpusPolicyTests(unittest.TestCase):
    def test_setup_prompts_ask_identity_and_inherit_runtime_model_entitlements(self):
        expected_phrases = (
            "Ask the user what name",
            "Inspect the active Codex runtime",
            "model and reasoning settings it actually supports",
            "preserve existing machine-local selections",
            "leave model and reasoning unset",
            "Do not commit the chosen partner name",
        )
        for path in SETUP_PROMPT_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                prompt = path.read_text(encoding="utf-8")
                normalized_prompt = prompt.lower()
                for phrase in expected_phrases:
                    self.assertIn(phrase.lower(), normalized_prompt)
                self.assertNotIn("Hun", prompt)
                self.assertNotIn("Inspect the active Codex and Claude runtimes", prompt)
                self.assertNotRegex(prompt, r"\b(?:gpt-\d|claude-(?:opus|sonnet|haiku))")

    def test_root_prompt_stays_within_compact_size_budget(self):
        root_prompt = ROOT_PROMPT_PATH.read_text(encoding="utf-8")
        self.assertLessEqual(len(root_prompt.split()), ROOT_PROMPT_MAX_WORDS)
        self.assertLessEqual(len(root_prompt.encode("utf-8")), ROOT_PROMPT_MAX_BYTES)

    def test_root_prompt_keeps_local_include_final(self):
        root_prompt = ROOT_PROMPT_PATH.read_text(encoding="utf-8")
        nonempty = [line.strip() for line in root_prompt.splitlines() if line.strip()]
        self.assertEqual(nonempty[-1], "@local.md")
        self.assertEqual(nonempty.count("@local.md"), 1)

    def test_root_prompt_uses_result_oriented_sections(self):
        headings = [
            normalize_semantic_text(line.lstrip("#").strip())
            for line in ROOT_PROMPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.startswith("#")
        ]
        expected = (
            ("outcome",),
            ("source of truth",),
            ("authority", "preservation"),
            ("execution",),
            ("evidence", "completion"),
            ("git", "worktree"),
            ("skills", "delegation"),
        )
        self.assertEqual(
            [terms for terms in expected if not any(all(term in heading for term in terms) for heading in headings)],
            [],
        )

    def test_root_prompt_preserves_lean_outcome_contract(self):
        normalized = normalize_semantic_text(ROOT_PROMPT_PATH.read_text(encoding="utf-8"))
        expected = (
            "smallest concrete outcome",
            "host/runtime",
            "memory or journals",
            "after compaction",
            "authoritative",
            "explicit approval",
            "preserve unrelated work",
            "lowest cost direct proof",
            "fresh, minimal context",
            "performance skills",
            "bounded outcome",
            "stop condition",
            "completion claims cover only evidence actually obtained",
        )
        self.assertEqual([anchor for anchor in expected if anchor not in normalized], [])

    def test_local_prompt_snapshot_is_equal_and_budgeted(self):
        texts = [path.read_text(encoding="utf-8") for path in LOCAL_PROMPT_PATHS]
        self.assertEqual(texts[0], texts[1])
        self.assertLessEqual(len(texts[0].split()), 120)
        self.assertLessEqual(len(texts[0].encode("utf-8")), 1024)

    def test_codex_home_prompt_and_roles_match_canonical_sources(self):
        self.assertEqual(
            ROOT_PROMPT_PATH.read_bytes(),
            (REPO_ROOT / "codex-home" / "AGENTS.md").read_bytes(),
        )
        for source in CANONICAL_ROLE_DIR.glob("*.md"):
            with self.subTest(agent=source.name):
                self.assertEqual(
                    source.read_bytes(),
                    (REPO_ROOT / "codex-home" / "agents" / source.name).read_bytes(),
                )

    def test_lead_delegation_has_minimal_context_ownership_and_stop_contract(self):
        text = (CANONICAL_ROLE_DIR / "eng-lead.md").read_text(encoding="utf-8")
        expected = (
            "current host/runtime provides",
            "minimal self-contained source map",
            "fresh context",
            "one owner",
            "Stop or cancel work",
            "at most one assurance sidecar",
            "source-grounded worker evidence",
        )
        for phrase in expected:
            self.assertIn(phrase, text)

    def test_worker_returns_bounded_work_without_nested_delegation(self):
        text = (CANONICAL_ROLE_DIR / "worker.md").read_text(encoding="utf-8")
        self.assertIn("one bounded routine implementation outcome", text)
        self.assertIn("further delegation remain with the lead", text)
        self.assertNotIn("Delegate independent work", text)

    def test_debugger_can_continue_when_fix_requested(self):
        text = (CANONICAL_ROLE_DIR / "debugger.md").read_text(encoding="utf-8")
        self.assertIn("If {{PARTNER_NAME}} requested a fix", text)
        self.assertIn("smallest fix", text)
        self.assertIn("supported by the evidence", text)

    def test_root_and_verifier_scope_full_regression_to_wider_risk(self):
        for path in (ROOT_PROMPT_PATH, CANONICAL_ROLE_DIR / "verifier.md"):
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                policy = " ".join(full_regression_policy_lines(path.read_text(encoding="utf-8")))
                for criterion in ("only", "broad", "cross cutting", "high risk", "release", "wider impact"):
                    self.assertIn(criterion, policy)

    def test_prompts_omit_legacy_mandates_process_skill_names_and_reread_loops(self):
        paths = [ROOT_PROMPT_PATH, *sorted(CANONICAL_ROLE_DIR.glob("*.md"))]
        texts = [path.read_text(encoding="utf-8") for path in paths]
        for mandate in LEGACY_ABSOLUTE_MANDATES:
            self.assertFalse(any(mandate in text for text in texts), mandate)
        for pattern in DIRECT_PROCESS_REFERENCE_PATTERNS:
            self.assertFalse(any(re.search(pattern, text.casefold()) for text in texts), pattern)
        for phrase in ("reread", "read again", "review thoroughly", "check thoroughly"):
            self.assertFalse(any(phrase in text.casefold() for text in texts), phrase)

    def test_specialists_search_only_unresolved_parent_brief_boundaries(self):
        specialists = (
            "backend-engineer.md",
            "data-engineer.md",
            "frontend-engineer.md",
            "integrations-engineer.md",
            "performance-engineer.md",
            "platform-engineer.md",
            "security-engineer.md",
        )
        for name in specialists:
            with self.subTest(agent=name):
                text = (CANONICAL_ROLE_DIR / name).read_text(encoding="utf-8")
                for phrase in (
                    "parent brief's current source map",
                    "Search only unresolved",
                    "side effects",
                    "silent fallback",
                ):
                    self.assertIn(phrase, text)
                self.assertRegex(text, r"edge (?:cases|states)")

    def test_reviewer_retains_concrete_risk_contract(self):
        text = (CANONICAL_ROLE_DIR / "reviewer.md").read_text(encoding="utf-8")
        for phrase in (
            "hidden coupling",
            "duplicate replacement",
            "swallowed errors",
            "fan-in",
            "fan-out",
            "internal behavior",
        ):
            self.assertIn(phrase, text)

    def test_skill_author_classifies_and_benchmarks_performance_skills(self):
        text = (CANONICAL_ROLE_DIR / "skill-author.md").read_text(encoding="utf-8")
        for phrase in (
            "workflow skill",
            "performance skill",
            "before/after benchmarks",
            "frequently loaded content",
        ):
            self.assertIn(phrase, text)

    def test_verifier_uses_direct_invalidated_evidence_and_stops(self):
        normalized = normalize_semantic_text(
            (CANONICAL_ROLE_DIR / "verifier.md").read_text(encoding="utf-8")
        )
        for phrase in (
            "lowest cost check",
            "run only missing or invalidated checks",
            "exact remaining gap",
            "stop once the claim is proved",
        ):
            self.assertIn(phrase, normalized)

    def test_canonical_role_prompts_stay_within_pragmatic_word_budgets(self):
        violations = {}
        for path in sorted(CANONICAL_ROLE_DIR.glob("*.md")):
            words = len(path.read_text(encoding="utf-8").split())
            if words > DEFAULT_ROLE_MAX_WORDS:
                violations[path.name] = words
        self.assertEqual(violations, {})


if __name__ == "__main__":
    unittest.main()
