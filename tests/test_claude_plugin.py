import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN_ROOT = REPO_ROOT / "plugins" / "process-first-agents"
PLUGIN_MANIFEST_PATH = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
PLUGIN_SETTINGS_PATH = PLUGIN_ROOT / "settings.json"
MINIMUM_READ_ONLY_DISALLOWED_TOOLS = {
    "Write",
    "Edit",
    "MultiEdit",
    "NotebookEdit",
}
READ_ONLY_NO_MUTATION_GUARD = (
    "Do not create, edit, delete, stage, commit, or run mutating shell commands."
)


def parse_frontmatter(markdown: str) -> dict[str, object]:
    lines = markdown.splitlines()
    if not lines or lines[0] != "---":
        return {}

    frontmatter: dict[str, object] = {}
    current_key: str | None = None
    for line in lines[1:]:
        if line == "---":
            return frontmatter
        if line.startswith("  - ") and current_key is not None:
            value = line.removeprefix("  - ")
            current_value = frontmatter[current_key]
            if not isinstance(current_value, list):
                current_value = []
                frontmatter[current_key] = current_value
            current_value.append(value)
            continue
        if ": " in line:
            key, value = line.split(": ", 1)
            frontmatter[key] = value
            current_key = key
            continue
        if line.endswith(":"):
            key = line[:-1]
            frontmatter[key] = []
            current_key = key
            continue
        current_key = None

    return frontmatter


def load_renderer_module():
    renderer_path = REPO_ROOT / "scripts" / "render_claude_plugin.py"
    spec = importlib.util.spec_from_file_location("render_claude_plugin", renderer_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load renderer module from {renderer_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_agent_metadata() -> dict[str, dict[str, object]]:
    return json.loads(
        (REPO_ROOT / "shared" / "agent-metadata.json").read_text(encoding="utf-8")
    )


class ClaudePluginTests(unittest.TestCase):
    def run_claude_plugin_validate(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["claude", "plugin", "validate", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    def test_marketplace_points_at_plugin_package(self) -> None:
        marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
        plugins = {plugin["name"]: plugin for plugin in marketplace["plugins"]}

        self.assertEqual(marketplace["name"], "agent-bootstrap")
        self.assertEqual(marketplace["owner"], {"name": "Hun"})
        self.assertEqual(
            set(plugins), {"process-first-agents", "frontend-design-pack"}
        )
        self.assertEqual(
            plugins["process-first-agents"]["source"],
            "./plugins/process-first-agents",
        )
        self.assertEqual(
            plugins["frontend-design-pack"]["source"],
            "./plugins/frontend-design-pack",
        )

    def test_marketplace_manifest_passes_claude_validation(self) -> None:
        if shutil.which("claude") is None:
            self.skipTest("claude CLI is not installed")

        result = self.run_claude_plugin_validate(MARKETPLACE_PATH)

        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr,
        )

    def test_plugin_manifest_and_settings_enable_eng_lead(self) -> None:
        manifest = json.loads(PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8"))
        settings = json.loads(PLUGIN_SETTINGS_PATH.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "process-first-agents")
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertEqual(settings, {"agent": "eng-lead"})

    def test_plugin_manifest_uses_hun_identity(self) -> None:
        manifest = json.loads(PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8"))

        self.assertEqual(
            manifest["author"],
            {"name": "Hun", "email": "48903443+hun99999@users.noreply.github.com"},
        )
        self.assertEqual(
            manifest["repository"],
            "https://github.com/hun99999/agent-bootstrap",
        )

    def test_renderer_outputs_hun_identity(self) -> None:
        renderer = load_renderer_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "process-first-agents"

            renderer.render_plugin_bundle(REPO_ROOT, plugin_root, "Hun")

            manifest = json.loads(
                (plugin_root / ".claude-plugin" / "plugin.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(
            manifest["author"],
            {"name": "Hun", "email": "48903443+hun99999@users.noreply.github.com"},
        )
        self.assertEqual(
            manifest["repository"],
            "https://github.com/hun99999/agent-bootstrap",
        )

    def test_renderer_outputs_read_only_agent_policy(self) -> None:
        renderer = load_renderer_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "process-first-agents"

            renderer.render_plugin_bundle(REPO_ROOT, plugin_root, "Hun")

            planner = parse_frontmatter(
                (plugin_root / "agents" / "planner.md").read_text(encoding="utf-8")
            )

        self.assertEqual(
            set(planner["disallowedTools"]),
            MINIMUM_READ_ONLY_DISALLOWED_TOOLS,
        )

    def test_renderer_outputs_read_only_no_mutation_guard(self) -> None:
        renderer = load_renderer_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "process-first-agents"

            renderer.render_plugin_bundle(REPO_ROOT, plugin_root, "Hun")

            planner = (plugin_root / "agents" / "planner.md").read_text(encoding="utf-8")
            worker = (plugin_root / "agents" / "worker.md").read_text(encoding="utf-8")

        self.assertIn(READ_ONLY_NO_MUTATION_GUARD, planner)
        self.assertNotIn(READ_ONLY_NO_MUTATION_GUARD, worker)

    def test_generated_agents_have_frontmatter_and_rendered_constitution(self) -> None:
        eng_lead = (PLUGIN_ROOT / "agents" / "eng-lead.md").read_text(encoding="utf-8")
        reviewer = (PLUGIN_ROOT / "agents" / "reviewer.md").read_text(encoding="utf-8")

        self.assertIn("name: eng-lead", eng_lead)
        self.assertIn("description: Primary lead for day-to-day work", eng_lead)
        self.assertIn("Hun", eng_lead)
        self.assertNotIn("{{PARTNER_NAME}}", eng_lead)
        self.assertNotIn("@local.md", eng_lead)
        self.assertIn("name: reviewer", reviewer)
        self.assertIn("description: Review-only work focused on bugs and regressions", reviewer)

    def test_generated_agents_have_claude_frontmatter_policy(self) -> None:
        metadata = load_agent_metadata()
        expected_agents = set(metadata)
        read_only_agents = {
            agent_name
            for agent_name, agent_metadata in metadata.items()
            if agent_metadata.get("read_only") is True
        }
        isolated_agents = {
            agent_name
            for agent_name, agent_metadata in metadata.items()
            if isinstance(agent_metadata.get("claude"), dict)
            and agent_metadata["claude"].get("isolation") == "worktree"
        }
        self.assertEqual(read_only_agents & isolated_agents, set())
        self.assertEqual(
            read_only_agents | isolated_agents | {"eng-lead"},
            expected_agents,
        )

        agent_paths = {path.stem: path for path in (PLUGIN_ROOT / "agents").glob("*.md")}
        self.assertEqual(set(agent_paths), expected_agents)

        for agent_name, agent_path in sorted(agent_paths.items()):
            with self.subTest(agent=agent_name):
                frontmatter = parse_frontmatter(agent_path.read_text(encoding="utf-8"))

                self.assertEqual(frontmatter.get("model"), "inherit")
                self.assertNotIn("hooks", frontmatter)
                self.assertNotIn("mcpServers", frontmatter)
                self.assertNotIn("permissionMode", frontmatter)
                if agent_name in read_only_agents:
                    self.assertEqual(
                        set(frontmatter["disallowedTools"]),
                        MINIMUM_READ_ONLY_DISALLOWED_TOOLS,
                    )
                    self.assertNotIn("isolation", frontmatter)
                elif agent_name in isolated_agents:
                    self.assertEqual(frontmatter["isolation"], "worktree")
                    self.assertNotIn("disallowedTools", frontmatter)
                else:
                    self.assertEqual(agent_name, "eng-lead")
                    self.assertNotIn("disallowedTools", frontmatter)
                    self.assertNotIn("isolation", frontmatter)

    def test_generated_read_only_agents_include_no_mutation_guard(self) -> None:
        metadata = load_agent_metadata()

        for agent_name, agent_metadata in metadata.items():
            contents = (PLUGIN_ROOT / "agents" / f"{agent_name}.md").read_text(encoding="utf-8")
            with self.subTest(agent=agent_name):
                if agent_metadata.get("read_only") is True:
                    self.assertIn(READ_ONLY_NO_MUTATION_GUARD, contents)
                else:
                    self.assertNotIn(READ_ONLY_NO_MUTATION_GUARD, contents)


if __name__ == "__main__":
    unittest.main()
