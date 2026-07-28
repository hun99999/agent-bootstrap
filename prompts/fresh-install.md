You are setting up a fresh Codex environment from this repository.

The repository is the source of truth for a managed subset of `~/.codex`.
Follow these rules exactly:

1. Read `README.md`.
2. Ask the user what name Codex should use to address them.
   - If they have no preference, ask whether the generic name `Partner` is acceptable.
3. Inspect the active Codex and Claude runtimes to determine the models and reasoning levels they actually support.
   - Do not promise or hard-code a particular model, reasoning level, or paid plan.
   - Leave model and reasoning assignments out of shared configuration so each runtime inherits its supported selection and account ceiling.
   - Treat model and reasoning selection independently from the optional Superpowers decision.
   - If support cannot be discovered, ask the user rather than guessing.
   - Do not install or reconfigure a runtime solely to inspect it.
4. Do not commit the chosen partner name or any rendered file containing it. Keep the chosen name only in local runtime output and local backups.
5. Use the repository installer instead of manually editing files unless the installer is broken.
6. Ask whether the user wants the optional manual Codex Superpowers checkout.
   - Do not install or update it automatically.
   - The installer default is `skip`; use `--superpowers-mode manual` only after explicit opt-in.
   - `skip` is non-mutating: it does not deactivate, disable, or remove an existing checkout,
     symlink, or curated discovery.
   - Model and reasoning selection is independent of the Superpowers choice.
   - Warn that enabling both curated and manual discovery can create duplicate skill entries.
7. Run `bash scripts/install.sh --partner-name "<chosen-name>"` for the default `skip` choice.
   - If manual mode was approved, add the exact flag `--superpowers-mode manual`.
8. Read `docs/frontend-design-stack.md` and validate the tracked plugin with `python3 scripts/validate_frontend_design_stack.py --repo-root .`.
   - Inspect current Codex plugin state and report whether `frontend-design-pack` and Figma are available.
   - Do not authenticate Figma, change accounts, or inspect private Figma files.
   - Ask before installing or replacing `frontend-design-pack` or any other runtime copy.
   - If approved, use the documented marketplace/plugin commands, locate the actual installed root, and validate the runtime copy separately.
   - Start a fresh task to prove skill discovery; static validation in the installation task is not discovery evidence.
9. Do not modify or delete unrelated `~/.codex` state such as credentials, history, logs, or automations.
10. If the installer fails, inspect `.codex/install.py`, diagnose the actual cause, and fix the smallest reasonable issue before retrying.
11. Summarize:
   - chosen partner name
   - model and reasoning inheritance decision for each detected runtime
   - backup location reported by the installer
   - installed files
   - tracked plugin and runtime copy validation results
   - Figma availability without authentication changes
   - selected Superpowers mode and whether existing discovery was preserved
   - only when manual mode was approved, the Superpowers remote, path, and synced commit
   - anything skipped or requiring manual follow-up

If any required repo file is missing or malformed, stop and report the issue instead of guessing.
