# Agent Bootstrap Structure

`agent-bootstrap` is a public-safe baseline for preparing AI coding environments
for Codex and Claude Code.

OpenCode and OpenClaw files may remain in history or legacy folders for audit
and migration reference, but they are not current first-class service targets.
Do not expand those surfaces unless Hun explicitly asks to restore them.

## Shared Core

The shared core defines the behavior once:

- `AGENTS.md`
- `agents/*.md`
- `shared/agent-metadata.json`
- repository-level docs and prompts that explain the operating model

These files provide the process-first constitution, role prompts, source of
truth ordering, high-risk approval boundary, TDD expectation, review habits, and
privacy rules that Codex and Claude Code adapters consume.

## Harness Adapters

Current first-class harness adapters are:

- `.codex/`
  - Codex installer, templates, and install docs.
  - `.codex/install.py` renders Codex config and user-level defaults.
  - `.codex/templates/config.toml` and `.codex/templates/local.md` are Codex-specific templates.
- `.claude-plugin/`
  - Repository-level Claude Code marketplace entry.
- `plugins/process-first-agents/`
  - Generated Claude Code plugin package.
  - `scripts/render_claude_plugin.py` renders this package from the shared core.

Legacy OpenCode/OpenClaw docs or prompts are not part of the active setup path.
Do not route new setup work through them by default.

## Generated Artifacts

Generated artifacts are committed so a fresh cloner can inspect and install the
Claude Code plugin without guessing what the renderer should produce.

Generated Claude Code plugin files include:

- `.claude-plugin/marketplace.json`
- `plugins/process-first-agents/.claude-plugin/plugin.json`
- `plugins/process-first-agents/settings.json`
- `plugins/process-first-agents/agents/*.md`

Do not edit generated Claude plugin agents by hand. Change the shared source,
run the renderer, then verify the generated bundle.

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
```

## Skill Catalog

The public skill model is deliberately small:

- `skills/karpathy-guidelines/` is the public default base skill.
- `skills/chatgpt-collaboration-harness/` is an optional Codex collaboration skill, not a Claude Code default.
- `skills/hun-engineering-loop/` is a Hun-local wrapper, not part of the public default install set.
- `skills/_template/` is a template for future project workflow skills.

Optional Codex skill catalog workflow:

- [skills/README.md](../skills/README.md)
- [docs/codex-skills.md](codex-skills.md)
- [prompts/setup-codex-skills.md](../prompts/setup-codex-skills.md)

Optional Claude Code skill catalog workflow:

- [docs/claude-skills.md](claude-skills.md)

Private project skills stay in local runtime homes such as `~/.codex/skills` or
`~/.claude/skills`, not in this public repository.

## Source Of Truth

When changing this repository, use this order:

1. Hun's latest instruction.
2. `AGENTS.md`.
3. Current README and docs.
4. Tests and scripts.
5. Generated artifacts.
6. Memory or prior summaries.

Memory is a recall layer, not a source of truth. Current repo files, scripts,
tests, and observed runtime output override memory when they conflict.

## No Private Paths

Tracked files must not contain:

- personal home paths
- private project access paths
- credentials, tokens, keys, or auth state
- private MCP endpoints
- browser profiles
- machine-specific trust settings
- customer data

Run the private-path checker before publishing docs, prompts, skills, generated
plugin output, or setup script changes:

```bash
python3 scripts/check_private_paths.py
```

## Update Flow

Use this flow after pulling repo changes or changing shared prompts, metadata,
docs, skills, or generated plugin output:

```bash
git status --short --branch
python3 scripts/render_claude_plugin.py --partner-name "Hun"
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/audit_agent_stack.py
python3 scripts/check_private_paths.py
```

If the worktree is dirty before starting, stop and decide how to preserve local
work. Do not stash, overwrite, or delete user work automatically.

## Editing Map

- Shared behavior: `AGENTS.md` and `agents/*.md`
- Role metadata: `shared/agent-metadata.json`
- Codex installer: `.codex/install.py`
- Claude renderer: `scripts/render_claude_plugin.py`
- Root onboarding docs: `README.md` plus translated README files
- Harness docs: `docs/README.codex.md`, `docs/README.claude.md`
- Skill catalog docs: `skills/README.md`, `docs/codex-skills.md`, `docs/claude-skills.md`
- Repo metadata guidance: `docs/repo-metadata.md`

## Review Checklist

Before calling a change complete:

- The README and translated README files agree on first-class supported surfaces.
- Codex and Claude Code docs do not route users into legacy setup paths.
- `karpathy-guidelines` remains the public default base skill.
- `hun-engineering-loop` is described as Hun-local, not a public default.
- `chatgpt-collaboration-harness` is not installed into Claude Code.
- Generated Claude plugin output matches the renderer.
- Tests pass.
- No private paths or secrets are present.
