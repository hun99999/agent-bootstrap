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

```bash
bash .codex/install.sh --partner-name "Hun"
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
bash .codex/install.sh --partner-name "Hun"
```

## Audit

```bash
python3 scripts/audit_agent_stack.py
```

The default audit is offline and read-only. It checks the local Codex CLI, Claude Code CLI, the `~/.codex/superpowers` checkout, the `~/.agents/skills/superpowers` symlink, and the generated Claude plugin bundle. Use `--online` only when you want current npm and remote git drift checks.

## Profiles

The default Codex profile prioritizes quality with `gpt-5.5` and high reasoning settings. The `balanced` profile keeps `gpt-5.5` but uses medium reasoning and verbosity for lower-latency work. The `previous` profile pins the immediately previous supported model, `gpt-5.4`.
