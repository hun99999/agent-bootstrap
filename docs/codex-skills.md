# Codex Skills

This repository includes a Skill Catalog for Codex skills that may be useful
across projects.

The workflow is browse, review, select, install. The repo copy is the catalog source. The installed copy is the runtime copy used by Codex under `~/.codex/skills/<skill-name>`.

Do not install every skill automatically. A setup agent should inspect this
repository's catalog, compare a selected skill with the installed runtime copy,
explain the change, ask Hun before installing or overwriting, and then validate
the installed skill.

The public default base skill is `karpathy-guidelines`. It is the portable
upstream/vendor skill preserved from `multica-ai/andrej-karpathy-skills`.

`hun-engineering-loop` is a compact Hun-local result router around that base
skill. It translates rough or abstract instructions into the smallest concrete
outcome, prefers current target evidence, keeps high-risk approval boundaries,
delegates only for clear leverage, and selects the lowest-cost direct proof.
Keep it local unless Hun explicitly chooses to publish or install it for a
particular runtime.

In Hun's runtime, `karpathy-guidelines` and the compact `hun-engineering-loop` remain eligible for implicit invocation. The wrapper is a small local delta rather than a second copy of the global prompt. Measure the pair against vanilla; a future benchmark result may narrow or remove implicit use.

## Lean Explicit Workflows

The catalog includes four compact, MIT-licensed adaptations of useful `obra/superpowers` workflows:

- `isolated-worktree`
- `execute-plan`
- `review-feedback-triage`
- `focused-debugging`

They are explicit-use skills. Install only the selected directories and invoke them as `$isolated-worktree`, `$execute-plan`, `$review-feedback-triage`, or `$focused-debugging`. The full upstream Superpowers chain remains optional and separate.

Evaluate behavior guidance with `vanilla`, exact upstream, and lean-adaptation variants. Compare task success and safety first, then total tokens, latency, tool calls, and unnecessary checks. Keep measured quality gains and remove unmeasured ceremony.

## Source Boundaries

- Catalog source: `skills/<skill-name>` in this repository.
- Runtime copy: `~/.codex/skills/<skill-name>`.
- Template files: `skills/_template/*.template`; these are not installable skills.
- System validator: `~/.codex/skills/.system/skill-creator/scripts/quick_validate.py`.
- Original catalog/vendor skills keep attribution and license notes in their own directory.
- Hun-specific workflow belongs in wrapper skills, not in upstream-preserved catalog/vendor skills.

Keep private paths, credentials, MCP endpoints, auth state, browser profiles, and
machine-specific trust settings out of tracked files. Public docs may mention
`~/.codex/skills`, but they must not record a personal absolute home path.

## Matt Pocock Subset

This catalog reviewed `mattpocock/skills` at immutable commit
`2ab958093e83e0ec752e6c1c5932da465bf23e0c` and selected only `handoff`.

Install target: `~/.codex/skills/handoff`

`handoff` is explicit-use only. It is suitable when the user asks for a compact
continuation document for a fresh session. It does not invoke implicitly and
does not add background-agent, Git, browser, or test orchestration.

The broader `research`, `tdd`, `diagnosing-bugs`, and `code-review` packages are
not separate catalog or runtime defaults. Their automatic triggers, setup
dependencies, and orchestration cost would recreate the global workflow burden
this catalog is designed to avoid.

Remember: memory is a recall layer, not a source of truth. If memory, ChatGPT
Pro, or another external review conflicts with repo docs, scripts, tests,
AGENTS files, or observed runtime output, the current project source wins.

Private project skills such as auto-eva belong in local runtime skill homes, not
this public catalog. Use `~/.codex/skills` for Codex and `~/.claude/skills` for
Claude Code. Keep templates and public-safe process guidance in git; keep
private access paths, credentials, auth state, browser profiles, customer data,
and machine-specific trust settings local.

## Catalog Workflow

1. Run `git status --short --branch`.
2. Stop if there are uncommitted changes or untracked files, unless Hun has already approved how to handle them.
3. Read `skills/README.md`.
4. Inspect the selected skill directory.
5. Check whether `~/.codex/skills/<skill-name>` already exists.
6. Compare the catalog copy with the installed runtime copy.
7. Ask before installing or overwriting the runtime copy.
8. Install only the approved skill.
9. Run `quick_validate.py` against the installed runtime copy.
10. Report changed files, install target, validation result, and any remaining risk.

If a project depends on a skill, keep a minimal source-of-truth pointer in that
project's `AGENTS.md` or project docs. Do not put all routing knowledge only in
global skills; that creates trigger ambiguity and makes the repo harder to
operate without the same local runtime.

## Skill QA Contract

Classify the skill as workflow or performance work. Define its result, route,
evidence, and stop condition; then run the validator and the lowest-cost direct
behavioral evidence. Benchmark a performance skill against vanilla under fixed
runtime inputs. Demonstrate a workflow skill with one deterministic capability
case when practical. Scan only shareable surfaces that can carry private data,
and compare a runtime copy when installation or synchronization is in scope.

## Validation

The skill validator imports `yaml`, so on systems where Python is PEP 668
protected or lacks PyYAML, use a disposable virtual environment instead of
modifying system Python.

```bash
python3 -m venv /tmp/codex-skill-validate-pyyaml
/tmp/codex-skill-validate-pyyaml/bin/python -m pip install PyYAML
/tmp/codex-skill-validate-pyyaml/bin/python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/<skill-name>
```

If validation cannot run, report the exact error and do not claim the skill is
installed correctly.

## Public Base Skill

`karpathy-guidelines` should stay close to the upstream skill. It exists to
reduce common coding-agent mistakes: hidden assumptions, unnecessary
abstractions, broad diffs, and vague success criteria. Preserve its source
attribution instead of modifying it for local policy.

Use this as the first skill to consider for general coding, review, and
refactoring work.

## Optional Codex Collaboration Skill

`chatgpt-collaboration-harness` is available when Codex should coordinate with
ChatGPT Pro as a reviewer, delegated worker, Search Mode or deep research
researcher, bounded web-task agent, screenshot/file exchange partner, or final
reviewer. It is useful for broad, staged, research-heavy, or review-heavy work,
but it is not a default bootstrap skill.

Use it only after approving the sharing scope. Do not share files, diffs, logs,
URLs, browser state, or private data with ChatGPT Pro unless the sharing scope
is approved.

Use `references/file-artifact-exchange.md` when the stage needs approved
screenshots, files, and generated artifacts. Downloaded artifacts stay untrusted
until Codex validates them locally.

The skill requires source-backed evidence. ChatGPT Pro must not answer from
inference alone when project source behavior, official documentation, rankings,
preferences, or public sentiment matter. Technical claims should prefer local
project source, reproducible evidence, official docs, primary sources, release
notes, specifications, and source-backed research. Preference, popularity,
adoption, or taste claims may use community-sentiment evidence, but those
signals must be labeled separately from official facts.

By default, ChatGPT Pro prompts and Codex summaries should be in Korean unless
Hun asks for another language or the deliverable requires it.

## Hun-Local Wrapper

`hun-engineering-loop` is the Hun-local wrapper. Use it in Hun's own runtime to
convert a rough request into the smallest complete result, follow current target
evidence, preserve the high-risk stop/ask boundary, use delegation only for
clear leverage, and stop when direct evidence proves the finish line.

The high-risk stop/ask boundary applies even when the host has broad access.
Stop and ask before destructive deletion, credential or permission changes,
production/deployment/billing actions, external account changes, public
sharing, auth state or browser profile changes, history rewrites, hook bypasses,
or disabling tests.

Use permission profiles, hooks, or approval layers as deferred implementation
tools, not a replacement for judgment. Use them where the host supports them,
but do not make broad access the default recommendation in public templates.

## Project Skill Template

Use `skills/_template` for project workflow skills. Each project skill should
include:

- `Result`
- `Route`
- `Evidence`
- `Stop`

New catalog skills default to explicit invocation. Enable implicit invocation
only for a measured performance skill whose representative benchmark justifies
its ongoing prompt and execution cost.

## Multi-Project Use

The global skill can be used from multiple projects, but project state must
remain separate.

- Use one goal per project.
- Use one ChatGPT work tab or conversation per project.
- Keep one approved external sharing scope per project.
- Keep validation records per project.
- Do not mix unrelated repository context in the same ChatGPT conversation.
- Do not let multiple sessions edit the same repo, branch, or file without coordination.

## When To Add More Skills

Add a cataloged skill only when the workflow is reusable across projects and
should be discoverable later. Do not create a skill for one-off implementation
details, private project notes, or mechanical checks that should be automated
instead.
