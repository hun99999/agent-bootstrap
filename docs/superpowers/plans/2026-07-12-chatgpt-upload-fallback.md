# ChatGPT Pro Upload Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the ChatGPT collaboration harness diagnose Chrome local-file denial without overclaiming its cause, stage approved PNGs through a verified clipboard fallback, synchronize the installed runtime copy, and integrate the validated change into `main`.

**Architecture:** Keep `SKILL.md` as the compact router, place Chrome file-chooser diagnosis in `references/chrome-chatgpt-pro.md`, and place PNG-only verified clipboard staging and exact-packet evidence rules in `references/file-artifact-exchange.md`. Enforce the process with repository contract tests, then mechanically synchronize and independently validate the installed runtime copy.

**Tech Stack:** Markdown skills and references, Python 3 `unittest`, Codex skill validator with PyYAML, Chrome browser-client runtime, Git.

---

## File Structure

- Modify: `tests/test_skill_catalog.py`
- Modify: `skills/chatgpt-collaboration-harness/SKILL.md`
- Modify: `skills/chatgpt-collaboration-harness/references/chrome-chatgpt-pro.md`
- Modify: `skills/chatgpt-collaboration-harness/references/file-artifact-exchange.md`
- Synchronize after repository validation: `~/.codex/skills/chatgpt-collaboration-harness/`

No new dependency, script, configuration file, browser-profile edit, or skill
directory is required.

### Task 1: Add The RED Skill Contracts

**Files:**
- Modify: `tests/test_skill_catalog.py`
- Test: `tests/test_skill_catalog.py`

- [ ] **Step 1: Add the Chrome upload diagnosis test**

Add this method to `SkillCatalogTests`:

```python
def test_chatgpt_collaboration_harness_diagnoses_chrome_upload_failures(
    self,
) -> None:
    skill_root = REPO_ROOT / "skills" / "chatgpt-collaboration-harness"
    skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    reference = (skill_root / "references" / "chrome-chatgpt-pro.md").read_text(
        encoding="utf-8"
    )

    self.assertIn("Chrome file upload fails", skill)
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
```

- [ ] **Step 2: Add the verified clipboard fallback test**

Add this second method:

```python
def test_chatgpt_collaboration_harness_documents_verified_clipboard_fallback(
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
        "Verified Clipboard Image Fallback",
        "approved attachment-sharing scope",
        "`tab.clipboard.write(...)`",
        "Base64-encode",
        "`base64`",
        "`mimeType`",
        "image MIME type",
        "one image at a time",
        "attachment preview",
        "visible attachment count",
        "Do not send",
        "non-image files",
        "persisted outgoing message",
        "Composer previews prove staging, not delivery",
    )
    for phrase in expected_phrases:
        self.assertIn(phrase, reference)
    self.assertNotIn(PRIVATE_HOME_PATH, reference)
```

- [ ] **Step 3: Run the focused tests and observe RED**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_skill_catalog.py' -v
```

Expected: the two new tests fail because the current skill has neither the
Chrome permission diagnosis contract nor the verified clipboard fallback.
Existing catalog tests must remain green.

- [ ] **Step 4: Commit the RED tests**

```bash
git add tests/test_skill_catalog.py
git commit -m "test: define ChatGPT upload fallback contract"
```

### Task 2: Implement The Minimal Repository Skill Change

**Files:**
- Modify: `skills/chatgpt-collaboration-harness/SKILL.md`
- Modify: `skills/chatgpt-collaboration-harness/references/chrome-chatgpt-pro.md`
- Modify: `skills/chatgpt-collaboration-harness/references/file-artifact-exchange.md`
- Test: `tests/test_skill_catalog.py`

- [ ] **Step 1: Route upload failures from `SKILL.md`**

Add one Required Components bullet after the existing file-artifact bullet:

```markdown
- When Chrome file upload fails or approved PNGs need a clipboard fallback,
  read both `references/chrome-chatgpt-pro.md` and
  `references/file-artifact-exchange.md` before retrying, changing permissions,
  pasting, or reporting a blocker.
```

- [ ] **Step 2: Add `File Upload Diagnosis` to the Chrome reference**

Document this exact decision path:

```markdown
## File Upload Diagnosis

Before uploading, read the selected browser's `file-uploads` documentation.
Start the `filechooser` wait before activating the visible attachment control,
use absolute paths with `chooser.setFiles(...)`, and call
`chooser.isMultiple()` before passing more than one path.

Do not diagnose a permission failure from a hidden input click or an unopened
picker. Diagnose the boundary from the awaited `chooser.setFiles(...)`
fulfillment or rejection and the visible composer state. The API resolves with
no result value.

If the underlying chooser rejection is `Not allowed`, Chrome may instead
surface the packaged permission instruction. Read
`chrome-file-upload-troubleshooting` and reproduce its current instruction
verbatim, including its details link. The current user-directed check is to
open `chrome://extensions`, select Details for the ChatGPT Chrome Extension,
and enable **Allow access to file URLs**; see the
[OpenAI file-upload guide](https://developers.openai.com/codex/app/chrome-extension#upload-files).
Opening the Extension Manager is approval-gated.
The permission change requires action-time confirmation.
The permission change remains user-directed.

Do not work around a blocked `chrome://` page through another browser surface,
raw browser commands, profile-file edits, or indirect extension-state changes.
For approved PNGs, use the Verified Clipboard Image Fallback in
`file-artifact-exchange.md`; for non-image files, require a supported upload
route or manual attachment.
```

- [ ] **Step 3: Add `Verified Clipboard Image Fallback` to the artifact reference**

Document the verified image-only sequence:

```markdown
## Verified Clipboard Image Fallback

Use this only for approved PNG attachments after direct file upload is
unavailable. The verified scope is limited to `image/png`; changing transport
does not widen the approved files or ChatGPT destination.

1. Record the approved PNG manifest index, intended order and count, MIME type,
   and non-sensitive aliases. Do not use this route for other MIME types.
2. Establish a clean packet baseline with no preview, error, pending state, or
   text beyond the exact approved prompt.
3. In manifest order, write one PNG through the nested clipboard-item shape and
   await the call before pasting:

   ```js
   await tab.clipboard.write([
     {
       entries: [{ base64: encodedBytes, mimeType: "image/png" }],
     },
   ]);
   ```

4. Focus the verified composer and use the virtual clipboard paste call:

   ```js
   await tab.cua.keypress({ keys: ["ControlOrMeta", "v"] });
   ```

5. After each paste, require the preview count to equal the manifest index and
   require no error or pending state. Count proves staging, not byte identity.
6. Before sending, verify the exact packet: approved prompt, intended preview
   count and order, no unexpected content, and no error or pending state.
7. On a failed or ambiguous paste, do not send a partial packet. Remove only
   unambiguous draft attachments from the failed attempt; otherwise report the
   exact draft state.
8. When delivery is required, verify the persisted outgoing message after
   sending. Composer previews prove staging, not delivery.

Clipboard paste may expose generated names. Never include absolute paths; use
non-sensitive aliases and include an original basename only when separately
approved for the destination.
```

- [ ] **Step 4: Run GREEN**

```bash
python3 -m unittest discover -s tests -p 'test_skill_catalog.py' -v
git diff --check
```

Expected: all skill-catalog tests pass with pristine output and no whitespace
errors.

- [ ] **Step 5: Review and commit the repository skill**

Inspect the diff for unrelated prose, duplicated rules, private paths, invented
browser APIs, or claims stronger than the observed evidence. Then commit:

```bash
git add skills/chatgpt-collaboration-harness/SKILL.md \
  skills/chatgpt-collaboration-harness/references/chrome-chatgpt-pro.md \
  skills/chatgpt-collaboration-harness/references/file-artifact-exchange.md
git commit -m "fix: add ChatGPT clipboard upload fallback"
```

### Task 3: Synchronize And Validate The Runtime Skill

**Files:**
- Source: `skills/chatgpt-collaboration-harness/`
- Synchronize: `~/.codex/skills/chatgpt-collaboration-harness/`

- [ ] **Step 1: Run repository-wide validation before installation**

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_private_paths.py
python3 scripts/audit_agent_stack.py
git diff --check
```

Expected: all tests and audits pass with no errors or warnings attributable to
the change.

- [ ] **Step 2: Create a disposable validator environment**

```bash
VALIDATOR_ROOT="$(mktemp -d /tmp/chatgpt-skill-validator.XXXXXX)"
python3 -m venv "$VALIDATOR_ROOT/venv"
"$VALIDATOR_ROOT/venv/bin/python" -m pip install PyYAML
```

Expected: PyYAML installs only inside the disposable environment; system Python
remains unchanged.

- [ ] **Step 3: Validate the repository skill**

```bash
"$VALIDATOR_ROOT/venv/bin/python" \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/chatgpt-collaboration-harness
```

Expected: `Skill is valid!`

- [ ] **Step 4: Synchronize only the approved skill**

```bash
diff -rq \
  skills/chatgpt-collaboration-harness \
  ~/.codex/skills/chatgpt-collaboration-harness
rsync -acni --delete \
  skills/chatgpt-collaboration-harness/ \
  ~/.codex/skills/chatgpt-collaboration-harness/
```

Inspect every non-noop itemized record. The only expected records are
regular-file updates at the three approved paths:

- `SKILL.md`
- `references/chrome-chatgpt-pro.md`
- `references/file-artifact-exchange.md`

Stop on any unexpected path, creation, file-type change, symlink change,
standalone metadata-only change, or deletion. A proposed deletion may proceed
only after Hun explicitly approves the exact runtime-only path; approval to
update the skill is not blanket approval to delete unknown runtime-only files.

After reviewing the output and obtaining any required deletion approval,
repeat the checksum-aware dry run immediately before synchronization. The new
output must be identical to the reviewed output.
Any difference invalidates every prior deletion approval and requires a new
review before continuing. Only proceed when the repeated output is identical
and either no deletion is proposed or every exact deletion is separately
approved by Hun.
The actual synchronization uses the same checksum comparison as the dry run
and never applies a blanket deletion. Then run:

```bash
rsync -ac \
  skills/chatgpt-collaboration-harness/ \
  ~/.codex/skills/chatgpt-collaboration-harness/
```

If the dry run listed an exact deletion that Hun separately approved, recheck
that the same path is still unchanged and runtime-only immediately before
deleting only that path. Do not use a blanket deletion command.

Do not copy credentials, browser profiles, auth state, Chrome permissions, or
any other catalog skill.

- [ ] **Step 5: Validate and compare the installed copy**

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

Expected: `Skill is valid!`, no checksum dry-run output, and no recursive diff
output.

- [ ] **Step 6: Forward-test the installed skill**

Start a fresh subagent with only this raw task: six approved local PNGs must be
sent to a logged-in ChatGPT Pro conversation, while Chrome reports local-file
access denial. Require the agent to use the installed skill, propose the exact
diagnostic and fallback sequence, distinguish images from non-image files, and
state staging-versus-delivery evidence. Do not include this plan or the intended
answer in the subagent context.

Expected: the agent reads both references, does not attempt a `chrome://`
workaround, uses clipboard bytes only for images, verifies every preview, and
does not claim delivery from an unsent composer.

### Task 4: Obtain Final Review And Integrate Main

**Files:**
- Review the branch diff and validation evidence.
- Modify only the already scoped files if final review identifies a verified defect.

- [ ] **Step 1: Build the public-safe final review packet**

Include the final objective, stage summary, changed relative paths, relevant
changed excerpts, RED/GREEN evidence, browser reproduction summary, six-preview
smoke result, repository/runtime validator results, complete test/audit results,
and known limitations. Omit user images, repository and Git URLs, browser state,
authentication state, private absolute paths, and unrelated project context.

- [ ] **Step 2: Request ChatGPT Pro normal-chat final review**

Ask in Korean for defects, missed constraints, unsafe permission assumptions,
clipboard edge cases, and overclaims. Require each item to be labeled
`accepted`, `rejected`, `deferred`, or `needs-local-verification` and require
source-backed claims when browser behavior or official guidance is asserted.

- [ ] **Step 3: Classify feedback and apply only verified corrections**

For every suggestion, compare it with repository source, selected Chrome plugin
documentation, and observed browser evidence. Apply only accepted corrections,
then rerun the focused tests, both validators, the full suite, private-path scan,
agent-stack audit, recursive runtime diff, and `git diff --check`.

If any file under `skills/chatgpt-collaboration-harness/` changes, first
repeat the complete guarded synchronization and installed-copy validation
from Task 3 using a fresh dry-run snapshot.
Prior dry-run output and deletion approvals are invalid after a skill change.
If only tests, plan, or design files change, no runtime synchronization is
needed.

Accepted corrections must keep `Not allowed` conditional, include the
fresh-task verification step from the current official OpenAI guide after a
permission change, require action-time confirmation for that change, limit
verified clipboard evidence to PNG, require a clean composer baseline and exact
packet before send, await every clipboard write, preserve the documented
clipboard-item `entries` shape and virtual paste call, avoid sole-cause
attribution after a multi-step remediation, and use
non-sensitive manifest aliases. Reject any review claim contradicted by the
source, including an assertion that
`chooser.isMultiple()` is checked after multiple paths when the reference
already requires the check before passing more than one path.

- [ ] **Step 4: Commit any final-review correction**

If files changed:

```bash
git add tests/test_skill_catalog.py \
  docs/superpowers/plans/2026-07-12-chatgpt-upload-fallback.md \
  docs/superpowers/specs/2026-07-12-chatgpt-upload-fallback-design.md \
  skills/chatgpt-collaboration-harness/SKILL.md \
  skills/chatgpt-collaboration-harness/references/chrome-chatgpt-pro.md \
  skills/chatgpt-collaboration-harness/references/file-artifact-exchange.md
git commit -m "fix: address ChatGPT upload fallback review"
```

If no files changed, record that no corrective commit was needed.

- [ ] **Step 5: Fast-forward `main` and push**

Verify both the feature worktree and the primary `main` worktree are clean.
Run these commands in the primary worktree where `main` is already checked out,
not in the feature worktree:

```bash
git worktree list --porcelain
git pull --ff-only origin main
git merge --ff-only codex/chatgpt-upload-fallback
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_private_paths.py
python3 scripts/audit_agent_stack.py
git diff --check origin/main..HEAD
git push origin main
```

Stop rather than force or rebase if `origin/main` changed incompatibly.

- [ ] **Step 6: Prove final remote state**

```bash
git fetch origin
git rev-parse HEAD
git rev-parse origin/main
git ls-remote origin refs/heads/main
git status --short --branch
```

Expected: all three commit IDs match, the current branch is `main`, and the
working tree is clean.
