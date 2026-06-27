# Goal Harness

## Goal Setup

- Compress the user's final objective into one actionable outcome.
- If the goal is unclear, do not start implementation or external sharing; explain Codex's understanding and confirm with the user.
- If goal tooling is available, inspect the current goal state first.
- If no goal is active and the user provided a confirmed goal, set that goal.
- If a goal is already active, check whether the new request conflicts with it; if it does, ask the user to choose the priority.

## Stage Decomposition

If the goal is broad, long-running, multi-file, ambiguous, or likely to need multiple review passes, decompose it into 1 to 10 concrete stages before implementation.

Each stage should define:

- Outcome: what must be true when the stage is complete.
- Scope: files, modules, or behavior likely to be touched.
- Context: what can be shared with ChatGPT Pro.
- ChatGPT role: reviewer, delegated worker, Search Mode researcher, deep research reporter, agent task executor, or skipped with reason.
- Validation: the command, test, browser check, or manual evidence required.
- Stop condition: what would require user judgment before continuing.

Prefer fewer stages for small tasks and more stages for broad work. Do not create more than 10 stages unless the user explicitly approves a larger plan.

## Stage Ordering

- Work stages sequentially by default.
- Parallelize only when stages are independent and cannot edit the same files, mutate the same state, or rely on the same external resource.
- Keep the final objective stable while narrowing the current stage and next validation item.
- If new information changes the stage plan, explain the change and update the plan before continuing.

## Goal Operating Rules

- Write goals as outcomes. Example: "Reproduce the login error, fix it, and make the tests pass."
- Do not put browser session details, temporary prompts, or internal reasoning into the goal.
- Keep current evidence, completed stages, blocked stages, and next validation visible in working notes or status updates.
- When a stage is complete, record what changed, what was validated, which ChatGPT Pro capability was used, and what Codex accepted, rejected, or deferred.

## Completion Handling

- Mark a stage complete only when its outcome and validation criteria are satisfied.
- Mark the whole goal complete only when all required stages and final review handling are done.
- Do not mark the goal complete because the budget is low or the task is taking a long time.
- Report the goal as blocked only when the same blocking condition repeats and Codex cannot proceed without user input or an external state change.

## When User Judgment Is Needed

Stop the loop and ask the user when:

- Product direction or UX direction would change.
- A large dependency, data model, architecture, or security policy change is needed.
- ChatGPT Pro and Codex disagree and local evidence is not enough to decide.
- External sharing scope would expand beyond the approved scope.
- The sensitivity of material to be shared externally is unclear.
