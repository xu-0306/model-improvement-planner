# Capability Intake Contract

Use this reference when normalizing an arbitrary capability request into a stable machine-readable intake artifact.

## Goal

Capture the minimum structured facts needed to route the request before selecting methods.

## Ownership

The intake artifact should own:

- requested capability
- desired outcomes
- failure modes
- success criteria
- modality expectations
- deployment context
- user intent
- constraints
- sub-capability decomposition
- external dependencies
- missing facts

## Machine-Readable Contract

Prefer a JSON artifact with these top-level fields:

- `contract`: `capability_intake`
- `schema_version`
- `requested_capability`
- `desired_outcomes`
- `failure_modes`
- `success_criteria`
- `deployment_context`
- `user_intent`
- `input_modalities`
- `output_modalities`
- `constraints`
- `sub_capabilities`
- `external_dependencies`
- `missing_facts`

Default output path when no project-specific convention exists:

- `artifacts/model-improvement-planner/<target-slug>/capability-intake.json`

Keep empty arrays or explicit empty strings instead of inventing facts. Put project-local additions in extra fields without renaming the core contract fields.

## Guidance

- keep the artifact focused on the request, not the final recommendation
- record missing evidence explicitly
- separate user intent from inferred bottleneck hypotheses
- preserve modality expectations even when the route is later judged infeasible

## Worked Example

```json
{
  "contract": "capability_intake",
  "schema_version": "1.0",
  "requested_capability": "Enable structured browser-assisted coding help on a local model.",
  "desired_outcomes": [
    "The system can inspect web pages when needed.",
    "The model can produce patch-ready coding guidance."
  ],
  "failure_modes": [
    "Hallucinates browser actions",
    "Produces coding suggestions without checking repository context"
  ],
  "success_criteria": [
    "Browser-dependent answers cite inspected evidence.",
    "Coding guidance remains grounded in local files."
  ],
  "deployment_context": {
    "environment": "local workstation",
    "latency_budget": "interactive"
  },
  "user_intent": "planning",
  "input_modalities": [
    "text",
    "web-environment"
  ],
  "output_modalities": [
    "text",
    "tool-call"
  ],
  "constraints": {
    "hardware": [
      "single GPU"
    ],
    "policy": [
      "prefer local execution when possible"
    ]
  },
  "sub_capabilities": [
    "browser action selection",
    "evidence-grounded response generation",
    "repository-aware coding assistance"
  ],
  "external_dependencies": [
    "browser automation environment"
  ],
  "missing_facts": [
    "target browser stack not yet confirmed"
  ]
}
```
