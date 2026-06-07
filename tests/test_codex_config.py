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
    "eng-lead": ("workspace-write", "on-request", "xhigh"),
    "planner": ("read-only", "never", "xhigh"),
    "researcher": ("read-only", "never", "high"),
    "debugger": ("read-only", "never", "xhigh"),
    "reviewer": ("read-only", "never", "xhigh"),
    "verifier": ("read-only", "never", "high"),
    "release-manager": ("read-only", "never", "high"),
    "skill-author": ("workspace-write", "on-request", "high"),
    "worker": ("workspace-write", "on-request", "high"),
    "frontend-engineer": ("workspace-write", "on-request", "high"),
    "backend-engineer": ("workspace-write", "on-request", "high"),
    "platform-engineer": ("workspace-write", "on-request", "high"),
    "data-engineer": ("workspace-write", "on-request", "high"),
    "security-engineer": ("workspace-write", "on-request", "xhigh"),
    "integrations-engineer": ("workspace-write", "on-request", "high"),
    "performance-engineer": ("workspace-write", "on-request", "high"),
}


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


def top_level_text(config: str) -> str:
    lines = []
    for line in config.splitlines():
        if re.match(r"^\s*\[", line):
            break
        lines.append(line)
    return "\n".join(lines)


def previous_profile_text(config: str) -> str:
    match = re.search(r"(?ms)^\[profiles\.previous\]\n(?P<body>.*?)(?=^\[|\Z)", config)
    if match is None:
        return ""
    return match.group("body")


def custom_agent_blocks(config: str) -> list[str]:
    return re.findall(r"(?ms)^\[\[custom_agent\]\]\n.*?(?=^\[\[custom_agent\]\]|^\[|\Z)", config)


def has_assignment(text: str, key: str, value: str) -> bool:
    return re.search(
        rf'(?m)^\s*{re.escape(key)}\s*=\s*"{re.escape(value)}"\s*(?:#.*)?$',
        text,
    ) is not None


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
                parsed = parse_toml_subset(config)

                expected_top_level_assignments = {
                    "model": "gpt-5.5",
                    "model_reasoning_effort": "xhigh",
                    "model_reasoning_summary": "detailed",
                    "model_verbosity": "high",
                    "plan_mode_reasoning_effort": "xhigh",
                    "personality": "pragmatic",
                }
                for key, value in expected_top_level_assignments.items():
                    self.assertTrue(has_assignment(top_level, key, value), key)
                    self.assertEqual(parsed[key], value)

                self.assertEqual(parsed["features"]["multi_agent"], True)

    def test_previous_profile_is_only_gpt_5_4_default_fallback(self) -> None:
        for path in CONFIG_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                config = read_config(path)
                previous = previous_profile_text(config)
                parsed = parse_toml_subset(config)

                self.assertTrue(has_assignment(previous, "model", "gpt-5.4"))
                self.assertEqual(parsed["profiles"]["previous"], {"model": "gpt-5.4"})
                gpt_5_4_model_assignments = re.findall(
                    r'(?m)^\s*model\s*=\s*"gpt-5\.4"\s*(?:#.*)?$',
                    config,
                )
                self.assertEqual(len(gpt_5_4_model_assignments), 1)

    def test_balanced_profile_uses_latest_model_with_medium_reasoning(self) -> None:
        for path in CONFIG_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                parsed = read_toml(path)

                self.assertEqual(
                    parsed["profiles"]["balanced"],
                    {
                        "model": "gpt-5.5",
                        "model_reasoning_effort": "medium",
                        "model_verbosity": "medium",
                        "plan_mode_reasoning_effort": "medium",
                    },
                )

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
            "model_reasoning_effort",
        }

        for role_dir in ROLE_CONFIG_DIRS:
            for role in EXPECTED_ROLES:
                with self.subTest(role_dir=role_dir.relative_to(REPO_ROOT), role=role):
                    path = role_dir / f"{role}.toml"
                    role_config = read_toml(path)
                    sandbox_mode, approval_policy, reasoning_effort = EXPECTED_ROLE_POLICIES[role]

                    self.assertEqual(set(role_config), allowed_role_config_keys)
                    self.assertEqual(
                        role_config["model_instructions_file"],
                        f"{{{{CODEX_HOME_ABS}}}}/agents/{role}.md",
                    )
                    self.assertEqual(role_config["sandbox_mode"], sandbox_mode)
                    self.assertEqual(role_config["approval_policy"], approval_policy)
                    self.assertEqual(role_config["model_reasoning_effort"], reasoning_effort)
                    self.assertNotIn("model", role_config)

    def test_gpt_5_4_is_not_pinned_in_role_configs(self) -> None:
        scanned_paths = tuple(CONFIG_PATHS) + tuple(
            role_dir / f"{role}.toml"
            for role_dir in ROLE_CONFIG_DIRS
            for role in EXPECTED_ROLES
        )
        model_assignments = []

        for path in scanned_paths:
            for line in read_config(path).splitlines():
                if re.match(r'^\s*model\s*=\s*"gpt-5\.4"\s*(?:#.*)?$', line):
                    model_assignments.append(path.relative_to(REPO_ROOT))

        self.assertEqual(
            model_assignments,
            [CONFIG_PATHS[0].relative_to(REPO_ROOT), CONFIG_PATHS[1].relative_to(REPO_ROOT)],
        )


if __name__ == "__main__":
    unittest.main()
