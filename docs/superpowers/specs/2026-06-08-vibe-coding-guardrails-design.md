# Vibe Coding Guardrails Design

## Goal

Improve this repository and Hun's local AI coding environment so Codex, Claude Code, and OpenCode sessions reduce repeated helpers, hidden coupling, weak tests, silent fallbacks, oversized files, and ungrounded reviews.

The first implementation should set up the guardrails inside this repository, then document how Hun can give this repository to Codex or Claude Code and ask it to apply the same operating model to another project on macOS or Windows.

## Source Ideas

The design adapts these ideas from the referenced DCInside post and comments:

- Agents forget context between sessions, so project structure and existing helpers need a persistent index.
- Boundaries, dependency direction, and public surfaces should be explicit before code changes.
- Tests should validate behavior and edge cases, not string-level implementation details.
- Mocking should stay at external boundaries.
- Agents should avoid silent fallbacks, duplicate defensive code, deep nesting, oversized functions, god files, circular dependencies, and unmanaged re-exports.
- Review should look for duplicate replacements, dead code, hidden contracts, initialization order coupling, global state, side effects, fan-in/fan-out hubs, and stale barrels.
- AST or repository-structure evidence is useful before and after writing.
- A local wiki or Obsidian index can preserve project-specific structure, but personal paths and private knowledge should not be committed to a public bootstrap repository.

## Scope

This work has four deliverables.

1. Public guardrail documentation in this repository.
2. Prompt and agent instruction updates that make the existing process-first agents use the guardrails.
3. Optional local overlay guidance for Hun's current machine, including Obsidian/wiki usage without committing personal vault paths.
4. Tests and audit coverage that prove the repository distributes the guardrails consistently across Codex, Claude Code, and OpenCode surfaces.

This work will not vendor third-party tools, install global dependencies automatically, or commit Hun's private Obsidian paths. Third-party tools such as `annyeong844/lumin-repo-lens` should be integrated as optional evidence providers.

## Architecture

The repository should keep its existing split between shared core and harness adapters.

- Shared core: `AGENTS.md`, `agents/*.md`, and `shared/agent-metadata.json`.
- Codex adapter: `.codex/`, `codex-home/`, and Codex install docs.
- Claude Code adapter: `plugins/process-first-agents/`, `.claude-plugin/`, and Claude install docs.
- OpenCode adapter: `.opencode/` and OpenCode install docs.
- Docs and prompts: reusable setup guides and copy-paste prompts for applying the guardrails to another repository.

Guardrails should live in tracked public docs and shared prompt text. Personal project indexes should live in local overlays, for example a project's `local.md`, an untracked note, or an Obsidian vault selected by Hun outside this repository.

## Public Guardrail Model

Add a public guide that agents can read before modifying a repository. It should define a three-stage loop.

### 1. Pre-Write Lens

Before changing code, the agent should inspect:

- module, layer, and domain boundaries
- existing helpers, types, shapes, and public APIs
- dependency direction and likely cycle risks
- re-export and barrel files
- function and file size hotspots
- tests that already cover the target behavior
- edge cases and side effects that should be locked before implementation

For TS/JS repositories, the guide should mention optional evidence tools such as `lumin-repo-lens` and explain that evidence files are local artifacts. For other languages, the fallback is repository-native tools, language-native AST/lint commands, and direct file inspection.

### 2. Write Gate

During implementation, agents should:

- follow TDD for every feature, bugfix, and refactor
- test edge cases first
- avoid internal mocks
- use guard clauses instead of unnecessary deep nesting
- introduce new helpers, functions, types, and shapes only after searching for existing ones
- keep error handling at clear boundaries
- avoid silent fallback unless the fallback is a documented product requirement
- keep files and functions small enough to review
- preserve existing style and avoid broad rewrites

### 3. Post-Write Review

After implementation, agents should check:

- whether a new helper duplicates an existing one
- whether dead code or commented-out code remains
- whether errors are swallowed
- whether side effects, global state, or initialization order created hidden coupling
- whether barrels and re-exports are still intentional
- whether fan-in/fan-out has concentrated too much responsibility in one file
- whether tests validate behavior, failure paths, and side effects
- whether the local evidence artifacts should stay untracked

## Agent Instruction Updates

The root constitution should add a short "Structure and coupling guardrails" section. It should be general enough for all harnesses and should not depend on Claude-only commands.

The `planner` agent should explicitly design module boundaries, SSOT locations, dependency direction, testing edge cases, and evidence-gathering steps.

The `worker` and specialist implementation agents should search before creating helpers or shapes, run the pre-write checks from the plan, and use TDD before production changes.

The `reviewer` should prioritize hidden coupling, duplicate replacements, swallowed errors, unmanaged re-exports, fan-in/fan-out hubs, and tests that mock internal behavior.

The `verifier` should confirm pristine test output and report whether local evidence artifacts are intentionally untracked.

The generated Claude plugin and Codex/OpenCode installed copies must be updated through the existing render/install mechanisms, not edited independently.

## Documentation Deliverables

Add a detailed guide under `docs/` for applying the guardrails to another repository. It should include:

- a short explanation of the problem this solves
- the expected repo hygiene loop: pre-write, write, post-write
- macOS setup commands
- Windows PowerShell setup commands
- Codex workflow
- Claude Code workflow
- OpenCode notes where applicable
- optional Lumin Repo Lens setup and usage
- local wiki or Obsidian index guidance
- a copy-paste prompt for "apply this to my repository"
- a copy-paste prompt for "start work in a repository using these guardrails"
- guidance for keeping private local notes out of a public repository

The guide must avoid claiming that a third-party command exists unless it is confirmed from the tool's documentation. When a command is optional and third-party, the guide should name it as optional and link or cite the upstream source.

## Local Overlay Guidance

Add a template for project-local knowledge that Hun can copy into `local.md`, an untracked repo note, or Obsidian. It should capture:

- project purpose
- architecture map
- source-of-truth utilities and types
- module boundaries and dependency direction
- public APIs and re-export policy
- test strategy
- error-handling boundaries
- known hotspots
- commands for lint, tests, type checks, and structure checks
- current decisions and rejected alternatives

The repository should not hard-code Hun's Obsidian vault path. It may document that Hun can keep this template in Obsidian and paste or link the relevant sections into a session.

## Repository Self-Setup

This repository should be configured first as the reference implementation.

Minimum self-setup:

- Add `.audit/` to `.gitignore` for local repository-lens artifacts.
- Add public guardrail docs and prompts.
- Update shared agent prompts.
- Regenerate Claude plugin outputs if shared agent prompts change.
- Update tests that assert prompt corpus and generated plugin consistency.
- Run the repository's unittest suite.

Possible follow-up self-setup:

- Add a lightweight audit script that checks prompt docs mention the guardrail loop.
- Add optional local notes under `codex-home/local.md` only if they are generic and safe to share.
- Add a future plan for repository-specific dependency linting when a target project has TypeScript or JavaScript tooling.

## Testing

Use TDD for implementation.

Expected tests:

- Prompt corpus tests verify the root constitution mentions structure boundaries, search-before-new-helper behavior, edge-case-first tests, external-boundary mocks, and no silent fallbacks.
- Agent tests verify planner, worker, reviewer, and verifier roles include their guardrail responsibilities.
- Claude plugin tests verify regenerated plugin outputs include the same guardrail text and read-only guards still apply where expected.
- Documentation tests verify the new guide and prompts exist and mention Codex, Claude Code, macOS, Windows PowerShell, optional Lumin usage, local wiki/Obsidian guidance, and `.audit/` handling.
- Existing install and audit tests continue to pass.

## Risks

- Too many rules can make agents slow or performative. The implementation should keep constitution changes concise and put long explanations in docs and prompts.
- Lumin Repo Lens is TS/JS-focused. The guide must not imply it covers every language equally.
- Obsidian guidance can leak personal paths if made too concrete. Keep public docs path-neutral.
- Strict lint examples can be wrong for target repos. The guide should tell agents to inspect existing tooling before adding ESLint, dependency-cruiser, or language-specific equivalents.

## Success Criteria

- A fresh Codex or Claude Code session can read this repository and know how to apply the guardrails to another repo.
- The current repository itself has the guardrail docs, prompt updates, ignored local evidence artifacts, regenerated harness outputs, and passing tests.
- The public repository stays free of private paths, secrets, credentials, and machine-specific trust state.
- The workflow remains pragmatic: evidence first, small changes, TDD, review, verification.
