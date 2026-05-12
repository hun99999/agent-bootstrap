import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / ".codex" / "install.py"
LEGACY_INSTALLER = REPO_ROOT / "scripts" / "install.py"


class InstallScriptTests(unittest.TestCase):
    def run_installer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(INSTALLER),
                "--repo-root",
                str(REPO_ROOT),
                *args,
            ],
            capture_output=True,
            text=True,
        )

    def run_legacy_installer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(LEGACY_INSTALLER),
                "--repo-root",
                str(REPO_ROOT),
                *args,
            ],
            capture_output=True,
            text=True,
        )

    def run_git(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )

    def create_superpowers_remote(self, root: Path) -> tuple[Path, Path]:
        remote = root / "superpowers-remote.git"
        working = root / "superpowers-working"
        remote_result = subprocess.run(
            ["git", "init", "--bare", "--initial-branch", "main", str(remote)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(remote_result.returncode, 0, msg=remote_result.stderr)

        working_result = subprocess.run(
            ["git", "init", "--initial-branch", "main", str(working)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(working_result.returncode, 0, msg=working_result.stderr)

        self.run_git(working, "config", "user.name", "Codex Tests")
        self.run_git(working, "config", "user.email", "codex-tests@example.com")
        self.run_git(working, "remote", "add", "origin", str(remote))
        return remote, working

    def commit_superpowers_change(self, working: Path, relative_path: str, content: str, message: str) -> str:
        destination = working / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        self.run_git(working, "add", relative_path)
        self.run_git(working, "commit", "-m", message)
        self.run_git(working, "push", "origin", "main")
        return self.run_git(working, "rev-parse", "HEAD").stdout.strip()

    def create_legacy_codex_template_repo(self, root: Path) -> Path:
        repo_root = root / "codex-template-repo"
        (repo_root / ".codex" / "templates").mkdir(parents=True)
        (repo_root / "agents").mkdir()
        (repo_root / "AGENTS.md").write_text("Hello {{PARTNER_NAME}}\n", encoding="utf-8")
        (repo_root / ".codex" / "templates" / "local.md").write_text(
            "Local {{PARTNER_NAME}}\n",
            encoding="utf-8",
        )
        (repo_root / ".codex" / "templates" / "config.toml").write_text(
            'model_instructions_file = "{{CODEX_HOME_ABS}}/agents/eng-lead.md"\n',
            encoding="utf-8",
        )
        (repo_root / "agents" / "eng-lead.md").write_text("Lead {{PARTNER_NAME}}\n", encoding="utf-8")
        return repo_root

    def test_dry_run_reports_managed_files_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            codex_home = Path(tmpdir) / ".codex"
            agents_home = Path(tmpdir) / ".agents"
            resolved_codex_home = codex_home.resolve()
            resolved_agents_home = agents_home.resolve()
            result = self.run_installer(
                "--partner-name",
                "Hun",
                "--codex-home",
                str(codex_home),
                "--agents-home",
                str(agents_home),
                "--dry-run",
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("Dry run:", result.stdout)
            self.assertIn(str(resolved_codex_home / "config.toml"), result.stdout)
            self.assertIn(str(resolved_codex_home / "superpowers"), result.stdout)
            self.assertIn(str(resolved_agents_home / "skills" / "superpowers"), result.stdout)
            self.assertFalse(codex_home.exists())
            self.assertFalse(agents_home.exists())

    def test_legacy_installer_delegates_to_codex_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            codex_home = Path(tmpdir) / ".codex"
            agents_home = Path(tmpdir) / ".agents"
            result = self.run_legacy_installer(
                "--partner-name",
                "Hun",
                "--codex-home",
                str(codex_home),
                "--agents-home",
                str(agents_home),
                "--dry-run",
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn(str(codex_home.resolve() / "config.toml"), result.stdout)
            self.assertIn(str(agents_home.resolve() / "skills" / "superpowers"), result.stdout)

    def test_install_writes_codex_agent_role_configs(self) -> None:
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
            config_text = (codex_home / "config.toml").read_text(encoding="utf-8")
            self.assertIn('config_file = "agents/eng-lead.toml"', config_text)
            eng_lead_config = codex_home / "agents" / "eng-lead.toml"
            self.assertTrue(eng_lead_config.exists())
            eng_lead_text = eng_lead_config.read_text(encoding="utf-8")
            self.assertIn(
                f'model_instructions_file = "{codex_home.resolve()}/agents/eng-lead.md"',
                eng_lead_text,
            )
            self.assertNotIn("model =", eng_lead_text)

    def test_install_refuses_dirty_superpowers_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / ".codex"
            agents_home = root / ".agents"
            repo_root = self.create_legacy_codex_template_repo(root)
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
                "--repo-root",
                str(repo_root),
            )
            self.assertEqual(first_result.returncode, 0, msg=first_result.stderr)
            dirty_skill = codex_home / "superpowers" / "skills" / "example" / "SKILL.md"
            dirty_content = "local user edits\n"
            dirty_skill.write_text(dirty_content, encoding="utf-8")

            result = self.run_installer(
                "--partner-name",
                "Hun",
                "--codex-home",
                str(codex_home),
                "--agents-home",
                str(agents_home),
                "--superpowers-remote",
                str(remote),
                "--repo-root",
                str(repo_root),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("dirty superpowers checkout", result.stderr)
            self.assertEqual(dirty_skill.read_text(encoding="utf-8"), dirty_content)

    def test_install_refuses_to_replace_existing_superpowers_skills_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / ".codex"
            agents_home = root / ".agents"
            existing_skills = agents_home / "skills" / "superpowers"
            existing_skills.mkdir(parents=True)
            owned_file = existing_skills / "owned.txt"
            owned_content = "user managed\n"
            owned_file.write_text(owned_content, encoding="utf-8")
            repo_root = self.create_legacy_codex_template_repo(root)
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
                "--repo-root",
                str(repo_root),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to replace existing superpowers skills path", result.stderr)
            self.assertEqual(owned_file.read_text(encoding="utf-8"), owned_content)

    def test_install_syncs_superpowers_repo_to_latest_remote_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / ".codex"
            agents_home = root / ".agents"
            remote, working = self.create_superpowers_remote(root)

            first_commit = self.commit_superpowers_change(
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
            self.assertEqual(
                (codex_home / "superpowers" / "skills" / "example" / "SKILL.md").read_text(encoding="utf-8"),
                "version 1\n",
            )
            self.assertEqual(
                self.run_git(codex_home / "superpowers", "rev-parse", "HEAD").stdout.strip(),
                first_commit,
            )
            skills_symlink = agents_home / "skills" / "superpowers"
            self.assertTrue(skills_symlink.is_symlink())
            self.assertEqual(skills_symlink.resolve(), (codex_home / "superpowers" / "skills").resolve())

            second_commit = self.commit_superpowers_change(
                working,
                "skills/example/SKILL.md",
                "version 2\n",
                "Update skill",
            )

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
            self.assertEqual(second_result.returncode, 0, msg=second_result.stderr)
            self.assertEqual(
                (codex_home / "superpowers" / "skills" / "example" / "SKILL.md").read_text(encoding="utf-8"),
                "version 2\n",
            )
            self.assertEqual(
                self.run_git(codex_home / "superpowers", "rev-parse", "HEAD").stdout.strip(),
                second_commit,
            )
            self.assertTrue(skills_symlink.is_symlink())
            self.assertEqual(skills_symlink.resolve(), (codex_home / "superpowers" / "skills").resolve())

    def test_install_can_skip_manual_superpowers_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            codex_home = root / ".codex"
            agents_home = root / ".agents"

            result = self.run_installer(
                "--partner-name",
                "Hun",
                "--codex-home",
                str(codex_home),
                "--agents-home",
                str(agents_home),
                "--superpowers-mode",
                "skip",
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("Superpowers: skipped manual checkout and symlink", result.stdout)
            self.assertFalse((codex_home / "superpowers").exists())
            self.assertFalse((agents_home / "skills" / "superpowers").exists())


if __name__ == "__main__":
    unittest.main()
