import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class CiWorkflowTests(unittest.TestCase):
    def test_ci_workflow_runs_repository_verification_commands(self) -> None:
        workflow_path = REPO_ROOT / ".github" / "workflows" / "ci.yml"

        self.assertTrue(workflow_path.exists(), f"missing workflow: {workflow_path}")
        workflow = workflow_path.read_text(encoding="utf-8")

        expected_phrases = (
            "python3 -m unittest discover -s tests -p 'test_*.py'",
            "python3 scripts/validate_frontend_design_stack.py --repo-root .",
            "python3 scripts/audit_agent_stack.py",
            "python3 scripts/check_private_paths.py",
            "python3 scripts/inventory_optional_tools.py --json",
            "git diff --check",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, workflow)

        self.assertLess(
            workflow.index("python3 -m unittest discover"),
            workflow.index("python3 scripts/validate_frontend_design_stack.py"),
        )
        self.assertLess(
            workflow.index("python3 scripts/validate_frontend_design_stack.py"),
            workflow.index("python3 scripts/audit_agent_stack.py"),
        )
        self.assertLess(
            workflow.index("python3 scripts/validate_frontend_design_stack.py"),
            workflow.index("python3 scripts/check_private_paths.py"),
        )


if __name__ == "__main__":
    unittest.main()
