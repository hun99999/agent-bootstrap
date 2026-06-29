# Skill Catalog

This directory is a browse, review, select, then install catalog for reusable skills.
Codex is the primary catalog target. Public-safe portable skills may also be
reviewed and installed into Claude Code's user skill home.

It is not an always-install bootstrap. Future agents should inspect this catalog,
compare a selected skill with the installed runtime copy under `~/.codex/skills`
or `~/.claude/skills`, ask before installing or overwriting, then validate the
installed skill.

## Catalog Rules

- The repo copy is the reviewable catalog source.
- The installed copy under `~/.codex/skills/<skill-name>` is the runtime copy used by Codex.
- The installed copy under `~/.claude/skills/<skill-name>` is the runtime copy used by Claude Code.
- Do not install every skill automatically.
- Do not copy private paths, credentials, MCP endpoints, auth state, browser profiles, or machine-specific trust settings into tracked files.
- Run the skill validator after installing or syncing a skill.
- Preserve original catalog/vendor skills separately from Hun-specific operational wrappers.

## Private Project Skills

Private project skills such as auto-eva belong in local runtime skill homes, not this public catalog. Use `~/.codex/skills` for Codex and `~/.claude/skills` for Claude Code. Keep templates and public-safe process guidance here; keep private access paths, credentials, auth state, browser profiles, customer data, and machine-specific trust settings out of git.

## Skill QA Contract

Treat skill changes as tested workflow code. Start with a failing test or explicit pressure scenario when possible, run the skill validator, run relevant repo tests, check for private paths and secrets, and verify the installed runtime copy separately from the repo catalog source before calling the skill ready.

### chatgpt-collaboration-harness

Use this first when work should be coordinated with ChatGPT Pro across staged implementation, delegated subtasks, Search Mode, deep research, source-backed investigation, or final review.

Key policy:

- Codex owns local files, validation, and final judgment.
- Use `references/file-artifact-exchange.md` when the stage needs approved screenshots, files, and generated artifacts.
- ChatGPT Pro must not answer from inference alone when facts, project source behavior, official docs, rankings, preferences, or public sentiment matter.
- Technical claims should use project source, local evidence, official documentation, primary sources, or source-backed research first.
- Community evidence is allowed for taste, popularity, adoption, or preference questions, but it must be labeled `community-sentiment`, not treated as official fact.
- ChatGPT Pro and Codex summaries are Korean by default unless Hun asks otherwise or the deliverable requires another language.
- Keep one goal, one ChatGPT work tab or conversation, one approved sharing scope, and one validation record per project.

Catalog path: `skills/chatgpt-collaboration-harness`

Codex runtime install target: `~/.codex/skills/chatgpt-collaboration-harness`

Claude Code install: review and adapt before use. This skill assumes a
Codex-owned local validation loop plus ChatGPT Pro browser collaboration, so do
not auto-sync it into Claude Code without checking those tool assumptions.

### karpathy-guidelines

Use this when writing, reviewing, or refactoring code and the main risk is overcomplication, hidden assumptions, broad diffs, or weak success criteria.

Key policy:

- This is an original catalog/vendor skill preserved from `multica-ai/andrej-karpathy-skills`.
- Keep upstream attribution and the MIT license note in `skills/karpathy-guidelines/references/SOURCE.md`.
- Do not add Hun-specific local workflow rules to this skill.
- Use `hun-engineering-loop` when the work also needs memory preflight, source-of-truth ordering, access approval boundaries, and QA evidence contracts.

Catalog path: `skills/karpathy-guidelines`

Codex runtime install target: `~/.codex/skills/karpathy-guidelines`

Claude Code runtime install target: `~/.claude/skills/karpathy-guidelines`

### hun-engineering-loop

Use this for Hun-specific non-trivial engineering work across planning, implementation, review, refactor, QA, or handoff.

Key policy:

- This is the Hun-specific operational wrapper around `karpathy-guidelines`, repo rules, memory preflight, and executable verification.
- Memory is a recall layer, not a source of truth.
- Current repo docs, scripts, tests, `AGENTS.md`, and observed runtime output beat memory and external advice.
- Broad access is allowed only as capability; high-risk actions still require a stop/ask approval boundary.
- Every project skill should name a concrete QA evidence contract instead of saying only "test it".

Catalog path: `skills/hun-engineering-loop`

Codex runtime install target: `~/.codex/skills/hun-engineering-loop`

Claude Code runtime install target: `~/.claude/skills/hun-engineering-loop`

### _template

Use this only as a starting skeleton for future catalog entries. The files are intentionally named with `.template` suffixes so they are not installed as a working skill by accident.

Catalog path: `skills/_template`
