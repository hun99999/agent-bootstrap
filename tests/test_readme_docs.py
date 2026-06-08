import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LANGUAGE_SWITCHER = "[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)"


class ReadmeDocsTests(unittest.TestCase):
    def test_main_readme_has_language_switcher_and_value_props(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(LANGUAGE_SWITCHER, readme)
        self.assertIn("Codex, Claude Code, and OpenCode", readme)
        self.assertIn("superpowers", readme)
        self.assertIn("subagents", readme)
        self.assertIn("token-efficient", readme)

    def test_translated_readmes_exist_with_language_switcher(self) -> None:
        for relative in ("README.ko.md", "README.ja.md", "README.zh-CN.md"):
            contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(LANGUAGE_SWITCHER, contents)

    def test_repo_metadata_doc_exists(self) -> None:
        metadata = (REPO_ROOT / "docs" / "repo-metadata.md").read_text(encoding="utf-8")

        self.assertIn("Repository description", metadata)
        self.assertIn("Topics", metadata)
        self.assertIn("Social preview", metadata)

    def test_codex_superpowers_docs_explain_plugin_and_manual_modes(self) -> None:
        expected_phrases = (
            "Codex App curated Superpowers plugin",
            "manual ~/.codex/superpowers fallback",
            "duplicate skill entries",
        )

        for relative in ("README.md", "docs/README.codex.md", ".codex/INSTALL.md"):
            contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
            for phrase in expected_phrases:
                self.assertIn(phrase, contents)

    def test_docs_explain_agent_stack_audit_command(self) -> None:
        for relative in (
            "README.md",
            "README.ko.md",
            "README.ja.md",
            "README.zh-CN.md",
            "docs/README.codex.md",
            "docs/README.claude.md",
            "docs/README.opencode.md",
        ):
            contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("scripts/audit_agent_stack.py", contents)

    def test_translated_readmes_mention_duplicate_superpowers_discovery(self) -> None:
        expected_phrases = {
            "README.ko.md": "중복 skill 항목",
            "README.ja.md": "重複する skill 項目",
            "README.zh-CN.md": "重复的 skill 条目",
        }

        for relative, phrase in expected_phrases.items():
            contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(phrase, contents)

    def test_readme_links_vibe_coding_guardrails(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/vibe-coding-guardrails.md", readme)
        self.assertIn("docs/global-guardrail-setup.md", readme)
        self.assertIn("prompts/apply-vibe-coding-guardrails.md", readme)
        self.assertIn("prompts/start-with-vibe-coding-guardrails.md", readme)

    def test_readme_explains_guardrail_workflows_near_the_top(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        introduction = readme[:7000]

        expected_phrases = (
            "What You Can Ask An Agent To Do",
            "Install global defaults",
            "Apply guardrails to a project",
            "Start feature work inside a guarded project",
            "Update this bootstrap after repository changes",
            "Optional tooling is decision-based",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, introduction)

    def test_all_readmes_include_public_target_repo_claude_prompt(self) -> None:
        expectations = {
            "README.md": (
                "Target Repository Claude Code Prompt",
                "Reference repository:",
                "https://github.com/hun99999/agent-bootstrap",
                "Apply agent-bootstrap vibe-coding guardrails to this project.",
                "git status --short --branch",
                "optional tool inventory",
                "Obsidian",
                "Lumin Repo Lens",
                "scan range",
                "Do not install optional tools automatically",
            ),
            "README.ko.md": (
                "대상 프로젝트용 Claude Code 프롬프트",
                "참조 레포:",
                "https://github.com/hun99999/agent-bootstrap",
                "이 프로젝트에 agent-bootstrap 기반 vibe-coding guardrails를 적용해줘.",
                "git status --short --branch",
                "optional tool inventory",
                "Obsidian",
                "Lumin Repo Lens",
                "scan range",
                "선택 도구를 자동 설치하지 마라",
            ),
            "README.ja.md": (
                "対象プロジェクト用 Claude Code プロンプト",
                "参照リポジトリ:",
                "https://github.com/hun99999/agent-bootstrap",
                "このプロジェクトに agent-bootstrap ベースの vibe-coding guardrails を適用してください。",
                "git status --short --branch",
                "optional tool inventory",
                "Obsidian",
                "Lumin Repo Lens",
                "scan range",
                "任意ツールを自動インストールしない",
            ),
            "README.zh-CN.md": (
                "目标项目 Claude Code 提示词",
                "参考仓库:",
                "https://github.com/hun99999/agent-bootstrap",
                "请把 agent-bootstrap 的 vibe-coding guardrails 应用到这个项目。",
                "git status --short --branch",
                "optional tool inventory",
                "Obsidian",
                "Lumin Repo Lens",
                "scan range",
                "不要自动安装可选工具",
            ),
        }

        for relative, phrases in expectations.items():
            with self.subTest(relative=relative):
                readme = (REPO_ROOT / relative).read_text(encoding="utf-8")
                for phrase in phrases:
                    self.assertIn(phrase, readme)
                self.assertNotIn("/" + "Users/hooooonje/codex-dotfiles", readme)

    def test_korean_readme_explains_guardrail_workflows_near_the_top(self) -> None:
        readme = (REPO_ROOT / "README.ko.md").read_text(encoding="utf-8")
        introduction = readme[:7000]

        expected_phrases = (
            "에이전트에게 맡길 수 있는 일",
            "전역 기본값 설치",
            "프로젝트에 guardrail 적용",
            "guardrail이 있는 프로젝트에서 기능 작업 시작",
            "이 bootstrap 업데이트/재점검",
            "선택 도구는 판단 후 사용",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, introduction)

    def test_readme_links_repo_structure_and_update_prompt(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/agent-bootstrap-structure.md", readme)
        self.assertIn("prompts/update-agent-bootstrap.md", readme)

    def test_korean_readme_links_repo_structure_and_update_prompt(self) -> None:
        readme = (REPO_ROOT / "README.ko.md").read_text(encoding="utf-8")

        self.assertIn("docs/agent-bootstrap-structure.md", readme)
        self.assertIn("prompts/update-agent-bootstrap.md", readme)

    def test_translated_readmes_link_repo_structure_and_update_prompt(self) -> None:
        for relative in ("README.ko.md", "README.ja.md", "README.zh-CN.md"):
            with self.subTest(relative=relative):
                readme = (REPO_ROOT / relative).read_text(encoding="utf-8")

                self.assertIn("docs/agent-bootstrap-structure.md", readme)
                self.assertIn("prompts/update-agent-bootstrap.md", readme)

    def test_all_readmes_put_master_prompt_near_the_top(self) -> None:
        expectations = {
            "README.md": (
                "## Master Prompt",
                "Paste this into Codex, Claude Code, OpenCode, or another coding agent",
                "First read AGENTS.md",
                "git status --short --branch",
                "Choose the smallest valid scope",
                "Do not install optional tools just because they are mentioned",
                "run post-write review",
                "verification results",
                "Bootstrap a process-first AI coding environment",
            ),
            "README.ko.md": (
                "## 마스터 프롬프트",
                "아래를 Codex, Claude Code, OpenCode 또는 다른 코딩 에이전트에게 그대로 붙여넣습니다",
                "먼저 AGENTS.md",
                "git status --short --branch",
                "가장 작은 유효 범위",
                "언급됐다는 이유만으로 선택 도구를 설치하지 마십시오",
                "post-write review",
                "검증 결과",
                "Codex, Claude Code, OpenCode를 위한",
            ),
            "README.ja.md": (
                "## マスタープロンプト",
                "次を Codex、Claude Code、OpenCode、または別のコーディングエージェントにそのまま貼り付けます",
                "まず AGENTS.md",
                "git status --short --branch",
                "最小の有効スコープ",
                "言及されているだけの理由で任意ツールをインストールしないでください",
                "post-write review",
                "検証結果",
                "Codex、Claude Code、OpenCode向け",
            ),
            "README.zh-CN.md": (
                "## 主提示词",
                "把下面内容原样粘贴给 Codex、Claude Code、OpenCode 或其他编码代理",
                "先阅读 AGENTS.md",
                "git status --short --branch",
                "最小有效范围",
                "不要仅仅因为文档提到某个可选工具就安装它",
                "post-write review",
                "验证结果",
                "面向 Codex、Claude Code 和 OpenCode",
            ),
        }

        for relative, phrases in expectations.items():
            with self.subTest(relative=relative):
                readme = (REPO_ROOT / relative).read_text(encoding="utf-8")
                for phrase in phrases:
                    self.assertIn(phrase, readme)
                self.assertLess(readme.index(phrases[0]), readme.index(phrases[-1]))

    def test_all_readmes_explain_detailed_guardrail_workflow(self) -> None:
        expectations = {
            "README.md": (
                "Quick Start",
                "Choose the scope first",
                "When To Use Each Prompt",
                "What The Guardrails Enforce",
                "Optional Tools And Installation Policy",
                "Maintaining This Repository",
                "Do not install optional tools just because they are mentioned",
            ),
            "README.ko.md": (
                "빠른 시작",
                "먼저 범위를 고릅니다",
                "프롬프트별 사용 시점",
                "Guardrail이 강제하는 것",
                "선택 도구와 설치 정책",
                "이 레포 유지보수",
                "언급됐다는 이유만으로 선택 도구를 설치하지 않습니다",
            ),
            "README.ja.md": (
                "クイックスタート",
                "最初にスコープを選ぶ",
                "各プロンプトを使う場面",
                "Guardrail が強制すること",
                "任意ツールとインストールポリシー",
                "このリポジトリの保守",
                "言及されているだけの理由で任意ツールをインストールしません",
            ),
            "README.zh-CN.md": (
                "快速开始",
                "先选择范围",
                "每个提示词的使用场景",
                "Guardrail 强制的内容",
                "可选工具和安装策略",
                "维护这个仓库",
                "不要仅仅因为文档提到某个可选工具就安装它",
            ),
        }

        for relative, phrases in expectations.items():
            with self.subTest(relative=relative):
                readme = (REPO_ROOT / relative).read_text(encoding="utf-8")
                for phrase in phrases:
                    self.assertIn(phrase, readme)

    def test_agent_bootstrap_structure_doc_covers_boundaries_and_update_flow(self) -> None:
        structure = (REPO_ROOT / "docs" / "agent-bootstrap-structure.md").read_text(
            encoding="utf-8"
        )

        expected_phrases = (
            "Shared Core",
            "Harness Adapters",
            "Generated Artifacts",
            "Source Of Truth",
            "Do not edit generated Claude plugin agents by hand",
            "Update Flow",
            "python3 scripts/render_claude_plugin.py --partner-name",
            "python3 -m unittest discover -s tests -p 'test_*.py'",
            "python3 scripts/audit_agent_stack.py",
            "No private paths",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, structure)

    def test_update_prompt_covers_pull_render_install_and_review_loop(self) -> None:
        prompt = (REPO_ROOT / "prompts" / "update-agent-bootstrap.md").read_text(
            encoding="utf-8"
        )

        expected_phrases = (
            "Update agent-bootstrap from the current repository state",
            "git status",
            "git pull --ff-only",
            "docs/agent-bootstrap-structure.md",
            "pre-write lens",
            "python3 scripts/render_claude_plugin.py --partner-name",
            "bash .codex/install.sh --partner-name",
            "python3 scripts/audit_agent_stack.py",
            "post-write review",
            "do not commit private paths",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, prompt)

    def test_harness_docs_explain_global_guardrail_install_scope(self) -> None:
        expectations = {
            "docs/README.codex.md": ("~/.codex", "user-level defaults", "new Codex sessions"),
            "docs/README.claude.md": (
                "Claude Code plugin",
                "user-level defaults",
                "new Claude Code sessions",
            ),
            "docs/README.opencode.md": (
                "~/.config/opencode",
                "user-level defaults",
                "new OpenCode sessions",
            ),
        }

        for relative, phrases in expectations.items():
            contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                for phrase in phrases:
                    self.assertIn(phrase, contents)


if __name__ == "__main__":
    unittest.main()
