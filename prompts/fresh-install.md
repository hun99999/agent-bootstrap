You are setting up a fresh Codex environment from this repository.

The repository is the source of truth for a managed subset of `~/.codex`.
Follow these rules exactly:

1. Read `README.md`.
2. Ask the user what name Codex should use to address them.
   - If they have no preference, ask whether the generic name `Partner` is acceptable.
3. Inspect the active Codex and Claude runtimes to determine the models and reasoning levels they actually support.
   - Do not promise or hard-code a particular model, reasoning level, or paid plan.
   - Leave model and reasoning assignments out of shared configuration so each runtime inherits its supported selection and account ceiling.
   - If support cannot be discovered, ask the user rather than guessing.
   - Do not install or reconfigure a runtime solely to inspect it.
4. Do not commit the chosen partner name or any rendered file containing it. Keep the chosen name only in local runtime output and local backups.
5. Use the repository installer instead of manually editing files unless the installer is broken.
6. Run:
   - `bash scripts/install.sh --partner-name "<chosen-name>"`
7. This install must set up both:
   - the managed subagent configuration under `~/.codex`
   - the latest `~/.codex/superpowers` checkout
8. Do not modify or delete unrelated `~/.codex` state such as credentials, history, logs, or automations.
9. If the installer fails, inspect `.codex/install.py`, diagnose the actual cause, and fix the smallest reasonable issue before retrying.
10. Summarize:
   - chosen partner name
   - model and reasoning inheritance decision for each detected runtime
   - backup location reported by the installer
   - installed files
   - superpowers remote, path, and synced commit
   - anything skipped or requiring manual follow-up

If any required repo file is missing or malformed, stop and report the issue instead of guessing.
