# Skill Catalog

This directory is a browse, review, select, then install catalog for reusable Codex skills.

It is not an always-install bootstrap. Future agents should inspect this catalog, compare a selected skill with the installed runtime copy under `~/.codex/skills`, ask before installing or overwriting, then validate the installed skill.

## Catalog Rules

- The repo copy is the reviewable catalog source.
- The installed copy under `~/.codex/skills/<skill-name>` is the runtime copy used by Codex.
- Do not install every skill automatically.
- Do not copy private paths, credentials, MCP endpoints, auth state, browser profiles, or machine-specific trust settings into tracked files.
- Run the skill validator after installing or syncing a skill.

### chatgpt-collaboration-harness

Use this first when work should be coordinated with ChatGPT Pro across staged implementation, delegated subtasks, Search Mode, deep research, source-backed investigation, or final review.

Key policy:

- Codex owns local files, validation, and final judgment.
- ChatGPT Pro must not answer from inference alone when facts, project source behavior, official docs, rankings, preferences, or public sentiment matter.
- Technical claims should use project source, local evidence, official documentation, primary sources, or source-backed research first.
- Community evidence is allowed for taste, popularity, adoption, or preference questions, but it must be labeled `community-sentiment`, not treated as official fact.
- ChatGPT Pro and Codex summaries are Korean by default unless Hun asks otherwise or the deliverable requires another language.
- Keep one goal, one ChatGPT work tab or conversation, one approved sharing scope, and one validation record per project.

Catalog path: `skills/chatgpt-collaboration-harness`

Runtime install target: `~/.codex/skills/chatgpt-collaboration-harness`

### _template

Use this only as a starting skeleton for future catalog entries. The files are intentionally named with `.template` suffixes so they are not installed as a working skill by accident.

Catalog path: `skills/_template`
