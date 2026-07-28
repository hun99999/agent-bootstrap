You are setting this repository up in `shared-core-only` mode.

Read `README.md` first.

Follow these rules exactly:

1. If the user says "set this up from the repo" and does not specify a harness, default to `shared-core-only`.
2. `shared-core-only` means:
   - install the shared constitution and agent/subagent prompts in the current tool's native format
   - separately ask whether the user wants optional Superpowers support; do not install or update it automatically
   - avoid unrelated runtime reconfiguration
3. Apply the Superpowers choice only to a harness the user selected:
   - For Codex, the default is `skip`; use `--superpowers-mode manual` only after explicit opt-in.
   - Codex `skip` is non-mutating and does not deactivate, disable, or remove an existing checkout,
     symlink, or curated discovery.
   - Warn that combining Codex curated and manual discovery can create duplicate skill entries.
   - For Claude Code, Superpowers is separate from `process-first-agents`; shared prompts work
     without Superpowers.
   - Model and reasoning selection is independent of the Superpowers choice.
4. Do not choose a harness unless the user explicitly asks for one.
5. Do not redesign ACP, gateway, transport, auth, identity, or provider settings unless the user explicitly asks.
6. Back up or preserve any existing prompt or skills files that will be replaced.
7. Summarize:
   - scope used
   - files backed up
   - files changed
   - Superpowers choice and any explicitly approved action
   - anything skipped because the current tool cannot consume it natively

If the repository does not provide a native path for the current tool, stop and say so instead of inventing one.
