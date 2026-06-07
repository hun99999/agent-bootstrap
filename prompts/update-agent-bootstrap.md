# Update agent-bootstrap

Use this prompt when `agent-bootstrap` has changed upstream or locally and you want Codex, Claude Code, or another coding agent to apply, audit, and improve the setup from the current repository state.

```text
Update agent-bootstrap from the current repository state.

First, read AGENTS.md if it exists. Then read docs/agent-bootstrap-structure.md, docs/vibe-coding-guardrails.md, and docs/global-guardrail-setup.md.

Before changing files:
- run git status --short --branch
- if there is uncommitted or untracked user work, stop and ask how to handle it
- if the worktree is clean and the task is to consume upstream changes, run git pull --ff-only
- identify whether this task affects the shared core, Codex adapter, Claude Code plugin renderer, OpenCode adapter, docs, tests, or copy-paste prompts
- run a pre-write lens over the affected area before implementation

Use the repository boundaries:
- shared behavior belongs in AGENTS.md and agents/*.md
- role metadata belongs in shared/agent-metadata.json
- Codex install behavior belongs in .codex/install.py
- OpenCode install behavior belongs in .opencode/install.py
- Claude plugin rendering belongs in scripts/render_claude_plugin.py
- generated Claude plugin agents under plugins/process-first-agents/agents must not be edited by hand

If shared prompts or metadata changed, regenerate Claude plugin output:

python3 scripts/render_claude_plugin.py --partner-name "<Name>"

If the current local Codex defaults should be updated, run:

bash .codex/install.sh --partner-name "<Name>"

If the current local OpenCode defaults should be updated, run:

bash .opencode/install.sh --partner-name "<Name>"

Use TDD for behavior, installer, renderer, policy, and prompt-contract changes. Write the failing test first, confirm the expected failure, implement the smallest change, and rerun the test.

After changes:
- run python3 -m unittest discover -s tests -p 'test_*.py'
- run python3 scripts/audit_agent_stack.py
- run post-write review for duplicate prompt rules, generated output drift, hidden coupling, swallowed errors, unmanaged compatibility behavior, weak tests, and private path leakage
- do not commit private paths, credentials, tokens, MCP endpoints, auth state, browser profile paths, or machine-specific trust settings
- commit in small reviewable commits
- summarize files changed, commands run, generated artifacts, local installs performed, and remaining risks
```
