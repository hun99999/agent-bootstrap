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
- inspect each selected skill before recommending it
- Compare the catalog copy with the installed runtime copy under ~/.codex/skills/<skill-name>
- classify each selected skill as install, update, already current, skip, or needs review
- Ask before installing or overwriting any skill

For chatgpt-collaboration-harness, preserve these rules:
- ChatGPT Pro must not answer from inference alone when facts, source behavior, official docs, rankings, preferences, or public sentiment matter
- technical claims should prefer project source, local reproduction evidence, official docs, primary sources, release notes, specifications, and source-backed research
- community sources may be used for preferences, rankings, popularity, taste, adoption, or ecosystem feel, but label them as community-sentiment rather than official fact
- use Korean by default unless I request another language or the deliverable requires another language
- Codex must classify ChatGPT Pro output as accepted, rejected, deferred, or needs-local-verification and verify locally before relying on it
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
