# Open Design On-Demand Provider

Open Design is an optional, third-party-derived inspiration provider. It is never a default source.

## Demand and selection

- Continue only when the user names Open Design. A generic request for good references, an existing
  cache, or a previous task's selection is not demand.
- Require an exact lowercase package slug, or explicit authority to choose one. If the user names
  Open Design without either, list candidates and present at most three labeled options before
  asking for the exact slug.
- Before a network fetch or cache write, report the selected slug, pinned revision, destination
  cache namespace, and that no authentication or upstream code will be used.

## Safe helper flow

The packaged helper is `scripts/open_design_cache.py`; its provider contract is
`references/open-design-provider.json`.

```bash
python3 scripts/open_design_cache.py list --explicit-demand --json
python3 scripts/open_design_cache.py fetch --explicit-demand --slug "<slug>" --json
python3 scripts/open_design_cache.py verify --explicit-demand --slug "<slug>" --json
```

`list` and `fetch` may access the pinned public Git repository. `verify` is offline. Never add a
repository, revision, latest, force, purge, or authentication override. Do not execute the upstream
CLI, install dependencies, run package scripts, or open preview HTML automatically.

Every use begins with `verify`. Load `USAGE.md`, `DESIGN.md`, and `tokens.css` from the returned
package root as needed; inspect components, previews, assets, or source evidence only when the task
requires them. Cache presence never authorizes loading a package in a later task.

## Authority and reuse boundary

Report the source as `open-design:<slug>@<revision>`, authority `optional-provider`, and the exact
files actually read. The provider's root Apache-2.0 notice does not establish redistribution rights
for every package's third-party-derived bytes. Use the package as labeled inspiration. Copying its
code, tokens, assets, or fonts into a project, committing them, or publicly redistributing them
requires separate package-level provenance and license review plus user approval.

Do not replace an established project design system without an explicit material-design decision.
If the cache is corrupt, fail without deleting or overwriting it and ask before any repair.
