# Local Model Profile Contract

Use this contract for deterministic inspection output produced before baseline probing.

## Goal

Capture local checkpoint facts that affect route selection without pretending metadata alone proves capability strength.

## Machine-Readable Contract

Emit one JSON object with:

- `contract`: `local_model_profile`
- `schema_version`
- `model_id`
- `model_path`
- `profile_status`
- `architecture`
- `tokenizer`
- `generation`
- `model_card`
- `adapter_presence`
- `family_hints`
- `language_hints`
- `capability_hints`
- `stack_hints`
- `inspected_files`
- `unresolved_facts`

## Required Interpretation Rule

- Treat `language_hints` and `capability_hints` as priors, not verdicts.
- Keep unresolved items explicit when metadata is missing.
- Require empirical probes before claiming which language or capability is strongest.
