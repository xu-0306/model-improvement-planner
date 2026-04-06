# Research Evidence Contract

Use this reference when external sources were needed to clarify feasibility, stack support, or method selection.

## Goal

Capture the minimum inspectable research output needed to justify route selection or deferral.

## Machine-Readable Contract

Prefer a JSON artifact with these top-level fields:

- `contract`: `research_evidence`
- `schema_version`
- `target_capability`
- `research_scope`
- `sources`
- `confirmed_facts`
- `unresolved_facts`
- `route_implications`
- `unsupported_assumptions`
- `recommended_followups`

Default output path when no project-specific convention exists:

- `artifacts/model-improvement-planner/<target-slug>/research-evidence.json`

## Guidance

- keep source metadata concise but traceable
- separate confirmed facts from route implications
- record unsupported assumptions explicitly instead of burying them in prose
- use followups only for material gaps that could still change the route

## Worked Example

```json
{
  "contract": "research_evidence",
  "schema_version": "1.0",
  "target_capability": "Local speech dialogue loop",
  "research_scope": "ASR, TTS, and local text-model orchestration options",
  "sources": [
    {
      "source_type": "official_docs",
      "label": "chosen ASR runtime docs"
    },
    {
      "source_type": "model_card",
      "label": "target local LLM card"
    }
  ],
  "confirmed_facts": [
    "The current base model is text-only.",
    "The serving stack does not natively provide ASR or TTS."
  ],
  "unresolved_facts": [
    "Streaming ASR latency on the target hardware is not yet measured."
  ],
  "route_implications": [
    "Pure text finetuning will not add speech IO by itself.",
    "System composition is the leading route unless a multimodal-native replacement model is chosen."
  ],
  "unsupported_assumptions": [
    "Assuming end-to-end speech support can be achieved without external components."
  ],
  "recommended_followups": [
    "benchmark one local ASR candidate",
    "compare TTS latency against the interaction budget"
  ]
}
```
