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
- Do not modify repository files.

- [ ] **Step 1: Resolve and isolate the bundled artifact runtimes**

Call the workspace dependency resolver and use only its returned bundled
Python executable, bundled Node executable, and bundled `node_modules`
directory. Also set `DOCUMENTS_SKILL_DIR` and `PRESENTATIONS_SKILL_DIR` from the
absolute directories of the currently loaded installed skills; do not guess or
hardcode a versioned cache path. Confirm the required files and imports without
installing anything:

```bash
test -x "$BUNDLED_PYTHON"
test -x "$BUNDLED_NODE"
test -d "$BUNDLED_NODE_MODULES"
test -f "$DOCUMENTS_SKILL_DIR/render_docx.py"
test -f "$PRESENTATIONS_SKILL_DIR/container_tools/setup_artifact_tool_workspace.mjs"
test -f "$PRESENTATIONS_SKILL_DIR/container_tools/slides_test.py"
"$BUNDLED_PYTHON" -c "import PIL, reportlab, docx, pypdf; print('python artifact imports: ok')"
```

Before creating anything, require every disposable top-level path to be absent:

```bash
GENERATOR="/tmp/chatgpt-multi-format-generate-20260713.py"
BUILD_ROOT="/tmp/chatgpt-multi-format-artifact-workspace-20260713"
FIXTURE_ROOT="/tmp/chatgpt-multi-format-smoke-20260713"
QA_ROOT="/tmp/chatgpt-multi-format-qa-20260713"
test ! -e "$GENERATOR"
test ! -e "$BUILD_ROOT"
test ! -e "$FIXTURE_ROOT"
test ! -e "$QA_ROOT"
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
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

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
await fs.writeFile(
  path.join(qaRoot, "xlsx-inspect.ndjson"),
  `${structure.ndjson}\n${content.ndjson}\n`,
  "utf8",
);

const preview = await workbook.render({
  sheetName: "Smoke",
  range: "A1:B2",
  autoCrop: "all",
  scale: 2,
  format: "png",
});
await writeBlob(path.join(qaRoot, "sample-xlsx.png"), preview);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, qaRoot, marker }, null, 2));
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
import path from "node:path";
import {
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
await fs.writeFile(
  path.join(qaRoot, "pptx-inspect.ndjson"),
  `${inspection.ndjson}\n`,
  "utf8",
);
const layout = await slide.export({ format: "layout" });
await fs.writeFile(
  path.join(qaRoot, "pptx-layout.json"),
  await layout.text(),
  "utf8",
);
const preview = await presentation.export({
  slide,
  format: "png",
  scale: 2,
});
await writeBlob(path.join(qaRoot, "sample-pptx.png"), preview);

const output = await PresentationFile.exportPptx(presentation);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, qaRoot, marker }, null, 2));
```

- [ ] **Step 3: Generate and locally validate all eleven fixtures**

Run:

```bash
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
artifact-tool builders pass Node syntax checks, inspect their marker content,
render non-empty previews, and export real Office files; the final generator
invocation prints exactly eleven manifest entries in the approved order with
MIME, non-zero size, and SHA-256; `file` recognizes every real format; and the
ZIP contains only safe `README.txt` and passes its integrity test.

Run the format-specific render gates:

```bash
mkdir "$QA_ROOT/docx" "$QA_ROOT/pdf"
"$BUNDLED_PYTHON" "$DOCUMENTS_SKILL_DIR/render_docx.py" \
  "$FIXTURE_ROOT/sample.docx" --output_dir "$QA_ROOT/docx"
PDFTOPPM="$(command -v pdftoppm)"
test -x "$PDFTOPPM"
"$PDFTOPPM" -png "$FIXTURE_ROOT/sample.pdf" "$QA_ROOT/pdf/sample"
"$BUNDLED_PYTHON" "$PRESENTATIONS_SKILL_DIR/container_tools/slides_test.py" \
  "$FIXTURE_ROOT/sample.pptx"
test -s "$QA_ROOT/docx/page-1.png"
test -s "$QA_ROOT/pdf/sample-1.png"
test -s "$QA_ROOT/xlsx/sample-xlsx.png"
test -s "$QA_ROOT/pptx/sample-pptx.png"
test -s "$QA_ROOT/xlsx/xlsx-inspect.ndjson"
test -s "$QA_ROOT/pptx/pptx-inspect.ndjson"
test -s "$QA_ROOT/pptx/pptx-layout.json"
```

Use the host image-viewing capability at 100% zoom on all four render outputs:

- `$QA_ROOT/docx/page-1.png`
- `$QA_ROOT/pdf/sample-1.png`
- `$QA_ROOT/xlsx/sample-xlsx.png`
- `$QA_ROOT/pptx/sample-pptx.png`

Also read the compact XLSX inspection, PPTX inspection, and PPTX layout JSON.
The DOCX page must show its heading and full marker without clipping; the PDF
must show its title and marker with clean margins; the spreadsheet must show
both cells, full marker text, and legible styling; the slide must preserve the
selected Codex Grid hierarchy, show the full 80px title and 32px marker, and
contain no overlap, overflow, out-of-bounds content, or ignored layout warning.
Any visual or layout defect is a failure. Preserve the failed evidence,
allocate a new absent suffix for build, fixture, and QA roots, create the
corrected builder under that new build root with `apply_patch`, and re-run the
full generation/render/inspection gate. Do not overwrite or delete the first
attempt, and do not use a different authoring library as a fallback.

Keep the fixture, build, and QA directories until final reporting. They are
disposable and synthetic, but do not delete them automatically, copy them into
Git, or commit any binary output.

- [ ] **Step 4: Establish a fresh Chrome staging surface**

Invoke the Chrome control skill, initialize the extension-backed browser with
the documented browser-client route, and read the complete selected-browser
documentation plus `file-uploads` documentation. Use a Codex-owned ChatGPT tab
or a new clean composer, and do not reuse the stale chooser from before the
permission change. Define the exact fixture inventory in the JavaScript browser
session using the fixed fixture root from Step 3:

```js
const fixtureRoot = "/tmp/chatgpt-multi-format-smoke-20260713";
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
```

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
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_private_paths.py
python3 scripts/audit_agent_stack.py
git diff --check
```

Expected: the full test count is at least the 288-test design baseline plus the
net new contract test, both scripts pass with pristine output, and the diff
check emits nothing. Any failure is in scope and must be resolved before sync.

- [ ] **Step 2: Create a disposable validator environment**

Run:

```bash
VALIDATOR_ROOT="$(mktemp -d /tmp/chatgpt-multi-format-validator.XXXXXX)"
python3 -m venv "$VALIDATOR_ROOT/venv"
"$VALIDATOR_ROOT/venv/bin/python" -m pip install PyYAML
```

Expected: PyYAML installs only inside the disposable environment. Do not modify
system Python.

- [ ] **Step 3: Validate the repository skill**

Run:

```bash
"$VALIDATOR_ROOT/venv/bin/python" \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/chatgpt-collaboration-harness
```

Expected: `Skill is valid!`.

- [ ] **Step 4: Review two identical checksum-aware dry runs**

Run the first snapshot:

```bash
rsync -acni --delete \
  skills/chatgpt-collaboration-harness/ \
  ~/.codex/skills/chatgpt-collaboration-harness/ \
  > "$VALIDATOR_ROOT/runtime-dry-run-1.txt"
cat "$VALIDATOR_ROOT/runtime-dry-run-1.txt"
```

The only expected non-noop records are regular-file updates for:

- `SKILL.md`
- `references/chrome-chatgpt-pro.md`
- `references/file-artifact-exchange.md`

Stop on an unexpected path, creation, deletion, file-type change, symlink
change, or standalone metadata-only change. A runtime-only deletion requires
Hun's exact-path approval and must never be converted into blanket delete
authorization.

Immediately before sync, run:

```bash
rsync -acni --delete \
  skills/chatgpt-collaboration-harness/ \
  ~/.codex/skills/chatgpt-collaboration-harness/ \
  > "$VALIDATOR_ROOT/runtime-dry-run-2.txt"
cmp "$VALIDATOR_ROOT/runtime-dry-run-1.txt" \
  "$VALIDATOR_ROOT/runtime-dry-run-2.txt"
```

Expected: `cmp` exits zero. Any difference invalidates the review and every
prior deletion approval.

- [ ] **Step 5: Synchronize without blanket deletion**

Only after the reviewed dry runs are identical, run:

```bash
rsync -ac \
  skills/chatgpt-collaboration-harness/ \
  ~/.codex/skills/chatgpt-collaboration-harness/
```

Do not use `--delete`. If an exact runtime-only path was separately approved
for deletion, revalidate only that path immediately before removing it; do not
remove any other path.

- [ ] **Step 6: Validate and compare the installed copy**

Run:

```bash
"$VALIDATOR_ROOT/venv/bin/python" \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  ~/.codex/skills/chatgpt-collaboration-harness
rsync -acni --delete \
  skills/chatgpt-collaboration-harness/ \
  ~/.codex/skills/chatgpt-collaboration-harness/
diff -ru \
  skills/chatgpt-collaboration-harness \
  ~/.codex/skills/chatgpt-collaboration-harness
```

Expected: `Skill is valid!`, then no `rsync` output and no recursive diff.

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
git status --short
git add tests/test_skill_catalog.py \
  docs/superpowers/plans/2026-07-13-chatgpt-multi-format-attachments.md \
  docs/superpowers/specs/2026-07-13-chatgpt-multi-format-attachments-design.md \
  skills/chatgpt-collaboration-harness/SKILL.md \
  skills/chatgpt-collaboration-harness/references/chrome-chatgpt-pro.md \
  skills/chatgpt-collaboration-harness/references/file-artifact-exchange.md
git commit -m "fix: address multi-format attachment review"
```

If any installed skill source changes, repeat all guarded dry-run,
synchronization, installed validator, and recursive diff steps from Task 4 with
a fresh snapshot. Prior snapshots and deletion approvals are invalid.

- [ ] **Step 5: Run final branch verification**

Run:

```bash
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
git worktree list --porcelain
git status --short --branch
```

Run the second status command in both the feature worktree and the primary
`main` worktree. Stop and ask how to handle any uncommitted or untracked file.

- [ ] **Step 3: Fast-forward, verify, and push from the primary worktree**

Run only in the primary worktree where `main` is checked out:

```bash
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
git fetch origin
git rev-parse HEAD
git rev-parse origin/main
git ls-remote origin refs/heads/main
git status --short --branch
```

Expected: local `HEAD`, `origin/main`, and the remote `refs/heads/main` SHA all
match; `main` is clean and not ahead or behind.
