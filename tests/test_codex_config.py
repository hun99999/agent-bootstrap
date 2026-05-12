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

                expected_top_level_assignments = {
                    "model": "gpt-5.5",
                    "model_reasoning_effort": "xhigh",
                    "model_reasoning_summary": "detailed",
                    "model_verbosity": "high",
                    "plan_mode_reasoning_effort": "xhigh",
                }
                for key, value in expected_top_level_assignments.items():
                    self.assertTrue(has_assignment(top_level, key, value), key)

    def test_previous_profile_is_only_gpt_5_4_default_fallback(self) -> None:
        for path in CONFIG_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                config = read_config(path)
                previous = previous_profile_text(config)

                self.assertTrue(has_assignment(previous, "model", "gpt-5.4"))
                gpt_5_4_model_assignments = re.findall(
                    r'(?m)^\s*model\s*=\s*"gpt-5\.4"\s*(?:#.*)?$',
                    config,
                )
                self.assertEqual(len(gpt_5_4_model_assignments), 1)

    def test_legacy_custom_agents_do_not_pin_previous_model(self) -> None:
        for path in CONFIG_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                config = read_config(path)
                blocks = custom_agent_blocks(config)

                self.assertFalse(any(has_assignment(block, "agent_type", "eng-lead") for block in blocks))

                for block in blocks:
                    self.assertFalse(has_assignment(block, "model", "gpt-5.4"))


if __name__ == "__main__":
    unittest.main()
