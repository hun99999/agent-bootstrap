---
name: hun-engineering-loop
description: Use when Hun asks Codex to plan, implement, review, refactor, or QA software work using Hun's local engineering loop, memory preflight, source-of-truth checks, high-risk approval boundaries, and evidence-backed verification.
---

# Hun Engineering Loop

## Purpose

Run Hun's day-to-day engineering workflow as an operational wrapper around `karpathy-guidelines`, repository rules, memory recall, and executable verification.

Use this for non-trivial project work. Do not use it as a replacement for repo `AGENTS.md`, scripts, tests, docs, or explicit user instructions.

## Memory Preflight

Before meaningful work, check available memory or journal context for the current repo, project name, feature, prior blocker, or user preference.

- Remember: memory is a recall layer, not a source of truth.
- If memory conflicts with repo docs, scripts, tests, `AGENTS.md`, or observed runtime output, the current source wins.
- Verify drift-prone memory before using it for decisions.
- Record meaningful learnings only through the host's approved memory mechanism.

## Source Of Truth

Establish the current source-of-truth stack before editing:

1. User's latest instruction.
2. Repo-local `AGENTS.md`, README, docs, scripts, tests, CI, and runtime output.
3. Project skill or project routing docs.
4. Memory and prior summaries.
5. External advice, including ChatGPT Pro, after local verification.

Keep at least a minimal source-of-truth pointer in repo docs or `AGENTS.md` when a project depends on a skill. Do not hide all project routing inside global skills.

## Access And Approval Boundary

Broad access is operational capability, not permission to perform every action.

Use a high-risk stop/ask boundary before actions that can delete, expose, spend, deploy, rotate, revoke, or materially change trust:

- deleting source, sessions, history, databases, user data, or large directories;
- changing permissions, credentials, API keys, auth state, browser profiles, MCP endpoints, or security settings;
- touching production, deployment, billing, external accounts, or public-facing systems;
- rewriting history, force-pushing, bypassing hooks, disabling tests, or changing protected branches.

Prefer natural-language rules plus permission profiles, hooks, or approval layers where the host supports them. In public templates, do not present broad access as the default recommendation.

## Artifact-First Execution

Convert broad intent into durable artifacts before open-ended work:

- For implementation: write or update tests, specs, plans, or checklists that define success.
- For planning: produce a design/spec plus a stepwise implementation plan when architecture or rollout choices matter.
- For external review: summarize accepted, rejected, deferred, and needs-local-verification items.
- For reusable policy: put project-specific behavior in project docs or project skills, not global prose.

## Verification Contract

Name the evidence required before claiming completion.

- `fast check`: smallest command that proves the touched surface is syntactically or structurally healthy.
- `targeted regression`: test or repro that covers the changed behavior or fixed bug.
- `type/lint/build`: project-level static checks when available.
- `browser/manual QA`: real UI check for browser, visual, or workflow changes.
- `deployment smoke`: live or preview check only when deploy/release state is in scope.
- `negative/regression test`: prove the old failure or unsafe path is blocked when applicable.

Separate smoke evidence from official proof. Do not overclaim from HTTP 200, a local render, or a passing narrow test.

## QA / Refactor Loop

After the first working artifact:

1. Run the targeted verification.
2. Review the diff for excess scope, duplicate helpers, hidden coupling, weak tests, swallowed errors, and unrelated formatting churn.
3. Refactor only where it reduces real duplication, clarifies boundaries, or matches existing project patterns.
4. Re-run the relevant verification after refactoring.

Use `karpathy-guidelines` to keep the change simple, surgical, assumption-aware, and goal-driven.

## Final Report

Report only what is evidenced:

- files or runtime paths changed;
- tests, checks, browser QA, or smoke checks run;
- accepted/rejected/deferred external advice;
- unresolved risks or verification not run;
- whether any runtime install or Codex restart is still needed.
