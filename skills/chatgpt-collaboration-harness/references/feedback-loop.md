# Feedback Loop

## Loop State

Track the following state during each stage:

- Confirmed final goal.
- Current stage number, outcome, and validation criteria.
- What was shared with ChatGPT Pro.
- Which ChatGPT Pro capability was used: normal chat, Search Mode, deep research, agent mode, apps, or none.
- ChatGPT Pro's key feedback and useful original excerpts.
- Codex's judgment: accepted, rejected, or deferred.
- Local changes made.
- Validation results.
- Next stage or remaining risk.

## Preapproval Mode

At session startup, ask whether the user wants review-first mode or preapproved harness mode.

In preapproved harness mode, the user may approve the whole planned staged loop in advance. This allows Codex to:

- Proceed through planned stages sequentially.
- Send approved project summaries, selected diffs, or redacted logs to ChatGPT Pro.
- Apply clear, low-risk ChatGPT Pro suggestions.
- Send bounded delegated-worker packets and integrate low-risk output locally.
- Use Search Mode or deep research for approved public-web research.
- Run validation commands.
- Continue to the next stage when the current stage passes validation.
- Request final ChatGPT Pro review automatically.

Preapproval does not cover:

- Expanding external sharing beyond the approved scope.
- Sharing repository URLs, Git URLs, private files, secrets, credentials, customer data, or sensitive personal data unless explicitly approved.
- Broad architecture, dependency, data model, security, or UX direction changes.
- Destructive commands.
- Deployment, paid operations, account settings, production changes, credential changes, logged-in web actions, or write actions in external services.
- Actions that conflict with repository rules, AGENTS.md, work-rules, or explicit user instructions.

When in doubt, stop and ask the user.

## Stage Feedback Loop

For each stage:

1. Restate the current stage outcome and validation criteria.
2. Perform the local work required for the stage.
3. Ask ChatGPT Pro for focused feedback, delegated output, research, or agent work unless the stage is simple, mechanical, explicitly exempted, or the user asked to skip Pro involvement.
4. Request one primary output type from ChatGPT Pro: code review, implementation risk, debugging hypothesis, UX critique, test plan, alternative comparison, source-backed research brief, delegated draft, web task report, or final-stage readiness review.
5. Require Korean output and explicit evidence labels unless the user requested another language or the deliverable requires another language.
6. Classify feedback as accepted, rejected, deferred, or needs-local-verification.
7. Apply accepted feedback within the approved risk and sharing scope.
8. Run validation.
9. If validation fails, summarize the failure back to ChatGPT Pro and request narrow correction hypotheses.
10. Complete the stage only after validation passes or the user accepts a documented residual risk.

## Delegated Work Loop

Use delegated-worker mode when ChatGPT Pro can complete a bounded subtask more effectively than a simple review, such as source-backed research, alternative comparison, bug triage, test planning, copy drafting, implementation sketching, or documentation drafting.

For delegated work:

1. Send a packet with the goal, allowed context, constraints, exact deliverable, acceptance criteria, and what not to do.
2. Ask ChatGPT Pro to answer in Korean, state assumptions, cite sources when research is involved, and separate facts, community sentiment, speculation, and recommendations.
3. Treat the result as untrusted input until Codex verifies it locally.
4. Apply only the parts Codex can justify with repository evidence, source evidence, or validation output.
5. Record accepted, rejected, and deferred portions before continuing.

## Codex Review Criteria

Classify ChatGPT Pro feedback using these criteria:

- Accepted: it matches local evidence, is low risk, and directly contributes to the goal.
- Rejected: it conflicts with repository rules, user instructions, security constraints, approved scope, or technical evidence.
- Deferred: it needs more information, user judgment, additional validation, or later-stage context.
- Needs-local-verification: it may be useful, but Codex has not yet reproduced, source-checked, or tested it.

## Validation

Run appropriate validation after edits:

- Tests or build.
- Type checks or lint.
- Reproduction steps.
- Browser or manual flow checks.
- Logs and error message review.

If validation cannot be run, report why and keep the residual risk visible.

## Resync

Before the next ChatGPT Pro turn, if local changes were made, send a delta packet:

- Stage completed or in progress.
- Summary of changed files.
- Core diff or explanation.
- Validation commands and results.
- Remaining unresolved issue.
- Prior ChatGPT output classification and what Codex changed after local verification.

Share full files, large diffs, logs, Git URLs, or repository URLs only after user approval.

## Final Review

After all planned stages are complete, ask ChatGPT Pro to review the final result.

The final review packet should include:

- Confirmed final goal.
- Stage list and completion summary.
- Key changes or relevant diff excerpts.
- Validation commands and results.
- Known tradeoffs and residual risks.
- ChatGPT Pro capabilities used and why each was appropriate.
- Specific request for defects, missed constraints, unsafe assumptions, and final corrections.

Codex must treat final review feedback as advice. Apply only feedback that fits the user goal, repository rules, approved risk scope, and local validation evidence.

## Exit Criteria

End the loop when:

- The goal is achieved and required validation is complete.
- Final ChatGPT Pro review has been handled.
- Product or design judgment from the user is needed.
- External sharing or broad change approval is required.
- The same blocking condition repeats and Codex cannot proceed.

## Final Report Format

The final report should include:

- Goal and result.
- Stage completion summary.
- ChatGPT Pro capability summary and short original excerpts.
- Changes Codex applied.
- Validation results.
- Suggestions Codex rejected or deferred.
- Remaining risks.
