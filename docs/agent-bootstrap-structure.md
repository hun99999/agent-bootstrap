# agent-bootstrap Structure

This is the project-local structure map for `agent-bootstrap`. Use it before changing installer behavior, shared agent prompts, generated plugin output, setup docs, or copy-paste prompts.

## Purpose

`agent-bootstrap` is a public-safe baseline for preparing AI coding environments across Codex, Claude Code, and OpenCode.

It has two jobs:

1. Install or render the same process-first operating model into each supported harness.
2. Give future agents enough repository structure to update that operating model without duplicating prompts, editing generated output by hand, or leaking local machine state.

## Shared Core

The shared core is the source of truth for the operating model.

- `AGENTS.md`
  - Shared constitution template.
  - Contains global behavior rules, structure guardrails, TDD requirements, review requirements, version-control policy, and privacy boundaries.
  - Must stay identical to `codex-home/AGENTS.md`.
- `agents/*.md`
  - Shared role prompt bodies.
  - These are the prompt bodies that Codex, Claude Code, and OpenCode adapters render or copy.
- `shared/agent-metadata.json`
  - Role metadata used by Claude plugin rendering and OpenCode install tests.
  - Add new agent metadata here before expecting harness adapters to render a new role.

## Harness Adapters

Harness adapters translate the shared core into each host's native shape.

- `.codex/`
  - Current Codex installer and templates.
  - `.codex/install.py` is the implementation.
  - `.codex/install.sh` is the shell entrypoint.
  - `.codex/templates/config.toml` and `.codex/templates/local.md` are Codex-specific templates.
- `codex-home/`
  - Checked-in sample/rendered Codex home tree.
  - `codex-home/AGENTS.md` and `codex-home/agents/*.md` must mirror the shared core.
  - `codex-home/agents/*.toml` are Codex role config files.
- `.opencode/`
  - OpenCode installer, templates, and install docs.
  - `.opencode/install.py` renders OpenCode config and agent files.
- `.claude-plugin/marketplace.json`
  - Repository-level Claude Code marketplace entry.
- `plugins/process-first-agents/`
  - Generated Claude Code plugin package.
  - Built by `scripts/render_claude_plugin.py`.
- `skills/`
  - Optional Codex skill catalog.
  - `skills/README.md` lists available catalog skills.
  - Skill source directories such as `skills/chatgpt-collaboration-harness/` are reviewable catalog copies, not automatically installed runtime state.

## Generated Artifacts

Generated artifacts are committed because users install directly from this repository, but they should not become separate sources of truth.

- Do not edit generated Claude plugin agents by hand.
- Regenerate Claude output with:

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
```

- After changing `AGENTS.md`, `agents/*.md`, or `shared/agent-metadata.json`, compare generated output and commit the source and generated changes together.
- Treat `plugins/process-first-agents/agents/*.md` as render output.
- Treat `codex-home/AGENTS.md` and `codex-home/agents/*.md` as mirrors of the shared core, guarded by tests.

## Source Of Truth

- Shared behavior rules: `AGENTS.md`.
- Role behavior: `agents/*.md`.
- Role metadata: `shared/agent-metadata.json`.
- Codex install behavior: `.codex/install.py`.
- OpenCode install behavior: `.opencode/install.py`.
- Claude plugin render behavior: `scripts/render_claude_plugin.py`.
- Stack verification behavior: `scripts/audit_agent_stack.py`.
- Public setup explanation: `README.md` and `docs/README.*.md`.
- Guardrail workflow explanation: `docs/vibe-coding-guardrails.md`.
- Global installation and optional tooling rules: `docs/global-guardrail-setup.md`.
- Project-local knowledge shape: `docs/local-project-knowledge-template.md`.
- Optional Codex skill catalog workflow: `docs/codex-skills.md`.
- Optional Codex skill setup prompt: `prompts/setup-codex-skills.md`.

## Dependency Direction

Keep dependency direction simple:

1. Shared prompt corpus feeds harness adapters.
2. Harness adapters render or install host-specific files.
3. Tests verify the shared corpus, adapter output, docs, and generated plugin bundle.
4. Public docs explain how to use the output.

Do not make shared prompt files depend on generated artifacts. Do not make tests depend on local user paths or already-installed harness state unless the test explicitly uses a temporary directory.

## Update Flow

Use this flow when Hun says the repository has been updated and asks an agent to apply or improve the setup:

1. Check Git state.

```bash
git status --short --branch
```

2. Pull only when the worktree is clean or Hun has approved how to handle local changes.

```bash
git pull --ff-only
```

3. Read the structure and guardrail docs.

```text
docs/agent-bootstrap-structure.md
docs/vibe-coding-guardrails.md
docs/global-guardrail-setup.md
```

4. Run a pre-write lens over touched areas: shared core, adapters, generated artifacts, tests, docs, and prompts.
5. Use TDD for behavior, installer, renderer, policy, and prompt-contract changes.
6. Regenerate Claude plugin output when shared prompt or metadata sources change.

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
```

7. Install globally only when the current task asks to update the local harness defaults. Run only the installer for the harness being updated.

```bash
bash .codex/install.sh --partner-name "Hun"
bash .opencode/install.sh --partner-name "Hun"
```

8. Verify repository behavior.

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/audit_agent_stack.py
```

9. Run post-write review for duplicate prompt rules, generated output drift, private path leakage, swallowed errors, unmanaged compatibility behavior, and weak tests.

## Review Hotspots

Check these areas carefully:

- `AGENTS.md` and `codex-home/AGENTS.md` drift.
- `agents/*.md`, `codex-home/agents/*.md`, and `plugins/process-first-agents/agents/*.md` drift.
- `shared/agent-metadata.json` missing metadata for a new role.
- Installer changes that overwrite user files without backup or preflight.
- Claude renderer changes that silently accept unknown placeholders.
- Docs that mention commands not implemented by this repository.
- Optional tool docs that imply installation without user approval.
- Skill catalog changes that confuse the repo catalog source with the runtime copy under `~/.codex/skills`.

## Privacy Boundary

No private paths, credentials, tokens, cookies, MCP endpoints, auth state, or machine-specific trust settings belong in tracked files.

Use `local.md`, untracked notes, or a private Obsidian page for local-only state. Public docs should describe what to record, not where Hun personally stores it.
