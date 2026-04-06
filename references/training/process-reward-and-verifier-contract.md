# Process Reward and Verifier Contract

Use this reference when deciding whether outcome reward is sufficient or whether verifier-driven optimization needs process supervision.

## Start With Outcome Reward

Outcome reward is usually enough when:

- the task has a clear, checkable final answer
- correctness can be decided from the final output alone
- multiple valid solution paths are acceptable
- the verifier can score cheaply and consistently

Examples of verifiable tasks:

- exact-answer QA
- code that must pass tests
- structured extraction with deterministic validation
- math, logic, or transformation tasks with known targets

Prefer outcome reward first. Add process supervision only when final-answer scoring leaves important blind spots.

## Add Process Supervision When

Use process reward or step supervision when:

- the final answer hides whether the reasoning was sound
- the task is multi-step and early mistakes compound
- the student can guess the answer without learning the method
- reward is sparse and gives weak learning signal
- safety, compliance, or tool-use order matters
- the verifier needs intermediate artifacts to distinguish good work from lucky work

Process supervision is most useful when intermediate steps are themselves inspectable.

## PRM-Style Step Labels

If using step labels, keep them simple and local to the trace:

- `good`: step materially helps solve the task
- `neutral`: step is unnecessary but not harmful
- `bad`: step introduces an error, unsupported claim, or invalid action
- `uncertain`: label cannot be assigned confidently

Use labels on meaningful steps, not every token. Good units include:

- decomposition steps
- tool calls
- intermediate calculations
- constraint checks
- final verification steps

Do not reward verbosity. More steps should not imply more reward.

## Implicit Process Rewards

Not all process rewards need explicit step labels. Acceptable implicit sources include:

- agreement between independent solutions
- passing intermediate checks
- consistency between plan, actions, and final answer
- tool-call validity and grounded citations
- self-verification that matches external verification

Treat implicit rewards as weak evidence unless they correlate with final correctness on held-out tasks.

## Verifier Contract

A verifier should expose:

- `task_id` or equivalent traceable task key
- `final_score` on a stable scale
- `is_correct` or a clear pass/fail decision when available
- `confidence`
- `rationale` kept separate from the score
- `failure_tags` for common error modes
- `evidence` used for the judgment

Useful optional fields:

- `step_scores` or `step_labels`
- `agreement_score` across independent checks
- `length_features` so bias can be audited
- `abstained` when the verifier cannot judge safely

The verifier should also state:

- what inputs it needs
- which outputs are actually checked
- whether it judges only the final answer or both process and outcome
- when it must abstain

## Process Reward Source Contract

A process reward source should expose:

- `trace_unit` definition such as step, tool call, or segment
- `reward_value` or `label` for each unit
- `reason` for non-obvious penalties or rewards
- `coverage` showing which parts of the trace were scored
- `aggregation_rule` from unit scores to example score
- `missing_data_policy` for incomplete traces

Useful optional fields:

- `reward_confidence`
- `reward_version`
- `normalization_rule`
- `source_type` such as explicit label, heuristic, or verifier-derived

Keep the scoring interface stable enough that teacher and student runs are comparable across iterations.

## Failure Modes To Watch

Common failure modes:

- reward hacking: student learns patterns that trigger reward without solving the task
- judge bias: verifier prefers a style, dialect, format, or chain-of-thought surface form
- length bias: longer answers receive higher scores regardless of quality
- agreement traps: multiple judges or samples agree on the same wrong answer
- student-capacity mismatch: the target process is too complex for the student to imitate usefully
- over-supervision: process labels force one strategy when many are valid
- leakage: verifier uses hidden answer cues unavailable at inference time

## Practical Checks

Run these checks before trusting the signal:

- compare outcome-only and process-aware rankings on a held-out set
- test whether reward still works after length normalization
- check agreement across at least two differently-formed verifiers
- inspect high-score failures for obvious reward hacking
- inspect low-score correct answers for judge bias
- confirm the student can realistically produce the supervised process format

If process supervision does not improve held-out outcome quality, remove or simplify it.

## Decision Rule

Use outcome reward alone by default.

Add verifier-driven process reward only when:

- the task is verifiable
- intermediate quality matters
- the verifier can expose auditable evidence
- the process reward source has a stable scoring contract
- failure checks show the signal is improving learning rather than only changing style
