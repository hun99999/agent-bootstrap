# Agent Stack Modernization Design

Date: 2026-05-12

## Context

This repository bootstraps Hun's coding-agent environment across Codex, Claude Code, and OpenCode. The current machine and repository are out of sync with the current toolchain:

- Local Codex CLI is `0.128.0`; npm reports `@openai/codex` latest as `0.130.0`.
- Local Claude Code is `2.1.47`; npm reports `@anthropic-ai/claude-code` latest as `2.1.139`.
- Local manual `~/.codex/superpowers` is on commit `917e5f53b16b115b70a3a355ed5f4993b9f8b73d`; upstream `obra/superpowers` `main` is `f2cbfbefebbfef77321e4c9abc9e949826bea9d7`, with latest tag `v5.1.0`.
- The Codex curated `superpowers` plugin cache already reports version `5.1.0`, so this machine currently has both curated-plugin and manual-symlink discovery paths available.
- Repository Codex templates still default to `gpt-5.4`.
- Claude plugin metadata still contains stale `jerrygoha` identity values.

The update should improve both the live local environment and the reusable bootstrap artifacts in this repository.

## Goals

- Update Hun's local Codex, Claude Code, and manual Superpowers installation to the latest confirmed versions.
- Make `gpt-5.5` the default Codex model and keep `gpt-5.4` as the explicitly supported previous-model fallback.
- Modernize Codex templates around the current config reference where doing so is low risk.
- Improve AGENTS/local prompt templates and role prompts by removing conflicts and aligning them with current Codex and Claude Code agent behavior.
- Update Claude plugin metadata and generated files to use `hun99999` identity values.
- Clarify Superpowers installation so users understand official plugin versus manual fallback behavior.
- Add tests that prevent stale model defaults, stale GitHub identity values, and broken generated plugin metadata from returning.

## Non-Goals

- Do not rewrite the whole prompt corpus.
- Do not delete user data or private repository content.
- Do not remove backward compatibility for existing manual Superpowers installs unless Hun approves that specific removal.
- Do not hardcode Claude model IDs unless the current Claude Code docs or CLI clearly confirm the exact latest and previous model aliases.
- Do not bypass pre-commit hooks or skip test output review.

## Design

### Local Environment

Update local global npm tools using the existing Node environment:

- `@openai/codex@latest`
- `@anthropic-ai/claude-code@latest`

Refresh the manual Superpowers checkout by fetching upstream and moving it to the current upstream default branch. Verify with:

- `codex --version`
- `claude --version`
- `git -C ~/.codex/superpowers rev-parse HEAD`

Because Codex already has the curated `superpowers` plugin cached, do not immediately delete the manual `~/.agents/skills/superpowers` symlink. First document the duplicate-loading risk and make repository behavior explicit. Any symlink removal should be a separately visible step.

### Codex Models and Config

Repository Codex templates should default to:

```toml
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
model_reasoning_summary = "detailed"
model_verbosity = "high"
plan_mode_reasoning_effort = "xhigh"
```

They should also include a profile for the previous model:

```toml
[profiles.previous]
model = "gpt-5.4"
```

The top-level default is the strongest current model. The `previous` profile is the escape hatch for quota, latency, regressions, or model availability issues.

Codex agent-role configuration should be modernized only after tests capture the expected config shape. The preferred target is the current `[agents.<name>]` role format from the Codex config reference, using role config files where needed instead of legacy `[[custom_agent]]` tables. If implementation discovers that the current Codex App still requires legacy tables for this bootstrap, keep the smallest compatible bridge and document why.

### Claude Code Agents

Regenerate the Claude plugin with updated metadata:

- author name should be Hun-oriented rather than stale `Jerry Go`
- author email should use `48903443+hun99999@users.noreply.github.com`
- repository should be `https://github.com/hun99999/agent-bootstrap`

Claude agent frontmatter should be improved conservatively:

- use `model: inherit` unless current docs or CLI confirm a better exact alias
- add `effort` or `maxTurns` only where the role clearly benefits
- use `isolation: worktree` only for roles that are expected to edit independently

This avoids inventing Claude model names while still adopting current Claude Code agent features.

### Prompt Corpus

Prompt changes should be narrow and behavior-driven:

- Keep the Hun/Bot working relationship and honesty rules.
- Preserve TDD, verification, git safety, and root-cause debugging requirements.
- Reduce conflicts between "always ask" and "proactively continue" by spelling out when clarification is required.
- Keep the standing preference that subagents may be used for independent work when the runtime allows it, while acknowledging that an individual host may still impose stricter tool-use rules.
- Remove stale username and repository references.

The goal is shorter, clearer operating policy, not a larger prompt.

### Superpowers Documentation

Docs should explain the current split plainly:

- Codex App can use the official curated Superpowers plugin.
- The installer can still maintain a manual `~/.codex/superpowers` checkout for environments that rely on local skill discovery.
- Users should avoid enabling both discovery paths unless they intentionally want duplicate skill entries.

The implementation should prefer explicit documentation and tests before changing destructive local state.

### Tests and Verification

Add or update tests to check:

- Codex templates default to `gpt-5.5`.
- Codex templates expose a `gpt-5.4` previous-model profile.
- Generated Claude plugin metadata uses `hun99999` values.
- Repository files no longer contain stale `jerrygoha` or `Jerry Go` references, except in historical docs where explicitly allowed.
- Installer/docs still describe Superpowers behavior consistently.

Run the repository test suite after implementation and read the full output.

## Rollout

1. Commit this design.
2. After Hun reviews the design, write an implementation plan.
3. Update local tools first and verify actual versions.
4. Add failing tests for the repository policy changes.
5. Implement repository changes in the smallest coherent patches.
6. Regenerate derived Claude plugin files.
7. Run tests and stale-string checks.
8. Commit the completed changes.

## Open Decisions

- Whether to remove or keep the local `~/.agents/skills/superpowers` symlink after confirming the curated plugin path is active.
- Whether to fully migrate Codex custom agents to `[agents.<name>]` in this pass, or keep a compatibility bridge if the app surface still depends on legacy role registration.
