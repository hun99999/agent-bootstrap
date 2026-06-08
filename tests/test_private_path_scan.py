import tempfile
import unittest
from pathlib import Path

from scripts import check_private_paths


class PrivatePathScanTests(unittest.TestCase):
    def test_scan_reports_private_paths_and_secret_assignments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaking = root / "leak.md"
            leaking.write_text(
                "vault=/" + "Users/hun/private-vault\n" + "API_" + "TOKEN" + "=secret-value\n",
                encoding="utf-8",
            )

            findings = check_private_paths.scan_paths([leaking])

        labels = {finding.label for finding in findings}
        self.assertIn("private-user-path", labels)
        self.assertIn("secret-assignment", labels)

    def test_scan_allows_policy_docs_without_concrete_private_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            safe = root / "policy.md"
            safe.write_text(
                "Do not commit private paths, credentials, MCP endpoints, or auth state.\n",
                encoding="utf-8",
            )

            findings = check_private_paths.scan_paths([safe])

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
