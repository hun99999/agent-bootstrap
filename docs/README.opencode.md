# OpenCode

OpenCode uses a local installer because the baseline needs user-specific prompt rendering while still relying on upstream `obra/superpowers` through OpenCode's native plugin support.

## Default Scope

Inside OpenCode, the default setup scope is `current-harness-only`.

If the user says "set this up from the repo" and does not explicitly ask for Codex, Claude Code, OpenClaw ACP, or cross-harness setup, configure OpenCode only.

Do not configure another harness unless the user explicitly asks.

## Install

```bash
bash .opencode/install.sh --partner-name "Hun"
```

## What It Does

- writes `~/.config/opencode/opencode.json`
- enables the upstream plugin line `superpowers@git+https://github.com/obra/superpowers.git`
- renders the shared constitution plus each role body into `~/.config/opencode/agents/*.md`
- marks review-only agents as read-only where appropriate

## Re-run

```bash
git pull
bash .opencode/install.sh --partner-name "Hun"
```

## Audit

```bash
python3 scripts/audit_agent_stack.py
```

The default audit is offline and read-only. OpenCode is optional by default because this repository can be used from Codex or Claude Code sessions too. Add `--strict` when a missing OpenCode CLI should fail the audit, and add `--online` when you explicitly want remote drift checks.
