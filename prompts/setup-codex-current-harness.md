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
8. Read `docs/frontend-design-stack.md` and validate the tracked plugin with `python3 scripts/validate_frontend_design_stack.py --repo-root .`.
   - Inspect current Codex plugin state and report whether `frontend-design-pack` and Figma are available.
   - Do not authenticate Figma, change accounts, or inspect private Figma files.
   - Ask before installing or replacing `frontend-design-pack` or any runtime copy.
   - If approved, install from the documented marketplace, locate the actual installed root, and validate the runtime copy separately.
   - Start a fresh task for a read-only discovery pressure case.
9. Preserve unrelated Codex state such as credentials, history, logs, and automations.
10. Summarize:
   - chosen partner name
   - model and reasoning inheritance decision for each detected runtime
   - files changed
   - backups created
   - tracked plugin and runtime copy validation results
   - Figma availability without authentication changes
   - anything that still needs manual follow-up
