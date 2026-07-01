import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = REPO_ROOT / "scripts" / "audit_agent_stack.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_agent_stack", AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit module from {AUDIT_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AgentStackAuditTests(unittest.TestCase):
    def run_git(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )

    def create_superpowers_checkout(self, root: Path) -> Path:
        remote = root / "superpowers-remote.git"
        working = root / "superpowers-working"
        checkout = root / "superpowers"

        subprocess.run(
            ["git", "init", "--bare", "--initial-branch", "main", str(remote)],
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            ["git", "init", "--initial-branch", "main", str(working)],
            capture_output=True,
            text=True,
            check=True,
        )
        self.run_git(working, "config", "user.name", "Codex Tests")
        self.run_git(working, "config", "user.email", "codex-tests@example.com")
        self.run_git(working, "remote", "add", "origin", str(remote))

        skills = working / "skills" / "example"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text("test skill\n", encoding="utf-8")
        self.run_git(working, "add", "skills/example/SKILL.md")
        self.run_git(working, "commit", "-m", "Add skill")
        self.run_git(working, "push", "-u", "origin", "main")

        subprocess.run(
            ["git", "clone", str(remote), str(checkout)],
            capture_output=True,
            text=True,
            check=True,
        )
        return checkout

    def create_agents_symlink(self, root: Path, target: Path) -> Path:
        agents_home = root / ".agents"
        skill_home = agents_home / "skills"
        skill_home.mkdir(parents=True)
        (skill_home / "superpowers").symlink_to(target)
        return agents_home

    def test_parse_version_handles_current_cli_formats(self) -> None:
        audit = load_audit_module()

        self.assertEqual(audit.parse_version("codex-cli 0.135.0"), "0.135.0")
        self.assertEqual(audit.parse_version("2.1.159 (Claude Code)"), "2.1.159")
        self.assertEqual(audit.parse_version("tool 1.15.13"), "1.15.13")

    def test_default_cli_checks_only_first_class_surfaces(self) -> None:
        audit = load_audit_module()

        check_names = [check[0] for check in audit.CLI_CHECKS]

        self.assertEqual(check_names, ["codex", "claude"])

    def test_cli_check_reports_installed_version_without_online_latest(self) -> None:
        audit = load_audit_module()

        result = audit.check_cli(
            "python",
            (sys.executable, "--version"),
            package_name=None,
            required=True,
            online=False,
        )

        self.assertEqual(result.name, "python")
        self.assertEqual(result.status, "ok")
        self.assertTrue(result.required)
        self.assertRegex(result.installed, r"^\d+\.\d+\.\d+")
        self.assertIsNone(result.latest)

    def test_missing_optional_tool_is_nonfatal_by_default(self) -> None:
        audit = load_audit_module()
        checks = [
            audit.CheckResult(
                name="opencode",
                status="missing",
                required=False,
                detail="not installed",
            )
        ]

        self.assertFalse(audit.should_fail(checks, strict=False))
        self.assertTrue(audit.should_fail(checks, strict=True))

    def test_missing_required_tool_fails(self) -> None:
        audit = load_audit_module()
        checks = [
            audit.CheckResult(
                name="codex",
                status="missing",
                required=True,
                detail="not installed",
            )
        ]

        self.assertTrue(audit.should_fail(checks, strict=False))

    def test_superpowers_checkout_ok_requires_expected_skills_symlink(self) -> None:
        audit = load_audit_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            checkout = self.create_superpowers_checkout(root)
            agents_home = self.create_agents_symlink(root, checkout / "skills")

            result = audit.check_superpowers(checkout, agents_home, online=False)

            self.assertEqual(result.status, "ok", msg=result.detail)
            self.assertEqual(result.installed, result.latest)
            self.assertTrue(result.required)

    def test_superpowers_checkout_flags_wrong_skills_symlink(self) -> None:
        audit = load_audit_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            checkout = self.create_superpowers_checkout(root)
            wrong_target = root / "wrong-skills"
            wrong_target.mkdir()
            agents_home = self.create_agents_symlink(root, wrong_target)

            result = audit.check_superpowers(checkout, agents_home, online=False)

            self.assertEqual(result.status, "error")
            self.assertIn("skills symlink", result.detail)

    def test_claude_generated_bundle_matches_renderer(self) -> None:
        audit = load_audit_module()

        result = audit.check_claude_generated_bundle(REPO_ROOT)

        self.assertEqual(result.status, "ok", msg=result.detail)
        self.assertTrue(result.required)

    def test_repo_only_audit_skips_local_cli_and_superpowers_checks(self) -> None:
        audit = load_audit_module()

        checks = audit.run_audit(
            REPO_ROOT,
            Path("/missing/superpowers"),
            Path("/missing/agents"),
            online=False,
            repo_only=True,
        )

        self.assertEqual([check.name for check in checks], ["claude-generated-bundle"])


if __name__ == "__main__":
    unittest.main()
