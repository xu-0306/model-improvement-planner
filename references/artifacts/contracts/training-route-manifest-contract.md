# Training Route Manifest Contract

Use this contract when emitting a stable local training scaffold from an already-selected training plan.

## Goal

Turn a bounded `training_plan` into a repeatable route scaffold without pretending every launcher detail is already production-ready.

## Machine-Readable Contract

Emit one JSON object with:

- `contract`: `training_route_manifest`
- `schema_version`
- `route_family`
- `target_capability`
- `training_plan_reference`
- `intervention_family`
- `trainer_stack`
- `supervision_shape`
- `implementation_candidates`
- `required_dataset_kind`
- `entrypoint`
- `implementation_profile`
- `dataset_path`
- `base_model`
- `output_dir`
- `base_model_suitability_verdict`
- `training_stack_suitability_verdict`
- `serving_compatibility_notes`
- `stop_criteria`
- `rollback_criteria`
- `expected_failure_modes`
- `unresolved_gaps`
- `status`

## Required Interpretation Rule

- `training_route_manifest` is scaffold-facing, not proof that the run is immediately executable.
- Keep unresolved runtime inputs such as missing dataset path or base model explicit in `unresolved_gaps`.
- Keep `route_family` small and normalized, for example `sft`, `preference`, `reward`, or `distill`.
- Treat `implementation_profile` as an optional bundled hint, not as the only valid launcher or stack.
- `entrypoint` should point to the emitted project-local launcher scaffold, even when a bundled profile hint is available.
