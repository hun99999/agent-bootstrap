# ChatGPT Pro Multi-Format Attachment Transport Design

## Goal

Extend `chatgpt-collaboration-harness` from its PNG-only clipboard fallback to
an evidence-based attachment workflow for common images, PDFs, documents,
spreadsheets, presentations, text files, and ZIP archives. Prefer Chrome's
file chooser, use clipboard paste only for formats proven to stage correctly in
the ChatGPT composer, and keep manual attachment as the explicit final fallback.

The repository catalog source and the installed Codex runtime copy must expose
the same behavior. Validation must use synthetic, non-sensitive files and must
not send a ChatGPT message.

## Confirmed Evidence

- The ChatGPT Pro composer exposes a multiple-file chooser.
- Before the permission change, the chooser opened but
  `chooser.setFiles(...)` rejected an absolute local PNG path with
  `Not allowed` at the Chrome extension boundary.
- Chrome's packaged troubleshooting and current OpenAI documentation direct the
  user to enable **Allow access to file URLs** for the ChatGPT Chrome
  Extension and then start the Chrome task again.
- Hun has now enabled that setting. This is a user-reported environment change,
  not yet evidence that a fresh chooser attempt succeeds or that the setting
  was the sole cause of the previous denial.
- The installed browser API accepts an absolute file path or path array through
  `chooser.setFiles(...)`. Its clipboard API accepts entries containing a MIME
  type plus Base64 or text data, but that API shape does not prove that the
  ChatGPT composer accepts every MIME type as an attachment.
- PNG bytes written as `image/png` to the selected ChatGPT tab's clipboard and
  pasted into the composer previously produced six ordered previews without
  sending a message. This proves PNG staging, not delivery or generic-file
  clipboard support.
- Hun has successfully attached a ZIP archive in ChatGPT. Treat ZIP attachment
  as user-verified capability and separately record the result of this
  environment's fresh direct-attachment staging test.
- Current OpenAI guidance lists common text, spreadsheet, presentation, and
  document formats including PDF, DOCX, XLSX, PPTX, CSV, and TXT, and names JPEG
  and PNG among supported upload examples. Product support still does not prove
  that the Chrome extension transport or clipboard path works in this runtime.

Official product references for these claims:

- `https://help.openai.com/en/articles/8983675`
- `https://learn.chatgpt.com/docs/chrome-extension#upload-files`

## Chosen Approach

Use a direct-first hybrid transport:

1. Validate the approved attachment manifest and sharing scope.
2. Establish a clean ChatGPT composer at the approved destination.
3. Try the documented Chrome file-chooser flow first.
4. Treat fulfilled `setFiles(...)` plus an unambiguous visible attachment
   preview with no error or pending state as direct-staging evidence.
5. If direct staging fails, use clipboard paste only when that exact format's
   MIME path has already passed the same visible staging checks.
6. If neither verified route is available, stop and hand the exact file list to
   Hun for manual attachment. Do not convert, unpack, or partially send files.

This keeps original names and bytes on the primary path while preserving a
verified fallback where the browser and ChatGPT composer demonstrably support
one.

## Initial Format Matrix

The first implementation covers only this bounded set:

| Format | Direct chooser | Clipboard probe | Initial evidence |
| --- | --- | --- | --- |
| PNG | Fresh test required | Supported | Six previews staged previously |
| JPEG/JPG | Fresh test required | Test candidate | OpenAI-supported upload example |
| WebP | Fresh test required | Test candidate | No current transport evidence |
| GIF | Fresh test required | Test candidate | No current transport evidence |
| PDF | Fresh test required | Test candidate | OpenAI-supported file format |
| DOCX | Fresh test required | Test candidate | OpenAI-supported file format |
| XLSX | Fresh test required | Test candidate | OpenAI-supported file format |
| PPTX | Fresh test required | Test candidate | OpenAI-supported file format |
| TXT | Fresh test required | Test candidate | OpenAI-supported file format |
| CSV | Fresh test required | Test candidate | OpenAI-supported file format |
| ZIP | Fresh test required | Test candidate | Hun-confirmed attachment capability |

`Test candidate` means the implementation may run a synthetic clipboard smoke
for that MIME type. It does not mean the production workflow may use that path.
A clipboard format becomes supported only after both the clipboard write and
the visible ChatGPT staging contract pass. Any other extension, legacy office
format, archive type, or MIME alias is outside the initial scope.

## Attachment And Evidence Contract

Before either transport:

- Confirm the destination, file count, order, intended use, and approval scope.
- Reject secrets, credentials, auth state, customer data, browser profiles,
  private endpoints, or other sensitive material.
- Use non-sensitive aliases in manifests. Never expose absolute local paths to
  ChatGPT or store machine-specific paths in the public skill.
- Require a clean composer with no unexpected text, previews, errors, or
  pending state.

For direct staging:

1. Read the selected browser's current `file-uploads` documentation.
2. Start the `filechooser` wait before activating the attachment control.
3. Check `chooser.isMultiple()` before passing multiple paths.
4. Await `chooser.setFiles(...)`; its successful result has no payload.
5. Verify the expected visible preview count, names when shown, and absence of
   error or pending state.

For clipboard staging:

1. Require the exact format/MIME pair to be marked verified in the capability
   matrix before using it for real work.
2. Write one file at a time through the documented clipboard-item payload and
   await the write before pasting.
3. Focus the verified composer and paste with `ControlOrMeta+V`.
4. Require the visible preview count to increase by exactly one, with no error,
   pending state, or ambiguous duplicate.
5. Record that clipboard-generated filenames may differ from original names.

Preview evidence proves staging only. It does not prove byte identity,
persistence, model readability, or delivery. Those claims require their own
explicit evidence in a stage that is authorized to send; this implementation's
browser smoke is not authorized to send.

## Failure Handling

- If fresh direct staging still rejects with `Not allowed`, preserve the exact
  error and visible state. Do not claim that file-URL permission is disabled or
  that it is the sole root cause.
- If `setFiles(...)` fulfills but the preview is missing, erroneous, pending,
  or ambiguous, classify direct staging as unverified for that attempt.
- If a clipboard write rejects, stop before paste and leave the format
  unsupported on the clipboard route.
- If paste produces text, no preview, an error, a pending state, or an
  ambiguous duplicate, do not promote the format to supported.
- Never send a partial packet. Remove only draft attachments created by the
  current smoke when they are unambiguous; otherwise abandon that composer and
  use a fresh one.
- Do not bypass blocked `chrome://` pages, edit Chrome profile files, toggle
  extension state indirectly, convert files, or unpack archives as fallback
  behavior.

## Synthetic Browser Smoke

Create one small, valid, non-sensitive temporary fixture for each format. Do
not commit binary fixtures to the repository.

- Every fixture contains a harmless marker that identifies its format and
  test purpose.
- Office files and PDFs must be structurally valid and locally parseable or
  renderable before use.
- Images must decode locally and report the intended MIME type.
- The ZIP contains one harmless text file, no absolute or parent-traversal
  paths, no executable entry, and no nested archive.
- Inspect file type and size before browser use.

Use a fresh ChatGPT task or a proven-clean composer. Test direct staging one
file at a time, then test clipboard candidates one at a time. Never click Send.
Record for each attempt: format, MIME type, transport, API result, visible
preview result, visible error or pending state, cleanup result, and final
classification.

## Skill Structure

- `SKILL.md` remains the concise router. It routes any approved-file upload
  failure or clipboard fallback to both attachment references.
- `references/chrome-chatgpt-pro.md` owns direct file-chooser diagnosis,
  permission remediation, fresh-task retry behavior, and browser safety
  boundaries.
- `references/file-artifact-exchange.md` owns the direct-first decision flow,
  bounded capability matrix, clipboard staging contract, packet integrity, and
  manual handoff.
- `tests/test_skill_catalog.py` enforces the routing, supported-format scope,
  evidence states, transport order, negative rules, and staging-versus-delivery
  distinction.

Do not add a new script, dependency, global Codex configuration option,
separate fallback skill, or committed binary fixture. The user-controlled
Chrome permission is environment state, not repository configuration.

## Source And Runtime Boundaries

- Repository catalog source: `skills/chatgpt-collaboration-harness/`
- Installed Codex runtime copy: `~/.codex/skills/chatgpt-collaboration-harness/`

Implement and test the repository source first. After it passes, perform an
itemized checksum-aware dry run against the runtime copy. Review every proposed
path, repeat the identical dry run immediately before synchronization, and
synchronize only the reviewed regular-file updates without blanket deletion.
Stop for Hun's exact-path approval before removing any runtime-only file or
accepting any unexpected creation, file-type change, symlink change, metadata-
only change, or unplanned path. Validate source and runtime independently and
require a recursive diff with no output.

## Test And Review Contract

Before changing skill behavior:

- add contract tests for the approved design;
- run the focused tests and preserve the expected RED output;
- run the synthetic browser smoke as evidence gathering, not as a substitute
  for contract tests.

Before declaring the skill ready:

- run the targeted skill-catalog tests;
- run the complete repository test suite;
- run both skill validators in a disposable PyYAML environment;
- run the private-path and secret scan, agent-stack audit, and
  `git diff --check`;
- validate the installed runtime copy separately;
- require a no-op checksum-aware runtime dry run and recursive source/runtime
  comparison;
- pressure-test the updated skill from the raw failure and multi-format request;
- obtain an independent final review and classify every finding.

If ChatGPT Pro is used for final review, share only public-safe changed excerpts
and validation summaries. Do not share synthetic binaries, repository or Git
URLs, browser state, authentication state, private paths, or unrelated project
material.

## Git And Release Boundary

Keep all design and implementation commits on the existing
`codex/chatgpt-upload-fallback` feature branch. Preserve hooks and inspect Git
status before every stage operation. Updating or pushing protected `main`
requires a separate action-time approval from Hun after final evidence and
review are complete.

## Non-Goals

- Supporting every extension accepted by any ChatGPT surface.
- Treating an arbitrary MIME string accepted by the clipboard API as proof of
  ChatGPT attachment support.
- Sending the synthetic test packet or Hun's real files during browser QA.
- Automatically changing Chrome permissions, browser profiles, auth state, or
  website allowlists.
- Automatically converting documents, transcoding images, unpacking archives,
  or rewriting filenames.
- Claiming delivery, persistence, byte identity, or model readability from an
  unsent composer preview.
