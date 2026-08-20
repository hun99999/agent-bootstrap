# Portable Runtime Adapters

Codex and Claude Code are the first-class targets in this repository. Other AI coding CLIs can
reuse the shared operating model when their native instruction, skill, MCP, and hook surfaces are
identified from the target runtime rather than guessed from another machine.

Use [setup-portable-runtime.md](../prompts/setup-portable-runtime.md) from the target CLI when no
first-class adapter exists.

## Portable Core

Reuse these tracked sources:

- `shared/agent-core.md` for the compact cross-harness outcome contract;
- `AGENTS.md` for the full public operating policy;
- `agents/*.md` and `shared/agent-metadata.json` for role intent;
- selected public-safe directories under `skills/`.

Adapt those sources to the target's native format. Do not copy Codex TOML, generated Claude
frontmatter, plugin cache paths, model names, effort levels, permissions, or user identity into a
different runtime.

For an unrecognized `gpt` command, resolve the executable and read its help before treating it as an
AI client. On macOS, `/usr/sbin/gpt` is a disk-partition utility, not an OpenAI coding CLI.

## Target Contract

Before writing target configuration:

1. Identify the exact client, version, user-level instruction file, skill directory, and supported
   MCP or hook mechanism.
2. Preserve the target's model and reasoning selection. On a fresh target, inherit its supported
   defaults; select an explicit model or effort only after the user chooses an available value.
3. Render the partner name only into local output. Keep `{{PARTNER_NAME}}` in tracked sources.
4. Install the smallest supported surface: shared instructions first, then approved roles and skills.
5. Start one fresh session and prove that the target loads the intended instructions or one selected
   skill. Static files alone are not runtime discovery evidence.

Until a target has a maintained installer and a fresh-session check, report it as a reference
adapter rather than first-class support.

## Skill Mode

Choose one target-local mode with the user:

- **Lean:** install approved catalog skills; keep `karpathy-guidelines` as the portable base and the
  four Superpowers adaptations explicit-use.
- **Full upstream:** use the target's supported upstream Superpowers package after approval.
- **Neither:** use the shared prompt without extra workflow skills.

Inspect current discovery before changing it. Path-specific entries must be derived from the target.
For Codex, `skills.config` is the supported per-skill enablement surface; its path identifies the
current skill folder. Plugin cache versions can change, so re-resolve discovered folders after a
plugin update instead of copying versioned paths from another machine. See the
[official Codex configuration reference](https://developers.openai.com/codex/config-reference).

## Optional Basic Memory

Basic Memory is a target-local, opt-in recall layer. Ask separately before installing a package,
adding an MCP server, enabling hooks, or creating a repository mapping.

When approved:

- verify the installed Basic Memory CLI and its current MCP command from the target;
- keep executable paths, project identifiers, cloud workspace details, and credentials local;
- create `.codex/basic-memory.json` only when the user explicitly maps that repository;
- bound automatic startup recall to at most three search results and one exact note;
- treat recalled notes as lower authority than the current request, repository, Git, runtime, and
  test evidence;
- store concise decisions or checkpoints, never secrets, transcripts, source trees, diffs, or logs.

If the target cannot provide equivalent MCP or hook behavior, keep the shared core working without
memory and report the missing capability.

## Optional Computer Use

Computer Use, browser control, desktop permissions, and authenticated profiles are separate
target-local choices. Ask before installing or enabling them and before changing accessibility,
screen-recording, browser-profile, or authentication state.

Keep app paths, plugin cache versions, notification commands, trusted-project lists, permission
state, and profiles out of Git. Prefer a target's native browser or application integration when it
fits the task; Computer Use remains an explicit fallback or user-selected capability.

## Release Boundary

A portable adapter may commit public prompt templates, install instructions, and deterministic
renderers. It must leave credentials, private project skills, absolute home paths, plugin caches,
trusted repositories, model availability, account state, Basic Memory projects, and Computer Use
permissions on the target machine.
