# Slim Core And Optional Superpowers Design

## Goal

Reduce always-on instruction cost and procedural duplication while keeping the safety, source-of-truth,
scope, and evidence contracts that materially improve engineering work.

The local Codex runtime should stop discovering the manual Superpowers checkout. The repository should
continue to offer the latest upstream Superpowers default branch as an explicit choice for other
machines and lower-capability models. The public skill catalog should add only Matt Pocock's compact,
user-invoked `handoff` skill.

## Approved Decisions

- Keep `AGENTS.md` as the canonical global prompt source and `codex-home/AGENTS.md` as its exact
  distribution snapshot. Their overlap is intentional in this dotfiles repository.
- Reduce the shared core to at most 850 words and 6.5 KiB.
- Remove direct Superpowers dependencies and unconditional TDD, review, subagent, and full-regression
  requirements from the shared core and role prompts.
- Preserve explicit approval boundaries, current-evidence precedence, unrelated-work protection,
  smallest-change discipline, boundary-aware error handling, root-cause diagnosis, and honest
  verification reporting.
- Select tests by invalidated evidence:
  - run the narrowest relevant check;
  - reuse a passing result when relevant source, configuration, dependencies, toolchain, and runtime
    inputs are unchanged;
  - rerun only invalidated checks;
  - run full regression/build/E2E or broad QA for broad, cross-cutting, high-risk, release-bound
    changes, or when a narrow check reveals wider impact;
  - never claim an unrun check passed.
- Make the Codex installer's `--superpowers-mode skip` the default.
- Keep `--superpowers-mode manual` as the explicit, model-independent opt-in. It continues to safely
  fast-forward the official upstream default branch and must not replace a dirty, divergent, or
  user-managed path.
- Treat an absent or intentionally inactive manual Superpowers installation as a healthy optional
  audit state. Broken links, wrong targets, dirty active checkouts, and invalid active installs remain
  failures.
- Vendor only `mattpocock/skills`'s `handoff` package at reviewed commit
  `2ab958093e83e0ec752e6c1c5932da465bf23e0c`, with its MIT attribution.
- Keep `handoff` explicitly user-invoked through both
  `disable-model-invocation: true` and `allow_implicit_invocation: false`.
- Do not add `research`, `tdd`, `diagnosing-bugs`, `code-review`, or the Matt Pocock setup workflow.
- After repository verification, install the reviewed `handoff` snapshot into the local Codex skill
  directory and remove only the exact local Codex Superpowers discovery symlink. Preserve the checkout
  for rollback and do not change the separate Claude Code plugin.
- Do not overwrite the live Codex `config.toml` while synchronizing prompts.

## Current Upstream Evidence

Checked on 2026-07-28:

- `obra/superpowers` latest immutable release: `v6.2.0`, published 2026-07-24.
- `obra/superpowers` remote default branch HEAD:
  `3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9`.
- `mattpocock/skills` remote default branch HEAD:
  `2ab958093e83e0ec752e6c1c5932da465bf23e0c`.

The installer follows the configured remote's default branch rather than hard-coding a release tag.
This lets an explicit manual install receive the current upstream state while retaining existing
fast-forward safety checks.

## Shared Prompt Contract

The compact shared core has seven responsibilities:

1. Partner contract: address the configured partner, communicate directly, and do not invent
   technical details.
2. Authority and evidence: current user instruction and repository/runtime evidence outrank memory.
   After context compaction, reread the relevant sources and state.
3. Scope and safety: broad access is not blanket approval; stop for destructive, production,
   deployment, auth, permission, secret, account, public-sharing, protected-branch, hook, or
   test-enforcement changes.
4. Implementation discipline: use the smallest reasonable change, existing helpers and public APIs,
   explicit boundaries, readable domain names, and surrounding style. Do not swallow errors or add
   undocumented fallbacks.
5. Diagnosis and verification: reproduce and identify root causes, use risk-proportionate evidence,
   and report what was not run.
6. Git protection: inspect state, preserve unrelated work, use a task branch for non-trivial work,
   and never bypass hooks or destroy history without approval.
7. Skills and delegation: load applicable skills only when they add value; treat skill changes as
   process-code changes with focused validation; delegate independent work only when useful.

`@local.md` remains the final nonblank line so machine-local additions stay outside the public core.

## Role Prompt Contract

Role prompts should contain only role-specific responsibilities plus the minimum shared execution
contract needed for that role. They must not restate the full shared core or require named
Superpowers skills.

- `eng-lead`: own scope, dependency ordering, risk, and evidence; delegate only independent work.
- `planner`: produce implementable, source-grounded plans; no implementation.
- implementation roles: make bounded changes, preserve APIs and data integrity, and run invalidated
  focused checks.
- `debugger`: reproduce, isolate, and explain the root cause before proposing a fix.
- `reviewer`: report evidence-backed regressions and risks; do not invent style work.
- `verifier`: apply the invalidated-evidence policy and distinguish targeted evidence from full
  regression.
- `release-manager`: assess branch, CI, release, and deployment readiness without performing external
  release actions unless authorized.
- `researcher`: remain read-only and separate facts, inference, and unresolved uncertainty.
- `skill-author`: keep skills concise, explicit in their trigger, and independently validated.

The canonical role sources remain `agents/*.md`; `codex-home/agents/*.md` remains an exact snapshot;
the Claude plugin bundle remains generated output.

## Optional Superpowers State Model

| Checkout | Discovery link | Audit result |
| --- | --- | --- |
| absent | absent | optional disabled; success |
| present and valid | absent | optional inactive; success |
| present and valid | correct link | optional active; success |
| absent | dangling or other link | broken; failure |
| invalid or dirty active checkout | any active link | broken; failure |
| present | wrong link target | broken; failure |

An inactive preserved checkout does not need online freshness checks because it cannot affect Codex
behavior. An active manual install retains identity, cleanliness, link-target, and optional online
freshness checks.

## Handoff Catalog Package

The tracked package is a byte-for-byte snapshot of:

- `skills/productivity/handoff/SKILL.md`
- `skills/productivity/handoff/agents/openai.yaml`

Add a small source record containing the upstream URL, immutable commit, source paths, license, and
review date. Keep the upstream MIT text in the package. Do not broaden its trigger or add automatic
agent, Git, browser, test, or repository-write behavior.

The repository catalog documents installation to `~/.codex/skills/handoff`. Runtime installation is
validated separately from the tracked snapshot.

## Documentation Contract

The four top-level READMEs and Codex/Claude setup docs should describe Superpowers as optional:

- default Codex install: no manual checkout and no discovery symlink;
- explicit Codex manual opt-in:
  `--superpowers-mode manual`;
- do not enable both the Codex curated plugin and manual discovery unless duplicate entries are
  intentional;
- Claude Code Superpowers is a separate user choice;
- model selection and Superpowers selection are independent;
- `skip` does not remove an existing manual link;
- `handoff` is a small explicit-use catalog skill, not a replacement workflow framework.

Historical specifications and plans remain historical records and are not rewritten.

## Verification Strategy

This is a broad shared-policy and installer change, so one final full repository regression is
required after the final source state is stable.

Before that final run:

1. Add focused contract tests and observe them fail against the old behavior.
2. Implement the smallest change for each contract.
3. Run only the focused tests invalidated by that change.
4. Regenerate the Claude plugin once after canonical prompt sources stabilize.
5. Review the diff and resolve generated drift.
6. Run the full suite exactly once at the final stable state.
7. Run the repository audit, private-path scan, and runtime-copy comparisons without repeating an
   unchanged passing test suite.

The current long-lived Codex task may retain its initial skill snapshot. Local Superpowers
deactivation is therefore proven by filesystem/plugin state now and by fresh-task discovery after
this task.

