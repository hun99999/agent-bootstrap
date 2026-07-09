# Frontend Design Stack Design

## Goal

Build a public-shareable frontend design environment for Codex and Claude Code that can use the
complete usable MengTo/Skills corpus, structured DESIGN.md references, Vercel's official interface
quality guidance, and Figma without flattening every source into one always-on prompt.

The environment should help an agent shape, explore, implement, review, and harden user-facing
frontends. It must preserve the current repository's safety, model-inheritance, public-path, and
approval boundaries. It cannot promise a perfect frontend, but it should make visual and product
quality repeatable and verifiable.

## Approved Product Decisions

- Keep this repository reusable by fresh cloners and pullers.
- Ask each user for the partner name during setup; do not commit a private name into public
  templates.
- Inherit the models that Codex and Claude Code can actually use. Do not force a latest-model name
  that may be unavailable under a personal or company plan.
- Keep one broad frontend-design entry point and route internally to focused source material.
- Make the full usable MengTo corpus available behind the router instead of exposing all upstream
  skills as independent native skills.
- Use Google DESIGN.md as the project-owned visual contract.
- Use Meta, Vercel, and other reverse-engineered DESIGN.md files as clearly labeled inspiration,
  never as official brand systems.
- Use Vercel's official guidance for interface, accessibility, interaction, React performance, and
  composition checks.
- Keep Open Design as an on-demand provider instead of vendoring its complete repository.
- Install and verify the resulting plugin in Hun's local Codex environment as part of the work.

## Source Classification

Every external source must be recorded with an authority class, scope, immutable revision,
license, local role, and update method.

### Primary Project Sources

These sources outrank all external design guidance:

1. The user's explicit goal and constraints.
2. The target repository's actual behavior, components, tokens, and tests.
3. The target project's Figma selections, supplied screenshots, and approved assets.
4. The target project's own DESIGN.md.
5. Explicit accessibility, legal, compliance, and brand constraints.

### MengTo/Skills

- Upstream: `https://github.com/MengTo/Skills`
- Reviewed revision: `25f872a94e3bbee85ecacba4041fa52c21cb0e44`
- Declared root license: MIT.
- Reviewed inventory: 95 SKILL.md files, including 18 codex, 2 media, 13 UI, and 62 web-design
  skills, plus scripts, assets, and agent metadata.
- Local role: visual exploration, prompt structure, typography, layout, landing pages, motion,
  WebGL, image-to-code, and related frontend procedures.
- Runtime behavior: inert reference corpus selected by the router. Operational procedures that can
  deploy, authenticate, post, email, invoke external APIs, request OS permissions, or modify
  external accounts are explicit-use-only.

The upstream README count is not authoritative. The importer must derive the inventory from the
tree at the pinned revision.

### Google DESIGN.md

- Upstream: `https://github.com/google-labs-code/design.md`
- Reviewed CLI version: `0.3.0`.
- License: Apache-2.0.
- Status: alpha; pin the release or commit because the schema can change.
- Local role: project-owned design tokens and rationale, linting, diffing, and token export.

External brand presets may inform a project's DESIGN.md, but they may not silently replace it.

### VoltAgent Awesome DESIGN.md

- Upstream: `https://github.com/VoltAgent/awesome-design-md`
- Reviewed revision: `664b3e78fd1a298ba11973822da988483256d4b4`.
- License: MIT for the authored collection.
- Reviewed inventory: 74 DESIGN.md files.
- Local role: optional visual inspiration indexed by product archetype and style characteristics.

The Meta and Vercel files are third-party analyses of publicly visible websites. They must be
labeled `third-party-analysis`, and their licenses do not grant rights to redistribute the brands'
logos, trademarks, proprietary imagery, or proprietary fonts.

### Vercel Official Guidance

- Web Interface Guidelines: `https://github.com/vercel-labs/web-interface-guidelines`.
- Agent skills: `https://github.com/vercel-labs/agent-skills`.
- Local role: interface audit, accessibility, keyboard and focus behavior, forms, responsive
  behavior, motion restraint, React and Next.js performance, component composition, and optional
  view-transition guidance.

Vercel-specific copy and brand choices do not become universal rules. Project copy guidance and
explicit accessibility contracts take precedence.

### Meta Official Guidance

- Design at Meta and Meta Brand Resource Center remain external official references.
- StyleX LLM resources may be used only when a target project already uses or intentionally adopts
  StyleX.
- Meta Horizon guidance applies only to XR or Horizon work.

These sources are not vendored unless their redistribution terms are verified. Store source URLs,
review dates, and content hashes when a stable Git revision is unavailable.

### Open Design

- Upstream: `https://github.com/nexu-io/open-design`.
- License: Apache-2.0 for the Open Design repository.
- Local role: optional provider for packaged DESIGN.md, tokens.css, design-tokens.json,
  Tailwind CSS, component fixtures, and previews.

The reviewed shallow checkout was approximately 449 MB and contained extensive overlap with
VoltAgent and other sources. Do not vendor the complete repository. Fetch only an explicitly
selected design-system package into a local cache, preserve its provenance, and do not treat a
derived package as fresher than its underlying evidence.

## Architecture

Create one dual-manifest plugin package named `frontend-design-pack`. It exposes one native skill,
`frontend-design`, to Codex and Claude Code. The plugin carries a catalog and a pinned, vetted
reference corpus inside its own directory so installed plugin caches never depend on paths outside
the plugin.

```text
plugins/frontend-design-pack/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
└── skills/frontend-design/
    ├── SKILL.md
    └── references/
        ├── catalog.json
        ├── source-precedence.md
        ├── quality-gates.md
        ├── mengto/
        ├── design-md/
        └── vercel/
```

The repository also owns the source registry, lock, provenance ledger, deterministic renderer, and
tests:

```text
design-stack/
├── sources.json
├── sources.lock.json
├── provenance.json
├── routing.json
├── templates/
│   ├── DESIGN.md.template
│   ├── product-brief.md
│   └── design-decision.md
└── evals/
    ├── routing-cases.json
    └── trigger-cases.json

scripts/
├── check_design_sources.py
├── sync_design_sources.py
├── render_frontend_design_plugin.py
└── validate_frontend_design_stack.py
```

The renderer must produce deterministic output from the locked source inventory. The tracked plugin
is reviewable output. Runtime Codex and Claude copies must be verified separately from the tracked
source.

## Router Contract

The router resolves a request mode before loading references.

| Mode | Typical request | Required behavior |
| --- | --- | --- |
| Shape | Design a flow or decide how a feature should work | Frame user, job, outcome, states, alternatives, risks, and open decisions. Do not edit unless requested. |
| Explore | Produce visual directions or choose a design language | Load the smallest relevant MengTo procedures and one to three labeled references. Compare materially different directions. |
| Implement | Build, redesign, or fix a user-facing surface | Resolve material decisions, honor project sources, use the smallest coherent implementation, and follow TDD. |
| Review | Audit a URL, screenshot, component, or diff | Inspect source and rendered evidence, report prioritized findings, and do not edit unless requested. |
| Copy | Improve user-facing language | Change only copy, accessible names, and directly required markup. Report structural blockers separately. |
| Harden | Polish or make production-ready | Preserve the chosen direction while covering reachable states, resilience, accessibility, responsive behavior, and finish defects. |

The router must report the mode, target surface, and references it loaded. It must select the
smallest sufficient source set instead of loading every reference.

## Source Precedence

Resolve conflicts in this order:

1. Current user instruction and approved scope.
2. Verified project behavior and product evidence.
3. Project-owned component APIs, tokens, Figma, and DESIGN.md.
4. Explicit accessibility, legal, compliance, and brand requirements.
5. Vercel official interface and React quality guidance where applicable.
6. MengTo procedural and visual-taste guidance.
7. Third-party DESIGN.md inspiration.
8. Router defaults.

External aesthetics must never overwrite a target project's established design system without an
explicit material design decision.

## Project Workflow

For material frontend work, the router should:

1. Inspect the target repository's instructions, components, tokens, and test commands.
2. Inspect supplied Figma context, screenshots, or approved assets when available.
3. Define user, job, current behavior, desired outcome, success signal, non-goals, reachable states,
   and open decisions.
4. Choose one to three relevant inspiration sources and label their authority and scope.
5. Compare materially different directions before implementation when the direction is unsettled.
6. Create or update a project-owned DESIGN.md only with user approval for the material direction.
7. Validate DESIGN.md with the pinned Google CLI.
8. Implement through the target project's existing component and token sources.
9. Verify compact and wide viewports, keyboard and focus behavior, touch targets, reduced motion,
   long content, large values, localization and RTL risk, and every materially changed reachable
   state.
10. Run target-repository lint, type, test, and build commands.
11. Run the Vercel interface review and applicable React performance review.
12. Compare the rendered result with Figma or screenshot references when supplied.
13. Report which sources were used and which checks were actually run.

A successful build is not visual verification. Source inspection and HTTP success are not visual
verification either.

## Update Model

Updates are explicit, reviewable repository changes. Never pull and execute mutable upstream code
at agent startup.

### Read-Only Check

`check_design_sources.py` compares the locked revisions with upstream heads and reports:

- added, removed, or renamed skills and DESIGN.md files
- instruction and description changes
- new or changed scripts and assets
- new URLs, dependencies, permissions, external services, or side effects
- license and provenance changes

It does not modify the repository or runtime installation.

### Approved Sync

`sync_design_sources.py --source <source-id> --archive <reviewed-archive>` accepts only an explicit
local archive for an immutable revision. It must:

1. Require a clean task branch.
2. Reject path traversal, unexpected links, invalid frontmatter, duplicate skill names, missing
   required files, or a revision mismatch.
3. Produce a file inventory with path, size, and SHA-256.
4. Produce a semantic change report for skills, scripts, dependencies, URLs, and side effects.
5. Enforce the provenance and license gate.
6. Replace the pinned reference tree atomically.
7. Regenerate the catalog and plugin output.
8. Run source, plugin, repository, secret, and private-path validation.
9. Require human diff review before runtime installation.

Rollback restores the previous lock and reference tree, increments the plugin version, and
reinstalls that new rollback version. Do not reuse a broken cached version number.

## Provenance And License Gate

The importer must not assume that one root license covers every copied upstream file.

The reviewed MengTo revision contains concrete provenance gaps:

- Its PDF SKILL.md is byte-identical to an Apache-2.0 Codex skill, but the MengTo tree does not carry
  the corresponding LICENSE.txt.
- Its screenshot SKILL.md has the same issue.
- Its frontend-design frontmatter refers to a LICENSE.txt that is absent.
- Playwright-family source and notice requirements need source verification.

Before public redistribution, identify the original source and preserve every required license and
notice. Prefer mapping byte-identical functionality to an already available official plugin instead
of distributing a duplicate. Block unresolved material from the public plugin and report the block
instead of silently relicensing it.

For every imported file, provenance.json records:

- upstream repository and path
- immutable commit and tree when available
- original license and notice paths
- local role and authority class
- file hash
- import decision: included, mapped-to-official, excluded, or blocked
- reason for any transformation or exclusion

## Safety Boundaries

- Treat imported scripts as inert data during sync and installation.
- Never execute upstream install, deploy, authentication, email, posting, browser-profile, API, or
  OS-permission instructions merely because the router found them.
- Existing repository approval boundaries remain higher priority than imported instructions.
- Do not read or copy `.env`, credentials, auth state, browser profiles, or private project data
  unless the user explicitly authorizes that task.
- Do not disable pre-commit hooks, test enforcement, secret scanning, or private-path scanning.
- Use a hash-bound vendor baseline only to distinguish known upstream placeholders from newly
  introduced secret-like content; changed vendor files remain fully scanned.

## Codex And Claude Code Distribution

The same plugin root contains both product manifests.

- Codex installs the plugin from the repository marketplace, then starts a new task to load the new
  plugin version.
- Claude Code installs the matching plugin through the existing repository marketplace, then
  reloads or starts a new session.
- Both runtimes receive only the `frontend-design` native entry point.
- Both installed copies are validated separately from the tracked plugin.
- Plugin versions stay synchronized. Local Codex cachebuster suffixes are for local iteration only;
  published repository updates use a shared semantic version bump.

Figma remains an optional official plugin. Setup may verify availability and explain authentication,
but it must not authenticate or change account state without explicit user approval.

## Public Bootstrap Integration

The setup agent should:

1. Ask the user for the partner name and render local runtime output without committing that value.
2. Inspect available Codex and Claude models and inherit the actual supported ceiling.
3. Explain the design pack and ask before installing or replacing runtime copies.
4. Build and validate the locked plugin.
5. Install it for each approved runtime.
6. Start a fresh task or session and verify discovery and a read-only routing pressure case.
7. Report optional Figma availability and leave authentication to a separate approved step.

No public template hard-codes Hun's local paths, name, model entitlement, or account state.

## Testing

Implementation follows TDD.

Required automated coverage includes:

- source and lock schema validation
- deterministic inventory and catalog generation
- archive traversal and unexpected-link rejection
- revision and SHA-256 verification
- duplicate and invalid-skill rejection
- provenance and license blocking
- safe handling of executable files as inert data
- router mode and source-selection pressure cases
- explicit-use-only handling for external-side-effect skills
- project-source precedence over external aesthetics
- Codex and Claude manifest consistency
- tracked plugin and installed-runtime validation
- setup docs and prompts for public partner-name and model inheritance behavior
- private-path and secret scan coverage for the new tree

At least one fixture must verify trigger behavior separately from guidance application, because a
good rule is useless when the router does not load it.

## Success Criteria

- One frontend-design entry point is discoverable in fresh Codex and Claude Code sessions.
- The router can select and read every included usable MengTo skill without exposing all 95 as
  native metadata.
- All 74 reviewed VoltAgent DESIGN.md references are indexed and labeled as third-party analysis.
- Google DESIGN.md validation uses a pinned version.
- Vercel official review and applicable React guidance are available as quality gates.
- Open Design packages can be selected on demand without vendoring the complete repository.
- Public packaging contains complete provenance and required license/notice files; unresolved items
  are blocked and reported.
- Imported scripts are never executed during sync, render, install, or validation.
- The tracked plugin and Hun's live Codex installation pass separate validation.
- The repository remains public-safe and the full repository test and audit suite passes.
