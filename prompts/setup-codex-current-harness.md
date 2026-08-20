You are setting this repository up inside Codex in `current-harness-only` mode.

Read `README.md` and `docs/README.codex.md` first.

Follow these rules exactly:

1. Default to `current-harness-only`.
2. Ask the user what name Codex should use to address them.
   - If they have no preference, ask whether the generic name `Partner` is acceptable.
3. Inspect the active Codex runtime and the model and reasoning settings it actually supports.
   - Preserve existing machine-local selections and unmanaged runtime sections.
   - On a fresh target, leave model and reasoning unset so Codex inherits supported defaults.
   - Apply an explicit model or effort only when the user chooses one the target supports.
   - Keep model and reasoning selection independent of the optional Superpowers mode.
   - When account-specific availability cannot be enumerated, retain inheritance and report it.
   - Do not install or reconfigure a runtime solely to inspect it.
4. Configure Codex only.
5. Do not configure another harness unless the user explicitly asks.
6. Do not commit the chosen partner name or any rendered file containing it. Keep the chosen name only in local runtime output and local backups.
7. Install or update the shared Codex agent/subagent prompts.
8. Resolve one target-local skill mode with the user: lean catalog skills, full upstream
   Superpowers, or neither.
   - Recommend lean catalog skills when lower prompt and workflow overhead is the goal.
   - Inspect current skill and plugin discovery before changing it. Use the target-supported plugin
     or skill settings, and derive every path-specific entry from this target rather than copying
     another machine's configuration.
   - In lean mode, install only approved catalog skills and keep the four Superpowers adaptations
     explicit-use. Keep existing full upstream discovery unchanged until the user approves disabling
     or uninstalling it.
   - In full upstream mode, separately ask whether the user wants the optional manual Codex
     Superpowers checkout.
   - Do not install or update it automatically.
   - The installer default is `skip`; pass `--superpowers-mode manual` only after explicit opt-in.
   - `skip` is non-mutating: it does not deactivate, disable, or remove existing manual or curated
     discovery.
   - Model and reasoning selection is independent of the Superpowers choice.
   - Warn that enabling both curated and manual discovery can create duplicate skill entries.
   - When disabling current curated skills, derive each `skills.config` folder from this target and
     re-resolve it after plugin updates; do not copy another machine's versioned cache paths.
8a. Ask separately whether the user wants Basic Memory and whether the user wants Computer Use or
    browser control.
   - Do not install or enable either capability before its own approval.
   - Keep MCP commands, hooks, project mappings, app paths, permissions, auth state, and browser
     profiles target-local.
   - The shared core and selected skill mode must work when either capability is absent.
9. Read `docs/frontend-design-stack.md` and validate the tracked plugin with `python3 scripts/validate_frontend_design_stack.py --repo-root .`.
   - Inspect current Codex plugin state and report whether `frontend-design-pack` and Figma are available.
   - Do not authenticate Figma, change accounts, or inspect private Figma files.
   - Ask before installing or replacing `frontend-design-pack` or any runtime copy.
   - If approved, install from the documented marketplace, locate the actual installed root, and validate the runtime copy separately.
   - Start a fresh task for a read-only discovery pressure case.
10. Preserve unrelated Codex state such as credentials, history, logs, and automations.
11. Summarize:
   - chosen partner name
   - preserved, inherited, or explicitly selected Codex model and reasoning policy
   - files changed
   - backups created
   - tracked plugin and runtime copy validation results
   - Figma availability without authentication changes
   - selected target-local skill mode and whether existing discovery was preserved, disabled, or
     explicitly installed
   - anything that still needs manual follow-up
