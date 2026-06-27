# Codex Long-Running Work Settings Design

## Summary

Improve only the Codex-side setup so Hun's local Codex defaults better support long-running work, while leaving Claude Code, OpenCode, OpenClaw, and shared cross-harness prompt surfaces unchanged.

The target is not a new automation system. The target is a tighter Codex operating loop:

- high-autonomy Codex permissions remain intentional: `approval_policy = "never"` and `sandbox_mode = "danger-full-access"`
- long-running work uses verifiable goals, checkpoints, progress logs, and explicit stopping conditions
- memory stays enabled as a local recall layer, while durable rules remain in checked-in Codex docs and templates
- Codex setup prompts explain when to use `/goal`, skills, browser, Chrome, computer use, and memory notes
- the repository's Codex templates remain the source of truth for future `~/.codex` installs

## Sources

This design is based on the current repository state plus current OpenAI Codex guidance reviewed on 2026-06-24:

- OpenAI article: `https://openai.com/index/codex-maxxing-long-running-work/`
- OpenAI whitepaper PDF: `https://cdn.openai.com/pdf/8a9f00cf-d379-4e20-b06f-dd7ba5196a11/OAI_WhitePaper_Codex-maxxing26.pdf`
- Codex best practices: `https://developers.openai.com/codex/learn/best-practices`
- Codex config basics: `https://developers.openai.com/codex/config-basic`
- Codex follow goals: `https://developers.openai.com/codex/use-cases/follow-goals`
- Codex memories: `https://developers.openai.com/codex/memories`
- Codex subagents: `https://developers.openai.com/codex/subagents`
- Codex skills: `https://developers.openai.com/codex/skills`

The relevant guidance is:

- Use `AGENTS.md` and configuration for reusable, durable behavior.
- Keep personal defaults in `~/.codex/config.toml` and project behavior in `.codex/config.toml` or repo-local docs.
- Use goals for work with one objective, a stopping condition, proof commands, checkpoints, and compact progress reports.
- Treat memories as helpful recall, not the only place for required rules.
- Use skills for repeated workflows instead of repeated long prompts.
- Use subagents for independent or highly parallel work, with awareness that they consume more tokens and inherit parent runtime policy.
- Separate browser, Chrome, computer-use, connector, and skill surfaces by what each task actually needs.

## Current State

The repository already has a strong Codex setup:

- `.codex/templates/config.toml` and `codex-home/config.toml` define `gpt-5.5`, `xhigh` reasoning, a `balanced` profile, a `previous` profile, custom role agents, `[agents] max_threads = 6`, `[agents] max_depth = 1`, and `[features] multi_agent = true`.
- `tests/test_codex_config.py` verifies the Codex template and snapshot config stay identical, verifies model policy, verifies role configs, and prevents role-level model pins.
- `docs/README.codex.md`, `.codex/INSTALL.md`, and `prompts/setup-codex-current-harness.md` explain Codex installation and current-harness-only behavior.
- The live `~/.codex/config.toml` already includes `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, `memories = true`, and memory settings.

The gap is that the checked-in Codex templates do not fully encode the intended high-autonomy permission and memory policy. A future reinstall from this repository can overwrite live Codex behavior with a weaker source-of-truth. The docs also do not yet provide a first-class Codex long-running-work prompt or concise operating contract.

## Scope

This work is Codex-only.

Modify only Codex-scoped files:

- `.codex/templates/config.toml`
- `codex-home/config.toml`
- `.codex/templates/local.md`
- `codex-home/local.md`
- `docs/README.codex.md`
- `.codex/INSTALL.md`
- `prompts/setup-codex-current-harness.md`
- a new Codex-only long-running-work prompt under `prompts/`
- Codex-related tests under `tests/`

Do not modify Claude Code, OpenCode, OpenClaw, or shared cross-harness surfaces:

- no `.claude-plugin/` changes
- no `plugins/process-first-agents/` changes
- no `docs/README.claude.md`, `docs/README.opencode.md`, or `docs/README.openclaw.md` changes
- no `prompts/setup-claude-current-harness.md`, `prompts/setup-opencode-current-harness.md`, or OpenClaw prompt changes
- no `scripts/render_claude_plugin.py` or generated Claude plugin refresh
- no shared `AGENTS.md` or `agents/*.md` changes, because those are shared prompt corpus files and can affect Claude Code plugin output
- no new broad automation runner unless a later design explicitly approves it

## Design

### 1. Codex Config Source Of Truth

Add the intentional high-autonomy default to both Codex config source files:

```toml
approval_policy = "never"
sandbox_mode = "danger-full-access"
```

Add long-running-work feature defaults:

```toml
[features]
goals = true
multi_agent = true
memories = true

[memories]
generate_memories = true
use_memories = true
disable_on_external_context = true
```

Keep the existing model, profile, and agent role policy unless a test exposes a concrete mismatch. Do not change role-level `sandbox_mode` or `approval_policy` in this pass. Role-specific read-only/write behavior is separate from root session autonomy and was already intentionally tested.

The installer already replaces `{{CODEX_HOME_ABS}}` in agent TOML files and verifies role config references. No installer architecture change is expected.

### 2. Codex Local Notes Template

Replace the minimal `local.md` template with a Codex-only note surface for long-running state.

The template should remain short and machine-safe:

- state that durable rules belong in checked-in docs, not generated memory
- reserve space for active long-running work notes
- reserve space for local-only tool or environment notes
- remind agents not to commit credentials, private paths, MCP endpoints, auth state, browser profiles, or machine-specific trust settings

This file is installed into `~/.codex/local.md`, so it may contain local note headings, but the checked-in template must not include Hun's private project paths or live secrets.

### 3. Codex Long-Running Prompt

Add `prompts/start-codex-long-running-work.md`.

The prompt should be public-shareable and path-neutral. It should ask Codex to:

- read the repository's Codex instructions and task-relevant docs first
- confirm the current working tree before changes
- define one objective and one stopping condition
- identify files, docs, logs, issues, or plans to read first
- define proof commands or artifacts
- break the work into checkpoints
- use `/goal` or goal tooling when available
- keep a compact progress log
- separate tool surfaces: local browser for local previews, Chrome for authenticated browser state, computer use for GUI-only work, MCP/connectors only when the source of truth lives outside the repo, skills for repeatable workflows
- keep memory-worthy facts as explicit notes for review, not hidden assumptions
- stop before irreversible, destructive, production, account, billing, external-send, or broad architecture actions unless the user approved that exact action

The prompt should not include private local paths.

### 4. Codex Docs

Update `docs/README.codex.md` and `.codex/INSTALL.md` only.

The docs should explain:

- the setup intentionally installs high-autonomy Codex defaults
- high autonomy does not remove user approval requirements for irreversible or external side-effect actions
- long-running work should use a goal with one objective, a stopping condition, checkpoints, and proof commands
- memory is enabled but required rules stay in checked-in docs
- Codex App and CLI may need a restart after config changes
- the new long-running prompt is the recommended starting point for broad Codex-only work

Update `prompts/setup-codex-current-harness.md` so setup workers preserve and report these Codex-only defaults.

Do not update translated README files in this pass unless a Codex-only test already requires it. The narrower Codex docs are enough for the requested scope.

### 5. Tests

Use TDD for behavior changes:

1. Add failing tests in `tests/test_codex_config.py` proving both `.codex/templates/config.toml` and `codex-home/config.toml` include:
   - root `approval_policy = "never"`
   - root `sandbox_mode = "danger-full-access"`
   - `[features] goals = true`
   - `[features] memories = true`
   - `[memories] generate_memories = true`
   - `[memories] use_memories = true`
   - `[memories] disable_on_external_context = true`

2. Add or extend a Codex docs test proving:
   - `docs/README.codex.md` references long-running work, goals, memory, and `prompts/start-codex-long-running-work.md`
   - `.codex/INSTALL.md` documents the high-autonomy defaults
   - `prompts/setup-codex-current-harness.md` mentions preserving high-autonomy Codex defaults
   - `prompts/start-codex-long-running-work.md` exists and does not contain private local paths

3. Verify the new tests fail before implementation.

4. Make the smallest changes to pass.

5. Run the relevant focused tests, then the normal repository verification stack:
   - `python3 -m unittest discover -s tests -p 'test_*.py'`
   - `python3 scripts/audit_agent_stack.py`
   - `python3 scripts/check_private_paths.py`
   - `git diff --check`

### 6. Global Install

After tests pass and Hun approves the implementation plan, run the Codex installer:

```bash
bash .codex/install.sh --partner-name "Hun"
```

Then verify the live config:

```bash
codex features list
```

The live feature list should show `goals`, `multi_agent`, and `memories` enabled. The live `~/.codex/config.toml` should retain the high-autonomy permission defaults.

## Risks

- Updating root/shared prompt files would accidentally affect Claude Code or OpenCode. This design avoids that by limiting edits to Codex-specific files.
- `~/.codex/config.toml` contains local plugin, MCP, project trust, and desktop state that should not be copied into tracked templates. Only stable Codex setup defaults belong in the repo templates.
- High autonomy can execute destructive local commands without approval. Hun explicitly approved the high-autonomy default, so the mitigation is documentation and prompt-level action boundaries for irreversible or external side effects.
- Memory generation can lag and should not be treated as a reliable rule store. Required rules stay in checked-in Codex docs and templates.

## Acceptance Criteria

- The work changes only Codex-scoped files listed in this design.
- Checked-in Codex templates encode high-autonomy root defaults and long-running-work features.
- Codex docs and setup prompts explain long-running goals, checkpoints, memory boundaries, tool-surface separation, and high-autonomy action boundaries.
- A public-shareable Codex long-running-work prompt exists.
- Tests cover the new Codex config and docs expectations.
- Full repository verification passes.
- The final global install updates `~/.codex` without touching Claude Code, OpenCode, or OpenClaw setup.
