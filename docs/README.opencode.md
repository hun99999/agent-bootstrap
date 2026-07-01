# OpenCode Legacy Notes

OpenCode is legacy/reference material in this repository, not a current first-class setup target.

The current public setup path is Codex or Claude Code. Do not run the OpenCode installer for a fresh setup unless Hun explicitly asks for legacy migration or restoration work.

## Preserved Files

The repository still contains older OpenCode files so prior work can be audited:

- `.opencode/install.py`
- `.opencode/install.sh`
- `.opencode/INSTALL.md`
- `prompts/setup-opencode-current-harness.md`
- `tests/test_opencode_install.py`

Those files are compatibility/reference material. They should not appear in the
root README as a normal install path.

## If Hun Explicitly Restores OpenCode Work

Before touching OpenCode files:

1. Run `git status --short --branch`.
2. Confirm the request is legacy OpenCode migration or restoration, not normal setup.
3. Read the preserved installer and tests.
4. Do not change Codex or Claude Code behavior unless the request explicitly says so.
5. Run the relevant legacy tests and the full repository test suite.

```bash
python3 -m unittest tests.test_opencode_install -v
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Audit

`python3 scripts/audit_agent_stack.py` no longer checks OpenCode by default. That
is intentional: OpenCode is not a current supported surface.
