# Claude Code

This repository supports Claude Code in three layers:

- install Anthropic's official `superpowers` plugin for the skills library
- install this repository's `process-first-agents` plugin for the shared agent prompts
- optionally install this repository's `frontend-design-pack` for the reviewed frontend router

## Default Scope

Inside Claude Code, the default setup scope is `current-harness-only`.

If the user says "set this up from the repo" and does not explicitly ask for Codex, configure Claude Code only.

Do not configure another harness unless the user explicitly asks.

OpenCode and OpenClaw are not current first-class setup targets for this repository.

## Recommended Setup

1. Install upstream `superpowers` from the official Claude marketplace.
2. Clone this repository locally.
3. Run `git status --short --branch` and stop if there is uncommitted or untracked user work.
4. Ask the user what name Claude Code should use. Keep the chosen name local, substitute it for
   `<chosen-name>` below, and do not commit the chosen name or any rendered file containing it.
5. Inspect the active runtime and inherit the models and reasoning levels the user's account and
   organization actually support. Do not hard-code a latest model or paid-plan ceiling.
6. Render the Claude plugin bundle with the chosen partner name.
7. Add the local repository as a Claude plugin marketplace.
8. Install `process-first-agents` from that marketplace.
9. Optionally review and install only the public Claude Code skill set into `~/.claude/skills`.
10. Validate and offer `frontend-design-pack` separately; install it only after approval.

## Render the Plugin Bundle

```bash
python3 scripts/render_claude_plugin.py --partner-name "<chosen-name>"
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

## Models And Reasoning

The public templates carry no model, reasoning, verbosity, or paid-plan pin. Inspect the current
Claude Code runtime and let it inherit the supported selection and organization ceiling. If the
available ceiling cannot be discovered, ask the user instead of guessing.

## Frontend Design Pack

Read `docs/frontend-design-stack.md` and validate the tracked source before changing runtime state:

```bash
python3 scripts/validate_frontend_design_stack.py --repo-root .
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate plugins/frontend-design-pack
claude plugin marketplace list
claude plugin list --json
```

Report whether `frontend-design-pack` and Figma are available. Do not authenticate Figma, change
accounts, or inspect private Figma files. Ask before adding the marketplace, installing the plugin,
or replacing an installed runtime copy.

After approval, use the exact commands and Vercel companion-skill boundary documented in
[frontend-design-stack.md](frontend-design-stack.md). Read `installPath` from
`claude plugin list --json` to resolve the live runtime root rather than guessing its cache path,
then validate that root separately:

```bash
python3 scripts/validate_frontend_design_stack.py \
  --repo-root . \
  --claude-runtime-root "<installed-frontend-design-pack-root>"
```

Start a fresh Claude Code session and run a read-only `frontend-design` request before claiming
runtime discovery. Static validation in the installation session is not discovery evidence.

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
python3 scripts/render_claude_plugin.py --partner-name "<chosen-name>"
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/audit_agent_stack.py
```

Then read `docs/frontend-design-stack.md`. If its tracked source or generated plugin changed, run
`python3 scripts/validate_frontend_design_stack.py --repo-root .`, inspect the installed runtime,
ask before replacing it, validate the installed root separately, and use a fresh Claude Code
session to verify discovery. Do not update every global companion skill as a side effect.

## Audit

```bash
python3 scripts/audit_agent_stack.py
```

The default audit is offline and read-only. It checks the local Codex CLI,
Claude Code CLI, Superpowers checkout state, the Codex skills symlink, and the
generated Claude plugin bundle. Add `--online` only when you explicitly want
current npm and remote git drift checks.
