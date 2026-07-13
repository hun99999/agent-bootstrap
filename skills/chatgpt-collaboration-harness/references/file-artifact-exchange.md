# File Artifact Exchange

Use this reference when a ChatGPT Pro collaboration stage needs screenshots, files, or generated artifacts. Codex remains responsible for approval scope, local validation, and final judgment.

## Screenshot Attachments

Use screenshots when visible UI state, remote screens, layout, design fidelity, chart output, document rendering, browser errors, or app behavior matters.

Before upload:

- Check for secrets, API keys, tokens, cookies, private URLs, internal hostnames, account details, customer data, personal data, private file paths, notifications, browser profile details, and unrelated windows.
- Crop or retake the screenshot when unrelated sensitive content is visible.
- State what the screenshot is supposed to prove and what ChatGPT Pro should inspect.
- Ask ChatGPT Pro to call out uncertainty when the evidence is not visible in the screenshot.

Do not treat a screenshot critique as proof. Verify the relevant behavior locally after applying advice.

## File Attachments

Share the smallest approved file set that lets ChatGPT Pro do the stage. Prefer focused excerpts, diffs, failing logs, test output, screenshots, or generated reports over full repositories.

Do not upload credentials, private keys, API tokens, database passwords, cookies, auth state, browser profiles, raw production data, customer data, private endpoints, or machine-specific trust settings.

Large bundles, full source files, private repository material, Git URLs, repository URLs, browser state, and scope expansion require Hun's approval before sharing.

## Attachment Transport Capability Matrix

| Format | MIME type | Direct chooser | Clipboard | Evidence |
| --- | --- | --- | --- | --- |
| PNG | image/png | `unsupported-in-current-smoke` | `verified-staging` | Direct: fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles; no preview. Clipboard: one fresh exact-MIME write and paste fulfilled; the one preview initially named `clipboard.png` stabilized to `clipboard(1).png`, with no error or pending state. Six previews staged previously. |
| JPEG/JPG | image/jpeg | `unsupported-in-current-smoke` | `verified-staging` | Direct: fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles; no preview. Clipboard: fresh exact-MIME write and paste fulfilled; exactly one visible `clipboard.jpeg` preview, with no error or pending state. |
| WebP | image/webp | `unsupported-in-current-smoke` | `verified-staging` | Direct: fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles; no preview. Clipboard: fresh exact-MIME write and paste fulfilled; exactly one visible `clipboard.webp` preview, with no error or pending state. |
| GIF | image/gif | `unsupported-in-current-smoke` | `verified-staging` | Direct: fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles; no preview. Clipboard: fresh exact-MIME write and paste fulfilled; exactly one visible `clipboard.gif` preview, with no error or pending state. |
| PDF | application/pdf | `unsupported-in-current-smoke` | `verified-staging` | Direct: fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles; no preview. Clipboard: fresh exact-MIME write and paste fulfilled; exactly one visible `clipboard.pdf` preview, with no error or pending state. |
| DOCX | application/vnd.openxmlformats-officedocument.wordprocessingml.document | `unsupported-in-current-smoke` | `verified-staging` | Direct: fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles; no preview. Clipboard: fresh exact-MIME write and paste fulfilled; exactly one visible `clipboard.vnd.openxmlformats-officedocument.wordprocessingml.document` preview, with no error or pending state. |
| XLSX | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | `unsupported-in-current-smoke` | `verified-staging` | Direct: fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles; no preview. Clipboard: fresh exact-MIME write and paste fulfilled; exactly one visible `clipboard.vnd.openxmlformats-officedocument.spreadsheetml.sheet` preview, with no error or pending state. |
| PPTX | application/vnd.openxmlformats-officedocument.presentationml.presentation | `unsupported-in-current-smoke` | `verified-staging` | Direct: fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles; no preview. Clipboard: fresh exact-MIME write and paste fulfilled; exactly one visible `clipboard.vnd.openxmlformats-officedocument.presentationml.presentation` preview, with no error or pending state. |
| TXT | text/plain | `unsupported-in-current-smoke` | `verified-staging` | Direct: fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles; no preview. Clipboard: fresh exact-MIME write and paste fulfilled; exactly one visible `clipboard.plain` attachment preview and no prompt text, error, or pending state. |
| CSV | text/csv | `unsupported-in-current-smoke` | `verified-staging` | Direct: fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles; no preview. Clipboard: fresh exact-MIME write and paste fulfilled; exactly one visible `clipboard.csv` preview, with no error or pending state. |
| ZIP | application/zip | `user-verified` | `verified-staging` | Direct: Hun-confirmed attachment capability; the fresh chooser event failed with `Timed out after 3000ms waiting for file chooser.` before chooser/isMultiple/setFiles and produced no preview. Clipboard: fresh exact-MIME write and paste fulfilled; exactly one visible `clipboard.zip` preview, with no error or pending state. |

- `verified-staging`: that transport passed its complete composer-staging rule
  for the exact format/MIME pair in this smoke.
- `unsupported-in-current-smoke`: the attempted transport did not pass that
  rule in the current smoke. It is not a categorical product-support claim.
- `not-tested`: an external blocker prevented the transport attempt from
  starting, so there is no current transport result.
- `user-verified`: Hun reported successful product use, but the report does not
  prove that the current browser API path passes its staging rule.

Product support, browser API acceptance, clipboard write fulfillment, visible
composer staging, and a user report are distinct evidence levels. The
clipboard results above prove composer staging only. Generated preview names
may derive from MIME because clipboard bytes carry no original filename; those
names do not prove original filename preservation.

Visible composer previews from this smoke were removed and no Send occurred.
ChatGPT Library persistence or deletion was not inspected, so this does not
establish account-side cleanup.

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

### Verified Clipboard Attachment Fallback

Use this only after direct staging is unavailable and the capability matrix
marks the exact format/MIME pair as `verified-staging`. API success alone is
not attachment evidence. Do not promote a format unless both the
`tab.clipboard.write(...)` call and a visible attachment preview passed the
smoke contract.

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

## Attachment Packet

When sending screenshots or files, include a compact manifest:

```text
Objective:
Stage:
Attachments:
- <filename or screenshot label>: <why it is included>
Omitted on purpose:
- <sensitive or irrelevant material withheld>
Allowed inferences:
- <what ChatGPT Pro may infer from the attachment>
Not allowed:
- <claims that require local verification or additional source>
Requested output:
- Classify advice as accepted, rejected, deferred, or needs-local-verification.
```

## Receiving Generated Artifacts

Downloaded artifacts are untrusted until Codex validates them locally.

Before using a returned file:

- Record artifact name, type, source conversation, intended use, and any assumptions ChatGPT Pro stated.
- Save it to a review or temporary location before moving it into a project.
- For archives, inspect an archive listing before extraction and reject unexpected absolute paths, path traversal, hidden executables, oversized contents, or unrelated files.
- For documents, PDFs, images, slides, or spreadsheets, render or open them locally and inspect the visible result.
- For code, patches, configs, prompts, or data files, diff them against the target project and run the relevant validator, tests, or parser.
- For scripts, binaries, macros, installers, browser extensions, auth files, or anything executable, stop and ask before running or installing.

## Artifact Return Contract

Ask ChatGPT Pro to return generated artifacts with:

- artifact name and file type;
- intended use;
- source inputs used;
- assumptions and omitted context;
- safety notes;
- validation steps Codex should run;
- any dependency, runtime, or format requirement.

## Classification

Classify every ChatGPT Pro artifact or attachment-derived answer as:

- `accepted`: safe enough to integrate after local validation.
- `rejected`: incorrect, unsafe, off-scope, or not useful.
- `deferred`: potentially useful later but outside the current stage.
- `needs-local-verification`: plausible but not yet proven by local evidence.

Do not advance a stage only because ChatGPT Pro generated a plausible file. The local evidence contract still decides completion.

## Final Reporting

When the stage or harness ends, report:

- screenshots or files shared;
- artifacts received;
- artifacts accepted, rejected, deferred, or needs-local-verification;
- local validation run for accepted artifacts;
- anything withheld or requiring Hun's approval.
