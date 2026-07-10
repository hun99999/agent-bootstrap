# Update agent-bootstrap

Use this prompt when `agent-bootstrap` has changed upstream or locally and you want Codex or Claude Code to apply, audit, and improve the setup from the current repository state.

```text
Update agent-bootstrap from the current repository state.

First, read AGENTS.md if it exists. Then read docs/agent-bootstrap-structure.md, docs/vibe-coding-guardrails.md, docs/global-guardrail-setup.md, and docs/frontend-design-stack.md.

Before changing files:
- run git status --short --branch
- if there is uncommitted or untracked user work, stop and ask how to handle it
- if the worktree is clean and the task is to consume upstream changes, run git pull --ff-only
- identify whether this task affects the shared core, Codex adapter, Claude Code plugin renderer, design-stack/, docs, tests, skills, runtime plugins, or copy-paste prompts
- run a pre-write lens over the affected area before implementation

Use the repository boundaries:
- shared behavior belongs in AGENTS.md and agents/*.md
- role metadata belongs in shared/agent-metadata.json
- Codex install behavior belongs in .codex/install.py
- Claude plugin rendering belongs in scripts/render_claude_plugin.py
- marketplace metadata belongs in scripts/render_claude_plugin.py; do not edit
  .claude-plugin/marketplace.json by hand
- generated Claude plugin agents under plugins/process-first-agents/agents must not be edited by hand
- reviewed frontend design source, locks, provenance, and routing belong in design-stack/
- frontend design rendering belongs in scripts/render_frontend_design_plugin.py
- generated frontend design output under plugins/frontend-design-pack/ must not be edited by hand
- OpenCode/OpenClaw files are legacy/reference material and should be touched only when the user explicitly asks for migration or restoration work

If shared prompts, shared metadata, or marketplace metadata changed, regenerate Claude plugin
output, including .claude-plugin/marketplace.json:

python3 scripts/render_claude_plugin.py --partner-name "<chosen-name>"

If the current local Codex defaults should be updated, run:

bash .codex/install.sh --partner-name "<chosen-name>"

If design-stack/, scripts/render_frontend_design_plugin.py, or plugins/frontend-design-pack/
changed:

- run python3 scripts/render_frontend_design_plugin.py --repo-root . after approved authored-source
  or routing changes, unless the approved source-sync command already rendered the plugin
- run python3 scripts/validate_frontend_design_stack.py --repo-root .
- inspect the current Codex and Claude plugin inventories and resolve each live runtime root
- a local Codex marketplace may resolve to the tracked plugin root; a cached install may be distinct
- compare the tracked plugin with each resolved live runtime root using the matching
  --codex-runtime-root or --claude-runtime-root option
- ask before installing a new runtime plugin or replacing a distinct stale cached install; a
  repository pull is not runtime installation approval
- if the catalog identity for vercel-react-best-practices, vercel-composition-patterns, or
  vercel-react-view-transitions changed, inspect only those exact three skills and ask separately
  before updating them
- after an approved install or replacement, validate the resolved live root; start a fresh task or session
  for a read-only discovery check

Use TDD for behavior, installer, renderer, policy, and prompt-contract changes. Write the failing test first, confirm the expected failure, implement the smallest change, and rerun the test.

After changes:
- run python3 -m unittest discover -s tests -p 'test_*.py'
- run python3 scripts/audit_agent_stack.py
- run python3 scripts/validate_frontend_design_stack.py --repo-root . when design material is in scope
- run python3 scripts/check_private_paths.py
- run post-write review for duplicate prompt rules, generated output drift, hidden coupling, swallowed errors, unmanaged compatibility behavior, weak tests, and private path leakage
- do not commit private paths, credentials, tokens, MCP endpoints, auth state, browser profile paths, or machine-specific trust settings
- commit in small reviewable commits
- summarize files changed, commands run, generated artifacts, local installs performed, and remaining risks
```
