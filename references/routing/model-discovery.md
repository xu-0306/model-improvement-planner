# Model Discovery

Use this reference when the requested model does not already have a known runtime integration.

## Goal

Produce a normalized fact sheet before treating a route as execution-ready.

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

Capture at least:

- model family hint
- checkpoint or weight format
- tokenizer format
- expected load path
- likely inference library
- likely training library or unsupported status
- device/runtime assumptions
- missing facts that still block safe support

If structured output helps, use a compact fact sheet such as:

```json
{
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

- If the model can be classified safely, continue with route selection and serving-fit checks.
- If critical facts are missing, stop and report the missing facts instead of guessing.
