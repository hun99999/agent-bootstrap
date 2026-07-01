# OpenClaw Legacy Notes

OpenClaw is legacy/reference material in this repository, not a current first-class bootstrap target.

The current public setup path is Codex or Claude Code. Do not configure OpenClaw
from this repository unless Hun explicitly asks for legacy OpenClaw migration,
shared-core reference work, or ACP integration work.

## Native Vs ACP

OpenClaw should stay `native-first` for any explicit legacy work.

ACP is optional.

Use OpenClaw-native delegation for routine internal orchestration. Use ACP only when the user explicitly asks for ACP and identifies the harness to connect.

## Path A: legacy shared-core-only

This path is preserved for users who explicitly want to map the repository's
workflow layer into an existing OpenClaw setup.

Use this path only when the user asks for OpenClaw shared-core work.

What to do:

- read the root `AGENTS.md`
- apply only the shared prompt/skill layer the user approved
- back up any prompt or skill files you replace
- do not change ACP settings
- do not reset the OpenClaw environment

What not to do:

- do not choose Codex-first, Claude-first, or OpenCode-first by default
- do not change unrelated identity, gateway, transport, auth, provider, or messaging settings
- do not treat a repo URL alone as permission to redesign the runtime stack

## Path B: ACP integration

This is the optional path.

Use it only if the user explicitly asks for ACP integration.

What to do:

- ask the user which harness to connect if that is not already explicit
- identify the requested harness explicitly
- bootstrap that harness only if the user asked for it
- configure OpenClaw ACP settings only within that requested integration scope
- back up ACP-related config before editing it

What not to do:

- do not infer ACP from a generic setup request
- do not change unrelated OpenClaw identity, gateway, transport, auth, provider, or messaging settings
- do not touch Codex or Claude Code configuration unless the approved ACP scope requires it

## Scope Boundary

This repository does not ship a universal OpenClaw config because those settings
are environment-specific:

- model/provider selection
- transport and gateway details
- auth and token handling
- local path assumptions

Those should remain in the user's own environment unless they explicitly request
changes inside that scope.
