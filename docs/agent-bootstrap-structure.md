# Agent Bootstrap Structure

`agent-bootstrap` is a public-safe baseline for preparing AI coding environments
for Codex and Claude Code.

OpenCode and OpenClaw files may remain in history or legacy folders for audit
and migration reference, but they are not current first-class service targets.
Do not expand those surfaces unless the user explicitly asks to restore them.

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
- `plugins/frontend-design-pack/`
  - Generated dual-runtime plugin containing the single native `frontend-design` router.
  - `scripts/render_frontend_design_plugin.py` renders it from reviewed design source and routing
    metadata.

## Frontend Design Source

The reviewed design source is separate from generated runtime output:

- `design-stack/sources.json` defines source authority, scope, update method, and distribution.
- `design-stack/sources.lock.json` pins reviewed revisions, trees, files, modes, sizes, and hashes.
- `design-stack/provenance.json` records inclusion decisions and source evidence.
- `design-stack/router/` contains the authored router and reference-selection contracts.
- `design-stack/vendor/` contains only reviewed, license-compatible vendored material.
- `design-stack/vercel-runtime-skills.json` maps exact external companion skill identities without
  copying unresolved-license upstream skill bodies into the plugin.

Change authored source and metadata, then run `scripts/render_frontend_design_plugin.py`. Do not
edit `plugins/frontend-design-pack/` by hand.

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

Generated frontend design plugin files include:

- `plugins/frontend-design-pack/.codex-plugin/plugin.json`
- `plugins/frontend-design-pack/.claude-plugin/plugin.json`
- `plugins/frontend-design-pack/skills/frontend-design/`
- `plugins/frontend-design-pack/THIRD_PARTY_NOTICES.md`

Do not edit generated Claude plugin agents by hand. Change the shared source,
run the renderer, then verify the generated bundle.

```bash
python3 scripts/render_claude_plugin.py --partner-name "<chosen-name>"
python3 scripts/render_frontend_design_plugin.py --repo-root .
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

1. The user's latest instruction.
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
python3 scripts/render_claude_plugin.py --partner-name "<chosen-name>"
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/audit_agent_stack.py
python3 scripts/validate_frontend_design_stack.py --repo-root .
python3 scripts/check_private_paths.py
```

Use `<chosen-name>` instead of a public default when rendering local identity. If design source or
the generated design plugin changed, validate the tracked plugin and resolve the live Codex and Claude runtime roots.
A local Codex marketplace may resolve to the tracked plugin root, while a cached install may be distinct.
Ask before installing a new runtime plugin or replacing a distinct stale cached install. Validate each resolved live root
separately, then use a fresh task or session to prove discovery.

If the worktree is dirty before starting, stop and decide how to preserve local
work. Do not stash, overwrite, or delete user work automatically.

## Editing Map

- Shared behavior: `AGENTS.md` and `agents/*.md`
- Role metadata: `shared/agent-metadata.json`
- Codex installer: `.codex/install.py`
- Claude renderer: `scripts/render_claude_plugin.py`
- Frontend design registry, locks, provenance, and router: `design-stack/`
- Frontend design renderer: `scripts/render_frontend_design_plugin.py`
- Frontend design validator: `scripts/validate_frontend_design_stack.py`
- Generated frontend design plugin: `plugins/frontend-design-pack/`
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
- Generated frontend design plugin output matches its renderer, source locks, and provenance.
- Each live runtime root is resolved and validated; a tracked local Codex root is not conflated with
  a distinct cached install.
- Tests pass.
- No private paths or secrets are present.
