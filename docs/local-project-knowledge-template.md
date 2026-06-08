# Local Project Knowledge Template

Copy this template into a project-local `local.md`, an untracked note, or an Obsidian page. Keep private paths, credentials, tokens, MCP endpoints, and auth state out of public repositories.

## Project Purpose

- What the project does:
- Who uses it:
- What correctness means:

## Architecture Map

- Main entrypoints:
- Core domains:
- Adapters or integrations:
- Storage or persistence:
- UI or delivery surfaces:

## Structural Evidence Index

- Last refreshed:
- Scan range:
- Claim rule: state scan range before saying something was not found.
- Confidence or blind spots:
- `.audit/manifest.json`:
- `.audit/audit-summary.latest.md`:
- `.audit/pre-write-advisory.latest.json`:
- `.audit/post-write-delta.latest.json`:
- `docs/current/audit/lumin-structural-audit.md`:
- Canon or source-of-truth docs:
- Files that must be inspected before touching shared helpers:
- Files that must be inspected before changing public APIs:
- Files that must be inspected before changing import topology:
- Local-only notes that should stay untracked:

## Source Of Truth

- Shared utility source of truth:
- Shared type or schema source of truth:
- API contract source of truth:
- Configuration source of truth:

## Module Boundaries

- Domain modules:
- Infrastructure modules:
- UI or presentation modules:
- Test-only support modules:
- Modules that should not import each other:

## Dependency Direction

- Allowed dependency direction:
- Forbidden dependency direction:
- Known cycle risks:
- Tools or commands that check dependency direction:

## Public APIs And Re-Exports

- Public entrypoints:
- Barrel or re-export policy:
- Internal modules that should not be imported directly:
- Compatibility promises:

## Test Strategy

- Unit test command:
- Integration test command:
- End-to-end test command:
- Type check command:
- Lint command:
- Edge cases that must stay covered:
- External boundaries where mocks are allowed:
- Internal behavior that should not be mocked:

## Error Boundaries

- Where errors should be handled:
- Where errors should be allowed to propagate:
- Expected fallback behavior:
- Fallback behavior that is not allowed:

## Known Hotspots

- Large files:
- Large functions:
- High fan-in files:
- High fan-out files:
- Fragile initialization order:
- Global state:

## Commands

```bash
# Replace these with the repository's real commands.
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Decisions

- Current decisions:
- Rejected alternatives:
- Reasons:
- Date and owner:
