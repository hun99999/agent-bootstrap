import tempfile
import unittest
import json
import hashlib
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

    def test_hash_bound_vendor_baseline_suppresses_only_the_exact_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            vendor = repo_root / "design-stack/vendor/source/reference.md"
            vendor.parent.mkdir(parents=True)
            content = "API_" + "TOKEN" + "=placeholder\n"
            vendor.write_text(content, encoding="utf-8")
            digest = hashlib.sha256(content.encode()).hexdigest()
            baseline = {
                "schema_version": 1,
                "entries": [
                    {
                        "path": "design-stack/vendor/source/reference.md",
                        "sha256": digest,
                        "findings": [
                            {
                                "label": "secret-assignment",
                                "line": 1,
                                "excerpt": "API_" + "TOKEN" + "=placeholder",
                            }
                        ],
                    }
                ],
            }
            baseline_path = repo_root / "design-stack/vendor-scan-baseline.json"
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

            findings = check_private_paths.scan_repository_paths(
                repo_root, [vendor]
            )

        self.assertEqual(findings, [])

    def test_changed_content_new_finding_and_unlisted_line_are_not_suppressed(self) -> None:
        scenarios = (
            "API_" + "TOKEN" + "=changed\n",
            "API_" + "TOKEN" + "=placeholder\n" + "SECRET" + "=value\n",
            "safe first line\nAPI_" + "TOKEN" + "=placeholder\n",
        )
        for changed_content in scenarios:
            with self.subTest(content=changed_content), tempfile.TemporaryDirectory() as tmpdir:
                repo_root = Path(tmpdir)
                vendor = repo_root / "design-stack/vendor/source/reference.md"
                vendor.parent.mkdir(parents=True)
                original = "API_" + "TOKEN" + "=placeholder\n"
                vendor.write_text(changed_content, encoding="utf-8")
                baseline = {
                    "schema_version": 1,
                    "entries": [
                        {
                            "path": "design-stack/vendor/source/reference.md",
                            "sha256": hashlib.sha256(original.encode()).hexdigest(),
                            "findings": [
                                {
                                    "label": "secret-assignment",
                                    "line": 1,
                                    "excerpt": "API_" + "TOKEN" + "=placeholder",
                                }
                            ],
                        }
                    ],
                }
                baseline_path = repo_root / "design-stack/vendor-scan-baseline.json"
                baseline_path.parent.mkdir(parents=True, exist_ok=True)
                baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

                findings = check_private_paths.scan_repository_paths(
                    repo_root, [vendor]
                )

            self.assertTrue(findings)

    def test_invalid_hash_missing_target_and_authored_path_baselines_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            baseline_path = repo_root / "design-stack/vendor-scan-baseline.json"
            baseline_path.parent.mkdir(parents=True)
            for entry in (
                {
                    "path": "design-stack/vendor/source/missing.md",
                    "sha256": "0" * 64,
                    "findings": [],
                },
                {
                    "path": "design-stack/vendor/source/reference.md",
                    "sha256": "invalid",
                    "findings": [],
                },
                {
                    "path": "design-stack/router/SKILL.md",
                    "sha256": "0" * 64,
                    "findings": [],
                },
            ):
                with self.subTest(entry=entry):
                    baseline_path.write_text(
                        json.dumps({"schema_version": 1, "entries": [entry]}),
                        encoding="utf-8",
                    )
                    if entry["sha256"] == "invalid" or "router" in entry["path"]:
                        with self.assertRaisesRegex(ValueError, "baseline|SHA-256|scope"):
                            check_private_paths.scan_repository_paths(repo_root, [])
                    else:
                        findings = check_private_paths.scan_repository_paths(
                            repo_root, []
                        )
                        self.assertTrue(findings)

    def test_baseline_rejects_unrecognized_fields_instead_of_hiding_them(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            baseline_path = repo_root / "design-stack/vendor-scan-baseline.json"
            baseline_path.parent.mkdir(parents=True)
            baseline_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "entries": [],
                        "unreviewed": "/" + "Users/example/private",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "field"):
                check_private_paths.scan_repository_paths(
                    repo_root, [baseline_path]
                )


if __name__ == "__main__":
    unittest.main()
