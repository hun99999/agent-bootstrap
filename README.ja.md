# agent-bootstrap

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

## マスタープロンプト

次を Codex または Claude Code にそのまま貼り付けます。エージェントはこのリポジトリの clone 内で開始してください。

```text
このリポジトリから agent-bootstrap を最後までセットアップしてください。

まず AGENTS.md, README.md, docs/agent-setup-playbook.md, docs/global-guardrail-setup.md, docs/vibe-coding-guardrails.md, docs/agent-bootstrap-structure.md, docs/local-project-knowledge-template.md を読んでください。コマンド、パッケージ名、設定オプション、API 詳細を推測で作らないでください。

ファイルを変更する前に git status --short --branch を実行してください。未コミット変更や untracked file があれば停止し、どう扱うか確認してください。現在のハーネスが Codex か Claude Code かを確認し、私が要求した範囲を確認してください。

ローカル設定を render する前に、エージェントが私を何と呼ぶか質問してください。現在の Codex と Claude runtime が実際に利用できる model と reasoning level を確認し、最新 model 名や paid plan を固定せず、利用可能な選択を継承してください。選択した名前は local に保持してください。選択した名前や、その名前を含む render 結果を commit しないでください。

docs/frontend-design-stack.md を読んでください。tracked frontend-design-pack を検証し、Figma は認証せず利用可否だけを報告し、runtime plugin copy の install または replacement 前に承認を求めてください。承認後は installed root を別に検証し、fresh task/session で discovery を確認してください。

最小の有効スコープを選んでください:
- すでに Codex の中にいる場合、私が Claude Code も明示的に要求しない限り Codex だけを設定してください。
- すでに Claude Code の中にいる場合、私が Codex も明示的に要求しない限り Claude Code だけを設定してください。
- サポート対象のハーネスが明確でなければ、どれを設定するか確認してください。
- アプリケーションリポジトリなら project guardrails と project-local knowledge guidance を適用してください。
- 言及されているだけの理由で任意ツールをインストールしないでください。

選択したスコープを最後まで設定してください:
- このリポジトリに文書化されたコマンドで shared core を install または render する
- upstream Superpowers は optional として扱う。Codex installer の default は `skip` のままにし、私が明示的に選択した場合だけ `--superpowers-mode manual` を使う
- shared prompts や metadata が変わった場合は Claude plugin output を再生成する
- public default base skill は karpathy-guidelines にする
- hun-engineering-loop は明示承認がない限り Hun local runtime wrapper として扱う
- chatgpt-collaboration-harness を Claude Code にインストールしない
- Obsidian, Lumin Repo Lens, dependency lint, strict type checks, cycle detection, complexity limits を optional tool inventory として read-only に確認し、required, recommended, optional, skipped に分類してからインストール承認を求める
- private path, credential, MCP endpoint, auth state, browser profile, machine-specific trust setting を tracked file に入れない
- tests と scripts/audit_agent_stack.py を含む実際の検証コマンドを実行する
- duplicate helpers, hidden coupling, swallowed errors, fallback drift, unmanaged re-exports, fan-in/fan-out hotspots, weak tests, generated-output drift, private path leakage の post-write review を行う
- 適切なら小さくコミットし、変更内容、インストール内容、実行したコマンド、検証結果、残リスクを要約する
```

Codex と Claude Code 向けの process-first AI coding environment bootstrap です。

`agent-bootstrap` は、薄い process-first core、role-based subagents、token-efficient な作業習慣、詳細なセットアップ文書、`karpathy-guidelines` ベースの public-safe skill model、optional な `superpowers` 経路を新しい clone に提供します。

## 現在のサポート対象

Codex と Claude Code だけが first-class setup target です。

OpenCode と OpenClaw は legacy/reference material であり active service target ではありません。古いファイルは履歴や移行確認のために git に残る場合がありますが、新しい README、setup guide、default audit では通常の install path として扱いません。

## Private Project Skills

auto-eva のような private project skill はこの public repository にコミットしません。実際の project-specific skill は Codex なら `~/.codex/skills`、Claude Code なら `~/.claude/skills` のような local runtime home に置きます。このリポジトリには templates and public-safe process guidance だけを置き、private access path, credential, auth state, browser profile, customer data, machine-specific trust setting は入れません。

## コアモデル

- `karpathy-guidelines` が public default base skill です。assumption、simplicity、surgical diff、verifiable success criteria を重視します。
- `superpowers` は brainstorming, planning, TDD, debugging, verification, review の optional workflow library です。薄い process-first core は Superpowers を必要としません。
- `hun-engineering-loop` は Hun local wrapper です。memory preflight, source-of-truth ordering, high-risk approval boundary, artifact-first execution, QA evidence contract を加えますが、public default install set ではありません。
- `chatgpt-collaboration-harness` は Codex 側の ChatGPT Pro collaboration skill です。Claude Code にはデフォルトで入れません。
- `handoff` は explicit-use catalog skill です。別の agent や session に現在の作業状態を渡すようユーザーが明示的に求めた場合だけ使い、[skills/README.md](skills/README.md)、[docs/codex-skills.md](docs/codex-skills.md)、[prompts/setup-codex-skills.md](prompts/setup-codex-skills.md) から確認します。

Memory は recall layer であり source of truth ではありません。現在の user instruction、repo docs、scripts、tests、`AGENTS.md`、observed runtime output が優先されます。

## クイックスタート

最初にスコープを選ぶことが重要です。多くの失敗は、別のハーネス、plugin stack、optional tools、project rules を一度に設定しようとすることから始まります。

1. Clone または pull します。

   ```bash
   git clone https://github.com/hun99999/agent-bootstrap.git
   cd agent-bootstrap
   git status --short --branch
   ```

2. 編集やインストール前に共通ルールを読みます。

   ```bash
   sed -n '1,220p' AGENTS.md
   sed -n '1,220p' docs/agent-setup-playbook.md
   ```

3. 現在のサポート対象を選びます。

   - Codex: [docs/README.codex.md](docs/README.codex.md)
   - Claude Code: [docs/README.claude.md](docs/README.claude.md)

4. 変更で無効になった evidence に合わせて検証を選びます。広範囲、cross-cutting、
   high-risk、release-bound の変更だけで次の full regression を使います。

   ```bash
   python3 -m unittest discover -s tests -p 'test_*.py'
   python3 scripts/audit_agent_stack.py
   ```

5. 既存 clone を更新するときは pull 後に影響を受けた generated artifact と無効になった
   check だけを再実行します。focused result が wider impact を示した場合も full
   regression に広げます。

   ```bash
   git pull --ff-only
   python3 scripts/render_claude_plugin.py --partner-name "<Name>"
   python3 -m unittest discover -s tests -p 'test_*.py'
   python3 scripts/audit_agent_stack.py
   ```

## エージェントに依頼できること

- Install global defaults: [docs/global-guardrail-setup.md](docs/global-guardrail-setup.md) を使って Codex または Claude Code の user-level defaults に guardrails を入れます。
- Apply guardrails to a project: [prompts/apply-vibe-coding-guardrails.md](prompts/apply-vibe-coding-guardrails.md) を対象リポジトリで使います。
- Start feature work inside a guarded project: [prompts/start-with-vibe-coding-guardrails.md](prompts/start-with-vibe-coding-guardrails.md) を feature, bugfix, refactor の前に使います。
- Review optional Codex skills: [skills/README.md](skills/README.md), [docs/codex-skills.md](docs/codex-skills.md), [prompts/setup-codex-skills.md](prompts/setup-codex-skills.md) を使います。
- Update this bootstrap after repository changes: [prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md) を pull 後の再監査に使います。
- Explain repository structure: [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md) を先に読みます。

Optional tooling is decision-based. Obsidian, Lumin Repo Lens, dependency lint, cycle detection, strict type checks, complexity limits は、対象リポジトリと承認が正当化するときだけ使います。

## 対象プロジェクト用 Claude Code プロンプト

Claude Code を対象プロジェクトのリポジトリ内で開き、次を貼り付けます。公開 URL を参照するため、個人の local path に依存しません。

```text
このプロジェクトに agent-bootstrap ベースの vibe-coding guardrails を適用してください。

参照リポジトリ:
- https://github.com/hun99999/agent-bootstrap

まずこのプロジェクトで git status --short --branch を実行してください。未コミット変更や untracked files があれば停止して扱いを確認してください。承認なしに stash, delete, overwrite, git add をしないでください。

次を確認してください:
- AGENTS.md, CLAUDE.md, README.md, existing docs
- package.json, pyproject.toml, Cargo.toml, go.mod, or other tooling signals
- real test, lint, type-check, build commands
- source-of-truth helpers, types, schemas, public APIs, module boundaries, dependency direction, error boundaries, re-export policy, known hotspots

参照リポジトリの docs を URL から読みます。必要なら対象プロジェクト外に read-only clone します:
- docs/agent-setup-playbook.md
- docs/vibe-coding-guardrails.md
- docs/global-guardrail-setup.md
- docs/local-project-knowledge-template.md
- prompts/apply-vibe-coding-guardrails.md
- prompts/start-with-vibe-coding-guardrails.md

optional tool inventory は read-only evidence として扱ってください。clone した場合:
- python3 <agent-bootstrap-clone>/scripts/inventory_optional_tools.py --repo-root .
- python3 <agent-bootstrap-clone>/scripts/inventory_optional_tools.py --repo-root . --json

使えない場合は制約を説明して直接調査を続けます。任意ツールを自動インストールしない。Do not install optional tools automatically. Obsidian, Lumin Repo Lens, dependency lint, strict type checks, cycle detection, complexity limits を required, recommended, optional, skipped に分類してから承認を求めます。

必要最小限の guardrails だけ適用してください。TS/JS-heavy project で Lumin Repo Lens を承認された場合、structural claims require evidence、absence claims require scan range、部分的な evidence なら "not observed in this scan range" と言ってください。

behavior が明確で testable、または repository が要求する場合だけ test-first を使ってください。invalidated evidence から検証を選びます: narrow change では focused check、関連する source, configuration, dependencies, toolchain, runtime inputs が変わらない場合だけ既存の合格結果を再利用し、broad, cross-cutting, high-risk, release-bound, wider-impact の作業だけで full regression を実行します。prose, generated output, mechanical configuration には比例した structural または executable check を使います。unrun check が合格したと主張しないでください。変更後は post-write review を行い、変更ファイル、実行したコマンド、検証結果、optional tools skipped/recommended、残リスクを報告してください。
```

## 各プロンプトを使う場面

- `prompts/setup-codex-current-harness.md`: Codex に shared core を適用する場合。
- `prompts/setup-claude-current-harness.md`: Claude Code plugin と shared role prompts を設定する場合。
- `prompts/setup-shared-core.md`: 対象環境が不明で、install せず shared prompt guidance を読むのが安全な場合。
- `prompts/setup-codex-skills.md`: optional Codex skill catalog を調べ、承認された skill だけ入れる場合。
- `prompts/apply-vibe-coding-guardrails.md`: application repository に guardrails を適用する場合。
- `prompts/start-with-vibe-coding-guardrails.md`: すでに guardrails のある project で通常作業を始める場合。
- `prompts/update-agent-bootstrap.md`: この repository を pull, render, install, audit, document, review する場合。

## Guardrail が強制すること

- Pre-write lens
- Verification gate: behavior が明確で testable、または repository-required の場合だけ test-first を使い、それ以外は比例した structural または executable check を使います。invalidated evidence から検証を選び、broad, cross-cutting, high-risk, release-bound, wider-impact の作業だけで full regression を実行します。unrun check が合格したと主張しません。
- Coupling control
- Error discipline
- Test discipline
- Privacy discipline
- Skill discipline

## 任意ツールとインストールポリシー

Optional tools は workflow を支えるためのものです。Obsidian, Lumin Repo Lens, dependency lint, cycle detection, strict type checks, complexity limits は有用ですが、実際の tooling change です。言及されているだけの理由で任意ツールをインストールしません。まず inventory を取り、required, recommended, optional, skipped を説明し、インストール前に承認を得ます。

## インストールガイド

- Codex: [docs/README.codex.md](docs/README.codex.md)
- Claude Code: [docs/README.claude.md](docs/README.claude.md)
- Codex・Claude Code frontend design pack: [docs/frontend-design-stack.md](docs/frontend-design-stack.md)
- Codex skills: [docs/codex-skills.md](docs/codex-skills.md)
- Claude Code skills: [docs/claude-skills.md](docs/claude-skills.md)

## アーキテクチャ

The repository has four layers:

- shared core: `AGENTS.md`, `agents/*.md`, `shared/agent-metadata.json`
- reviewed frontend design source: `design-stack/`
- first-class harness adapters: `.codex/`, `.claude-plugin/`, `plugins/process-first-agents/`, `plugins/frontend-design-pack/`
- reusable public-safe skills: `skills/karpathy-guidelines/`, `skills/chatgpt-collaboration-harness/`, `skills/handoff/`, `skills/hun-engineering-loop/`, `skills/_template/`

詳細は [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md) を読んでください。

## Superpowers 統合

薄い process-first core は Superpowers なしでも動作します。Superpowers は Codex と Claude Code のどちらでも optional で、ユーザーが選択するものです。

- Codex installer の default は `skip` です。manual checkout を明示的に選んだ場合だけ `--superpowers-mode manual` を使います。
- `skip` は Superpowers の既存状態を変更しません。既存の curated または manual discovery を無効化したり削除したりしません。
- model と reasoning の選択は Superpowers の選択から独立しています。`skip` または `manual` を選んでも model や reasoning level は選択・固定・変更されません。
- Codex App curated Superpowers plugin は別に利用でき、installer は local skill discovery 用の manual ~/.codex/superpowers fallback をサポートします。
- Claude Superpowers も optional で、この repository の generated `process-first-agents` plugin とは別です。ユーザーが明示的に選択した場合だけ install または update し、`process-first-agents` は Superpowers を必要としません。

Codex App curated Superpowers plugin と manual fallback の両方を有効にすると、重複する skill 項目 が生じる可能性があります。意図しない場合は discovery path を一つだけ使います。

## このリポジトリの保守

- Shared behavior: `AGENTS.md`, `agents/*.md`
- Metadata: `shared/agent-metadata.json`
- Codex installer: `.codex/install.py`
- Claude renderer: `scripts/render_claude_plugin.py`
- Frontend design source and router: `design-stack/`
- Frontend design renderer: `scripts/render_frontend_design_plugin.py`; do not edit `plugins/frontend-design-pack/` by hand
- Verification: narrow change では invalidated focused checks を使います。full regression
  (`python3 -m unittest discover -s tests -p 'test_*.py'`) は broad, cross-cutting, high-risk,
  release-bound, wider-impact の場合だけ実行します。必要な scope に応じて
  `python3 scripts/audit_agent_stack.py` と `python3 scripts/validate_frontend_design_stack.py --repo-root .` を追加します。

Existing clone update: 次の例は full regression が必要な場合だけ使います:

```bash
git status --short --branch
git pull --ff-only
python3 scripts/render_claude_plugin.py --partner-name "<Name>"
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/audit_agent_stack.py
```

更新が `design-stack/` または `plugins/frontend-design-pack/` に触れる場合は、
[docs/frontend-design-stack.md](docs/frontend-design-stack.md) と
[prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md) の条件付き手順に従います。
pull 後に live runtime root を解決して検証します。local Codex marketplace では tracked
plugin root の場合がありますが、cached install は別の場所にある場合があります。
cached install の置換前に個別の承認を得て、解決した root を検証し、fresh task または
session で discovery を確認します。

## Agent Stack Audit

Codex, Claude Code, optional Superpowers state, generated Claude plugin bundle を確認します。

```bash
python3 scripts/audit_agent_stack.py
```

Default audit is offline/read-only. OpenCode は default supported surface ではありません。

## テスト

次の full command は変更または release boundary が full regression を必要とする場合だけ
使います。narrow change では関連する test module や structural check を実行し、入力が
変わっていない passing evidence は繰り返しません。

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_private_paths.py
```
