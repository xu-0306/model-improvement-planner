# Output Shapes

Use this file as public-skill guidance for planning outputs.

This is not a formal schema, validator, or contract system. Treat these shapes as the minimum structure that helps another agent understand the plan, inspect the reasoning, and see what is still missing. Keep outputs small. Add fields only when they change the next decision.

## Minimal Planning Bundle

The public skill should usually emit a bounded planning bundle with these sections:

- `target_capability`
- `bottleneck_hypothesis`
- `facts`
- `evaluation_plan`
- `intervention_decision`
- `recommended_next_artifacts`

Example bundle shape:

```json
{
  "target_capability": {},
  "bottleneck_hypothesis": {},
  "facts": {
    "confirmed": [],
    "missing": []
  },
  "evaluation_plan": {},
  "intervention_decision": {},
  "recommended_next_artifacts": []
}
```

## Capability Target

Use this section to pin down what capability is being improved and what "better" means.

Suggested fields:

- `task`
- `desired_behavior`
- `failure_surface`
- `constraints`

Minimal shape:

```json
{
  "task": "Grounded browser-assisted coding help",
  "desired_behavior": "Inspect pages when needed and return repository-grounded guidance.",
  "failure_surface": [
    "hallucinated browser success",
    "answers not grounded in local code"
  ],
  "constraints": [
    "local deployment preferred"
  ]
}
```

## Bottleneck Hypothesis

Use this section to state the current best explanation of why the capability fails. Keep it falsifiable.

Suggested fields:

- `primary_gap`
- `why_this_is_likely`
- `competing_hypotheses`
- `confidence`

Minimal shape:

```json
{
  "primary_gap": "system_composition",
  "why_this_is_likely": "The requested behavior depends on a controller path that is not yet verified.",
  "competing_hypotheses": [
    "base-model tool-use weakness",
    "missing evaluator"
  ],
  "confidence": "medium"
}
```

## Confirmed Vs Missing Facts

Use this section to separate evidence from assumptions. If a fact is missing, say so plainly instead of filling gaps with guesses.

Suggested fields:

- `confirmed`
- `missing`
- `assumptions`

Minimal shape:

```json
{
  "confirmed": [
    "The target workflow requires browser interaction.",
    "Repository context must be available during answer generation."
  ],
  "missing": [
    "Whether a reliable browser controller already exists",
    "Which local model and serving stack are actually available"
  ],
  "assumptions": [
    "Training should not start before controller feasibility is checked"
  ]
}
```

## Evaluation Plan

Define how the route will be judged before recommending expensive optimization work.

Suggested fields:

- `baseline_checks`
- `success_metrics`
- `acceptance_bar`
- `regression_checks`
- `stop_conditions`

Minimal shape:

```json
{
  "baseline_checks": [
    "Run small browser-grounding probes",
    "Check whether responses cite inspected evidence"
  ],
  "success_metrics": [
    "action grounding",
    "repository grounding"
  ],
  "acceptance_bar": "Improvement must appear on held-out tasks, not only on examples.",
  "regression_checks": [
    "general coding quality does not collapse"
  ],
  "stop_conditions": [
    "No verified controller path",
    "No measurable gain on held-out evaluation"
  ]
}
```

## Intervention Decision

Use this section to record the narrowest recommended route, why it was chosen, and what was ruled out for now.

Suggested fields:

- `chosen_family`
- `decision_summary`
- `evidence_basis`
- `rejected_for_now`
- `decision_status`

Minimal shape:

```json
{
  "chosen_family": "system_composition",
  "decision_summary": "Do not recommend finetuning first; verify controller and grounding path before model optimization.",
  "evidence_basis": [
    "The target behavior depends on external action execution.",
    "No confirmed execution path exists yet."
  ],
  "rejected_for_now": [
    "supervised finetuning",
    "reward optimization"
  ],
  "decision_status": "bounded_recommendation"
}
```

## Recommended Next Artifacts

Use this section to say what planning artifacts should exist next. Keep this list small and ordered.

Suggested fields per item:

- `artifact`
- `purpose`
- `required_before_execution`

Minimal shape:

```json
[
  {
    "artifact": "evaluation-brief",
    "purpose": "Define the held-out probes and success criteria.",
    "required_before_execution": true
  },
  {
    "artifact": "system-design-note",
    "purpose": "Describe the controller and grounding boundary.",
    "required_before_execution": true
  }
]
```

## Stop Rules

Output a bounded recommendation instead of pretending the plan is execution-ready when any of these are true:

- the core bottleneck is still only a hypothesis
- key environment or model facts are unconfirmed
- the evaluation path is missing or too vague to reject failure
- the chosen route depends on external tools, runtimes, or data not yet verified
- the safest recommendation is to research, probe, or redesign before training

In those cases, say what is known, what is missing, what should be checked next, and where the current recommendation stops.
