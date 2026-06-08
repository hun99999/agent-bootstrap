# agent-bootstrap

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

## 主提示词

把下面内容原样粘贴给 Codex、Claude Code、OpenCode 或其他编码代理。代理应当在这个仓库的 clone 中开始。

```text
请以这个仓库为准，从头到尾设置 agent-bootstrap。

先阅读 AGENTS.md、README.md、docs/agent-setup-playbook.md、docs/global-guardrail-setup.md、docs/vibe-coding-guardrails.md、docs/agent-bootstrap-structure.md 和 docs/local-project-knowledge-template.md。不要编造命令、package name、配置选项或 API 细节。

修改文件之前，运行 git status --short --branch。如果有未提交修改或 untracked file，停止并询问如何处理。确认当前 harness 是 Codex、Claude Code、OpenCode 还是其他，并确认我要求的范围。

选择最小有效范围:
- 如果已经在 Codex、Claude Code 或 OpenCode 中，除非我明确要求其他 harness，否则只配置当前 harness。
- 如果 harness 不明确，应用 shared-core-only。
- 如果这是应用仓库，应用 project guardrail，并创建 project-local knowledge guidance。
- 不要仅仅因为文档提到某个可选工具就安装它。

从头到尾设置所选范围:
- 使用本仓库文档化的命令安装或 render shared core。
- 只通过本仓库文档化的路径更新 Superpowers。
- 如果 shared prompt 或 metadata 改变，重新生成 Claude plugin output。
- inventory Obsidian、Lumin Repo Lens、dependency lint、strict type checks、cycle detection、complexity limits 等可选工具，并把每个工具分类为 required、recommended、optional 或 skipped。安装任何东西之前必须询问。
- 不要把 private path、credential、MCP endpoint、auth state、browser profile 或 machine-specific trust setting 放入 tracked file。
- 运行本仓库真实的验证命令，包括 tests 和 scripts/audit_agent_stack.py。
- 用 post-write review 检查 duplicate helper、hidden coupling、swallowed error、fallback drift、unmanaged re-export、fan-in/fan-out hotspot、weak test、generated-output drift 和 private path leakage。
- 适当时以小的可评审单位提交，并总结改了什么、安装了什么、运行了哪些命令、验证结果和剩余风险。
```

面向 Codex、Claude Code 和 OpenCode 的流程优先 AI 编程环境引导仓库。

`agent-bootstrap` 提供可复用的 `superpowers` 工作流、基于角色的子代理、更加节省 token 的执行方式，以及面向现代 AI 编码工具的多语言安装文档。

> 本文档是 `README.md` 的简体中文翻译。以英文版为准。

## 为什么使用 agent-bootstrap？

- 不需要为 Codex、Claude Code、OpenCode 分别维护不同的提示词栈，而是共享一套基于 `superpowers` 的工作流。
- 通过子代理和共享提示语料，把规划、实现、评审、验证、发布职责拆开，保持一致的协作流程。
- 借助范围清晰的任务、短 handoff 和可复用 skill，推动 token-efficient 的 process-first 执行模型，减少上下文浪费。
- 不是一个勉强适配所有工具的通用 installer，而是针对每个 harness 的原生适配层。
  - Codex 使用 managed `.codex` 配置和 latest `superpowers`
  - Claude Code 使用 marketplace entry 和 generated agent plugin package
  - OpenCode 使用 generated agents 和 native plugin wiring
- 设计目标就是不把 credential、private MCP endpoint、个人路径或机器特定 trust state 放进 public baseline。
- 同一个仓库同时提供英文、韩文、日文、简体中文文档。

## 目标项目 Claude Code 提示词

在目标项目仓库中打开 Claude Code，然后原样粘贴下面的提示词。它引用公开 URL，不依赖个人本地路径。

```text
请把 agent-bootstrap 的 vibe-coding guardrails 应用到这个项目。

参考仓库:
- https://github.com/hun99999/agent-bootstrap

首先在这个项目中运行 git status --short --branch。如果有未提交修改或 untracked files，停止并询问我如何处理。未经批准，不要 stash、delete、overwrite 或 git add。

然后检查这个项目:
- AGENTS.md、CLAUDE.md、README.md 和现有 docs
- package.json、pyproject.toml、Cargo.toml、go.mod 或其他语言/工具信号
- 真实的 test、lint、type-check、build 命令
- source-of-truth helper、type、schema、public API、module boundary、dependency direction、error boundary、re-export/barrel policy、known hotspot

阅读上面参考仓库 URL 中的文档。必要时，在这个项目之外 read-only clone 后阅读。使用这些文件作为 source:
- docs/agent-setup-playbook.md
- docs/vibe-coding-guardrails.md
- docs/global-guardrail-setup.md
- docs/local-project-knowledge-template.md
- prompts/apply-vibe-coding-guardrails.md
- prompts/start-with-vibe-coding-guardrails.md

如果可以，把 optional tool inventory 只作为 read-only evidence 运行。如果已经 clone 参考仓库，就用那个 clone 的 script 检查这个项目 root:
- python3 <agent-bootstrap-clone>/scripts/inventory_optional_tools.py --repo-root .
- python3 <agent-bootstrap-clone>/scripts/inventory_optional_tools.py --repo-root . --json

如果这个 script 在本地不可用，说明限制，并继续直接检查。不要自动安装可选工具。Obsidian、Lumin Repo Lens、dependency lint、strict type checks、cycle detection、complexity limits 在请求安装批准前，必须先分类为 required、recommended、optional 或 skipped。

只应用这个项目需要的最小 guardrail:
- 添加或更新这个项目已经使用的 agent guidance
- 基于 docs/local-project-knowledge-template.md 创建 project structure index
- 记录 source-of-truth helper、type、schema、public API、module boundary、dependency direction、error boundary、re-export policy、test strategy、known hotspot 和 decision
- 只有在可能产生 local evidence artifact 时，才把 .audit/ 加入 .gitignore
- 不要提交 personal vault path、private path、credential、MCP endpoint、auth state、browser profile 或 machine-specific trust setting

只有当这个项目是 TS/JS-heavy，并且我批准使用 Lumin Repo Lens 时，才把它作为 evidence tool 使用:
- structural claim 需要 evidence
- absence claim 需要 scan range
- 证据不完整时，说 "not observed in this scan range"
- pre-write intent 使用 names、shapes、files、dependencies、plannedTypeEscapes
- post-write machine evidence 仅限 type escapes、unexpected files、scan range、confidence changes
- duplicate helpers、dependency drift、public API drift、re-export drift 是需要 direct evidence 的 manual review claim

行为变更使用 TDD。修改后运行这个项目真实的 verification 命令和 post-write review。报告修改文件、执行命令、验证结果、skipped/recommended optional tools 和剩余风险。
```

## 快速开始

先选择范围。代理设置最容易失败的情况，是一次性改动新的 harness、新插件栈、新 provider 和仓库工作流。先应用最小的有效范围，验证之后再扩大。

1. 如果要让这台机器未来的 Codex、Claude Code 或 OpenCode 会话默认带上这些规则，请使用 [docs/global-guardrail-setup.md](docs/global-guardrail-setup.md)。
2. 如果要把同样的纪律应用到另一个应用仓库，请在目标仓库中粘贴 [prompts/apply-vibe-coding-guardrails.md](prompts/apply-vibe-coding-guardrails.md)。
3. 如果某个仓库已经有 guardrail，并且要开始功能、bugfix 或重构，请使用 [prompts/start-with-vibe-coding-guardrails.md](prompts/start-with-vibe-coding-guardrails.md)。
4. 如果这个 bootstrap 仓库本身发生变化，需要重新应用、审计或改进，请使用 [prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md)。

## 每个提示词的使用场景

- `prompts/setup-codex-current-harness.md`: 在 Codex 中只为当前 Codex harness 应用 shared core。
- `prompts/setup-claude-current-harness.md`: 在 Claude Code 中设置 Claude plugin 和共享角色提示词。
- `prompts/setup-opencode-current-harness.md`: 在 OpenCode 中应用 generated agents 和 native plugin wiring。
- `prompts/setup-shared-core.md`: 当目标环境不清楚，最安全的做法是只应用 shared prompt/skills 层时使用。
- `prompts/apply-vibe-coding-guardrails.md`: 在应用仓库中加入结构地图、edge-case-first 测试、依赖边界检查和 project-local knowledge。
- `prompts/start-with-vibe-coding-guardrails.md`: 在已有 project map 和 guardrail workflow 的仓库中，开始日常功能、bugfix 或重构。
- `prompts/update-agent-bootstrap.md`: 针对本仓库本身，执行 pull、render、install、audit、文档更新和 review。

## Guardrail 强制的内容

这些 guardrail 的目标，是减少代理在每个会话中丢失结构记忆、重复创建 helper、制造隐藏耦合的问题。

- Pre-write lens: 编辑前检查 module boundary、dependency direction、public API、helper、type、shape、re-export、test、error boundary 和 hotspot。
- TDD write gate: 先写空输入、null/missing、边界值、失败路径、side effect 和必要并发场景的测试，确认它按预期失败后再实现。
- 耦合控制: 避免隐藏 import、初始化顺序契约、重复 shape、无人管理的 barrel/re-export、fan-in/fan-out hotspot。
- 错误纪律: 不静默吞掉错误，不添加没有文档化需求的 fallback，并把错误处理放在明确边界上。
- 测试纪律: 验证行为和 side effect，而不是字符串或函数名；mock 只放在外部边界。
- 隐私边界: 不提交个人 vault 路径、private project path、credential、MCP endpoint、auth state、browser profile 或 machine-specific trust setting。

## 可选工具和安装策略

可选工具只是辅助 workflow，不是 workflow 本身。

- Obsidian 适合在仓库结构较大、反复重新理解成本很高时，作为 private project wiki 使用。
- Lumin Repo Lens 适合 TS/JS 仓库，用 AST 证据查找 duplicate helper、hidden coupling、re-export drift 或 fan-in/fan-out hotspot。
- Dependency lint、cycle detection、strict type checks、complexity limits、file/function size limits 都很有用，但它们是真实的 tooling 变更。

不要仅仅因为文档提到某个可选工具就安装它。先 inventory 当前环境，说明该工具是 required/recommended/optional/skipped，安装前取得批准，验证 package name 或 official source，并且只在仓库里留下 project-safe usage guidance。

## 维护这个仓库

修改这个 bootstrap 之前，先把 [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md) 当作 repo-local map 阅读。

- 共享行为规则在 `AGENTS.md` 和 `agents/*.md` 中修改。
- 角色 metadata 在 `shared/agent-metadata.json` 中修改。
- Codex 安装行为在 `.codex/install.py` 中修改。
- OpenCode 安装行为在 `.opencode/install.py` 中修改。
- Claude plugin render 行为在 `scripts/render_claude_plugin.py` 中修改。
- 修改 shared prompt 或 metadata 后，用 `python3 scripts/render_claude_plugin.py --partner-name "<Name>"` 重新生成 Claude plugin output。
- 使用 `python3 -m unittest discover -s tests -p 'test_*.py'` 和 `python3 scripts/audit_agent_stack.py` 验证。

## 这个仓库是什么

这个仓库是一个共享操作模型的 source of truth，它可以安装到多个编码 harness 中，而不是只绑定 Codex。

直接支持的 harness：

- Codex
- Claude Code
- OpenCode

它也会说明如何接入 OpenClaw，但 OpenClaw 被刻意视为 integration layer，而不是 first-class bootstrap target。

## 默认设置范围

如果用户只是说“看这个仓库帮我设一下”，但没有指定具体 harness，那么默认范围应当是 `shared-core-only`。

`shared-core-only` 的含义：

- 如果当前工具支持，就安装或更新 `superpowers`
- 只把 shared constitution 和 agent/subagent prompts 以当前工具的原生格式落地
- 除非用户明确要求，否则不要擅自选择新的 harness、ACP backend、gateway 或 provider stack

尤其对 OpenClaw 场景，默认行为不应该是 `Codex-first`，而应该先只处理 shared prompt 和 skills 层。

## 默认范围矩阵

- Codex: `current-harness-only`
- Claude Code: `current-harness-only`
- OpenCode: `current-harness-only`
- OpenClaw: `shared-core-only`

`current-harness-only` 的意思是：如果你已经处在 Codex、Claude Code 或 OpenCode 里，那么默认只配置当前这个 harness，除非用户明确要求，否则不要去配置别的 harness。

## 设置提示词

下面这些提示词适合直接贴给其他代理：

- Codex 当前 harness 专用: [prompts/setup-codex-current-harness.md](prompts/setup-codex-current-harness.md)
- Claude Code 当前 harness 专用: [prompts/setup-claude-current-harness.md](prompts/setup-claude-current-harness.md)
- OpenCode 当前 harness 专用: [prompts/setup-opencode-current-harness.md](prompts/setup-opencode-current-harness.md)
- 通用 shared core 设置: [prompts/setup-shared-core.md](prompts/setup-shared-core.md)
- OpenClaw shared core 专用: [prompts/setup-openclaw-shared-core.md](prompts/setup-openclaw-shared-core.md)
- OpenClaw ACP 集成: [prompts/setup-openclaw-acp.md](prompts/setup-openclaw-acp.md)
- 更新/复查这个 bootstrap: [prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md)

Codex 会话开场委托许可文案：

```text
在这个会话里，如果某些工作可以独立拆分，并且你判断使用子代理或并行代理能明显提高效率，就可以使用它们。这是许可，不是强制要求；如果任务很小、耦合很紧、会立刻阻塞当前进度，或者委托开销更大，就留在本地处理。
```

## 安装指南

- Codex: [docs/README.codex.md](docs/README.codex.md)
- Claude Code: [docs/README.claude.md](docs/README.claude.md)
- OpenCode: [docs/README.opencode.md](docs/README.opencode.md)
- OpenClaw integration: [docs/README.openclaw.md](docs/README.openclaw.md)

## 架构

仓库分成两层：

- shared core
  - `AGENTS.md`
  - `agents/*.md`
  - `shared/agent-metadata.json`
  - 公共的 process-first 宪章和角色提示正文
- harness adapters
  - `.codex/`
  - `.claude-plugin/`
  - `.opencode/`

shared core 只定义一次操作模型，各个 adapter 再把它转换为目标 harness 需要的原生格式。

详细的项目结构图、更新流程、source-of-truth 边界和生成物策略，请参见 [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md)。

## Superpowers 集成

这个 bootstrap 以 `obra/superpowers` 为中心。

- Codex 使用原生 `~/.agents/skills/superpowers` 符号链接模式。
- OpenCode 使用原生插件行 `superpowers@git+https://github.com/obra/superpowers.git`。
- Claude Code 分成两层：
  - upstream 官方 `superpowers` skill library
  - 本仓库生成的 Claude agent plugin package

如果同时启用 Codex App curated Superpowers plugin 和手动 `~/.codex/superpowers` fallback，可能会出现重复的 skill 条目。除非这是有意行为，否则只使用一条 discovery path。

目标是复用上游 `superpowers`，而不是把 skill library 复制进本仓库。

## 仓库结构

- `AGENTS.md`
  - 共享宪章模板
- `agents/`
  - 共享角色提示正文
- `shared/agent-metadata.json`
  - 共享描述和 OpenCode capability metadata
- `.codex/`
  - Codex installer、template、install guide
- `.opencode/`
  - OpenCode installer、template、install guide
- `.claude-plugin/marketplace.json`
  - 仓库级 Claude marketplace entry
- `plugins/process-first-agents/`
  - 已生成的 Claude plugin package
- `scripts/render_claude_plugin.py`
  - 从 shared prompt corpus 重新生成 Claude plugin package
- `docs/`
  - 各 harness 指南、repo metadata 指南、OpenClaw 文档
- `tests/`
  - 对 installer、plugin metadata、README 期望的 Python 校验

## 可发现性

GitHub 仓库的可发现性，更依赖 repository metadata，而不是传统网页 SEO。

本仓库通过以下方式提升 discoverability：

- 含关键字的 canonical README
- 多语言 README
- GitHub repository description 和 topics
- 在 [docs/repo-metadata.md](docs/repo-metadata.md) 中整理的 social preview 指南

## 约束

这个仓库只能包含可以安全公开共享的 baseline。

不要放入：

- private MCP endpoint
- 个人项目路径
- 组织专用 secret
- 机器特定的 trust configuration
- credential、token、auth state

## 更新

- Codex 和 OpenCode：拉取更新后重新运行各自 installer
- Claude Code：拉取更新后重新运行 `python3 scripts/render_claude_plugin.py --partner-name "<Name>"`，然后更新插件安装

## 代理栈审计

在更新前后，可以运行下面的命令检查本地 Codex、Claude Code、OpenCode 和 Superpowers 状态：

```bash
python3 scripts/audit_agent_stack.py
```

默认审计是 offline/read-only。需要检查 npm 和远程 git 的最新 drift 时添加 `--online`；如果希望 OpenCode 等 optional tool 缺失也导致失败，添加 `--strict`。

## 兼容旧文件

仓库里仍保留了一些早期 Codex-only bootstrap 时代的文件。

- `codex-home/`
- `scripts/install.py`
- `scripts/install.sh`
- `prompts/fresh-install.md`

它们是兼容性 entrypoint，不是长期的多 harness 主结构。

## 测试

installer 和 metadata 使用 Python `unittest` 进行验证：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
