# Evaluator Contract

Use this reference when designing teacher-side scoring and correction logic.

## Ownership

The evaluator side should own:

- scoring
- correctness decisions
- preference or verifier judgments when relevant
- feedback or critique text when relevant
- correction text when relevant
- mistake classification when relevant

## Structured Evaluation Payload

Return a structured payload with:

- `subject`
- `evaluation`
- `signals`
- `artifacts`

Prefer a machine-readable envelope with:

- `contract`: `evaluator_payload`
- `schema_version`
- `subject`
- `evaluation`
- `signals`
- `artifacts`

Useful optional fields:

- `teacher_feedback`
- `teacher_correction`
- `mistake_classification`
- `advance`
- `confidence`

Evaluator outputs should stay export-friendly: keep source lineage that belongs in dataset records on the dataset side under `metadata.source_provenance`. Use `signals` and `artifacts` for evaluator-local evidence, traces, and rewritten outputs.

Default output path when no project-specific convention exists:

- `artifacts/model-improvement-planner/<target-slug>/evaluator-payloads.jsonl`

## Evaluation Guidance

- prefer explicit criteria over vague judgments
- keep outputs directly useful for dataset export
- separate final score from explanatory rationale
- declare uncertainty instead of inventing rubric logic

## Minimum `evaluation` Fields

- `mode`
- `summary`

Useful optional fields:

- `score`
- `is_correct`
- `chosen_candidate`
- `rejected_candidate`
- `binary_label`
- `scalar_reward`
- `verifier_status`
- `process_label`
- `mastery_delta`
- `rationale`

## `signals` Examples

- verifier evidence
- failed checks
- reward components
- length features
- agreement signals
- uncertainty flags

## `artifacts` Examples

- corrected answer
- critique text
- rewritten answer
- step labels or step rewards
- rationale trace
- distilled soft targets

## Worked Examples

### `direct_answer` / SFT evaluator payload

```json
{
  "contract": "evaluator_payload",
  "schema_version": "1.0",
  "subject": {
    "prompt_id": "boiling-point-001",
    "response": "Water boils at 100 degrees Celsius at sea level."
  },
  "evaluation": {
    "mode": "direct_answer",
    "summary": "Reference answer is correct and concise.",
    "is_correct": true
  },
  "signals": [
    "factually_correct",
    "includes_units",
    "concise"
  ],
  "artifacts": {
    "teacher_correction": "100 degrees Celsius."
  },
  "confidence": 0.99
}
```

### `preference_pair` evaluator payload

```json
{
  "contract": "evaluator_payload",
  "schema_version": "1.0",
  "subject": {
    "prompt_id": "rewrite-politeness-014",
    "candidates": [
      {
        "candidate_id": "A",
        "text": "Please send the file when you have a moment."
      },
      {
        "candidate_id": "B",
        "text": "Send the file now."
      }
    ]
  },
  "evaluation": {
    "mode": "preference_pair",
    "summary": "Candidate A is more polite while preserving the instruction.",
    "chosen_candidate": "A",
    "rejected_candidate": "B"
  },
  "signals": [
    "politeness",
    "instruction_preservation"
  ],
  "artifacts": {
    "teacher_feedback": "Prefer softened phrasing without dropping the request."
  },
  "confidence": 0.93
}
```

### `verifier_outcome` evaluator payload

```json
{
  "contract": "evaluator_payload",
  "schema_version": "1.0",
  "subject": {
    "task_id": "json-only-119",
    "response": "{\"name\":\"Ana\",\"age\":12,\"extra\":true}"
  },
  "evaluation": {
    "mode": "verifier_outcome",
    "summary": "Output parses as JSON but violates the allowed-keys constraint.",
    "verifier_status": "fail",
    "is_correct": false
  },
  "signals": [
    {
      "failed_checks": [
        "schema.allowed_keys"
      ]
    }
  ],
  "artifacts": {
    "verifier_evidence": [
      {
        "check_id": "json.parse",
        "passed": true
      },
      {
        "check_id": "schema.allowed_keys",
        "passed": false,
        "message": "Unexpected key: extra"
      }
    ]
  },
  "confidence": 1.0
}
```

### `process_step` evaluator payload

```json
{
  "contract": "evaluator_payload",
  "schema_version": "1.0",
  "subject": {
    "trace_id": "arith-trace-2007",
    "step_id": "arith-trace-2007-step-2",
    "step_text": "17 * 6 = 102"
  },
  "evaluation": {
    "mode": "process_step",
    "summary": "This step applies multiplication correctly.",
    "process_label": "correct"
  },
  "signals": [
    {
      "reward_components": {
        "operation_correct": 1.0,
        "format_ok": 1.0
      }
    }
  ],
  "artifacts": {
    "step_reward": 1.0,
    "aggregation_rule": "sum step rewards, then normalize by trace length"
  },
  "confidence": 0.97
}
```
