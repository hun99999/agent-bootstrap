# Setup Another AI Coding Runtime

```text
Adapt agent-bootstrap to the AI coding CLI that is running this prompt.

Read README.md, AGENTS.md, shared/agent-core.md, docs/agent-bootstrap-structure.md, and
docs/portable-runtime-adapters.md. Treat Codex and Claude Code as the only first-class adapters;
this task creates a target-local reference adapter unless the repository already has one.

Before changing anything:
- identify the exact client, executable, version, user-level instruction file, skill directory, and
  supported MCP or hook mechanism from current help or official documentation;
- do not treat macOS /usr/sbin/gpt as an AI client;
- inspect Git and target configuration, preserve unrelated state, and keep credentials and absolute
  machine paths out of the repository;
- ask what name the agent should use, and keep the rendered name local;
- preserve the target model and reasoning selection, or inherit supported defaults on a fresh target.

Ask for these decisions separately:
1. skill mode: lean catalog skills, full upstream Superpowers, or neither;
2. Basic Memory: whether to install/configure its MCP, hooks, and repository mapping;
3. Computer Use or browser control: whether to install or enable it and change required permissions.

Do not install, enable, authenticate, or change permissions for an optional capability before its
specific approval. Derive every path-specific setting from this target instead of copying another
machine's config.

Install the smallest supported shared instruction surface. Add only approved roles and skills.
Start one fresh session and prove instruction or skill discovery with one read-only case. Report the
target, installed files, inherited or selected model policy, optional capability decisions, direct
evidence, and unsupported features without claiming first-class support.
```
