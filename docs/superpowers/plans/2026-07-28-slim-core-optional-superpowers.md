# Slim Core And Optional Superpowers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a compact shared prompt corpus, make Superpowers an explicit optional install, add only Matt Pocock's explicit-use `handoff` skill, and safely apply the reviewed result to Hun's local Codex runtime.

**Architecture:** Keep the repository's existing source/snapshot/generated boundaries. Encode prompt size and risk-proportionate verification as semantic tests, reuse the existing `manual|skip` installer interface with `skip` as the default, teach the audit to distinguish disabled/inactive/active/broken optional states, and keep runtime mutation limited to reviewed prompt/skill copies plus one exact discovery symlink.

**Tech Stack:** Markdown, Python 3.9+ standard library, `unittest`, Git, Codex skill discovery, Claude plugin rendering.

---

## File Structure

- Create: `docs/superpowers/specs/2026-07-28-slim-core-optional-superpowers-design.md`
- Create: `docs/superpowers/plans/2026-07-28-slim-core-optional-superpowers.md`
- Create: `skills/handoff/SKILL.md`
- Create: `skills/handoff/agents/openai.yaml`
- Create: `skills/handoff/SOURCE.md`
- Create: `skills/handoff/LICENSE`
- Modify: `AGENTS.md`
- Modify: `codex-home/AGENTS.md`
- Modify: `agents/*.md`
- Modify: `codex-home/agents/*.md`
- Regenerate: `plugins/process-first-agents/agents/*.md`
- Modify: `.codex/install.py`
- Modify: `scripts/audit_agent_stack.py`
- Modify: `tests/test_prompt_corpus_policy.py`
- Modify: `tests/test_install.py`
- Modify: `tests/test_agent_stack_audit.py`
- Modify: `tests/test_skill_catalog.py`
- Modify: `tests/test_readme_docs.py`
- Modify: `skills/README.md`
- Modify: `docs/codex-skills.md`
- Modify: `.codex/INSTALL.md`
- Modify: `docs/README.codex.md`
- Modify: `docs/README.claude.md`
- Modify: `prompts/fresh-install.md`
- Modify: `prompts/setup-codex-current-harness.md`
- Modify: `prompts/setup-claude-current-harness.md`
- Modify: `prompts/setup-codex-skills.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `README.ja.md`
- Modify: `README.zh-CN.md`

### Task 1: Lock The Compact Shared-Core Contract

**Files:**
- Modify: `tests/test_prompt_corpus_policy.py`
- Modify: `AGENTS.md`
- Modify: `codex-home/AGENTS.md`

- [ ] **Step 1: Add the failing compact-core test**

Require:

```python
self.assertLessEqual(len(root_prompt.encode("utf-8")), 6_656)
self.assertLessEqual(len(root_prompt.split()), 850)
self.assertEqual(root_prompt, codex_snapshot)
self.assertEqual(root_prompt.rstrip().splitlines()[-1], "@local.md")
```

Assert the seven compact section headings and semantic anchors for current evidence, compaction
recovery, approval boundaries, unrelated-work preservation, smallest changes, explicit boundaries,
root-cause diagnosis, invalidated evidence, full-regression criteria, Git protection, and selective
skill/delegation use.

Forbid legacy mandates including `Rule #1`, `FOR EVERY NEW FEATURE OR BUGFIX`, `ALL TEST FAILURES`,
`Always complete ALL steps`, `Fix broken things immediately`, and direct Superpowers skill names.

- [ ] **Step 2: Run the focused test and observe RED**

Run:

```bash
python3 -m unittest tests.test_prompt_corpus_policy -v
```

Expected: failures report the current prompt budget and legacy mandates.

- [ ] **Step 3: Replace the shared core with the approved seven-section prompt**

Write the compact prompt to `AGENTS.md`, keep `{{PARTNER_NAME}}`, and keep `@local.md` as the final
nonblank line. Copy the same bytes to `codex-home/AGENTS.md`.

- [ ] **Step 4: Run the focused test and observe GREEN**

Run the same command. Expected: all prompt-corpus tests pass after role tests are rebaselined in the
next task; the compact-core test itself is green.

### Task 2: Slim Role Prompts And Verification Policy

**Files:**
- Modify: `tests/test_prompt_corpus_policy.py`
- Modify: `agents/*.md`
- Modify: `codex-home/agents/*.md`
- Regenerate: `plugins/process-first-agents/agents/*.md`

- [ ] **Step 1: Add failing role-policy tests**

Assert every role source:

```python
self.assertNotRegex(text, r"(?i)superpowers|test-driven-development|verification-before-completion")
```

Require the verifier to contain `invalidated`, the broad-regression criteria
`broad`, `cross-cutting`, `high-risk`, and `release`, plus a prohibition on claiming unrun checks.
Require each role source to remain below a role-appropriate word budget.

- [ ] **Step 2: Run the focused role tests and observe RED**

Run:

```bash
python3 -m unittest tests.test_prompt_corpus_policy tests.test_claude_plugin -v
```

Expected: existing direct Superpowers references and generated drift fail.

- [ ] **Step 3: Rewrite each canonical role source**

Keep only role-specific responsibilities. Give implementation roles bounded-change and focused-check
language. Give debugger root-cause language, reviewer evidence-backed finding language, verifier the
invalidated-evidence policy, and release-manager separate branch/CI/deployment verdicts.

Copy each canonical `agents/*.md` file byte-for-byte to `codex-home/agents/*.md`.

- [ ] **Step 4: Regenerate the Claude bundle**

Run:

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
```

Expected: deterministic generated agents contain the compact rendered shared core and slim role body.

- [ ] **Step 5: Run the focused prompt and renderer tests**

Run the same focused command. Expected: green with no generated drift.

### Task 3: Make Manual Superpowers Explicit

**Files:**
- Modify: `tests/test_install.py`
- Modify: `.codex/install.py`

- [ ] **Step 1: Add a failing default-skip test**

Invoke the installer without `--superpowers-mode` and assert:

```python
self.assertIn("Superpowers mode: skip", result.stdout)
self.assertFalse((codex_home / "superpowers").exists())
self.assertFalse((agents_home / "skills" / "superpowers").exists())
```

Update existing manual-install safety tests to pass `--superpowers-mode manual` explicitly.

- [ ] **Step 2: Run installer tests and observe RED**

Run:

```bash
python3 -m unittest tests.test_install -v
```

Expected: the default invocation still selects `manual`.

- [ ] **Step 3: Change only the existing default and help text**

Set the parser default to `skip`. Keep choices, preflight safety, remote-default-branch tracking,
fast-forward checks, symlink refusal, and manual output intact.

- [ ] **Step 4: Run installer tests and observe GREEN**

Run the same command. Expected: default-skip and explicit-manual cases pass.

### Task 4: Model Optional Superpowers Audit States

**Files:**
- Modify: `tests/test_agent_stack_audit.py`
- Modify: `scripts/audit_agent_stack.py`

- [ ] **Step 1: Add failing state-table tests**

Cover:

```text
absent checkout + absent link -> optional disabled, success
valid checkout + absent link -> optional inactive, success
valid checkout + correct link -> optional active, success
dangling/wrong link -> failure
invalid or dirty active checkout -> failure
```

Assert an inactive checkout does not invoke online freshness logic.

- [ ] **Step 2: Run audit tests and observe RED**

Run:

```bash
python3 -m unittest tests.test_agent_stack_audit -v
```

Expected: missing/inactive states currently fail as required Superpowers.

- [ ] **Step 3: Implement the smallest state classifier**

Return an optional status for healthy disabled, inactive, and active states. Keep malformed or active
unsafe states as errors. Run remote freshness only for an active manual installation when online
checking is requested.

- [ ] **Step 4: Run audit tests and observe GREEN**

Run the same command. Expected: all state-table cases pass.

### Task 5: Vendor And Validate The Explicit Handoff Skill

**Files:**
- Modify: `tests/test_skill_catalog.py`
- Create: `skills/handoff/SKILL.md`
- Create: `skills/handoff/agents/openai.yaml`
- Create: `skills/handoff/SOURCE.md`
- Create: `skills/handoff/LICENSE`
- Modify: `skills/README.md`
- Modify: `docs/codex-skills.md`
- Modify: `prompts/setup-codex-skills.md`

- [ ] **Step 1: Add failing package-policy tests**

Require the exact reviewed source files, immutable commit, MIT attribution, small word budget, and:

```python
self.assertIn("disable-model-invocation: true", skill)
self.assertIn("allow_implicit_invocation: false", agent)
self.assertNotRegex(skill, r"(?i)background agent|git commit|run tests|browser")
```

Require the catalog to recommend only `handoff` from Matt Pocock's repository and document
`~/.codex/skills/handoff`.

- [ ] **Step 2: Run catalog tests and observe RED**

Run:

```bash
python3 -m unittest tests.test_skill_catalog -v
```

Expected: the reviewed package and catalog entry are absent.

- [ ] **Step 3: Add the byte-reviewed package and attribution**

Copy the two upstream files exactly from commit
`2ab958093e83e0ec752e6c1c5932da465bf23e0c`. Add source and MIT files without changing the skill
trigger or behavior.

- [ ] **Step 4: Document explicit installation and selection**

Add the package to the public catalog, explain why other Matt Pocock workflow skills are not global
defaults, and keep installation an explicit user choice.

- [ ] **Step 5: Run catalog and private-path tests**

Run:

```bash
python3 -m unittest tests.test_skill_catalog tests.test_private_path_scan -v
```

Expected: green with no private path or secret.

### Task 6: Align Setup And User Documentation

**Files:**
- Modify: `tests/test_readme_docs.py`
- Modify: `.codex/INSTALL.md`
- Modify: `docs/README.codex.md`
- Modify: `docs/README.claude.md`
- Modify: `prompts/fresh-install.md`
- Modify: `prompts/setup-codex-current-harness.md`
- Modify: `prompts/setup-claude-current-harness.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `README.ja.md`
- Modify: `README.zh-CN.md`

- [ ] **Step 1: Add failing optional-install documentation tests**

Require every applicable setup surface to say that Superpowers is optional, Codex defaults to skip,
manual mode is explicit, model choice is independent, and skip does not deactivate an existing link.
Retain the duplicate-discovery warning.

- [ ] **Step 2: Run documentation tests and observe RED**

Run:

```bash
python3 -m unittest tests.test_readme_docs -v
```

Expected: current Superpowers-centered and forced-install wording fails.

- [ ] **Step 3: Update the English canonical documentation**

Describe the compact shared core, explicit `handoff`, default skip, explicit manual opt-in, separate
Claude choice, and local deactivation boundary.

- [ ] **Step 4: Update Korean, Japanese, and Simplified Chinese counterparts**

Preserve each document's existing headings and commands while translating the same optional behavior.

- [ ] **Step 5: Run documentation tests and observe GREEN**

Run the same command. Expected: green.

### Task 7: Apply The Reviewed Runtime State Safely

**Files outside repository:**
- Install: `~/.codex/skills/handoff/`
- Update only managed prompt files: `~/.codex/AGENTS.md`, `~/.codex/agents/*.md`
- Remove exact symlink: `~/.agents/skills/superpowers`
- Preserve: `~/.codex/config.toml`, `~/.codex/superpowers`, Claude plugin state

- [ ] **Step 1: Render into temporary homes**

Run the installer against temporary Codex and agents homes with the default skip mode. Do not point
the installer at the live Codex home.

- [ ] **Step 2: Compare rendered managed files**

Verify the temporary `AGENTS.md` and role prompts contain the configured partner name, no placeholder,
and no direct Superpowers dependency.

- [ ] **Step 3: Copy only reviewed managed prompt and handoff files**

Copy the rendered prompt files and reviewed handoff package to their exact live targets. Do not copy
the template `config.toml`.

- [ ] **Step 4: Resolve and remove only the approved symlink**

Prove `~/.agents/skills/superpowers` is a symlink to
`~/.codex/superpowers/skills`, then unlink that exact symlink. Do not delete the checkout.

- [ ] **Step 5: Verify live state**

Verify prompt/runtime copies, handoff metadata, absent Codex Superpowers discovery link, preserved
clean checkout, no installed Codex Superpowers plugin, and unchanged enabled Claude Superpowers
plugin. Note that fresh-task discovery is required because this task retains its initial snapshot.

### Task 8: Final Broad Verification And Diff Review

**Files:**
- Review all changed and generated files.

- [ ] **Step 1: Run the full regression exactly once at the final stable state**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Expected: all tests pass with no failures or errors.

- [ ] **Step 2: Run non-duplicative repository checks**

Run:

```bash
python3 scripts/audit_agent_stack.py --repo-only
python3 scripts/check_private_paths.py
git diff --check
```

Expected: generated bundle is synchronized, no private path or secret is found, and the diff has no
whitespace error.

- [ ] **Step 3: Review scope and evidence**

Inspect `git status`, `git diff --stat`, and the complete diff. Confirm historical plans/specs were not
rewritten, live config was not overwritten, only the approved runtime link was removed, and every
completion claim maps to fresh evidence.

