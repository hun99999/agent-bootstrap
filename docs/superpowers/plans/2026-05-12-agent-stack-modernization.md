# Agent Stack Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update Hun's local agent tooling and repository bootstrap artifacts for current Codex, Claude Code, and Superpowers behavior while preserving safe local state handling.

**Architecture:** Treat local tool updates and repository template updates as separate but related workstreams. Repository changes are test-first and target active public surfaces: Codex config templates, Codex installer, Claude plugin generator, prompt corpus, README/install docs, and repo metadata docs. Codex `[agents.<name>]` migration is gated by live runtime validation; if the updated runtime cannot prove the new shape works, stop before adding a compatibility bridge.

**Tech Stack:** Python 3.9 `unittest`, shell/git/npm, Codex CLI, Claude Code CLI, JSON files, TOML-like config text inspected by focused tests, Markdown docs.

---

## File Structure

- Modify: `docs/superpowers/specs/2026-05-12-agent-stack-modernization-design.md`
- Create: `docs/superpowers/plans/2026-05-12-agent-stack-modernization.md`
- Create: `tests/test_codex_config.py`
- Create: `tests/test_prompt_corpus_policy.py`
- Modify: `tests/test_claude_plugin.py`
- Modify: `tests/test_install.py`
- Modify: `tests/test_readme_docs.py`
- Modify: `.codex/templates/config.toml`
- Modify: `codex-home/config.toml`
- Modify: `.codex/install.py`
- Modify: `.codex/INSTALL.md`
- Modify: `docs/README.codex.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `README.ja.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/repo-metadata.md`
- Modify: `AGENTS.md`
- Modify: `codex-home/AGENTS.md`
- Modify: `agents/eng-lead.md`
- Modify: `agents/worker.md`
- Modify: `agents/debugger.md`
- Modify: matching files under `codex-home/agents/`
- Modify: `shared/agent-metadata.json`
- Modify: `scripts/render_claude_plugin.py`
- Regenerate: `.claude-plugin/marketplace.json`
- Regenerate: `plugins/process-first-agents/.claude-plugin/plugin.json`
- Regenerate: `plugins/process-first-agents/settings.json`
- Regenerate: `plugins/process-first-agents/agents/*.md`

---

### Task 1: Local Tool Baseline And Safe Update

**Files:**
- No repository file edits.

- [ ] **Step 1: Record current repository and tool state**

Run:

```bash
git status --short --branch
codex --version
claude --version
npm view @openai/codex version
npm view @anthropic-ai/claude-code version
git -C ~/.codex/superpowers status --short
git -C ~/.codex/superpowers remote get-url origin
git -C ~/.codex/superpowers rev-parse HEAD
git ls-remote https://github.com/obra/superpowers.git HEAD refs/heads/main refs/tags/v5.1.0
```

Expected:

```text
git status shows branch codex/update-agent-stack with no unexpected working tree changes
codex local version is older than npm latest
claude local version is older than npm latest
~/.codex/superpowers status output is empty
origin remote is https://github.com/obra/superpowers.git
```

If `git -C ~/.codex/superpowers status --short` prints any path, stop and report the dirty checkout to Hun.

- [ ] **Step 2: Update global npm tools**

Run:

```bash
npm install -g @openai/codex@latest @anthropic-ai/claude-code@latest
```

Expected:

```text
npm exits 0
```

- [ ] **Step 3: Verify global npm tools**

Run:

```bash
codex --version
claude --version
```

Expected:

```text
codex reports 0.130.0 or newer
claude reports 2.1.139 or newer
```

- [ ] **Step 4: Fast-forward manual Superpowers checkout**

Run:

```bash
git -C ~/.codex/superpowers fetch origin
git -C ~/.codex/superpowers remote set-head origin -a
git -C ~/.codex/superpowers symbolic-ref refs/remotes/origin/HEAD --short
git -C ~/.codex/superpowers merge --ff-only origin/main
git -C ~/.codex/superpowers rev-parse HEAD
```

Expected:

```text
origin/HEAD resolves to origin/main
merge exits 0
HEAD equals the current upstream main commit
```

If `merge --ff-only` fails, stop and report that local Superpowers cannot fast-forward.

- [ ] **Step 5: Commit**

No commit for this task. It changes local global tool state, not repository files.

---

### Task 2: Codex Config Policy Tests

**Files:**
- Create: `tests/test_codex_config.py`

- [ ] **Step 1: Write the failing test file**

Create `tests/test_codex_config.py` with:

```python
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATHS = (
    REPO_ROOT / ".codex" / "templates" / "config.toml",
    REPO_ROOT / "codex-home" / "config.toml",
)


def read_config(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def top_level_text(config: str) -> str:
    lines = []
    for line in config.splitlines():
        if line.startswith("["):
            break
        lines.append(line)
    return "\n".join(lines)


def previous_profile_text(config: str) -> str:
    match = re.search(r"(?ms)^\\[profiles\\.previous\\]\\n(?P<body>.*?)(?=^\\[|\\Z)", config)
    if match is None:
        return ""
    return match.group("body")


class CodexConfigPolicyTests(unittest.TestCase):
    def test_template_and_snapshot_configs_match(self) -> None:
        template = read_config(CONFIG_PATHS[0])
        snapshot = read_config(CONFIG_PATHS[1])

        self.assertEqual(snapshot, template)

    def test_default_model_policy_uses_latest_model(self) -> None:
        for path in CONFIG_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                config = read_config(path)
                top_level = top_level_text(config)

                self.assertIn('model = "gpt-5.5"', top_level)
                self.assertIn('model_reasoning_effort = "xhigh"', top_level)
                self.assertIn('model_reasoning_summary = "detailed"', top_level)
                self.assertIn('model_verbosity = "high"', top_level)
                self.assertIn('plan_mode_reasoning_effort = "xhigh"', top_level)

    def test_previous_profile_is_only_gpt_5_4_default_fallback(self) -> None:
        for path in CONFIG_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                config = read_config(path)
                previous = previous_profile_text(config)

                self.assertIn('model = "gpt-5.4"', previous)
                self.assertEqual(config.count('model = "gpt-5.4"'), 1)

    def test_legacy_custom_agents_do_not_pin_previous_model(self) -> None:
        for path in CONFIG_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                config = read_config(path)
                self.assertNotIn('[[custom_agent]]\\nagent_type = "eng-lead"\\n', config)
                self.assertNotIn('model = "gpt-5.4"\\nmodel_reasoning_effort', config)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_codex_config
```

Expected:

```text
FAIL: test_default_model_policy_uses_latest_model
FAIL: test_previous_profile_is_only_gpt_5_4_default_fallback
```

- [ ] **Step 3: Commit failing test**

Run:

```bash
git status --short
git add tests/test_codex_config.py
git commit -m "test: capture codex model policy"
```

Expected:

```text
commit succeeds
```

---

### Task 3: Codex Config Implementation And Runtime Gate

**Files:**
- Modify: `.codex/templates/config.toml`
- Modify: `codex-home/config.toml`

- [ ] **Step 1: Check whether Codex has a documented local validation command**

Run:

```bash
codex debug --help
codex debug prompt-input --help
```

Expected:

```text
The available debug commands are shown.
```

Use only commands shown by this help output. Do not invent a config validation command.

- [ ] **Step 2: Decide config shape**

If a live validation path for `[agents.<name>]` and role `config_file` can be proven, implement the new shape. The initial target shape is:

```toml
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
model_reasoning_summary = "detailed"
model_verbosity = "high"
plan_mode_reasoning_effort = "xhigh"
personality = "pragmatic"

[profiles.previous]
model = "gpt-5.4"

[agents.eng-lead]
description = "Primary lead for day-to-day work. Stay local by default and delegate only when it creates clear leverage."
config_file = "agents/eng-lead.toml"
```

If a live validation path cannot be proven, stop and ask Hun before retaining legacy `[[custom_agent]]` or adding any compatibility bridge.

- [ ] **Step 3: Implement the selected config shape**

For the legacy shape approved by Hun, the minimum allowed implementation is:

```toml
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
model_reasoning_summary = "detailed"
model_verbosity = "high"
plan_mode_reasoning_effort = "xhigh"
personality = "pragmatic"

[profiles.previous]
model = "gpt-5.4"
```

and every default `[[custom_agent]]` model pin must be either removed for inheritance or changed to:

```toml
model = "gpt-5.5"
```

Do not leave `model = "gpt-5.4"` outside `[profiles.previous]`.

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_codex_config
```

Expected:

```text
OK
```

- [ ] **Step 5: Commit**

Run:

```bash
git status --short
git add .codex/templates/config.toml codex-home/config.toml tests/test_codex_config.py
git commit -m "feat: update codex model policy"
```

Expected:

```text
commit succeeds
```

---

### Task 4: Safe Superpowers Installer Tests

**Files:**
- Modify: `tests/test_install.py`

- [ ] **Step 1: Add failing tests for destructive-update protection**

Append these methods to `InstallScriptTests` in `tests/test_install.py`:

```python
    def test_install_refuses_dirty_superpowers_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / ".codex"
            agents_home = root / ".agents"
            remote, working = self.create_superpowers_remote(root)
            self.commit_superpowers_change(
                working,
                "skills/example/SKILL.md",
                "version 1\n",
                "Add initial skill",
            )

            first_result = self.run_installer(
                "--partner-name",
                "Hun",
                "--codex-home",
                str(codex_home),
                "--agents-home",
                str(agents_home),
                "--superpowers-remote",
                str(remote),
            )
            self.assertEqual(first_result.returncode, 0, msg=first_result.stderr)

            dirty_file = codex_home / "superpowers" / "skills" / "example" / "SKILL.md"
            dirty_file.write_text("local edit\n", encoding="utf-8")

            second_result = self.run_installer(
                "--partner-name",
                "Hun",
                "--codex-home",
                str(codex_home),
                "--agents-home",
                str(agents_home),
                "--superpowers-remote",
                str(remote),
            )

            self.assertNotEqual(second_result.returncode, 0)
            self.assertIn("dirty superpowers checkout", second_result.stderr)
            self.assertEqual(dirty_file.read_text(encoding="utf-8"), "local edit\n")

    def test_install_refuses_to_replace_existing_superpowers_skills_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / ".codex"
            agents_home = root / ".agents"
            remote, working = self.create_superpowers_remote(root)
            self.commit_superpowers_change(
                working,
                "skills/example/SKILL.md",
                "version 1\n",
                "Add initial skill",
            )
            existing = agents_home / "skills" / "superpowers"
            existing.mkdir(parents=True)
            (existing / "owned.txt").write_text("user owned\n", encoding="utf-8")

            result = self.run_installer(
                "--partner-name",
                "Hun",
                "--codex-home",
                str(codex_home),
                "--agents-home",
                str(agents_home),
                "--superpowers-remote",
                str(remote),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to replace existing superpowers skills path", result.stderr)
            self.assertEqual((existing / "owned.txt").read_text(encoding="utf-8"), "user owned\n")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest tests.test_install.InstallScriptTests.test_install_refuses_dirty_superpowers_checkout tests.test_install.InstallScriptTests.test_install_refuses_to_replace_existing_superpowers_skills_path
```

Expected:

```text
FAIL
```

- [ ] **Step 3: Commit failing tests**

Run:

```bash
git status --short
git add tests/test_install.py
git commit -m "test: capture safe superpowers install behavior"
```

Expected:

```text
commit succeeds
```

---

### Task 5: Safe Superpowers Installer Implementation

**Files:**
- Modify: `.codex/install.py`
- Modify: `tests/test_install.py`

- [ ] **Step 1: Add mode argument**

In `parse_args()`, add:

```python
    parser.add_argument(
        "--superpowers-mode",
        choices=("manual", "skip"),
        default="manual",
        help="Control manual Superpowers checkout and symlink installation. Defaults to manual.",
    )
```

- [ ] **Step 2: Add dirty checkout guard**

Add:

```python
def git_status_short(cwd: Path) -> str:
    return git_stdout("status", "--short", cwd=cwd)


def verify_superpowers_checkout_clean(superpowers_root: Path) -> None:
    status = git_status_short(superpowers_root).strip()
    if status:
        raise RuntimeError(
            f"dirty superpowers checkout: {superpowers_root}; commit, stash, or clean it before running install"
        )
```

- [ ] **Step 3: Replace force-reset sync with fast-forward sync**

Replace the existing checkout/reset section in `sync_superpowers_repo()` with:

```python
        verify_superpowers_checkout_clean(superpowers_root)
        git_stdout("fetch", "origin", cwd=superpowers_root)
        git_stdout("remote", "set-head", "origin", "-a", cwd=superpowers_root)
        remote_head = git_stdout(
            "symbolic-ref",
            "refs/remotes/origin/HEAD",
            "--short",
            cwd=superpowers_root,
        ).strip()
        branch_name = remote_head.split("/", maxsplit=1)[1]
        current_branch = git_stdout("branch", "--show-current", cwd=superpowers_root).strip()
        if current_branch != branch_name:
            raise RuntimeError(
                f"superpowers checkout is on branch {current_branch}, expected {branch_name}; refusing to switch branches"
            )
        git_stdout("merge", "--ff-only", f"origin/{branch_name}", cwd=superpowers_root)
```

- [ ] **Step 4: Refuse to replace user-managed skill paths**

Replace `ensure_superpowers_symlink()` body with:

```python
def ensure_superpowers_symlink(codex_home: Path, agents_home: Path) -> None:
    link_path = agents_home / "skills" / "superpowers"
    target = codex_home / "superpowers" / "skills"
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if link_path.is_symlink() and link_path.resolve() == target.resolve():
        return
    if link_path.exists() or link_path.is_symlink():
        raise RuntimeError(f"refusing to replace existing superpowers skills path: {link_path}")
    link_path.symlink_to(target)
```

- [ ] **Step 5: Respect skip mode**

In `main()`, wrap manual sync and symlink work:

```python
    superpowers_backup_root = None
    superpowers_commit = None
    if args.superpowers_mode == "manual":
        superpowers_backup_root, superpowers_commit = sync_superpowers_repo(
            target_root,
            args.superpowers_remote,
        )
        ensure_superpowers_symlink(target_root, agents_home)
```

Adjust verification and output so `verify_superpowers_symlink()` only runs in manual mode and skip mode prints:

```python
    print("Superpowers: skipped manual checkout and symlink")
```

- [ ] **Step 6: Run focused tests**

Run:

```bash
python3 -m unittest tests.test_install
```

Expected:

```text
OK
```

- [ ] **Step 7: Commit**

Run:

```bash
git status --short
git add .codex/install.py tests/test_install.py
git commit -m "fix: make superpowers install updates safe"
```

Expected:

```text
commit succeeds
```

---

### Task 6: Claude Plugin Policy Tests

**Files:**
- Modify: `tests/test_claude_plugin.py`

- [ ] **Step 1: Add frontmatter parser and renderer import helper**

Add near the top of `tests/test_claude_plugin.py`:

```python
import importlib.util
import tempfile


def parse_frontmatter(markdown: str) -> dict[str, object]:
    self_closing = markdown.startswith("---\n")
    if not self_closing:
        raise AssertionError("missing frontmatter start")
    _, body = markdown.split("---\n", 1)
    frontmatter_text, _ = body.split("\n---\n", 1)
    parsed: dict[str, object] = {}
    current_list_key = None
    for line in frontmatter_text.splitlines():
        if line.startswith("  - ") and current_list_key:
            parsed[current_list_key].append(line.removeprefix("  - "))
            continue
        current_list_key = None
        if line.endswith(":"):
            key = line[:-1]
            parsed[key] = []
            current_list_key = key
            continue
        key, value = line.split(": ", 1)
        parsed[key] = value
    return parsed


def load_renderer_module():
    script_path = REPO_ROOT / "scripts" / "render_claude_plugin.py"
    spec = importlib.util.spec_from_file_location("render_claude_plugin", script_path)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load render_claude_plugin.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

- [ ] **Step 2: Add failing manifest identity tests**

Add:

```python
    def test_plugin_manifest_uses_hun_identity(self) -> None:
        manifest = json.loads(PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8"))

        self.assertEqual(manifest["author"], {
            "name": "Hun",
            "email": "48903443+hun99999@users.noreply.github.com",
        })
        self.assertEqual(manifest["repository"], "https://github.com/hun99999/agent-bootstrap")

    def test_renderer_outputs_hun_identity(self) -> None:
        renderer = load_renderer_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_root = Path(tmpdir) / "process-first-agents"
            renderer.render_plugin_bundle(REPO_ROOT, plugin_root, "Hun")
            manifest = json.loads((plugin_root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["author"], {
            "name": "Hun",
            "email": "48903443+hun99999@users.noreply.github.com",
        })
        self.assertEqual(manifest["repository"], "https://github.com/hun99999/agent-bootstrap")
```

- [ ] **Step 3: Add failing frontmatter policy test**

Add:

```python
    def test_generated_agents_have_claude_frontmatter_policy(self) -> None:
        read_only_agents = {"planner", "researcher", "debugger", "reviewer", "verifier", "release-manager"}
        isolated_agents = {
            "worker",
            "frontend-engineer",
            "backend-engineer",
            "platform-engineer",
            "data-engineer",
            "security-engineer",
            "integrations-engineer",
            "performance-engineer",
            "skill-author",
        }

        for path in sorted((PLUGIN_ROOT / "agents").glob("*.md")):
            with self.subTest(agent=path.stem):
                frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
                self.assertEqual(frontmatter["model"], "inherit")
                self.assertNotIn("hooks", frontmatter)
                self.assertNotIn("mcpServers", frontmatter)
                self.assertNotIn("permissionMode", frontmatter)
                if path.stem in read_only_agents:
                    self.assertEqual(frontmatter["disallowedTools"], ["Write", "Edit"])
                if path.stem in isolated_agents:
                    self.assertEqual(frontmatter["isolation"], "worktree")
```

- [ ] **Step 4: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_claude_plugin
```

Expected:

```text
FAIL
```

- [ ] **Step 5: Commit failing tests**

Run:

```bash
git status --short
git add tests/test_claude_plugin.py
git commit -m "test: capture claude plugin policy"
```

Expected:

```text
commit succeeds
```

---

### Task 7: Claude Plugin Generator Implementation

**Files:**
- Modify: `shared/agent-metadata.json`
- Modify: `scripts/render_claude_plugin.py`
- Regenerate: `.claude-plugin/marketplace.json`
- Regenerate: `plugins/process-first-agents/.claude-plugin/plugin.json`
- Regenerate: `plugins/process-first-agents/settings.json`
- Regenerate: `plugins/process-first-agents/agents/*.md`

- [ ] **Step 1: Add Claude metadata to shared agent metadata**

For each read-only agent in `shared/agent-metadata.json`, add:

```json
"claude": {
  "model": "inherit",
  "disallowedTools": ["Write", "Edit"]
}
```

For `eng-lead`, add:

```json
"claude": {
  "model": "inherit"
}
```

For each write-capable specialist agent except `eng-lead`, add:

```json
"claude": {
  "model": "inherit",
  "isolation": "worktree"
}
```

- [ ] **Step 2: Add plugin metadata constants**

In `scripts/render_claude_plugin.py`, add after `METADATA_PATH`:

```python
PLUGIN_AUTHOR = {"name": "Hun", "email": "48903443+hun99999@users.noreply.github.com"}
PLUGIN_REPOSITORY = "https://github.com/hun99999/agent-bootstrap"
```

- [ ] **Step 3: Add YAML frontmatter serialization**

Add:

```python
def format_frontmatter_value(key: str, value: object) -> list[str]:
    if isinstance(value, list):
        lines = [f"{key}:"]
        lines.extend(f"  - {item}" for item in value)
        return lines
    return [f"{key}: {value}"]
```

Replace the current `frontmatter = "\n".join([...])` block with:

```python
    claude_metadata = metadata.get("claude", {})
    frontmatter_lines = [
        "---",
        f"name: {agent_source.stem}",
        f"description: {metadata['description']}",
    ]
    for key in ("model", "disallowedTools", "isolation"):
        if key in claude_metadata:
            frontmatter_lines.extend(format_frontmatter_value(key, claude_metadata[key]))
    frontmatter_lines.append("---")
    frontmatter = "\n".join(frontmatter_lines)
```

- [ ] **Step 4: Update manifest identity**

Replace the `author` and `repository` entries in `manifest` with:

```python
        "author": PLUGIN_AUTHOR,
        "repository": PLUGIN_REPOSITORY,
```

- [ ] **Step 5: Regenerate plugin**

Run:

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
```

Expected:

```text
Rendered Claude plugin bundle at /Users/hooooonje/codex-dotfiles/plugins/process-first-agents
```

- [ ] **Step 6: Run focused tests**

Run:

```bash
python3 -m unittest tests.test_claude_plugin
```

Expected:

```text
OK
```

- [ ] **Step 7: Commit**

Run:

```bash
git status --short
git add shared/agent-metadata.json scripts/render_claude_plugin.py .claude-plugin/marketplace.json plugins/process-first-agents/.claude-plugin/plugin.json plugins/process-first-agents/settings.json plugins/process-first-agents/agents
git commit -m "feat: modernize claude plugin metadata"
```

Expected:

```text
commit succeeds
```

---

### Task 8: Prompt Corpus Policy Tests

**Files:**
- Create: `tests/test_prompt_corpus_policy.py`

- [ ] **Step 1: Write failing prompt policy tests**

Create `tests/test_prompt_corpus_policy.py` with:

```python
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PromptCorpusPolicyTests(unittest.TestCase):
    def test_root_prompt_scopes_clarification_and_host_capabilities(self) -> None:
        prompt = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertNotIn("YOU MUST ALWAYS STOP and ask for clarification", prompt)
        self.assertIn("Ask for clarification only when ambiguity would change scope, safety, architecture, destructive actions, or correctness", prompt)
        self.assertIn("current host/runtime provides the capability", prompt)
        self.assertIn("Use the host's journal or memory mechanism when available", prompt)
        self.assertNotIn("The last assistant was a sycophant", prompt)

    def test_codex_home_prompt_matches_root_prompt(self) -> None:
        self.assertEqual(
            (REPO_ROOT / "codex-home" / "AGENTS.md").read_text(encoding="utf-8"),
            (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8"),
        )

    def test_codex_home_agents_match_shared_agents(self) -> None:
        for source in sorted((REPO_ROOT / "agents").glob("*.md")):
            target = REPO_ROOT / "codex-home" / "agents" / source.name
            with self.subTest(agent=source.name):
                self.assertEqual(target.read_text(encoding="utf-8"), source.read_text(encoding="utf-8"))

    def test_delegation_roles_are_host_capability_gated(self) -> None:
        for relative in ("agents/eng-lead.md", "agents/worker.md"):
            with self.subTest(path=relative):
                text = (REPO_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("current host/runtime provides", text)

    def test_debugger_can_continue_when_fix_requested(self) -> None:
        text = (REPO_ROOT / "agents" / "debugger.md").read_text(encoding="utf-8")

        self.assertIn("If Hun asked you to fix the issue", text)
        self.assertIn("continue into TDD implementation", text)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest tests.test_prompt_corpus_policy
```

Expected:

```text
FAIL
```

- [ ] **Step 3: Commit failing tests**

Run:

```bash
git status --short
git add tests/test_prompt_corpus_policy.py
git commit -m "test: capture prompt corpus policy"
```

Expected:

```text
commit succeeds
```

---

### Task 9: Prompt Corpus Implementation

**Files:**
- Modify: `AGENTS.md`
- Modify: `codex-home/AGENTS.md`
- Modify: `agents/eng-lead.md`
- Modify: `agents/worker.md`
- Modify: `agents/debugger.md`
- Modify: matching files under `codex-home/agents/`
- Regenerate: `plugins/process-first-agents/agents/*.md`

- [ ] **Step 1: Update root prompt wording**

In `AGENTS.md`, replace the absolute clarification line with:

```markdown
- Ask for clarification only when ambiguity would change scope, safety, architecture, destructive actions, or correctness. Otherwise, state the assumption briefly and proceed.
```

Replace repeated anti-sycophancy wording with:

```markdown
- Do not use performative agreement or praise. Give direct technical judgment and push back when needed.
```

Replace journal wording with:

```markdown
- Use the host's journal or memory mechanism when available to record important facts and insights before they are lost.
- Search the host's journal or memory mechanism when trying to remember or recover prior context.
```

Replace subagent permission wording with:

```markdown
- You may use sub-agents or parallel agents for independent work without asking again each time when the current host/runtime provides the capability. This is a standing preference, not a requirement: use them when they create clear leverage, and stay local when they do not.
```

- [ ] **Step 2: Update role prompts**

In `agents/eng-lead.md`, add after the standing preference sentence:

```markdown
Use only delegation mechanisms the current host/runtime provides. If delegation is unavailable or restricted, stay local and say so.
```

In `agents/worker.md`, replace the delegation paragraph with:

```markdown
You may spawn sub-agents for independent work when {{PARTNER_NAME}}'s standing preference or the lead's direction allows it, the current host/runtime provides the capability, and the task can be split cleanly.
Do not delegate small, tightly coupled, or immediately blocking work. If delegation overhead is likely higher than execution overhead, stay local.
```

In `agents/debugger.md`, replace the post-root-cause handoff rule with:

```markdown
If {{PARTNER_NAME}} asked you to fix the issue and the current host permits edits, continue into TDD implementation after the cause is proven.
Otherwise, hand off to the assigned implementation agent.
```

- [ ] **Step 3: Sync prompt snapshots**

Run:

```bash
cp AGENTS.md codex-home/AGENTS.md
cp agents/eng-lead.md codex-home/agents/eng-lead.md
cp agents/worker.md codex-home/agents/worker.md
cp agents/debugger.md codex-home/agents/debugger.md
```

- [ ] **Step 4: Regenerate Claude plugin agents**

Run:

```bash
python3 scripts/render_claude_plugin.py --partner-name "Hun"
```

Expected:

```text
Rendered Claude plugin bundle at /Users/hooooonje/codex-dotfiles/plugins/process-first-agents
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
python3 -m unittest tests.test_prompt_corpus_policy tests.test_claude_plugin
```

Expected:

```text
OK
```

- [ ] **Step 6: Commit**

Run:

```bash
git status --short
git add AGENTS.md codex-home/AGENTS.md agents/eng-lead.md agents/worker.md agents/debugger.md codex-home/agents/eng-lead.md codex-home/agents/worker.md codex-home/agents/debugger.md plugins/process-first-agents/agents tests/test_prompt_corpus_policy.py
git commit -m "feat: clarify prompt corpus policy"
```

Expected:

```text
commit succeeds
```

---

### Task 10: README, Installer Docs, And Stale Identity Tests

**Files:**
- Modify: `tests/test_readme_docs.py`
- Create: `tests/test_identity_policy.py`

- [ ] **Step 1: Add README docs tests**

Append to `tests/test_readme_docs.py`:

```python
    def test_codex_superpowers_docs_explain_plugin_and_manual_modes(self) -> None:
        for relative in ("README.md", "docs/README.codex.md", ".codex/INSTALL.md"):
            with self.subTest(path=relative):
                contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("Codex App curated Superpowers plugin", contents)
                self.assertIn("manual ~/.codex/superpowers fallback", contents)
                self.assertIn("duplicate skill entries", contents)

    def test_translated_readmes_mention_duplicate_superpowers_discovery(self) -> None:
        expected = {
            "README.ko.md": "중복 skill 항목",
            "README.ja.md": "重複する skill 項目",
            "README.zh-CN.md": "重复的 skill 条目",
        }
        for relative, phrase in expected.items():
            with self.subTest(path=relative):
                contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn(phrase, contents)
```

- [ ] **Step 2: Add stale identity tests**

Create `tests/test_identity_policy.py` with:

```python
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STALE_PATTERNS = ("jerrygoha", "Jerry Go", "48903443+jerrygoha@users.noreply.github.com", "github.com/jerrygoha/agent-bootstrap")
ALLOWLIST_PREFIXES = (
    "docs/superpowers/plans/",
    "docs/superpowers/specs/",
)


class IdentityPolicyTests(unittest.TestCase):
    def tracked_files(self) -> list[Path]:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return [REPO_ROOT / line for line in result.stdout.splitlines()]

    def test_active_files_do_not_contain_stale_github_identity(self) -> None:
        offenders = []
        for path in self.tracked_files():
            relative = path.relative_to(REPO_ROOT).as_posix()
            if relative.startswith(ALLOWLIST_PREFIXES):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in STALE_PATTERNS:
                if pattern in text:
                    offenders.append(f"{relative}: {pattern}")

        self.assertEqual(offenders, [])

    def test_repo_metadata_targets_hun_repository(self) -> None:
        metadata = (REPO_ROOT / "docs" / "repo-metadata.md").read_text(encoding="utf-8")

        self.assertIn("gh repo edit hun99999/agent-bootstrap", metadata)
        self.assertNotIn("gh repo edit jerrygoha/agent-bootstrap", metadata)
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```bash
python3 -m unittest tests.test_readme_docs tests.test_identity_policy
```

Expected:

```text
FAIL
```

- [ ] **Step 4: Commit failing tests**

Run:

```bash
git status --short
git add tests/test_readme_docs.py tests/test_identity_policy.py
git commit -m "test: capture docs and identity policy"
```

Expected:

```text
commit succeeds
```

---

### Task 11: README, Installer Docs, And Identity Implementation

**Files:**
- Modify: `.codex/INSTALL.md`
- Modify: `docs/README.codex.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `README.ja.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/repo-metadata.md`
- Modify: `tests/test_readme_docs.py`
- Modify: `tests/test_identity_policy.py`

- [ ] **Step 1: Update English Superpowers wording**

Use this exact concept text in `README.md`, `docs/README.codex.md`, and `.codex/INSTALL.md` with file-local wording:

```markdown
Codex App can use the Codex App curated Superpowers plugin. The installer still supports a manual ~/.codex/superpowers fallback for environments that rely on local skill discovery. Avoid enabling both discovery paths unless you intentionally want duplicate skill entries.
```

- [ ] **Step 2: Update translated README wording**

Add equivalent short text:

```markdown
Codex App은 Codex App curated Superpowers plugin을 사용할 수 있습니다. installer는 로컬 skill discovery가 필요한 환경을 위해 manual ~/.codex/superpowers fallback도 유지합니다. 두 discovery path를 동시에 켜면 중복 skill 항목이 생길 수 있습니다.
```

```markdown
Codex App は Codex App curated Superpowers plugin を使用できます。installer は、local skill discovery に依存する環境向けに manual ~/.codex/superpowers fallback も維持します。両方の discovery path を有効にすると、重複する skill 項目が表示されることがあります。
```

```markdown
Codex App 可以使用 Codex App curated Superpowers plugin。installer 仍保留 manual ~/.codex/superpowers fallback，供依赖 local skill discovery 的环境使用。同时启用两条 discovery path 可能产生重复的 skill 条目。
```

- [ ] **Step 3: Update repo metadata command**

In `docs/repo-metadata.md`, replace:

```bash
gh repo edit jerrygoha/agent-bootstrap \
```

with:

```bash
gh repo edit hun99999/agent-bootstrap \
```

- [ ] **Step 4: Run focused tests**

Run:

```bash
python3 -m unittest tests.test_readme_docs tests.test_identity_policy
```

Expected:

```text
OK
```

- [ ] **Step 5: Commit**

Run:

```bash
git status --short
git add .codex/INSTALL.md docs/README.codex.md README.md README.ko.md README.ja.md README.zh-CN.md docs/repo-metadata.md tests/test_readme_docs.py tests/test_identity_policy.py
git commit -m "docs: clarify superpowers and identity policy"
```

Expected:

```text
commit succeeds
```

---

### Task 12: Installer Rendering Coverage

**Files:**
- Modify: `tests/test_install.py`

- [ ] **Step 1: Add rendered config policy test**

Append to `InstallScriptTests`:

```python
    def test_install_renders_codex_model_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / ".codex"
            agents_home = root / ".agents"
            remote, working = self.create_superpowers_remote(root)
            self.commit_superpowers_change(
                working,
                "skills/example/SKILL.md",
                "version 1\n",
                "Add initial skill",
            )

            result = self.run_installer(
                "--partner-name",
                "Hun",
                "--codex-home",
                str(codex_home),
                "--agents-home",
                str(agents_home),
                "--superpowers-remote",
                str(remote),
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            config = (codex_home / "config.toml").read_text(encoding="utf-8")
            self.assertIn('model = "gpt-5.5"', config)
            self.assertIn('model_reasoning_summary = "detailed"', config)
            self.assertIn('model_verbosity = "high"', config)
            self.assertIn('plan_mode_reasoning_effort = "xhigh"', config)
            self.assertIn("[profiles.previous]", config)
            self.assertEqual(config.count('model = "gpt-5.4"'), 1)
```

- [ ] **Step 2: Run test**

Run:

```bash
python3 -m unittest tests.test_install.InstallScriptTests.test_install_renders_codex_model_policy
```

Expected:

```text
OK
```

- [ ] **Step 3: Commit**

Run:

```bash
git status --short
git add tests/test_install.py
git commit -m "test: cover installed codex config policy"
```

Expected:

```text
commit succeeds
```

---

### Task 13: Full Verification And Repository Metadata Application

**Files:**
- No planned repository edits unless verification exposes a defect.

- [ ] **Step 1: Run full test suite**

Run:

```bash
python3 -m unittest discover -s tests
```

Expected:

```text
OK
```

- [ ] **Step 2: Run stale identity scan**

Run:

```bash
rg -n "jerrygoha|Jerry Go|48903443\\+jerrygoha@users\\.noreply\\.github\\.com|github\\.com/jerrygoha/agent-bootstrap" .
```

Expected:

```text
Only allowlisted historical files under docs/superpowers/plans/ or docs/superpowers/specs/ are reported.
```

- [ ] **Step 3: Run model fallback scan**

Run:

```bash
rg -n 'model = "gpt-5\\.4"' .codex/templates/config.toml codex-home/config.toml
```

Expected:

```text
Only [profiles.previous] occurrences are reported.
```

- [ ] **Step 4: Inspect final diff**

Run:

```bash
git status --short --branch
git diff --stat HEAD
git diff --check
```

Expected:

```text
No whitespace errors
Only expected files are changed since the last task commit
```

- [ ] **Step 5: Commit remaining verification fixes**

If verification required corrections, stage each changed path shown by `git status --short` explicitly. For example, when verification only changes prompt-policy tests and README docs, run:

```bash
git status --short
git add tests/test_prompt_corpus_policy.py README.md
git commit -m "fix: address modernization verification gaps"
```

Expected:

```text
commit succeeds only if corrections were made
```

- [ ] **Step 6: Verify GitHub repository target**

Run:

```bash
gh repo view hun99999/agent-bootstrap
```

Expected:

```text
GitHub shows the hun99999/agent-bootstrap repository.
```

If `gh repo view` fails, stop and report the exact error.

- [ ] **Step 7: Apply repo metadata if target is confirmed**

Run the updated command from `docs/repo-metadata.md` only after Step 6 succeeds.

Expected:

```text
gh repo edit exits 0
```

- [ ] **Step 8: Final repository state**

Run:

```bash
git status --short --branch
git log --oneline -5
```

Expected:

```text
Branch is codex/update-agent-stack
Working tree has no uncommitted repository changes
Recent commits show the design, plan, tests, implementation, and verification commits
```
