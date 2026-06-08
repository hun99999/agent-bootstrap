# Vibe Coding Guardrails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add public vibe-coding guardrails, local wiki guidance, copy-paste setup prompts, and prompt/agent updates so this repository can apply the workflow to itself and guide Codex or Claude Code through applying it to other repositories.

**Architecture:** Keep the existing shared-core and harness-adapter split. Put long-form operating guidance in `docs/`, short reusable prompts in `prompts/`, concise agent requirements in `AGENTS.md` and `agents/*.md`, and regenerated Claude plugin output under `plugins/process-first-agents/`. Keep personal Obsidian paths out of tracked files.

**Tech Stack:** Python `unittest`, Markdown docs and prompts, existing Python renderer `scripts/render_claude_plugin.py`, Git.

---

## File Structure

- Create: `docs/vibe-coding-guardrails.md`
  - Public long-form guide for applying the pre-write, write, and post-write loop to another repository on macOS or Windows.
- Create: `docs/local-project-knowledge-template.md`
  - Public template Hun can copy into `local.md`, an untracked note, or Obsidian.
- Create: `prompts/apply-vibe-coding-guardrails.md`
  - Copy-paste prompt for asking Codex or Claude Code to install/apply the guardrails to a target repository.
- Create: `prompts/start-with-vibe-coding-guardrails.md`
  - Copy-paste prompt for starting day-to-day work in a target repository with the guardrails active.
- Create: `tests/test_vibe_coding_guardrails.py`
  - Documentation and prompt tests for guide coverage, prompt coverage, and `.audit/` handling.
- Modify: `.gitignore`
  - Ignore `.audit/` local evidence artifacts.
- Modify: `README.md`
  - Link the new guide and prompts from the setup section.
- Modify: `AGENTS.md` and `codex-home/AGENTS.md`
  - Add concise structure and coupling guardrails to the shared constitution.
- Modify: `agents/planner.md`, `agents/worker.md`, `agents/reviewer.md`, `agents/verifier.md`
  - Add role-specific guardrail responsibilities.
- Modify: `codex-home/agents/planner.md`, `codex-home/agents/worker.md`, `codex-home/agents/reviewer.md`, `codex-home/agents/verifier.md`
  - Keep Codex snapshot agents identical to shared agents.
- Modify: `plugins/process-first-agents/agents/*.md`
  - Regenerated Claude plugin output from the shared prompt corpus.
- Modify: `tests/test_prompt_corpus_policy.py`
  - Assert shared prompts contain the new guardrail responsibilities and Codex snapshots match.
- Modify: `tests/test_readme_docs.py`
  - Assert README links the new guide and prompts.

### Task 1: Add Documentation Guardrail Tests

**Files:**
- Create: `tests/test_vibe_coding_guardrails.py`
- Modify: `tests/test_readme_docs.py`
- Modify: `.gitignore`
- Modify: `README.md`
- Create: `docs/vibe-coding-guardrails.md`
- Create: `docs/local-project-knowledge-template.md`
- Create: `prompts/apply-vibe-coding-guardrails.md`
- Create: `prompts/start-with-vibe-coding-guardrails.md`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_vibe_coding_guardrails.py` with tests equivalent to:

```python
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class VibeCodingGuardrailsDocsTests(unittest.TestCase):
    def test_gitignore_ignores_local_audit_artifacts(self) -> None:
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".audit/", gitignore)

    def test_public_guardrail_guide_covers_cross_platform_workflow(self) -> None:
        guide = (REPO_ROOT / "docs" / "vibe-coding-guardrails.md").read_text(
            encoding="utf-8"
        )

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

    def test_local_project_knowledge_template_captures_operational_index(self) -> None:
        template = (
            REPO_ROOT / "docs" / "local-project-knowledge-template.md"
        ).read_text(encoding="utf-8")

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
        self.assertNotIn("C:\\\\Users\\\\", template)

    def test_copy_paste_prompts_cover_apply_and_start_workflows(self) -> None:
        prompt_paths = (
            REPO_ROOT / "prompts" / "apply-vibe-coding-guardrails.md",
            REPO_ROOT / "prompts" / "start-with-vibe-coding-guardrails.md",
        )
        for prompt_path in prompt_paths:
            with self.subTest(prompt=prompt_path.name):
                prompt = prompt_path.read_text(encoding="utf-8")
                self.assertIn("pre-write", prompt.lower())
                self.assertIn("post-write", prompt.lower())
                self.assertIn("TDD", prompt)
                self.assertIn("edge cases", prompt)
                self.assertIn("do not commit", prompt.lower())
```

Update `tests/test_readme_docs.py` with:

```python
    def test_readme_links_vibe_coding_guardrails(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/vibe-coding-guardrails.md", readme)
        self.assertIn("prompts/apply-vibe-coding-guardrails.md", readme)
        self.assertIn("prompts/start-with-vibe-coding-guardrails.md", readme)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest tests.test_vibe_coding_guardrails tests.test_readme_docs -v
```

Expected: `test_vibe_coding_guardrails` fails because the new docs and prompts do not exist, and the README test fails because the new links are not present.

- [ ] **Step 3: Add minimal docs, prompts, `.gitignore`, and README links**

Add `.audit/` to `.gitignore`.

Create `docs/vibe-coding-guardrails.md` with these sections:

```markdown
# Vibe Coding Guardrails

## What This Solves
## Operating Loop
### Pre-write lens
### Write gate
### Post-write review
## macOS Setup
## Windows PowerShell Setup
## Codex Workflow
## Claude Code Workflow
## OpenCode Notes
## Optional Lumin Repo Lens
## Local Wiki Or Obsidian Index
## Applying This To Another Repository
## Starting Daily Work
## Privacy Boundaries
```

Create `docs/local-project-knowledge-template.md` with the headings asserted by the test.

Create `prompts/apply-vibe-coding-guardrails.md` and `prompts/start-with-vibe-coding-guardrails.md` as direct copy-paste prompts.

Add a short "Vibe Coding Guardrails" section to `README.md` linking the guide and both prompts.

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
python3 -m unittest tests.test_vibe_coding_guardrails tests.test_readme_docs -v
```

Expected: all tests in those two modules pass with no warnings or unexpected output.

- [ ] **Step 5: Commit documentation guardrails**

Run:

```bash
git status --short
git add .gitignore README.md docs/vibe-coding-guardrails.md docs/local-project-knowledge-template.md prompts/apply-vibe-coding-guardrails.md prompts/start-with-vibe-coding-guardrails.md tests/test_vibe_coding_guardrails.py tests/test_readme_docs.py
git commit -m "docs: add vibe coding guardrail guide"
```

### Task 2: Add Prompt Corpus Guardrail Tests

**Files:**
- Modify: `tests/test_prompt_corpus_policy.py`
- Modify: `AGENTS.md`
- Modify: `codex-home/AGENTS.md`
- Modify: `agents/planner.md`
- Modify: `agents/worker.md`
- Modify: `agents/reviewer.md`
- Modify: `agents/verifier.md`
- Modify: `codex-home/agents/planner.md`
- Modify: `codex-home/agents/worker.md`
- Modify: `codex-home/agents/reviewer.md`
- Modify: `codex-home/agents/verifier.md`
- Modify: `plugins/process-first-agents/agents/*.md`

- [ ] **Step 1: Write the failing prompt tests**

Append tests to `tests/test_prompt_corpus_policy.py` equivalent to:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest tests.test_prompt_corpus_policy -v
```

Expected: new tests fail because root and role prompts do not yet contain the new guardrail phrases.

- [ ] **Step 3: Update shared prompts and Codex snapshots**

Add a concise `## Structure and coupling guardrails` section to both `AGENTS.md` and `codex-home/AGENTS.md`.

Update the shared and Codex snapshot role files for `planner`, `worker`, `reviewer`, and `verifier` with the responsibilities asserted by the tests.

Keep the wording concise. Put long explanations in docs, not in every agent prompt.

- [ ] **Step 4: Regenerate Claude plugin output**

Run:

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
```

Expected: plugin output is refreshed under `plugins/process-first-agents/`.

- [ ] **Step 5: Run prompt and plugin tests**

Run:

```bash
python3 -m unittest tests.test_prompt_corpus_policy tests.test_claude_plugin tests.test_agent_stack_audit -v
```

Expected: prompt corpus tests pass, generated Claude plugin tests pass, and audit stale-bundle check passes.

- [ ] **Step 6: Commit prompt guardrails**

Run:

```bash
git status --short
git add AGENTS.md codex-home/AGENTS.md agents/planner.md agents/worker.md agents/reviewer.md agents/verifier.md codex-home/agents/planner.md codex-home/agents/worker.md codex-home/agents/reviewer.md codex-home/agents/verifier.md plugins/process-first-agents/agents tests/test_prompt_corpus_policy.py
git commit -m "feat: add structure guardrails to agent prompts"
```

### Task 3: Final Verification

**Files:**
- No new files.
- Verify all files changed by Tasks 1 and 2.

- [ ] **Step 1: Run the full test suite**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Expected: all tests pass with pristine output.

- [ ] **Step 2: Run the local audit**

Run:

```bash
python3 scripts/audit_agent_stack.py
```

Expected: command exits 0, prints `Agent stack audit:`, and reports no required check in a failing status.

- [ ] **Step 3: Inspect git status and final diff**

Run:

```bash
git status --short
git log --oneline -3
```

Expected: working tree is clean after the task commits, and recent commits include the design, docs, and prompt guardrail commits.

## Self-Review

- Spec coverage: The plan covers public docs, prompts, local overlay guidance, `.audit/`, shared agent updates, generated Claude output, and tests.
- Placeholder scan: The plan has no placeholder sections; all paths, commands, and expected outcomes are concrete.
- Type consistency: The only code changes are Python `unittest` assertions and existing Markdown/Python renderer flows; no new runtime types are introduced.
