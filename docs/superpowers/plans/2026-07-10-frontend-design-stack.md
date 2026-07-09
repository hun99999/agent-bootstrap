# Frontend Design Stack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a public-shareable, provenance-safe `frontend-design-pack` for Codex and Claude Code, inherit each user's available model ceiling, and install and validate the same tracked plugin in Hun's local Codex runtime.

**Architecture:** Keep one native `frontend-design` router and a self-contained reference corpus rather than exposing every upstream procedure as a native skill. Treat `design-stack/` as the reviewed source of truth, render `plugins/frontend-design-pack/` deterministically, keep source checks read-only, require explicit local tar archives for approved updates, and validate the tracked plugin separately from each installed runtime copy.

**Tech Stack:** Python 3.9+ standard library, `unittest`, JSON, Markdown, TOML-like Codex configuration, Git, Codex CLI, Claude Code CLI, GitHub source archives, SHA-256 inventories.

---

## File Structure

- Create: `design-stack/sources.json`
- Create: `design-stack/sources.lock.json`
- Create: `design-stack/provenance.json`
- Create: `design-stack/routing.json`
- Create: `design-stack/templates/DESIGN.md.template`
- Create: `design-stack/templates/product-brief.md`
- Create: `design-stack/templates/design-decision.md`
- Create: `design-stack/evals/routing-cases.json`
- Create: `design-stack/evals/trigger-cases.json`
- Create: `design-stack/router/SKILL.md`
- Create: `design-stack/router/references/source-precedence.md`
- Create: `design-stack/router/references/quality-gates.md`
- Create: `design-stack/vendor/` reviewed upstream files and required notices
- Create: `scripts/design_stack.py`
- Create: `scripts/check_design_sources.py`
- Create: `scripts/sync_design_sources.py`
- Create: `scripts/render_frontend_design_plugin.py`
- Create: `scripts/validate_frontend_design_stack.py`
- Create: `plugins/frontend-design-pack/` deterministic rendered output
- Create: `tests/frontend_design_test_support.py`
- Create: `tests/test_frontend_design_registry.py`
- Create: `tests/test_frontend_design_source_check.py`
- Create: `tests/test_frontend_design_sync.py`
- Create: `tests/test_frontend_design_plugin.py`
- Create: `tests/test_frontend_design_router.py`
- Create: `tests/test_frontend_design_docs.py`
- Modify: `tests/test_codex_config.py`
- Modify: `tests/test_claude_plugin.py`
- Modify: `tests/test_skill_catalog.py`
- Modify: `tests/test_private_path_scan.py`
- Modify: `tests/test_ci_workflow.py`
- Modify: `.codex/templates/config.toml`
- Modify: `.codex/templates/agents/*.toml`
- Modify: `codex-home/config.toml`
- Modify: `codex-home/agents/*.toml`
- Modify: `prompts/fresh-install.md`
- Modify: `prompts/setup-codex-current-harness.md`
- Create: `docs/frontend-design-stack.md`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `scripts/render_claude_plugin.py`
- Modify: `scripts/check_private_paths.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `README.ja.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/README.codex.md`
- Modify: `.codex/INSTALL.md`

## Locked Upstream Inputs

| Source ID | Immutable input | Local policy |
| --- | --- | --- |
| `mengto-skills` | `MengTo/Skills@25f872a94e3bbee85ecacba4041fa52c21cb0e44` | Derive all 95 skill decisions from the tree; include vetted material and map known official duplicates. |
| `google-design-md` | `google-labs-code/design.md`, CLI `0.3.0`, reviewed commit `ea4a3240d4c0d06778b9e39efeb553851be27c17` | Pin validator contract and project-owned DESIGN.md workflow. |
| `awesome-design-md` | `VoltAgent/awesome-design-md@664b3e78fd1a298ba11973822da988483256d4b4` | Index all 74 references as third-party analysis. |
| `vercel-agent-skills` | `vercel-labs/agent-skills@f8a72b9603728bb92a217a879b7e62e43ad76c81` | Include selected official interface, React, composition, transition, and writing guidance. |
| `vercel-web-interface-guidelines` | `vercel-labs/web-interface-guidelines@d0a657bfe87e86dd3a4753d7ec28c7e7dd7a88fe` | Official UI review quality gate. |
| `anthropic-frontend-design` | `anthropics/skills@9d2f1ae187231d8199c64b5b762e1bdf2244733d` | Preserve official frontend-design provenance and notice for the mapped MengTo duplicate. |
| `open-design` | `nexu-io/open-design@81b20dc6a214da2228bdd08f8850656b98f9bcea` | Registry-only on-demand provider; do not vendor the complete checkout. |

### Task 1: Remove Public Model Entitlement Assumptions

**Files:**
- Modify: `tests/test_codex_config.py`
- Modify: `.codex/templates/config.toml`
- Modify: `.codex/templates/agents/*.toml`
- Modify: `codex-home/config.toml`
- Modify: `codex-home/agents/*.toml`
- Modify: `prompts/fresh-install.md`
- Modify: `prompts/setup-codex-current-harness.md`

- [ ] **Step 1: Write failing model-inheritance tests**

Replace the hard-coded latest-model assertions with tests that require both public config trees to be byte-identical, retain `personality = "pragmatic"`, retain the agent and feature tables, and contain no assignments for `model`, `model_reasoning_effort`, `model_reasoning_summary`, `model_verbosity`, or `plan_mode_reasoning_effort` in either root or role configs. Add prompt assertions requiring the setup agent to ask for the partner name, discover runtime-supported models without promising a particular model, and avoid committing the rendered private name.

- [ ] **Step 2: Run the focused tests and observe RED**

Run:

```bash
python3 -m unittest tests.test_codex_config tests.test_prompt_corpus_policy -v
```

Expected: failures name the existing `gpt-5.5`, `gpt-5.4`, `xhigh`, `high`, and profile pins.

- [ ] **Step 3: Implement model inheritance**

Remove model and reasoning assignments and the `previous` and `balanced` profiles from both public config copies. Remove reasoning pins from every public role TOML while preserving sandbox, approval, role instructions, personality, feature, and concurrency policy. Update both setup prompts so the setup agent asks the user's preferred partner name, inspects what the active Codex and Claude runtimes actually support, and inherits those runtimes' selected model/reasoning ceiling.

- [ ] **Step 4: Run GREEN and inspect the diff**

Run:

```bash
python3 -m unittest tests.test_codex_config tests.test_prompt_corpus_policy -v
git diff --check
```

Expected: all focused tests pass and no whitespace errors are reported.

- [ ] **Step 5: Commit**

```bash
git add tests/test_codex_config.py tests/test_prompt_corpus_policy.py .codex/templates/config.toml .codex/templates/agents codex-home/config.toml codex-home/agents prompts/fresh-install.md prompts/setup-codex-current-harness.md
git commit -m "feat: inherit available agent models"
```

### Task 2: Define And Validate The Source, Lock, And Provenance Contract

**Files:**
- Create: `tests/frontend_design_test_support.py`
- Create: `tests/test_frontend_design_registry.py`
- Create: `design-stack/sources.json`
- Create: `design-stack/sources.lock.json`
- Create: `design-stack/provenance.json`
- Create: `scripts/design_stack.py`
- Create: `scripts/validate_frontend_design_stack.py`

- [ ] **Step 1: Write failing schema and inventory tests**

Use real temporary files, not mocks. Require every source to have `id`, `repository`, immutable `revision`, `authority`, `scope`, `license`, `role`, `update_method`, and local destination. Require lock entries to match the registry revision and list `path`, `size`, and `sha256`. Require every included file to resolve through provenance with upstream path, revision, license, notice, role, authority, hash, decision, and reason when transformed or not included. Assert exactly 95 MengTo decisions and 74 DESIGN.md index entries in the committed data; `meta` and `vercel` DESIGN.md entries must say `third-party-analysis`; Open Design must be `on-demand` and absent from the vendored tree; Google CLI must be pinned to `0.3.0`.

- [ ] **Step 2: Run RED**

```bash
python3 -m unittest tests.test_frontend_design_registry -v
```

Expected: missing registry, lock, provenance, and validator failures.

- [ ] **Step 3: Implement the standard-library data model and validator**

In `scripts/design_stack.py`, implement typed-by-validation JSON loaders, SHA-256 helpers, canonical path checks, frontmatter parsing for the supported upstream subset, catalog inventory checks, provenance resolution, and actionable `ValidationError` messages. Keep the command wrapper in `validate_frontend_design_stack.py` thin. Seed the registries with the locked source table above; do not fabricate inventories before importing the reviewed archives.

- [ ] **Step 4: Import only metadata needed to turn schema tests GREEN**

Generate the 95 MengTo decisions and 74 DESIGN.md entries from the actual pinned trees. Record known mappings for MengTo `pdf`, `screenshot`, `frontend-design`, `playwright`, and `playwright-interactive` to verified official sources instead of silently redistributing missing notices. Mark any unresolved file `blocked`, never MIT by assumption.

- [ ] **Step 5: Run GREEN and commit**

```bash
python3 -m unittest tests.test_frontend_design_registry -v
python3 scripts/validate_frontend_design_stack.py --repo-root . --metadata-only
git diff --check
git add design-stack/sources.json design-stack/sources.lock.json design-stack/provenance.json scripts/design_stack.py scripts/validate_frontend_design_stack.py tests/frontend_design_test_support.py tests/test_frontend_design_registry.py
git commit -m "feat: define design source provenance"
```

### Task 3: Build A Safe, Review-Only Update Pipeline

**Files:**
- Create: `tests/test_frontend_design_source_check.py`
- Create: `tests/test_frontend_design_sync.py`
- Create: `scripts/check_design_sources.py`
- Create: `scripts/sync_design_sources.py`
- Modify: `scripts/design_stack.py`

- [ ] **Step 1: Write failing read-only source-check tests**

Build local temporary Git repositories and immutable trees. Assert reports cover added, removed, renamed, instruction, description, script, asset, dependency, URL, permission, service, side-effect, license, and provenance changes. Snapshot all tracked design-stack/plugin bytes before and after and require no mutation.

- [ ] **Step 2: Run source-check RED**

```bash
python3 -m unittest tests.test_frontend_design_source_check -v
```

- [ ] **Step 3: Implement the read-only checker**

Accept explicit source directories in tests and use `git ls-remote` only in the live online mode. Compare against the lock, emit human-readable and JSON reports, never fetch, checkout, render, install, or write repository files.

- [ ] **Step 4: Write failing tar-sync safety tests**

Support tar archives only. Require a clean non-default task branch and an explicit local archive. Reject absolute paths, `..`, symlinks, hardlinks, devices, FIFOs, duplicate destination paths, revision mismatch, duplicate skill names, invalid frontmatter, and missing required files. Prove executable members remain inert with a sentinel script. Prove late failure leaves the previous lock, reference tree, catalog, and plugin byte-identical. Prove success replaces the source tree atomically and records every file's path, size, mode-as-data, and SHA-256.

- [ ] **Step 5: Run sync RED**

```bash
python3 -m unittest tests.test_frontend_design_sync -v
```

- [ ] **Step 6: Implement safe sync**

Never call `extractall` and never execute imported content. Inspect each `tarfile.TarInfo`, copy regular-file bytes into a staging directory, validate the staged tree and provenance, generate a semantic report, render into staging, and replace live outputs only after every gate passes. Require explicit `--source`, `--archive`, and immutable revision evidence.

- [ ] **Step 7: Run GREEN and commit**

```bash
python3 -m unittest tests.test_frontend_design_source_check tests.test_frontend_design_sync -v
git diff --check
git add scripts/design_stack.py scripts/check_design_sources.py scripts/sync_design_sources.py tests/test_frontend_design_source_check.py tests/test_frontend_design_sync.py
git commit -m "feat: add reviewed design source updates"
```

### Task 4: Author The Router Contract And Pressure Cases

**Files:**
- Create: `tests/test_frontend_design_router.py`
- Create: `design-stack/routing.json`
- Create: `design-stack/evals/routing-cases.json`
- Create: `design-stack/evals/trigger-cases.json`
- Create: `design-stack/router/SKILL.md`
- Create: `design-stack/router/references/source-precedence.md`
- Create: `design-stack/router/references/quality-gates.md`
- Create: `design-stack/templates/DESIGN.md.template`
- Create: `design-stack/templates/product-brief.md`
- Create: `design-stack/templates/design-decision.md`

- [ ] **Step 1: Write failing router tests**

Cover `shape`, `explore`, `implement`, `review`, `copy`, and `harden`. Keep positive/negative trigger fixtures separate from guidance-application fixtures. Require mode, target surface, and loaded references in each route; smallest-sufficient reference sets; at most three labeled inspiration sources; the approved source precedence; no edits in Shape/Review without explicit request; TDD in Implement; copy-only scope in Copy; external-side-effect material explicit-use-only; Open Design explicit-demand-only; and resolution of every included/mapped MengTo entry without creating 95 native skills.

- [ ] **Step 2: Run RED**

```bash
python3 -m unittest tests.test_frontend_design_router -v
```

- [ ] **Step 3: Implement router data, skill, references, and templates**

Keep `SKILL.md` concise: classify the request, inspect primary project evidence, load only catalog paths selected by `routing.json`, announce authority and scope, follow the mode contract, and report actual verification. Move detailed workflow, source precedence, reachable-state checks, visual-vs-build evidence, accessibility, responsiveness, motion, copy, React, and DESIGN.md procedure into references. Do not include mutable upstream commands or automatic installation instructions.

- [ ] **Step 4: Run GREEN and commit**

```bash
python3 -m unittest tests.test_frontend_design_router -v
git diff --check
git add design-stack/routing.json design-stack/evals design-stack/router design-stack/templates tests/test_frontend_design_router.py
git commit -m "feat: add frontend design router"
```

### Task 5: Import The Reviewed Corpus And Render One Dual Plugin

**Files:**
- Create/modify: `design-stack/vendor/**`
- Create: `tests/test_frontend_design_plugin.py`
- Create: `scripts/render_frontend_design_plugin.py`
- Create/modify: `plugins/frontend-design-pack/**`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `scripts/render_claude_plugin.py`
- Modify: `tests/test_claude_plugin.py`

- [ ] **Step 1: Write failing renderer and manifest tests**

Require byte-identical output in two clean destinations; tracked output equal to a fresh render; `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` with name `frontend-design-pack` and the same semantic version; exactly one native `frontend-design` skill; all references self-contained; no symlinks or parent-relative paths; catalog coverage for every included/mapped decision; separate runtime-root validation for Codex and Claude; and actionable reports for missing, changed, and unexpected runtime files. Update the existing marketplace test to index plugins by name and preserve `process-first-agents` coverage.

- [ ] **Step 2: Run RED**

```bash
python3 -m unittest tests.test_frontend_design_plugin tests.test_claude_plugin -v
```

- [ ] **Step 3: Create reviewed local tar archives**

Use `git archive` against the already reviewed immutable checkouts. Create one archive per source, import with `sync_design_sources.py`, and retain only the scoped files declared by `sources.json`. Import all vetted MengTo skill procedure files needed by the 95-decision catalog, all 74 VoltAgent DESIGN.md references, Google DESIGN.md contract material, selected official Vercel guidance, the official Anthropic frontend-design notice/mapping, and required license/notice files. Do not import the full Open Design checkout.

- [ ] **Step 4: Implement deterministic rendering**

Render from the lock and provenance ledger into a temporary destination, use sorted traversal and canonical JSON with trailing newlines, normalize only generated metadata, copy imported bytes unchanged, emit `THIRD_PARTY_NOTICES.md`, and atomically replace tracked output. Extend the existing marketplace renderer so both plugin entries remain stable when either bundle is regenerated.

- [ ] **Step 5: Render and validate the tracked plugin**

```bash
python3 scripts/render_frontend_design_plugin.py --repo-root .
python3 scripts/validate_frontend_design_stack.py --repo-root .
python3 -m unittest tests.test_frontend_design_plugin tests.test_claude_plugin -v
git diff --check
```

- [ ] **Step 6: Commit**

```bash
git add design-stack plugins/frontend-design-pack .claude-plugin/marketplace.json scripts/render_frontend_design_plugin.py scripts/render_claude_plugin.py scripts/design_stack.py tests/test_frontend_design_plugin.py tests/test_claude_plugin.py
git commit -m "feat: package frontend design references"
```

### Task 6: Add A Hash-Bound Vendor Safety Baseline

**Files:**
- Modify: `tests/test_private_path_scan.py`
- Modify: `scripts/check_private_paths.py`
- Create: `design-stack/vendor-scan-baseline.json`

- [ ] **Step 1: Write failing baseline tests**

Require an unchanged vendor file to suppress only the exact recorded finding at the exact content hash. Require changed content, a new finding, an invalid hash, a missing file, or an unlisted line to be scanned normally and fail. Require every new `design-stack/` and plugin text file to remain in repository scan scope.

- [ ] **Step 2: Run RED**

```bash
python3 -m unittest tests.test_private_path_scan -v
```

- [ ] **Step 3: Implement narrow baseline handling**

Load the baseline only for paths under the vendored/generated design corpus. Validate the file SHA-256 first, match the rule and normalized finding exactly, and never suppress findings in authored router, script, config, prompt, or documentation files. Generate entries only for reviewed upstream placeholders that the current scanner actually identifies.

- [ ] **Step 4: Run GREEN and commit**

```bash
python3 -m unittest tests.test_private_path_scan -v
python3 scripts/check_private_paths.py
git diff --check
git add scripts/check_private_paths.py tests/test_private_path_scan.py design-stack/vendor-scan-baseline.json
git commit -m "feat: scan vendored design references safely"
```

### Task 7: Integrate Public Setup, Documentation, Catalog, And CI

**Files:**
- Create: `tests/test_frontend_design_docs.py`
- Modify: `tests/test_skill_catalog.py`
- Modify: `tests/test_ci_workflow.py`
- Create: `docs/frontend-design-stack.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `README.ja.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/README.codex.md`
- Modify: `.codex/INSTALL.md`
- Modify: `prompts/fresh-install.md`
- Modify: `prompts/setup-codex-current-harness.md`
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Write failing public-contract tests**

Require every README to link the setup guide. Require the guide/prompts to ask for a partner name without committing a private default, inherit available Codex/Claude models, explain the design pack, ask before runtime install or replacement, validate tracked and runtime copies separately, require a fresh task/session for discovery, report Figma availability without authenticating, distinguish build/HTTP/source checks from visual verification, explain Open Design on-demand behavior, and label reverse-engineered brand references third-party analysis. Assert `skills/frontend-design` does not exist because distribution is through the plugin.

- [ ] **Step 2: Add CI expectation and run RED**

```bash
python3 -m unittest tests.test_frontend_design_docs tests.test_skill_catalog tests.test_ci_workflow -v
```

- [ ] **Step 3: Write the public setup/update guide and wire CI**

Document install, explicit source checking, reviewed tar sync, diff review, semantic version bump, Codex and Claude installation, fresh-session discovery, optional Figma authentication boundary, rollback with a new version, source authority, and real verification expectations. Add `python3 scripts/validate_frontend_design_stack.py --repo-root .` to CI after unit tests and before the existing audit/private-path gates.

- [ ] **Step 4: Run GREEN and commit**

```bash
python3 -m unittest tests.test_frontend_design_docs tests.test_skill_catalog tests.test_ci_workflow -v
python3 scripts/validate_frontend_design_stack.py --repo-root .
git diff --check
git add docs/frontend-design-stack.md README.md README.ko.md README.ja.md README.zh-CN.md docs/README.codex.md .codex/INSTALL.md prompts/fresh-install.md prompts/setup-codex-current-harness.md .github/workflows/ci.yml tests/test_frontend_design_docs.py tests/test_skill_catalog.py tests/test_ci_workflow.py
git commit -m "docs: add frontend design setup workflow"
```

### Task 8: Verify The Repository And External Plugin Schemas

**Files:**
- Modify only files required by objective test failures.

- [ ] **Step 1: Run the complete repository gate**

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/validate_frontend_design_stack.py --repo-root .
python3 scripts/audit_agent_stack.py --repo-only
python3 scripts/check_private_paths.py
python3 scripts/inventory_optional_tools.py --json
git diff --check
```

Expected: every command exits zero and the output contains no ignored errors.

- [ ] **Step 2: Run product validators**

```bash
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate plugins/frontend-design-pack
python3 -m venv /tmp/frontend-design-plugin-validate
/tmp/frontend-design-plugin-validate/bin/python -m pip install PyYAML
/tmp/frontend-design-plugin-validate/bin/python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/frontend-design-pack
/tmp/frontend-design-plugin-validate/bin/python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/frontend-design-pack/skills/frontend-design
```

Expected: both Claude validators and both Codex validators exit zero. The disposable environment is verification-only and is not committed.

- [ ] **Step 3: Perform two-stage review**

Use a fresh spec-compliance reviewer against `docs/superpowers/specs/2026-07-10-frontend-design-stack-design.md`, resolve every objective gap, rerun the focused tests, then use a fresh code-quality reviewer and resolve every confirmed issue. Do not combine these reviews.

- [ ] **Step 4: Run final repository gate and commit fixes**

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/validate_frontend_design_stack.py --repo-root .
python3 scripts/audit_agent_stack.py --repo-only
python3 scripts/check_private_paths.py
git diff --check
git status --short --branch
```

Commit any review fixes in focused commits. Do not install runtime copies until this gate is green.

### Task 9: Install And Verify Hun's Local Codex Copy

**Files:**
- No repository file edits unless runtime validation reveals a tracked packaging defect.

- [ ] **Step 1: Record current local plugin state**

```bash
codex plugin marketplace list
codex plugin list
```

Expected: the commands succeed; preserve unrelated installed plugins, including the already approved official Figma plugin.

- [ ] **Step 2: Add or refresh the local repository marketplace**

Use the current Codex CLI's documented `plugin marketplace add` command with `/Users/hooooonje/codex-dotfiles`. If the marketplace already exists, use only the documented non-destructive refresh/update path; do not remove unrelated marketplaces or plugins.

- [ ] **Step 3: Install the approved plugin**

Use the discovered fully qualified plugin ID for `frontend-design-pack` and `codex plugin add`. Do not authenticate Figma or change any account state.

- [ ] **Step 4: Locate and validate the installed Codex root**

Use `codex plugin list` and read-only filesystem inspection to identify the actual installed cache root. Run:

```bash
python3 scripts/validate_frontend_design_stack.py --repo-root . --codex-runtime-root <actual-installed-plugin-root>
```

Expected: the installed root is byte-identical to the tracked plugin, except a documented Codex cachebuster/version wrapper if the CLI adds one.

- [ ] **Step 5: Verify discovery in a fresh Codex task**

Start a fresh task because skills are discovered at task start. Run a read-only pressure case that should select `frontend-design`, report one router mode, a target surface, and the smallest loaded reference set, without editing or invoking imported scripts. Record observed evidence; do not claim live discovery from static file validation alone.

- [ ] **Step 6: Final status**

```bash
git status --short --branch
git log --oneline --decorate -10
```

Expected: no uncommitted repository changes, the task branch contains focused commits, the tracked plugin passes all gates, and Hun's installed Codex copy passes separate validation. Leave merging, pushing, publication, and Claude installation to a separately approved release action.
