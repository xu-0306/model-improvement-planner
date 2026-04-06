# Training Plan Contract

Use this reference when the chosen route includes supervised learning, distillation, preference optimization, reward-driven optimization, or adaptation.

## Goal

Capture a bounded, inspectable training decision rather than a vague statement that the model should be tuned.

## Machine-Readable Contract

Prefer a JSON artifact with these top-level fields:

- `contract`: `training_plan`
- `schema_version`
- `target_capability`
- `intervention_family`
- `implementation_candidates`
- `rejected_alternatives`
- `supervision_shape`
- `teacher_plan`
- `data_plan`
- `evaluation_plan`
- `base_model_suitability_verdict`
- `training_stack_suitability_verdict`
- `serving_compatibility_notes`
- `compute_assumptions`
- `stop_criteria`
- `rollback_criteria`
- `expected_failure_modes`

Default output path when no project-specific convention exists:

- `artifacts/model-improvement-planner/<target-slug>/training-plan.json`

## Guidance

- choose the intervention family before naming PEFT or stack details
- keep rejected alternatives explicit
- distinguish base-model suitability from stack suitability
- make `evaluation_plan` a linkable object that includes `reference_artifact` or `artifact`
- make rollback criteria concrete enough to act on

## Worked Example

```json
{
  "contract": "training_plan",
  "schema_version": "1.0",
  "target_capability": "Repository-grounded coding assistance",
  "intervention_family": "supervised_learning",
  "implementation_candidates": [
    "instruction_tuning",
    "tool-trace_finetuning"
  ],
  "rejected_alternatives": [
    "preference_optimization before direct imitation quality is established"
  ],
  "supervision_shape": "instruction-response pair plus tool trace",
  "teacher_plan": {
    "roles": [
      "diagnostician",
      "demonstrator",
      "critique teacher"
    ]
  },
  "data_plan": {
    "sources": [
      "repository-grounded prompts",
      "teacher-generated critique-rewrite pairs"
    ]
  },
  "evaluation_plan": {
    "reference_artifact": "evaluation-plan.json"
  },
  "base_model_suitability_verdict": "plausible with tooling support",
  "training_stack_suitability_verdict": "needs confirmed tool-trace support in the chosen stack",
  "serving_compatibility_notes": [
    "Serving path must preserve tool schema formatting."
  ],
  "compute_assumptions": [
    "single GPU PEFT run"
  ],
  "stop_criteria": [
    "Held-out execution accuracy plateaus across two checkpoints"
  ],
  "rollback_criteria": [
    "Regression on plain coding prompts exceeds the agreed threshold"
  ],
  "expected_failure_modes": [
    "hallucinated tool success",
    "overfitting to one repository layout"
  ]
}
```
