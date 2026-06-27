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
