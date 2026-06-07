# Start Work With Vibe Coding Guardrails

Use this prompt when a repository already has guardrails and you want Codex, Claude Code, or another coding agent to work on a specific feature, bug, or refactor.

```text
Work in this repository using the vibe-coding guardrails.

Before implementation, run a pre-write lens:
- read AGENTS.md and any local project knowledge note
- inspect the target module boundaries and dependency direction
- search for existing helpers, types, shapes, public APIs, and tests before creating new ones
- identify edge cases, failure paths, side effects, and concurrency risks
- check whether .audit/ or other local evidence artifacts should remain untracked

Use TDD:
- write the failing test first
- include edge cases before happy-path-only coverage
- keep mocks at external boundaries
- do not mock internal behavior
- run the test and confirm the expected failure before production changes

During implementation:
- make the smallest reasonable change
- avoid silent fallback and swallowed errors
- keep error handling at explicit boundaries
- use guard clauses or early returns instead of unnecessary deep nesting
- do not rewrite or replace existing implementations without explicit approval
- do not commit personal vault paths, credentials, tokens, MCP endpoints, auth state, or machine-specific trust settings

After implementation, run post-write review:
- check for duplicate helpers, duplicate shapes, dead code, commented-out code, hidden coupling, initialization order dependencies, global state, unmanaged re-exports, fan-in/fan-out hotspots, and weak tests
- run the repository's real verification commands
- report exact commands, results, files changed, and remaining risks
```
