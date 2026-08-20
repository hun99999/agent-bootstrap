# Setup Codex Skills

```text
Review and optionally install Codex skills from this repository.

First read AGENTS.md if it exists. Then read README.md, skills/README.md, and docs/codex-skills.md. Do not invent commands, package names, configuration options, install paths, or API details.

Before changing anything, run:

git status --short --branch

If there are uncommitted changes or untracked files, stop and ask me how to handle them. Do not stash, delete, overwrite, or git add anything without approval.

Treat this repository as a skill catalog, not an always-install bootstrap:
- list the skills available under skills/
- identify karpathy-guidelines as the public base and preserve its source attribution
- identify hun-engineering-loop as the compact Hun-local result router; keep it outside the public default set
- identify isolated-worktree, execute-plan, review-feedback-triage, and focused-debugging as explicit-use lean Superpowers adaptations
- identify chatgpt-collaboration-harness as an optional Codex-only collaboration workflow
- identify handoff as the only reviewed Matt Pocock subset skill; it is explicit-use only and installs to ~/.codex/skills/handoff
- do not add Matt Pocock research, tdd, diagnosing-bugs, or code-review as global defaults
- apply the skill QA contract: classify each selected skill as workflow or performance guidance; benchmark performance claims against vanilla and use one deterministic capability case for a workflow when practical
- validate the skill and inspect shareable surfaces for private paths or secrets; verify a runtime copy only when installation is in scope
- inspect each selected skill before recommending it
- Compare the catalog copy with the installed runtime copy under ~/.codex/skills/<skill-name>
- classify each selected skill as install, update, already current, skip, or needs review
- Ask before installing or overwriting any skill

For karpathy-guidelines:
- keep the upstream content and attribution separate from Hun-specific local policy
- do not fold project-specific or machine-specific rules into the original catalog/vendor skill

For hun-engineering-loop:
- translate rough instructions into the smallest concrete outcome supported by current context
- treat current target evidence as authoritative and load memory only when it changes the next action
- enforce the high-risk stop/ask boundary even when broad filesystem or tool access is available
- delegate only when parallel ownership creates clear leverage
- use the lowest-cost direct evidence that proves the finish line

For the four lean Superpowers adaptations:
- keep policy.allow_implicit_invocation false
- install them selectively and invoke them explicitly
- do not enable the full upstream workflow chain as a side effect
- keep focused-debugging under benchmark because it is performance-oriented; treat the other three as workflow capabilities

For chatgpt-collaboration-harness, preserve these rules:
- ChatGPT Pro must not answer from inference alone when facts, source behavior, official docs, rankings, preferences, or public sentiment matter
- technical claims should prefer project source, local reproduction evidence, official docs, primary sources, release notes, specifications, and source-backed research
- community sources may be used for preferences, rankings, popularity, taste, adoption, or ecosystem feel, but label them as community-sentiment rather than official fact
- use Korean by default unless I request another language or the deliverable requires another language
- Codex must classify ChatGPT Pro output as accepted, rejected, deferred, or needs-local-verification and verify locally before relying on it
- use file-artifact-exchange rules before sharing screenshots, files, and generated artifacts or relying on downloaded artifacts
- keep project goals, ChatGPT work tabs/conversations, approved sharing scopes, and validation records separate across projects

If I approve installation or update:
- install only the approved skill into ~/.codex/skills/<skill-name>
- do not install every skill automatically
- Do not copy private paths, credentials, MCP endpoints, auth state, or browser profiles
- run ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py against the installed skill
- if PyYAML is missing or system Python is protected, use a disposable virtual environment and report the commands used
- start a fresh task to verify discovery; restart Codex only if the new task still does not detect the change

Report:
- skills reviewed
- selected install/update decisions
- files or runtime paths changed
- validation commands and results
- skipped skills and reasons
- remaining risks
```
