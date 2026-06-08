# Apply Vibe Coding Guardrails

Use this prompt when you give a repository to Codex, Claude Code, or another coding agent and want it to set up the guardrails from this repository.

```text
Apply the vibe-coding guardrails from agent-bootstrap to this repository.

First, read AGENTS.md if it exists. Then read docs/vibe-coding-guardrails.md, docs/global-guardrail-setup.md, and docs/local-project-knowledge-template.md from agent-bootstrap.

Before changing files:
- check git status
- identify uncommitted or untracked user work
- inspect existing docs, tests, lint, type checks, and dependency tooling
- identify module boundaries, existing helpers, types, shapes, public APIs, re-exports, and error boundaries
- inventory optional tools that may matter for this repo, including Obsidian, Lumin Repo Lens, dependency lint, strict type checks, cycle detection, and complexity limits
- if Lumin Repo Lens is installed or approved for a TS/JS repo, read .audit/manifest.json first when it exists and treat scan range, skipped lanes, and confidence as part of every structural claim
- do not claim that a helper, shape, public API, cycle, or consumer does not exist unless you state the scan range; say "not observed in this scan range" when the evidence is partial
- do not invent tool commands, config options, package names, or API details

Set up only the smallest useful guardrails for this repository:
- add .audit/ to .gitignore if local evidence artifacts may be created
- add or update local project knowledge guidance without committing private paths
- document the pre-write lens, write gate, and post-write review loop for this repo
- include a structural evidence index that points to shareable audit docs, .audit artifact names, source-of-truth docs, and any private wiki or Obsidian page type without committing personal vault paths
- keep optional tools such as Lumin Repo Lens optional unless this repo already uses TS/JS and I explicitly approve installing it
- for Obsidian or any other optional desktop app, plugin, CLI, browser extension, or package dependency, explain whether it is required, recommended, optional, or skipped
- ask before installing optional tools; do not install them only because a guide mentions them
- on macOS, verify the package name or official source before installing; on Windows PowerShell, use commands such as winget search Obsidian to verify the package name before installation
- do not commit personal vault paths, credentials, tokens, MCP endpoints, auth state, or machine-specific trust settings

When documenting the daily workflow:
- make pre-write intent explicit with names, shapes, files, dependencies, and plannedTypeEscapes
- require the agent to read the invocation-specific pre-write advisory before editing when one is produced
- require post-write delta review against the same advisory after editing
- check Lumin machine evidence for `silent-new` type escapes, planned-not-observed type escapes, unexpected new files, and degraded scan confidence
- check duplicate helpers, changed dependencies, public API drift, and re-export drift as manual post-write review claims backed by direct evidence

Use TDD for any behavior changes. Tests must cover edge cases, failure paths, and side effects. Mocks belong at external boundaries only; do not mock internal implementation details.

After setup:
- run the repository's real verification commands
- run post-write review for duplicate helpers, hidden coupling, swallowed errors, unmanaged re-exports, fan-in/fan-out hotspots, and weak tests
- commit in small, reviewable commits
- summarize the evidence, commands run, files changed, and remaining risks
```
