# Claude Code Skills

This guide mirrors only the public-safe part of the repository skill catalog
into Claude Code. The workflow is browse, review, select, install.

Claude Code runtime skills live under:

```text
~/.claude/skills/<skill-name>
```

Do not install every skill automatically. Inspect the catalog source, compare it
with any installed runtime copy, ask Hun before installing or overwriting, then
validate the installed copy.

## Source Boundaries

- Catalog source: `skills/<skill-name>` in this repository.
- Claude Code runtime copy: `~/.claude/skills/<skill-name>`.
- Codex runtime copy: `~/.codex/skills/<skill-name>`.
- Private project skills belong in local runtime homes, not in this public repo.
  Treat private project skills as local-only runtime state.

Keep private access paths, credentials, auth state, browser profiles, customer
data, MCP endpoints, and machine-specific trust settings out of git.

## Public Claude Code Default Skill Set

The public Claude Code default skill set is intentionally small:

- `karpathy-guidelines`: portable upstream/vendor behavior for reducing common
  coding-agent mistakes.

Hun's own Claude Code runtime may also install the compact `hun-engineering-loop` and leave both core guidance skills active. Other users should keep the Hun-specific wrapper outside their default set.

Do not install `hun-engineering-loop` as part of the public default. It is a
compact Hun-local result router for rough instructions, current evidence,
approval boundaries, efficient delegation, and proportionate proof. It can
exist in Hun's private runtime when Hun explicitly approves that local setup.

Do not install `chatgpt-collaboration-harness` into Claude Code. It is cataloged
because it is useful for Codex-led ChatGPT Pro collaboration, but it assumes
Codex-owned local validation and browser coordination.

## Lean Explicit Workflows

The following public-safe Superpowers adaptations may be installed selectively:

- `isolated-worktree`
- `execute-plan`
- `review-feedback-triage`
- `focused-debugging`

Their trigger text requires explicit use. Invoke the selected skill with `/isolated-worktree`, `/execute-plan`, `/review-feedback-triage`, or `/focused-debugging`. They do not enable the full upstream Superpowers planning, test, review, delegation, or branch-finishing chain.

## Install Or Sync A Skill

From the repository root:

```bash
git status --short --branch
```

Stop if there is uncommitted or untracked user work unless Hun has already
approved how to handle it.

Inspect the source and any installed runtime copy:

```bash
ls skills/karpathy-guidelines
test -e ~/.claude/skills/karpathy-guidelines && diff -ru skills/karpathy-guidelines ~/.claude/skills/karpathy-guidelines || true
```

After Hun approves installing or overwriting, copy only the selected public-safe
skill:

```bash
SKILL_BACKUP_DIR=~/.claude/skill-backups/YYYYMMDDTHHMMSSZ
mkdir -p "$SKILL_BACKUP_DIR" ~/.claude/skills
test ! -e ~/.claude/skills/karpathy-guidelines || \
  mv ~/.claude/skills/karpathy-guidelines "$SKILL_BACKUP_DIR/"
cp -R skills/karpathy-guidelines ~/.claude/skills/karpathy-guidelines
```

Do not use a broad copy command that installs all catalog skills.

## Validate

Use the same skill validator used for Codex skills. It imports `yaml`, so use a
disposable PyYAML environment when system Python lacks PyYAML:

```bash
python3 -m venv /tmp/codex-skill-validate-pyyaml
/tmp/codex-skill-validate-pyyaml/bin/python -m pip install PyYAML
/tmp/codex-skill-validate-pyyaml/bin/python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.claude/skills/karpathy-guidelines
diff -ru skills/karpathy-guidelines ~/.claude/skills/karpathy-guidelines
```

If validation cannot run, report the exact error and do not claim the Claude
Code skill copy is ready.

## Report

Summarize:

- selected skill names
- runtime target paths
- whether an existing runtime copy was overwritten
- validator result
- repo test result
- any skipped skill and why
