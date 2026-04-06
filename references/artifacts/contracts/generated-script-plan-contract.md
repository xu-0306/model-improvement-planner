# Generated Script Plan Contract

Use this contract when the skill turns capability artifacts plus environment discovery into a project-local execution scaffold.

## Goal

Describe which scripts should be generated or called for source collection, data generation, curation, training, and evaluation without pretending the skill only supports one hardcoded launcher.

## Machine-Readable Contract

Emit one JSON object with:

- `contract`: `generated_script_plan`
- `schema_version`
- `target_capability`
- `plan_status`
- `selected_flow_kind`
- `capability_intake_reference`
- `evaluation_plan_reference`
- `environment_discovery_reference`
- `training_plan_reference` when a training plan shaped the flow
- `dataset_strategy`
- `script_plan`
- `assumptions`
- `unresolved_gaps`

## Interpretation Rules

- `script_plan` is the canonical list of generated or callable project-local steps.
- Each script step should identify its `script_id`, `path`, `script_kind`, `purpose`, `inputs`, `outputs`, and `status`.
- Framework-specific launchers may appear as optional implementation profiles, but the artifact must not imply that one bundled launcher is the only valid route.
- Use `plan_status` to distinguish between scaffold-only output and something closer to execution-ready handoff.

## Default Output Path

- `artifacts/model-improvement-planner/<target-slug>/generated-script-plan.json`
