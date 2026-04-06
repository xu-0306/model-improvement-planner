# Probe Generation Plan Contract

Use this contract when the skill needs to explain how baseline probes were derived for a capability request before responses are collected or route selection is locked.

## Goal

Make probe design inspectable, capability-aware, and reusable across language, coding, tool-use, multimodal, speech, and novel requests.

## Machine-Readable Contract

Emit one JSON object with:

- `contract`: `probe_generation_plan`
- `schema_version`
- `target_capability`
- `planning_scope`
- `probe_families`
- `generation_rationale`
- `teacher_roles`
- `evaluation_modes`
- `target_modalities`
- `target_languages`
- `probe_blueprints`
- `acceptance_signals`
- `known_limitations`

## Interpretation Rules

- `planning_scope` should distinguish between an initial baseline plan and an expanded follow-up plan.
- `probe_families` should name the capability clusters being tested, such as `language-localization` or `tool-use`.
- `generation_rationale` should explain why those probe families are sufficient for the current baseline.
- `teacher_roles` should identify which roles are expected during evaluation design, such as `diagnostician` or `verifier`.
- `evaluation_modes` should describe how the planned probes will be judged, such as `teacher-review`, `exact-match`, or `execution-based`.
- `probe_blueprints` is the canonical list of planned probe patterns. Each item should stay compact and export-friendly.
- `acceptance_signals` should describe what evidence would make the baseline good enough for route selection.
- `known_limitations` should record meaningful blind spots instead of hiding them in prose.

## Default Output Path

- `artifacts/model-improvement-planner/<target-slug>/probe-generation-plan.json`

## Worked Example

```json
{
  "contract": "probe_generation_plan",
  "schema_version": "1.0",
  "target_capability": "Traditional Chinese instruction following",
  "planning_scope": "initial_baseline",
  "probe_families": [
    "language-localization",
    "instruction-following"
  ],
  "generation_rationale": [
    "Need to compare the model's relatively strongest language against the requested target language.",
    "Need to distinguish language mismatch from general reasoning weakness."
  ],
  "teacher_roles": [
    "diagnostician",
    "critique_teacher"
  ],
  "evaluation_modes": [
    "teacher-review",
    "rubric-based"
  ],
  "target_modalities": {
    "input": [
      "text"
    ],
    "output": [
      "text"
    ]
  },
  "target_languages": [
    "zh-Hant"
  ],
  "probe_blueprints": [
    {
      "probe_family": "language-localization",
      "pattern": "strong-language prompt with Traditional Chinese answer requirement",
      "expected_evaluation_mode": "teacher-review"
    }
  ],
  "acceptance_signals": [
    "Enough scored probes exist to identify relative strengths and weaknesses."
  ],
  "known_limitations": [
    "Tokenizer-specific script fidelity issues are not directly isolated by this first probe batch."
  ]
}
```
