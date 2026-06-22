# Codex Skills

This repository includes a Skill Catalog for Codex skills that may be useful across projects.

The workflow is browse, review, select, install. The repo copy is the catalog source. The installed copy is the runtime copy used by Codex under `~/.codex/skills/<skill-name>`.

Do not install every skill automatically. A setup agent should inspect this repository's catalog, compare a selected skill with the installed runtime copy, explain the change, ask Hun before installing or overwriting, and then validate the installed skill.

## Source Boundaries

- Catalog source: `skills/<skill-name>` in this repository.
- Runtime copy: `~/.codex/skills/<skill-name>`.
- Template files: `skills/_template/*.template`; these are not installable skills.
- System validator: `~/.codex/skills/.system/skill-creator/scripts/quick_validate.py`.

Keep private paths, credentials, MCP endpoints, auth state, browser profiles, and machine-specific trust settings out of tracked files. Public docs may mention `~/.codex/skills`, but they must not record a personal absolute home path.

## Catalog Workflow

1. Run `git status --short --branch`.
2. Stop if there are uncommitted changes or untracked files, unless Hun has already approved how to handle them.
3. Read `skills/README.md`.
4. Inspect the selected skill directory.
5. Check whether `~/.codex/skills/<skill-name>` already exists.
6. Compare the catalog copy with the installed runtime copy.
7. Ask before installing or overwriting the runtime copy.
8. Install only the approved skill.
9. Run `quick_validate.py` against the installed runtime copy.
10. Report changed files, install target, validation result, and any remaining risk.

## Validation

The skill validator imports `yaml`, so on systems where Python is PEP 668 protected or lacks PyYAML, use a disposable virtual environment instead of modifying system Python.

```bash
python3 -m venv /tmp/codex-skill-validate-pyyaml
/tmp/codex-skill-validate-pyyaml/bin/python -m pip install PyYAML
/tmp/codex-skill-validate-pyyaml/bin/python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/<skill-name>
```

If validation cannot run, report the exact error and do not claim the skill is installed correctly.

## First Catalog Skill

`chatgpt-collaboration-harness` is intentionally listed first because it is useful for broad, staged, research-heavy, or review-heavy work.

Use it when Codex should coordinate with ChatGPT Pro as a reviewer, delegated worker, Search Mode or deep research researcher, or bounded web-task agent. Do not use it for every local edit. Do not share files, diffs, logs, URLs, browser state, or private data with ChatGPT Pro unless the sharing scope is approved.

The skill requires source-backed evidence. ChatGPT Pro must not answer from inference alone when project source behavior, official documentation, rankings, preferences, or public sentiment matter. Technical claims should prefer local project source, reproducible evidence, official docs, primary sources, release notes, specifications, and source-backed research. Preference, popularity, adoption, or taste claims may use community-sentiment evidence, but those signals must be labeled separately from official facts.

By default, ChatGPT Pro prompts and Codex summaries should be in Korean unless Hun asks for another language or the deliverable requires it.

## Multi-Project Use

The global skill can be used from multiple projects, but project state must remain separate.

- Use one goal per project.
- Use one ChatGPT work tab or conversation per project.
- Keep one approved external sharing scope per project.
- Keep validation records per project.
- Do not mix unrelated repository context in the same ChatGPT conversation.
- Do not let multiple sessions edit the same repo, branch, or file without coordination.

## When To Add More Skills

Add a cataloged skill only when the workflow is reusable across projects and should be discoverable later. Do not create a skill for one-off implementation details, private project notes, or mechanical checks that should be automated instead.
