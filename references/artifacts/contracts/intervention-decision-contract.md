# Intervention Decision Contract

Use this reference when the skill must record the selected route and the reasoning that justified it.

## Goal

Capture the bounded intervention decision after intake, decomposition, evaluation design, and evidence gathering.

## Machine-Readable Contract

Prefer a JSON artifact with these top-level fields:

- `contract`: `intervention_decision`
- `schema_version`
- `target_capability`
- `problem_types`
- `chosen_intervention_family`
- `implementation_direction`
- `decision_status`
- `decision_summary`
- `evidence_basis`
- `rejected_alternatives`
- `key_risks`
- `next_actions`
- `stop_or_continue_reason`

Default output path when no project-specific convention exists:

- `artifacts/model-improvement-planner/<target-slug>/intervention-decision.json`

## Guidance

- keep the chosen intervention family separate from implementation details
- record rejected alternatives explicitly so the route is inspectable
- distinguish the decision summary from the evidence basis
- make the stop or continue reason concrete enough to explain the current execution boundary

## Worked Example

```json
{
  "contract": "intervention_decision",
  "schema_version": "1.0",
  "target_capability": "Grounded browser-assisted coding help",
  "problem_types": [
    "tool-use or controller gap",
    "evaluator deficiency"
  ],
  "chosen_intervention_family": "system_composition",
  "implementation_direction": "browser controller plus repository-aware local model",
  "decision_status": "continue",
  "decision_summary": "Do not start training yet; first compose browser execution and repository grounding around the local model.",
  "evidence_basis": [
    "The requested capability depends on reliable browser actions.",
    "The current base model has no verified action-execution path."
  ],
  "rejected_alternatives": [
    "plain supervised finetuning before a browser controller exists",
    "reward-driven optimization without a trusted action verifier"
  ],
  "key_risks": [
    "hallucinated action success",
    "repository context drift during long sessions"
  ],
  "next_actions": [
    "define the controller interface",
    "add evaluation probes for action grounding"
  ],
  "stop_or_continue_reason": "Continue with system design and evaluation setup before any training route is selected."
}
```
