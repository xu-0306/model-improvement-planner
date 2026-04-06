---
name: model-improvement-planner
description: Diagnoses arbitrary local-model capability requests, decomposes the real gap, gathers evidence, selects the narrowest viable intervention family, and emits evaluation, data, training, runtime, or system-composition artifacts. Use when capability work requires intake and routing, method selection, research, supervision planning, contract validation, runtime discovery, or explicit decisions between prompting, tooling, finetuning, distillation, preference optimization, reward-driven optimization, model replacement, and system composition.
---

# Model Improvement Planner

Use this skill as an open-world model improvement controller.

Do not jump straight to finetuning. Start with capability intake, decomposition, problem typing, evidence, and evaluation.

Core principles:

- **Open-world**: listed task families, intervention families, stacks, and benchmarks are illustrative, not exhaustive. Prefer principled decomposition over case memorization.
- **Invariant workflow**: for every request, answer: what capability? where is the gap? what evidence is sufficient? what routes are feasible? which is the narrowest rational intervention? what artifacts come next? what are the stop conditions?
- **Intervention-family policy**: the primary outcome is a justified intervention decision, not "always train the model". Valid families include prompting, tooling, data work, finetuning, distillation, preference optimization, reward-driven optimization, runtime adaptation, system composition, model replacement, or explicit deferral.
- **Unknown-requirement protocol**: when the request exceeds existing references, follow `references/orchestration/unknown-requirement-research-guide.md`.

## Default Workflow

For nontrivial requests, follow this sequence:

1. Inspect the current session and workspace to discover available references, scripts, skills, MCP tools, runtimes, and backend adapters before assuming a route.
2. Normalize the target capability, success criteria, failure modes, deployment context, and requested execution depth.
3. Decompose the request into sub-capabilities, modalities, and external dependencies.
4. Classify the main bottleneck before naming a method.
5. Gather model, tokenizer, checkpoint, runtime, stack, hardware, and evaluation facts.
6. Define the baseline evaluation path and probe-generation plan before proposing data generation or training.
7. Research local references first; use session tools, MCP, and external sources only when local evidence is insufficient.
8. Choose the narrowest viable intervention family and explicit teacher-role bundle.
9. Reuse existing runtime and project support when evidenced; otherwise emit bounded external artifacts or project-local script plans.
10. Emit artifacts, risks, stop rules, confirmation points, and rejected alternatives instead of pretending execution is ready.

Copy this checklist when the run is large enough to need explicit progress tracking:

```text
Capability Optimization Progress
- [ ] Inspect the current session and workspace for available tools and route-relevant constraints.
- [ ] Normalize the target capability, failure modes, success criteria, and deployment target.
- [ ] Decompose the request into sub-capabilities, modalities, and external dependencies.
- [ ] Classify the bottleneck: prompt, data, objective, runtime, controller, subsystem, architecture, or deployment.
- [ ] Inspect model, tokenizer, checkpoint, runtime, stack, and hardware facts.
- [ ] Define a baseline evaluation path, probe-generation plan, and acceptance threshold.
- [ ] Research bundled references first, then use current-session tools and external sources only when local evidence is insufficient.
- [ ] Choose the narrowest viable intervention family and teacher-role bundle before naming implementation methods.
- [ ] Reuse existing support when evidenced; generate project-local scaffolds only when the route and environment justify them.
- [ ] Emit artifacts, risks, stop rules, and rejected alternatives.
```

## Default Output Bundle

Start by producing:

1. normalized capability target
2. decomposition and bottleneck hypothesis
3. confirmed facts and missing facts
4. evaluation-first plan
5. intervention-family recommendation
6. runtime-support verdict: reuse, scaffold, compose externally, replace model, or stop
7. teacher-loop recommendation and data-sourcing policy
8. artifact plan with concrete output paths
9. environment discovery and project-local script-generation plan when execution depends on the active workspace

## Boundaries

- Keep orchestration, decision rules, prompt contracts, and validation logic in the skill.
- Keep generated adapters, training launchers, runtime wrappers, and project-local integration code outside the skill package.
- Treat PEFT as an implementation choice after the objective family is selected.
- Do not claim support, training readiness, or architecture fit without evidence.
- Do not assume any skill, MCP server, or backend exists until it is discoverable in the current session or workspace.
- Prefer bundled references and local evidence before external research.
- Prefer open datasets from Hugging Face or GitHub before asking to scrape the web or use user-private data.
- When evidence is incomplete, emit a bounded recommendation rather than hallucinating readiness.

## Quick Start

Use this fast path when the user needs a concrete execution pattern rather than only policy guidance:

1. Emit the bootstrap pair with `scripts/artifact_cli.py bundle bootstrap`.
2. Inspect the active project with `scripts/discover_environment.py` before assuming local tools, datasets, or training surfaces exist.
3. Inspect the local model with `scripts/local_model_profile.py` and gather baseline evidence with `scripts/run_capability_probes.py` when route choice depends on real capability data.
4. If the route depends on live facts, read bundled references first, then use currently available session tools or external sources to emit `research-evidence`.
5. Emit either `bundle training-route` or `bundle system-route` after the intervention family and teacher-loop plan are justified.
6. Generate a project-local scaffold with `scripts/emit_generated_script_plan.py` when the route depends on workspace-specific data or training surfaces.
7. If the route is training-bound, prefer open datasets from Hugging Face or GitHub before asking to scrape or use user-private data.
8. Validate with `scripts/validate_contracts.py`, then `scripts/validate_artifact_chain.py`.

Use this minimal command pattern for a first nontrivial run:

```bash
python3 scripts/artifact_cli.py bundle bootstrap \
  --output-dir "$WORKSPACE/artifacts/model-improvement-planner/chart-qa" \
  --target-capability "chart-grounded question answering" \
  --user-intent planning \
  --input-modality image \
  --output-modality text \
  --sub-capability chart-extraction \
  --sub-capability grounded-answering \
  --primary-evaluation-mode verifier-based \
  --baseline-probe "held-out chart probe set" \
  --heldout-evaluation "chart qa regression split" \
  --acceptance-criterion "answers stay grounded in image evidence"

python3 scripts/validate_contracts.py \
  --artifact "$WORKSPACE/artifacts/model-improvement-planner/chart-qa/capability-intake.json" \
  --contract capability-intake

python3 scripts/validate_contracts.py \
  --artifact "$WORKSPACE/artifacts/model-improvement-planner/chart-qa/evaluation-plan.json" \
  --contract evaluation-plan
```

Load `references/example-runs.md` only when you need longer copy-paste command patterns for bootstrap, training-route, or system-route flows. Treat those patterns as illustrative helpers, not mandatory stack choices.
Treat any language-specific values in example runs, such as `--target-language zh-Hant`, as case-specific placeholders tied to that user's optimization target, not as defaults for unrelated users or sessions.
Load `references/release-evaluation-cases.md` only when you need manual release review cases and pass/fail expectations.

## From Plan to Execution

After the planning artifacts are ready, follow this path to actual execution:

1. Connect to the student model: determine whether the model is served or raw weights. See `references/routing/student-model-connection-guide.md`.
2. Generate and run probes: author probe specs following `references/probes/probe-spec-template.jsonl` format, then run `scripts/run_capability_probes.py`.
3. Execute teacher loop: the reading model acts as teacher. See `references/training/teacher-loop-execution-guide.md`.
4. Convert training data: transform dataset records into framework-compatible format. See `references/data/dataset-format-guide.md`.
5. Generate training script: produce a project-local training script based on the route and environment. See `references/orchestration/dynamic-script-generation.md`.

For a complete worked example, see `references/walkthrough-example.md`.

When the request is outside the scope of existing references, follow `references/orchestration/unknown-requirement-research-guide.md` to research and design a solution.

## Trigger Examples

These example requests should trigger this skill:

- "Figure out whether my local Qwen checkpoint should use prompting, SFT, or model replacement to improve chart understanding."
- "Diagnose why my tool-use model fails long-horizon tasks and tell me whether the bottleneck is data, controller logic, or runtime support."
- "Plan a system-composition route for invoice image extraction instead of pretending my text-only base model can already do vision."
- "Inspect this local adapter checkpoint, tell me what training and serving stacks are realistic, and emit the next artifacts."
- "I need a bounded recommendation for adding speech I/O to a local model without hallucinating that the current architecture already supports audio."

## Artifact Paths

Use this default convention unless the user gives a project-specific location:

- `<workspace>/artifacts/model-improvement-planner/<target-slug>/capability-intake.json`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/model-discovery.json`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/environment-discovery.json`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/research-evidence.json`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/intervention-decision.json`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/evaluation-plan.json`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/training-plan.json`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/generated-script-plan.json`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/system-composition-plan.json`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/runtime-scaffold/`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/dataset-records.jsonl`
- `<workspace>/artifacts/model-improvement-planner/<target-slug>/evaluator-payloads.jsonl`

## Reference Map

Read only what the current request needs.

Core routing and policy:

- `references/routing/` - capability intake, research routing, evaluation-first workflow, intervention taxonomy, model discovery, training-stack selection, serving compatibility, planner orchestration, method selection matrix, quality gates, student model connection guide, probe backend adapters, cold-start playbook

Dynamic orchestration:

- `references/orchestration/` - tool discovery and routing, dynamic script generation, stop and confirmation policy, unknown requirement research guide

Artifact contracts and schemas:

- `references/artifacts/` - see `references/artifacts/README.md` for the full contract-schema index and required-field summary

Method and supervision references:

- `references/training/` - finetuning method taxonomy, supervision shapes, teacher and verifier prompt contracts, process-reward and verifier contract, route thresholds, Unsloth stack guide, TRL stack guide, teacher-loop execution guide

Probe and data references:

- `references/probes/` - probe generation playbook, probe spec template
- `references/data/` - open dataset sourcing policy, dataset format guide

Domain playbooks:

- `references/domains/code.md`
- `references/domains/tool-use.md`
- `references/domains/multimodal.md`
- `references/domains/speech-audio.md`

Examples and walkthroughs:

- `references/example-runs.md`
- `references/release-evaluation-cases.md`
- `references/walkthrough-example.md`

## Scripts

Prefer the consolidated artifact entrypoint:

- `scripts/artifact_cli.py write capability-intake`
- `scripts/artifact_cli.py write dataset-record`
- `scripts/artifact_cli.py write evaluation-plan`
- `scripts/artifact_cli.py write evaluator-payload`
- `scripts/artifact_cli.py write model-discovery`
- `scripts/artifact_cli.py write environment-discovery`
- `scripts/artifact_cli.py write intervention-decision`
- `scripts/artifact_cli.py write research-evidence`
- `scripts/artifact_cli.py write training-plan`
- `scripts/artifact_cli.py write generated-script-plan`
- `scripts/artifact_cli.py write system-composition-plan`
- `scripts/artifact_cli.py bundle bootstrap`
- `scripts/artifact_cli.py bundle training-route`
- `scripts/artifact_cli.py bundle system-route`

Keep these validation and runtime tools:

- `scripts/local_model_profile.py` for backend-agnostic local model metadata inspection
- `scripts/run_capability_probes.py` for normalized probe-result and probe-summary emission from probe specs plus either captured responses, a backend config, or a legacy backend command; use `probe_summary` as the compact baseline-diagnosis artifact before route selection
- `scripts/discover_environment.py` for environment-first workspace inspection before selecting reusable project-local data or training surfaces
- `scripts/emit_generated_script_plan.py` for emitting project-local source collection, data generation, curation, training, and evaluation scaffold steps from the discovered environment
- `scripts/emit_training_route.py` for scaffold-only `training_route_manifest`, `train_config.json`, and `launch.sh` emission. Use normalized route families first, then add an optional bundled implementation profile only when it matches the discovered environment.
- `scripts/validate_contracts.py` for single-artifact contract checks
- `scripts/validate_artifact_chain.py` for cross-artifact consistency
- `scripts/generate_runtime_scaffold.py` for generic external scaffolds
- `scripts/validate_runtime_scaffold.py` for scaffold validation
- `scripts/smoke_test.py` for a bundled release-hardening check that exercises bootstrap, probes, training-route emission, system-route emission, and runtime scaffold validation in a temporary workspace

Use `artifact_cli.py` and `validate_contracts.py` as the canonical entrypoints.

## Dynamic Execution Rules

When the request depends on live facts or external capabilities:

1. inspect the current session and workspace first
2. read bundled references before using external tools
3. discover which skills, MCP tools, backends, and runtimes are actually available now
4. choose the narrowest tool that can complete the current step
5. record route-critical findings in `research-evidence` or `tool-inventory`

When data collection is needed:

1. prefer local datasets first
2. then search open datasets from Hugging Face
3. then search open datasets or curated corpora from GitHub
4. if still insufficient, ask the user before scraping web data or using private data

When script generation is needed:

1. generate project-local scripts only after the route is justified
2. prefer small single-purpose scripts over one large orchestrator
3. use scaffold-only scripts when route-critical facts remain unresolved

## Release Validation

Before publishing or after major edits:

1. Run `python3 scripts/smoke_test.py`.
2. Review the manual checks in `references/release-evaluation-cases.md`.
3. Confirm the skill still routes multimodal and system-composition requests conservatively instead of defaulting to finetuning.
