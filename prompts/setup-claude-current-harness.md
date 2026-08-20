You are setting this repository up inside Claude Code in `current-harness-only` mode.

Read `README.md`, `docs/README.claude.md`, `docs/claude-skills.md`, and
`docs/frontend-design-stack.md` first.

Follow these rules exactly:

1. Default to `current-harness-only`.
2. Ask the user what name Claude Code should use to address them.
   - If they have no preference, ask whether the generic name `Partner` is acceptable.
   - Keep the chosen name local and substitute it for `<chosen-name>`; do not commit the chosen
     name or any rendered file containing it.
3. Inspect the active Claude Code runtime with `claude --help` and retain `model: inherit` with no
   per-agent `effort` pin. Use `/model` or `/effort` only when the user chooses a selection the
   active account and model support. When availability cannot be enumerated, retain session
   inheritance and report it.
4. Configure Claude Code only.
5. Do not configure another harness unless the user explicitly asks.
6. Render and install or update the shared `process-first-agents` prompts using
   `--partner-name "<chosen-name>"`.
7. Resolve one target-local skill mode with the user: lean catalog skills, full upstream
   Superpowers, or neither.
   - Recommend lean catalog skills when lower prompt and workflow overhead is the goal.
   - Inspect current skill and plugin discovery before changing it. Use the target-supported plugin
     or skill controls, and derive any path-specific entry from this target.
   - In lean mode, install only approved catalog skills; keep the four Superpowers adaptations
     explicit-use and keep the full upstream plugin unchanged until the user approves a change.
   - In full upstream mode, separately ask whether the user wants the optional upstream Claude
     Superpowers plugin.
   - Do not install or update Superpowers automatically.
   - Install it through the official Claude marketplace only after explicit user approval.
   - `process-first-agents` is separate from Superpowers and remains usable without Superpowers.
7a. Ask separately whether the user wants Basic Memory and whether the user wants Computer Use or
    browser control.
   - Do not install or enable either capability before its own approval.
   - Keep MCP commands, hooks, project mappings, app paths, permissions, auth state, and browser
     profiles target-local.
   - `process-first-agents` and selected skills must work when either capability is absent.
8. Review public-safe skills before installing anything into `~/.claude/skills`.
9. Install only user-approved selected skills; do not auto-install the full catalog.
10. Validate the tracked frontend design plugin with
   `python3 scripts/validate_frontend_design_stack.py --repo-root .`.
   - Inspect current Claude plugin state and report whether `frontend-design-pack` and Figma are
     available without authenticating Figma, changing accounts, or opening private files.
   - Ask before installing or replacing any runtime copy.
   - If approved, follow `docs/frontend-design-stack.md`, locate the actual installed root, and
     validate it separately with `--claude-runtime-root`.
   - Start a fresh Claude Code session and run a read-only discovery check before claiming that the
     skill or any approved companion skill is available.
11. Preserve unrelated Claude Code state.
12. Summarize:
   - chosen partner name
   - inherited or explicitly selected Claude model and session effort
   - files changed
   - backups created
   - selected skills installed or skipped
   - selected target-local skill mode and whether upstream Superpowers was approved, declined, or
     left unchanged
   - tracked plugin and installed runtime validation
   - Figma availability without authentication changes
   - anything that still needs manual follow-up
