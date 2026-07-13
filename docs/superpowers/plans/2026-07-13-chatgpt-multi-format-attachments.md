# ChatGPT Pro Multi-Format Attachments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `chatgpt-collaboration-harness` with a direct-first, evidence-labeled attachment workflow for common images, PDFs, documents, spreadsheets, presentations, text files, and ZIP archives, then synchronize and independently validate the installed runtime copy.

**Architecture:** Keep `SKILL.md` as the compact router, keep Chrome chooser diagnosis and permission remediation in `references/chrome-chatgpt-pro.md`, and move transport selection, the bounded format/MIME matrix, clipboard qualification, and manual handoff into `references/file-artifact-exchange.md`. Drive the repository change with contract tests, gather browser evidence using valid synthetic files without sending, and promote only transport/format pairs that produce unambiguous composer previews.

**Tech Stack:** Markdown skills and references, Python 3 `unittest`, bundled Python artifact libraries (`Pillow`, `reportlab`, `python-docx`, `pypdf`) for ordinary/image/PDF/DOCX fixtures, bundled Node.js plus `@oai/artifact-tool` for XLSX/PPTX authoring and rendering, Poppler and the installed document/presentation render helpers for visual QA, Chrome browser-client runtime, Codex skill validator with PyYAML, `rsync`, Git.

---

## File Structure

- Modify: `tests/test_skill_catalog.py`
- Modify: `skills/chatgpt-collaboration-harness/SKILL.md`
- Modify: `skills/chatgpt-collaboration-harness/references/chrome-chatgpt-pro.md`
- Modify: `skills/chatgpt-collaboration-harness/references/file-artifact-exchange.md`
- Read as source of truth: `docs/superpowers/specs/2026-07-13-chatgpt-multi-format-attachments-design.md`
- Create temporarily outside Git: `/tmp/chatgpt-multi-format-generate-20260713.py`
- Create temporarily outside Git: `/tmp/chatgpt-multi-format-artifact-workspace-20260713/xlsx/build-xlsx.mjs`
- Create temporarily outside Git: `/tmp/chatgpt-multi-format-artifact-workspace-20260713/pptx/build-pptx.mjs`
- Create temporarily outside Git: `/tmp/chatgpt-multi-format-smoke-20260713/`
- Create temporarily outside Git: `/tmp/chatgpt-multi-format-qa-20260713/`
- Create temporarily outside Git: `/tmp/chatgpt-multi-format-validated-root-20260713.txt` (synthetic coordination pointer; preserve it through browser staging)
- Synchronize after repository validation: `~/.codex/skills/chatgpt-collaboration-harness/`

Do not add a repository script, dependency, binary fixture, global Codex config
option, browser-profile edit, or second skill. The user-controlled Chrome
permission is already enabled and remains environment state.

### Task 1: Replace The PNG-Only Contracts With RED Multi-Format Contracts

**Files:**
- Modify: `tests/test_skill_catalog.py:321-435`
- Test: `tests/test_skill_catalog.py`

- [ ] **Step 1: Replace the four PNG-only behavior tests**

Replace the methods beginning with
`test_chatgpt_collaboration_harness_documents_verified_clipboard_fallback`
and ending with
`test_chatgpt_collaboration_harness_uses_the_virtual_clipboard_paste_call`
with these tests:

```python
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
```

- [ ] **Step 2: Run the focused test and preserve RED**

Run:

```bash
set -euo pipefail
python3 -m unittest discover -s tests -p 'test_skill_catalog.py' -v
```

Expected: the five replacement tests fail because the current router still
says `approved images`, the reference still has
`Verified Clipboard Image Fallback`, and there is no direct-first capability
matrix. Existing unrelated catalog tests remain green.

- [ ] **Step 3: Review and commit the RED tests**

Inspect the failure output and confirm that every failure points to the missing
multi-format contract rather than a syntax, fixture, or path error. Then run:

```bash
set -euo pipefail
git status --short
git add tests/test_skill_catalog.py
git commit -m "test: define multi-format attachment contract"
```

Expected: one test-only commit; pre-commit hooks run normally.

### Task 2: Generate Valid Synthetic Fixtures And Gather Browser Evidence

**Files:**
- Create temporarily: `/tmp/chatgpt-multi-format-generate-20260713.py`
- Create temporarily: `/tmp/chatgpt-multi-format-artifact-workspace-20260713/xlsx/build-xlsx.mjs`
- Create temporarily: `/tmp/chatgpt-multi-format-artifact-workspace-20260713/pptx/build-pptx.mjs`
- Create temporarily: `/tmp/chatgpt-multi-format-smoke-20260713/`
- Create temporarily: `/tmp/chatgpt-multi-format-qa-20260713/`
- Create temporarily: `/tmp/chatgpt-multi-format-validated-root-20260713.txt` (synthetic coordination pointer; preserve it through browser staging)
- Do not modify repository files.

- [ ] **Step 1: Resolve and isolate the bundled artifact runtimes**

Call the workspace dependency resolver and use only its returned bundled
Python executable, bundled Node executable, bundled `node_modules` directory,
and bundled executable override directory. Also set `DOCUMENTS_SKILL_DIR` and
`PRESENTATIONS_SKILL_DIR` from the absolute directories of the currently loaded
installed skills; do not guess or hardcode a versioned cache path. Confirm the
required files and imports without installing anything:

```bash
set -euo pipefail
: "${BUNDLED_PYTHON:?workspace dependency loader did not return bundled Python}"
: "${BUNDLED_NODE:?workspace dependency loader did not return bundled Node}"
: "${BUNDLED_NODE_MODULES:?workspace dependency loader did not return node_modules}"
: "${BUNDLED_BIN:?workspace dependency loader did not return bundled executables}"
: "${DOCUMENTS_SKILL_DIR:?loaded documents skill directory is required}"
: "${PRESENTATIONS_SKILL_DIR:?loaded presentations skill directory is required}"
test -x "$BUNDLED_PYTHON"
test -x "$BUNDLED_NODE"
test -d "$BUNDLED_NODE_MODULES"
test -d "$BUNDLED_BIN"
test -x "$BUNDLED_BIN/pdftoppm"
test -f "$DOCUMENTS_SKILL_DIR/render_docx.py"
test -f "$PRESENTATIONS_SKILL_DIR/container_tools/setup_artifact_tool_workspace.mjs"
test -f "$PRESENTATIONS_SKILL_DIR/container_tools/slides_test.py"
"$BUNDLED_PYTHON" -c "import PIL, reportlab, docx, pypdf; print('python artifact imports: ok')"
```

Before creating anything, require every disposable top-level path to be absent:

```bash
set -euo pipefail
: "${BUNDLED_PYTHON:?workspace dependency loader did not return bundled Python}"
: "${BUNDLED_NODE:?workspace dependency loader did not return bundled Node}"
: "${BUNDLED_NODE_MODULES:?workspace dependency loader did not return node_modules}"
: "${PRESENTATIONS_SKILL_DIR:?loaded presentations skill directory is required}"
RUN_SUFFIX="${RUN_SUFFIX:-20260713}"
GENERATOR="/tmp/chatgpt-multi-format-generate-${RUN_SUFFIX}.py"
BUILD_ROOT="/tmp/chatgpt-multi-format-artifact-workspace-${RUN_SUFFIX}"
FIXTURE_ROOT="/tmp/chatgpt-multi-format-smoke-${RUN_SUFFIX}"
QA_ROOT="/tmp/chatgpt-multi-format-qa-${RUN_SUFFIX}"
VALIDATED_ROOT_FILE="/tmp/chatgpt-multi-format-validated-root-${RUN_SUFFIX}.txt"
test -x "$BUNDLED_PYTHON"
test -x "$BUNDLED_NODE"
test -d "$BUNDLED_NODE_MODULES"
test -f "$PRESENTATIONS_SKILL_DIR/container_tools/setup_artifact_tool_workspace.mjs"
test ! -e "$GENERATOR"
test ! -e "$BUILD_ROOT"
test ! -e "$FIXTURE_ROOT"
test ! -e "$QA_ROOT"
test ! -e "$VALIDATED_ROOT_FILE"
test ! -L "$VALIDATED_ROOT_FILE"
mkdir "$BUILD_ROOT"
mkdir "$BUILD_ROOT/xlsx" "$BUILD_ROOT/pptx"
ln -s "$BUNDLED_NODE_MODULES" "$BUILD_ROOT/xlsx/node_modules"
test "$(realpath "$BUILD_ROOT/xlsx/node_modules")" = "$(realpath "$BUNDLED_NODE_MODULES")"
"$BUNDLED_NODE" \
  "$PRESENTATIONS_SKILL_DIR/container_tools/setup_artifact_tool_workspace.mjs" \
  --workspace "$BUILD_ROOT/pptx"
test "$(realpath "$BUILD_ROOT/pptx/node_modules/@oai/artifact-tool")" = \
  "$(realpath "$BUNDLED_NODE_MODULES/@oai/artifact-tool")"
(cd "$BUILD_ROOT/xlsx" && "$BUNDLED_NODE" -e \
  "import('@oai/artifact-tool').then(({ Workbook, SpreadsheetFile }) => { if (!Workbook || !SpreadsheetFile) process.exit(2); console.log('xlsx artifact imports: ok'); })"
)
(cd "$BUILD_ROOT/pptx" && "$BUNDLED_NODE" -e \
  "import('@oai/artifact-tool').then(({ Presentation, PresentationFile }) => { if (!Presentation || !PresentationFile) process.exit(2); console.log('pptx artifact imports: ok'); })")
```

Expected: the Python import check, XLSX import check, and PPTX import check each
print `ok`; the XLSX workspace resolves the loader-provided `node_modules`, and
the PPTX workspace is initialized by the installed presentation skill's
official setup helper. Stop on any collision, missing import, path mismatch, or
setup error. Do not overwrite or delete an unknown path, install packages,
modify the managed dependency directory, use system runtimes, or invent a
package path.

- [ ] **Step 2: Create the temporary fixture builders with `apply_patch`**

The collision checks in Step 1 must have passed. Create the Python generator
and both ES-module builders with `apply_patch`; do not use heredocs or copy
these files into the repository. The Python generator owns only PNG, JPEG,
WebP, GIF, PDF, DOCX, TXT, CSV, and ZIP. It may inventory the final eleven
files, but it must not import, create, parse, or validate XLSX/PPTX with
`openpyxl`, `python-pptx`, or any alternate Office authoring library.

For DOCX, select the installed `compact_reference_guide` preset and apply its
page, Normal, and Heading 1-3 tokens explicitly. This one-page fixture has no
title block, list, table, callout, running header, or running footer content, so
no header-template, numbering, or table-geometry role is introduced.

Create `$GENERATOR` with this complete content:

```python
from __future__ import annotations

import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor, Twips
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas


ROOT = Path(sys.argv[1])
MARKER = "Synthetic ChatGPT attachment transport smoke fixture"
MIME_TYPES = {
    "sample.png": "image/png",
    "sample.jpg": "image/jpeg",
    "sample.webp": "image/webp",
    "sample.gif": "image/gif",
    "sample.pdf": "application/pdf",
    "sample.docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "sample.xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "sample.pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "sample.txt": "text/plain",
    "sample.csv": "text/csv",
    "sample.zip": "application/zip",
}


def create_image(name: str, image_format: str) -> None:
    image = Image.new("RGB", (960, 180), "white")
    drawing = ImageDraw.Draw(image)
    drawing.text((24, 48), f"Attachment smoke: {name}", fill="black")
    drawing.text((24, 96), MARKER, fill="black")
    image.save(ROOT / name, format=image_format)


def configure_docx_style(
    document: Document,
    style_name: str,
    *,
    size: int,
    color: str,
    before: int,
    after: int,
    line_spacing: float | None,
) -> None:
    style = document.styles[style_name]
    style.font.name = "Calibri"
    style._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Calibri")
    style._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Calibri")
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor.from_string(color)
    style.paragraph_format.space_before = Pt(before)
    style.paragraph_format.space_after = Pt(after)
    if line_spacing is not None:
        style.paragraph_format.line_spacing = line_spacing


def create_docx() -> None:
    document = Document()
    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Twips(708)
    section.footer_distance = Twips(708)

    configure_docx_style(
        document,
        "Normal",
        size=11,
        color="000000",
        before=0,
        after=6,
        line_spacing=1.25,
    )
    configure_docx_style(
        document,
        "Heading 1",
        size=16,
        color="2E74B5",
        before=18,
        after=10,
        line_spacing=None,
    )
    configure_docx_style(
        document,
        "Heading 2",
        size=13,
        color="2E74B5",
        before=14,
        after=7,
        line_spacing=None,
    )
    configure_docx_style(
        document,
        "Heading 3",
        size=12,
        color="1F4D78",
        before=10,
        after=5,
        line_spacing=None,
    )
    document.add_heading("Attachment transport smoke", level=1)
    document.add_paragraph(MARKER)
    document.save(ROOT / "sample.docx")


def create_fixtures() -> None:
    ROOT.mkdir(parents=True, exist_ok=False)
    create_image("sample.png", "PNG")
    create_image("sample.jpg", "JPEG")
    create_image("sample.webp", "WEBP")
    create_image("sample.gif", "GIF")

    pdf_path = ROOT / "sample.pdf"
    canvas = Canvas(str(pdf_path), pagesize=letter)
    canvas.setTitle("Attachment transport smoke")
    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawString(72, 720, "Attachment transport smoke")
    canvas.setFont("Helvetica", 12)
    canvas.drawString(72, 684, MARKER)
    canvas.showPage()
    canvas.save()

    create_docx()

    (ROOT / "sample.txt").write_text(f"{MARKER}\n", encoding="utf-8")
    with (ROOT / "sample.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["kind", "marker"])
        writer.writerow(["csv", MARKER])

    with zipfile.ZipFile(ROOT / "sample.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README.txt", f"{MARKER}\n")


def validate_ordinary_fixtures() -> list[str]:
    expected_image_formats = {
        "sample.png": "PNG",
        "sample.jpg": "JPEG",
        "sample.webp": "WEBP",
        "sample.gif": "GIF",
    }
    for name, expected_format in expected_image_formats.items():
        with Image.open(ROOT / name) as image:
            image.verify()
            assert image.format == expected_format

    assert MARKER in (PdfReader(ROOT / "sample.pdf").pages[0].extract_text() or "")
    document = Document(ROOT / "sample.docx")
    assert MARKER in "\n".join(paragraph.text for paragraph in document.paragraphs)
    section = document.sections[0]
    assert section.page_width == Inches(8.5)
    assert section.page_height == Inches(11)
    assert section.top_margin == Inches(1)
    assert section.right_margin == Inches(1)
    assert section.bottom_margin == Inches(1)
    assert section.left_margin == Inches(1)
    assert section.header_distance == Twips(708)
    assert section.footer_distance == Twips(708)
    normal = document.styles["Normal"]
    assert normal.font.name == "Calibri"
    assert normal.font.size == Pt(11)
    assert str(normal.font.color.rgb) == "000000"
    assert normal.paragraph_format.space_before == Pt(0)
    assert normal.paragraph_format.space_after == Pt(6)
    assert normal.paragraph_format.line_spacing == 1.25
    expected_headings = {
        "Heading 1": (16, "2E74B5", 18, 10),
        "Heading 2": (13, "2E74B5", 14, 7),
        "Heading 3": (12, "1F4D78", 10, 5),
    }
    for name, (size, color, before, after) in expected_headings.items():
        style = document.styles[name]
        assert style.font.name == "Calibri"
        assert style.font.size == Pt(size)
        assert str(style.font.color.rgb) == color
        assert style.paragraph_format.space_before == Pt(before)
        assert style.paragraph_format.space_after == Pt(after)
    assert (ROOT / "sample.txt").read_text(encoding="utf-8").strip() == MARKER
    with (ROOT / "sample.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[1] == ["csv", MARKER]

    with zipfile.ZipFile(ROOT / "sample.zip") as archive:
        assert archive.namelist() == ["README.txt"]
        assert archive.testzip() is None
        entry = archive.getinfo("README.txt")
        assert not entry.filename.startswith("/")
        assert ".." not in Path(entry.filename).parts
        assert ((entry.external_attr >> 16) & 0o111) == 0
        assert archive.read("README.txt").decode("utf-8").strip() == MARKER

    ordinary_names = [
        name for name in MIME_TYPES if name not in {"sample.xlsx", "sample.pptx"}
    ]
    assert {path.name for path in ROOT.iterdir()} == set(ordinary_names)
    return ordinary_names


def build_manifest() -> list[dict[str, str | int]]:
    assert {path.name for path in ROOT.iterdir()} == set(MIME_TYPES)
    manifest: list[dict[str, str | int]] = []
    for name, mime_type in MIME_TYPES.items():
        path = ROOT / name
        payload = path.read_bytes()
        assert payload
        manifest.append(
            {
                "name": path.name,
                "mime_type": mime_type,
                "size": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    return manifest


if len(sys.argv) == 2:
    create_fixtures()
    print(json.dumps(validate_ordinary_fixtures(), indent=2))
elif len(sys.argv) == 3 and sys.argv[2] == "--manifest":
    print(json.dumps(build_manifest(), indent=2, sort_keys=True))
else:
    raise SystemExit(f"usage: {Path(sys.argv[0]).name} FIXTURE_ROOT [--manifest]")
```

Create `$BUILD_ROOT/xlsx/build-xlsx.mjs` with this complete content. This is a
small, styled fixture workbook rather than a business model, but it still uses
the spreadsheet skill's authoring, inspection, rendering, and export path:

```js
import fs from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import path from "node:path";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [fixtureRoot, qaRoot] = process.argv.slice(2).map((value) =>
  path.resolve(value),
);
if (!fixtureRoot || !qaRoot) {
  throw new Error("usage: build-xlsx.mjs FIXTURE_ROOT XLSX_QA_ROOT");
}

const marker = "Synthetic ChatGPT attachment transport smoke fixture";
const outputPath = path.join(fixtureRoot, "sample.xlsx");

async function assertMissing(targetPath) {
  try {
    await fs.access(targetPath);
  } catch (error) {
    if (error.code === "ENOENT") return;
    throw error;
  }
  throw new Error(`refusing to overwrite existing path: ${targetPath}`);
}

async function writeBlob(targetPath, blob) {
  await fs.writeFile(targetPath, new Uint8Array(await blob.arrayBuffer()));
}

await assertMissing(outputPath);
await assertMissing(qaRoot);
await fs.mkdir(qaRoot, { recursive: false });
const validatedExportPath = path.join(qaRoot, "sample.xlsx");

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Smoke");
sheet.showGridLines = false;
sheet.getRange("A1:B2").values = [
  ["Fixture", "Marker"],
  ["XLSX", marker],
];
sheet.getRange("A1:B1").format = {
  fill: "#0F766E",
  font: { bold: true, color: "#FFFFFF" },
};
sheet.getRange("A1:B2").format.borders = {
  preset: "outside",
  style: "thin",
  color: "#D9D9D9",
};
sheet.getRange("A1").format.columnWidth = 16;
sheet.getRange("B1").format.columnWidth = 56;

const structure = await workbook.inspect({
  kind: "sheet",
  include: "id,name",
  maxChars: 2000,
});
const content = await workbook.inspect({
  kind: "table",
  range: "Smoke!A1:B2",
  include: "values,formulas",
  tableMaxRows: 4,
  tableMaxCols: 4,
  maxChars: 4000,
});
if (!structure.ndjson.includes("Smoke")) {
  throw new Error("XLSX structure inspection did not find Smoke");
}
if (!content.ndjson.includes(marker)) {
  throw new Error("XLSX content inspection did not find the marker");
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(validatedExportPath);

const importedWorkbook = await SpreadsheetFile.importXlsx(
  await FileBlob.load(validatedExportPath),
);
const importedStructure = await importedWorkbook.inspect({
  kind: "sheet",
  include: "id,name",
  maxChars: 2000,
});
const importedContent = await importedWorkbook.inspect({
  kind: "table",
  range: "Smoke!A1:B2",
  include: "values,formulas",
  tableMaxRows: 4,
  tableMaxCols: 4,
  maxChars: 4000,
});
if (!importedStructure.ndjson.includes("Smoke")) {
  throw new Error("Exported XLSX structure inspection did not find Smoke");
}
if (!importedContent.ndjson.includes(marker)) {
  throw new Error("Exported XLSX content inspection did not find the marker");
}
await fs.writeFile(
  path.join(qaRoot, "xlsx-inspect.ndjson"),
  [
    "source workbook",
    structure.ndjson,
    content.ndjson,
    "re-imported exported workbook",
    importedStructure.ndjson,
    importedContent.ndjson,
    "",
  ].join("\n"),
  "utf8",
);

const preview = await importedWorkbook.render({
  sheetName: "Smoke",
  range: "A1:B2",
  autoCrop: "all",
  scale: 2,
  format: "png",
});
await writeBlob(path.join(qaRoot, "sample-xlsx.png"), preview);
await fs.copyFile(validatedExportPath, outputPath, fsConstants.COPYFILE_EXCL);

console.log(
  JSON.stringify({ outputPath, qaRoot, validatedExportPath, marker }, null, 2),
);
```

Create `$BUILD_ROOT/pptx/build-pptx.mjs` with this complete content. The
communication job is intentionally narrow: by the end, a smoke-test reviewer
should recognize this as a synthetic transport fixture because the marker is
prominent and unambiguous. With no user visual reference, adapt the installed
Codex Grid `slide-01.mjs` sparse stacked-text layout: preserve its 1280x720
canvas, `layers(...)`/`text(...)` Compose structure, three aligned text slots,
80px title, and 32px supporting text.

```js
import fs from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import path from "node:path";
import {
  FileBlob,
  layers,
  Presentation,
  PresentationFile,
  text,
} from "@oai/artifact-tool";

const [fixtureRoot, qaRoot] = process.argv.slice(2).map((value) =>
  path.resolve(value),
);
if (!fixtureRoot || !qaRoot) {
  throw new Error("usage: build-pptx.mjs FIXTURE_ROOT PPTX_QA_ROOT");
}

const marker = "Synthetic ChatGPT attachment transport smoke fixture";
const outputPath = path.join(fixtureRoot, "sample.pptx");

async function assertMissing(targetPath) {
  try {
    await fs.access(targetPath);
  } catch (error) {
    if (error.code === "ENOENT") return;
    throw error;
  }
  throw new Error(`refusing to overwrite existing path: ${targetPath}`);
}

async function writeBlob(targetPath, blob) {
  await fs.writeFile(targetPath, new Uint8Array(await blob.arrayBuffer()));
}

await assertMissing(outputPath);
await assertMissing(qaRoot);
await fs.mkdir(qaRoot, { recursive: false });
const validatedExportPath = path.join(qaRoot, "sample.pptx");

const presentation = Presentation.create({
  slideSize: { width: 1280, height: 720 },
});
const slide = presentation.slides.add();
slide.compose(
  layers(
    {
      name: "codex-grid-layout-library#slide-01-smoke-fixture",
      width: "fill",
      height: "fill",
    },
    [
      text(["Attachment transport smoke"], {
        name: "Fixture title",
        position: { left: 41.33, top: 182.55 },
        width: 992,
        height: 261.57,
        style: {
          fontSize: "80px",
          typeface: "Helvetica Neue",
          color: "#000000",
          alignment: "left",
          verticalAlignment: "bottom",
          autoFit: "none",
          insets: { top: 0, right: 0, bottom: 0, left: 0 },
        },
      }),
      text([marker], {
        name: "Fixture marker",
        position: { left: 41.33, top: 497.87 },
        width: 598.67,
        height: 113.41,
        style: {
          fontSize: "32px",
          typeface: "Helvetica Neue",
          color: "#000000",
          alignment: "left",
          autoFit: "none",
          insets: { top: 0, right: 0, bottom: 0, left: 0 },
        },
      }),
      text(["Synthetic attachment fixture"], {
        name: "Fixture supertitle",
        position: { left: 41.33, top: 41.18 },
        width: 598.67,
        height: 68.15,
        style: {
          fontSize: "32px",
          typeface: "Helvetica Neue",
          color: "#000000",
          alignment: "left",
          autoFit: "none",
          insets: { top: 0, right: 0, bottom: 0, left: 0 },
        },
      }),
    ],
  ),
  {
    frame: { left: 0, top: 0, width: 1280, height: 720 },
    baseUnit: 1,
  },
);

const inspection = await presentation.inspect({
  kind: "slide,textbox,shape,layout",
  maxChars: 6000,
});
if (!inspection.ndjson.includes(marker)) {
  throw new Error("PPTX content inspection did not find the marker");
}
const output = await PresentationFile.exportPptx(presentation);
await output.save(validatedExportPath);

const importedPresentation = await PresentationFile.importPptx(
  await FileBlob.load(validatedExportPath),
);
const importedInspection = await importedPresentation.inspect({
  kind: "slide,textbox,shape,layout",
  maxChars: 6000,
});
if (!importedInspection.ndjson.includes(marker)) {
  throw new Error("Exported PPTX inspection did not find the marker");
}
const importedSlide = importedPresentation.slides.items[0];
if (!importedSlide) {
  throw new Error("Exported PPTX did not contain a slide");
}
await fs.writeFile(
  path.join(qaRoot, "pptx-inspect.ndjson"),
  [
    "source presentation",
    inspection.ndjson,
    "re-imported exported presentation",
    importedInspection.ndjson,
    "",
  ].join("\n"),
  "utf8",
);
const layout = await importedSlide.export({ format: "layout" });
await fs.writeFile(
  path.join(qaRoot, "pptx-layout.json"),
  await layout.text(),
  "utf8",
);
const preview = await importedPresentation.export({
  slide: importedSlide,
  format: "png",
  scale: 2,
});
await writeBlob(path.join(qaRoot, "sample-pptx.png"), preview);
await fs.copyFile(validatedExportPath, outputPath, fsConstants.COPYFILE_EXCL);

console.log(
  JSON.stringify({ outputPath, qaRoot, validatedExportPath, marker }, null, 2),
);
```

Both builders deliberately save and re-import the Office file inside their QA
directory before copying it into the fixture root. Artifact-tool may create an
inspection sidecar next to an imported file; keeping that source under QA
preserves the exact eleven-file fixture inventory. Only after imported marker
inspection and final rendering pass may `COPYFILE_EXCL` copy the validated
Office bytes to `sample.xlsx` or `sample.pptx`; it must never overwrite an
existing fixture.

- [ ] **Step 3: Generate and locally validate all eleven fixtures**

Run:

```bash
set -euo pipefail
: "${BUNDLED_PYTHON:?workspace dependency loader did not return bundled Python}"
: "${BUNDLED_NODE:?workspace dependency loader did not return bundled Node}"
RUN_SUFFIX="${RUN_SUFFIX:-20260713}"
GENERATOR="/tmp/chatgpt-multi-format-generate-${RUN_SUFFIX}.py"
BUILD_ROOT="/tmp/chatgpt-multi-format-artifact-workspace-${RUN_SUFFIX}"
FIXTURE_ROOT="/tmp/chatgpt-multi-format-smoke-${RUN_SUFFIX}"
QA_ROOT="/tmp/chatgpt-multi-format-qa-${RUN_SUFFIX}"
VALIDATED_ROOT_FILE="/tmp/chatgpt-multi-format-validated-root-${RUN_SUFFIX}.txt"
test -x "$BUNDLED_PYTHON"
test -x "$BUNDLED_NODE"
test -f "$GENERATOR"
test -d "$BUILD_ROOT/xlsx"
test -d "$BUILD_ROOT/pptx"
test ! -e "$FIXTURE_ROOT"
test ! -e "$QA_ROOT"
test ! -e "$VALIDATED_ROOT_FILE"
test ! -L "$VALIDATED_ROOT_FILE"
"$BUNDLED_NODE" --check "$BUILD_ROOT/xlsx/build-xlsx.mjs"
"$BUNDLED_NODE" --check "$BUILD_ROOT/pptx/build-pptx.mjs"
"$BUNDLED_PYTHON" "$GENERATOR" "$FIXTURE_ROOT"
mkdir "$QA_ROOT"
(cd "$BUILD_ROOT/xlsx" && "$BUNDLED_NODE" build-xlsx.mjs \
  "$FIXTURE_ROOT" "$QA_ROOT/xlsx")
(cd "$BUILD_ROOT/pptx" && "$BUNDLED_NODE" build-pptx.mjs \
  "$FIXTURE_ROOT" "$QA_ROOT/pptx")
"$BUNDLED_PYTHON" "$GENERATOR" "$FIXTURE_ROOT" --manifest
file "$FIXTURE_ROOT"/*
unzip -l "$FIXTURE_ROOT/sample.zip"
unzip -t "$FIXTURE_ROOT/sample.zip"
```

Expected: the Python generator validates its nine owned formats; both
artifact-tool builders pass Node syntax checks, inspect their source marker
content, export real Office files under QA, re-import those saved files, find
the marker again, render the final non-empty previews from the re-imported
artifacts, and exclusively copy the validated bytes into the fixture root; the
final generator invocation prints exactly eleven manifest entries in the
approved order with MIME, non-zero size, and SHA-256; `file` recognizes every
real format; and the ZIP contains only safe `README.txt` and passes its
integrity test.

Run the format-specific render gates:

```bash
set -euo pipefail
: "${BUNDLED_PYTHON:?workspace dependency loader did not return bundled Python}"
: "${BUNDLED_BIN:?workspace dependency loader did not return bundled executables}"
: "${DOCUMENTS_SKILL_DIR:?loaded documents skill directory is required}"
: "${PRESENTATIONS_SKILL_DIR:?loaded presentations skill directory is required}"
unset FONTCONFIG_FILE FONTCONFIG_PATH
RUN_SUFFIX="${RUN_SUFFIX:-20260713}"
FIXTURE_ROOT="/tmp/chatgpt-multi-format-smoke-${RUN_SUFFIX}"
QA_ROOT="/tmp/chatgpt-multi-format-qa-${RUN_SUFFIX}"
VALIDATED_ROOT_FILE="/tmp/chatgpt-multi-format-validated-root-${RUN_SUFFIX}.txt"
PPTX_OVERFLOW_OUTPUT="$QA_ROOT/pptx/slides-test.txt"
PDF_RENDER_LOG="$QA_ROOT/pdf/pdftoppm.log"
BUNDLED_RUNTIME_ROOT="$(cd "$BUNDLED_BIN/../.." && pwd -P)"
PDFTOPPM="$BUNDLED_BIN/pdftoppm"
test -x "$BUNDLED_PYTHON"
test -d "$BUNDLED_BIN"
test -d "$BUNDLED_RUNTIME_ROOT/native/poppler"
test -x "$PDFTOPPM"
test -f "$DOCUMENTS_SKILL_DIR/render_docx.py"
test -f "$PRESENTATIONS_SKILL_DIR/container_tools/slides_test.py"
test -d "$FIXTURE_ROOT"
test -d "$QA_ROOT/xlsx"
test -d "$QA_ROOT/pptx"
test ! -e "$QA_ROOT/docx"
test ! -e "$QA_ROOT/pdf"
test ! -e "$PPTX_OVERFLOW_OUTPUT"
test ! -e "$PDF_RENDER_LOG"
test ! -e "$VALIDATED_ROOT_FILE"
test ! -L "$VALIDATED_ROOT_FILE"
FONTCONFIG_OUTPUT="$(
  find "$BUNDLED_RUNTIME_ROOT/native/poppler" \
    -type f -path '*/etc/fonts/fonts.conf' -print
)" || exit 1
test -n "$FONTCONFIG_OUTPUT"
test "$(printf '%s\n' "$FONTCONFIG_OUTPUT" | wc -l | tr -d ' ')" = "1"
FONTCONFIG_FILE="$FONTCONFIG_OUTPUT"
test -f "$FONTCONFIG_FILE"
test -r "$FONTCONFIG_FILE"
mkdir "$QA_ROOT/docx" "$QA_ROOT/pdf"
"$BUNDLED_PYTHON" "$DOCUMENTS_SKILL_DIR/render_docx.py" \
  "$FIXTURE_ROOT/sample.docx" --output_dir "$QA_ROOT/docx"
FONTCONFIG_FILE="$FONTCONFIG_FILE" \
  "$PDFTOPPM" -png "$FIXTURE_ROOT/sample.pdf" "$QA_ROOT/pdf/sample" \
  2>&1 | tee "$PDF_RENDER_LOG"
test ! -s "$PDF_RENDER_LOG"
"$BUNDLED_PYTHON" "$PRESENTATIONS_SKILL_DIR/container_tools/slides_test.py" \
  "$FIXTURE_ROOT/sample.pptx" 2>&1 | tee "$PPTX_OVERFLOW_OUTPUT"
if grep -Fq "ERROR:" "$PPTX_OVERFLOW_OUTPUT"; then
  exit 1
fi
grep -Fxq "Test passed. No overflow detected." "$PPTX_OVERFLOW_OUTPUT"
test -s "$QA_ROOT/docx/page-1.png"
test -s "$QA_ROOT/pdf/sample-1.png"
test -s "$QA_ROOT/xlsx/sample.xlsx"
test -s "$QA_ROOT/xlsx/sample-xlsx.png"
test -s "$QA_ROOT/pptx/sample.pptx"
test -s "$QA_ROOT/pptx/sample-pptx.png"
test -s "$QA_ROOT/xlsx/xlsx-inspect.ndjson"
test -s "$QA_ROOT/pptx/pptx-inspect.ndjson"
test -s "$QA_ROOT/pptx/pptx-layout.json"
cmp "$QA_ROOT/xlsx/sample.xlsx" "$FIXTURE_ROOT/sample.xlsx"
cmp "$QA_ROOT/pptx/sample.pptx" "$FIXTURE_ROOT/sample.pptx"
```

Expected: the displayed and captured slide-test output contains the exact line
`Test passed. No overflow detected.` and contains no `ERROR:` record. Either a
missing success line or any error record fails the gate even if the helper
process exits zero. The displayed and captured `pdftoppm` output is exactly
empty. Any Fontconfig warning, other warning, or error is a render-gate failure;
an output PNG alone is not sufficient. Ambient Fontconfig variables are cleared;
the discovered `FONTCONFIG_FILE` remains unexported and is supplied only to the
bundled `pdftoppm` command.

Run this one-time Poppler pressure scenario outside the primary QA root to
prove the environment requirement. These pressure outputs are evidence only
and must never become browser fixtures:

```bash
set -euo pipefail
: "${BUNDLED_BIN:?workspace dependency loader did not return bundled executables}"
unset FONTCONFIG_FILE FONTCONFIG_PATH
RUN_SUFFIX="${RUN_SUFFIX:-20260713}"
FIXTURE_ROOT="/tmp/chatgpt-multi-format-smoke-${RUN_SUFFIX}"
POPLER_PRESSURE_ROOT="/tmp/chatgpt-multi-format-poppler-pressure-${RUN_SUFFIX}"
NO_ENV_ROOT="$POPLER_PRESSURE_ROOT/no-env"
CONFIGURED_ROOT="$POPLER_PRESSURE_ROOT/configured"
NO_ENV_LOG="$NO_ENV_ROOT/pdftoppm.log"
CONFIGURED_LOG="$CONFIGURED_ROOT/pdftoppm.log"
BUNDLED_RUNTIME_ROOT="$(cd "$BUNDLED_BIN/../.." && pwd -P)"
PDFTOPPM="$BUNDLED_BIN/pdftoppm"
test -d "$BUNDLED_BIN"
test -d "$BUNDLED_RUNTIME_ROOT/native/poppler"
test -x "$PDFTOPPM"
test -f "$FIXTURE_ROOT/sample.pdf"
test ! -e "$POPLER_PRESSURE_ROOT"
FONTCONFIG_OUTPUT="$(
  find "$BUNDLED_RUNTIME_ROOT/native/poppler" \
    -type f -path '*/etc/fonts/fonts.conf' -print
)" || exit 1
test -n "$FONTCONFIG_OUTPUT"
test "$(printf '%s\n' "$FONTCONFIG_OUTPUT" | wc -l | tr -d ' ')" = "1"
FONTCONFIG_FILE="$FONTCONFIG_OUTPUT"
test -f "$FONTCONFIG_FILE"
test -r "$FONTCONFIG_FILE"
mkdir "$POPLER_PRESSURE_ROOT" "$NO_ENV_ROOT" "$CONFIGURED_ROOT"
env -u FONTCONFIG_FILE -u FONTCONFIG_PATH \
  "$PDFTOPPM" -png "$FIXTURE_ROOT/sample.pdf" "$NO_ENV_ROOT/sample" \
  2>&1 | tee "$NO_ENV_LOG"
grep -Fxq \
  "Fontconfig error: Cannot load default config file: File not found" \
  "$NO_ENV_LOG"
test "$(wc -l < "$NO_ENV_LOG" | tr -d ' ')" = "1"
FONTCONFIG_FILE="$FONTCONFIG_FILE" \
  "$PDFTOPPM" -png "$FIXTURE_ROOT/sample.pdf" "$CONFIGURED_ROOT/sample" \
  2>&1 | tee "$CONFIGURED_LOG"
test ! -s "$CONFIGURED_LOG"
test -s "$NO_ENV_ROOT/sample-1.png"
test -s "$CONFIGURED_ROOT/sample-1.png"
cmp "$NO_ENV_ROOT/sample-1.png" "$CONFIGURED_ROOT/sample-1.png"
```

Expected: the no-environment path is RED with exactly the one Fontconfig line
above; the dynamically discovered config path is GREEN with pristine empty
output; and `cmp` proves the two rendered PNGs are byte-identical. Preserve the
fresh pressure root through final reporting without copying it into the primary
QA or fixture roots.

Use the host image-viewing capability at 100% zoom on all four render outputs:

- `$QA_ROOT/docx/page-1.png`
- `$QA_ROOT/pdf/sample-1.png`
- `$QA_ROOT/xlsx/sample-xlsx.png`
- `$QA_ROOT/pptx/sample-pptx.png`

Also read the compact XLSX inspection, PPTX inspection, and PPTX layout JSON.
The final XLSX preview, PPTX preview, and PPTX layout must come from the
re-imported saved artifacts, not only their source in-memory objects.
The DOCX page must show its heading and full marker without clipping; the PDF
must show its title and marker with clean margins; the spreadsheet must show
both cells, full marker text, and legible styling; the slide must preserve the
selected Codex Grid hierarchy, show the full 80px title and 32px marker, and
contain no overlap, overflow, out-of-bounds content, or ignored layout warning.
Any visual or layout defect is a failure. Stop and report it without creating
another fixture set in this approved run. Do not overwrite or delete the failed
evidence, and do not use a different authoring library as a fallback. If Hun
separately approves a new generation run, choose a single new suffix and apply
it through the same explicit `RUN_SUFFIX` value on every standalone shell
block, deriving fresh build, fixture, and QA roots together before doing any
work. Do not override those roots independently. Leave the validated-root file
absent until that new root passes every gate.

Only after the render, image, inspection, and layout gates above all pass, run:

```bash
set -euo pipefail
: "${BUNDLED_NODE:?workspace dependency loader did not return bundled Node}"
RUN_SUFFIX="${RUN_SUFFIX:-20260713}"
FIXTURE_ROOT="/tmp/chatgpt-multi-format-smoke-${RUN_SUFFIX}"
QA_ROOT="/tmp/chatgpt-multi-format-qa-${RUN_SUFFIX}"
VALIDATED_ROOT_FILE="/tmp/chatgpt-multi-format-validated-root-${RUN_SUFFIX}.txt"
test -x "$BUNDLED_NODE"
test -d "$FIXTURE_ROOT"
test -d "$QA_ROOT"
VALIDATED_FIXTURE_ROOT="$FIXTURE_ROOT"
"$BUNDLED_NODE" -e '
  const { writeFileSync } = require("node:fs");
  const [pointerPath, validatedRoot] = process.argv.slice(1);
  writeFileSync(pointerPath, `${validatedRoot}\n`, {
    flag: "wx",
    mode: 0o600,
  });
' "$VALIDATED_ROOT_FILE" "$VALIDATED_FIXTURE_ROOT"
"$BUNDLED_NODE" -e '
  const { readFileSync, statSync } = require("node:fs");
  const [pointerPath, validatedRoot] = process.argv.slice(1);
  if (readFileSync(pointerPath, "utf8") !== `${validatedRoot}\n`) {
    throw new Error("validated-root pointer content mismatch");
  }
  if ((statSync(pointerPath).mode & 0o777) !== 0o600) {
    throw new Error("validated-root pointer mode is not 0600");
  }
' "$VALIDATED_ROOT_FILE" "$VALIDATED_FIXTURE_ROOT"
```

This is the only step that defines `VALIDATED_FIXTURE_ROOT`. If it does not
complete, browser staging must not begin.

Keep the fixture, build, and QA directories until final reporting. They are
disposable and synthetic, but do not delete them automatically, copy them into
Git, or commit any binary output.

- [ ] **Step 4: Establish a fresh Chrome staging surface**

Invoke the Chrome control skill, initialize the extension-backed browser with
the documented browser-client route, and read the complete selected-browser
documentation plus `file-uploads` documentation. Use a Codex-owned ChatGPT tab
or a new clean composer, and do not reuse the stale chooser from before the
permission change. Define the exact fixture inventory in the JavaScript browser
session by reading the exact root serialized after Step 3. Never substitute a
default fixture path:

```js
const {
  readFileSync: readValidatedRootFileSync,
  readdirSync,
  statSync,
} = await import("node:fs");
const { isAbsolute } = await import("node:path");
const validatedRunSuffix = "20260713";
const validatedRootFile =
  `/tmp/chatgpt-multi-format-validated-root-${validatedRunSuffix}.txt`;
const serializedRoot = readValidatedRootFileSync(validatedRootFile, "utf8");
const rootLines = serializedRoot.trim().split(/\r?\n/);
if (rootLines.length !== 1 || !isAbsolute(rootLines[0])) {
  throw new Error("validated fixture root is missing or ambiguous");
}
const fixtureRoot = rootLines[0];
if (!statSync(fixtureRoot).isDirectory()) {
  throw new Error("validated fixture root is not a directory");
}
const fixtures = [
  { format: "PNG", name: "sample.png", mimeType: "image/png" },
  { format: "JPEG/JPG", name: "sample.jpg", mimeType: "image/jpeg" },
  { format: "WebP", name: "sample.webp", mimeType: "image/webp" },
  { format: "GIF", name: "sample.gif", mimeType: "image/gif" },
  { format: "PDF", name: "sample.pdf", mimeType: "application/pdf" },
  { format: "DOCX", name: "sample.docx", mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" },
  { format: "XLSX", name: "sample.xlsx", mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" },
  { format: "PPTX", name: "sample.pptx", mimeType: "application/vnd.openxmlformats-officedocument.presentationml.presentation" },
  { format: "TXT", name: "sample.txt", mimeType: "text/plain" },
  { format: "CSV", name: "sample.csv", mimeType: "text/csv" },
  { format: "ZIP", name: "sample.zip", mimeType: "application/zip" },
].map((fixture) => ({
  ...fixture,
  path: `${fixtureRoot}/${fixture.name}`,
}));
const expectedFixtureNames = fixtures.map(({ name }) => name).sort();
const actualFixtureNames = readdirSync(fixtureRoot).sort();
if (JSON.stringify(actualFixtureNames) !== JSON.stringify(expectedFixtureNames)) {
  throw new Error("validated fixture root does not contain the exact inventory");
}
```

`validatedRunSuffix` must equal the exact `RUN_SUFFIX` used by every successful
shell block in this run. The shown value is for the initially approved run. If
Hun separately approves a suffixed run, explicitly substitute that same suffix
before executing this browser block; never reuse `20260713` as a fallback.

Confirm all of the following before the first fixture:

- the URL and title identify ChatGPT;
- the logged-in session and intended Pro conversation surface are visible;
- there is no prompt text, attachment preview, error, or pending state;
- the test will stop at staging and will never click Send.

If the tab is not clean, use a fresh composer. Do not borrow an arbitrary user
conversation and do not inspect cookies, profiles, local storage, or auth data.
Composer staging is an external-account write and may consume upload quota or
leave a synthetic file in ChatGPT Library even without a sent message. Hun's
approved design authorizes only these eleven synthetic fixtures, one direct and
one clipboard attempt per format. Do not retry or broaden the packet without a
new approval. If ChatGPT shows a quota, Library, retention, or account warning,
stop and report it. Do not delete Library items without separate approval.

- [ ] **Step 5: Test direct chooser staging one file at a time**

For each fixture in this exact order — PNG, JPEG/JPG, WebP, GIF, PDF, DOCX,
XLSX, PPTX, TXT, CSV, ZIP — start the file chooser wait before activating the
attachment input, assert `chooser.isMultiple()` is boolean, and await
`chooser.setFiles(currentFixture.path)`.

For each inventory entry, assign it in order with
`let currentFixture = fixtures[0]` for the first attempt and
`currentFixture = fixtures[index]` for each later index, then run this exact
chooser sequence:

```js
const chooserPromise = tab.playwright.waitForEvent("filechooser", {
  timeoutMs: 10000,
});
await tab.playwright.locator('input[type="file"]').click();
const chooser = await chooserPromise;
const chooserAllowsMultiple = chooser.isMultiple();
if (typeof chooserAllowsMultiple !== "boolean") {
  throw new Error("chooser.isMultiple() did not return boolean");
}
await chooser.setFiles(currentFixture.path);
```

Classify the direct attempt with this exact rule:

```text
verified-staging:
  setFiles fulfilled AND exactly one new expected preview is visible
  AND no visible error or pending state remains

unsupported-in-current-smoke:
  setFiles rejected OR the expected preview is missing/ambiguous
  OR an error/pending state remains
```

Record format, MIME, API fulfillment/rejection, exact rejection text when any,
preview result, visible error/pending state, and cleanup result. If the fresh
attempt still rejects with `Not allowed`, preserve the error and continue the
evidence matrix without claiming that permission is disabled or was the sole
cause.

Remove only the current fixture's preview when its remove control is
unambiguous. Otherwise close that Codex-owned test tab and open a new clean
composer before continuing. Never send.

- [ ] **Step 6: Probe clipboard staging one format/MIME pair at a time**

For each of the eleven fixtures, read its bytes inside the JavaScript browser
session and use the exact MIME from the generator's `MIME_TYPES` mapping:

```js
const { readFileSync } = await import("node:fs");
const encodedBytes = readFileSync(currentFixture.path).toString("base64");
await tab.clipboard.write([
  {
    entries: [{ base64: encodedBytes, mimeType: currentFixture.mimeType }],
  },
]);
await tab.cua.keypress({ keys: ["ControlOrMeta", "v"] });
```

Await the clipboard write before paste. Classify with this exact rule:

```text
verified-staging:
  clipboard.write fulfilled AND paste created exactly one new attachment preview
  AND no visible error or pending state remains

unsupported-in-current-smoke:
  clipboard.write rejected OR paste produced text/no preview/ambiguous preview
  OR an error/pending state remains
```

API fulfillment alone is not success. Record the generated preview name when
visible. Clean up or replace the composer using the same unambiguous-only rule
as direct staging. Never send.

- [ ] **Step 7: Freeze the evidence matrix for implementation**

Keep the eleven rows in the specified order. Use these exact labels:

- `verified-staging` only when the transport's complete staging rule passed;
- `unsupported-in-current-smoke` for every attempted transport that did not;
- `user-verified` only for ZIP direct attachment if the current direct attempt
  fails, preserving Hun's prior real-use evidence without pretending this
  smoke passed;
- `not-tested` only if an external blocker prevented an attempt from starting.

The PNG clipboard evidence cell must retain `Six previews staged previously`
and append the fresh attempt result. The ZIP direct evidence cell must retain
`Hun-confirmed` and append the fresh attempt result. Do not generalize from one
format to another.

### Task 3: Implement The Minimal Repository Skill Change And Reach GREEN

**Files:**
- Modify: `skills/chatgpt-collaboration-harness/SKILL.md:21-24`
- Modify: `skills/chatgpt-collaboration-harness/references/chrome-chatgpt-pro.md:47-62`
- Modify: `skills/chatgpt-collaboration-harness/references/file-artifact-exchange.md:26-82`
- Test: `tests/test_skill_catalog.py`

- [ ] **Step 1: Broaden only the router noun**

Change the Required Components bullet to:

```markdown
- When Chrome file upload fails or approved files need a clipboard fallback,
  read both `references/chrome-chatgpt-pro.md` and
  `references/file-artifact-exchange.md` before retrying, changing permissions,
  pasting, or reporting a blocker.
```

Do not add the format matrix or transport procedure to `SKILL.md`.

- [ ] **Step 2: Route Chrome diagnosis into the evidence-qualified transport**

Keep the existing conditional permission diagnosis intact. Replace only the
final approved-image/non-image paragraph in `File Upload Diagnosis` with:

```markdown
For approved files, use the Direct-First Attachment Transport in
`file-artifact-exchange.md`. Use clipboard only when the capability matrix
marks that exact format/MIME pair as `verified-staging`; otherwise require
manual attachment.
```

Do not weaken the fresh-task retry, action-time confirmation, user-directed
permission, blocked-`chrome://`, or sole-cause rules.

- [ ] **Step 3: Replace the PNG-only section with the capability matrix**

Replace `## Verified Clipboard Image Fallback` through the line before
`## Attachment Packet` with three parts in this order:

1. `## Attachment Transport Capability Matrix`
2. `## Direct-First Attachment Transport`
3. `### Verified Clipboard Attachment Fallback`

The matrix columns must be exactly:

```markdown
| Format | MIME type | Direct chooser | Clipboard | Evidence |
| --- | --- | --- | --- | --- |
```

Write exactly eleven rows in the format order from Task 2. Use these MIME
values without aliases:

```text
PNG       image/png
JPEG/JPG  image/jpeg
WebP      image/webp
GIF       image/gif
PDF       application/pdf
DOCX      application/vnd.openxmlformats-officedocument.wordprocessingml.document
XLSX      application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
PPTX      application/vnd.openxmlformats-officedocument.presentationml.presentation
TXT       text/plain
CSV       text/csv
ZIP       application/zip
```

Derive each status deterministically from Task 2's frozen evidence:

```text
if the attempted transport passed its full staging rule:
    write `verified-staging`
else if the attempted transport ran and did not pass:
    write `unsupported-in-current-smoke`
else:
    write `not-tested`

ZIP direct exception:
    if current direct staging did not pass, write `user-verified`
    and state the current failure or blocker in Evidence
```

After the table, define all four labels and state that product support, API
acceptance, a clipboard write, and a user report are distinct evidence levels.
Retain `Six previews staged previously` in the PNG evidence cell and
`Hun-confirmed` in the ZIP evidence cell.

- [ ] **Step 4: Document the direct-first decision flow**

Use this procedure, preserving the wording required by the RED tests:

```markdown
## Direct-First Attachment Transport

Reuse the approved attachment-sharing scope; changing transport does not
authorize more files or a different ChatGPT destination. Try the documented
file chooser first for every approved file.

1. Confirm the destination, file count, order, intended use, MIME type, and
   non-sensitive alias. Never place an absolute path in the attachment manifest.
2. Establish a clean packet baseline: no attachment previews, error or pending
   state, or unapproved text. Existing text must be the exact approved prompt.
3. Follow `File Upload Diagnosis` and await `chooser.setFiles(...)`.
4. Treat direct staging as verified only when the call fulfills, the expected
   preview count and visible names are unambiguous, and no error or pending
   state remains.
5. If direct staging fails, consult the capability matrix. Use clipboard only
   when that exact format/MIME pair is `verified-staging` for clipboard.
6. Otherwise stop and require manual attachment. Do not convert, unpack, rename,
   partially send, or claim that another format's result applies.

Composer previews prove staging, not byte identity, persistence, model
readability, or delivery.
```

- [ ] **Step 5: Document the qualified clipboard fallback**

Use this exact API ordering and qualification contract:

```markdown
### Verified Clipboard Attachment Fallback

Use this only after direct staging is unavailable and the capability matrix
marks the exact format/MIME pair as `verified-staging`. API success alone is
not attachment evidence. Do not promote a format unless both the clipboard
write and a visible attachment preview passed the smoke contract.

1. Record the manifest index, intended order and count, exact MIME type, and
   non-sensitive alias.
2. Read one file's bytes and Base64-encode them. For the already verified PNG
   example, the documented payload is:

   ```js
   const verifiedMimeType = "image/png";
   await tab.clipboard.write([
     {
       entries: [{ base64: encodedBytes, mimeType: verifiedMimeType }],
     },
   ]);
   ```

   For another format, substitute only the exact MIME value from a clipboard
   row marked `verified-staging`. Await the write and stop before paste if it
   rejects or throws.
3. Focus the verified ChatGPT composer and paste:

   ```js
   await tab.cua.keypress({ keys: ["ControlOrMeta", "v"] });
   ```

4. Paste one file at a time. Require the preview count to increase by exactly
   one and require no error, pending state, or ambiguous duplicate.
5. Before sending in an authorized delivery stage, verify the exact packet:
   approved prompt, expected preview count and order, no unexpected content,
   and no error or pending state. This browser smoke is not authorized to send.
6. On failure, do not send a partial packet. Remove only unambiguous draft
   attachments from the current attempt; otherwise leave a handoff and report
   the exact state.
7. When delivery is separately authorized, verify the persisted outgoing
   message. Composer previews prove staging, not delivery.

Clipboard paste may expose generated names. Use non-sensitive aliases by
default and an original basename only when separately approved.
```

- [ ] **Step 6: Run GREEN and the focused negative checks**

Run:

```bash
set -euo pipefail
python3 -m unittest discover -s tests -p 'test_skill_catalog.py' -v
git diff --check
python3 scripts/check_private_paths.py
```

Expected: all skill-catalog tests pass, the private-path scan reports `ok`, and
`git diff --check` emits no output. Test output must contain no unexpected
warnings or errors.

- [ ] **Step 7: Review and commit the repository skill**

Inspect the diff for invented browser APIs, unsupported MIME promotion,
duplicated safety prose, absolute private paths, unrelated formatting, and any
claim stronger than composer staging. Confirm the source files match Task 2's
frozen evidence, then run:

```bash
set -euo pipefail
git status --short
git add skills/chatgpt-collaboration-harness/SKILL.md \
  skills/chatgpt-collaboration-harness/references/chrome-chatgpt-pro.md \
  skills/chatgpt-collaboration-harness/references/file-artifact-exchange.md
git commit -m "feat: support evidence-based file attachment fallback"
```

Expected: one skill implementation commit with hooks preserved.

### Task 4: Validate The Repository And Synchronize The Runtime Skill

**Files:**
- Source: `skills/chatgpt-collaboration-harness/`
- Synchronize: `~/.codex/skills/chatgpt-collaboration-harness/`

- [ ] **Step 1: Run the complete repository verification stack**

Run:

```bash
set -euo pipefail
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_private_paths.py
python3 scripts/audit_agent_stack.py
git diff --check
```

Expected: the full test count is at least the 288-test design baseline plus the
net new contract test, both scripts pass with pristine output, and the diff
check emits nothing. Any failure is in scope and must be resolved before sync.

- [ ] **Step 2: Preserve the stopped RED evidence and create a fresh validator**

The previous checksum dry run is intentionally stopped evidence. Explicitly
preserve the stopped validator and its snapshots as RED evidence: do not delete, overwrite,
rename, or reuse `/tmp/chatgpt-multi-format-validator-20260713`. Create a new,
collision-checked content-only validator root and record the old snapshot hash:

```bash
set -euo pipefail
set -C
OLD_VALIDATOR_ROOT="/tmp/chatgpt-multi-format-validator-20260713"
FAILED_VALIDATOR_ROOT="/tmp/chatgpt-multi-format-validator-20260713-content-only"
VALIDATOR_ROOT="/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe"
test -d "$OLD_VALIDATOR_ROOT"
test -s "$OLD_VALIDATOR_ROOT/runtime-dry-run-1.txt"
test -d "$FAILED_VALIDATOR_ROOT"
test -f "$FAILED_VALIDATOR_ROOT/runtime-raw-dry-run-1.txt"
test ! -s "$FAILED_VALIDATOR_ROOT/runtime-raw-dry-run-1.txt"
test ! -e "$VALIDATOR_ROOT"
mkdir -m 700 "$VALIDATOR_ROOT"
test ! -e "$VALIDATOR_ROOT/old-red-snapshot.sha256"
shasum -a 256 "$OLD_VALIDATOR_ROOT/runtime-dry-run-1.txt" \
  > "$VALIDATOR_ROOT/old-red-snapshot.sha256"
shasum -a 256 "$FAILED_VALIDATOR_ROOT/runtime-raw-dry-run-1.txt" \
  > "$VALIDATOR_ROOT/failed-path-raw.sha256"
python3 -m venv "$VALIDATOR_ROOT/venv"
"$VALIDATOR_ROOT/venv/bin/python" -m pip install PyYAML
```

Expected: the new environment is isolated, PyYAML is installed only in its
venv, and both prior validators remain untouched. Explicitly preserve the failed content-only validator and its zero-byte raw evidence.

- [ ] **Step 3: Create the independent manifest and rsync-review tools**

Use `apply_patch` to create
`/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe/compare_skill_trees.py`
with this complete content:

```python
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from typing import Any


ALLOWED_CONTENT_DIFFERENCES = {
    "SKILL.md",
    "references/chrome-chatgpt-pro.md",
    "references/file-artifact-exchange.md",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def regular_digest(path: str, expected: os.stat_result) -> tuple[int, str]:
    if not hasattr(os, "O_NOFOLLOW"):
        fail("O_NOFOLLOW is required to hash regular files safely")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            fail(f"regular file changed type while opening: {path}")
        expected_identity = (
            expected.st_dev,
            expected.st_ino,
            expected.st_size,
            stat.S_IMODE(expected.st_mode),
            expected.st_mtime_ns,
            expected.st_ctime_ns,
        )
        opened_identity = (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            stat.S_IMODE(opened.st_mode),
            opened.st_mtime_ns,
            opened.st_ctime_ns,
        )
        if opened_identity != expected_identity:
            fail(f"regular file changed identity while opening: {path}")
        digest = hashlib.sha256()
        size = 0
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
        finished = os.fstat(descriptor)
        finished_identity = (
            finished.st_dev,
            finished.st_ino,
            finished.st_size,
            stat.S_IMODE(finished.st_mode),
            finished.st_mtime_ns,
            finished.st_ctime_ns,
        )
        if finished_identity != opened_identity:
            fail(f"regular file changed while hashing: {path}")
        return size, digest.hexdigest()
    finally:
        os.close(descriptor)


def describe(path: str, relative_path: str) -> dict[str, Any]:
    metadata = os.lstat(path)
    record: dict[str, Any] = {
        "path": relative_path,
        "mode": f"{stat.S_IMODE(metadata.st_mode):04o}",
    }
    if stat.S_ISDIR(metadata.st_mode):
        record["type"] = "directory"
    elif stat.S_ISREG(metadata.st_mode):
        size, digest = regular_digest(path, metadata)
        record.update(type="regular", size=size, sha256=digest)
    elif stat.S_ISLNK(metadata.st_mode):
        record.update(type="symlink", target=os.readlink(path))
    else:
        fail(f"special files are forbidden: {relative_path}")
    return record


def inventory(root: str) -> dict[str, dict[str, Any]]:
    root = os.path.abspath(root)
    root_metadata = os.lstat(root)
    if not stat.S_ISDIR(root_metadata.st_mode):
        fail(f"tree root must be a real directory: {root}")

    entries = {".": describe(root, ".")}

    def walk_error(error: OSError) -> None:
        raise error

    for current, dirnames, filenames in os.walk(
        root,
        topdown=True,
        onerror=walk_error,
        followlinks=False,
    ):
        dirnames.sort()
        filenames.sort()
        for name in [*dirnames, *filenames]:
            full_path = os.path.join(current, name)
            relative_path = os.path.relpath(full_path, root).replace(os.sep, "/")
            if relative_path in entries:
                fail(f"duplicate relative path: {relative_path}")
            entries[relative_path] = describe(full_path, relative_path)
        dirnames[:] = [
            name
            for name in dirnames
            if not stat.S_ISLNK(os.lstat(os.path.join(current, name)).st_mode)
        ]
    return dict(sorted(entries.items()))


def write_manifest(path: str, entries: dict[str, dict[str, Any]]) -> None:
    with open(path, "x", encoding="utf-8") as output:
        json.dump(entries, output, indent=2, sort_keys=True)
        output.write("\n")


def compare(
    source: dict[str, dict[str, Any]],
    runtime: dict[str, dict[str, Any]],
    phase: str,
) -> None:
    source_paths = set(source)
    runtime_paths = set(runtime)
    if source_paths != runtime_paths:
        fail(
            "exact relative path set differs: "
            f"source_only={sorted(source_paths - runtime_paths)!r}, "
            f"runtime_only={sorted(runtime_paths - source_paths)!r}"
        )

    content_differences: set[str] = set()
    for relative_path in sorted(source):
        source_entry = source[relative_path]
        runtime_entry = runtime[relative_path]
        if source_entry["type"] != runtime_entry["type"]:
            fail(f"type differs at {relative_path}")
        if source_entry["mode"] != runtime_entry["mode"]:
            fail(f"mode differs at {relative_path}")
        if source_entry["type"] == "symlink":
            if source_entry["target"] != runtime_entry["target"]:
                fail(f"symlink target differs at {relative_path}")
        elif source_entry["type"] == "regular":
            source_content = (source_entry["size"], source_entry["sha256"])
            runtime_content = (runtime_entry["size"], runtime_entry["sha256"])
            if source_content != runtime_content:
                content_differences.add(relative_path)

    if phase == "capture":
        return
    expected = ALLOWED_CONTENT_DIFFERENCES if phase == "pre" else set()
    if content_differences != expected:
        fail(
            f"{phase} content differences are not exact: "
            f"expected={sorted(expected)!r}, actual={sorted(content_differences)!r}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--runtime-manifest", required=True)
    parser.add_argument(
        "--phase", choices=("pre", "post", "capture"), required=True
    )
    arguments = parser.parse_args()

    source = inventory(arguments.source)
    runtime = inventory(arguments.runtime)
    write_manifest(arguments.source_manifest, source)
    write_manifest(arguments.runtime_manifest, runtime)
    compare(source, runtime, arguments.phase)
    print(
        f"{arguments.phase} manifests verified: "
        f"{len(source)} exact relative paths"
    )


if __name__ == "__main__":
    main()
```

This comparator uses `os.lstat` for every entry, `stat.S_IMODE` for modes,
`hashlib.sha256` plus byte size for regular files, and `os.readlink` for
symlink targets. Its `os.walk(..., followlinks=False)` inventory has an exact
relative path set, rejects special files, and writes stable sorted JSON. This is
cooperative drift detection, not an adversarial race-proof no-follow guarantee:
path-based traversal and final-component `O_NOFOLLOW` cannot defeat malicious
concurrent parent or root replacement. mtime is intentionally excluded from
the manifest equality decision, while mtime, `st_ctime_ns`, device, inode, size,
and mode participate in the per-read race check. The immutable reviewed staging
snapshot and exact allowlist are the mutation safety boundary. Pre-sync accepts
exactly the three approved regular-file content differences; post-sync requires
exact equality, and `capture` writes independent manifests without comparing.

Then use `apply_patch` to create
`/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe/review_rsync.py`
with this complete content:

```python
from __future__ import annotations

import argparse
import json
import re


ALLOWED_UPDATES = {
    "SKILL.md",
    "references/chrome-chatgpt-pro.md",
    "references/file-artifact-exchange.md",
}
ITEMIZED = re.compile(r"^[<>ch.][fdLDS][cstTpoguaxA.+?]{7}$")
PSEUDO_RECORD = ".f..T...."


def fail(message: str) -> None:
    raise SystemExit(message)


def read_manifest(path: str) -> dict[str, dict[str, object]]:
    with open(path, encoding="utf-8") as input_file:
        value = json.load(input_file)
    if not isinstance(value, dict):
        fail(f"manifest is not an object: {path}")
    return value


def prove_equal_regular(
    relative_path: str,
    source: dict[str, dict[str, object]],
    runtime: dict[str, dict[str, object]],
) -> None:
    if relative_path not in source or relative_path not in runtime:
        fail(f"pseudo-record path is absent from a manifest: {relative_path}")
    source_entry = source[relative_path]
    runtime_entry = runtime[relative_path]
    if source_entry.get("type") != "regular":
        fail(f"pseudo-record is not a regular file: {relative_path}")
    evidence_keys = ("type", "mode", "size", "sha256")
    if any(source_entry.get(key) != runtime_entry.get(key) for key in evidence_keys):
        fail(
            "pseudo-record lacks equal regular-file size, SHA-256, and mode: "
            f"{relative_path}"
        )


def write_exclusive(path: str, content: str) -> None:
    with open(path, "x", encoding="utf-8") as output:
        output.write(content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--count", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--runtime-manifest", required=True)
    parser.add_argument("--reviewed", required=True)
    parser.add_argument("--phase", choices=("pre", "post"), required=True)
    arguments = parser.parse_args()

    source = read_manifest(arguments.source_manifest)
    runtime = read_manifest(arguments.runtime_manifest)
    actions: list[tuple[str, str, str]] = []
    with open(arguments.raw, encoding="utf-8") as input_file:
        for raw_line in input_file:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            fields = line.split(maxsplit=1)
            item = fields[0]
            if item == PSEUDO_RECORD:
                if len(fields) != 2:
                    fail(f"pseudo-record has no path: {line!r}")
                prove_equal_regular(fields[1], source, runtime)
                continue
            if item == "*deleting":
                relative_path = fields[1] if len(fields) == 2 else ""
                actions.append((item, relative_path, line))
            elif ITEMIZED.fullmatch(item):
                if len(fields) != 2:
                    fail(f"itemized record has no path: {line!r}")
                actions.append((item, fields[1], line))
            else:
                fail(f"unrecognized raw rsync output: {line!r}")

    with open(arguments.count, encoding="utf-8") as input_file:
        count_lines = [line.rstrip("\n") for line in input_file]
    expected_count = 3 if arguments.phase == "pre" else 0
    expected_count_line = f"Number of files transferred: {expected_count}"
    if count_lines != [expected_count_line]:
        fail(
            f"unstable transfer-count evidence: "
            f"expected={[expected_count_line]!r}, actual={count_lines!r}"
        )

    if arguments.phase == "pre":
        paths = {path for _, path, _ in actions}
        if len(actions) != 3 or paths != ALLOWED_UPDATES:
            fail(f"reviewed pre-sync actions are not exact: {actions!r}")
        for item, relative_path, _ in actions:
            if not item.startswith(">f") or "+" in item:
                fail(f"pre-sync action is not a regular-file update: {item} {relative_path}")
    elif actions:
        fail(f"post-sync reviewed dry run is not empty: {actions!r}")

    reviewed = "".join(f"{line}\n" for _, _, line in actions)
    write_exclusive(arguments.reviewed, reviewed)
    print(
        f"{arguments.phase} rsync evidence verified: "
        f"{len(actions)} reviewed actions"
    )


if __name__ == "__main__":
    main()
```

The reviewer filters only a record whose first field is exactly `.f..T....`,
and only after the independent manifests prove equal regular-file size,
SHA-256, and mode at that path. It does not hide any other `T` record. Every
deletion, creation, type, mode, symlink, special-file, or unplanned-path
difference remains fail-closed through the independent comparator, raw
snapshot, or reviewed action set.

Next, use `apply_patch` to create
`/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe/snapshot_reviewed_source.py`
with this complete content:

```python
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from typing import Any


APPROVED_PATHS = (
    "SKILL.md",
    "references/chrome-chatgpt-pro.md",
    "references/file-artifact-exchange.md",
)
ALLOWLIST_BYTES = (
    b"SKILL.md\n"
    b"references/chrome-chatgpt-pro.md\n"
    b"references/file-artifact-exchange.md\n"
)
ALLOWLIST_SHA256 = (
    "7e36fc01e0b8390bfcfeb93bf4fb2e88cf4180fa8714968ce968d41507274c8f"
)


def fail(message: str) -> None:
    raise SystemExit(message)


def stable_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        stat.S_IMODE(metadata.st_mode),
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def read_regular(path: str) -> tuple[bytes, dict[str, Any]]:
    before = os.lstat(path)
    if not stat.S_ISREG(before.st_mode):
        fail(f"reviewed source entry is not regular: {path}")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            fail(f"reviewed source entry changed type: {path}")
        if stable_identity(opened) != stable_identity(before):
            fail(f"reviewed source entry changed while opening: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after_fd = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after_path = os.lstat(path)
    if (
        stable_identity(after_fd) != stable_identity(opened)
        or stable_identity(after_path) != stable_identity(opened)
    ):
        fail(f"reviewed source entry changed while reading: {path}")
    content = b"".join(chunks)
    record = {
        "path": "",
        "type": "regular",
        "mode": f"{stat.S_IMODE(opened.st_mode):04o}",
        "size": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }
    return content, record


def load_object(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as input_file:
        value = json.load(input_file)
    if not isinstance(value, dict):
        fail(f"JSON object required: {path}")
    return value


def write_json_exclusive(path: str, value: dict[str, Any], mode: int = 0o600) -> None:
    content = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    write_bytes_exclusive(path, content, mode)


def write_bytes_exclusive(path: str, content: bytes, mode: int) -> None:
    exclusive_flags = os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    descriptor = os.open(path, os.O_WRONLY | exclusive_flags, mode)
    try:
        os.fchmod(descriptor, mode)
        position = 0
        while position < len(content):
            position += os.write(descriptor, content[position:])
        os.fsync(descriptor)
        written = os.fstat(descriptor)
        if not stat.S_ISREG(written.st_mode):
            fail(f"exclusive output changed type: {path}")
        if written.st_size != len(content):
            fail(f"exclusive output size mismatch: {path}")
        if stat.S_IMODE(written.st_mode) != mode:
            fail(f"exclusive output mode mismatch: {path}")
    finally:
        os.close(descriptor)


def approved_subset(full_manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    subset: dict[str, dict[str, Any]] = {}
    for relative_path in APPROVED_PATHS:
        entry = full_manifest.get(relative_path)
        if not isinstance(entry, dict) or entry.get("type") != "regular":
            fail(f"approved manifest entry is not regular: {relative_path}")
        subset[relative_path] = entry
    return subset


def reviewed_directory_mode(full_manifest: dict[str, Any], path: str) -> int:
    entry = full_manifest.get(path)
    if not isinstance(entry, dict) or entry.get("type") != "directory":
        fail(f"reviewed parent is not a directory: {path}")
    return int(entry["mode"], 8)


def validate_allowlist(path: str) -> None:
    content, record = read_regular(path)
    if content != ALLOWLIST_BYTES:
        fail("allowlist bytes are not the exact three-path allowlist")
    if hashlib.sha256(content).hexdigest() != ALLOWLIST_SHA256:
        fail("allowlist SHA-256 mismatch")
    if record["mode"] != "0600":
        fail("allowlist mode must be 0600")
    lines = content.decode("ascii").splitlines()
    if tuple(lines) != APPROVED_PATHS:
        fail("allowlist ordering or path set changed")
    for line in lines:
        components = line.split("/")
        if (
            not line
            or line.startswith("/")
            or ".." in components
            or any(character in line for character in "*?[")
        ):
            fail(f"unsafe allowlist path: {line!r}")


def create_snapshot(
    source: str,
    source_manifest_path: str,
    staging: str,
    allowlist: str,
    staging_manifest_path: str,
) -> None:
    full_manifest = load_object(source_manifest_path)
    expected = approved_subset(full_manifest)
    root_mode = reviewed_directory_mode(full_manifest, ".")
    references_mode = reviewed_directory_mode(full_manifest, "references")
    os.mkdir(staging, root_mode)
    os.chmod(staging, root_mode, follow_symlinks=False)
    references = os.path.join(staging, "references")
    os.mkdir(references, references_mode)
    os.chmod(references, references_mode, follow_symlinks=False)
    actual: dict[str, dict[str, Any]] = {}
    for relative_path in APPROVED_PATHS:
        source_path = os.path.join(source, *relative_path.split("/"))
        content, record = read_regular(source_path)
        record["path"] = relative_path
        if record != expected[relative_path]:
            fail(f"live source no longer matches reviewed manifest: {relative_path}")
        destination = os.path.join(staging, *relative_path.split("/"))
        write_bytes_exclusive(destination, content, int(record["mode"], 8))
        actual[relative_path] = record
    write_bytes_exclusive(allowlist, ALLOWLIST_BYTES, 0o600)
    write_json_exclusive(staging_manifest_path, actual)
    verify_snapshot(staging, allowlist, source_manifest_path, staging_manifest_path)


def scan_staging(
    staging: str,
    full_manifest: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    root = os.lstat(staging)
    references = os.lstat(os.path.join(staging, "references"))
    if not stat.S_ISDIR(root.st_mode) or not stat.S_ISDIR(references.st_mode):
        fail("staging root and references parent must be real directories")
    if stat.S_IMODE(root.st_mode) != reviewed_directory_mode(full_manifest, "."):
        fail("staging root mode differs from reviewed source")
    if stat.S_IMODE(references.st_mode) != reviewed_directory_mode(
        full_manifest, "references"
    ):
        fail("staging references mode differs from reviewed source")
    observed_paths: set[str] = set()
    for current, dirnames, filenames in os.walk(staging, followlinks=False):
        dirnames.sort()
        filenames.sort()
        for name in [*dirnames, *filenames]:
            relative_path = os.path.relpath(
                os.path.join(current, name), staging
            ).replace(os.sep, "/")
            observed_paths.add(relative_path)
    expected_paths = {*APPROVED_PATHS, "references"}
    if observed_paths != expected_paths:
        fail(
            f"staging path set changed: expected={sorted(expected_paths)!r}, "
            f"actual={sorted(observed_paths)!r}"
        )
    actual: dict[str, dict[str, Any]] = {}
    for relative_path in APPROVED_PATHS:
        content, record = read_regular(
            os.path.join(staging, *relative_path.split("/"))
        )
        record["path"] = relative_path
        if record["size"] != len(content):
            fail(f"staging size mismatch: {relative_path}")
        actual[relative_path] = record
    return actual


def verify_snapshot(
    staging: str,
    allowlist: str,
    source_manifest_path: str,
    staging_manifest_path: str,
) -> None:
    validate_allowlist(allowlist)
    full_manifest = load_object(source_manifest_path)
    expected = approved_subset(full_manifest)
    recorded = load_object(staging_manifest_path)
    actual = scan_staging(staging, full_manifest)
    if recorded != expected or actual != expected:
        fail("staging manifest does not match the reviewed source subset")
    print("staging manifest matches the reviewed allowlisted subset")


def root_identity(root: str) -> dict[str, Any]:
    metadata = os.lstat(root)
    if not stat.S_ISDIR(metadata.st_mode):
        fail("runtime root is not a real directory")
    return {
        "device": metadata.st_dev,
        "inode": metadata.st_ino,
        "mode": f"{stat.S_IMODE(metadata.st_mode):04o}",
        "type": "directory",
    }


def capture_identity(root: str, output: str) -> None:
    write_json_exclusive(output, root_identity(root))


def check_identity(root: str, expected_path: str) -> None:
    if root_identity(root) != load_object(expected_path):
        fail("runtime root identity mismatch")
    print("runtime root identity is unchanged")


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("--source", required=True)
    create.add_argument("--source-manifest", required=True)
    create.add_argument("--staging", required=True)
    create.add_argument("--allowlist", required=True)
    create.add_argument("--staging-manifest", required=True)

    verify = subparsers.add_parser("verify")
    verify.add_argument("--staging", required=True)
    verify.add_argument("--allowlist", required=True)
    verify.add_argument("--source-manifest", required=True)
    verify.add_argument("--staging-manifest", required=True)

    identity = subparsers.add_parser("identity")
    identity.add_argument("--root", required=True)
    identity.add_argument("--output", required=True)

    check = subparsers.add_parser("check-identity")
    check.add_argument("--root", required=True)
    check.add_argument("--expected", required=True)

    arguments = parser.parse_args()
    if arguments.command == "create":
        create_snapshot(
            arguments.source,
            arguments.source_manifest,
            arguments.staging,
            arguments.allowlist,
            arguments.staging_manifest,
        )
    elif arguments.command == "verify":
        verify_snapshot(
            arguments.staging,
            arguments.allowlist,
            arguments.source_manifest,
            arguments.staging_manifest,
        )
    elif arguments.command == "identity":
        capture_identity(arguments.root, arguments.output)
    else:
        check_identity(arguments.root, arguments.expected)


if __name__ == "__main__":
    main()
```

The snapshot builder reads each approved live source file with
`O_NOFOLLOW`/`fstat` and checks device, inode, size, mode, `st_mtime_ns`, and
`st_ctime_ns` before and after the read. It requires a regular file whose
bytes, SHA-256, size, and mode exactly match the reviewed full manifest. It
creates parents and files exclusively, uses
`O_CREAT | os.O_EXCL | os.O_NOFOLLOW`, writes and `fsync`s the reviewed bytes,
and never copies a symlink or special file. The exclusive allowlist is exactly
three ASCII relative paths with no blank, absolute, `..`, or glob entry; its
bytes, SHA-256, and `0600` mode are validated on every gate.
The staging root and required parent directory are created exclusively with
the reviewed full-manifest modes, and reviewed parent directory modes match source-pre-2.

Finally, use `apply_patch` to create
`/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe/pressure_sync.py`
with this complete content:

```python
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ALLOWED = (
    "SKILL.md",
    "references/chrome-chatgpt-pro.md",
    "references/file-artifact-exchange.md",
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_tree(root: Path) -> None:
    write(root / "SKILL.md", "same skill\n")
    write(root / "agents/openai.yaml", "same agent\n")
    write(root / "references/chrome-chatgpt-pro.md", "same chrome\n")
    write(root / "references/file-artifact-exchange.md", "same exchange\n")
    write(root / "references/unchanged.md", "same unchanged\n")
    os.symlink("unchanged.md", root / "references/sample-link")


def invoke_comparator(
    comparator: Path,
    scenario: Path,
    source: Path,
    runtime: Path,
    *,
    phase: str = "post",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(comparator),
            "--source",
            str(source),
            "--runtime",
            str(runtime),
            "--source-manifest",
            str(scenario / "source.json"),
            "--runtime-manifest",
            str(scenario / "runtime.json"),
            "--phase",
            phase,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def structural_case(
    root: Path,
    comparator: Path,
    name: str,
    mutate,
    *,
    should_pass: bool,
    expected_error: str | None = None,
) -> None:
    scenario = root / name
    source = scenario / "source"
    runtime = scenario / "runtime"
    make_tree(source)
    shutil.copytree(source, runtime, symlinks=True)
    mutate(source, runtime)
    result = invoke_comparator(comparator, scenario, source, runtime)
    if (result.returncode == 0) != should_pass:
        raise SystemExit(
            f"{name}: unexpected comparator result "
            f"rc={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
    if not should_pass and expected_error not in result.stderr:
        raise SystemExit(
            f"{name}: expected error {expected_error!r}, got {result.stderr!r}"
        )
    print(f"{name}: {'PASS' if should_pass else 'REJECTED'}")


def run_openrsync_case(root: Path, comparator: Path, reviewer: Path) -> None:
    scenario = root / "openrsync"
    source = scenario / "source"
    runtime = scenario / "runtime"
    make_tree(source)
    shutil.copytree(source, runtime, symlinks=True)
    for relative_path in ALLOWED:
        write(source / relative_path, f"source content for {relative_path}\n")
    unchanged = runtime / "agents/openai.yaml"
    original = unchanged.stat()
    os.utime(unchanged, (original.st_atime + 120, original.st_mtime + 120))

    result = invoke_comparator(
        comparator,
        scenario,
        source,
        runtime,
        phase="pre",
    )
    if result.returncode != 0:
        raise SystemExit(f"openrsync comparator failed: {result.stderr!r}")

    raw_path = scenario / "raw.txt"
    raw = subprocess.run(
        [
            "/usr/bin/rsync",
            "--rsync-path=/usr/bin/rsync",
            "-rlpcni",
            "--delete",
            "--out-format=%i %n%L",
            f"{source}/",
            f"{runtime}/",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"},
    )
    raw_path.write_text(raw.stdout, encoding="utf-8")
    if ".f..T.... agents/openai.yaml\n" not in raw.stdout:
        raise SystemExit(f"openrsync pseudo-record not reproduced: {raw.stdout!r}")

    stats = subprocess.run(
        [
            "/usr/bin/rsync",
            "--rsync-path=/usr/bin/rsync",
            "-rlpcni",
            "--delete",
            "--stats",
            "--out-format=",
            f"{source}/",
            f"{runtime}/",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"},
    )
    count_lines = [
        line
        for line in stats.stdout.splitlines()
        if line.startswith("Number of files transferred:")
    ]
    count_path = scenario / "count.txt"
    count_path.write_text("\n".join(count_lines) + "\n", encoding="utf-8")

    review_result = subprocess.run(
        [
            sys.executable,
            str(reviewer),
            "--raw",
            str(raw_path),
            "--count",
            str(count_path),
            "--source-manifest",
            str(scenario / "source.json"),
            "--runtime-manifest",
            str(scenario / "runtime.json"),
            "--reviewed",
            str(scenario / "reviewed.txt"),
            "--phase",
            "pre",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    if review_result.stdout != "pre rsync evidence verified: 3 reviewed actions\n":
        raise SystemExit(f"unexpected reviewer output: {review_result.stdout!r}")
    reviewed = (scenario / "reviewed.txt").read_text(encoding="utf-8").splitlines()
    if len(reviewed) != 3:
        raise SystemExit(f"openrsync reviewed actions are not exact: {reviewed!r}")
    print("openrsync raw/review: PASS")


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def reviewer_case(
    root: Path,
    reviewer: Path,
    name: str,
    *,
    raw: str,
    count: int,
    phase: str,
    source_manifest: dict[str, object],
    runtime_manifest: dict[str, object],
    should_pass: bool,
    expected_error: str = "",
) -> None:
    scenario = root / f"reviewer-{name}"
    scenario.mkdir()
    write(scenario / "raw.txt", raw)
    write(scenario / "count.txt", f"Number of files transferred: {count}\n")
    write_json(scenario / "source.json", source_manifest)
    write_json(scenario / "runtime.json", runtime_manifest)
    result = subprocess.run(
        [
            sys.executable,
            str(reviewer),
            "--raw",
            str(scenario / "raw.txt"),
            "--count",
            str(scenario / "count.txt"),
            "--source-manifest",
            str(scenario / "source.json"),
            "--runtime-manifest",
            str(scenario / "runtime.json"),
            "--reviewed",
            str(scenario / "reviewed.txt"),
            "--phase",
            phase,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if (result.returncode == 0) != should_pass:
        raise SystemExit(
            f"reviewer {name}: unexpected result "
            f"rc={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
    if not should_pass and expected_error not in result.stderr:
        raise SystemExit(
            f"reviewer {name}: expected {expected_error!r}, got {result.stderr!r}"
        )
    print(f"{name}: {'PASS' if should_pass else 'REJECTED'}")


def reviewer_pressure(root: Path, reviewer: Path) -> None:
    equal = {
        "agents/openai.yaml": {
            "type": "regular",
            "mode": "0644",
            "size": 4,
            "sha256": "same",
        }
    }
    unequal = {
        "agents/openai.yaml": {
            "type": "regular",
            "mode": "0644",
            "size": 5,
            "sha256": "different",
        }
    }
    reviewer_case(
        root,
        reviewer,
        "unequal-manifest pseudo-record",
        raw=".f..T.... agents/openai.yaml\n",
        count=3,
        phase="pre",
        source_manifest=equal,
        runtime_manifest=unequal,
        should_pass=False,
        expected_error="lacks equal regular-file size, SHA-256, and mode",
    )
    reviewer_case(
        root,
        reviewer,
        "non-pseudo T record",
        raw=(
            ">fcsT.... SKILL.md\n"
            ">fcsT.... references/chrome-chatgpt-pro.md\n"
            ">fcsT.... references/file-artifact-exchange.md\n"
        ),
        count=3,
        phase="pre",
        source_manifest={},
        runtime_manifest={},
        should_pass=True,
    )
    reviewer_case(
        root,
        reviewer,
        "unknown raw line",
        raw="unexpected output\n",
        count=3,
        phase="pre",
        source_manifest={},
        runtime_manifest={},
        should_pass=False,
        expected_error="unrecognized raw rsync output",
    )
    reviewer_case(
        root,
        reviewer,
        "transfer-count mismatch",
        raw=(
            ">fcsT.... SKILL.md\n"
            ">fcsT.... references/chrome-chatgpt-pro.md\n"
            ">fcsT.... references/file-artifact-exchange.md\n"
        ),
        count=2,
        phase="pre",
        source_manifest={},
        runtime_manifest={},
        should_pass=False,
        expected_error="unstable transfer-count evidence",
    )
    reviewer_case(
        root,
        reviewer,
        "deletion or creation record",
        raw="*deleting runtime-only.md\n",
        count=3,
        phase="pre",
        source_manifest={},
        runtime_manifest={},
        should_pass=False,
        expected_error="reviewed pre-sync actions are not exact",
    )
    reviewer_case(
        root,
        reviewer,
        "post-sync action",
        raw=">fcsT.... SKILL.md\n",
        count=0,
        phase="post",
        source_manifest={},
        runtime_manifest={},
        should_pass=False,
        expected_error="post-sync reviewed dry run is not empty",
    )
    reviewer_case(
        root,
        reviewer,
        "duplicate or unapproved action",
        raw=(
            ">fcsT.... SKILL.md\n"
            ">fcsT.... SKILL.md\n"
            ">fcsT.... unapproved.md\n"
        ),
        count=3,
        phase="pre",
        source_manifest={},
        runtime_manifest={},
        should_pass=False,
        expected_error="reviewed pre-sync actions are not exact",
    )


def run_snapshot(
    snapshotter: Path,
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(snapshotter), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def snapshot_binding_pressure(
    root: Path,
    comparator: Path,
    snapshotter: Path,
) -> None:
    scenario = root / "snapshot-binding"
    source = scenario / "source"
    runtime = scenario / "runtime"
    make_tree(source)
    shutil.copytree(source, runtime, symlinks=True)
    for relative_path in ALLOWED:
        write(source / relative_path, f"reviewed {relative_path}\n")
    result = invoke_comparator(
        comparator,
        scenario,
        source,
        runtime,
        phase="pre",
    )
    if result.returncode != 0:
        raise SystemExit(f"snapshot comparator failed: {result.stderr!r}")

    staging = scenario / "reviewed-source"
    allowlist = scenario / "reviewed-allowlist.txt"
    staging_manifest = scenario / "staging.json"
    result = run_snapshot(
        snapshotter,
        "create",
        "--source",
        str(source),
        "--source-manifest",
        str(scenario / "source.json"),
        "--staging",
        str(staging),
        "--allowlist",
        str(allowlist),
        "--staging-manifest",
        str(staging_manifest),
    )
    if result.returncode != 0:
        raise SystemExit(f"snapshot creation failed: {result.stderr!r}")

    initial_transport = subprocess.run(
        [
            "/usr/bin/rsync",
            "--rsync-path=/usr/bin/rsync",
            "-rlpcni",
            f"--files-from={allowlist}",
            "--out-format=%i %n%L",
            f"{staging}/",
            f"{runtime}/",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"},
    )
    transport_lines = initial_transport.stdout.splitlines()
    transport_paths = {
        line.split(maxsplit=1)[1] for line in transport_lines if " " in line
    }
    if (
        len(transport_lines) != 3
        or transport_paths != set(ALLOWED)
        or any(not line.startswith(">f") for line in transport_lines)
    ):
        raise SystemExit(
            f"transport contains directory or unapproved action: {transport_lines!r}"
        )
    print(
        "transport contains exactly three regular-file actions "
        "and no directory metadata action"
    )

    reviewed_skill = (staging / "SKILL.md").read_bytes()
    write(source / "SKILL.md", "mutated live source\n")
    result = run_snapshot(
        snapshotter,
        "verify",
        "--staging",
        str(staging),
        "--allowlist",
        str(allowlist),
        "--source-manifest",
        str(scenario / "source.json"),
        "--staging-manifest",
        str(staging_manifest),
    )
    if result.returncode != 0 or (staging / "SKILL.md").read_bytes() != reviewed_skill:
        raise SystemExit("reviewed staging changed after live-source mutation")
    print("live-source mutation after pre-2: PASS")

    write(source / "source-only-after-pre-2.md", "must not transport\n")
    transport = subprocess.run(
        [
            "/usr/bin/rsync",
            "--rsync-path=/usr/bin/rsync",
            "-rlpcni",
            f"--files-from={allowlist}",
            f"{staging}/",
            f"{runtime}/",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"},
    )
    if "source-only-after-pre-2.md" in transport.stdout:
        raise SystemExit("allowlist transport exposed a source-only addition")
    print("source-only addition after pre-2: PASS")

    identity_path = scenario / "runtime-root.json"
    result = run_snapshot(
        snapshotter,
        "identity",
        "--root",
        str(runtime),
        "--output",
        str(identity_path),
    )
    if result.returncode != 0:
        raise SystemExit(f"identity capture failed: {result.stderr!r}")
    runtime.rename(scenario / "runtime-replaced")
    runtime.mkdir()
    result = run_snapshot(
        snapshotter,
        "check-identity",
        "--root",
        str(runtime),
        "--expected",
        str(identity_path),
    )
    if result.returncode == 0 or "runtime root identity mismatch" not in result.stderr:
        raise SystemExit("runtime-root identity mismatch was not rejected")
    print("runtime-root identity mismatch: REJECTED")

    write(staging / "SKILL.md", "mutated staging\n")
    result = run_snapshot(
        snapshotter,
        "verify",
        "--staging",
        str(staging),
        "--allowlist",
        str(allowlist),
        "--source-manifest",
        str(scenario / "source.json"),
        "--staging-manifest",
        str(staging_manifest),
    )
    if result.returncode == 0 or "staging manifest does not match" not in result.stderr:
        raise SystemExit("staging mutation was not rejected")
    print("staging mutation: REJECTED")


def poisoned_path_pressure(root: Path) -> None:
    scenario = root / "poisoned-path"
    source = scenario / "source"
    runtime = scenario / "runtime"
    write(source / "sample.txt", "source\n")
    write(runtime / "sample.txt", "runtime\n")
    base = ["/usr/bin/rsync", "-rlpcni"]
    poisoned_env = {"LC_ALL": "C", "PATH": "/nonexistent"}
    rejected = subprocess.run(
        [*base, f"{source}/", f"{runtime}/"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=poisoned_env,
    )
    if rejected.returncode != 14 or "rsync" not in rejected.stderr:
        raise SystemExit(
            f"poisoned unpinned peer did not fail as expected: {rejected!r}"
        )
    print("poisoned PATH without peer pin: REJECTED")
    pinned = subprocess.run(
        [*base, "--rsync-path=/usr/bin/rsync", f"{source}/", f"{runtime}/"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=poisoned_env,
    )
    if pinned.returncode != 0:
        raise SystemExit(f"poisoned pinned peer failed: {pinned.stderr!r}")
    print("poisoned PATH with peer pin: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--comparator", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--snapshotter", required=True)
    arguments = parser.parse_args()
    root = Path(arguments.root)
    comparator = Path(arguments.comparator)
    reviewer = Path(arguments.reviewer)
    snapshotter = Path(arguments.snapshotter)
    root.mkdir(mode=0o700)

    structural_case(
        root,
        comparator,
        "deletion",
        lambda _source, runtime: (runtime / "agents/openai.yaml").unlink(),
        should_pass=False,
        expected_error="exact relative path set differs",
    )
    structural_case(
        root,
        comparator,
        "source-only creation",
        lambda source, _runtime: write(source / "source-only.md", "new\n"),
        should_pass=False,
        expected_error="exact relative path set differs",
    )
    structural_case(
        root,
        comparator,
        "regular-file mode change",
        lambda _source, runtime: os.chmod(runtime / "SKILL.md", 0o600),
        should_pass=False,
        expected_error="mode differs at SKILL.md",
    )
    structural_case(
        root,
        comparator,
        "directory mode change",
        lambda _source, runtime: os.chmod(runtime / "references", 0o700),
        should_pass=False,
        expected_error="mode differs at references",
    )

    def replace_type(_source: Path, runtime: Path) -> None:
        path = runtime / "agents/openai.yaml"
        path.unlink()
        path.mkdir()

    structural_case(
        root,
        comparator,
        "file-type replacement",
        replace_type,
        should_pass=False,
        expected_error="type differs at agents/openai.yaml",
    )

    def change_link(_source: Path, runtime: Path) -> None:
        link = runtime / "references/sample-link"
        link.unlink()
        os.symlink("chrome-chatgpt-pro.md", link)

    structural_case(
        root,
        comparator,
        "changed symlink target",
        change_link,
        should_pass=False,
        expected_error="symlink target differs at references/sample-link",
    )
    structural_case(
        root,
        comparator,
        "special-file insertion",
        lambda _source, runtime: os.mkfifo(runtime / "references/special.fifo"),
        should_pass=False,
        expected_error="special files are forbidden: references/special.fifo",
    )

    def change_timestamp(_source: Path, runtime: Path) -> None:
        path = runtime / "agents/openai.yaml"
        current = path.stat()
        os.utime(path, (current.st_atime + 120, current.st_mtime + 120))

    structural_case(
        root,
        comparator,
        "timestamp-only mismatch",
        change_timestamp,
        should_pass=True,
    )
    run_openrsync_case(root, comparator, reviewer)
    reviewer_pressure(root, reviewer)
    snapshot_binding_pressure(root, comparator, snapshotter)
    poisoned_path_pressure(root)


if __name__ == "__main__":
    main()
```

Mark all four scripts executable only after `apply_patch` succeeds:

```bash
set -euo pipefail
VALIDATOR_ROOT="/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe"
test -f "$VALIDATOR_ROOT/compare_skill_trees.py"
test -f "$VALIDATOR_ROOT/review_rsync.py"
test -f "$VALIDATOR_ROOT/snapshot_reviewed_source.py"
test -f "$VALIDATOR_ROOT/pressure_sync.py"
chmod 700 \
  "$VALIDATOR_ROOT/compare_skill_trees.py" \
  "$VALIDATOR_ROOT/review_rsync.py" \
  "$VALIDATOR_ROOT/snapshot_reviewed_source.py" \
  "$VALIDATOR_ROOT/pressure_sync.py"
```

- [ ] **Step 4: Pressure-test the comparator and validate the repository skill**

Use a separate collision-checked diagnostic root. Preserve it after the run;
never use it as the validator, repository source, or installed runtime:

```bash
set -euo pipefail
VALIDATOR_ROOT="/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe"
PRESSURE_ROOT="/tmp/chatgpt-multi-format-sync-pressure-20260713-content-only"
test ! -e "$PRESSURE_ROOT"
RSYNC_IDENTITY="$(/usr/bin/rsync --version | sed -n '1,2p')"
EXPECTED_RSYNC_IDENTITY="$(printf '%s\n%s' \
  'openrsync: protocol version 29' \
  'rsync version 2.6.9 compatible')"
test "$RSYNC_IDENTITY" = "$EXPECTED_RSYNC_IDENTITY"
PATH_BEFORE_LOOP="$PATH"
for evidence_path in alpha beta
do
  test -n "$evidence_path"
done
test "$PATH" = "$PATH_BEFORE_LOOP"
"$VALIDATOR_ROOT/venv/bin/python" "$VALIDATOR_ROOT/pressure_sync.py" \
  --root "$PRESSURE_ROOT" \
  --comparator "$VALIDATOR_ROOT/compare_skill_trees.py" \
  --reviewer "$VALIDATOR_ROOT/review_rsync.py" \
  --snapshotter "$VALIDATOR_ROOT/snapshot_reviewed_source.py"
"$VALIDATOR_ROOT/venv/bin/python" \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/chatgpt-collaboration-harness
```

Expected pressure evidence:

```text
deletion: REJECTED
source-only creation: REJECTED
regular-file mode change: REJECTED
directory mode change: REJECTED
file-type replacement: REJECTED
changed symlink target: REJECTED
special-file insertion: REJECTED
timestamp-only mismatch: PASS
openrsync raw/review: PASS
unequal-manifest pseudo-record: REJECTED
non-pseudo T record: PASS
unknown raw line: REJECTED
transfer-count mismatch: REJECTED
deletion or creation record: REJECTED
post-sync action: REJECTED
duplicate or unapproved action: REJECTED
live-source mutation after pre-2: PASS
source-only addition after pre-2: PASS
runtime-root identity mismatch: REJECTED
staging mutation: REJECTED
transport contains exactly three regular-file actions and no directory metadata action
poisoned PATH without peer pin: REJECTED
poisoned PATH with peer pin: PASS
Skill is valid!
```

The manifest must catch all structural cases, including the changed symlink
target that this host's openrsync did not itemize. Only timestamp-only mismatch
is ignored. The openrsync case must reproduce and safely filter the exact
pseudo-record while retaining exactly three reviewed content updates.
`/usr/bin/rsync` must match the tested openrsync protocol and itemized format
above. A different implementation stops the workflow and requires fresh raw-
format pressure validation before any transport or mutation command.
Pressure subprocesses use the explicit equivalent of `PATH=/usr/bin:/bin` and
do not inherit the ambient command search path.

- [ ] **Step 5: Bind two pre-sync evidence sets to reviewed staging**

Capture dry-run 1. Every output path uses exclusive creation, so a collision
stops the run:
The prior `rsync -rlpcni --delete` structural intent is retained, with the
mandatory peer-path pin added to the executable command.
The prior `/usr/bin/rsync -rlpcni --files-from="$ALLOWLIST"` and
`/usr/bin/rsync -rlpc --files-from="$ALLOWLIST" \` shapes are likewise retained
semantically, with `--rsync-path=/usr/bin/rsync` inserted before the allowlist.

```bash
set -euo pipefail
set -C
VALIDATOR_ROOT="/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe"
SOURCE="skills/chatgpt-collaboration-harness"
RUNTIME="$HOME/.codex/skills/chatgpt-collaboration-harness"
STAGING="$VALIDATOR_ROOT/reviewed-source"
ALLOWLIST="$VALIDATOR_ROOT/reviewed-allowlist.txt"
STAGING_MANIFEST="$VALIDATOR_ROOT/reviewed-source-manifest.json"
for evidence_path in \
  "$VALIDATOR_ROOT/source-pre-1.json" \
  "$VALIDATOR_ROOT/runtime-pre-1.json" \
  "$VALIDATOR_ROOT/runtime-raw-dry-run-1.txt" \
  "$VALIDATOR_ROOT/runtime-reviewed-dry-run-1.txt" \
  "$VALIDATOR_ROOT/runtime-transfer-count-1.txt"
do
  test ! -e "$evidence_path"
done
"$VALIDATOR_ROOT/venv/bin/python" "$VALIDATOR_ROOT/compare_skill_trees.py" \
  --source "$SOURCE" \
  --runtime "$RUNTIME" \
  --source-manifest "$VALIDATOR_ROOT/source-pre-1.json" \
  --runtime-manifest "$VALIDATOR_ROOT/runtime-pre-1.json" \
  --phase pre
LC_ALL=C /usr/bin/rsync -rlpcni --rsync-path=/usr/bin/rsync --delete --out-format='%i %n%L' \
  "$SOURCE/" "$RUNTIME/" \
  > "$VALIDATOR_ROOT/runtime-raw-dry-run-1.txt"
LC_ALL=C /usr/bin/rsync -rlpcni --rsync-path=/usr/bin/rsync --delete --stats --out-format='' \
  "$SOURCE/" "$RUNTIME/" \
  | awk '/^Number of files transferred:/{print}' \
  > "$VALIDATOR_ROOT/runtime-transfer-count-1.txt"
"$VALIDATOR_ROOT/venv/bin/python" "$VALIDATOR_ROOT/review_rsync.py" \
  --raw "$VALIDATOR_ROOT/runtime-raw-dry-run-1.txt" \
  --count "$VALIDATOR_ROOT/runtime-transfer-count-1.txt" \
  --source-manifest "$VALIDATOR_ROOT/source-pre-1.json" \
  --runtime-manifest "$VALIDATOR_ROOT/runtime-pre-1.json" \
  --reviewed "$VALIDATOR_ROOT/runtime-reviewed-dry-run-1.txt" \
  --phase pre
cat "$VALIDATOR_ROOT/runtime-reviewed-dry-run-1.txt"
cat "$VALIDATOR_ROOT/runtime-transfer-count-1.txt"
for evidence_path in \
  "$STAGING" \
  "$ALLOWLIST" \
  "$STAGING_MANIFEST" \
  "$VALIDATOR_ROOT/transport-raw-dry-run-1.txt" \
  "$VALIDATOR_ROOT/transport-reviewed-dry-run-1.txt" \
  "$VALIDATOR_ROOT/transport-transfer-count-1.txt"
do
  test ! -e "$evidence_path"
done
"$VALIDATOR_ROOT/venv/bin/python" \
  "$VALIDATOR_ROOT/snapshot_reviewed_source.py" create \
  --source "$SOURCE" \
  --source-manifest "$VALIDATOR_ROOT/source-pre-1.json" \
  --staging "$STAGING" \
  --allowlist "$ALLOWLIST" \
  --staging-manifest "$STAGING_MANIFEST"
LC_ALL=C /usr/bin/rsync -rlpcni --rsync-path=/usr/bin/rsync --files-from="$ALLOWLIST" \
  --out-format='%i %n%L' "$STAGING/" "$RUNTIME/" \
  > "$VALIDATOR_ROOT/transport-raw-dry-run-1.txt"
LC_ALL=C /usr/bin/rsync -rlpcni --rsync-path=/usr/bin/rsync --files-from="$ALLOWLIST" \
  --stats --out-format='' "$STAGING/" "$RUNTIME/" \
  | awk '/^Number of files transferred:/{print}' \
  > "$VALIDATOR_ROOT/transport-transfer-count-1.txt"
"$VALIDATOR_ROOT/venv/bin/python" "$VALIDATOR_ROOT/review_rsync.py" \
  --raw "$VALIDATOR_ROOT/transport-raw-dry-run-1.txt" \
  --count "$VALIDATOR_ROOT/transport-transfer-count-1.txt" \
  --source-manifest "$STAGING_MANIFEST" \
  --runtime-manifest "$VALIDATOR_ROOT/runtime-pre-1.json" \
  --reviewed "$VALIDATOR_ROOT/transport-reviewed-dry-run-1.txt" \
  --phase pre
```

Expected: the independent manifests allow
exactly the three approved regular-file content differences; the reviewed snapshot has exactly those three update
paths, and the stable count is `Number of files transferred: 3`. Any deletion,
creation, type, mode, symlink, special-file, or unplanned-path difference stops.
A runtime-only deletion requires Hun's exact-path approval; it never authorizes
blanket deletion.

Immediately before synchronization, capture dry-run 2 and byte-compare all raw,
reviewed, stable-count, and independent-manifest evidence:

```bash
set -euo pipefail
set -C
VALIDATOR_ROOT="/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe"
SOURCE="skills/chatgpt-collaboration-harness"
RUNTIME="$HOME/.codex/skills/chatgpt-collaboration-harness"
STAGING="$VALIDATOR_ROOT/reviewed-source"
ALLOWLIST="$VALIDATOR_ROOT/reviewed-allowlist.txt"
STAGING_MANIFEST="$VALIDATOR_ROOT/reviewed-source-manifest.json"
for evidence_path in \
  "$VALIDATOR_ROOT/source-pre-2.json" \
  "$VALIDATOR_ROOT/runtime-pre-2.json" \
  "$VALIDATOR_ROOT/runtime-raw-dry-run-2.txt" \
  "$VALIDATOR_ROOT/runtime-reviewed-dry-run-2.txt" \
  "$VALIDATOR_ROOT/runtime-transfer-count-2.txt" \
  "$VALIDATOR_ROOT/transport-raw-dry-run-2.txt" \
  "$VALIDATOR_ROOT/transport-reviewed-dry-run-2.txt" \
  "$VALIDATOR_ROOT/transport-transfer-count-2.txt"
do
  test ! -e "$evidence_path"
done
"$VALIDATOR_ROOT/venv/bin/python" "$VALIDATOR_ROOT/compare_skill_trees.py" \
  --source "$SOURCE" \
  --runtime "$RUNTIME" \
  --source-manifest "$VALIDATOR_ROOT/source-pre-2.json" \
  --runtime-manifest "$VALIDATOR_ROOT/runtime-pre-2.json" \
  --phase pre
LC_ALL=C /usr/bin/rsync -rlpcni --rsync-path=/usr/bin/rsync --delete --out-format='%i %n%L' \
  "$SOURCE/" "$RUNTIME/" \
  > "$VALIDATOR_ROOT/runtime-raw-dry-run-2.txt"
LC_ALL=C /usr/bin/rsync -rlpcni --rsync-path=/usr/bin/rsync --delete --stats --out-format='' \
  "$SOURCE/" "$RUNTIME/" \
  | awk '/^Number of files transferred:/{print}' \
  > "$VALIDATOR_ROOT/runtime-transfer-count-2.txt"
"$VALIDATOR_ROOT/venv/bin/python" "$VALIDATOR_ROOT/review_rsync.py" \
  --raw "$VALIDATOR_ROOT/runtime-raw-dry-run-2.txt" \
  --count "$VALIDATOR_ROOT/runtime-transfer-count-2.txt" \
  --source-manifest "$VALIDATOR_ROOT/source-pre-2.json" \
  --runtime-manifest "$VALIDATOR_ROOT/runtime-pre-2.json" \
  --reviewed "$VALIDATOR_ROOT/runtime-reviewed-dry-run-2.txt" \
  --phase pre
cmp -- "$VALIDATOR_ROOT/source-pre-1.json" \
  "$VALIDATOR_ROOT/source-pre-2.json"
cmp -- "$VALIDATOR_ROOT/runtime-pre-1.json" \
  "$VALIDATOR_ROOT/runtime-pre-2.json"
cmp -- "$VALIDATOR_ROOT/runtime-raw-dry-run-1.txt" \
  "$VALIDATOR_ROOT/runtime-raw-dry-run-2.txt"
cmp -- "$VALIDATOR_ROOT/runtime-reviewed-dry-run-1.txt" \
  "$VALIDATOR_ROOT/runtime-reviewed-dry-run-2.txt"
cmp -- "$VALIDATOR_ROOT/runtime-transfer-count-1.txt" \
  "$VALIDATOR_ROOT/runtime-transfer-count-2.txt"
"$VALIDATOR_ROOT/venv/bin/python" \
  "$VALIDATOR_ROOT/snapshot_reviewed_source.py" verify \
  --staging "$STAGING" \
  --allowlist "$ALLOWLIST" \
  --source-manifest "$VALIDATOR_ROOT/source-pre-2.json" \
  --staging-manifest "$STAGING_MANIFEST"
LC_ALL=C /usr/bin/rsync -rlpcni --rsync-path=/usr/bin/rsync --files-from="$ALLOWLIST" \
  --out-format='%i %n%L' "$STAGING/" "$RUNTIME/" \
  > "$VALIDATOR_ROOT/transport-raw-dry-run-2.txt"
LC_ALL=C /usr/bin/rsync -rlpcni --rsync-path=/usr/bin/rsync --files-from="$ALLOWLIST" \
  --stats --out-format='' "$STAGING/" "$RUNTIME/" \
  | awk '/^Number of files transferred:/{print}' \
  > "$VALIDATOR_ROOT/transport-transfer-count-2.txt"
"$VALIDATOR_ROOT/venv/bin/python" "$VALIDATOR_ROOT/review_rsync.py" \
  --raw "$VALIDATOR_ROOT/transport-raw-dry-run-2.txt" \
  --count "$VALIDATOR_ROOT/transport-transfer-count-2.txt" \
  --source-manifest "$STAGING_MANIFEST" \
  --runtime-manifest "$VALIDATOR_ROOT/runtime-pre-2.json" \
  --reviewed "$VALIDATOR_ROOT/transport-reviewed-dry-run-2.txt" \
  --phase pre
cmp -- "$VALIDATOR_ROOT/transport-raw-dry-run-1.txt" \
  "$VALIDATOR_ROOT/transport-raw-dry-run-2.txt"
cmp -- "$VALIDATOR_ROOT/transport-reviewed-dry-run-1.txt" \
  "$VALIDATOR_ROOT/transport-reviewed-dry-run-2.txt"
cmp -- "$VALIDATOR_ROOT/transport-transfer-count-1.txt" \
  "$VALIDATOR_ROOT/transport-transfer-count-2.txt"
```

Expected: every `cmp --` exits zero. The staging manifest exactly matches the
allowlisted entries from source-pre-2.json, both transport dry runs use the
same reviewed staging snapshot and exact three-path allowlist, their raw,
reviewed, and stable-count evidence is byte-identical, and the count is
`Number of files transferred: 3`. Any difference invalidates the review and
every prior deletion approval.

- [ ] **Step 6: Synchronize without blanket deletion**

Only after dry-run 2 and every comparison succeed, recapture the full live
source/runtime manifests, revalidate the reviewed subset, record the runtime
root identity, and synchronize from staging. The mutation source is the
reviewed staging snapshot, never the live source tree:

Binding contract: mutation source is the reviewed staging snapshot; staging manifest exactly matches the allowlisted entries from source-pre-2.json; immutable reviewed staging snapshot and exact allowlist are the mutation safety boundary. The legacy `rsync -rlpc \` live-source form is forbidden.

```bash
set -euo pipefail
VALIDATOR_ROOT="/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe"
SOURCE="skills/chatgpt-collaboration-harness"
RUNTIME="$HOME/.codex/skills/chatgpt-collaboration-harness"
STAGING="$VALIDATOR_ROOT/reviewed-source"
ALLOWLIST="$VALIDATOR_ROOT/reviewed-allowlist.txt"
STAGING_MANIFEST="$VALIDATOR_ROOT/reviewed-source-manifest.json"
for evidence_path in \
  "$VALIDATOR_ROOT/source-pre-final.json" \
  "$VALIDATOR_ROOT/runtime-pre-final.json" \
  "$VALIDATOR_ROOT/runtime-root-before-sync.json"
do
  test ! -e "$evidence_path"
done
"$VALIDATOR_ROOT/venv/bin/python" "$VALIDATOR_ROOT/compare_skill_trees.py" \
  --source "$SOURCE" \
  --runtime "$RUNTIME" \
  --source-manifest "$VALIDATOR_ROOT/source-pre-final.json" \
  --runtime-manifest "$VALIDATOR_ROOT/runtime-pre-final.json" \
  --phase pre
cmp -- "$VALIDATOR_ROOT/source-pre-2.json" \
  "$VALIDATOR_ROOT/source-pre-final.json"
cmp -- "$VALIDATOR_ROOT/runtime-pre-2.json" \
  "$VALIDATOR_ROOT/runtime-pre-final.json"
"$VALIDATOR_ROOT/venv/bin/python" \
  "$VALIDATOR_ROOT/snapshot_reviewed_source.py" verify \
  --staging "$STAGING" \
  --allowlist "$ALLOWLIST" \
  --source-manifest "$VALIDATOR_ROOT/source-pre-2.json" \
  --staging-manifest "$STAGING_MANIFEST"
"$VALIDATOR_ROOT/venv/bin/python" \
  "$VALIDATOR_ROOT/snapshot_reviewed_source.py" identity \
  --root "$RUNTIME" \
  --output "$VALIDATOR_ROOT/runtime-root-before-sync.json"
"$VALIDATOR_ROOT/venv/bin/python" \
  "$VALIDATOR_ROOT/snapshot_reviewed_source.py" check-identity \
  --root "$RUNTIME" \
  --expected "$VALIDATOR_ROOT/runtime-root-before-sync.json"
/usr/bin/rsync -rlpc --rsync-path=/usr/bin/rsync --files-from="$ALLOWLIST" \
  "$STAGING/" "$RUNTIME/"
```

Do not add `-t`, `-a`, or the deletion flag. Do not substitute `$SOURCE/` for
`$STAGING/`; the actual mutation must consume the exact bytes reviewed in the
staging manifest. If an exact runtime-only path was separately approved for
deletion, revalidate only that path immediately before removing it; do not
remove any other path.

- [ ] **Step 7: Validate the installed copy and exact equality**

Capture collision-checked post-sync manifests, raw output, reviewed output, and
stable count:

```bash
set -euo pipefail
set -C
OLD_VALIDATOR_ROOT="/tmp/chatgpt-multi-format-validator-20260713"
VALIDATOR_ROOT="/tmp/chatgpt-multi-format-validator-20260713-content-only-pathsafe"
SOURCE="skills/chatgpt-collaboration-harness"
RUNTIME="$HOME/.codex/skills/chatgpt-collaboration-harness"
STAGING="$VALIDATOR_ROOT/reviewed-source"
ALLOWLIST="$VALIDATOR_ROOT/reviewed-allowlist.txt"
STAGING_MANIFEST="$VALIDATOR_ROOT/reviewed-source-manifest.json"
for evidence_path in \
  "$VALIDATOR_ROOT/source-post.json" \
  "$VALIDATOR_ROOT/runtime-post.json" \
  "$VALIDATOR_ROOT/runtime-root-after-sync.json" \
  "$VALIDATOR_ROOT/transport-raw-post.txt" \
  "$VALIDATOR_ROOT/transport-reviewed-post.txt" \
  "$VALIDATOR_ROOT/transport-transfer-count-post.txt"
do
  test ! -e "$evidence_path"
done
"$VALIDATOR_ROOT/venv/bin/python" \
  "$VALIDATOR_ROOT/snapshot_reviewed_source.py" identity \
  --root "$RUNTIME" \
  --output "$VALIDATOR_ROOT/runtime-root-after-sync.json"
cmp -- "$VALIDATOR_ROOT/runtime-root-before-sync.json" \
  "$VALIDATOR_ROOT/runtime-root-after-sync.json"
"$VALIDATOR_ROOT/venv/bin/python" \
  "$VALIDATOR_ROOT/snapshot_reviewed_source.py" check-identity \
  --root "$RUNTIME" \
  --expected "$VALIDATOR_ROOT/runtime-root-before-sync.json"
"$VALIDATOR_ROOT/venv/bin/python" "$VALIDATOR_ROOT/compare_skill_trees.py" \
  --source "$SOURCE" \
  --runtime "$RUNTIME" \
  --source-manifest "$VALIDATOR_ROOT/source-post.json" \
  --runtime-manifest "$VALIDATOR_ROOT/runtime-post.json" \
  --phase capture
cmp -- "$VALIDATOR_ROOT/source-pre-2.json" \
  "$VALIDATOR_ROOT/runtime-post.json"
"$VALIDATOR_ROOT/venv/bin/python" \
  "$VALIDATOR_ROOT/snapshot_reviewed_source.py" verify \
  --staging "$STAGING" \
  --allowlist "$ALLOWLIST" \
  --source-manifest "$VALIDATOR_ROOT/source-pre-2.json" \
  --staging-manifest "$STAGING_MANIFEST"
cmp -- "$VALIDATOR_ROOT/source-pre-2.json" \
  "$VALIDATOR_ROOT/source-post.json"
cmp -- "$VALIDATOR_ROOT/source-post.json" \
  "$VALIDATOR_ROOT/runtime-post.json"
LC_ALL=C /usr/bin/rsync -rlpcni --rsync-path=/usr/bin/rsync --files-from="$ALLOWLIST" \
  --out-format='%i %n%L' "$STAGING/" "$RUNTIME/" \
  > "$VALIDATOR_ROOT/transport-raw-post.txt"
LC_ALL=C /usr/bin/rsync -rlpcni --rsync-path=/usr/bin/rsync --files-from="$ALLOWLIST" \
  --stats --out-format='' "$STAGING/" "$RUNTIME/" \
  | awk '/^Number of files transferred:/{print}' \
  > "$VALIDATOR_ROOT/transport-transfer-count-post.txt"
"$VALIDATOR_ROOT/venv/bin/python" "$VALIDATOR_ROOT/review_rsync.py" \
  --raw "$VALIDATOR_ROOT/transport-raw-post.txt" \
  --count "$VALIDATOR_ROOT/transport-transfer-count-post.txt" \
  --source-manifest "$STAGING_MANIFEST" \
  --runtime-manifest "$VALIDATOR_ROOT/runtime-post.json" \
  --reviewed "$VALIDATOR_ROOT/transport-reviewed-post.txt" \
  --phase post
test ! -s "$VALIDATOR_ROOT/transport-reviewed-post.txt"
grep -Fx "Number of files transferred: 0" \
  "$VALIDATOR_ROOT/transport-transfer-count-post.txt"
"$VALIDATOR_ROOT/venv/bin/python" \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  "$RUNTIME"
diff -ru "$SOURCE" "$RUNTIME"
shasum -a 256 -c "$VALIDATOR_ROOT/old-red-snapshot.sha256"
test -s "$OLD_VALIDATOR_ROOT/runtime-dry-run-1.txt"
```

Expected: the runtime full manifest equals the reviewed source-pre-2 full manifest
before any live-source comparison; staging still equals the approved subset;
live source still equals source-pre-2; runtime root identity is unchanged.
The post-sync reviewed dry run is empty, the stable count is
`Number of files transferred: 0`, post-sync manifests are exactly equal,
`quick_validate.py` reports `Skill is valid!`, `diff -ru` has no output, and
the old stopped RED snapshot still matches its recorded hash. If live source
drifted during synchronization, the live-source comparison and final diff fail,
but the earlier runtime-versus-reviewed comparison proves that installed bytes
still came from the reviewed staging payload.

### Task 5: Pressure-Test, Review, And Correct The Final Branch

**Files:**
- Review all branch changes since `origin/main`.
- Modify only the scoped test, skill, plan, or design files if a verified defect
  requires correction.

- [ ] **Step 1: Forward-test the installed runtime skill**

Give a fresh worker only this raw scenario, not this plan or expected answer:

```text
ChatGPT Pro must receive a mixed packet containing PNG, PDF, DOCX, and ZIP.
Chrome direct file attachment may fail, and clipboard behavior differs by MIME.
Explain the exact transport decision, evidence required before fallback, what
must never be sent, and what an unsent composer preview proves.
```

Expected: the worker reads both references, uses direct chooser first, consults
the exact format/MIME matrix, never generalizes API success, uses manual
attachment for an unverified clipboard route, and distinguishes staging from
delivery.

- [ ] **Step 2: Run two independent local reviews**

Dispatch one reviewer for spec/requirement compliance and one for test quality,
safety boundaries, and overclaims. Give both reviewers the design, plan, branch
diff, RED/GREEN evidence, synthetic-smoke matrix, validator output, and
source/runtime diff result. Require findings with file/line evidence and
severity; no file edits.

Expected: every finding is classified as accepted, rejected, deferred, or
needs-local-verification by the primary worker.

- [ ] **Step 3: Request ChatGPT Pro final review with public-safe excerpts**

Use a clean ChatGPT Pro conversation and send only:

- the goal and bounded format list;
- the three changed relative skill paths;
- public-safe changed excerpts;
- summarized RED/GREEN, browser staging, validator, and runtime-diff evidence;
- known limits: no send, preview is not delivery, and user-reported ZIP evidence
  is distinct from this smoke.

Omit synthetic binaries, repository/Git URLs, browser state, authentication
state, private paths, and unrelated project material. Ask in Korean for
contradictions, unsafe permission assumptions, MIME overgeneralization, weak
tests, and evidence overclaims. Require source-backed support for browser or
OpenAI product claims.

- [ ] **Step 4: Apply accepted corrections through TDD**

For each accepted behavior correction:

1. add or tighten the failing contract assertion;
2. run the focused test and preserve RED;
3. make the smallest scoped reference change;
4. rerun focused GREEN and the private-path check;
5. commit the correction.

Use this exact staging set only for files that actually changed:

```bash
set -euo pipefail
git status --short
git add tests/test_skill_catalog.py \
  docs/superpowers/plans/2026-07-13-chatgpt-multi-format-attachments.md \
  docs/superpowers/specs/2026-07-13-chatgpt-multi-format-attachments-design.md \
  skills/chatgpt-collaboration-harness/SKILL.md \
  skills/chatgpt-collaboration-harness/references/chrome-chatgpt-pro.md \
  skills/chatgpt-collaboration-harness/references/file-artifact-exchange.md
git commit -m "fix: address multi-format attachment review"
```

If any installed skill source changes, preserve every prior validator and
snapshot, choose a fresh collision-checked content-only validator suffix, and
repeat Task 4's independent manifests, pressure cases, two raw/reviewed/count
pre-sync evidence sets, exclusive reviewed staging snapshot, exact allowlist,
staging-bound transport dry runs and mutation, runtime-root identity checks,
post-sync validator, exact manifest equality, and recursive diff. Prior
snapshots and deletion approvals are invalid.

- [ ] **Step 5: Run final branch verification**

Run:

```bash
set -euo pipefail
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_private_paths.py
python3 scripts/audit_agent_stack.py
git diff --check origin/main..HEAD
git status --short --branch
```

Expected: all tests and audits pass, the diff check emits nothing, and the
feature worktree is clean.

### Task 6: Obtain Protected-Branch Approval And Integrate Main

**Files:**
- No new file changes expected.
- Primary worktree: repository root where `main` is already checked out.

- [ ] **Step 1: Present the final action-time evidence to Hun**

Report the exact feature commit, changed files, per-format direct/clipboard
matrix, all test and validator results, source/runtime equality, independent
review disposition, temporary fixture directory, and remaining limitations.
Ask Hun for explicit permission to fast-forward and push protected `main`.

Stop here until Hun explicitly approves that protected-branch action. Prior
general permission to implement or update the runtime skill is not a substitute
for action-time protected-branch approval.

- [ ] **Step 2: Verify both worktrees before integration**

After approval, run:

```bash
set -euo pipefail
git worktree list --porcelain
git status --short --branch
```

Run the second status command in both the feature worktree and the primary
`main` worktree. Stop and ask how to handle any uncommitted or untracked file.

- [ ] **Step 3: Fast-forward, verify, and push from the primary worktree**

Run only in the primary worktree where `main` is checked out:

```bash
set -euo pipefail
git pull --ff-only origin main
git merge --ff-only codex/chatgpt-upload-fallback
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_private_paths.py
python3 scripts/audit_agent_stack.py
git diff --check origin/main..HEAD
git push origin main
```

Stop instead of rebasing, force-pushing, or rewriting history if `origin/main`
changed incompatibly. Preserve every hook.

- [ ] **Step 4: Prove final remote state**

Run:

```bash
set -euo pipefail
git fetch origin
git rev-parse HEAD
git rev-parse origin/main
git ls-remote origin refs/heads/main
git status --short --branch
```

Expected: local `HEAD`, `origin/main`, and the remote `refs/heads/main` SHA all
match; `main` is clean and not ahead or behind.
