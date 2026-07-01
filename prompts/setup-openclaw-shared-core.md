This is a legacy OpenClaw shared-core prompt.

Do not use it for normal setup. Codex and Claude Code are the current
first-class setup targets for this repository.

Proceed only if Hun explicitly asked for OpenClaw legacy shared-core migration
or restoration work.

If that explicit request exists:

1. Read `README.md` and `docs/README.openclaw.md`.
2. Run `git status --short --branch`.
3. Stop if there is uncommitted or untracked user work.
4. Apply only the approved shared prompt/skill layer.
5. Do not choose Codex-first, Claude-first, or OpenCode-first.
6. Do not modify unrelated OpenClaw settings such as identity, gateway, transport, auth, provider config, or messaging integrations.
7. Do not touch ACP settings unless the user explicitly asks for ACP integration.
8. Summarize:
   - backup locations
   - prompt/skill files changed
   - anything that requires a manual follow-up

If you cannot map the repository's shared core into the current OpenClaw
environment confidently, stop and explain what is missing.
