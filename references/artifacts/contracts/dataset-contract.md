# Dataset Contract

Use this reference when exporting teacher-student optimization data.

## Goal

Produce records that preserve enough metadata for downstream training and evaluation.

## Suggested Dataset Modes

- `direct_answer`
- `correction_only`
- `critique_then_rewrite`
- `preference_pair`
- `binary_label`
- `scalar_reward`
- `verifier_outcome`
- `process_step`
- `rationale_distillation`
- `trajectory_distillation`
- `distribution_target`

These are suggested defaults, not a universal closed list.

## Record Shape

Prefer a record that separates:

- input or prompt
- target or candidates
- supervision payload
- evidence
- metadata

## Machine-Readable Contract

Prefer one JSON object per record with a stable envelope:

- `contract`: `dataset_record`
- `schema_version`
- `input`
- `target`
- `candidates`
- `supervision`
- `evidence`
- `metadata`

Use `metadata.source_provenance` as the canonical provenance field. Do not introduce a top-level `provenance` sibling when exporting dataset records. Keep verification artifacts or raw traces in `evidence`; keep lineage, source ids, and collection origin in `metadata.source_provenance`.

Default output path when no project-specific convention exists:

- `artifacts/model-improvement-planner/<target-slug>/dataset-records.jsonl`

Conversation-style records remain useful for `direct_answer`, `correction_only`, and `critique_then_rewrite`, but not every supervision shape should be forced into a conversation transcript.

## Mode-Specific Payload Expectations

- `preference_pair`: include chosen and rejected candidates, plus the comparison basis if known.
- `binary_label`: include the item, label meaning, and label source.
- `scalar_reward`: include score scale, score source, and whether scores are calibrated across tasks.
- `verifier_outcome`: include pass or fail, checks run, and evidence when available.
- `process_step`: include trace unit definition, local label or reward, and aggregation rule if one exists.
- `rationale_distillation` and `trajectory_distillation`: include the final target plus the rationale or trajectory separately.
- `distribution_target`: include the target distribution format and any tokenization or action-space assumptions.

## Required Metadata

Each exported record should carry enough metadata for downstream training and audit:

- dataset mode
- capability family
- supervision shape
- teacher role or role bundle
- evaluator or verifier id when relevant
- rubric or scoring reference when relevant
- difficulty if known
- source provenance
- confidence if available

## Canonical Provenance Rule

Use one naming path for provenance across exports:

- canonical path: `metadata.source_provenance`
- use it for source ids, collection lineage, source type, capture context, and upstream artifact references
- do not duplicate the same information in `evidence`
- do not add top-level `provenance` for new records

## Worked Examples

### `direct_answer` / SFT

```json
{
  "contract": "dataset_record",
  "schema_version": "1.0",
  "input": [
    {
      "role": "system",
      "content": "Answer briefly and include units."
    },
    {
      "role": "user",
      "content": "What is the boiling point of water at sea level?"
    }
  ],
  "target": {
    "answer": "100 degrees Celsius."
  },
  "supervision": {
    "type": "sft",
    "loss_mask": "target_only"
  },
  "metadata": {
    "dataset_mode": "direct_answer",
    "capability_family": "science-qa",
    "supervision_shape": "single_target",
    "teacher_role": "reference-answer-generator",
    "difficulty": "easy",
    "source_provenance": {
      "source_type": "curated_prompt",
      "collection_id": "science-basics-v2",
      "example_id": "boiling-point-001"
    },
    "confidence": 0.99
  }
}
```

### `preference_pair`

```json
{
  "contract": "dataset_record",
  "schema_version": "1.0",
  "input": "Rewrite the sentence to be more polite: 'Send the file now.'",
  "candidates": [
    {
      "candidate_id": "A",
      "text": "Please send the file when you have a moment."
    },
    {
      "candidate_id": "B",
      "text": "Send the file now."
    }
  ],
  "supervision": {
    "type": "preference_pair",
    "chosen_candidate_id": "A",
    "rejected_candidate_id": "B",
    "comparison_basis": "politeness and instruction preservation"
  },
  "metadata": {
    "dataset_mode": "preference_pair",
    "capability_family": "rewriting",
    "supervision_shape": "pairwise_preference",
    "teacher_role": "style-judge",
    "rubric_reference": "tone.politeness.v1",
    "source_provenance": {
      "source_type": "synthetic_pair",
      "prompt_id": "rewrite-politeness-014",
      "generator_run_id": "pairgen-2026-03-20-01"
    },
    "confidence": 0.93
  }
}
```

### `verifier_outcome`

```json
{
  "contract": "dataset_record",
  "schema_version": "1.0",
  "input": {
    "task": "Return valid JSON with keys `name` and `age` only.",
    "model_output": "{\"name\":\"Ana\",\"age\":12,\"extra\":true}"
  },
  "supervision": {
    "type": "verifier_outcome",
    "verifier_status": "fail",
    "checks": [
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
  "evidence": {
    "verifier_run_id": "json-verifier-8821",
    "failed_check_ids": [
      "schema.allowed_keys"
    ]
  },
  "metadata": {
    "dataset_mode": "verifier_outcome",
    "capability_family": "structured-output",
    "supervision_shape": "binary_verifier",
    "teacher_role": "schema-verifier",
    "evaluator_id": "json-schema-verifier.v3",
    "source_provenance": {
      "source_type": "captured_model_output",
      "task_id": "json-only-119",
      "run_id": "student-run-4412"
    },
    "confidence": 1.0
  }
}
```

### `process_step`

```json
{
  "contract": "dataset_record",
  "schema_version": "1.0",
  "input": {
    "problem": "Compute 17 * 6.",
    "trace_context": "step_index=2 of 3"
  },
  "target": {
    "step_text": "17 * 6 = 102"
  },
  "supervision": {
    "type": "process_step",
    "trace_unit": "reasoning_step",
    "process_label": "correct",
    "local_reward": 1.0,
    "aggregation_rule": "sum step rewards, then normalize by trace length"
  },
  "metadata": {
    "dataset_mode": "process_step",
    "capability_family": "arithmetic",
    "supervision_shape": "step_level_label",
    "teacher_role": "step-verifier",
    "rubric_reference": "math.step-correctness.v1",
    "source_provenance": {
      "source_type": "annotated_trace",
      "trace_id": "arith-trace-2007",
      "step_id": "arith-trace-2007-step-2"
    },
    "confidence": 0.97
  }
}
```

## Lineage Rule

Resolve the dataset mode once for a bundle or session lineage, then keep per-record metadata consistent with that lineage.

Inside `metadata`, keep the contract fields named in this reference stable across exports. Put project-local extras in additional metadata keys rather than renaming the core fields.
