# Probe Result Contract

Use this contract for one normalized probe outcome after either offline capture or live backend execution.

## Goal

Preserve per-probe evidence in a stable shape so later diagnosis, teacher review, and dataset export do not depend on ad hoc response logs.

## Machine-Readable Contract

Emit one JSON object per probe with:

- `contract`: `probe_result`
- `schema_version`
- `probe_id`
- `probe_family`
- `input`
- `expected_evaluation_mode`
- `target_capability`
- `target_language`
- `rubric_reference`
- `tags`
- `metadata`
- `response_status`
- `student_response`
- `raw_metrics`
- `teacher_verdict`
- `evaluator_id`
- `notes`
- `response_language_hint`
- optional `model_profile_reference`
- optional `score`
- optional `passed`

## Required Interpretation Rule

- `response_status` is the canonical answered-vs-missing field.
- Keep raw execution or teacher signals in `raw_metrics` and `teacher_verdict`; do not collapse them into a single score when richer evidence exists.
