# Dataset Format Guide

Use this reference when the route produces `dataset-records.jsonl` and the downstream training framework requires a specific wrapper format.

## 1. Native Schema

- deliver records that match `references/artifacts/schemas/dataset-record.schema.json`
- each record must include `contract`, `schema_version`, `input`, and `metadata` (with `dataset_mode`, `capability_family`, `supervision_shape`, and `source_provenance`)
- the native record may also carry `target`, `candidates`, `supervision`, or `evidence`, depending on the supervision shape
- keep `metadata.teacher_role` or `metadata.teacher_roles` aligned with the teacher-loop decision
- use `metadata.source_provenance` for lineage and avoid duplicating provenance fields elsewhere

## 2. Conversion Targets

Describe each target so the skill can map native records to the format the training stack expects.

### Alpaca (`instruction` / `input` / `output`)

- `input` -> `instruction`
- optional context or secondary fields -> `input`
- `target` or `supervision.corrected_output` -> `output`
- `metadata` -> `context` metadata block (capability and confidence)

```python
from pathlib import Path
import json

def to_alpaca(record):
    return {
        "instruction": record["input"],
        "input": "",
        "output": record.get("target") or record["supervision"]["corrected_output"],
        "context": {
            "capability_family": record["metadata"]["capability_family"],
            "teacher_role": record["metadata"].get("teacher_role", record["metadata"].get("teacher_roles"))
        }
    }
```

### ChatML (`messages` array)

- create a `messages` array following OpenAI-style structure
- use `input` as `system/user` turns; add `assistant` turn with the corrected output or chosen candidate
- attach metadata to the last message via `metadata` field or a final `system` message listing capability data

```python
def to_chatml(record):
    messages = [{"role": "user", "content": record["input"]}]
    if target := record.get("target"):
        messages.append({"role": "assistant", "content": target})
    return {"messages": messages, "meta": record["metadata"]}
```

### ShareGPT (`conversations`)

- flatten `input` plus `target` into a sequence of turns (`user` request, `assistant` response)
- include `metadata` under `conversation_meta`
- preserve lens on difficulty and teacher role within `conversation_meta`

```python
def to_sharegpt(record):
    convo = [
        {"role": "user", "content": record["input"]},
        {"role": "assistant", "content": record.get("target", record["supervision"]["corrected_output"])}
    ]
    return {"conversations": convo, "conversation_meta": record["metadata"]}
```

### TRL DPO (prompt/chosen/rejected)

- map `input` -> `prompt`
- use `metadata.dataset_mode` to confirm this is a `preference_pair`
- `supervision.chosen_candidate_id` and `.rejected_candidate_id` become DPO fields

```python
def to_dpo(record):
    return {
        "prompt": record["input"],
        "chosen": next(c["text"] for c in record["candidates"] if c["candidate_id"] == record["supervision"]["chosen_candidate_id"]),
        "rejected": next(c["text"] for c in record["candidates"] if c["candidate_id"] == record["supervision"]["rejected_candidate_id"])
    }
```

### Tokenized HF Dataset

- tokenize `input`/`target` with the training tokenizer
- store both token ids and raw text (for audit)
- include `metadata` fields as dataset features (`capability_family`, `teacher_role`, `dataset_mode`)

```python
def to_tokenized(record, tokenizer):
    encoded = tokenizer(record["input"], return_tensors="pt")
    target = record.get("target") or record["supervision"].get("corrected_output")
    return {
        "input_ids": encoded["input_ids"][0].tolist(),
        "labels": tokenizer(target)["input_ids"],
        "meta": record["metadata"]
    }
```

## 3. Auto-Selection Logic

Inspect `training-plan.json` before choosing which conversion runs:

1. `intervention_family` tells you whether SFT-like formats (Alpaca, ChatML) or preference/ranking formats (TRL DPO) are appropriate.
2. `implementation_candidates` that mention `instruction_tuning`, `editor-style`, or `tool-trace` favor ChatML or Alpaca.
3. `supervision_shape` signals preference vs direct answer vs process trace.
4. `data_plan.sources` lists artifacts that must be preserved at conversion time (include the referenced `dataset_record` fields in the converted artifact).

Use these fields to pick a conversion target, and document the reasoning in `generated-script-plan` or `training-plan`.

## 4. Conversion Script Guidelines

- generate `scripts/convert_dataset.py` inside the project workspace (not in the skill)
- script must declare purpose, inputs, outputs, required runtimes, and validation command
- it should accept `--input records` and `--target-format` arguments
- support outputting both the target format and a validation summary (e.g., `--validate-contract dataset_record`)
- reuse `convert_dataset` when multiple formats are needed; parameterize `--format`
- mention unresolved preconditions (missing tokenizer, missing rubric reference) when script is in `scaffold_only`

When the training plan expects more than one format, the script should emit each format to a subdirectory named after the format, along with a manifest linking to the original dataset records and the compatibility notes recorded in `training-plan.json`.
