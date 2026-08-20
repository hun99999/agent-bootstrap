# Codex

Codex uses a local installer because the baseline needs two things that are user-specific:

- your partner name
- the local `~/.codex` and `~/.agents` paths

## Default Scope

Inside Codex, the default setup scope is `current-harness-only`.

If the user says "set this up from the repo" and does not explicitly ask for Claude Code, configure Codex only.

Do not configure another harness unless the user explicitly asks.

OpenCode and OpenClaw are legacy/reference material, not current first-class setup targets for this repository.

Codex session opener for standing delegation preference:

```text
In this session, you may use sub-agents or parallel agents for independently separable work when that clearly improves efficiency. This is permission, not a requirement: if the work is small, tightly coupled, immediately blocking, or the delegation overhead is not worth it, stay local instead.
```

## Install

Ask the user what name Codex should use before rendering. Keep that choice local and substitute it
for `<chosen-name>` below; do not commit the rendered name.

```bash
bash .codex/install.sh --partner-name "<chosen-name>"
```

This is a global Codex setup for the current user. It writes user-level defaults under `~/.codex`, so new Codex sessions in any project can inherit the shared constitution, role agents, and vibe-coding guardrails.

## What It Does

- renders `AGENTS.md`, `local.md`, `config.toml`, and `agents/*.md` into `~/.codex`
- when the user explicitly selects `--superpowers-mode manual`, syncs upstream
  `obra/superpowers` into `~/.codex/superpowers`
- in that manual mode, creates `~/.agents/skills/superpowers` as a symlink to
  `~/.codex/superpowers/skills`

These user-level defaults are the global layer. Project-specific structure still belongs in project-local knowledge such as `local.md`, an untracked note, or a private Obsidian page. New Codex sessions should pick up the installed defaults; existing sessions may need a restart or a short manual instruction to apply the new guardrails.

Superpowers is optional and opt-in. The installer default is `skip`; use
`--superpowers-mode manual` only after the user chooses the manual checkout. `skip` is non-mutating:
it does not deactivate, disable, or remove an existing checkout, symlink, or curated discovery.
Model and reasoning selection is independent of the Superpowers choice. Codex can use the
Codex App curated Superpowers plugin; the installer still supports the
manual ~/.codex/superpowers fallback for local skill discovery. Avoid enabling both discovery paths
unless duplicate skill entries are intentional.

## Re-run

```bash
git pull
bash .codex/install.sh --partner-name "<chosen-name>"
```

The bare command preserves the default `skip` choice. Add `--superpowers-mode manual` only after the
user explicitly opts in to installing or updating the manual fallback.

## Audit

```bash
python3 scripts/audit_agent_stack.py
```

The default audit is offline and read-only. It checks the local Codex CLI, Claude Code CLI, the `~/.codex/superpowers` checkout, the `~/.agents/skills/superpowers` symlink, and the generated Claude plugin bundle. Use `--online` only when you want current npm and remote git drift checks.

## Models And Reasoning

The public Codex templates carry no model or effort pin.

- **Existing Codex target:** the installer preserves top-level model, `model_reasoning_effort`, summary, verbosity, plan effort, named profiles, runtime-managed tables, unrecognized future settings, and per-role effort overrides. Managed agent definitions and the shared feature baseline still update from the repository.
- **Fresh Codex target:** the installer writes no model or effort pin, so the target runtime and account choose their supported defaults.
- **Explicit local choice:** set a model or effort only after the target runtime confirms support. Keep the choice in the target's local config rather than the public template.

For Hun's current runtime, routine root and coordination work use medium effort with concise reasoning summaries and medium response verbosity. Specialist roles may use more effort where the task shape warrants it. These are machine-local selections, not repository defaults.

Use medium as the balanced starting point and compare one lower level on representative tasks. Raise effort only when a repeated quality gain justifies the added tokens and latency. This policy is independent of the optional Superpowers mode.

## Target-Local Skill Mode

Choose one mode for the target: lean catalog skills, full upstream Superpowers, or neither. Lean is
the recommended starting point when prompt cost and workflow latency matter. Inspect current
discovery first, preserve it until the user approves a change, and use only the target-supported
plugin or skill controls. Derive every path-specific skill entry from that target; another machine's
plugin cache path and version are not portable configuration.

Lean mode installs only selected catalog skills. `karpathy-guidelines` is the public base;
`hun-engineering-loop` is Hun-local. The four Superpowers adaptations remain explicit-use. Full mode
may use the curated plugin or the optional manual checkout after approval; running both can create
duplicate discovery. Model and reasoning policy remains independent of this choice.

Codex `skills.config` entries are target-local and identify the current skill folder. Curated plugin
cache versions can change, so resolve the current discovered Superpowers directories again after a
plugin update. Do not copy another machine's versioned cache paths into config. Start a fresh task
after changing skill enablement and verify discovery once.

## Optional Runtime Capabilities

Ask separately whether the target should use Basic Memory and whether it should use Computer Use or
browser control. These decisions are independent from core installation and skill mode. Do not copy
MCP executable paths, hooks, project mappings, app paths, permissions, auth state, or browser
profiles from another machine. Follow [portable-runtime-adapters.md](portable-runtime-adapters.md).

## Frontend Design Pack

The reviewed `frontend-design-pack` is an optional runtime install, separate from the core Codex
installer. It provides one native `frontend-design` router backed by reviewed MengTo procedures,
official Vercel guidance, Google DESIGN.md contract metadata, and labeled third-party DESIGN.md
inspiration.

Read [frontend-design-stack.md](../docs/frontend-design-stack.md) for tracked validation, approval-gated
installation, runtime-copy validation, update/rollback, Figma boundaries, and fresh-task discovery.
Do not install or replace the plugin merely because the repository contains it.

## Figma

Report whether the official Figma integration is available in current plugin/tool state. Do not
authenticate Figma, change accounts, or inspect private Figma files without separate approval.
