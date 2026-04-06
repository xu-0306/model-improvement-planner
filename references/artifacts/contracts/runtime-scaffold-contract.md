# Runtime Scaffold Contract

Use this reference when generating external support for a model that is not already integrated.

For first-run intake, the default support-exists check, stop/continue rules, response bundle, and artifact locations, start with [cold-start-playbook.md](../../routing/cold-start-playbook.md).

## Boundary

Generate runtime code outside the skill package.

The skill owns:

- orchestration
- discovery logic
- prompt contracts
- validation expectations

The generated scaffold owns:

- runtime identity
- model loading logic
- inference wrapper
- training invocation builder or explicit unsupported declaration

## Required Outputs

Every scaffold should include:

- an adapter module
- a short note describing supported formats
- validation commands
- assumptions and unresolved gaps
- a machine-readable `scaffold_manifest.json`

Use the artifact location convention from the cold-start playbook unless the host project already defines a stronger external layout.

## Required Adapter Fields

- runtime id
- supported model family or artifact pattern
- supported checkpoint formats
- supported tokenizer formats
- inference loading strategy
- training strategy support or unsupported status

## Machine-Readable Contract

Treat `scaffold_manifest.json` as the canonical machine-readable contract for generated scaffolds.

Required manifest keys:

- `contract`: `runtime_scaffold_manifest`
- `schema_version`
- `runtime_id`
- `model_family`
- `supported_checkpoint_formats`
- `supported_tokenizer_formats`
- `inference_loading_strategy`
- `training_support_status`
- `assumptions`
- `unresolved_gaps`
- `status`

Validate generated scaffolds with `scripts/validate_runtime_scaffold.py` before claiming support on the scaffold path. If support is reused rather than generated, follow the reuse gate in `references/routing/cold-start-playbook.md`.

## Safety Rules

- declare unsupported behavior explicitly
- do not silently guess training support
- keep generated code reviewable and minimal
- write validation commands alongside the scaffold
- if support already exists, reuse it instead of generating a duplicate scaffold
