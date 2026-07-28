# Installing agent-bootstrap for Codex

This adapter installs the shared process-first prompt corpus into Codex. Upstream
`obra/superpowers` support is a separate optional choice.

## What It Installs

- `~/.codex/AGENTS.md`
- `~/.codex/local.md`
- `~/.codex/config.toml`
- `~/.codex/agents/*.md`

Superpowers is optional and opt-in. The installer default is `skip`; use
`--superpowers-mode manual` only after the user chooses the manual checkout. `skip` is non-mutating:
it does not deactivate, disable, or remove an existing checkout, symlink, or curated discovery.
Model and reasoning selection is independent of the Superpowers choice. Codex can use the
Codex App curated Superpowers plugin; this installer still supports the
manual ~/.codex/superpowers fallback for local skill discovery. Avoid enabling both discovery paths
unless duplicate skill entries are intentional.

When manual mode is selected, the installer also manages:

- `~/.codex/superpowers`
- `~/.agents/skills/superpowers` symlinked to `~/.codex/superpowers/skills`

## Installation

Ask the user what name Codex should use, then keep that chosen value local. Substitute it for
`<chosen-name>`; do not commit it as a public default.

```bash
bash .codex/install.sh --partner-name "<chosen-name>"
```

That command keeps the default `skip` mode. After explicit opt-in to the manual fallback, use:

```bash
bash .codex/install.sh \
  --partner-name "<chosen-name>" \
  --superpowers-mode manual
```

If you want custom locations:

```bash
bash .codex/install.sh \
  --partner-name "<chosen-name>" \
  --codex-home "/absolute/path/to/.codex" \
  --agents-home "/absolute/path/to/.agents"
```

## Verify

For the default `skip` choice, verify that the installer left any existing Superpowers discovery
unchanged. If manual mode was explicitly selected, verify:

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

The re-run also defaults to `skip`. Add `--superpowers-mode manual` only when the user still wants
the manual checkout updated.

## Frontend Design Pack

`frontend-design-pack` is distributed as a plugin, not by this core installer. Validate the tracked
plugin and ask before installing or replacing its runtime copy. Follow
[the frontend design stack guide](../docs/frontend-design-stack.md) for Codex marketplace commands,
separate runtime validation, Figma availability reporting without authentication, and the required
fresh task after installation.

The shared templates carry no model or reasoning pin. Inspect the active runtime and inherit the
models and reasoning levels the user's account and organization actually support. This selection is
independent of the optional Superpowers mode.
