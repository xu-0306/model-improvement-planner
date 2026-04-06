# Model Discovery

Use this reference when the requested model does not already have a known runtime integration.

For first-run intake, stop/continue behavior, response shape, artifact locations, and the default "does support already exist?" check, start with [cold-start-playbook.md](./cold-start-playbook.md).

## Goal

Produce a normalized discovery artifact before generating any external runtime scaffold.

## Inspect

- requested runtime id
- model family or architecture hint
- checkpoint format
- tokenizer format
- config files
- inference/runtime constraints
- training constraints
- hardware constraints

## Do Not Assume

- support from model brand alone
- that all `.bin` or `.safetensors` files follow the same loading path
- that inference and training stacks are the same

## Minimum Discovery Output

Capture the minimum intake fact sheet from the cold-start playbook, then add:

- model family hint
- checkpoint or weight format
- tokenizer format
- expected load path
- likely inference library
- likely training library or unsupported status
- device/runtime assumptions
- missing facts that still block safe support

## Machine-Readable Contract

Prefer a JSON artifact with these top-level fields:

- `contract`: `model_discovery`
- `schema_version`
- `requested_runtime_id`
- `model_family_hint`
- `checkpoint_format`
- `tokenizer_format`
- `expected_load_path`
- `likely_inference_library`
- `likely_training_library_or_status`
- `device_runtime_assumptions`
- `runtime_constraints`
- `missing_facts`

Keep empty strings or empty arrays instead of inventing values. Add project-specific fields only as non-contract extensions.

Example shape:

```json
{
  "contract": "model_discovery",
  "schema_version": "1.0",
  "requested_runtime_id": "example-runtime",
  "model_family_hint": "decoder-only transformer",
  "checkpoint_format": "safetensors",
  "tokenizer_format": "sentencepiece",
  "expected_load_path": "from_pretrained local directory",
  "likely_inference_library": "transformers",
  "likely_training_library_or_status": "unsupported",
  "device_runtime_assumptions": ["single GPU"],
  "runtime_constraints": [],
  "missing_facts": []
}
```

## Decision Rule

- If the model can be classified safely after the cold-start checks, generate an external runtime scaffold.
- If critical facts are missing, stop and report the missing facts instead of guessing.
