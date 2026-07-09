You are setting this repository up inside Codex in `current-harness-only` mode.

Read `README.md` and `docs/README.codex.md` first.

Follow these rules exactly:

1. Default to `current-harness-only`.
2. Ask the user what name Codex should use to address them.
   - If they have no preference, ask whether the generic name `Partner` is acceptable.
3. Inspect the active Codex and Claude runtimes to determine the models and reasoning levels they actually support.
   - Do not promise or hard-code a particular model, reasoning level, or paid plan.
   - Leave model and reasoning assignments out of shared configuration so each runtime inherits its supported selection and account ceiling.
   - If support cannot be discovered, ask the user rather than guessing.
   - Do not install or reconfigure a runtime solely to inspect it.
4. Configure Codex only.
5. Do not configure another harness unless the user explicitly asks.
6. Do not commit the chosen partner name or any rendered file containing it. Keep the chosen name only in local runtime output and local backups.
7. Install or update the Codex-side `superpowers` and shared agent/subagent prompts.
8. Preserve unrelated Codex state such as credentials, history, logs, and automations.
9. Summarize:
   - chosen partner name
   - model and reasoning inheritance decision for each detected runtime
   - files changed
   - backups created
   - anything that still needs manual follow-up
