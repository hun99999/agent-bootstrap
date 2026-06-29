You are setting this repository up inside Claude Code in `current-harness-only` mode.

Read `README.md`, `docs/README.claude.md`, and `docs/claude-skills.md` first.

Follow these rules exactly:

1. Default to `current-harness-only`.
2. Configure Claude Code only.
3. Do not configure another harness unless the user explicitly asks.
4. Install or update the Claude-side `superpowers` and shared agent/subagent prompts.
5. Review public-safe skills before installing anything into `~/.claude/skills`.
6. Install only Hun-approved selected skills such as `karpathy-guidelines` or `hun-engineering-loop`; do not auto-install the full catalog.
7. Preserve unrelated Claude Code state.
8. Summarize:
   - files changed
   - backups created
   - selected skills installed or skipped
   - anything that still needs manual follow-up
