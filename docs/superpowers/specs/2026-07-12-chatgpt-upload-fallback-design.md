# ChatGPT Pro File And Clipboard Transfer Design

## Goal

Make `chatgpt-collaboration-harness` recover predictably when Chrome blocks local
file reads: diagnose the real file-chooser failure, give the official narrow
permission remedy, and use a verified clipboard-image fallback when direct
attachment remains unavailable. Keep the repository catalog source and the
installed Codex runtime copy identical, then validate and integrate the change
into `main`.

## Confirmed Evidence

- The ChatGPT Pro composer exposes a multiple-file chooser.
- The chooser opens successfully, but setting an absolute local PNG path fails
  at the Chrome extension boundary with `Not allowed`.
- The selected Chrome plugin's upload troubleshooting identifies the required
  remedy as enabling **Allow access to file URLs** for the ChatGPT Chrome
  Extension from `chrome://extensions`.
- Browser automation is prohibited from opening or modifying the privileged
  `chrome://extensions` page. The skill must not attempt another browser
  surface, profile-file edit, raw browser command, or other workaround.
- Writing PNG bytes to the selected ChatGPT tab's clipboard and pasting into
  the composer created attachment previews. A bounded smoke test observed the
  preview count increase from one through six without sending a message.

The smoke test proves that six images can be staged in the composer through the
clipboard route. It does not by itself prove that arbitrary non-image files can
use the same route or that an unsent draft persisted as a delivered message.

## Chosen Behavior

Use an adaptive hybrid path.

1. Prefer the documented file-chooser workflow for screenshots and files.
2. Diagnose the failure at `chooser.setFiles(...)`; do not infer a permission
   problem merely because the upload control or hidden file input is awkward to
   click.
3. If Chrome rejects file setting, read the selected browser's
   `chrome-file-upload-troubleshooting` guidance and reproduce its exact manual
   permission instruction. Do not claim that Codex changed the permission.
4. For approved image attachments, continue with the verified clipboard-image
   fallback when direct file attachment remains unavailable.
5. For PDFs, archives, documents, or other non-image files, do not pretend that
   clipboard image paste is equivalent. Require the manual Chrome permission
   change, a supported upload route, or Hun's manual attachment.

## File-Chooser Contract

The Chrome collaboration reference will require the operator to:

1. Read the selected browser's `file-uploads` documentation.
2. Start the `filechooser` wait before clicking the visible attachment control.
3. Use absolute paths with `chooser.setFiles(...)`.
4. Check `chooser.isMultiple()` before passing more than one path.
5. Inspect the actual `setFiles(...)` result and visible composer state.
6. On Chrome rejection, read `chrome-file-upload-troubleshooting` and report
   the exact **Allow access to file URLs** remedy.

The reference will explicitly prohibit bypassing a blocked `chrome://` page or
editing Chrome profiles and extension state indirectly.

## Verified Clipboard Image Fallback

The artifact-exchange reference will define an image-only fallback:

1. Reuse the already approved attachment-sharing scope. Do not widen the files
   or destination because the transport changed.
2. Confirm that every input is an approved image and record the intended image
   count and order.
3. Read image bytes locally and Base64-encode them for the selected browser's
   documented clipboard-item payload. Then call `tab.clipboard.write(...)` with
   an entry whose `base64` value is the encoded bytes and whose `mimeType` is
   the correct image MIME type.
4. Focus the verified ChatGPT composer and use the selected browser's supported
   paste key sequence.
5. Paste one image at a time. After each paste, verify that a new attachment
   preview appears and that no error or pending state remains.
6. Do not send until the visible attachment count equals the intended count.
7. If a paste fails or creates an ambiguous duplicate, do not send a partial
   packet. Remove only draft attachments created by the failed attempt when
   that can be done unambiguously; otherwise leave a handoff and report the
   exact draft state.
8. When delivery is part of the stage, verify the persisted outgoing message
   after sending. Composer previews alone prove staging, not delivery.

Clipboard paste may replace original filenames with a generated name such as
`clipboard.png`. The attachment manifest must retain the original ordered
labels so ChatGPT Pro can relate each pasted image to its intended purpose.

## Skill Structure

- `SKILL.md` remains a concise router. It will point Chrome upload failures and
  image clipboard fallback work to the two existing reference files.
- `references/chrome-chatgpt-pro.md` owns browser connection and file-chooser
  diagnosis, including the official permission instruction and blocked-page
  safety boundary.
- `references/file-artifact-exchange.md` owns attachment scope, clipboard-image
  staging, count verification, partial-draft handling, and delivered-message
  evidence.
- `tests/test_skill_catalog.py` enforces both contracts without reading the
  machine-specific runtime directory.

No new script, dependency, global Codex configuration, Chrome profile setting,
or separate fallback skill is required.

## Source And Runtime Boundaries

- Repository catalog source:
  `skills/chatgpt-collaboration-harness/`
- Installed Codex runtime copy:
  `~/.codex/skills/chatgpt-collaboration-harness/`

Implement and test the repository source first. After it passes, mechanically
synchronize the complete skill directory to the runtime destination, validate
both directories independently, and require a recursive diff with no output.
Synchronization must begin with an itemized, checksum-aware dry run. If that
dry run proposes deleting any runtime-only file, stop and obtain Hun's explicit
approval for the exact deletion before running a deletion-capable sync.
Approval to update the skill is not blanket approval to delete unknown
runtime-only files.

## Test And Review Contract

Before editing skill instructions:

- retain the observed browser reproduction and six-preview smoke evidence;
- add repository contract tests and run them to observe the expected RED
  failures.

Before declaring the skill ready:

- run the targeted skill-catalog tests;
- run the complete repository test suite;
- run both skill validators in a disposable PyYAML virtual environment;
- run the private-path scan, agent-stack audit, and `git diff --check`;
- compare repository and runtime skill directories recursively;
- forward-test the updated skill with a fresh agent given only the raw failure
  scenario;
- ask ChatGPT Pro for a final review using only public-safe changed excerpts and
  validation results, then classify every suggestion before applying it.

The ChatGPT Pro packet must omit user images, repository and Git URLs, browser
state, authentication state, private absolute paths, and unrelated project
material.

## Git Integration

Keep the change on a branch created directly from the current `origin/main` so
the unrelated context-compaction branch is not included. Use ordinary commits,
preserve hooks, fast-forward `main` after final validation, push `origin/main`,
and verify local `HEAD`, `origin/main`, and the remote `main` ref all match.

## Non-Goals

- Automating or bypassing Chrome's privileged extension settings page.
- Persistently broadening Chrome extension permissions.
- Treating clipboard paste as a generic transport for non-image files.
- Uploading Hun's real screenshots as part of repository validation.
- Sending a partial image packet merely because some previews appeared.
