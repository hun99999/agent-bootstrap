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

## Verified Clipboard Image Fallback

Use this only for approved PNG attachments after direct file upload is
unavailable. The currently verified path is limited to `image/png`; do not
generalize its evidence to other image MIME types.
Reuse the approved attachment-sharing scope; changing transport does not
authorize more files or a different ChatGPT destination.

1. Confirm every input is an approved PNG and record its manifest index,
   intended order, count, correct image MIME type, and a non-sensitive alias.
   Do not use this route for non-image files or unverified image MIME types.
2. Establish a clean packet baseline at the verified ChatGPT destination: no
   attachment previews, no error or pending state, and no unapproved text. Any
   existing text must be the exact approved prompt for this packet; otherwise
   stop or use a fresh composer.
3. In manifest order, read one image's bytes locally and Base64-encode them for
   the selected browser's documented clipboard-item payload.
   `tab.clipboard.write(...)` receives an array containing one
   outer clipboard item. Its `entries` array contains the
   `base64` and `mimeType` entry:

   ```js
   await tab.clipboard.write([
     {
       entries: [{ base64: encodedBytes, mimeType: "image/png" }],
     },
   ]);
   ```

   Await each `tab.clipboard.write(...)` call before pasting. If the call
   rejects or throws, stop before pasting.
4. Focus the verified ChatGPT composer and use the paste key supported by the
   selected browser.
5. Paste one image at a time. After each paste, require the attachment preview
   count to equal that manifest index and verify that no error or pending state
   remains. The preview count does not prove byte identity; it proves the staged
   count, while order is limited to the recorded write-and-paste sequence.
6. Before sending, verify the exact packet: only the approved prompt text, no
   unapproved text, the intended visible attachment count, no unexpected
   previews, the ordered manifest matching the recorded sequence, and no error
   or pending state. Do not send until every check passes.
7. If a paste fails or creates an ambiguous duplicate, do not send a partial
   packet. Remove only draft attachments created by the failed attempt when
   they are unambiguous; otherwise leave a handoff and report the exact state.
8. If the stage requires delivery, verify that the persisted outgoing message
   contains the same exact packet after sending.
   Composer previews prove staging, not delivery.

Clipboard paste may expose generated names such as `clipboard.png`.
Never place an absolute path in the attachment manifest. Use non-sensitive
aliases by default, and use an original basename only after confirming that the
name itself is approved for the same destination.

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
