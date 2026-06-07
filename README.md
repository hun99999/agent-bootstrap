# agent-bootstrap

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

Bootstrap a process-first AI coding environment for Codex, Claude Code, and OpenCode.

`agent-bootstrap` gives you a shared `superpowers` workflow, role-based subagents, token-efficient execution, and multilingual setup docs for modern AI coding tools.

## Why use agent-bootstrap?

- Shared `superpowers` workflow across Codex, Claude Code, and OpenCode instead of maintaining separate prompt stacks for each tool.
- Role-based subagents and a shared prompt corpus so planning, implementation, review, verification, and release work stay consistent.
- Token-efficient, process-first execution that reduces wasted context by pushing teams toward scoped work, clear handoffs, and reusable skills.
- Native harness adapters instead of one generic installer hack:
  - Codex gets managed `.codex` files plus latest `superpowers`
  - Claude Code gets a plugin marketplace entry plus generated agent plugin package
  - OpenCode gets generated agents plus native plugin wiring
- Public-safe baseline that avoids shipping credentials, private MCP endpoints, personal paths, or machine-specific trust state.
- Multilingual onboarding so English, Korean, Japanese, and Simplified Chinese readers can start from the same repository.

## What This Repository Is

This repository is the source of truth for a shared operating model that can be installed into multiple coding harnesses instead of being tied to Codex alone.

It is aimed at teams and individual developers who want one reusable bootstrap for:

- Codex
- Claude Code
- OpenCode

It also documents how to integrate those tools into OpenClaw, but OpenClaw is intentionally treated as an integration layer rather than a first-class bootstrap target.

## Default Setup Scope

If the user says "set this up from the repo" and does not specify a harness, default to `shared-core-only`.

`shared-core-only` means:

- install or update `superpowers` if the current tool supports it
- install the shared constitution and agent/subagent prompts in the current tool's native format
- avoid picking a new harness, ACP backend, gateway, or provider stack unless the user explicitly asks for it

This matters most for OpenClaw-style setup requests. The correct default is not `Codex-first`, `Claude-first`, or `OpenCode-first`. The correct default is the shared prompt and skills layer only.

## Default Scope Matrix

- Codex: `current-harness-only`
- Claude Code: `current-harness-only`
- OpenCode: `current-harness-only`
- OpenClaw: `shared-core-only`

`current-harness-only` means: if you are already inside Codex, Claude Code, or OpenCode and the user says "set this up from the repo", default to configuring only that current harness. Do not configure another harness unless the user explicitly asks.

## Setup Prompts

These copy-paste prompts are the fastest way to keep another agent inside the intended scope:

- Codex current harness only: [prompts/setup-codex-current-harness.md](prompts/setup-codex-current-harness.md)
- Claude Code current harness only: [prompts/setup-claude-current-harness.md](prompts/setup-claude-current-harness.md)
- OpenCode current harness only: [prompts/setup-opencode-current-harness.md](prompts/setup-opencode-current-harness.md)
- Generic shared core setup: [prompts/setup-shared-core.md](prompts/setup-shared-core.md)
- OpenClaw shared core only: [prompts/setup-openclaw-shared-core.md](prompts/setup-openclaw-shared-core.md)
- OpenClaw ACP integration: [prompts/setup-openclaw-acp.md](prompts/setup-openclaw-acp.md)
- Apply vibe-coding guardrails to another repository: [prompts/apply-vibe-coding-guardrails.md](prompts/apply-vibe-coding-guardrails.md)
- Start work with vibe-coding guardrails: [prompts/start-with-vibe-coding-guardrails.md](prompts/start-with-vibe-coding-guardrails.md)
- Update this bootstrap after repository changes: [prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md)

## Vibe Coding Guardrails

Use [docs/global-guardrail-setup.md](docs/global-guardrail-setup.md) when you want these guardrails installed as Codex, Claude Code, or OpenCode user-level defaults across projects.

Use [docs/vibe-coding-guardrails.md](docs/vibe-coding-guardrails.md) when you want Codex, Claude Code, or OpenCode to apply a pre-write lens, TDD write gate, and post-write structure review to a repository.

For project-specific context, copy [docs/local-project-knowledge-template.md](docs/local-project-knowledge-template.md) into a local `local.md`, an untracked note, or a private Obsidian page. Keep private paths, credentials, MCP endpoints, auth state, and machine-specific trust settings out of the public baseline.

Codex session opener for standing delegation preference:

```text
In this session, you may use sub-agents or parallel agents for independently separable work when that clearly improves efficiency. This is permission, not a requirement: if the work is small, tightly coupled, immediately blocking, or the delegation overhead is not worth it, stay local instead.
```

## Install Guides

- Codex: [docs/README.codex.md](docs/README.codex.md)
- Claude Code: [docs/README.claude.md](docs/README.claude.md)
- OpenCode: [docs/README.opencode.md](docs/README.opencode.md)
- OpenClaw integration: [docs/README.openclaw.md](docs/README.openclaw.md)

## Architecture

The repository is split into two layers:

- shared core
  - `AGENTS.md`
  - `agents/*.md`
  - `shared/agent-metadata.json`
  - common process-first constitution and role prompt bodies
- harness adapters
  - `.codex/`
  - `.claude-plugin/`
  - `.opencode/`

The shared core defines the operating model once.
Each adapter translates that core into the native format expected by the target harness.

For the detailed project-local structure map, update flow, source-of-truth boundaries, and generated-artifact policy, read [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md).

## Superpowers Integration

This bootstrap is built around `obra/superpowers`.

- Codex uses the native `~/.agents/skills/superpowers` symlink pattern.
- OpenCode uses the native plugin line `superpowers@git+https://github.com/obra/superpowers.git`.
- Claude Code is split into:
  - upstream official `superpowers` for the skills library
  - this repository's Claude plugin package for the shared agent prompts

Codex App can use the Codex App curated Superpowers plugin; the installer still supports the manual ~/.codex/superpowers fallback for local skill discovery. Avoid enabling both discovery paths unless duplicate skill entries are intentional.

The intent is to reuse upstream `superpowers` instead of copying the skill library into this repository.

## Repository Layout

- `AGENTS.md`
  - shared constitution template
- `agents/`
  - shared role prompt bodies
- `shared/agent-metadata.json`
  - shared descriptions and OpenCode capability metadata
- `.codex/`
  - Codex installer, templates, and install guide
- `.opencode/`
  - OpenCode installer, templates, and install guide
- `.claude-plugin/marketplace.json`
  - repository-level Claude marketplace entry
- `plugins/process-first-agents/`
  - generated Claude plugin package
- `scripts/render_claude_plugin.py`
  - rebuilds the Claude plugin package from the shared prompt corpus
- `docs/`
  - harness-specific guides, repository metadata guidance, and OpenClaw notes
- `tests/`
  - Python verification for installers, plugin metadata, and README expectations

## Discoverability

GitHub repository discoverability is driven more by repository metadata than by classic web SEO.

This repository improves discoverability through:

- a keyword-rich canonical README
- multilingual README variants
- GitHub repository description and topics
- documented social preview guidance in [docs/repo-metadata.md](docs/repo-metadata.md)

## Constraints

This repository should contain only the baseline setup that is safe to share publicly.

Keep these out:

- private MCP endpoints
- personal project paths
- organization-specific secrets
- machine-specific trust configuration
- credentials, tokens, or auth state

## Updating

- Codex and OpenCode: re-run the harness installer after pulling
- Claude Code: re-run `python3 scripts/render_claude_plugin.py --partner-name "<Name>"` after pulling, then update the local plugin installation

## Agent Stack Audit

Run the local audit before or after updates to check Codex, Claude Code, OpenCode, and Superpowers state:

```bash
python3 scripts/audit_agent_stack.py
```

The default audit is offline and read-only. Add `--online` when you explicitly want npm and remote git drift checks, and add `--strict` when missing optional tools such as OpenCode should fail the audit.

## Legacy Files

Some files from the earlier Codex-only bootstrap still exist during the transition:

- `codex-home/`
- `scripts/install.py`
- `scripts/install.sh`
- `prompts/fresh-install.md`

They are compatibility entrypoints, not the long-term multi-harness architecture.

## Testing

Installer and metadata tests use Python's `unittest`:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
