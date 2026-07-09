# Installing agent-bootstrap for Codex

This adapter installs the shared process-first prompt corpus into Codex and wires Codex up to upstream `obra/superpowers` using native skill discovery.

## What It Installs

- `~/.codex/AGENTS.md`
- `~/.codex/local.md`
- `~/.codex/config.toml`
- `~/.codex/agents/*.md`
- `~/.codex/superpowers`
- `~/.agents/skills/superpowers` symlinked to `~/.codex/superpowers/skills`

Codex App can use the Codex App curated Superpowers plugin; this installer still supports the manual ~/.codex/superpowers fallback for local skill discovery. Avoid enabling both discovery paths unless duplicate skill entries are intentional.

## Installation

Ask the user what name Codex should use, then keep that chosen value local. Substitute it for
`<chosen-name>`; do not commit it as a public default.

```bash
bash .codex/install.sh --partner-name "<chosen-name>"
```

If you want custom locations:

```bash
bash .codex/install.sh \
  --partner-name "<chosen-name>" \
  --codex-home "/absolute/path/to/.codex" \
  --agents-home "/absolute/path/to/.agents"
```

## Verify

```bash
ls -la ~/.agents/skills/superpowers
```

You should see a symlink pointing at `~/.codex/superpowers/skills`.

## Updating

Re-run the installer after pulling the latest repo changes:

```bash
git pull
bash .codex/install.sh --partner-name "<chosen-name>"
```

## Frontend Design Pack

`frontend-design-pack` is distributed as a plugin, not by this core installer. Validate the tracked
plugin and ask before installing or replacing its runtime copy. Follow
[the frontend design stack guide](../docs/frontend-design-stack.md) for Codex marketplace commands,
separate runtime validation, Figma availability reporting without authentication, and the required
fresh task after installation.

The shared templates carry no model or reasoning pin. Inspect the active runtime and inherit the
models and reasoning levels the user's account and organization actually support.
