# System Composition Plan Contract

Use this reference when the right answer is not pure model tuning and the capability requires multiple components.

## Goal

Capture how external subsystems, controllers, specialist models, or runtimes should be composed to achieve the target capability.

## Machine-Readable Contract

Prefer a JSON artifact with these top-level fields:

- `contract`: `system_composition_plan`
- `schema_version`
- `target_capability`
- `system_goal`
- `architecture_summary`
- `components`
- `interfaces`
- `orchestration_summary`
- `latency_implications`
- `failure_handling`
- `observability_requirements`
- `evaluation_plan`
- `unresolved_gaps`

Default output path when no project-specific convention exists:

- `artifacts/model-improvement-planner/<target-slug>/system-composition-plan.json`

## Guidance

- use this artifact when the capability depends on more than one model or subsystem
- keep component roles explicit
- capture failure handling and observability, not only the happy path
- make `evaluation_plan` a linkable object that includes `reference_artifact` or `artifact`
- use the evaluation plan to judge the composed system rather than only one component

## Worked Example

```json
{
  "contract": "system_composition_plan",
  "schema_version": "1.0",
  "target_capability": "Speech dialogue with a local assistant",
  "system_goal": "Compose ASR, dialogue, and TTS into one interactive local system.",
  "architecture_summary": "Streaming ASR feeds a text LLM, which produces responses for a local TTS component.",
  "components": [
    {
      "component_id": "asr",
      "role": "speech-to-text"
    },
    {
      "component_id": "llm",
      "role": "dialogue generation"
    },
    {
      "component_id": "tts",
      "role": "text-to-speech"
    }
  ],
  "interfaces": [
    "audio stream -> transcript",
    "transcript -> dialogue prompt",
    "response text -> speech waveform"
  ],
  "orchestration_summary": "ASR and TTS run as external subsystems around the local LLM.",
  "latency_implications": [
    "Turn latency depends on ASR finalization and TTS synthesis time."
  ],
  "failure_handling": [
    "Fall back to text-only mode when TTS is unavailable."
  ],
  "observability_requirements": [
    "log ASR confidence and response latency per turn"
  ],
  "evaluation_plan": {
    "reference_artifact": "evaluation-plan.json"
  },
  "unresolved_gaps": [
    "streaming ASR component not yet selected"
  ]
}
```
