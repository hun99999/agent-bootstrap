# Codex

Codex uses a local installer because the baseline needs two things that are user-specific:

- your partner name
- the local `~/.codex` and `~/.agents` paths

## Default Scope

Inside Codex, the default setup scope is `current-harness-only`.

If the user says "set this up from the repo" and does not explicitly ask for Claude Code, OpenCode, OpenClaw ACP, or cross-harness setup, configure Codex only.

Do not configure another harness unless the user explicitly asks.

Codex session opener for standing delegation preference:

```text
In this session, you may use sub-agents or parallel agents for independently separable work when that clearly improves efficiency. This is permission, not a requirement: if the work is small, tightly coupled, immediately blocking, or the delegation overhead is not worth it, stay local instead.
```

## Install

```bash
bash .codex/install.sh --partner-name "Hun"
```

## What It Does

- renders `AGENTS.md`, `local.md`, `config.toml`, and `agents/*.md` into `~/.codex`
- syncs the latest upstream `obra/superpowers` into `~/.codex/superpowers`
- creates `~/.agents/skills/superpowers` as a symlink to `~/.codex/superpowers/skills`

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

The default audit is offline and read-only. It checks the local Codex CLI, Claude Code CLI, optional OpenCode CLI, the `~/.codex/superpowers` checkout, and the `~/.agents/skills/superpowers` symlink. Use `--online` only when you want current npm and remote git drift checks.

## Profiles

The default Codex profile prioritizes quality with `gpt-5.5` and high reasoning settings. The `balanced` profile keeps `gpt-5.5` but uses medium reasoning and verbosity for lower-latency work. The `previous` profile pins the immediately previous supported model, `gpt-5.4`.
