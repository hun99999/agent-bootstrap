from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_HOME_PATH = "/" + "Users/hooooonje"


def markdown_section(document: str, heading: str, next_heading: str) -> str:
    return document.split(heading, 1)[1].split(next_heading, 1)[0]


class SkillCatalogTests(unittest.TestCase):
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

    def test_hun_engineering_loop_wraps_karpathy_with_local_policy(self) -> None:
        skill_root = REPO_ROOT / "skills" / "hun-engineering-loop"

        self.assertTrue((skill_root / "SKILL.md").exists())
        self.assertTrue((skill_root / "agents" / "openai.yaml").exists())

        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        expected_sections = (
            "Memory Preflight",
            "Source Of Truth",
            "Access And Approval Boundary",
            "Artifact-First Execution",
            "Verification Contract",
            "QA / Refactor Loop",
            "Final Report",
        )
        for section in expected_sections:
            self.assertIn(section, skill)

        expected_phrases = (
            "karpathy-guidelines",
            "memory is a recall layer, not a source of truth",
            "high-risk stop/ask boundary",
            "permission profiles, hooks, or approval layers",
            "fast check",
            "targeted regression",
            "type/lint/build",
            "deployment smoke",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, skill)

    def test_project_skill_template_contains_qa_evidence_contract(self) -> None:
        template = (REPO_ROOT / "skills" / "_template" / "SKILL.md.template").read_text(
            encoding="utf-8"
        )

        expected_sections = (
            "Scope / Non-goals",
            "Memory Preflight",
            "Source Of Truth",
            "Access And Approval Boundary",
            "Artifact-First Execution",
            "Verification Contract",
            "QA / Refactor Loop",
            "Final Report",
        )
        for section in expected_sections:
            self.assertIn(section, template)

        expected_phrases = (
            "fast check",
            "targeted regression",
            "type/lint/build",
            "browser/manual QA",
            "deployment smoke",
            "negative/regression test",
            "memory is a recall layer, not a source of truth",
        )
        for phrase in expected_phrases:
            self.assertIn(phrase, template)

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
        matrix = markdown_section(
            reference,
            "## Attachment Transport Capability Matrix",
            "## Direct-First Attachment Transport",
        )
        rows = [line for line in matrix.splitlines() if line.startswith("|")][2:]
        expected_formats = (
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
        allowed_direct_statuses = {
            "`verified-staging`",
            "`unsupported-in-current-smoke`",
            "`not-tested`",
            "`user-verified`",
        }
        allowed_clipboard_statuses = {
            "`verified-staging`",
            "`unsupported-in-current-smoke`",
            "`not-tested`",
        }

        self.assertEqual(len(rows), len(expected_formats))
        for row, expected_format in zip(rows, expected_formats, strict=True):
            columns = [column.strip() for column in row.strip("|").split("|")]
            self.assertEqual(columns[0], expected_format)
            self.assertIn(columns[2], allowed_direct_statuses)
            self.assertIn(columns[3], allowed_clipboard_statuses)
            if columns[2] == "`user-verified`":
                self.assertEqual(expected_format, "ZIP")
        self.assertIn("Hun-confirmed", matrix)
        self.assertIn("Six previews staged", matrix)
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
        section = markdown_section(
            reference,
            "### Verified Clipboard Attachment Fallback",
            "## Attachment Packet",
        )

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
        self.assertIn(nested_write, section)
        self.assertIn(paste_call, section)
        self.assertLess(section.index(nested_write), section.index(focus_step))
        self.assertLess(section.index(focus_step), section.index(paste_call))
        self.assertLess(
            section.index(paste_call),
            section.index("Paste one file at a time"),
        )
        self.assertNotIn("write([{ base64", section)

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
            "QA evidence contract",
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
