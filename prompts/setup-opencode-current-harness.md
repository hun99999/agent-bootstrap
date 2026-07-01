This is a legacy OpenCode prompt.

Do not use it for normal setup. Codex and Claude Code are the current
first-class setup targets for this repository.

Proceed only if Hun explicitly asked for OpenCode legacy migration or
restoration work.

If that explicit request exists:

1. Read `README.md`, `docs/README.opencode.md`, and `.opencode/INSTALL.md`.
2. Run `git status --short --branch`.
3. Stop if there is uncommitted or untracked user work.
4. Confirm the scope is OpenCode legacy work only.
5. Preserve unrelated OpenCode, Codex, and Claude Code state.
6. Run the relevant legacy tests.
7. Summarize:
   - files changed
   - tests run
   - anything that still needs manual follow-up

If the explicit legacy request does not exist, stop and route the user to
`docs/README.codex.md` or `docs/README.claude.md`.
