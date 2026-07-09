import re
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATHS = (
    REPO_ROOT / ".codex" / "templates" / "config.toml",
    REPO_ROOT / "codex-home" / "config.toml",
)
ROLE_CONFIG_DIRS = (
    REPO_ROOT / ".codex" / "templates" / "agents",
    REPO_ROOT / "codex-home" / "agents",
)
EXPECTED_ROLES = (
    "eng-lead",
    "planner",
    "researcher",
    "debugger",
    "reviewer",
    "verifier",
    "release-manager",
    "skill-author",
    "worker",
    "frontend-engineer",
    "backend-engineer",
    "platform-engineer",
    "data-engineer",
    "security-engineer",
    "integrations-engineer",
    "performance-engineer",
)
EXPECTED_ROLE_POLICIES = {
    "eng-lead": ("workspace-write", "on-request"),
    "planner": ("read-only", "never"),
    "researcher": ("read-only", "never"),
    "debugger": ("read-only", "never"),
    "reviewer": ("read-only", "never"),
    "verifier": ("read-only", "never"),
    "release-manager": ("read-only", "never"),
    "skill-author": ("workspace-write", "on-request"),
    "worker": ("workspace-write", "on-request"),
    "frontend-engineer": ("workspace-write", "on-request"),
    "backend-engineer": ("workspace-write", "on-request"),
    "platform-engineer": ("workspace-write", "on-request"),
    "data-engineer": ("workspace-write", "on-request"),
    "security-engineer": ("workspace-write", "on-request"),
    "integrations-engineer": ("workspace-write", "on-request"),
    "performance-engineer": ("workspace-write", "on-request"),
}
FORBIDDEN_MODEL_KEYS = (
    "model",
    "model_reasoning_effort",
    "model_reasoning_summary",
    "model_verbosity",
    "plan_mode_reasoning_effort",
)


def read_config(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_value(value: str) -> object:
    value = value.split("#", 1)[0].strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value.isdecimal():
        return int(value)
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    raise ValueError(f"Unsupported TOML value in test fixture: {value}")


def parse_toml_subset(text: str) -> dict:
    parsed: dict = {}
    current: dict = parsed

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[[") and stripped.endswith("]]"):
            table_name = stripped[2:-2].strip()
            table_items = parsed.setdefault(table_name, [])
            current = {}
            table_items.append(current)
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            current = parsed
            for part in stripped[1:-1].split("."):
                current = current.setdefault(part, {})
            continue
        key, value = stripped.split("=", 1)
        current[key.strip()] = parse_value(value)

    return parsed


def read_toml(path: Path) -> dict:
    return parse_toml_subset(read_config(path))


class CodexConfigPolicyTests(unittest.TestCase):
    def test_template_and_snapshot_config_trees_match(self) -> None:
        template = read_config(CONFIG_PATHS[0])
        snapshot = read_config(CONFIG_PATHS[1])

        self.assertEqual(snapshot, template)
        template_roles = {
            path.name: path.read_bytes()
            for path in ROLE_CONFIG_DIRS[0].glob("*.toml")
        }
        snapshot_roles = {
            path.name: path.read_bytes()
            for path in ROLE_CONFIG_DIRS[1].glob("*.toml")
        }
        self.assertEqual(snapshot_roles, template_roles)

    def test_public_configs_inherit_runtime_model_and_retain_shared_policy(self) -> None:
        for path in CONFIG_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                config = read_config(path)
                parsed = parse_toml_subset(config)

                self.assertEqual(parsed["personality"], "pragmatic")
                self.assertIn("agents", parsed)
                self.assertEqual(parsed["features"], {"multi_agent": True})
                self.assertNotIn("profiles", parsed)

    def test_public_config_trees_do_not_pin_model_entitlements(self) -> None:
        scanned_paths = tuple(CONFIG_PATHS) + tuple(
            role_path
            for role_dir in ROLE_CONFIG_DIRS
            for role_path in sorted(role_dir.glob("*.toml"))
        )

        for path in scanned_paths:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                assignments = []
                for line in read_config(path).splitlines():
                    for key in FORBIDDEN_MODEL_KEYS:
                        if re.match(rf"^\s*{re.escape(key)}\s*=", line):
                            assignments.append(line.strip())

                self.assertEqual(assignments, [])

    def test_legacy_custom_agents_are_removed(self) -> None:
        for path in CONFIG_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                config = read_config(path)

                self.assertNotIn("[[custom_agent]]", config)
                self.assertNotIn("base_instructions_file", config)

    def test_expected_agent_role_tables_exist(self) -> None:
        expected_agents = set(EXPECTED_ROLES) | {"orchestrator"}
        expected_agent_controls = {
            "max_threads": 6,
            "max_depth": 1,
        }
        allowed_agent_keys = {"config_file", "description", "nickname_candidates"}

        for path in CONFIG_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                parsed = read_toml(path)
                agents = parsed["agents"]
                agent_tables = {
                    name
                    for name, value in agents.items()
                    if isinstance(value, dict)
                }
                agent_controls = {
                    name: value
                    for name, value in agents.items()
                    if not isinstance(value, dict)
                }

                self.assertEqual(agent_tables, expected_agents)
                self.assertEqual(agent_controls, expected_agent_controls)
                for role in EXPECTED_ROLES:
                    agent = agents[role]
                    self.assertLessEqual(set(agent), allowed_agent_keys)
                    self.assertEqual(agent["config_file"], f"agents/{role}.toml")
                    self.assertIsInstance(agent["description"], str)
                    self.assertNotEqual(agent["description"].strip(), "")

                orchestrator = agents["orchestrator"]
                self.assertLessEqual(set(orchestrator), allowed_agent_keys)
                self.assertEqual(orchestrator["config_file"], "agents/eng-lead.toml")
                self.assertIsInstance(orchestrator["description"], str)
                self.assertNotEqual(orchestrator["description"].strip(), "")

                config_file_counts = Counter(agents[role]["config_file"] for role in agent_tables)
                duplicates = {
                    config_file
                    for config_file, count in config_file_counts.items()
                    if count > 1
                }
                self.assertEqual(duplicates, {"agents/eng-lead.toml"})

    def test_role_config_files_reference_prompts_without_model_pins(self) -> None:
        allowed_role_config_keys = {
            "model_instructions_file",
            "sandbox_mode",
            "approval_policy",
        }

        for role_dir in ROLE_CONFIG_DIRS:
            for role in EXPECTED_ROLES:
                with self.subTest(role_dir=role_dir.relative_to(REPO_ROOT), role=role):
                    path = role_dir / f"{role}.toml"
                    role_config = read_toml(path)
                    sandbox_mode, approval_policy = EXPECTED_ROLE_POLICIES[role]

                    self.assertEqual(set(role_config), allowed_role_config_keys)
                    self.assertEqual(
                        role_config["model_instructions_file"],
                        f"{{{{CODEX_HOME_ABS}}}}/agents/{role}.md",
                    )
                    self.assertEqual(role_config["sandbox_mode"], sandbox_mode)
                    self.assertEqual(role_config["approval_policy"], approval_policy)
                    self.assertNotIn("model", role_config)


if __name__ == "__main__":
    unittest.main()
