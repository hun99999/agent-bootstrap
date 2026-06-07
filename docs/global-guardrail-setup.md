# Global Guardrail Setup

Global guardrail setup means installing the shared operating model into the current harness' user-level defaults so new projects start with the same baseline.

It does not mean every repository receives committed guardrail files. Repositories still need project-local knowledge only when the project has facts that the global baseline cannot know.

## Mental Model

- Global layer: user-level defaults for Codex, Claude Code, or OpenCode.
- Project layer: project-local knowledge, local commands, architecture notes, and optional `.audit/` evidence.
- Session layer: the currently running agent context.

The global layer gives every new session the same engineering rules: pre-write lens, TDD write gate, post-write review, search before creating helpers, no silent fallback, mocks only at external boundaries, and no private local artifacts in commits.

The project layer gives the agent facts that are unique to one repository: module boundaries, source-of-truth types, commands, error boundaries, and known hotspots.

The session layer may already be loaded before a new global install happens. New sessions should pick up the new user-level defaults. Existing sessions may need a restart or a manual prompt that tells them to read the new guardrail docs.

In short: install globally for new sessions, then use project-local knowledge for the facts that only one repository knows.

## Codex Global Setup

Codex uses `~/.codex` for user-level defaults and `~/.agents/skills/superpowers` for shared Superpowers skill discovery.

Run this from the repository root:

```bash
bash .codex/install.sh --partner-name "Hun"
python3 scripts/audit_agent_stack.py
```

The Codex installer writes:

- `~/.codex/AGENTS.md`
- `~/.codex/local.md`
- `~/.codex/config.toml`
- `~/.codex/agents/*.md`
- `~/.codex/agents/*.toml`
- `~/.codex/superpowers`
- `~/.agents/skills/superpowers`

Those files are the user-level defaults for new Codex sessions. After installing, start new Codex sessions for the cleanest pickup.

For existing sessions, paste this short instruction:

```text
Use the global vibe-coding guardrails now installed from agent-bootstrap. Before continuing, apply the pre-write lens, TDD write gate, and post-write review rules from the updated global AGENTS.md. Search before creating helpers/types/shapes, do not add silent fallback behavior, keep mocks at external boundaries, and do not commit local evidence artifacts or private paths.
```

## Claude Code Global Setup

Claude Code uses a Claude Code plugin to provide user-level defaults for the shared agents.

Recommended setup:

1. Install the upstream Superpowers plugin from Claude Code's official marketplace.
2. Clone this repository.
3. Render this repository's Claude Code plugin bundle.
4. Add this repository as a Claude Code plugin marketplace.
5. Install the `process-first-agents` Claude Code plugin.

Commands from the repository root:

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
```

Then inside Claude Code:

```text
/plugin marketplace add /absolute/path/to/this/repo
/plugin install process-first-agents@agent-bootstrap
```

The Claude Code plugin carries the same shared constitution and role prompt bodies that Codex and OpenCode use. New Claude Code sessions should use those user-level defaults after the plugin is installed or updated.

## OpenCode Global Setup

OpenCode uses `~/.config/opencode` for user-level defaults.

Run this from the repository root:

```bash
bash .opencode/install.sh --partner-name "Hun"
```

The OpenCode installer writes:

- `~/.config/opencode/opencode.json`
- `~/.config/opencode/agents/*.md`

The config enables the upstream Superpowers plugin line and renders this repository's shared agent prompts as OpenCode agents. New OpenCode sessions should use those user-level defaults.

## Project-Local Knowledge

Use [local-project-knowledge-template.md](local-project-knowledge-template.md) when a repository needs its own map.

Good project-local facts:

- module boundaries
- source-of-truth helpers, types, shapes, schemas, and public APIs
- dependency direction
- test, lint, type check, and build commands
- public API and re-export policy
- error boundaries
- known hotspots
- rejected alternatives and architectural decisions

Keep these out of public repositories:

- personal Obsidian vault paths
- private project paths
- credentials and tokens
- MCP endpoints
- auth state
- machine-specific trust settings

## macOS

Codex and OpenCode installers are shell scripts:

```bash
bash .codex/install.sh --partner-name "Hun"
bash .opencode/install.sh --partner-name "Hun"
```

Claude Code plugin installation happens inside Claude Code after rendering the plugin bundle with Python.

## Windows PowerShell

For this repository's Python tests:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

For repository-local `.audit/` handling:

```powershell
Add-Content -Path .gitignore -Value ".audit/"
```

The Codex and OpenCode installers are shell scripts. On Windows, run them in an environment that supports the target harness and shell behavior, such as WSL or Git Bash, unless the harness provides native Windows instructions. Do not invent native PowerShell installer flags that this repository does not implement.

## Updating

After pulling changes in this repository:

```bash
bash .codex/install.sh --partner-name "Hun"
python3 scripts/render_claude_plugin.py --partner-name "Hun"
bash .opencode/install.sh --partner-name "Hun"
python3 scripts/audit_agent_stack.py
```

Run only the installers for the harnesses you actually use.

## What To Tell Other Sessions

New sessions should use the installed global defaults.

Existing sessions may keep their already-loaded prompt context. If a session is already working, either restart it or paste a focused instruction that tells it to apply the newly installed guardrails.

Use [../prompts/start-with-vibe-coding-guardrails.md](../prompts/start-with-vibe-coding-guardrails.md) for project work after the global setup exists.
