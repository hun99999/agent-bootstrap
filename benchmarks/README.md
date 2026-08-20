# Skill and prompt benchmark

This directory measures whether an instruction earns its token and latency cost. It uses the pinned
[`alibaba/skill-up`](https://github.com/alibaba/skill-up) release in
`skill-up.lock.json`; live model runs are local experiments, not CI gates.

## Install and smoke-test the harness

```bash
python3 scripts/bootstrap_skill_up.py
SKILL_UP=.tools/skill-up/0.8.0/skill-up
CUSTOM_AGENT_BIN="$PWD/benchmarks/skill-up-smoke/agent.sh" \
  "$SKILL_UP" validate benchmarks/skill-up-smoke/evals/eval.yaml
CUSTOM_AGENT_BIN="$PWD/benchmarks/skill-up-smoke/agent.sh" \
  "$SKILL_UP" run benchmarks/skill-up-smoke/evals/eval.yaml \
  --output-dir .benchmarks/skill-up-smoke
```

The smoke run uses a deterministic local agent and consumes no model tokens. It proves only the
pinned binary, configuration, custom-engine transport, judge, and report path.

## Build an evaluable case set

Put `evals/eval.yaml`, `evals/cases/*.yaml`, disposable fixtures, and deterministic judges under the
skill being evaluated. A case enters the accepted set when a human confirms all of these:

- the prompt and fixture are self-contained for an agent with no conversation history;
- the case represents a real failure/requirement or cites its external source and license;
- the judge checks task behavior and changed-file/side-effect boundaries mechanically;
- the same fixture, prompt, model, reasoning effort, sandbox, CLI version, and timeout apply to both
  `with_skill` and `without_skill`;
- secrets, live accounts, production authority, root work-in-progress, and network side effects are
  absent.

Start with four to six approved pressure cases. Set `benchmark.enabled: true`, use rule or script
judges, set `parallelism: 1`, and run three paired iterations. Preserve raw execution order and reports
under `.benchmarks/`; use a separate controlled reversal only when order bias is being measured.

Primary metrics are task pass rate and safety-contract pass rate. Secondary metrics are input,
cached-input, and output tokens plus wall time, reported per run and as mean/standard deviation. A
performance skill stays enabled only when it preserves quality and shows a repeatable net benefit over
the baseline. A workflow skill is judged by whether it enables the required procedure at an acceptable
cost.

Do not accept generated cases merely because they validate, and do not use an LLM judge for the first
gate. A human-approved case corpus is the benchmark source of truth. Re-baseline after model, Codex,
skill-up, prompt, fixture, or runtime-policy changes.

`skill-up` can pin the Codex model with `--model`, but its built-in Codex adapter currently inherits
reasoning effort from the active Codex runtime. Record and hold that setting constant for paired runs.
Run `scripts/summarize_codex_usage.py` against Codex JSONL files for an independent usage snapshot.

## Current candidate matrix

`skill-candidates.json` records the comparison shape without pretending that unapproved cases or live runs already exist.

- `karpathy-guidelines`: vanilla versus Karpathy.
- `hun-engineering-loop`: vanilla versus Karpathy alone versus Karpathy plus the compact Hun wrapper.
- `focused-debugging`: vanilla versus upstream Superpowers `v6.2.0` versus the lean adaptation.
- `isolated-worktree`, `execute-plan`, and `review-feedback-triage`: explicit workflow capability versus vanilla.

Keep the current model, reasoning effort, runtime policy, prompt, fixture, and trial count identical within a comparison. Re-baseline when any of those inputs changes. The explicit workflow candidates remain available without implicit prompt cost; the two active core guidance skills stay under measurement.
