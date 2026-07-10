You are setting this repository up inside Claude Code in `current-harness-only` mode.

Read `README.md`, `docs/README.claude.md`, `docs/claude-skills.md`, and
`docs/frontend-design-stack.md` first.

Follow these rules exactly:

1. Default to `current-harness-only`.
2. Ask the user what name Claude Code should use to address them.
   - If they have no preference, ask whether the generic name `Partner` is acceptable.
   - Keep the chosen name local and substitute it for `<chosen-name>`; do not commit the chosen
     name or any rendered file containing it.
3. Inspect the active Claude Code runtime and inherit only the models and reasoning levels the
   user's account and organization actually support. Do not hard-code a latest model or paid plan.
4. Configure Claude Code only.
5. Do not configure another harness unless the user explicitly asks.
6. Install or update the Claude-side `superpowers` and shared agent/subagent prompts using
   `--partner-name "<chosen-name>"` when rendering.
7. Review public-safe skills before installing anything into `~/.claude/skills`.
8. Install only user-approved selected skills; do not auto-install the full catalog.
9. Validate the tracked frontend design plugin with
   `python3 scripts/validate_frontend_design_stack.py --repo-root .`.
   - Inspect current Claude plugin state and report whether `frontend-design-pack` and Figma are
     available without authenticating Figma, changing accounts, or opening private files.
   - Ask before installing or replacing any runtime copy.
   - If approved, follow `docs/frontend-design-stack.md`, locate the actual installed root, and
     validate it separately with `--claude-runtime-root`.
   - Start a fresh Claude Code session and run a read-only discovery check before claiming that the
     skill or any approved companion skill is available.
10. Preserve unrelated Claude Code state.
11. Summarize:
   - chosen partner name
   - model and reasoning inheritance decision
   - files changed
   - backups created
   - selected skills installed or skipped
   - tracked plugin and installed runtime validation
   - Figma availability without authentication changes
   - anything that still needs manual follow-up
