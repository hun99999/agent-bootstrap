# Source

- Upstream: <https://github.com/mattpocock/skills>
- Reviewed commit: `2ab958093e83e0ec752e6c1c5932da465bf23e0c`
- Reviewed paths:
  - `skills/productivity/handoff/SKILL.md`
  - `skills/productivity/handoff/agents/openai.yaml`
- Review date: 2026-07-28
- License: MIT
- Copyright: Matt Pocock

The instruction body and `agents/openai.yaml` are preserved from the reviewed commit. The Codex
catalog copy removes the upstream-only `argument-hint` and `disable-model-invocation` frontmatter
keys so it passes the installed Codex skill validator. Explicit-only behavior remains enforced by
`agents/openai.yaml` through `allow_implicit_invocation: false`.

Reviewed upstream SHA-256:

- `SKILL.md`: `57c9f1f392d7352cdc85b1e39ca49eddc70ce1dc278bd9653fb4f23dfc2560fc`
- `agents/openai.yaml`: `5c479fd562c691851690e8b18c8501045bef0943c10743d636b2fae26add1d28`

Codex catalog SHA-256:

- `SKILL.md`: `aa365c9c3fb57b52e282d901dc2ed8153707b9f54d3fa2a5d15499c2768aaead`
- `agents/openai.yaml`: `5c479fd562c691851690e8b18c8501045bef0943c10743d636b2fae26add1d28`
