# Evaluation Plan Contract

Use this reference when defining how progress will be measured before generating data or recommending optimization.

## Goal

Capture the baseline, the intended evaluation path, and the conditions under which a route should be accepted or rejected.

## Machine-Readable Contract

Prefer a JSON artifact with these top-level fields:

- `contract`: `evaluation_plan`
- `schema_version`
- `target_capability`
- `baseline_probes`
- `heldout_evaluation`
- `primary_evaluation_mode`
- `success_metrics`
- `acceptance_criteria`
- `regression_checks`
- `unresolved_risks`
- `stop_conditions`

Default output path when no project-specific convention exists:

- `artifacts/model-improvement-planner/<target-slug>/evaluation-plan.json`

## Guidance

- define evaluation before selecting an expensive optimization route
- keep baseline probes small enough to run early
- record what would invalidate the plan
- separate target metrics from unresolved risks

## Worked Example

```json
{
  "contract": "evaluation_plan",
  "schema_version": "1.0",
  "target_capability": "Traditional Chinese instruction following",
  "baseline_probes": [
    {
      "probe_id": "zh-tw-instruction-001",
      "goal": "test Traditional Chinese response quality"
    }
  ],
  "heldout_evaluation": [
    "held-out localization prompt set",
    "manual review of dialect consistency"
  ],
  "primary_evaluation_mode": "rubric-based",
  "success_metrics": [
    "instruction adherence",
    "Traditional Chinese fluency",
    "terminology consistency"
  ],
  "acceptance_criteria": [
    "Instruction adherence improves on the held-out set.",
    "Traditional Chinese outputs no longer drift into Simplified Chinese."
  ],
  "regression_checks": [
    "English instruction following does not collapse",
    "Response latency stays within the deployment budget"
  ],
  "unresolved_risks": [
    "Current rubric may underweight style drift"
  ],
  "stop_conditions": [
    "No measurable gain after the first supervised stage"
  ]
}
```
