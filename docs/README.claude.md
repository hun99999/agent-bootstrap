# Claude Code

This repository supports Claude Code in three layers:

- optionally install Anthropic's official `superpowers` plugin when the user chooses it
- install this repository's `process-first-agents` plugin independently for the shared agent prompts
- optionally install this repository's `frontend-design-pack` for the reviewed frontend router

Claude Superpowers is a separate optional user choice. Ask before installing or updating it; do not
auto-install it. `process-first-agents` can be installed and used without Superpowers.

## Default Scope

Inside Claude Code, the default setup scope is `current-harness-only`.

If the user says "set this up from the repo" and does not explicitly ask for Codex, configure Claude Code only.

Do not configure another harness unless the user explicitly asks.

OpenCode and OpenClaw are not current first-class setup targets for this repository.

## Recommended Setup

1. Ask whether the user wants upstream `superpowers`. Install it from the official Claude
   marketplace only after explicit approval.
2. Clone this repository locally.
3. Run `git status --short --branch` and stop if there is uncommitted or untracked user work.
4. Ask the user what name Claude Code should use. Keep the chosen name local, substitute it for
   `<chosen-name>` below, and do not commit the chosen name or any rendered file containing it.
5. Inspect the active runtime. Keep generated agents at `model: inherit` with no effort pin; use an
   explicit session selection only when the user chooses a model and effort the account supports.
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

Every generated Claude agent uses `model: inherit` and omits `effort`. The main Claude Code session therefore supplies both the model and session effort allowed by the user's account, organization, and provider.

Inspect the active runtime with `claude --help`; use `/model` and `/effort` in Claude Code when the user wants an explicit local choice. Leave the inherited selection in place when account-specific availability cannot be enumerated. Per-agent effort stays unpinned because available levels depend on the selected model.

Start routine work at the inherited or medium session effort when supported, compare a lower level on representative tasks, and raise effort only for a measured quality gain. The repository carries no paid-plan ceiling, and model or reasoning selection remains independent of the optional Superpowers choice.

## Target-Local Skill Mode

Choose one mode for the target: lean catalog skills, full upstream Superpowers, or neither. Lean is
the recommended starting point when prompt cost and workflow latency matter. Inspect current
discovery first, preserve it until the user approves a change, and use the target-supported plugin or
skill controls. Derive any path-specific entry from that target rather than copying another machine's
configuration.

Lean mode installs only selected public-safe catalog skills and keeps the four Superpowers
adaptations explicit-use. Hun may add the compact local wrapper on Hun-owned runtimes. Full mode uses
Anthropic's upstream Superpowers plugin only after approval. `process-first-agents`, model selection,
and session effort remain independent of this choice.

## Optional Runtime Capabilities

Ask separately whether the target should use Basic Memory and whether it should use Computer Use or
browser control. Keep MCP commands, hooks, project mappings, app paths, permissions, auth state, and
browser profiles target-local. The shared plugin must remain usable when either capability is absent.
Follow [portable-runtime-adapters.md](portable-runtime-adapters.md).

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
python3 scripts/audit_agent_stack.py
```

Run the narrowest checks invalidated by the changed renderer, docs, or plugin surface. Run
`python3 -m unittest discover -s tests -p 'test_*.py'` only for broad, cross-cutting, high-risk, or
release-bound updates, or when a focused result reveals wider impact. Reuse an unchanged passing
result instead of repeating it.

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
