# Teacher Loop Plan Contract

Use this contract when the skill selects one or more teacher roles and must show how those roles will produce critiques, corrections, preferences, verifier outputs, or distilled targets for downstream artifacts.

## Goal

Describe a teacher loop clearly enough that its outputs can be exported into probe results, dataset records, evaluator payloads, or training plans without inventing the workflow again later.

## Machine-Readable Contract

Emit one JSON object with:

- `contract`: `teacher_loop_plan`
- `schema_version`
- `target_capability`
- `loop_goal`
- `selected_teacher_roles`
- `loop_order`
- `input_artifacts`
- `output_artifacts`
- `export_strategy`
- `quality_gates`
- `stop_conditions`
- `open_questions`

## Interpretation Rules

- `loop_goal` should state what the teacher loop is trying to improve or verify.
- `selected_teacher_roles` should identify the active teacher bundle, not every theoretically possible role.
- `loop_order` is the canonical ordered list of teacher steps. Each step should identify the role, purpose, and expected emitted fields.
- `input_artifacts` should point to the artifacts or raw materials the loop consumes.
- `output_artifacts` should point to the artifacts or export formats the loop is expected to produce.
- `export_strategy` should say how teacher outputs are converted into machine-readable records such as `dataset_record` or `evaluator_payload`.
- `quality_gates` should prevent weak or contradictory teacher outputs from silently entering training data.
- `stop_conditions` should make it clear when the loop should halt rather than continue generating low-confidence supervision.

## Default Output Path

- `artifacts/model-improvement-planner/<target-slug>/teacher-loop-plan.json`

## Worked Example

```json
{
  "contract": "teacher_loop_plan",
  "schema_version": "1.0",
  "target_capability": "Traditional Chinese instruction following",
  "loop_goal": "diagnose language mismatch, correct student outputs, and export critique-rewrite data",
  "selected_teacher_roles": [
    "diagnostician",
    "critique_teacher",
    "verifier"
  ],
  "loop_order": [
    {
      "step_id": "diagnose",
      "teacher_role": "diagnostician",
      "purpose": "identify whether the main issue is target-language mismatch or broader task failure",
      "emits": [
        "failure_modes",
        "suggested_next_probes"
      ]
    },
    {
      "step_id": "rewrite",
      "teacher_role": "critique_teacher",
      "purpose": "repair student outputs and capture actionable defects",
      "emits": [
        "observed_defects",
        "rewrite_guidance",
        "corrected_output"
      ]
    },
    {
      "step_id": "verify",
      "teacher_role": "verifier",
      "purpose": "confirm target-language fidelity and instruction compliance",
      "emits": [
        "verdict",
        "failed_checks"
      ]
    }
  ],
  "input_artifacts": [
    "probe-results.jsonl"
  ],
  "output_artifacts": [
    "dataset-records.jsonl",
    "evaluator-payloads.jsonl"
  ],
  "export_strategy": {
    "dataset_record": "export critique-rewrite pairs when verifier confidence is sufficient",
    "evaluator_payload": "export failed checks as reusable evaluation cases"
  },
  "quality_gates": [
    "reject low-confidence corrections",
    "keep critique and correction separated"
  ],
  "stop_conditions": [
    "stop if the teacher cannot state a concrete defect",
    "stop if verifier evidence is insufficient"
  ],
  "open_questions": [
    "Whether the weakest cases should be handled by distillation instead of critique-rewrite."
  ]
}
```
