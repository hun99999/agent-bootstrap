# Chrome ChatGPT Pro

## Connection Principles

- If the user requested `@chrome`, or this skill requires Chrome integration, use Chrome plugin capabilities.
- Run ChatGPT collaboration in the user's Chrome session.
- Do not silently substitute the in-app browser or another browser path.
- If the Chrome connection, extension state, login state, or Pro conversation mode state is unclear, report the exact blocker.
- Do not conclude that Chrome is unavailable merely because no direct tool named `Chrome`, `chrome`, or `browser` appears in the active tool list. In Codex, Chrome automation is often exposed through the Chrome skill plus a browser-client runtime reached from the JavaScript/Node REPL tool.
- Before reporting "Chrome tools are not exposed", try the Chrome skill workflow: use the available JavaScript/Node REPL tool to initialize the Chrome browser-client, acquire the extension-backed browser, and list or open tabs. If the JavaScript/Node REPL tool itself is hidden, use tool discovery for the Node REPL JavaScript execution tool before declaring a blocker.
- Report a Chrome blocker only after the Chrome skill troubleshooting path fails: no JavaScript/Node REPL execution tool can be found, the Chrome extension cannot be reached after retry, the native host or extension is missing/disabled, Chrome is not running and the user does not approve launching it, or ChatGPT requires user-gated login/CAPTCHA/payment action.

## Session Selection

- If an existing ChatGPT tab is open, verify it by title, URL, and recency before reusing it.
- Prefer a Codex-owned ChatGPT work tab for staged harness loops.
- Do not borrow arbitrary user ChatGPT tabs unless the user explicitly asks for that.
- If a new tab is needed, open the ChatGPT web session and check whether Pro extended mode or Pro conversation mode is available.
- Do not assume a specific Chrome profile name, account name, local username, or fixed path.

## File Upload Diagnosis

Before uploading, read the selected browser's `file-uploads` documentation.
Start the `filechooser` wait before activating the visible attachment control,
use absolute paths with `chooser.setFiles(...)`, and call
`chooser.isMultiple()` before passing more than one path.

Do not diagnose a permission failure from a hidden input click or an unopened
picker. Diagnose the boundary only from the actual `chooser.setFiles(...)`
result and the visible composer state.

If Chrome rejects file setting with `Not allowed` or another chooser-level
denial, read `chrome-file-upload-troubleshooting` and reproduce its exact user
instruction: open `chrome://extensions`, select Details for the ChatGPT Chrome
Extension, and enable **Allow access to file URLs**. Do not claim Codex changed
the permission.
A chooser denial does not prove that file-URL access is the sole cause.
Present the setting as the official next check, not a confirmed root cause.

After the user changes the setting, start the Chrome task again and verify the
upload with a fresh file-chooser attempt. Record file-URL access as the confirmed
cause only if that attempt succeeds. If the setting was already enabled or the
fresh attempt still fails, keep the cause unconfirmed and report the observed
boundary.

Do not work around a blocked `chrome://` page through another browser surface,
raw browser commands, profile-file edits, or indirect extension-state changes.
For approved images, use the Verified Clipboard Image Fallback in
`file-artifact-exchange.md`; for non-image files, require a supported upload
route or manual attachment.

## Capability Selection

- If a pinned or "고정됨" ChatGPT area visibly offers Search Mode, use it for search stages after confirming the selected mode in the composer or tool state.
- If pinned Search Mode is not visible, check the current ChatGPT tool menu, composer controls, or available mode picker before declaring it unavailable.
- Use normal chat for critique, synthesis, code review, and short reasoning tasks that do not need current web evidence.
- Use Search Mode for quick current web answers, source discovery, official docs checks, or narrow fact verification.
- Use deep research for multi-source investigation, market scans, long comparisons, literature-style synthesis, or questions that need a documented cited report.
- Use agent mode for bounded online tasks where ChatGPT needs to navigate websites or take actions on behalf of the user. Do not use agent mode for local filesystem work.
- If a requested capability is unavailable, report the exact visible state and fall back only with user approval or a clear local alternative.

## Completion Channel

- Use normal Chrome UI checks when no trusted local response bridge is installed.
- If CS WebLatch or another trusted local response bridge is installed and approved by the user, prefer it as the ChatGPT Web completion channel.
- Keep this harness responsible for goal tracking, stage control, approval gates, feedback classification, local edits, validation, and final reporting.
- Treat bridge completion events as completion signals, not as permission to bypass approval or safety rules.

## Prompt Sending

Include the following in each ChatGPT Pro prompt:

- Confirmed final goal.
- Current stage number and desired stage outcome.
- Current local state summary.
- Context approved for sharing.
- Constraints and non-goals.
- Validation already run or planned.
- Desired output format.
- Capability Codex wants ChatGPT Pro to use: normal chat, Search Mode, deep research, agent mode, or apps.
- Output type Codex wants: critique, risks, alternatives, validation plan, implementation concerns, code-review findings, delegated draft, source-backed report, web task report, or final review.
- Evidence requirement: do not rely on reasoning alone when facts, source behavior, official docs, rankings, preferences, or public sentiment matter.
- Language: answer in Korean unless the user requested another language or the deliverable must be in another language.

If sensitive data may be present, stop before sending and ask the user.

## Research And Agent Prompts

- For Search Mode, ask for source links, publication or update dates when visible, evidence quality labels, and a short claim-to-source mapping.
- For deep research, ask for a documented report with source table, confidence notes, gaps, community-sentiment notes when relevant, and follow-up checks Codex should perform locally.
- For agent mode, define the exact website task, allowed accounts or logged-out requirement, actions requiring confirmation, stop conditions, and what evidence to return.
- For preference, ranking, taste, popularity, or adoption questions, allow reputable public community sources and ask ChatGPT Pro to present them as opinion signals rather than official truth.
- Do not paste secrets, private credentials, customer data, private file contents, or full repository bundles into ChatGPT Pro unless the user explicitly approves that exact sharing scope.

## Response Waiting

- In Pro conversation mode, recheck whether the response is complete every 2 minutes after sending the question unless a trusted bridge provides a completion event.
- Do not repeat unnecessary intermediate status reports before the response is complete.
- If a UI error, disconnection, expired login, failed send, or bridge error is clear, report it immediately without waiting 2 minutes.

## Completion Checks

When using Chrome UI checks, treat the response as complete only when multiple signals agree:

- The generating indicator or stop button is gone or inactive.
- The composer is not busy.
- The latest response text is stable across rechecks.
- Completion signals such as a copy button, response boundary, or final message are visible.

Do not treat a visible send button alone as completion.

## Session Cleanup

- When work is done, clean up Chrome tabs or keep only tabs the user needs to continue viewing.
- Keep a Codex-owned ChatGPT work tab as a handoff only when the staged harness may continue later.
- If the page is waiting for user input, login, CAPTCHA, approval, or payment, leave the tab as a handoff.
