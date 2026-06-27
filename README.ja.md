# agent-bootstrap

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

## マスタープロンプト

次を Codex、Claude Code、OpenCode、または別のコーディングエージェントにそのまま貼り付けます。エージェントはこのリポジトリの clone 内で開始してください。

```text
このリポジトリを基準に agent-bootstrap を最初から最後までセットアップしてください。

まず AGENTS.md、README.md、docs/agent-setup-playbook.md、docs/global-guardrail-setup.md、docs/vibe-coding-guardrails.md、docs/agent-bootstrap-structure.md、docs/local-project-knowledge-template.md を読んでください。コマンド、package name、設定オプション、API 詳細を作り出さないでください。

ファイルを変更する前に git status --short --branch を実行してください。未コミット変更や untracked file があれば停止し、どう扱うか確認してください。現在のハーネスが Codex、Claude Code、OpenCode、その他のどれかを確認し、私が要求した範囲を確認してください。

最小の有効スコープを選んでください:
- すでに Codex、Claude Code、OpenCode の中にいる場合、私が明示的に別のハーネスを要求しない限り、現在のハーネスだけを設定してください。
- ハーネスが不明な場合は shared-core-only を適用してください。
- アプリケーションリポジトリの場合は project guardrail を適用し、project-local knowledge guidance を作ってください。
- 言及されているだけの理由で任意ツールをインストールしないでください。

選んだ範囲を最初から最後までセットアップしてください:
- このリポジトリに文書化されたコマンドで shared core をインストールまたは render してください。
- Superpowers はこのリポジトリに文書化された経路でのみ更新してください。
- shared prompt または metadata が変わった場合は Claude plugin output を再生成してください。
- Obsidian、Lumin Repo Lens、dependency lint、strict type checks、cycle detection、complexity limits などの任意ツールを inventory し、required、recommended、optional、skipped のいずれかに分類してください。何かをインストールする前には必ず確認してください。
- private path、credential、MCP endpoint、auth state、browser profile、machine-specific trust setting を tracked file に入れないでください。
- tests と scripts/audit_agent_stack.py を含む、このリポジトリの実際の検証コマンドを実行してください。
- duplicate helper、hidden coupling、swallowed error、fallback drift、unmanaged re-export、fan-in/fan-out hotspot、weak test、generated-output drift、private path leakage を post-write review で確認してください。
- 適切であれば小さな単位で commit し、変更内容、インストールしたもの、実行したコマンド、検証結果、残リスクを要約してください。
```

Codex、Claude Code、OpenCode向けのプロセス重視AIコーディング環境ブートストラップです。

`agent-bootstrap` は、最新のAIコーディングツール向けに、共有 `superpowers` ワークフロー、役割ベースのサブエージェント、トークン効率の高い実行モデル、多言語セットアップ文書を提供します。

> この文書は `README.md` の日本語訳です。正本は英語版です。

## 現在の公開スコープ

Codex と Claude Code が現在の first-class setup target です。OpenCode と OpenClaw は optional/reference surface として残し、互換性維持に役立つ場合だけ既存文書を参照します。これらをデフォルトのセットアップ経路として扱わないでください。

## Private Project Skills

auto-eva のような private project skill はこの public repository にコミットしません。実際のプロジェクト別 skill は、Codex 用の `~/.codex/skills` や Claude Code 用の `~/.claude/skills` などローカル runtime home に置きます。このリポジトリには templates and public-safe process guidance だけを置き、private access path、credential、auth state、browser profile、customer data、machine-specific trust setting は入れません。

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

## 対象プロジェクト用 Claude Code プロンプト

Claude Code を対象プロジェクトのリポジトリ内で開き、次をそのまま貼り付けます。公開 URL を参照するため、個人ローカルパスに依存しません。

```text
このプロジェクトに agent-bootstrap ベースの vibe-coding guardrails を適用してください。

参照リポジトリ:
- https://github.com/hun99999/agent-bootstrap

まずこのプロジェクトで git status --short --branch を実行してください。未コミット変更または untracked files がある場合は停止し、どう扱うか私に確認してください。承認なしに stash、delete、overwrite、git add をしないでください。

次にこのプロジェクトを調査してください:
- AGENTS.md、CLAUDE.md、README.md、既存 docs
- package.json、pyproject.toml、Cargo.toml、go.mod、または他の言語/ツールの手がかり
- 実際の test、lint、type-check、build コマンド
- source-of-truth helper、type、schema、public API、module boundary、dependency direction、error boundary、re-export/barrel policy、known hotspot

上の参照リポジトリ URL の文書を読んでください。必要ならこのプロジェクト外に read-only clone して読んでください。次のファイルを source として使ってください:
- docs/agent-setup-playbook.md
- docs/vibe-coding-guardrails.md
- docs/global-guardrail-setup.md
- docs/local-project-knowledge-template.md
- prompts/apply-vibe-coding-guardrails.md
- prompts/start-with-vibe-coding-guardrails.md

可能なら optional tool inventory を read-only evidence としてだけ実行してください。参照リポジトリを clone した場合は、その clone の script をこのプロジェクト root に対して実行してください:
- python3 <agent-bootstrap-clone>/scripts/inventory_optional_tools.py --repo-root .
- python3 <agent-bootstrap-clone>/scripts/inventory_optional_tools.py --repo-root . --json

その script がローカルで使えない場合は、その制約を説明し、直接調査で続けてください。任意ツールを自動インストールしないでください。Obsidian、Lumin Repo Lens、dependency lint、strict type checks、cycle detection、complexity limits は、インストール承認を求める前に required、recommended、optional、skipped のいずれかに分類してください。

このプロジェクトに必要な最小限の guardrail だけを適用してください:
- このプロジェクトがすでに使っている agent guidance を追加または更新する
- docs/local-project-knowledge-template.md をもとに project structure index を作る
- source-of-truth helper、type、schema、public API、module boundary、dependency direction、error boundary、re-export policy、test strategy、known hotspot、decision を記録する
- local evidence artifact が作られる可能性がある場合だけ .audit/ を .gitignore に追加する
- personal vault path、private path、credential、MCP endpoint、auth state、browser profile、machine-specific trust setting をコミットしない

このプロジェクトが TS/JS-heavy で、私が Lumin Repo Lens の使用を承認した場合だけ evidence tool として使ってください:
- structural claim には evidence が必要
- absence claim には scan range が必要
- 証拠が部分的な場合は "not observed in this scan range" と言う
- pre-write intent は names、shapes、files、dependencies、plannedTypeEscapes を使う
- post-write machine evidence は type escapes、unexpected files、scan range、confidence changes に限定する
- duplicate helpers、dependency drift、public API drift、re-export drift は direct evidence が必要な manual review claim とする

振る舞いの変更には TDD を使ってください。変更後、このプロジェクトの実際の verification コマンドと post-write review を実行してください。変更ファイル、実行コマンド、検証結果、skipped/recommended optional tools、残リスクを報告してください。
```

## クイックスタート

最初にスコープを選ぶことが重要です。エージェントのセットアップは、新しいハーネス、プラグイン、provider、リポジトリ運用を一度に変えようとすると失敗しやすくなります。まず最小の有効範囲を適用し、検証してから広げます。

1. このマシンで今後開く Codex、Claude Code、OpenCode セッションに共通ルールを入れる場合は、[docs/global-guardrail-setup.md](docs/global-guardrail-setup.md) を使います。
2. 別のアプリケーションリポジトリに同じ規律を適用する場合は、そのリポジトリで [prompts/apply-vibe-coding-guardrails.md](prompts/apply-vibe-coding-guardrails.md) を貼り付けます。
3. すでに guardrail があるリポジトリで機能追加、バグ修正、リファクタリングを始める場合は、[prompts/start-with-vibe-coding-guardrails.md](prompts/start-with-vibe-coding-guardrails.md) を使います。
4. この bootstrap 自体を更新、再監査、改善する場合は、[prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md) を使います。

## 各プロンプトを使う場面

- `prompts/setup-codex-current-harness.md`: Codex 内で現在の Codex ハーネスに shared core だけを適用する場合。
- `prompts/setup-claude-current-harness.md`: Claude Code 内で Claude plugin と共有役割プロンプトを設定する場合。
- `prompts/setup-opencode-current-harness.md`: OpenCode 内で generated agents と native plugin wiring を適用する場合。
- `prompts/setup-shared-core.md`: 対象環境が曖昧で、shared prompt/skills レイヤーだけを適用するのが安全な場合。
- `prompts/apply-vibe-coding-guardrails.md`: アプリケーションリポジトリに構造マップ、edge-case-first テスト、依存境界チェック、project-local knowledge を追加する場合。
- `prompts/start-with-vibe-coding-guardrails.md`: すでに project map と guardrail workflow があるリポジトリで日常的な機能、バグ修正、リファクタリングを始める場合。
- `prompts/update-agent-bootstrap.md`: このリポジトリ自体の変更を pull、render、install、audit、文書化、レビューする場合。

## Guardrail が強制すること

この guardrail は、エージェントがセッションごとに構造記憶を失い、重複 helper や隠れた結合を増やす問題を抑えるためのものです。

- Pre-write lens: 編集前に module boundary、dependency direction、public API、helper、type、shape、re-export、test、error boundary、hotspot を確認します。
- TDD write gate: 空入力、null/missing、境界値、失敗経路、side effect、必要な並行性ケースを先にテストし、期待通り失敗することを確認してから実装します。
- 結合度の制御: 隠れ import、初期化順序契約、重複 shape、放置された barrel/re-export、fan-in/fan-out hotspot を避けます。
- エラー規律: エラーを黙って握りつぶさず、文書化された要件でない fallback を追加せず、エラー処理は明示的な境界に置きます。
- テスト規律: 文字列や関数名ではなく振る舞いと side effect を検証し、mock は外部境界に限定します。
- プライバシー境界: 個人 vault パス、private project path、credential、MCP endpoint、auth state、browser profile、machine-specific trust setting をコミットしません。

## 任意ツールとインストールポリシー

任意ツールは workflow を支える補助であり、workflow そのものではありません。

- Obsidian は、リポジトリ構造が大きく毎回再発見するコストが高い場合に、private project wiki として有用です。
- Lumin Repo Lens は、TS/JS リポジトリで AST ベースの証拠により duplicate helper、hidden coupling、re-export drift、fan-in/fan-out hotspot を探す場合に有用です。
- Dependency lint、cycle detection、strict type checks、complexity limits、file/function size limits は強力ですが、実際の tooling 変更です。

言及されているだけの理由で任意ツールをインストールしません。まず現在の環境を inventory し、そのツールが required/recommended/optional/skipped のどれかを説明し、インストール前に承認を取り、package name または official source を検証し、リポジトリには project-safe usage guidance だけを残します。

## このリポジトリの保守

この bootstrap を変更する前に、[docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md) を repo-local map として読みます。

- 共有動作ルールは `AGENTS.md` と `agents/*.md` で変更します。
- 役割 metadata は `shared/agent-metadata.json` で変更します。
- Codex のインストール動作は `.codex/install.py` で変更します。
- OpenCode のインストール動作は `.opencode/install.py` で変更します。
- Claude plugin の render 動作は `scripts/render_claude_plugin.py` で変更します。
- shared prompt または metadata を変更した場合は、`python3 scripts/render_claude_plugin.py --partner-name "<Name>"` で Claude plugin output を再生成します。
- `python3 -m unittest discover -s tests -p 'test_*.py'` と `python3 scripts/audit_agent_stack.py` で検証します。

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
- この bootstrap の更新/再監査: [prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md)

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

詳細なプロジェクト構造マップ、更新フロー、source-of-truth 境界、生成物ポリシーは [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md) を参照してください。

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
