from pathlib import Path
import re
import subprocess
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_HOME_PATH = "/" + "Users/hooooonje"
MATT_POCOCK_SKILLS_COMMIT = "2ab958093e83e0ec752e6c1c5932da465bf23e0c"
HANDOFF_CATALOG_FILES = (
    "skills/handoff/SKILL.md",
    "skills/handoff/agents/openai.yaml",
    "skills/handoff/SOURCE.md",
    "skills/handoff/LICENSE",
)
LEAN_WORKFLOW_SKILLS = {
    "isolated-worktree": "using-git-worktrees",
    "execute-plan": "executing-plans",
    "review-feedback-triage": "receiving-code-review",
    "focused-debugging": "systematic-debugging",
}


def markdown_section(document: str, heading: str, next_heading: str) -> str:
    return document.split(heading, 1)[1].split(next_heading, 1)[0]


class SkillCatalogTests(unittest.TestCase):
    def test_lean_superpowers_adaptations_are_compact_and_explicit_only(self) -> None:
        for skill_name, upstream_name in LEAN_WORKFLOW_SKILLS.items():
            with self.subTest(skill=skill_name):
                skill_root = REPO_ROOT / "skills" / skill_name
                skill_path = skill_root / "SKILL.md"
                openai_path = skill_root / "agents" / "openai.yaml"
                source_path = skill_root / "SOURCE.md"
                license_path = skill_root / "LICENSE"

                for path in (skill_path, openai_path, source_path, license_path):
                    self.assertTrue(path.is_file(), path)

                skill = skill_path.read_text(encoding="utf-8")
                openai = openai_path.read_text(encoding="utf-8")
                source = source_path.read_text(encoding="utf-8")
                license_text = license_path.read_text(encoding="utf-8")

                self.assertLessEqual(len(skill.split()), 220)
                self.assertIn(f"name: {skill_name}", skill)
                self.assertRegex(skill, r"description: Use only when ")
                self.assertIn("## Result", skill)
                self.assertIn("## Route", skill)
                self.assertIn("## Stop", skill)
                self.assertIn("allow_implicit_invocation: false", openai)
                self.assertIn(f"${skill_name}", openai)
                self.assertIn("https://github.com/obra/superpowers", source)
                self.assertIn("v6.2.0", source)
                self.assertIn(f"skills/{upstream_name}/SKILL.md", source)
                self.assertIn("adapted", source.lower())
                self.assertIn("MIT License", license_text)
                self.assertIn("Copyright (c) 2025 Jesse Vincent", license_text)

                lowered = skill.lower()
                for phrase in (
                    "subagent",
                    "review checkpoint",
                    "finishing-a-development-branch",
                    "verification-before-completion",
                    "test-driven-development",
                    "full test suite",
                    "read every line",
                    "read again",
                ):
                    self.assertNotIn(phrase, lowered)

    def test_core_guidance_stays_implicit_with_a_lean_hun_wrapper(self) -> None:
        for skill_name in ("karpathy-guidelines", "hun-engineering-loop"):
            with self.subTest(skill=skill_name):
                openai = (
                    REPO_ROOT / "skills" / skill_name / "agents" / "openai.yaml"
                ).read_text(encoding="utf-8")
                self.assertIn("allow_implicit_invocation: true", openai)

        hun_loop = (
            REPO_ROOT / "skills" / "hun-engineering-loop" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertLessEqual(len(hun_loop.split()), 220)
        self.assertIn("## Result", hun_loop)
        self.assertIn("## Route", hun_loop)
        self.assertIn("## Stop", hun_loop)
        self.assertNotIn("## Memory Preflight", hun_loop)
        self.assertNotIn("## QA / Refactor Loop", hun_loop)

    def test_catalog_explains_lean_workflow_and_performance_boundaries(self) -> None:
        catalog = (REPO_ROOT / "skills" / "README.md").read_text(encoding="utf-8")
        guides = "\n".join(
            (REPO_ROOT / relative).read_text(encoding="utf-8")
            for relative in ("docs/codex-skills.md", "docs/claude-skills.md")
        )

        for skill_name in LEAN_WORKFLOW_SKILLS:
            self.assertIn(f"### {skill_name}", catalog)
            self.assertIn(f"`{skill_name}`", guides)
        self.assertIn("explicit-use", catalog.lower())
        self.assertIn("benchmark", catalog.lower())

    def test_catalog_lists_karpathy_guidelines_as_public_base_first(self) -> None:
        catalog = (REPO_ROOT / "skills" / "README.md").read_text(encoding="utf-8")

        karpathy_entry = catalog.index("### karpathy-guidelines")
        chatgpt_entry = catalog.index("### chatgpt-collaboration-harness")
        hun_loop_entry = catalog.index("### hun-engineering-loop")
        template_entry = catalog.index("### _template")
        self.assertLess(karpathy_entry, chatgpt_entry)
        self.assertLess(chatgpt_entry, hun_loop_entry)
        self.assertLess(hun_loop_entry, template_entry)
        self.assertIn("browse, review, select, then install", catalog)
        self.assertIn("not an always-install bootstrap", catalog)
        self.assertIn("~/.codex/skills", catalog)
        self.assertIn("public default base skill", catalog)
        self.assertIn("community-sentiment", catalog)
        self.assertIn("Korean by default", catalog)
        self.assertIn("original catalog/vendor skill", catalog)
        self.assertIn("Hun-local operational wrapper", catalog)
        self.assertIn("not part of the public default install set", catalog)
        self.assertNotIn(PRIVATE_HOME_PATH, catalog)

    def test_karpathy_guidelines_source_is_preserved(self) -> None:
        skill_root = REPO_ROOT / "skills" / "karpathy-guidelines"

        self.assertTrue((skill_root / "SKILL.md").exists())
        self.assertTrue((skill_root / "references" / "SOURCE.md").exists())

        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        source = (skill_root / "references" / "SOURCE.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("name: karpathy-guidelines", skill)
        self.assertIn("license: MIT", skill)
        self.assertIn("Think Before Coding", skill)
        self.assertIn("Simplicity First", skill)
        self.assertIn("Surgical Changes", skill)
        self.assertIn("Goal-Driven Execution", skill)
        self.assertIn("https://github.com/multica-ai/andrej-karpathy-skills", source)
        self.assertIn("2c606141936f1eeef17fa3043a72095b4765b9c2", source)
        self.assertIn("MIT", source)
        self.assertNotIn(PRIVATE_HOME_PATH, source)

    def test_handoff_catalog_source_files_are_tracked(self) -> None:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        tracked_files = set(result.stdout.splitlines())

        self.assertEqual(set(), set(HANDOFF_CATALOG_FILES) - tracked_files)

    def test_handoff_preserves_reviewed_source_and_mit_attribution(self) -> None:
        skill_root = REPO_ROOT / "skills" / "handoff"
        source_path = skill_root / "SOURCE.md"
        license_path = skill_root / "LICENSE"

        self.assertTrue(source_path.is_file(), source_path)
        self.assertTrue(license_path.is_file(), license_path)

        source = source_path.read_text(encoding="utf-8")
        license_text = license_path.read_text(encoding="utf-8")
        self.assertIn("https://github.com/mattpocock/skills", source)
        self.assertIn(MATT_POCOCK_SKILLS_COMMIT, source)
        self.assertIn("MIT", source)
        self.assertIn("Matt Pocock", source)
        self.assertIn("MIT License", license_text)
        self.assertIn("Copyright (c) 2026 Matt Pocock", license_text)

    def test_handoff_is_compact_and_explicit_only(self) -> None:
        skill_root = REPO_ROOT / "skills" / "handoff"
        skill_path = skill_root / "SKILL.md"
        openai_path = skill_root / "agents" / "openai.yaml"

        self.assertTrue(skill_path.is_file(), skill_path)
        self.assertTrue(openai_path.is_file(), openai_path)

        skill = skill_path.read_text(encoding="utf-8")
        openai = openai_path.read_text(encoding="utf-8")
        self.assertLessEqual(len(skill.split()), 200)
        self.assertIn("name: handoff", skill)
        self.assertNotIn("argument-hint:", skill)
        self.assertNotIn("disable-model-invocation:", skill)
        self.assertIn("allow_implicit_invocation: false", openai)

    def test_handoff_does_not_add_broad_automatic_workflows(self) -> None:
        skill_root = REPO_ROOT / "skills" / "handoff"
        skill_path = skill_root / "SKILL.md"
        openai_path = skill_root / "agents" / "openai.yaml"

        self.assertTrue(skill_path.is_file(), skill_path)
        self.assertTrue(openai_path.is_file(), openai_path)

        workflow = (
            skill_path.read_text(encoding="utf-8")
            + "\n"
            + openai_path.read_text(encoding="utf-8")
        ).lower()
        forbidden_phrases = (
            "background agent",
            "spawn_agent",
            "sub-agent",
            "subagent",
            "agent tool",
            "git status",
            "git diff",
            "git log",
            "git commit",
            "git push",
            "browser",
            "playwright",
            "run tests",
            "test suite",
            "test command",
            "npm test",
            "pytest",
            "```bash",
        )
        for phrase in forbidden_phrases:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, workflow)

    def test_catalog_documents_only_handoff_from_matt_pocock_subset(self) -> None:
        catalog = (REPO_ROOT / "skills" / "README.md").read_text(encoding="utf-8")
        guide = (REPO_ROOT / "docs" / "codex-skills.md").read_text(encoding="utf-8")

        for document in (catalog, guide):
            self.assertIn("Matt Pocock", document)
            self.assertIn("only `handoff`", document)
            self.assertIn("`~/.codex/skills/handoff`", document)

        self.assertIn("### handoff", catalog)
        for excluded_skill in ("tdd", "diagnosing-bugs", "research", "code-review"):
            with self.subTest(excluded_skill=excluded_skill):
                self.assertNotIn(f"### {excluded_skill}", catalog)
                self.assertNotIn(
                    f"~/.codex/skills/{excluded_skill}",
                    catalog + "\n" + guide,
                )

    def test_handoff_catalog_files_do_not_contain_private_absolute_paths(self) -> None:
        paths = tuple(REPO_ROOT / relative for relative in HANDOFF_CATALOG_FILES) + (
            REPO_ROOT / "skills" / "README.md",
            REPO_ROOT / "docs" / "codex-skills.md",
        )

        for path in paths:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertTrue(path.is_file(), path)
                self.assertNotIn(
                    PRIVATE_HOME_PATH,
                    path.read_text(encoding="utf-8"),
                )

    def test_hun_engineering_loop_is_a_small_local_delta(self) -> None:
        skill_root = REPO_ROOT / "skills" / "hun-engineering-loop"

        self.assertTrue((skill_root / "SKILL.md").exists())
        self.assertTrue((skill_root / "agents" / "openai.yaml").exists())

        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        expected_sections = ("Result", "Route", "Stop")
        for section in expected_sections:
            self.assertIn(section, skill)

        expected_phrases = (
            "rough, abstract, or negative instruction",
            "smallest concrete outcome",
            "current target evidence",
            "lowest-cost direct evidence",
            "fresh minimal context",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, skill)

    def test_project_skill_template_is_compact_result_oriented_and_explicit(self) -> None:
        template = (REPO_ROOT / "skills" / "_template" / "SKILL.md.template").read_text(
            encoding="utf-8"
        )
        metadata = (
            REPO_ROOT / "skills" / "_template" / "agents" / "openai.yaml.template"
        ).read_text(encoding="utf-8")

        self.assertLessEqual(len(template.split()), 240)
        expected_sections = ("## Result", "## Route", "## Evidence", "## Stop")
        for section in expected_sections:
            self.assertIn(section, template)

        expected_phrases = (
            "Use only when",
            "workflow skill",
            "performance skill",
            "lowest-cost direct evidence",
            "concrete blocker",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, template)
        self.assertNotIn("Memory Preflight", template)
        self.assertNotIn("QA / Refactor Loop", template)
        self.assertIn("allow_implicit_invocation: false", metadata)

    def test_private_project_skills_are_not_cataloged(self) -> None:
        catalog = (REPO_ROOT / "skills" / "README.md").read_text(encoding="utf-8")

        self.assertFalse((REPO_ROOT / "skills" / "auto-eva").exists())
        expected_phrases = (
            "Private project skills such as auto-eva",
            "not this public catalog",
            "~/.codex/skills",
            "~/.claude/skills",
            "templates and public-safe process guidance",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, catalog)
        self.assertNotIn(PRIVATE_HOME_PATH, catalog)

    def test_chatgpt_collaboration_harness_source_is_cataloged(self) -> None:
        skill_root = REPO_ROOT / "skills" / "chatgpt-collaboration-harness"
        expected_files = (
            "SKILL.md",
            "agents/openai.yaml",
            "references/goal-harness.md",
            "references/feedback-loop.md",
            "references/chrome-chatgpt-pro.md",
            "references/delegated-work.md",
            "references/search-deep-research.md",
            "references/file-artifact-exchange.md",
        )

        for relative in expected_files:
            with self.subTest(relative=relative):
                self.assertTrue((skill_root / relative).exists())

        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Evidence And Language Rules", skill)
        self.assertIn("community-sentiment", skill)
        self.assertIn("keep the ChatGPT Pro conversation", skill)
        self.assertIn("screenshots, files, or generated artifacts", skill)
        self.assertIn("file-artifact-exchange.md", skill)

        prompt = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("source-backed evidence", prompt)
        self.assertIn("Korean", prompt)
        self.assertIn("screenshots, files, and artifacts", prompt)

    def test_chatgpt_collaboration_harness_diagnoses_chrome_upload_failures(
        self,
    ) -> None:
        skill_root = REPO_ROOT / "skills" / "chatgpt-collaboration-harness"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        reference = (skill_root / "references" / "chrome-chatgpt-pro.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Chrome file upload fails", skill)
        self.assertIn("`references/chrome-chatgpt-pro.md` and", skill)
        self.assertIn(
            "`references/file-artifact-exchange.md` before retrying", skill
        )
        expected_phrases = (
            "File Upload Diagnosis",
            "`file-uploads`",
            "`filechooser`",
            "absolute paths",
            "`chooser.isMultiple()`",
            "`chooser.setFiles(...)`",
            "`chrome-file-upload-troubleshooting`",
            "`Not allowed`",
            "Allow access to file URLs",
            "`chrome://extensions`",
            "Do not work around",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, reference)
        self.assertNotIn(PRIVATE_HOME_PATH, reference)

    def test_chatgpt_collaboration_harness_uses_the_chrome_upload_api_contract(
        self,
    ) -> None:
        reference = (
            REPO_ROOT
            / "skills"
            / "chatgpt-collaboration-harness"
            / "references"
            / "chrome-chatgpt-pro.md"
        ).read_text(encoding="utf-8")
        section = markdown_section(
            reference,
            "## File Upload Diagnosis",
            "## Capability Selection",
        )

        expected_phrases = (
            "fulfillment or rejection",
            "may instead surface the packaged permission instruction",
            "current instruction verbatim, including its details link",
            "https://developers.openai.com/codex/app/chrome-extension#upload-files",
            "Opening the Extension Manager is approval-gated",
            "permission change requires action-time confirmation",
            "permission change remains user-directed",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, section)
        self.assertNotIn("actual `chooser.setFiles(...)` result", section)
        self.assertNotIn(
            "https://learn.chatgpt.com/docs/chrome-extension#upload-files",
            section,
        )
        self.assertLess(
            section.index("Start the `filechooser` wait"),
            section.index("`chooser.isMultiple()`"),
        )
        self.assertLess(
            section.index("`chooser.isMultiple()`"),
            section.index("passing more than one path"),
        )

    def test_chatgpt_upload_design_keeps_extension_manager_user_directed(
        self,
    ) -> None:
        design = (
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "specs"
            / "2026-07-12-chatgpt-upload-fallback-design.md"
        ).read_text(encoding="utf-8")

        expected_phrases = (
            "Opening the Extension Manager is approval-gated",
            "reproduced browser safety blocked automated access",
            "permission change requires action-time confirmation",
            "permission change remains user-directed",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, design)

    def test_chatgpt_collaboration_harness_keeps_file_permission_diagnosis_conditional(
        self,
    ) -> None:
        reference = (
            REPO_ROOT
            / "skills"
            / "chatgpt-collaboration-harness"
            / "references"
            / "chrome-chatgpt-pro.md"
        ).read_text(encoding="utf-8")

        expected_phrases = (
            "does not prove that file-URL access is the sole cause",
            "start the Chrome task again",
            "fresh file-chooser attempt",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, reference)
        self.assertNotIn(PRIVATE_HOME_PATH, reference)

    def test_chatgpt_collaboration_harness_does_not_conflate_remediation_with_cause(
        self,
    ) -> None:
        reference = (
            REPO_ROOT
            / "skills"
            / "chatgpt-collaboration-harness"
            / "references"
            / "chrome-chatgpt-pro.md"
        ).read_text(encoding="utf-8")

        expected_phrases = (
            "record the documented remediation and the fresh attempt result",
            "does not isolate file-URL access as the sole cause",
            "unless independently isolated",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, reference)
        self.assertNotIn(PRIVATE_HOME_PATH, reference)

    def test_chatgpt_collaboration_harness_documents_file_artifact_exchange(self) -> None:
        reference = (
            REPO_ROOT
            / "skills"
            / "chatgpt-collaboration-harness"
            / "references"
            / "file-artifact-exchange.md"
        ).read_text(encoding="utf-8")

        expected_phrases = (
            "Screenshot Attachments",
            "File Attachments",
            "Receiving Generated Artifacts",
            "Attachment Packet",
            "Artifact Return Contract",
            "Check for secrets",
            "Do not upload credentials",
            "Downloaded artifacts are untrusted until Codex validates them locally",
            "archive listing before extraction",
            "accepted, rejected, deferred, or needs-local-verification",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, reference)
        self.assertNotIn(PRIVATE_HOME_PATH, reference)

    def test_chatgpt_collaboration_harness_routes_approved_file_fallbacks(
        self,
    ) -> None:
        skill_root = REPO_ROOT / "skills" / "chatgpt-collaboration-harness"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("approved files need a clipboard fallback", skill)
        self.assertIn("references/chrome-chatgpt-pro.md", skill)
        self.assertIn("references/file-artifact-exchange.md", skill)
        self.assertNotIn("approved images need a clipboard fallback", skill)
        self.assertNotIn(PRIVATE_HOME_PATH, skill)

    def test_chatgpt_collaboration_harness_documents_direct_first_transport(
        self,
    ) -> None:
        reference = (
            REPO_ROOT
            / "skills"
            / "chatgpt-collaboration-harness"
            / "references"
            / "file-artifact-exchange.md"
        ).read_text(encoding="utf-8")

        expected_phrases = (
            "Attachment Transport Capability Matrix",
            "Direct-First Attachment Transport",
            "file chooser first",
            "exact format/MIME pair",
            "manual attachment",
            "PNG",
            "JPEG/JPG",
            "WebP",
            "GIF",
            "PDF",
            "DOCX",
            "XLSX",
            "PPTX",
            "TXT",
            "CSV",
            "ZIP",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, reference)
        self.assertNotIn(PRIVATE_HOME_PATH, reference)

    def test_chatgpt_collaboration_harness_uses_evidence_labeled_matrix(
        self,
    ) -> None:
        reference = (
            REPO_ROOT
            / "skills"
            / "chatgpt-collaboration-harness"
            / "references"
            / "file-artifact-exchange.md"
        ).read_text(encoding="utf-8")
        matrix_heading = "## Attachment Transport Capability Matrix"
        transport_heading = "## Direct-First Attachment Transport"
        self.assertIn(matrix_heading, reference)
        self.assertIn(transport_heading, reference)
        self.assertLess(
            reference.index(matrix_heading),
            reference.index(transport_heading),
        )
        matrix = markdown_section(
            reference,
            matrix_heading,
            transport_heading,
        )
        normalized_matrix = " ".join(matrix.split())
        rows = [line for line in matrix.splitlines() if line.startswith("|")][2:]
        timeout_evidence = "Timed out after 3000ms waiting for file chooser."
        expected_rows = (
            (
                "PNG",
                "image/png",
                "`unsupported-in-current-smoke`",
                "`verified-staging`",
                (
                    "`clipboard.png`",
                    "`clipboard(1).png`",
                    "Six previews staged previously",
                ),
            ),
            (
                "JPEG/JPG",
                "image/jpeg",
                "`unsupported-in-current-smoke`",
                "`verified-staging`",
                ("`clipboard.jpeg`",),
            ),
            (
                "WebP",
                "image/webp",
                "`unsupported-in-current-smoke`",
                "`verified-staging`",
                ("`clipboard.webp`",),
            ),
            (
                "GIF",
                "image/gif",
                "`unsupported-in-current-smoke`",
                "`verified-staging`",
                ("`clipboard.gif`",),
            ),
            (
                "PDF",
                "application/pdf",
                "`unsupported-in-current-smoke`",
                "`verified-staging`",
                ("`clipboard.pdf`",),
            ),
            (
                "DOCX",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "`unsupported-in-current-smoke`",
                "`verified-staging`",
                (
                    "`clipboard.vnd.openxmlformats-officedocument.wordprocessingml.document`",
                ),
            ),
            (
                "XLSX",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "`unsupported-in-current-smoke`",
                "`verified-staging`",
                (
                    "`clipboard.vnd.openxmlformats-officedocument.spreadsheetml.sheet`",
                ),
            ),
            (
                "PPTX",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "`unsupported-in-current-smoke`",
                "`verified-staging`",
                (
                    "`clipboard.vnd.openxmlformats-officedocument.presentationml.presentation`",
                ),
            ),
            (
                "TXT",
                "text/plain",
                "`unsupported-in-current-smoke`",
                "`verified-staging`",
                ("`clipboard.plain`", "no prompt text"),
            ),
            (
                "CSV",
                "text/csv",
                "`unsupported-in-current-smoke`",
                "`verified-staging`",
                ("`clipboard.csv`",),
            ),
            (
                "ZIP",
                "application/zip",
                "`user-verified`",
                "`verified-staging`",
                ("`clipboard.zip`", "Hun-confirmed"),
            ),
        )

        self.assertIn(
            "| Format | MIME type | Direct chooser | Clipboard | Evidence |",
            matrix,
        )
        self.assertEqual(len(rows), len(expected_rows))
        forbidden_row_claims = (
            "delivery",
            "persistence",
            "byte identity",
            "model readability",
            "account-side cleanup",
            "cross-session",
        )
        for row, expected in zip(rows, expected_rows, strict=True):
            (
                expected_format,
                expected_mime,
                expected_direct,
                expected_clipboard,
                evidence_markers,
            ) = expected
            with self.subTest(format=expected_format):
                columns = [
                    column.strip() for column in row.strip("|").split("|")
                ]
                self.assertEqual(len(columns), 5)
                self.assertEqual(
                    tuple(columns[:4]),
                    (
                        expected_format,
                        expected_mime,
                        expected_direct,
                        expected_clipboard,
                    ),
                )
                evidence = columns[4]
                self.assertIn(timeout_evidence, evidence)
                for marker in evidence_markers:
                    self.assertIn(marker, evidence)
                for forbidden_claim in forbidden_row_claims:
                    self.assertNotIn(forbidden_claim, evidence.lower())
        self.assertIn("prove composer staging only", normalized_matrix)
        self.assertIn("no Send occurred", normalized_matrix)
        self.assertIn(
            "ChatGPT Library persistence or deletion was not inspected",
            normalized_matrix,
        )
        self.assertIn(
            "does not establish account-side cleanup",
            normalized_matrix,
        )
        self.assertIn(
            "not a categorical product-support claim",
            normalized_matrix,
        )
        self.assertNotIn(PRIVATE_HOME_PATH, matrix)

    def test_chatgpt_collaboration_harness_gates_clipboard_by_exact_mime_evidence(
        self,
    ) -> None:
        reference = (
            REPO_ROOT
            / "skills"
            / "chatgpt-collaboration-harness"
            / "references"
            / "file-artifact-exchange.md"
        ).read_text(encoding="utf-8")

        expected_phrases = (
            "Verified Clipboard Attachment Fallback",
            "`tab.clipboard.write(...)`",
            "exact format/MIME pair",
            "`verified-staging`",
            "API success alone",
            "visible attachment preview",
            "Do not promote",
            "one file at a time",
            "Never place an absolute path",
            "Composer previews prove staging, not delivery",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, reference)
        self.assertNotIn(PRIVATE_HOME_PATH, reference)

    def test_chatgpt_collaboration_harness_separates_staging_from_library_cleanup(
        self,
    ) -> None:
        reference = (
            REPO_ROOT
            / "skills"
            / "chatgpt-collaboration-harness"
            / "references"
            / "file-artifact-exchange.md"
        ).read_text(encoding="utf-8")
        normalized_reference = " ".join(reference.split())

        expected_phrases = (
            "Attachment staging may create an account-side Library item even without Send.",
            "Clearing or abandoning the composer is not account-side cleanup.",
            "Do not stage files that must not persist in the account.",
            "Library deletion requires Hun's action-time approval or direct user action.",
            "https://help.openai.com/en/articles/20001052-library",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, normalized_reference)

    def test_chatgpt_collaboration_harness_preserves_clipboard_api_order(
        self,
    ) -> None:
        reference = (
            REPO_ROOT
            / "skills"
            / "chatgpt-collaboration-harness"
            / "references"
            / "file-artifact-exchange.md"
        ).read_text(encoding="utf-8")
        section_heading = "### Verified Clipboard Attachment Fallback"
        next_heading = "## Attachment Packet"
        self.assertIn(section_heading, reference)
        self.assertIn(next_heading, reference)
        self.assertLess(
            reference.index(section_heading),
            reference.index(next_heading),
        )
        section = markdown_section(
            reference,
            section_heading,
            next_heading,
        )
        normalized_section = " ".join(section.split())

        nested_write = """const verifiedMimeType = "image/png";
   await tab.clipboard.write([
     {
       entries: [{ base64: encodedBytes, mimeType: verifiedMimeType }],
     },
   ]);"""
        paste_call = (
            'await tab.cua.keypress({ keys: ["ControlOrMeta", "v"] });'
        )
        focus_step = "Focus the verified ChatGPT composer"
        one_file_step = "Paste one file at a time"
        expected_anchors = (
            nested_write,
            focus_step,
            paste_call,
            one_file_step,
        )
        for anchor in expected_anchors:
            self.assertIn(anchor, section)
        self.assertLess(section.index(nested_write), section.index(focus_step))
        self.assertLess(section.index(focus_step), section.index(paste_call))
        self.assertLess(section.index(paste_call), section.index(one_file_step))
        cleanup_anchors = (
            "abandon that dirty composer",
            "establish a fresh clean composer before any continuation",
            "leave an exact handoff",
        )
        for anchor in cleanup_anchors:
            self.assertIn(anchor, normalized_section)
        self.assertNotIn("write([{ base64", section)

    def test_chatgpt_multi_format_plan_reconciles_completed_smoke_evidence(
        self,
    ) -> None:
        plan = (
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "plans"
            / "2026-07-13-chatgpt-multi-format-attachments.md"
        ).read_text(encoding="utf-8")
        normalized_plan = " ".join(plan.split())

        expected_phrases = (
            "timeoutMs: 10000",
            "clamps the effective chooser wait to 3000ms",
            "current-runtime smoke only",
            "revalidate if the browser-client runtime changes",
            "`/tmp/chatgpt-multi-format-qa-20260713/pdf/pdftoppm.log` was absent",
            "`/tmp/chatgpt-multi-format-qa-20260713/pdf-fontconfig-clean/pdftoppm-output.txt`",
            "empty",
            "byte-identical",
            "Future primary QA runs must still require",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, normalized_plan)

    def test_chatgpt_collaboration_harness_runtime_sync_rechecks_itemized_snapshot(
        self,
    ) -> None:
        documents = (
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "plans"
            / "2026-07-12-chatgpt-upload-fallback.md",
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "specs"
            / "2026-07-12-chatgpt-upload-fallback-design.md",
        )
        expected_phrases = (
            "every non-noop itemized record",
            "regular-file updates at the three approved paths",
            "unexpected path, creation, file-type change, symlink change",
            "standalone metadata-only change, or deletion",
            "repeat the checksum-aware dry run immediately before synchronization",
            "identical to the reviewed output",
            "invalidates every prior deletion approval",
        )

        for document in documents:
            content = document.read_text(encoding="utf-8")
            with self.subTest(document=document.name):
                for phrase in expected_phrases:
                    self.assertIn(phrase, content)
                self.assertNotIn(PRIVATE_HOME_PATH, content)

    def test_chatgpt_collaboration_harness_runtime_sync_uses_reviewed_checksums(
        self,
    ) -> None:
        plan = (
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "plans"
            / "2026-07-12-chatgpt-upload-fallback.md"
        ).read_text(encoding="utf-8")
        design = (
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "specs"
            / "2026-07-12-chatgpt-upload-fallback-design.md"
        ).read_text(encoding="utf-8")

        expected_phrase = (
            "actual synchronization uses the same checksum comparison as the dry run"
        )
        self.assertIn(expected_phrase, plan)
        self.assertIn(expected_phrase, design)
        self.assertIn("rsync -ac \\", plan)
        self.assertNotIn("rsync -a --delete", plan)

        sync_section = markdown_section(
            plan,
            "- [ ] **Step 4: Synchronize only the approved skill**",
            "- [ ] **Step 5: Validate and compare the installed copy**",
        )
        dry_run = "rsync -acni --delete"
        actual_sync = "rsync -ac \\"
        self.assertEqual(sync_section.count(dry_run), 1)
        self.assertEqual(sync_section.count(actual_sync), 1)
        self.assertLess(sync_section.index(dry_run), sync_section.index(actual_sync))
        self.assertNotIn("rsync -a --delete", sync_section)

    def test_chatgpt_multi_format_plan_uses_content_only_runtime_sync_evidence(
        self,
    ) -> None:
        plan = (
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "plans"
            / "2026-07-13-chatgpt-multi-format-attachments.md"
        ).read_text(encoding="utf-8")
        task = markdown_section(plan, "### Task 4:", "### Task 5:")

        expected_phrases = (
            "/tmp/chatgpt-multi-format-validator-20260713-content-only",
            "/tmp/chatgpt-multi-format-validator-20260713",
            "preserve the stopped validator and its snapshots as RED evidence",
            "os.lstat",
            "followlinks=False",
            "stat.S_IMODE",
            "hashlib.sha256",
            "os.readlink",
            "special files",
            "mtime is intentionally excluded",
            "exact relative path set",
            "stable sorted JSON",
            "SKILL.md",
            "references/chrome-chatgpt-pro.md",
            "references/file-artifact-exchange.md",
            "exactly the three approved regular-file content differences",
            "rsync -rlpcni --delete",
            "rsync -rlpc \\",
            "runtime-raw-dry-run-1.txt",
            "runtime-reviewed-dry-run-1.txt",
            "runtime-transfer-count-1.txt",
            "runtime-raw-dry-run-2.txt",
            "runtime-reviewed-dry-run-2.txt",
            "runtime-transfer-count-2.txt",
            "Number of files transferred: 3",
            "first field is exactly `.f..T....`",
            "equal regular-file size, SHA-256, and mode",
            "cmp --",
            "post-sync reviewed dry run is empty",
            "Number of files transferred: 0",
            "post-sync manifests are exactly equal",
            "quick_validate.py",
            "diff -ru",
            "runtime-only deletion requires Hun's exact-path approval",
            "source-only creation",
            "regular-file mode change",
            "directory mode change",
            "file-type replacement",
            "changed symlink target",
            "special-file insertion",
            "timestamp-only mismatch",
            "reviewed-source",
            "reviewed-allowlist.txt",
            "snapshot_reviewed_source.py",
            "O_CREAT | os.O_EXCL | os.O_NOFOLLOW",
            "st_ctime_ns",
            "exact three-path allowlist",
            "--files-from=\"$ALLOWLIST\"",
            "/usr/bin/rsync -rlpcni --files-from=\"$ALLOWLIST\"",
            "/usr/bin/rsync -rlpc --files-from=\"$ALLOWLIST\" \\",
            "mutation source is the reviewed staging snapshot",
            "staging manifest exactly matches the allowlisted entries from source-pre-2.json",
            "transport-raw-dry-run-1.txt",
            "transport-reviewed-dry-run-1.txt",
            "transport-transfer-count-1.txt",
            "transport-raw-dry-run-2.txt",
            "transport-reviewed-dry-run-2.txt",
            "transport-transfer-count-2.txt",
            "runtime full manifest equals the reviewed source-pre-2 full manifest",
            "staging still equals the approved subset",
            "live source still equals source-pre-2",
            "runtime root identity is unchanged",
            "cooperative drift detection",
            "not an adversarial race-proof no-follow guarantee",
            "owner-controlled, repeatedly verified staging snapshot and exact allowlist are the mutation safety boundary",
            "owner-writable",
            "check-to-use window",
            "unequal-manifest pseudo-record",
            "non-pseudo T record",
            "unknown raw line",
            "transfer-count mismatch",
            "deletion or creation record",
            "post-sync action",
            "duplicate or unapproved action",
            "live-source mutation after pre-2",
            "source-only addition after pre-2",
            "staging mutation",
            "runtime-root identity mismatch",
            "reviewed parent directory modes match source-pre-2",
            "transport contains exactly three regular-file actions and no directory metadata action",
            "/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe",
            "preserve the failed content-only validator and its zero-byte raw evidence",
            "for evidence_path in",
            "--rsync-path=/usr/bin/rsync",
            "PATH=/usr/bin:/bin",
            "poisoned PATH without peer pin: REJECTED",
            "poisoned PATH with peer pin: PASS",
            "/tmp/chatgpt-multi-format-sync-pressure-20260713-content-only-pathsafe",
            "preserve the old content-only pressure root and never delete, overwrite, or reuse it",
            "shasum -a 256 -c \"$VALIDATOR_ROOT/failed-path-raw.sha256\"",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, task)

        self.assertNotIn("rsync -acni", task)
        self.assertNotIn("rsync -ac \\", task)
        self.assertNotIn("rsync -a ", task)
        self.assertNotIn("for path in", task)
        self.assertNotIn("immutable reviewed staging snapshot", task)
        bash_fences = re.findall(r"```bash\n(.*?)\n```", task, re.DOTALL)
        for fence in bash_fences:
            normalized = fence.replace("\\\n", " ")
            for command in normalized.splitlines():
                if "/usr/bin/rsync" not in command or "--version" in command:
                    continue
                self.assertIn("--rsync-path=/usr/bin/rsync", command)
        actual_sync = markdown_section(
            task,
            "- [ ] **Step 6: Synchronize without blanket deletion**",
            "- [ ] **Step 7: Validate the installed copy and exact equality**",
        )
        self.assertIn('"$STAGING/" "$RUNTIME/"', actual_sync)
        self.assertNotIn('"$SOURCE/" "$RUNTIME/"', actual_sync)
        self.assertNotIn(
            "skills/chatgpt-collaboration-harness/ \\", actual_sync
        )
        self.assertNotIn("--delete", actual_sync)
        self.assertNotIn(PRIVATE_HOME_PATH, task)

    def test_chatgpt_multi_format_plan_supports_partial_correction_sync(
        self,
    ) -> None:
        plan = (
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "plans"
            / "2026-07-13-chatgpt-multi-format-attachments.md"
        ).read_text(encoding="utf-8")
        task = markdown_section(plan, "### Task 4:", "### Task 5:")
        final_review = markdown_section(plan, "### Task 5:", "### Task 6:")
        normalized_task = " ".join(task.split())
        normalized_final_review = " ".join(final_review.split())

        expected_phrases = (
            "content_differences.issubset(ALLOWED_CONTENT_DIFFERENCES)",
            "if not content_differences",
            "expected_updates = (",
            "approved_regular_updates(source, runtime)",
            "expected_count = len(expected_updates)",
            "paths != expected_updates",
            "one-file correction raw/review: PASS",
            "one to three approved regular-file content differences",
            "transport reviewer uses the corresponding full source manifest",
            '--source-manifest "$VALIDATOR_ROOT/source-pre-1.json"',
            '--source-manifest "$VALIDATOR_ROOT/source-pre-2.json"',
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, normalized_task)

        self.assertIn(
            "one to three currently changed allowlisted files",
            normalized_final_review,
        )
        self.assertNotIn(
            'expected_count = 3 if arguments.phase == "pre" else 0',
            task,
        )
        self.assertNotIn(
            "if len(actions) != 3 or paths != ALLOWED_UPDATES",
            task,
        )
        self.assertNotIn(
            '--source-manifest "$STAGING_MANIFEST"',
            task,
        )

    def test_chatgpt_upload_plan_repeats_guarded_sync_after_skill_corrections(
        self,
    ) -> None:
        plan = (
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "plans"
            / "2026-07-12-chatgpt-upload-fallback.md"
        ).read_text(encoding="utf-8")
        final_review = plan.split(
            "- [ ] **Step 3: Classify feedback and apply only verified corrections**",
            1,
        )[1]

        expected_phrases = (
            "repeat the complete guarded synchronization and installed-copy validation",
            "fresh dry-run snapshot",
            "Prior dry-run output and deletion approvals are invalid",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, final_review)

    def test_chatgpt_upload_plan_task_two_matches_the_final_png_contract(self) -> None:
        plan = (
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "plans"
            / "2026-07-12-chatgpt-upload-fallback.md"
        ).read_text(encoding="utf-8")
        task = markdown_section(plan, "### Task 2:", "### Task 3:")

        expected_phrases = (
            "approved PNG attachments",
            "limited to `image/png`",
            "clean packet baseline",
            "entries: [{ base64: encodedBytes, mimeType: \"image/png\" }]",
            "await tab.cua.keypress({ keys: [\"ControlOrMeta\", \"v\"] });",
            "permission change requires action-time confirmation",
            "https://developers.openai.com/codex/app/chrome-extension#upload-files",
            "exact packet",
            "non-sensitive aliases",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, task)

    def test_chatgpt_upload_plan_integrates_from_the_primary_worktree(self) -> None:
        plan = (
            REPO_ROOT
            / "docs"
            / "superpowers"
            / "plans"
            / "2026-07-12-chatgpt-upload-fallback.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "Run these commands in the primary worktree where `main` is already checked out",
            plan,
        )
        self.assertNotIn("git switch main", plan)

    def test_skill_setup_guide_documents_selective_install_flow(self) -> None:
        guide = (REPO_ROOT / "docs" / "codex-skills.md").read_text(encoding="utf-8")

        expected_phrases = (
            "Skill Catalog",
            "browse, review, select, install",
            "repo copy is the catalog source",
            "installed copy is the runtime copy",
            "Do not install every skill automatically",
            "git status --short --branch",
            "quick_validate.py",
            "PyYAML",
            "public default base skill",
            "community-sentiment",
            "one ChatGPT work tab or conversation per project",
            "screenshots, files, and generated artifacts",
            "karpathy-guidelines",
            "hun-engineering-loop",
            "Hun-local wrapper",
            "memory is a recall layer, not a source of truth",
            "high-risk stop/ask boundary",
            "permission profiles, hooks, or approval layers",
            "source-of-truth pointer",
            "smallest complete result",
            "lowest-cost direct",
            "workflow or performance",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, guide)
        self.assertNotIn(PRIVATE_HOME_PATH, guide)

    def test_setup_prompt_keeps_installation_approval_gated(self) -> None:
        prompt = (REPO_ROOT / "prompts" / "setup-codex-skills.md").read_text(
            encoding="utf-8"
        )

        expected_phrases = (
            "Review and optionally install Codex skills from this repository.",
            "git status --short --branch",
            "skills/README.md",
            "docs/codex-skills.md",
            "chatgpt-collaboration-harness",
            "Compare the catalog copy with the installed runtime copy",
            "Ask before installing or overwriting",
            "quick_validate.py",
            "Do not copy private paths, credentials, MCP endpoints, auth state, or browser profiles",
            "file-artifact-exchange",
            "skill QA contract",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, prompt)
        self.assertNotIn(PRIVATE_HOME_PATH, prompt)

    def test_readme_links_skill_catalog_workflow(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/codex-skills.md", readme)
        self.assertIn("prompts/setup-codex-skills.md", readme)
        self.assertIn("skills/README.md", readme)

    def test_catalog_distinguishes_codex_and_claude_runtime_targets(self) -> None:
        catalog = (REPO_ROOT / "skills" / "README.md").read_text(encoding="utf-8")

        expected_phrases = (
            "Codex runtime install target: `~/.codex/skills/karpathy-guidelines`",
            "Claude Code runtime install target: `~/.claude/skills/karpathy-guidelines`",
            "Codex runtime install target: `~/.codex/skills/chatgpt-collaboration-harness`",
            "Claude Code install: do not install by default",
            "Codex runtime install target: `~/.codex/skills/hun-engineering-loop`",
            "Claude Code install: Hun-local only, not a public default",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, catalog)

        self.assertNotIn(PRIVATE_HOME_PATH, catalog)

    def test_frontend_design_is_a_plugin_not_a_catalog_skill(self) -> None:
        catalog = (REPO_ROOT / "skills" / "README.md").read_text(encoding="utf-8")

        self.assertFalse((REPO_ROOT / "skills/frontend-design").exists())
        self.assertIn("frontend-design-pack", catalog)
        self.assertIn("docs/frontend-design-stack.md", catalog)
        self.assertIn("distributed as one plugin skill", catalog)


if __name__ == "__main__":
    unittest.main()
