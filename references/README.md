# Public References

Use the smallest subset needed for the current planning run.

This directory supports the public planning/routing skill. Start from `SKILL.md`, then read only the categories that matter for the current request.

## Core routing

- `routing/`: capability intake, evaluation-first workflow, intervention taxonomy, method selection, research routing, model discovery, training-stack selection, serving-compatibility checks, and cross-plan quality gates

Read this category first for most requests.

## Orchestration and policy

- `orchestration/`: stop-and-confirmation rules, tool-discovery checks, and guidance for unknown or under-specified requests

Read this when route decisions depend on missing facts, tool boundaries, or explicit user confirmation.

## Public output and examples

- `output-shapes.md`: minimal public planning-bundle shapes
- `examples/planning-examples.md`: short planning-first examples that show decomposition, evaluation-first moves, route choice, and stop gates

Read these when you need to structure the output or calibrate how detailed the plan should be.

## Evaluation, data, and route depth

- `probes/`: baseline probe design before escalation
- `data/`: open-data sourcing and data-boundary policy
- `training/`: supervision shapes and family-specific routing depth such as distillation, PEFT, model editing, merging, continual learning, self-improvement, and retrieval-conditioned tuning
- `domains/`: domain playbooks for code, tool use, multimodal, and speech/audio

Read these only after the main bottleneck and likely intervention family are clear.

If a `legacy/` directory exists elsewhere in the repo, treat it as historical material rather than part of the public reference surface.
