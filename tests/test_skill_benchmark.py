import importlib.util
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class SkillBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bootstrap = load_module("bootstrap_skill_up", "scripts/bootstrap_skill_up.py")
        cls.usage = load_module("summarize_codex_usage", "scripts/summarize_codex_usage.py")

    def write_jsonl(self, root: Path, events: list[dict[str, object]]) -> Path:
        path = root / "events.jsonl"
        path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
        return path

    def test_skill_up_lock_pins_supported_assets_and_commit(self) -> None:
        lock = json.loads(
            (REPO_ROOT / "benchmarks" / "skill-up.lock.json").read_text(encoding="utf-8")
        )

        self.assertEqual(lock["version"], "0.8.0")
        self.assertRegex(lock["commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(
            set(lock["assets"]),
            {
                "darwin-amd64",
                "darwin-arm64",
                "linux-amd64",
                "linux-arm64",
                "windows-amd64",
                "windows-arm64",
            },
        )
        for asset in lock["assets"].values():
            self.assertRegex(asset["sha256"], r"^[0-9a-f]{64}$")

    def test_bootstrap_extracts_only_the_skill_up_binary(self) -> None:
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode="w:gz") as bundle:
            payload = b"skill-up-binary"
            member = tarfile.TarInfo("dist/skill-up")
            member.size = len(payload)
            bundle.addfile(member, io.BytesIO(payload))

        self.assertEqual(
            self.bootstrap.extract_binary(archive.getvalue(), "skill-up.tar.gz"),
            b"skill-up-binary",
        )

    def test_bootstrap_uses_platform_executable_name(self) -> None:
        self.assertEqual(
            self.bootstrap.default_destination("0.8.0", "windows-amd64").name,
            "skill-up.exe",
        )
        self.assertEqual(
            self.bootstrap.default_destination("0.8.0", "linux-amd64").name,
            "skill-up",
        )

    def test_usage_summary_reads_desktop_cumulative_token_event(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self.write_jsonl(
                Path(temp_dir),
                [
                    {"timestamp": "2026-08-11T00:00:00Z", "type": "session_meta"},
                    {
                        "timestamp": "2026-08-11T00:00:02Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 120,
                                    "cached_input_tokens": 70,
                                    "output_tokens": 20,
                                    "reasoning_output_tokens": 8,
                                    "total_tokens": 140,
                                }
                            },
                        },
                    },
                ],
            )

            summary = self.usage.summarize(path)

        self.assertEqual(summary.non_cached_input_tokens, 50)
        self.assertEqual(summary.reasoning_output_tokens, 8)
        self.assertEqual(summary.total_tokens, 140)
        self.assertEqual(summary.wall_seconds, 2.0)

    def test_usage_summary_reads_codex_exec_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self.write_jsonl(
                Path(temp_dir),
                [
                    {
                        "timestamp": "2026-08-11T00:00:00Z",
                        "type": "turn.completed",
                        "usage": {
                            "input_tokens": 90,
                            "cached_input_tokens": 30,
                            "output_tokens": 10,
                        },
                    }
                ],
            )

            summary = self.usage.summarize(path)

        self.assertEqual(summary.non_cached_input_tokens, 60)
        self.assertEqual(summary.total_tokens, 100)
        self.assertIsNone(summary.wall_seconds)

    def test_usage_summary_rejects_files_without_usage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self.write_jsonl(Path(temp_dir), [{"type": "thread.started"}])

            with self.assertRaisesRegex(ValueError, "no token usage event"):
                self.usage.summarize(path)

    def test_smoke_fixture_is_deterministic_and_token_free(self) -> None:
        root = REPO_ROOT / "benchmarks" / "skill-up-smoke"
        eval_text = (root / "evals" / "eval.yaml").read_text(encoding="utf-8")
        agent_text = (root / "agent.sh").read_text(encoding="utf-8")

        self.assertIn("response_format: session_result", eval_text)
        self.assertIn("parallelism: 1", eval_text)
        self.assertIn('"input_tokens":0', agent_text)
        self.assertIn('"output_tokens":0', agent_text)

    def test_candidate_registry_separates_performance_and_workflow_skills(self) -> None:
        registry = json.loads(
            (REPO_ROOT / "benchmarks" / "skill-candidates.json").read_text(
                encoding="utf-8"
            )
        )
        candidates = {item["skill"]: item for item in registry["candidates"]}

        self.assertEqual(registry["schema_version"], 1)
        self.assertEqual(
            candidates["karpathy-guidelines"]["class"],
            "performance",
        )
        self.assertEqual(
            candidates["hun-engineering-loop"]["variants"],
            ["vanilla", "karpathy", "karpathy-plus-hun"],
        )
        self.assertEqual(
            candidates["focused-debugging"]["variants"],
            ["vanilla", "upstream-v6.2.0", "lean"],
        )
        for skill_name in (
            "isolated-worktree",
            "execute-plan",
            "review-feedback-triage",
        ):
            self.assertEqual(candidates[skill_name]["class"], "workflow")
            self.assertFalse(candidates[skill_name]["implicit"])


if __name__ == "__main__":
    unittest.main()
