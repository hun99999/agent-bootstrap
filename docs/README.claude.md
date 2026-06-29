# Claude Code

This repository supports Claude Code in two layers:

- install Anthropic's official `superpowers` plugin for the skills library
- install this repository's `process-first-agents` plugin for the shared agent prompts

## Default Scope

Inside Claude Code, the default setup scope is `current-harness-only`.

If the user says "set this up from the repo" and does not explicitly ask for Codex, OpenCode, OpenClaw ACP, or cross-harness setup, configure Claude Code only.

Do not configure another harness unless the user explicitly asks.

## Recommended Setup

1. Install upstream `superpowers` from the official Claude marketplace.
2. Clone this repository locally.
3. Render the Claude plugin bundle with your preferred partner name.
4. Add the local repository as a Claude plugin marketplace.
5. Install `process-first-agents` from that marketplace.
6. Optionally review and install public-safe skills into `~/.claude/skills`.

## Render the Plugin Bundle

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
```

This writes:

- `.claude-plugin/marketplace.json`
- `plugins/process-first-agents/.claude-plugin/plugin.json`
- `plugins/process-first-agents/settings.json`
- `plugins/process-first-agents/agents/*.md`

## Install in Claude Code

```text
/plugin marketplace add /absolute/path/to/this/repo
/plugin install process-first-agents@agent-bootstrap
```

This installs the `process-first-agents` Claude Code plugin as the user-level defaults for the shared agent prompts. New Claude Code sessions can then use the same process-first constitution and vibe-coding guardrails across projects.

In other words, new Claude Code sessions should inherit these user-level defaults after the plugin is installed or updated.

Project-specific structure still belongs in project-local knowledge such as `local.md`, an untracked note, or a private Obsidian page. Existing Claude Code sessions may need a restart, plugin reload, or a short manual instruction to apply newly installed guardrails.

## Claude Code Skill Catalog

Use [docs/claude-skills.md](claude-skills.md) when Claude Code should use the
same public-safe reusable skills that were added for Codex.

Recommended portable skills:

- `karpathy-guidelines`
- `hun-engineering-loop`

Install selected skills into `~/.claude/skills`. Do not install every catalog
skill automatically, and do not copy private project skills into this public
repository. `chatgpt-collaboration-harness` requires review before Claude Code
use because it assumes Codex-owned local validation and ChatGPT Pro browser
collaboration.

## Update

Re-run the renderer after pulling new repo changes, then update the plugin in Claude Code.

## Audit

```bash
python3 scripts/audit_agent_stack.py
```

The default audit is offline and read-only. It checks the local Codex CLI, Claude Code CLI, optional OpenCode CLI, Superpowers checkout state, and the Codex skills symlink. Add `--online` only when you explicitly want current npm and remote git drift checks.
