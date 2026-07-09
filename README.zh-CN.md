# agent-bootstrap

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

## 主提示词

把下面内容原样粘贴给 Codex 或 Claude Code。代理应当在这个仓库的 clone 中开始。

```text
请从这个仓库完整设置 agent-bootstrap。

先阅读 AGENTS.md, README.md, docs/agent-setup-playbook.md, docs/global-guardrail-setup.md, docs/vibe-coding-guardrails.md, docs/agent-bootstrap-structure.md, docs/local-project-knowledge-template.md。不要编造命令、包名、配置选项或 API 细节。

修改文件之前，运行 git status --short --branch。如果有未提交修改或 untracked file，停止并询问如何处理。确认当前 harness 是 Codex 还是 Claude Code，并确认我要求的范围。

渲染本地配置之前，先询问代理应如何称呼我。检查当前 Codex 和 Claude runtime 实际支持的 model 与 reasoning level，不要硬编码最新 model 名或 paid plan，而应继承可用选择。不要把选定名称写入 tracked file。

阅读 docs/frontend-design-stack.md。验证 tracked frontend-design-pack；只报告 Figma 是否可用，不要进行认证；安装或替换 runtime plugin copy 前先询问。获得批准后，单独验证 installed root，并在 fresh task/session 中确认 discovery。

选择最小有效范围:
- 如果已经在 Codex 中，除非我明确要求 Claude Code，否则只配置 Codex。
- 如果已经在 Claude Code 中，除非我明确要求 Codex，否则只配置 Claude Code。
- 如果无法确认支持的 harness，先询问要配置哪个。
- 如果这是应用仓库，应用 project guardrails 并创建 project-local knowledge guidance。
- 不要仅仅因为文档提到某个可选工具就安装它。

完整设置所选范围:
- 使用本仓库文档中的命令 install 或 render shared core
- 只通过当前 harness 文档化的路径安装 upstream superpowers
- 如果 shared prompts 或 metadata 改变，重新生成 Claude plugin output
- public default base skill 使用 karpathy-guidelines
- 除非我明确批准，hun-engineering-loop 只作为 Hun local runtime wrapper
- 不要把 chatgpt-collaboration-harness 安装到 Claude Code
- 以 read-only 方式检查 Obsidian, Lumin Repo Lens, dependency lint, strict type checks, cycle detection, complexity limits 等 optional tool inventory，分类为 required, recommended, optional, skipped，然后再询问是否安装
- 不要把 private path, credential, MCP endpoint, auth state, browser profile, machine-specific trust setting 写入 tracked file
- 运行真实验证命令，包括 tests 和 scripts/audit_agent_stack.py
- 进行 post-write review，检查 duplicate helpers, hidden coupling, swallowed errors, fallback drift, unmanaged re-exports, fan-in/fan-out hotspots, weak tests, generated-output drift, private path leakage
- 适当时做小的可审查 commit，并总结修改内容、安装内容、执行命令、验证结果和剩余风险
```

面向 Codex 和 Claude Code 的流程优先 AI 编程环境引导仓库。

`agent-bootstrap` 为新的 clone 提供共享 `superpowers` workflow、role-based subagents、token-efficient 工作习惯、详细设置文档，以及基于 `karpathy-guidelines` 的 public-safe skill model。

## 当前支持范围

只有 Codex 和 Claude Code 是 first-class setup target。

OpenCode 和 OpenClaw 是 legacy/reference material，不是 active service target。旧文件可能仍保留在 git 中，供历史审计或迁移参考，但新的 README、setup guide 和默认 audit 不应把它们当作普通安装路径。

## Private Project Skills

不要把 auto-eva 这类 private project skill 提交到这个 public repository。实际项目专用 skill 应放在本地 runtime home，例如 Codex 的 `~/.codex/skills` 和 Claude Code 的 `~/.claude/skills`。这个仓库只保留 templates and public-safe process guidance，不放 private access path、credential、auth state、browser profile、customer data 或 machine-specific trust setting。

## 核心模型

- `karpathy-guidelines` 是 public default base skill，用来强调 assumptions、simplicity、surgical diff 和 verifiable success criteria。
- `superpowers` 是 brainstorming、planning、TDD、debugging、verification、review 的 reusable workflow library。
- `hun-engineering-loop` 是 Hun local wrapper，加入 memory preflight、source-of-truth ordering、high-risk approval boundary、artifact-first execution 和 QA evidence contract，但不属于 public default install set。
- `chatgpt-collaboration-harness` 是 Codex 侧的 ChatGPT Pro collaboration skill，不默认安装到 Claude Code。

Memory 是 recall layer，不是 source of truth。当前 user instruction、repo docs、scripts、tests、`AGENTS.md` 和 observed runtime output 优先。

## 快速开始

先选择范围。很多失败来自一次性配置太多东西：另一个 harness、plugin stack、optional tools 和 project rules。

1. Clone 或 pull。

   ```bash
   git clone https://github.com/hun99999/agent-bootstrap.git
   cd agent-bootstrap
   git status --short --branch
   ```

2. 编辑或安装前先阅读共享规则。

   ```bash
   sed -n '1,220p' AGENTS.md
   sed -n '1,220p' docs/agent-setup-playbook.md
   ```

3. 选择当前支持的 harness。

   - Codex: [docs/README.codex.md](docs/README.codex.md)
   - Claude Code: [docs/README.claude.md](docs/README.claude.md)

4. 修改前后运行验证。

   ```bash
   python3 -m unittest discover -s tests -p 'test_*.py'
   python3 scripts/audit_agent_stack.py
   ```

5. 更新已有 clone 时，先 fast-forward pull，再重新生成必要的 generated artifact。

   ```bash
   git pull --ff-only
   python3 scripts/render_claude_plugin.py --partner-name "<Name>"
   python3 -m unittest discover -s tests -p 'test_*.py'
   python3 scripts/audit_agent_stack.py
   ```

## 可以让代理做什么

- Install global defaults: 使用 [docs/global-guardrail-setup.md](docs/global-guardrail-setup.md) 把 guardrails 安装到 Codex 或 Claude Code user-level defaults。
- Apply guardrails to a project: 在目标仓库中使用 [prompts/apply-vibe-coding-guardrails.md](prompts/apply-vibe-coding-guardrails.md)。
- Start feature work inside a guarded project: 在 feature、bugfix、refactor 前使用 [prompts/start-with-vibe-coding-guardrails.md](prompts/start-with-vibe-coding-guardrails.md)。
- Review optional Codex skills: 阅读 [skills/README.md](skills/README.md)、[docs/codex-skills.md](docs/codex-skills.md)，必要时使用 [prompts/setup-codex-skills.md](prompts/setup-codex-skills.md)。
- Update this bootstrap after repository changes: pull 后使用 [prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md)。
- Explain repository structure: 修改 shared prompts、installer、generated plugin output 或 setup docs 前先读 [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md)。

Optional tooling is decision-based。Obsidian、Lumin Repo Lens、dependency lint、cycle detection、strict type checks、complexity limits 只有在目标仓库和用户批准支持时才使用。

## 目标项目 Claude Code 提示词

在目标项目仓库中打开 Claude Code，然后原样粘贴下面的提示词。它引用公开 URL，不依赖个人本地路径。

```text
请把 agent-bootstrap 的 vibe-coding guardrails 应用到这个项目。

参考仓库:
- https://github.com/hun99999/agent-bootstrap

首先在这个项目中运行 git status --short --branch。如果有未提交修改或 untracked files，停止并询问如何处理。未经批准不要 stash、delete、overwrite 或 git add。

检查这个项目:
- AGENTS.md, CLAUDE.md, README.md, existing docs
- package.json, pyproject.toml, Cargo.toml, go.mod, or other tooling signals
- real test, lint, type-check, build commands
- source-of-truth helpers, types, schemas, public APIs, module boundaries, dependency direction, error boundaries, re-export policy, known hotspots

从上面的 URL 阅读参考仓库 docs。需要时在项目外 read-only clone:
- docs/agent-setup-playbook.md
- docs/vibe-coding-guardrails.md
- docs/global-guardrail-setup.md
- docs/local-project-knowledge-template.md
- prompts/apply-vibe-coding-guardrails.md
- prompts/start-with-vibe-coding-guardrails.md

optional tool inventory 尽量只作为 read-only evidence。如果已经 clone 参考仓库:
- python3 <agent-bootstrap-clone>/scripts/inventory_optional_tools.py --repo-root .
- python3 <agent-bootstrap-clone>/scripts/inventory_optional_tools.py --repo-root . --json

如果无法运行脚本，说明限制并继续直接检查。不要自动安装可选工具。Do not install optional tools automatically. 先把 Obsidian、Lumin Repo Lens、dependency lint、strict type checks、cycle detection、complexity limits 分类为 required、recommended、optional、skipped，再请求安装批准。

只应用最小有用 guardrails。如果是 TS/JS-heavy project 且我批准 Lumin Repo Lens，只把它作为 evidence tool：structural claims require evidence，absence claims require scan range，证据不完整时说 "not observed in this scan range"。

行为变更使用 TDD。修改后运行项目真实 verification commands 和 post-write review。报告修改文件、执行命令、验证结果、optional tools skipped/recommended 和剩余风险。
```

## 每个提示词的使用场景

- `prompts/setup-codex-current-harness.md`: 在 Codex 中应用 shared core。
- `prompts/setup-claude-current-harness.md`: 设置 Claude Code plugin 和 shared role prompts。
- `prompts/setup-shared-core.md`: 目标环境不清楚，最好只阅读 shared prompt guidance。
- `prompts/setup-codex-skills.md`: 检查 optional Codex skill catalog，只安装批准的 skill。
- `prompts/apply-vibe-coding-guardrails.md`: 给应用仓库应用 guardrails。
- `prompts/start-with-vibe-coding-guardrails.md`: 在已有 guardrails 的项目中开始日常工作。
- `prompts/update-agent-bootstrap.md`: pull、render、install、audit、document、review 本仓库。

## Guardrail 强制的内容

- Pre-write lens
- TDD write gate
- Coupling control
- Error discipline
- Test discipline
- Privacy discipline
- Skill discipline

## 可选工具和安装策略

Optional tools 应支持 workflow，而不是替代 workflow。Obsidian、Lumin Repo Lens、dependency lint、cycle detection、strict type checks、complexity limits 都可能有用，但它们是真实 tooling change。不要仅仅因为文档提到某个可选工具就安装它。先 inventory，说明 required、recommended、optional、skipped，再获得安装批准。

## 安装指南

- Codex: [docs/README.codex.md](docs/README.codex.md)
- Claude Code: [docs/README.claude.md](docs/README.claude.md)
- Codex 与 Claude Code frontend design pack: [docs/frontend-design-stack.md](docs/frontend-design-stack.md)
- Codex skills: [docs/codex-skills.md](docs/codex-skills.md)
- Claude Code skills: [docs/claude-skills.md](docs/claude-skills.md)

## 架构

The repository has three layers:

- shared core: `AGENTS.md`, `agents/*.md`, `shared/agent-metadata.json`
- first-class harness adapters: `.codex/`, `.claude-plugin/`, `plugins/process-first-agents/`
- reusable public-safe skills: `skills/karpathy-guidelines/`, `skills/chatgpt-collaboration-harness/`, `skills/hun-engineering-loop/`, `skills/_template/`

详细结构请阅读 [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md)。

## Superpowers 集成

Codex 可以使用 Codex App curated Superpowers plugin。Codex installer 也支持 manual ~/.codex/superpowers fallback。Claude Code 使用 official marketplace 的 upstream `superpowers`，再安装本仓库 generated `process-first-agents` plugin。同时启用两条 Codex discovery path 可能产生重复的 skill 条目。

## 维护这个仓库

- Shared behavior: `AGENTS.md`, `agents/*.md`
- Metadata: `shared/agent-metadata.json`
- Codex installer: `.codex/install.py`
- Claude renderer: `scripts/render_claude_plugin.py`
- Verification: `python3 -m unittest discover -s tests -p 'test_*.py'`, `python3 scripts/audit_agent_stack.py`

Existing clone update:

```bash
git status --short --branch
git pull --ff-only
python3 scripts/render_claude_plugin.py --partner-name "<Name>"
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/audit_agent_stack.py
```

## Agent Stack Audit

检查 Codex、Claude Code、Superpowers state 和 generated Claude plugin bundle:

```bash
python3 scripts/audit_agent_stack.py
```

Default audit is offline/read-only。OpenCode 不再是 default supported surface。

## 测试

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_private_paths.py
```
