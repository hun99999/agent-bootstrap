# Vibe Coding Guardrails

Use this guide when you want an AI coding session to improve a repository without repeating helpers, hiding coupling, over-mocking tests, swallowing errors, or leaving structure drift behind.

This repository is the public baseline. It should teach the workflow and provide reusable prompts. Project-specific knowledge belongs in a local overlay such as `local.md`, an untracked note, or an Obsidian page selected by the person doing the work.

## What This Solves

AI agents do not reliably keep continuous memory across sessions. Without a persistent structure map, they often recreate helpers, invent new types or shapes, miss existing public APIs, write shallow tests, and patch symptoms with defensive fallbacks.

The fix is not one huge prompt. The fix is a repeatable operating loop:

1. Gather evidence before writing.
2. Change code under a narrow write gate.
3. Review the result for structure drift after writing.

The loop should be boring. Boring is good here.

## Applied Checklist Mapping

This section maps the original vibe-coding problem checklist to concrete artifacts in this repository.

| Original issue or fix | Repository application |
| --- | --- |
| agent memory is not continuous | `docs/agent-setup-playbook.md` and `docs/local-project-knowledge-template.md` tell agents to build persistent project maps instead of rediscovering helpers, types, shapes, commands, and boundaries every session. |
| hidden coupling | `AGENTS.md`, this guide, and role prompts require pre-write checks for module boundaries, dependency direction, hidden imports, initialization order, global state, and side effects. |
| weak tests | `AGENTS.md` requires TDD; this guide requires behavior, failure-path, edge-case, and side-effect tests instead of string-only checks. |
| edge cases | The write gate requires empty input, null or missing values, boundary values, failure paths, side effects, and concurrency checks when relevant. |
| deep nesting | `AGENTS.md` tells agents to use guard clauses or early returns when nesting grows past two or three levels. |
| god functions | This guide tells agents to avoid god functions and god files, and the post-write review checks whether responsibility concentrated in one file. |
| circular dependencies | The pre-write lens asks agents to inspect dependency direction and likely cycle risks before editing. |
| re-export drift | The pre-write lens and post-write review both call out re-export and barrel files as coupling risks. |
| silent fallback | `AGENTS.md`, this guide, and the setup playbook all forbid swallowed errors and fallback behavior unless it is a documented requirement. |
| flat directories | `docs/local-project-knowledge-template.md` asks agents to record architecture maps, module boundaries, dependency direction, public APIs, and known hotspots so directory boundaries stay visible. |

The support scripts reinforce those rules:

- `scripts/inventory_optional_tools.py` gives agents a read-only way to classify Obsidian, Lumin Repo Lens, dependency lint, strict type checks, cycle detection, and complexity limits before asking to install anything.
- `scripts/check_private_paths.py` scans tracked files for concrete private paths and secret assignments.
- `scripts/audit_agent_stack.py` checks local harness state and generated Claude plugin drift; `--repo-only` keeps CI focused on repository artifacts.

## Operating Loop

### Pre-write lens

Before editing code, inspect the target repository and write down the smallest useful map:

- module, layer, and domain boundaries
- existing helpers, types, shapes, and public APIs
- source-of-truth files for shared utilities, schemas, and contracts
- dependency direction and likely cycle risks
- re-export and barrel files
- function and file size hotspots
- tests that already cover the target behavior
- missing edge cases, failure paths, side effects, and concurrency risks

For TypeScript and JavaScript repositories, an optional structure tool such as Lumin Repo Lens can create local evidence artifacts. For other languages, use the repository's native tools: language server output, package graph tools, AST tools, import scanners, test discovery, and direct file inspection.

Do not treat tool output as a decision. Treat it as evidence.

### Write gate

During implementation:

- follow TDD for every feature, bugfix, and refactor
- write edge cases first: empty input, null or missing values, boundary values, failure paths, side effects, and concurrency when relevant
- search for existing helpers, types, shapes, and public APIs before creating new ones
- keep mocks at external boundaries; do not mock internal implementation details
- use guard clauses or early returns when nesting grows past two or three levels
- keep error handling at explicit boundaries such as adapters, handlers, command entrypoints, and UI boundaries
- do not silently swallow errors
- do not add a silent fallback that hides a failed contract
- do not add fallback behavior unless it is a documented product requirement
- avoid god functions and god files by extracting focused units only when the extraction reduces real complexity
- preserve the repository's existing style and formatting

When adding dependency lint, strict type checks, or complexity rules, inspect the existing toolchain first. Do not invent ESLint, dependency-cruiser, TypeScript, or language-specific config that the target repository does not already support unless the owner approves that tooling change.

### Post-write review

After implementation, review the change before calling it complete:

- did a new helper duplicate an existing helper?
- did a new shape, schema, or type bypass an existing source of truth?
- did dead code or commented-out code remain?
- are any errors swallowed?
- did fallback behavior spread into callers instead of staying at a boundary?
- are modules connected through hidden contracts, import side effects, initialization order, or global state?
- are barrels and re-exports still intentional?
- did fan-in or fan-out concentrate too much responsibility in one file?
- do tests validate behavior, failure paths, and side effects?
- are local evidence artifacts such as `.audit/` intentionally untracked?

## macOS Setup

For this repository:

```bash
git clone https://github.com/hun99999/agent-bootstrap.git
cd agent-bootstrap
python3 -m unittest discover -s tests -p 'test_*.py'
```

For Codex current-harness setup from this repository:

```bash
bash .codex/install.sh --partner-name "Hun"
python3 scripts/audit_agent_stack.py
```

For Claude Code plugin rendering from this repository:

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
python3 -m unittest tests.test_claude_plugin -v
```

For a target repository that should keep local evidence artifacts out of Git:

```bash
printf '\n.audit/\n' >> .gitignore
git diff -- .gitignore
```

## Windows PowerShell Setup

For a target repository that should keep local evidence artifacts out of Git:

```powershell
Add-Content -Path .gitignore -Value ".audit/"
git diff -- .gitignore
```

For a Python-tested clone of this repository:

```powershell
git clone https://github.com/hun99999/agent-bootstrap.git
Set-Location agent-bootstrap
python -m unittest discover -s tests -p "test_*.py"
```

Some harness installers and symlink flows depend on the host tool and filesystem permissions. If a Codex or Claude Code install command is not documented for native Windows in this repository, use the harness' current official install path or WSL/Git Bash instead of guessing flags.

## Codex Workflow

When applying these guardrails in Codex, ask Codex to:

1. Read `AGENTS.md`.
2. Read this guide.
3. Read `docs/local-project-knowledge-template.md`.
4. Inspect the target repository's current tooling before adding lint or dependency rules.
5. Run a pre-write lens pass and summarize evidence.
6. Follow TDD for each code change.
7. Run post-write review before final verification.

Codex users can optionally install Lumin Repo Lens as a Codex skill wrapper. The upstream project documents this Codex-native install:

```bash
git clone https://github.com/annyeong844/lumin-repo-lens.git ~/.codex/lumin-repo-lens
mkdir -p ~/.codex/skills
ln -sfn ~/.codex/lumin-repo-lens/skills/lumin-repo-lens-codex ~/.codex/skills/lumin-repo-lens-codex
ln -sfn ~/.codex/lumin-repo-lens/skills/lumin-repo-lens ~/.codex/skills/lumin-repo-lens
ln -sfn ~/.codex/lumin-repo-lens/skills/lumin-repo-lens-write-gate ~/.codex/skills/lumin-repo-lens-write-gate
ln -sfn ~/.codex/lumin-repo-lens/skills/lumin-repo-lens-canon ~/.codex/skills/lumin-repo-lens-canon
```

Restart Codex after installing optional skills. In Codex, start with `$lumin-repo-lens-codex` only when the skill is actually installed.

## Claude Code Workflow

When applying these guardrails in Claude Code, ask Claude Code to:

1. Read `AGENTS.md`.
2. Read this guide.
3. Read `docs/local-project-knowledge-template.md`.
4. Use the planning and TDD workflow before code changes.
5. Use a reviewer pass that prioritizes hidden coupling, duplicate replacement, swallowed errors, re-export drift, fan-in/fan-out hotspots, and tests that mock internal behavior.

Optional Lumin Repo Lens commands documented by the upstream project:

```text
/plugin marketplace add annyeong844/lumin-repo-lens
/plugin install lumin-repo-lens@annyeong844-marketplace
/reload-plugins
/lumin-repo-lens:full
/lumin-repo-lens:pre-write
/lumin-repo-lens:post-write
```

Use `:full` for a first checkup, a branch-level review, or a major refactor. Use `:pre-write` before a scoped code change and `:post-write` after the change.

## Legacy Surface Notes

OpenCode and OpenClaw are legacy/reference material in this repository, not
current first-class service targets. If Hun explicitly asks for migration or
restoration work on those surfaces, apply the same shared-core guardrails: read
the root `AGENTS.md`, use the local project knowledge template, run pre-write,
write, and post-write checks, and keep local evidence artifacts untracked.

## Optional Lumin Repo Lens

Lumin Repo Lens is an optional TypeScript and JavaScript repository structure lens. It can produce JSON evidence files, a summary markdown file, and a Mermaid topology diagram under `.audit/`.

Use it when the target repository is TS/JS-heavy and structure evidence would help the agent avoid duplicates or boundary drift. Do not require it for Python, Rust, Go, or small one-file projects.

The upstream project also documents a direct CLI wrapper from a clone:

```bash
git clone https://github.com/annyeong844/lumin-repo-lens.git
cd lumin-repo-lens
node skills/lumin-repo-lens/scripts/audit-repo.mjs --root <repo>
```

If you do not want the tool to auto-install parser dependencies, upstream documents:

```bash
LUMIN_REPO_LENS_NO_AUTO_INSTALL=1 node skills/lumin-repo-lens/scripts/audit-repo.mjs --root <repo>
```

The tool output is evidence. The agent must still inspect the cited files and make the engineering call.

## Lumin Evidence Lifecycle

Use this lifecycle only when the target repository is TS/JS-heavy and Lumin Repo Lens is installed or explicitly approved. If Lumin is missing, the agent should still follow the same evidence rules with native repo tools and direct inspection.

### Structural claim contract

The contract is stricter than "run a tool and summarize it":

- No structural claim without evidence. A claim about duplicate helpers, hidden coupling, dead exports, cycles, topology, barrel drift, public-surface risk, god files, or fan-in/fan-out hotspots needs a cited artifact or direct file evidence.
- No absence claim without scan range. `not observed is not does not exist`; report the files, directories, excludes, language coverage, and confidence behind the statement.
- Read `.audit/manifest.json` first when it exists. It is the source for scan range, produced artifacts, skipped lanes, confidence, and blind spots.
- Treat `.audit/audit-summary.latest.md` as an artifact map, not a final review. The engineering review still belongs to the agent.
- Label structural conclusions as `grounded, degraded, unknown` when artifact quality, parse coverage, or scan range changes affect confidence.
- Avoid false-positive cleanup. Static "no consumer found" evidence is not enough to delete code when resolver blindness, parse taint, runtime imports, framework conventions, generated files, or public API promises might apply.

### Audit cadence

Use the smallest cadence that gives enough evidence:

- `quick, full, ci`: quick is for focused checks, full is for first pass or branch-level reviews, and ci is for automated guardrail enforcement when the repo has opted in.
- Use full evidence for a first checkup, large refactor, post-refactor review, stale artifacts, or an explicit structural audit request.
- Use focused checks for a narrow feature after a recent comparable full audit.
- Do not compare two audit results unless their scan range and confidence are compatible enough for the claim being made.

### Pre-write and post-write

For a scoped code task:

1. Build the pre-write intent from the requested change. Track `names`, `shapes`, `files`, `dependencies`, and `plannedTypeEscapes`.
2. Run the approved Lumin pre-write flow or native equivalent.
3. Read the invocation-specific `pre-write-advisory` before editing. Do not rely only on a `latest` pointer when a specific advisory path exists.
4. Implement with TDD and the write gate in this guide.
5. Run the matching `post-write-delta` against the same advisory.
6. Lumin post-write machine evidence covers `silent-new` type escapes, planned-not-observed type escapes, unexpected new files outside the intent, scan range changes, and degraded confidence.

If the post-write delta says a change was not observed, inspect the actual diff and the scan range before concluding anything. The correct closeout may be "unknown until a wider audit runs."

Manual post-write review still covers duplicate helpers, changed dependencies, public API drift, dependency direction, re-export drift, hidden coupling, and weak tests. Keep those as engineering review claims backed by direct file evidence or repository-native tools, not as unsupported Lumin delta fields.

### Canon and living audit

Use canon or living audit docs when the repo has enough structure to justify durable memory:

- Lumin canon sources are limited to type ownership, helper registry, topology, and naming.
- Use living audit or project docs for boundary policy, public API policy, dependency direction, and re-export policy.
- Keep a living audit for unresolved structure risks, stale evidence, recurring hotspots, and accepted deviations.
- Prefer `docs/current/audit/lumin-structural-audit.md` for shareable project facts.
- Keep private local details in `local.md`, an untracked note, or an Obsidian page. The repository should link to the kind of knowledge needed, not to Hun's personal vault path.

## Local Wiki Or Obsidian Index

Use `docs/local-project-knowledge-template.md` as the shape of a project wiki page.

Good places to keep that index:

- the target repository's `local.md` if it is intended to be local or machine-specific
- an untracked note under a private notes directory
- an Obsidian page in Hun's personal vault
- a team-visible architecture note if the content is safe to share

Do not commit personal vault paths, private project paths, credentials, MCP endpoints, auth state, or machine-specific trust settings.

For each new session, paste or reference only the sections relevant to the task. The goal is to give the agent the minimum structural memory needed to avoid repeating work.

## Applying This To Another Repository

Use [../prompts/apply-vibe-coding-guardrails.md](../prompts/apply-vibe-coding-guardrails.md) when you want an agent to add guardrails to a repository.

The agent should:

- check Git status before changes
- ask how to handle uncommitted user work when needed
- inspect existing docs, tests, lint, and type tooling
- add `.audit/` to `.gitignore` when local evidence artifacts are expected
- create or update local project knowledge guidance
- add repository-appropriate checks without inventing unsupported tooling
- commit the guardrail setup in small, reviewable commits

## Starting Daily Work

Use [../prompts/start-with-vibe-coding-guardrails.md](../prompts/start-with-vibe-coding-guardrails.md) when the guardrails already exist and you want an agent to work on a specific feature or bug.

The agent should:

- run the pre-write lens
- write or update tests before implementation
- implement the smallest reasonable change
- run post-write review
- run final verification commands
- report evidence and remaining risk

## Privacy Boundaries

Do not commit personal vault paths.

Also keep these out of public repositories:

- private MCP endpoints
- tokens, credentials, cookies, and auth state
- organization-specific secrets
- machine-specific trust configuration
- local browser profile paths
- private project paths unless the repository is private and the owner approves

The public baseline should teach the workflow. The local overlay should hold the private map.
