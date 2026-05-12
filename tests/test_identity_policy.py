import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STALE_PATTERNS = (
    "jerrygoha",
    "Jerry Go",
    "48903443+jerrygoha@users.noreply.github.com",
    "github.com/jerrygoha/agent-bootstrap",
)
ALLOWLIST_PREFIXES = ("docs/superpowers/plans/", "docs/superpowers/specs/")
ALLOWLIST_FILES = {"tests/test_identity_policy.py"}


class IdentityPolicyTests(unittest.TestCase):
    def tracked_files(self) -> list[Path]:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )

        return [Path(line) for line in result.stdout.splitlines()]

    def test_active_files_do_not_contain_stale_github_identity(self) -> None:
        offenders: list[str] = []

        for relative in self.tracked_files():
            relative_posix = relative.as_posix()
            if relative_posix in ALLOWLIST_FILES:
                continue

            if relative_posix.startswith(ALLOWLIST_PREFIXES):
                continue

            try:
                contents = (REPO_ROOT / relative).read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            for pattern in STALE_PATTERNS:
                if pattern in contents:
                    offenders.append(f"{relative_posix}: {pattern}")

        self.assertEqual([], offenders)

    def test_repo_metadata_targets_hun_repository(self) -> None:
        metadata = (REPO_ROOT / "docs" / "repo-metadata.md").read_text(encoding="utf-8")

        self.assertIn("gh repo edit hun99999/agent-bootstrap", metadata)
        self.assertNotIn("gh repo edit jerrygoha/agent-bootstrap", metadata)


if __name__ == "__main__":
    unittest.main()
