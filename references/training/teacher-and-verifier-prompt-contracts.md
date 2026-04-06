# Teacher and Verifier Prompt Contracts

Use this reference when deciding what teacher or verifier signal to produce and when designing reusable prompts for generation, critique, preference judgment, verification, or distillation.

## Goal

Choose teacher roles by the supervision they emit, then keep the resulting prompts bounded, inspectable, and export-friendly so their outputs can be turned into evaluation artifacts, dataset records, or intervention decisions without heavy post-processing.

## Core Roles

### Diagnostician

Use when the main need is to identify failure modes, missing skills, uncertainty, or data gaps.

Emit:

- `failure_modes`
- `missing_skills`
- `confidence`
- `suggested_next_probes`

### Demonstrator

Use when the student needs direct examples of a desirable response, action, or trajectory.

Emit:

- `prompt_or_task`
- `target_output`
- `style_or_policy_notes`
- `difficulty`

### Critique Teacher

Use when the student already produced an output and needs actionable feedback before or alongside correction.

Emit:

- `observed_defects`
- `why_each_defect_matters`
- `rewrite_guidance`
- `corrected_output`

### Preference Judge

Use when comparing alternatives is easier or more reliable than absolute scoring.

Emit:

- `candidates`
- `chosen_candidate`
- `rejected_candidate`
- `comparison_basis`
- `confidence`

### Verifier

Use when the target has checkable constraints, factual conditions, formal rules, or executable tests.

Emit:

- `verdict`
- `checks_run`
- `failed_checks`
- `evidence`
- `confidence`
- `abstained`

### Process-Reward Teacher

Use when intermediate steps matter and the student should learn better search, decomposition, or tool use.

Emit:

- per-step labels or rewards
- step-level critique
- approved and disallowed process patterns
- terminal summary over the full trajectory

### Distillation Teacher

Use when transferring behavior from a stronger policy, ensemble, or search process into a simpler target.

Emit:

- `distilled_target`
- `salient_rationale`
- `dropped_information`
- `teacher_confidence`

### Runtime Researcher

Use when the teacher must gather live facts, inspect tools, or resolve environment-dependent uncertainty before teaching.

Emit:

- discovered facts
- source or evidence notes
- unresolved unknowns
- updated recommendation or supervision plan

## Selection Guide

- Start with `diagnostician` when the failure is unclear.
- Use `demonstrator` when the student lacks a workable pattern.
- Use `critique teacher` when there is already a student attempt worth improving.
- Use `preference judge` when pairwise comparison is more stable than free-form scoring.
- Use `verifier` when correctness can be externally checked.
- Use `process-reward teacher` when outcome-only supervision hides important mistakes.
- Use `distillation teacher` when the source behavior is good but too expensive or complex to deploy directly.
- Use `runtime researcher` when static assumptions are likely wrong or incomplete.

## Combination Patterns

- `diagnostician` + `demonstrator`: find the gap, then show a target pattern.
- `critique teacher` + `verifier`: explain the defect, then confirm whether the rewrite passes.
- `preference judge` + `demonstrator`: select the better candidate and keep it as a training target.
- `process-reward teacher` + `verifier`: reward good intermediate behavior and still enforce final correctness.
- `runtime researcher` + any other role: refresh the factual basis before emitting supervision.
- `distillation teacher` + `preference judge`: compress a stronger policy while preserving ranking information.

## Role Boundaries

- One teacher may play multiple roles, but each emitted artifact should make its role clear.
- Do not present unverifiable opinion as `verifier` output.
- Do not use `demonstrator` alone when silent failure modes are likely; pair it with diagnosis or verification.
- Do not use `preference judge` output as if it were calibrated scalar reward unless that mapping is defined separately.

## General Prompt Contract Rules

- define the role explicitly
- define the task boundary explicitly
- name the required output fields
- forbid extra narrative outside the requested structure
- separate evidence from recommendation
- separate critique from correction
- separate verification from stylistic preference
- keep outputs short enough to audit and export

Prefer outputs that map cleanly into existing artifacts such as:

- `dataset_record`
- `evaluator_payload`
- `evaluation_plan`
- `training_plan`
- `intervention_decision`

## Shared Prompt Skeleton

When writing teacher or verifier prompts, include these blocks in order:

1. role
2. target capability or task
3. available evidence
4. required output fields
5. output constraints
6. abstain or uncertainty rule

Example shape:

```text
Role: <teacher or verifier role>
Target: <capability or task>
Available evidence:
- ...
Return:
- field_1
- field_2
- field_3
Constraints:
- no extra prose
- keep each field bounded
- mark uncertainty explicitly
If evidence is insufficient, abstain and state why.
```

## Diagnostician Prompt Contract

Use when the main job is to identify the real failure mode before proposing optimization.

Return:

- `failure_modes`
- `missing_skills`
- `confidence`
- `suggested_next_probes`

Keep the output diagnostic only. Do not jump to a training method unless that is explicitly requested.

Good fit for:

- capability decomposition
- weak-model triage
- unknown or mixed failure modes

## Demonstrator Prompt Contract

Use when the student needs direct demonstrations of a desired response, action, or trace.

Return:

- `prompt_or_task`
- `target_output`
- `style_or_policy_notes`
- `difficulty`

Keep the target concise and imitation-friendly. Do not bury the answer inside long explanation unless rationale is part of the supervision shape.

Good fit for:

- direct SFT
- instruction tuning
- tool-call demonstration data
- narrow behavior bootstrapping

## Critique Teacher Prompt Contract

Use when the student already produced an output and the goal is error-aware improvement.

Return:

- `observed_defects`
- `why_each_defect_matters`
- `rewrite_guidance`
- `corrected_output`

Keep critique and correction separate. Do not rely on the corrected output alone if the workflow needs mistake-aware supervision.

Good fit for:

- critique-rewrite data
- self-correction loops
- tool-use recovery examples
- coding repair data

## Preference Judge Prompt Contract

Use when relative ranking is easier than writing a gold answer.

Return:

- `candidates`
- `chosen_candidate`
- `rejected_candidate`
- `comparison_basis`
- `confidence`

Do not turn preference outputs into scalar rewards unless a separate mapping is defined.

Good fit for:

- DPO-style data
- reranking data
- model comparison
- style or quality ranking

## Verifier Prompt Contract

Use when correctness can be checked from rules, tests, execution, or stable rubric logic.

Return:

- `verdict`
- `checks_run`
- `failed_checks`
- `evidence`
- `confidence`
- `abstained`

Verifier prompts should prefer explicit checks over free-form judgment. If the verifier cannot decide safely, it should abstain rather than guess.

Good fit for:

- execution-based code evaluation
- structured output validation
- schema checks
- browser action grounding checks
- final-answer correctness checks

## Distillation Teacher Prompt Contract

Use when compressing behavior from a stronger teacher into a smaller or cheaper student.

Return:

- `distilled_target`
- `salient_rationale`
- `dropped_information`
- `teacher_confidence`

Keep the distilled target simpler than the full teacher trace when student capacity is limited.

Good fit for:

- response distillation
- rationale distillation
- trajectory compression
- teacher-bootstrapped SFT

## Export-Friendly Output Rules

- keep top-level fields stable across runs
- prefer arrays of short strings or objects with explicit keys
- avoid long free-form essays
- do not mix recommendation, evidence, and critique into one blob
- make abstention explicit

## Gating Checks Before Reuse

Before reusing a prompt contract for production data generation or evaluation, check:

- does the output map cleanly into the intended artifact?
- does the prompt separate evidence from judgment?
- does it have an uncertainty or abstain rule?
- is the output short enough to audit?
- would different raters likely interpret it the same way?

## Anti-Patterns

- asking the teacher to diagnose, correct, rank, and verify in one unstructured paragraph
- asking the verifier to infer hidden facts not present in the task
- using long rationale dumps when the student only needs direct targets
- using preference prompts when gold answers already exist and are easy to write
- using critique prompts without a corrected output when the downstream route needs rewrite supervision

## Decision Rule

Choose the narrowest teacher or verifier role that matches the required supervision signal.

If a single role cannot produce export-friendly outputs safely, split the workflow into separate prompts rather than letting one prompt emit an overloaded blob.
