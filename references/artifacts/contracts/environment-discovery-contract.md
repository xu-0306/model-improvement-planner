# Environment Discovery Contract

Use this contract when the skill inspects a real project workspace before selecting a data or training execution path.

## Goal

Capture what the current project already exposes so later planning can reuse detected surfaces instead of assuming one fixed stack.

## Machine-Readable Contract

Emit one JSON object with:

- `contract`: `environment_discovery`
- `schema_version`
- `workspace_root`
- `environment_summary`
- `discovered_surfaces`
- `constraints`
- `unresolved_gaps`
- `notes`

## Interpretation Rules

- `environment_summary` should capture high-level implementation affordances such as package managers, framework hints, available runtimes, and allowed source-access patterns.
- `discovered_surfaces` should capture concrete reusable surfaces already present in the project, such as dependency files, training entrypoints, serving entrypoints, dataset-related files, and evaluation files.
- This artifact is descriptive, not authoritative proof that any detected surface is production-ready.
- Keep unresolved or missing execution details explicit in `unresolved_gaps`.

## Default Output Path

- `artifacts/model-improvement-planner/<target-slug>/environment-discovery.json`
