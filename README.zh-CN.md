# agent-bootstrap

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

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
