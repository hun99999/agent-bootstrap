This is a legacy OpenClaw ACP integration prompt.

Do not use it for normal setup. Codex and Claude Code are the current
first-class setup targets for this repository.

Use this mode only if Hun explicitly asks for ACP integration.

You must ask the user which harness to connect before proceeding if that is not
already explicit.

Follow these rules exactly:

1. Read `README.md` and `docs/README.openclaw.md`.
2. Run `git status --short --branch`.
3. Stop if there is uncommitted or untracked user work.
4. Ask the user which harness to connect before changing anything if that is not already explicit.
5. Confirm the harness choice before changing anything if it is not already explicit.
6. Apply ACP integration only within the requested scope.
7. Do not modify unrelated OpenClaw settings such as identity, gateway, transport, auth, provider config, or messaging integrations.
8. Back up ACP-related config before editing it.
9. If the user did not explicitly ask for ACP, stop and route them to Codex or Claude Code setup instead.
10. Summarize:
   - chosen harness
   - ACP integration changes
   - backup locations
   - anything that still needs manual validation

This path is for ACP integration only if the user explicitly asks for ACP.
