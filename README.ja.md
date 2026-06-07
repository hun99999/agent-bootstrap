# agent-bootstrap

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

Codex、Claude Code、OpenCode向けのプロセス重視AIコーディング環境ブートストラップです。

`agent-bootstrap` は、最新のAIコーディングツール向けに、共有 `superpowers` ワークフロー、役割ベースのサブエージェント、トークン効率の高い実行モデル、多言語セットアップ文書を提供します。

> この文書は `README.md` の日本語訳です。正本は英語版です。

## agent-bootstrap を使う理由

- Codex、Claude Code、OpenCodeごとに別々のプロンプトスタックを管理せず、1つの `superpowers` ベースのワークフローを共有できます。
- 計画、実装、レビュー、検証、リリースの役割をサブエージェントと共有プロンプト群で分離し、一貫した作業フローを維持できます。
- スコープの明確な作業、短い handoff、再利用可能な skill を中心に進めることで、トークン浪費を減らす process-first 実行モデルを提供します。
- 1つの汎用 installer を無理に当てるのではなく、各ハーネスのネイティブ方式に合わせた adapter を持ちます。
  - Codex は managed `.codex` 設定と latest `superpowers`
  - Claude Code は marketplace entry と generated agent plugin package
  - OpenCode は generated agents と native plugin wiring
- credential、private MCP endpoint、個人パス、マシン固有の trust state を public baseline に含めないよう設計されています。
- 英語、韓国語、日本語、中国語簡体字の文書を同じレポで提供します。

## このリポジトリの役割

このリポジトリは、単一ツール専用ではなく、複数のコーディングハーネスにインストールできる共通運用モデルの source of truth です。

対象ハーネス:

- Codex
- Claude Code
- OpenCode

OpenClaw への統合方法も文書化しますが、OpenClaw は first-class bootstrap target ではなく integration layer として扱います。

## デフォルトのセットアップ範囲

ユーザーが「このレポを見てセットアップして」とだけ言い、特定のハーネスを指定しない場合、デフォルトは `shared-core-only` です。

`shared-core-only` の意味:

- 現在のツールが対応していれば `superpowers` をインストールまたは更新する
- shared constitution と agent/subagent prompts だけを現在のツールのネイティブ形式で適用する
- ユーザーが明示しない限り、新しいハーネス、ACP backend、gateway、provider stack を選ばない

特に OpenClaw の依頼では、`Codex-first` をデフォルトにせず、shared prompt と skills の層だけを先に揃えるのが正しい初期動作です。

## デフォルト範囲マトリクス

- Codex: `current-harness-only`
- Claude Code: `current-harness-only`
- OpenCode: `current-harness-only`
- OpenClaw: `shared-core-only`

`current-harness-only` とは、すでに Codex、Claude Code、OpenCode の中にいる場合、デフォルトではその現在のハーネスだけを設定し、他のハーネスはユーザーが明示的に要求したときだけ触るという意味です。

## セットアップ用プロンプト

別のエージェントにそのまま貼り付けやすいプロンプト:

- Codex 現在ハーネス専用: [prompts/setup-codex-current-harness.md](prompts/setup-codex-current-harness.md)
- Claude Code 現在ハーネス専用: [prompts/setup-claude-current-harness.md](prompts/setup-claude-current-harness.md)
- OpenCode 現在ハーネス専用: [prompts/setup-opencode-current-harness.md](prompts/setup-opencode-current-harness.md)
- 共通 shared core セットアップ: [prompts/setup-shared-core.md](prompts/setup-shared-core.md)
- OpenClaw shared core 専用: [prompts/setup-openclaw-shared-core.md](prompts/setup-openclaw-shared-core.md)
- OpenClaw ACP 統合: [prompts/setup-openclaw-acp.md](prompts/setup-openclaw-acp.md)

Codex セッション開始用の委任許可文:

```text
このセッションでは、独立して切り分けられる作業について、効率が明確に良くなると判断できる場合に限り、サブエージェントや並列エージェントを使ってよい。これは許可であって必須ではないので、作業が小さい、密結合している、直近の進行をすぐに塞ぐ、または委任オーバーヘッドのほうが大きい場合はローカルで進めること。
```

## インストールガイド

- Codex: [docs/README.codex.md](docs/README.codex.md)
- Claude Code: [docs/README.claude.md](docs/README.claude.md)
- OpenCode: [docs/README.opencode.md](docs/README.opencode.md)
- OpenClaw integration: [docs/README.openclaw.md](docs/README.openclaw.md)

## アーキテクチャ

リポジトリは2層構造です。

- shared core
  - `AGENTS.md`
  - `agents/*.md`
  - `shared/agent-metadata.json`
  - 共通の process-first 憲章と役割プロンプト本文
- harness adapters
  - `.codex/`
  - `.claude-plugin/`
  - `.opencode/`

shared core が運用モデルを一度だけ定義し、各 adapter がそれを対象ハーネスのネイティブ形式に変換します。

## Superpowers 統合

この bootstrap は `obra/superpowers` を中心に構成されています。

- Codex は `~/.agents/skills/superpowers` の symlink パターンを使います。
- OpenCode は `superpowers@git+https://github.com/obra/superpowers.git` の plugin line を使います。
- Claude Code は2層構成です。
  - upstream 公式 `superpowers` skill library
  - このリポジトリが生成する Claude agent plugin package

Codex App の curated Superpowers plugin と手動の `~/.codex/superpowers` fallback を同時に有効にすると、重複する skill 項目が表示されることがあります。意図していない場合は discovery path を1つだけ使います。

目的は、`superpowers` skill library をこのリポジトリにコピーせず、そのまま upstream を再利用することです。

## リポジトリ構成

- `AGENTS.md`
  - 共通憲章テンプレート
- `agents/`
  - 共通役割プロンプト本文
- `shared/agent-metadata.json`
  - 共有説明と OpenCode capability metadata
- `.codex/`
  - Codex installer、template、install guide
- `.opencode/`
  - OpenCode installer、template、install guide
- `.claude-plugin/marketplace.json`
  - リポジトリレベルの Claude marketplace entry
- `plugins/process-first-agents/`
  - 生成済み Claude plugin package
- `scripts/render_claude_plugin.py`
  - shared prompt corpus から Claude plugin package を再生成
- `docs/`
  - ハーネス別ガイド、repo metadata ガイド、OpenClaw 文書
- `tests/`
  - installer、plugin metadata、README 期待値の検証

## Discoverability

GitHub リポジトリの見つけやすさは、通常のWeb SEOよりも repository metadata の影響が大きいです。

このリポジトリは次の方法で discoverability を改善します。

- キーワードを含む canonical README
- 多言語 README
- GitHub repository description と topics
- [docs/repo-metadata.md](docs/repo-metadata.md) にまとめた social preview ガイド

## 制約

このリポジトリには public に共有して安全な baseline だけを含めるべきです。

含めないもの:

- private MCP endpoint
- 個人プロジェクトのパス
- 組織専用 secret
- マシン固有の trust configuration
- credential、token、auth state

## 更新

- Codex と OpenCode: pull 後に各 installer を再実行
- Claude Code: pull 後に `python3 scripts/render_claude_plugin.py --partner-name "<Name>"` を再実行し、plugin を更新

## エージェントスタック監査

更新の前後に、ローカルの Codex、Claude Code、OpenCode、Superpowers の状態を確認するには次を実行します。

```bash
python3 scripts/audit_agent_stack.py
```

デフォルトの監査は offline/read-only です。npm とリモート git に対する最新 drift まで確認する場合は `--online` を追加し、OpenCode など optional tool の不足も失敗扱いにする場合は `--strict` を追加します。

## レガシーファイル

以前の Codex-only bootstrap 時代のファイルが一部残っています。

- `codex-home/`
- `scripts/install.py`
- `scripts/install.sh`
- `prompts/fresh-install.md`

これらは互換性 entrypoint であり、長期的なマルチハーネス構造の中心ではありません。

## テスト

installer と metadata のテストには Python `unittest` を使います。

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
