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
- syncs the latest upstream `obra/superpowers` into `~/.codex/superpowers`
- creates `~/.agents/skills/superpowers` as a symlink to `~/.codex/superpowers/skills`

These user-level defaults are the global layer. Project-specific structure still belongs in project-local knowledge such as `local.md`, an untracked note, or a private Obsidian page. New Codex sessions should pick up the installed defaults; existing sessions may need a restart or a short manual instruction to apply the new guardrails.

Codex App can use the Codex App curated Superpowers plugin; the installer still supports the manual ~/.codex/superpowers fallback for local skill discovery. Avoid enabling both discovery paths unless duplicate skill entries are intentional.

## Re-run

```bash
git pull
bash .codex/install.sh --partner-name "<chosen-name>"
```

## Audit

```bash
python3 scripts/audit_agent_stack.py
```

The default audit is offline and read-only. It checks the local Codex CLI, Claude Code CLI, the `~/.codex/superpowers` checkout, the `~/.agents/skills/superpowers` symlink, and the generated Claude plugin bundle. Use `--online` only when you want current npm and remote git drift checks.

## Models And Reasoning

The public Codex templates do not pin a model, reasoning level, verbosity, or paid-plan ceiling.
Inspect what the active Codex and Claude runtimes actually support, report the result, and let each
runtime inherit its available selection. If the supported ceiling cannot be discovered, ask instead
of guessing.

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
