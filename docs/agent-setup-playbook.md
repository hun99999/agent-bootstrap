# Agent Setup Playbook

Use this playbook when an agent is asked to set up `agent-bootstrap` or apply this repository's guardrails to another project.

This playbook is not a guarantee that every agent will behave correctly. It is the operational checklist the agent should follow so it can make good setup decisions, explain them, and avoid changing more than the user asked for.

## Success Criteria

A setup pass is successful only when the agent can report all of these with evidence:

- the requested scope was identified
- the current harness was identified
- user work was protected before file changes
- required and optional tools were separated
- optional installations were approved before they happened
- private paths, credentials, MCP endpoints, auth state, browser profiles, and machine-specific trust settings were kept out of tracked files
- the selected setup path was executed with documented commands
- real verification commands were run
- post-write review was completed
- remaining risks were reported plainly

Do not claim completion just because a prompt was pasted or files were edited. Completion requires verification evidence.

## Discovery Pass

Before changing files, gather the minimum facts needed to choose the right setup path.

Run:

```bash
git status --short --branch
```

If the repository has uncommitted changes or untracked files, stop and ask how to handle them before editing. Do not stash, delete, overwrite, or add those files unless the user explicitly approves.

Then identify:

- current harness: Codex, Claude Code, OpenCode, OpenClaw, or other
- requested scope: current harness, shared core, project guardrails, this bootstrap repository, or another explicit target
- host OS and shell: macOS shell, Linux shell, Windows PowerShell, WSL, Git Bash, or unknown
- existing repo tooling: test command, lint command, type check command, build command, dependency graph tool, formatter, CI
- existing project docs: `AGENTS.md`, `CLAUDE.md`, `README.md`, architecture docs, local setup docs, test docs
- source-of-truth files: shared helpers, shared types, schemas, public APIs, config entrypoints
- privacy boundaries: files that must not contain private local paths, tokens, MCP endpoints, auth state, or browser profile paths

If a fact cannot be discovered, say so. Do not invent package names, command flags, API details, config keys, install paths, or official sources.

## Scope Decision

Choose the smallest valid scope that satisfies the user's request.

| User request or context | Default scope | What to do |
| --- | --- | --- |
| Inside Codex and user says "set this up" | Codex current-harness-only | Use the Codex docs and installer. Do not configure Claude Code or OpenCode unless requested. |
| Inside Claude Code and user says "set this up" | Claude Code current-harness-only | Render/install the Claude Code plugin path. Do not configure Codex or OpenCode unless requested. |
| Inside OpenCode and user says "set this up" | OpenCode current-harness-only | Use the OpenCode docs and installer. Do not configure Codex or Claude Code unless requested. |
| Harness is unclear | shared-core-only | Apply only shared operating guidance and ask before harness-specific setup. |
| User points at an application repository | project guardrails | Add project-local knowledge guidance and repo-appropriate checks. Do not install global harness defaults unless requested. |
| User says this repository was updated | agent-bootstrap maintenance | Read the structure doc, regenerate generated output when needed, verify tests and audit. |
| User asks what Codex skills are available in this repository | skill catalog review | Read `skills/README.md` and `docs/codex-skills.md`. Compare selected skills with `~/.codex/skills`, then ask before installing or overwriting anything. |
| User asks for OpenClaw ACP | explicit integration path | Follow OpenClaw docs. Do not infer provider, backend, or gateway choices. |

When two valid scopes could apply, prefer the smaller one and explain what is intentionally left untouched.

## Environment Inventory

Inventory tools before installing anything.

This repository includes a read-only optional tool inventory helper. It does not install tools.

```bash
python3 scripts/inventory_optional_tools.py
python3 scripts/inventory_optional_tools.py --json
```

Use its output as evidence, not as permission to install. The agent must still classify each tool, explain the reason, and ask before installing anything.

For every relevant tool, report:

- detected state: installed, missing, unknown, or not applicable
- evidence: command output, file path existence, or documentation reference
- decision: required, recommended, optional, or skipped
- reason: why that classification fits this repo and task
- install status: not installed, already installed, requested approval, installed after approval, or skipped

### Required, Recommended, Optional, Skipped

Use these meanings consistently:

- Required: the requested setup cannot reasonably work without it.
- Recommended: it materially improves structural memory, evidence quality, or daily ergonomics, but the workflow still works without it.
- Optional: useful for some users or repositories, not needed for this task.
- Skipped: unrelated, too heavy for the repo, already covered by native tooling, unsupported in the current environment, or not approved.

Do not let a tool move from optional to installed just because it appears in this repository's docs.

## Optional Tool Decisions

### Obsidian

Obsidian is a private knowledge workspace option, not a required guardrail.

Recommend Obsidian when:

- repeated repository rediscovery is wasting time
- the project map contains private local context that should not be committed
- the user wants a cross-project wiki
- architecture decisions need a searchable private index

Skip Obsidian when:

- a committed doc, untracked `local.md`, or plain Markdown note is enough
- the project is small
- the environment is headless
- the user does not want a desktop app

On macOS, this repository documents a check in `docs/global-guardrail-setup.md`. On Windows PowerShell, this repository documents `winget` discovery commands and explicitly says to verify the package name and publisher before installing.

### Lumin Repo Lens

Lumin Repo Lens is optional and TS/JS-focused.

Recommend it when:

- the target repository is TypeScript or JavaScript heavy
- the task touches module boundaries, public APIs, re-exports, shared types, or import topology
- manual fan-in/fan-out inspection is unreliable
- local `.audit/` evidence would improve review quality

Skip it when:

- the repo is not TS/JS
- the change is tiny and isolated
- native tooling already provides the needed structure evidence
- the user does not approve installation

If `.audit/` artifacts may be created, make sure `.audit/` is ignored before running the tool.

When Lumin Repo Lens is approved and available, use it as an evidence workflow, not as a magic reviewer:

- No structural claim without evidence: cite a produced artifact, a direct file inspection, or both before claiming a duplicate helper, public surface, cycle, fan-in hotspot, re-export drift, or missing boundary.
- No absence claim without scan range: say "not observed in this scan range" instead of "does not exist" unless the checked range, files, and exclusions make that claim true.
- For a first pass or branch-level review, prefer the upstream full audit workflow. Treat `quick, full, ci` as audit cadences with different confidence, and read the produced `manifest.json` before using summaries.
- Before writing code, capture the pre-write intent with these keys: `names, shapes, files, dependencies, plannedTypeEscapes`. The agent should infer this from the user's task and repository evidence; the user should not need to hand-write JSON.
- Read the invocation-specific advisory produced for that pre-write run before editing. Do not rely only on a `latest` pointer when a command produced a more specific advisory path.
- After writing, run the matching post-write delta against the same invocation-specific advisory. Review `silent-new` type escapes, planned-not-observed type escapes, unexpected files outside the intent, scan range changes, and degraded confidence.
- Use canon draft or check-canon only for Lumin-supported canon sources.
- Lumin canon sources are limited to type ownership, helper registry, topology, and naming.
- Use living audit or project docs for boundary policy, public API policy, dependency direction, and re-export policy.
- Keep a living audit when a repo needs ongoing structural tracking. Prefer a shareable repository doc such as `docs/current/audit/lumin-structural-audit.md` when it is safe to commit; otherwise keep the same index shape in an `Obsidian or private wiki` page.
- Do not treat Lumin warnings as automatic refactor permission. The agent still needs to inspect cited files, avoid false-positive cleanup, and make the smallest change approved by the task.

### Dependency, Type, Cycle, And Complexity Checks

Dependency lint, strict type checks, cycle detection, complexity limits, and file/function size limits are strong controls, but they are tooling changes.

Add or tighten them only when:

- the repository already has that toolchain
- the user explicitly approves adding the tool
- the repository's documented standards already require it

Otherwise, document the recommendation and leave installation for a separate approved task.

## Installation Approval Gate

Before installing any desktop app, CLI, plugin, browser extension, package manager dependency, or global user-level default, stop and report:

- tool name
- why it is needed
- required/recommended/optional/skipped classification
- exact install source or command, verified from this repository's docs or a current official source
- files or directories it may write
- how the install will be verified
- whether it changes global user state or only the current repository

Proceed only after approval. If approval is not given, continue with the best no-install path and report the limitation.

## Setup Paths

Use the documented path for the selected scope.

### Codex

Read:

- `docs/README.codex.md`
- `docs/global-guardrail-setup.md`
- `.codex/INSTALL.md`

Documented command from the repository root:

```bash
bash .codex/install.sh --partner-name "Hun"
python3 scripts/audit_agent_stack.py
```

This writes user-level Codex defaults. Existing sessions may need a restart or a focused instruction to apply the new guardrails.

### Optional Codex Skills

Read:

- `skills/README.md`
- `docs/codex-skills.md`
- `prompts/setup-codex-skills.md`

This is a browse and selective install path, not a blanket installer. The repo copy is the catalog source, and the runtime copy lives under `~/.codex/skills/<skill-name>`. Ask before installing or overwriting any skill, then run the documented `quick_validate.py` validation path.

### Claude Code

Read:

- `docs/README.claude.md`
- `docs/global-guardrail-setup.md`
- `scripts/render_claude_plugin.py`

Documented render command from the repository root:

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
python3 -m unittest tests.test_claude_plugin -v
```

Claude Code plugin installation itself happens inside Claude Code using the documented marketplace commands. If the active environment cannot run Claude Code plugin commands, report that limitation instead of pretending the install happened.

### OpenCode

Read:

- `docs/README.opencode.md`
- `docs/global-guardrail-setup.md`
- `.opencode/INSTALL.md`

Documented command from the repository root:

```bash
bash .opencode/install.sh --partner-name "Hun"
```

OpenCode is optional for users who only use Codex or Claude Code. Use `scripts/audit_agent_stack.py --strict` only when missing optional tools should fail the audit.

### Project Guardrails

Read:

- `docs/vibe-coding-guardrails.md`
- `docs/local-project-knowledge-template.md`
- `prompts/apply-vibe-coding-guardrails.md`
- `prompts/start-with-vibe-coding-guardrails.md`

Expected project-local work:

- record module boundaries, dependency direction, source-of-truth files, public APIs, error boundaries, and known hotspots
- add `.audit/` to `.gitignore` when local evidence artifacts may be produced
- identify real test, lint, type check, and build commands
- keep private local knowledge in `local.md`, an untracked note, or a private wiki when it should not be committed
- avoid adding dependency or complexity tooling unless the repo already supports it or the user approves

## Verification Matrix

Run verification that matches the work performed.

| Work performed | Required verification |
| --- | --- |
| README or docs changed | Relevant documentation tests, then full test suite if practical |
| Shared `AGENTS.md` or `agents/*.md` changed | Full tests, Claude plugin render check, generated bundle drift check |
| Claude plugin renderer changed | `python3 -m unittest tests.test_claude_plugin -v` and `python3 scripts/audit_agent_stack.py` |
| Codex installer changed | Codex install tests and full tests |
| OpenCode installer changed | OpenCode install tests and full tests |
| Global local install performed | `python3 scripts/audit_agent_stack.py` after install |
| Optional tool installed | Tool-specific version or health check plus a note about what state changed |
| Target project guardrails applied | Target repo's real test/lint/type/build commands, plus post-write review |

For this repository, the standard full verification is:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/audit_agent_stack.py
git diff --check
```

Do not claim completion if these commands were skipped. Say what was skipped and why.

## Post-Write Review

Before final reporting, inspect the diff and answer:

- Did a new helper duplicate an existing helper?
- Did a new type, shape, schema, prompt rule, or config bypass a source of truth?
- Did generated output drift from source files?
- Did a fallback, compatibility path, or defensive branch spread without a documented requirement?
- Did any error get swallowed?
- Did re-export or barrel usage expand without review?
- Did fan-in or fan-out concentrate more responsibility in one file?
- Did tests verify behavior and side effects rather than only strings?
- Did mocks stay at external boundaries?
- Did any tracked file include private paths, credentials, MCP endpoints, auth state, browser profiles, or trust settings?

If the answer is uncertain, report the uncertainty instead of hiding it.

## Existing Sessions

Global defaults usually affect new sessions more reliably than already-running sessions.

For existing sessions, tell the user one of these:

- restart the session for a clean pickup
- reload plugins when the harness supports it
- paste the focused instruction from `docs/global-guardrail-setup.md`
- continue with current context and explicitly apply the new guardrails for the rest of the task

Do not assume an already-running agent has re-read updated user-level defaults.

## No private paths

Tracked files must not contain:

- personal Obsidian vault paths
- private project paths
- credentials, tokens, cookies, or auth state
- MCP endpoints
- browser profile paths
- machine-specific trust settings

Public docs may describe what to record. They should not record where Hun personally stores private notes.

## Final Report Template

End with a report the user can audit.

```text
Scope:
- requested:
- applied:
- intentionally skipped:

Environment:
- harness:
- OS/shell:
- required tools:
- recommended tools:
- optional tools:
- skipped tools:

Changes:
- files changed:
- global state changed:
- local project state changed:
- generated artifacts:

Commands run:
- command:
  result:
- command:
  result:

Post-write review:
- duplicate helpers/types/shapes:
- hidden coupling:
- swallowed errors/fallback drift:
- re-export/fan-in/fan-out hotspots:
- weak tests or mock misuse:
- private path leakage:

Remaining risks:
- risk:
- follow-up:
```

If no files changed, say that. If no install happened, say that. If a verification command could not run, include the exact reason.
