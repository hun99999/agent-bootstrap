# Global Guardrail Setup

Global guardrail setup means installing the shared operating model into the current harness' user-level defaults so new projects start with the same baseline.

It does not mean every repository receives committed guardrail files. Repositories still need project-local knowledge only when the project has facts that the global baseline cannot know.

## Mental Model

- Global layer: user-level defaults for Codex or Claude Code.
- Project layer: project-local knowledge, local commands, architecture notes, and optional `.audit/` evidence.
- Session layer: the currently running agent context.

The global layer gives every new session the same engineering rules: pre-write lens, TDD write gate, post-write review, search before creating helpers, no silent fallback, mocks only at external boundaries, and no private local artifacts in commits.

The project layer gives the agent facts that are unique to one repository: module boundaries, source-of-truth types, commands, error boundaries, and known hotspots.

The session layer may already be loaded before a new global install happens. New sessions should pick up the new user-level defaults. Existing sessions may need a restart or a manual prompt that tells them to read the new guardrail docs.

In short: install globally for new sessions, then use project-local knowledge for the facts that only one repository knows.

Before running an installer or renderer, stop. Ask the user what name the active agent should use.
Keep the chosen name local. Substitute it for `<chosen-name>`, and do not commit the chosen name or
any rendered identity file that contains it. Inspect the active runtime's models and reasoning
levels. Do not hard-code a latest model or paid-plan ceiling.

## Codex Global Setup

Codex uses `~/.codex` for user-level defaults and `~/.agents/skills/superpowers` for shared Superpowers skill discovery.

Run this from the repository root:

```bash
bash .codex/install.sh --partner-name "<chosen-name>"
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
python3 scripts/render_claude_plugin.py --partner-name "<chosen-name>"
```

Then inside Claude Code:

```text
/plugin marketplace add /absolute/path/to/this/repo
/plugin install process-first-agents@agent-bootstrap
```

The Claude Code plugin carries the same shared constitution and role prompt bodies that Codex uses. New Claude Code sessions should use those user-level defaults after the plugin is installed or updated.

## Legacy Surfaces

OpenCode and OpenClaw are legacy/reference material in this repository, not
current first-class setup targets. Do not run legacy installers or route new
setup work through those files unless the user explicitly asks to restore that
support.

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

## Optional Tooling Decision Rules

Optional tools are helpers, not guardrails by themselves. Never install a tool just because a guide mentions it.

Use this rule set whenever an agent sets up a new repository, a new machine, or a new coding harness:

1. Inventory first.
2. Decide whether the tool is necessary for the current repository and task.
3. Recommend when the tool would materially improve structural memory, evidence, or daily ergonomics.
4. Ask before installing any new desktop app, CLI, plugin, browser extension, or package manager dependency.
5. Install only through a verified current source or a package manager query run in the target environment.
6. Verify the install after it finishes.
7. Record only the project-safe usage rule in project-local knowledge.
8. Skip installation when the repository can get the same benefit from existing docs, `local.md`, plain Markdown notes, or native repo tooling.

The agent should explain the decision in plain terms:

- Required: the repo cannot reasonably follow the requested workflow without it.
- Recommended: it reduces repeated context gathering or catches structural drift, but the workflow still works without it.
- Optional: useful for some users, not needed for the current task.
- Skip installation: the tool is unrelated, too heavy for the repo size, already covered by native tooling, or would add private/machine-specific state.

### Obsidian

Obsidian is useful when the team or individual wants a durable project wiki/index outside the agent session. It is not required for the guardrails.

Use Obsidian when:

- the repository is large enough that repeated architecture rediscovery wastes time
- the user wants a private cross-project vault for local project maps
- project knowledge includes personal paths or context that should not be committed
- the workflow needs a searchable index of module boundaries, source-of-truth files, decisions, and known hotspots

Skip Obsidian when:

- a committed `docs/architecture.md`, repo `AGENTS.md`, or untracked `local.md` is enough
- the project is small and structure can be inspected quickly
- the user does not want another desktop app
- the target environment is headless and only needs Markdown files

macOS check:

```bash
test -d /Applications/Obsidian.app && echo "Obsidian is installed" || echo "Obsidian is not installed"
```

macOS install options after user approval:

- Official installer: download from <https://obsidian.md/download>.
- Homebrew cask, when Homebrew is already trusted in that environment:

```bash
brew install --cask obsidian
```

Windows PowerShell check:

```powershell
winget list --name Obsidian
```

Windows PowerShell install flow after user approval:

```powershell
winget search Obsidian
winget install --exact --id Obsidian.Obsidian
```

On Windows, verify the package name and publisher from `winget search Obsidian` before installing. If `winget` is missing, follow Microsoft's current WinGet/App Installer instructions or use the official Obsidian download page. Do not guess installer URLs, registry paths, or native PowerShell flags.

After installing Obsidian, do not commit vault paths. A safe project-local note should say only where the project map lives relative to the repo, or that the private vault has an index the user can paste when needed.

### Lumin Repo Lens

Lumin Repo Lens is useful for TypeScript and JavaScript repositories where AST-backed structure evidence would help catch duplicate helpers, hidden coupling, unmanaged re-exports, and fan-in/fan-out hotspots.

Use Lumin Repo Lens when:

- the target repository is TS/JS-heavy
- the change touches module boundaries, public APIs, re-exports, or shared types
- the repo is large enough that manual import/fan-out inspection is unreliable
- local `.audit/` evidence will help the agent explain and review the change

Skip Lumin Repo Lens when:

- the repository is not TS/JS
- the task is a tiny isolated edit
- native repo tooling already provides the needed import graph or architecture check
- the user does not approve installing an optional plugin or skill

Before running it in a target repository, make sure `.audit/` is ignored if the tool may write local artifacts.

### Dependency And Complexity Tooling

Dependency lint, strict type checks, cycle detection, complexity limits, and file/function size limits are strong guardrails. They are also real tooling changes.

Add them only when one of these is true:

- the repository already has the relevant toolchain and you are tightening an existing rule
- the user explicitly approves adding the tool
- the repository's documented standards already require that tool

Otherwise, document the recommended rule and leave installation for a separate approved task.

## macOS

The Codex installer is a shell script:

```bash
bash .codex/install.sh --partner-name "<chosen-name>"
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

The Codex installer is a shell script. On Windows, run it in an environment that supports the target harness and shell behavior, such as WSL or Git Bash, unless the harness provides native Windows instructions. Do not invent native PowerShell installer flags that this repository does not implement.

## Updating

After pulling changes in this repository:

```bash
bash .codex/install.sh --partner-name "<chosen-name>"
python3 scripts/render_claude_plugin.py --partner-name "<chosen-name>"
python3 scripts/audit_agent_stack.py
```

Run only the installers for the harnesses you actually use.

## What To Tell Other Sessions

New sessions should use the installed global defaults.

Existing sessions may keep their already-loaded prompt context. If a session is already working, either restart it or paste a focused instruction that tells it to apply the newly installed guardrails.

Use [../prompts/start-with-vibe-coding-guardrails.md](../prompts/start-with-vibe-coding-guardrails.md) for project work after the global setup exists.
