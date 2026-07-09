# Frontend Design Stack

This repository packages a reviewed frontend-design environment for Codex and Claude Code. It
exposes one native skill, `frontend-design`, through `frontend-design-pack`; the larger corpus stays
behind a router so an agent loads only the references required by the current surface and mode.

The tracked repository is the review source. An installed plugin is a separate runtime copy. A
successful repository validation does not prove that an older installed copy was refreshed, and an
installed copy does not prove that the tracked plugin is current.

## First-Run Decisions

An agent setting up this repository should perform these steps in order:

1. Run `git status --short --branch` and protect existing work.
2. Ask the user what partner name Codex or Claude Code should use. Keep that value in local rendered
   output; do not commit it to this public repository. If the user has no preference, ask whether
   `Partner` is acceptable.
3. Inspect the active runtimes and inherit the models and reasoning levels they actually support.
   Do not assume a paid plan, a latest model name, or an unavailable reasoning tier. Shared config
   intentionally carries no model pin.
4. Validate the tracked plugin before proposing a runtime change.
5. Read the current plugin lists and report whether Figma is available. Do not authenticate Figma,
   change an account, or install its plugin merely to inspect availability. Authentication is a
   separate approval boundary.
6. Ask before installing, updating, or replacing any runtime plugin copy. Broad filesystem access
   is not installation approval.

## What Is Included

- One router with six modes: Shape, Explore, Implement, Review, Copy, and Harden.
- 95 reviewed MengTo catalog decisions: 90 procedures are included as inert Markdown references;
  5 provenance-gap duplicates resolve to pinned official mappings instead of being republished.
- 74 DESIGN.md references from VoltAgent's collection. These are third-party analysis of public
  interfaces. The Meta and Vercel entries are not guidance published by Meta or Vercel.
- The pinned Google DESIGN.md CLI package contract, currently version `0.3.0`.
- Pinned official Vercel Web Interface Guidelines material with its MIT notice.
- Complete lock, provenance, source authority, and license metadata.

Open Design is on-demand and explicit-demand-only. It is not vendored, installed, or loaded by
default. The Vercel agent-skills source remains reference-only because the reviewed root did not
provide a redistributable license; the MIT-licensed Web Interface Guidelines source supplies the
vendored official interface guidance instead.

Imported scripts are inert data. The sync, renderer, installer, and validators do not execute them.
Procedures that deploy, publish, authenticate, upload, email, or call an external service are
explicit-use-only and still require the user's approval for that action.

## Validate The Tracked Source

Run these commands from a clean clone:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/validate_frontend_design_stack.py --repo-root .
python3 scripts/audit_agent_stack.py --repo-only
python3 scripts/check_private_paths.py
git diff --check
```

`validate_frontend_design_stack.py` verifies locked source bytes, provenance, licenses, deterministic
rendering, and the tracked plugin. It does not silently validate an installed runtime copy.

## Install In Codex

First inspect current state:

```bash
codex plugin marketplace list
codex plugin list
```

After the user approves adding this repository marketplace and installing the plugin:

```bash
codex plugin marketplace add "$PWD"
codex plugin add frontend-design-pack@agent-bootstrap
codex plugin list
```

Use `codex plugin list` plus read-only filesystem inspection to locate the actual installed plugin
root. Validate it separately:

```bash
python3 scripts/validate_frontend_design_stack.py \
  --repo-root . \
  --codex-runtime-root "<installed-frontend-design-pack-root>"
```

Do not guess the cache path. Do not remove an existing marketplace or plugin to make installation
easier. If replacement is required, explain the current state and Ask before installing, updating,
or replacing it.

Start a fresh Codex task after installation. Skills are discovered at task start; the task that
performed installation is not valid discovery evidence. In the fresh task, use a read-only request
such as “Review this interface and report findings only.” Confirm that the agent reports one mode,
the target surface, and the smallest loaded reference set without editing files.

## Install In Claude Code

Validate both manifests before changing runtime state:

```bash
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate plugins/frontend-design-pack
claude plugin marketplace list
claude plugin list
```

After the user approves marketplace and plugin installation:

```bash
claude plugin marketplace add "$PWD"
claude plugin install frontend-design-pack@agent-bootstrap --scope user
claude plugin list
```

Locate the installed root from current Claude Code state and validate that runtime copy separately:

```bash
python3 scripts/validate_frontend_design_stack.py \
  --repo-root . \
  --claude-runtime-root "<installed-frontend-design-pack-root>"
```

Start a fresh Claude Code session after install or update. A restart or fresh session is required
before claiming discovery.

## Figma Boundary

Figma complements this stack; it does not replace project evidence or the router. During setup:

- report whether Figma is available in the current Codex plugin/tool inventory;
- do not authenticate, sign in, change accounts, or open private Figma files without separate
  approval;
- if Figma is unavailable, identify the exact official plugin offered by the current marketplace
  before asking whether to install it;
- use supplied Figma selections only within the user's approved project scope.

## How The Router Uses Evidence

The router resolves one mode, names the target surface, and reports every loaded reference. Its
source precedence is:

1. current user instruction and approved scope;
2. verified project behavior and product evidence;
3. project-owned components, tokens, Figma, assets, and DESIGN.md;
4. accessibility, legal, compliance, and brand requirements;
5. applicable official Vercel guidance;
6. applicable MengTo procedure;
7. one to three labeled third-party inspiration sources;
8. router defaults.

External aesthetics never overwrite an established project design system without an explicit
material decision.

Verification claims stay narrow:

- A successful build is not visual verification.
- HTTP 200 is not visual verification.
- source inspection is not visual verification.

Visual verification requires a rendered result, the relevant viewports and reachable states, and a
comparison with supplied Figma or screenshot evidence when available.

## Read-Only Update Check

To compare an already reviewed local checkout without modifying the repository:

```bash
python3 scripts/check_design_sources.py \
  --repo-root . \
  --source mengto-skills \
  --candidate-root "<reviewed-checkout>"
```

Without `--candidate-root`, the checker uses only `git ls-remote` to report the remote HEAD. It does
not fetch, checkout, render, install, or update a runtime.

Review added, removed, renamed, content, mode, frontmatter, script, asset, dependency, URL,
permission, service, side-effect, license, and provenance changes before approving an import.

## Approved Source Sync

Pin and review the immutable upstream revision first. Create a tar archive containing only the
reviewed paths. Set the archive umask explicitly so Git file modes remain stable:

```bash
git -c tar.umask=0022 archive \
  --format=tar \
  --prefix="<source-id>-<40-character-revision>/" \
  --output="<source-id>.tar" \
  "<40-character-revision>" \
  -- <reviewed-paths>
```

For an established tree, sync one source. For initial bootstrap or a coordinated update, repeat
the paired options so all source trees and the generated plugin commit in one transaction:

```bash
python3 scripts/sync_design_sources.py --repo-root . \
  --source "<source-id>" --archive "<source-id>.tar" \
  --source "<second-source-id>" --archive "<second-source-id>.tar"
```

The command requires a clean non-default task branch, rejects unsafe tar members, keeps imported
files non-executable, validates provenance and licenses, renders in staging, runs safety gates, and
uses a recovery journal for interrupted multi-path replacement. It never downloads an archive or
executes imported content.

After sync, require human diff review. Then rerun the full verification commands above. Review
`THIRD_PARTY_NOTICES.md`, the source lock, provenance changes, generated catalog, and plugin diff.

## Versioning, Update, And Rollback

Runtime caches are versioned. Any published content change requires a new semantic version in the
renderer and marketplace entry, followed by deterministic re-rendering and validation. Never reuse
a broken cached version number.

After pulling a reviewed repository update:

1. inspect `git status --short --branch`;
2. validate the tracked source and generated output;
3. inspect current marketplace/plugin state;
4. ask approval before runtime replacement;
5. install the newly versioned plugin using the current runtime's documented command;
6. validate the installed root separately;
7. start a fresh task or session and run a read-only discovery pressure case.

Rollback is a new reviewed release: restore the prior source content in a task branch, assign a new
semantic version, render and validate it, inspect the diff, then install that new rollback version.
Do not point a reused version at different bytes, and do not delete unrelated runtime state.
