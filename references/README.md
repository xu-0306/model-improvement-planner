# References Layout

Use the smallest subset needed for the current run.

## Folders

- `routing/`: core workflow, routing policy, stack selection, and cross-artifact gates
- `orchestration/`: dynamic tool discovery, script-generation policy, and stop/confirmation rules
- `artifacts/contracts/`: human-readable artifact contracts, including dataset, evaluator, local-model-profile, and probe evidence rules
- `artifacts/schemas/`: bundled JSON schemas used by `scripts/validate_contracts.py`, including Phase 2 profile and probe artifacts
- `training/`: supervision, teacher, verifier, and stack-specific training references
- `probes/`: capability-aware probe design playbooks used before route selection
- `data/`: sourcing policy for open datasets, synthetic data, and user-confirmation boundaries
- `domains/`: consolidated domain playbooks for code, tool use, multimodal, and speech/audio

This keeps the top-level `references/` directory as a lightweight index instead of a flat dump of every document, while avoiding paired domain files that duplicated routing and evaluator guidance.

Phase 2 execution support now lives in scripts rather than additional reference sprawl:

- `scripts/local_model_profile.py`: inspect local model metadata, tokenizer facts, and model-card hints before route selection
- `scripts/run_capability_probes.py`: normalize probe specs plus either captured responses, a backend config, or a legacy command backend into `probe-result` and `probe-summary` artifacts, including compact baseline diagnosis and route-readiness hints
- `scripts/discover_environment.py`: inspect the active workspace and emit `environment-discovery.json` before selecting reusable data or training surfaces
- `scripts/emit_generated_script_plan.py`: turn capability, evaluation, and environment artifacts into a project-local scaffold for collection, generation, curation, training, and evaluation
- `scripts/emit_training_route.py`: emit scaffold-only training route artifacts with normalized route families plus optional bundled implementation profiles, without treating those profiles as the only valid execution path
- `references/routing/probe-backend-adapters.md`: minimal config shapes for `command` and `openai_compatible_http` execution backends
- `references/example-runs.md`: concrete command patterns for bootstrap, evidence gathering, route emission, and release smoke testing
