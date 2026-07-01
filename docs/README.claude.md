# Claude Code

This repository supports Claude Code in two layers:

- install Anthropic's official `superpowers` plugin for the skills library
- install this repository's `process-first-agents` plugin for the shared agent prompts

## Default Scope

Inside Claude Code, the default setup scope is `current-harness-only`.

If the user says "set this up from the repo" and does not explicitly ask for Codex, configure Claude Code only.

Do not configure another harness unless the user explicitly asks.

OpenCode and OpenClaw are not current first-class setup targets for this repository.

## Recommended Setup

1. Install upstream `superpowers` from the official Claude marketplace.
2. Clone this repository locally.
3. Run `git status --short --branch` and stop if there is uncommitted or untracked user work.
4. Render the Claude plugin bundle with your preferred partner name.
5. Add the local repository as a Claude plugin marketplace.
6. Install `process-first-agents` from that marketplace.
7. Optionally review and install only the public Claude Code skill set into `~/.claude/skills`.

## Render the Plugin Bundle

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
```

This writes:

- `.claude-plugin/marketplace.json`
- `plugins/process-first-agents/.claude-plugin/plugin.json`
- `plugins/process-first-agents/settings.json`
- `plugins/process-first-agents/agents/*.md`

Do not edit generated Claude plugin agents by hand. Change the shared source and re-run the renderer.

## Install in Claude Code

```text
/plugin marketplace add /absolute/path/to/this/repo
/plugin install process-first-agents@agent-bootstrap
```

This installs the `process-first-agents` Claude Code plugin as the user-level defaults for the shared agent prompts. New Claude Code sessions can then use the same process-first constitution and vibe-coding guardrails across projects. In other words, new Claude Code sessions should inherit these user-level defaults after the plugin is installed or updated.

Project-specific structure still belongs in project-local knowledge such as
`local.md`, an untracked note, or a private Obsidian page. Existing Claude Code
sessions may need a restart, plugin reload, or a short manual instruction to
apply newly installed guardrails.

## Claude Code Skill Catalog

Use [docs/claude-skills.md](claude-skills.md) when Claude Code should use the
same public-safe reusable skill model that was added for Codex.

Recommended portable skill:

- `karpathy-guidelines`

Install selected skills into `~/.claude/skills`. Do not install every catalog
skill automatically, and do not copy private project skills into this public
repository.

Do not install `hun-engineering-loop` as part of the public Claude Code default.
It is a Hun-local wrapper and can exist in Hun's private runtime when explicitly
approved for that machine.

Do not install `chatgpt-collaboration-harness` into Claude Code. It assumes a
Codex-owned local validation loop plus ChatGPT Pro browser collaboration.

## Update

After pulling new repo changes:

```bash
git status --short --branch
git pull --ff-only
python3 scripts/render_claude_plugin.py --partner-name "Hun"
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/audit_agent_stack.py
```

Then update the plugin inside Claude Code if generated files changed.

## Audit

```bash
python3 scripts/audit_agent_stack.py
```

The default audit is offline and read-only. It checks the local Codex CLI,
Claude Code CLI, Superpowers checkout state, the Codex skills symlink, and the
generated Claude plugin bundle. Add `--online` only when you explicitly want
current npm and remote git drift checks.
