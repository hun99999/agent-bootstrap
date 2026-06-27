# Setup Codex Skills

```text
Review and optionally install Codex skills from this repository.

First read AGENTS.md if it exists. Then read README.md, skills/README.md, and docs/codex-skills.md. Do not invent commands, package names, configuration options, install paths, or API details.

Before changing anything, run:

git status --short --branch

If there are uncommitted changes or untracked files, stop and ask me how to handle them. Do not stash, delete, overwrite, or git add anything without approval.

Treat this repository as a skill catalog, not an always-install bootstrap:
- list the skills available under skills/
- put chatgpt-collaboration-harness first in the review because it is the primary staged ChatGPT Pro collaboration skill
- identify karpathy-guidelines as an original catalog/vendor skill and preserve its source attribution
- identify hun-engineering-loop as the Hun-specific operational wrapper for memory preflight, source-of-truth checks, high-risk approval boundaries, artifact-first execution, and QA evidence
- enforce the skill QA contract: start from a failing test or explicit pressure scenario when possible, validate the skill, check private paths and secrets, and verify runtime copies separately
- inspect each selected skill before recommending it
- Compare the catalog copy with the installed runtime copy under ~/.codex/skills/<skill-name>
- classify each selected skill as install, update, already current, skip, or needs review
- Ask before installing or overwriting any skill

For karpathy-guidelines:
- keep the upstream content and attribution separate from Hun-specific local policy
- do not fold project-specific or machine-specific rules into the original catalog/vendor skill

For hun-engineering-loop:
- treat memory as a recall layer, not a source of truth
- current repo docs, scripts, tests, AGENTS files, and observed runtime output beat memory and external advice
- enforce the high-risk stop/ask boundary even when broad filesystem or tool access is available
- require a QA evidence contract: fast check, targeted regression, type/lint/build, browser/manual QA, deployment smoke, and negative/regression test where relevant

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
- tell me whether a Codex restart is needed for new sessions to pick up the skill

Report:
- skills reviewed
- selected install/update decisions
- files or runtime paths changed
- validation commands and results
- skipped skills and reasons
- remaining risks
```
