---
name: model-improvement-planner
description: Diagnoses local-model capability gaps, decomposes bottlenecks, selects the narrowest viable intervention family, and produces evaluation-first improvement plans with recommended outputs and next steps. Use when capability work requires problem framing, bottleneck diagnosis, research planning, supervision/data strategy, or explicit decisions between prompting, tooling, finetuning, distillation, preference optimization, reward design, model editing, model merging, continual learning, retrieval-conditioned tuning, system composition, model replacement, or stop/defer.
---

# Model Improvement Planner

Use this skill as a planning and routing layer for model improvement work.

Do not jump straight to finetuning. Diagnose the real gap first, define how it will be measured, then choose the narrowest rational intervention.

## Core Positioning

- Treat the primary output as a justified intervention decision, not as "a training plan by default."
- Work evaluation-first: define baseline checks, probes, and acceptance criteria before proposing data generation or training.
- Separate model problems from controller, runtime, serving, retrieval, tool, or architecture problems.
- Prefer the narrowest viable route: prompting, tooling, data cleanup, evaluation improvement, small post-training, system composition, model replacement, or explicit stop/defer.
- Keep recommendations evidence-gated. When facts are missing, say what is confirmed, what is missing, and what must be checked next.
- Use bundled references only as needed. Keep the main workflow here; load deeper guidance only for the selected route.

## Default Workflow

Follow this sequence for any nontrivial request:

1. Normalize the target capability, failure mode, success criteria, deployment context, and user intent.
2. Decompose the request into sub-capabilities, modalities, external dependencies, and likely failure surfaces.
3. Classify the main bottleneck before naming a method: prompt, data, objective, evaluator, runtime, controller, retrieval, subsystem, architecture, or deployment.
4. Gather route-critical facts about the student model, tokenizer, checkpoint form, serving path, hardware, data availability, and constraints.
5. Mark confirmed facts versus missing facts. Do not fill gaps with assumptions.
6. Define the baseline evaluation path: probes, held-out checks, acceptance thresholds, and failure evidence needed to move forward.
7. Decide whether additional research is needed. Prefer bundled references first, then local workspace evidence, then external sources when required.
8. Choose the narrowest intervention family that can plausibly close the gap.
9. Recommend supervision, teacher, verifier, or data strategy only after the intervention family is chosen.
10. Emit a bounded output bundle: diagnosis, evidence state, evaluation-first plan, route recommendation, rejected alternatives, risks, stop rules, and next actions.

Use this checklist when the run is large enough to need explicit tracking:

```text
Model Improvement Planning
- [ ] Normalize target capability, failures, success criteria, and deployment context.
- [ ] Decompose the capability into sub-problems and dependencies.
- [ ] Classify the bottleneck before choosing a method.
- [ ] Gather model, runtime, serving, hardware, and data facts.
- [ ] Separate confirmed facts from missing facts.
- [ ] Define baseline evaluation and acceptance thresholds.
- [ ] Research only as needed, starting from bundled references.
- [ ] Choose the narrowest viable intervention family.
- [ ] State rejected alternatives, risks, stop rules, and next actions.
```

## Decision Checkpoints

Answer these questions before committing to a route:

1. What exact capability is being improved, and how will success be measured?
2. Is the failure actually in the model, or in prompting, controller logic, retrieval, tools, serving, or environment setup?
3. Is there an architecture mismatch? Do not recommend multimodal or speech training when the current system lacks the required subsystem.
4. Are evaluation and probes strong enough to distinguish prompt fixes from model-side improvements?
5. What facts are missing that could invalidate the recommendation?
6. What supervision shapes are available: preferences, demonstrations, verifier labels, trajectories, edits, retrieval traces, or only weak outcomes?
7. Does the proposed route fit the serving target, packaging constraints, latency budget, and hardware reality?
8. Is there a narrower route that should be tried first?
9. What should stop the plan from proceeding until more evidence or user confirmation is available?

## Default Output Bundle

Produce a concise planning bundle in sections or structured fields. Use `references/output-shapes.md` when the request benefits from a more explicit shape. Include at least:

1. `target_capability`: the normalized capability and success condition
2. `decomposition`: sub-capabilities, dependencies, and main failure surfaces
3. `bottleneck_hypothesis`: primary bottleneck and why it is the leading explanation
4. `confirmed_facts`: route-critical facts already established
5. `missing_facts`: unknowns that could change the route
6. `evaluation_plan`: baseline probes, held-out checks, and acceptance thresholds
7. `intervention_decision`: recommended family, why it fits, and what it is not
8. `rejected_alternatives`: narrower or broader routes considered and rejected
9. `risks_and_stop_rules`: what could invalidate the plan or require confirmation
10. `next_actions`: the smallest sensible next steps

When the request needs more structure, organize the bundle as:

- capability brief
- fact inventory
- evaluation plan
- intervention decision
- next-step execution outline

## Boundaries

- Keep this skill focused on diagnosis, routing, and planning.
- Do not assume any bundled automation, private toolkit, or hidden backend exists.
- Do not promise training readiness, stack compatibility, serving compatibility, or dataset sufficiency without evidence.
- Do not recommend training when prompt, controller, retrieval, or system-composition fixes are more plausible.
- Do not overclaim architecture fit for multimodal, audio, or tool-use requests.
- Prefer local and open data sources before suggesting scraping or private data use.
- If evidence is incomplete, emit a bounded recommendation or stop/defer decision instead of pretending execution is ready.

## Reference Map

Read only what the current request needs.

Core routing:

- `references/routing/capability-intake-and-routing.md`
- `references/routing/evaluation-first-workflow.md`
- `references/routing/intervention-taxonomy.md`
- `references/routing/method-selection-matrix.md`
- `references/routing/research-routing.md`
- `references/routing/artifact-consistency-and-quality-gates.md`
- `references/routing/model-discovery.md`
- `references/routing/training-stack-selection.md`
- `references/routing/serving-compatibility-guide.md`

Orchestration and policy:

- `references/orchestration/stop-and-confirmation-policy.md`
- `references/orchestration/tool-discovery-and-routing.md`
- `references/orchestration/unknown-requirement-research-guide.md`

Evaluation and data:

- `references/output-shapes.md`
- `references/examples/planning-examples.md`
- `references/probes/probe-generation-playbook.md`
- `references/data/open-dataset-sourcing-policy.md`
- `references/training/supervision-shapes.md`

Family-specific routing:

- `references/training/distillation-patterns.md`
- `references/training/peft-method-selection.md`
- `references/training/model-editing-method-taxonomy.md`
- `references/training/model-merging-guide.md`
- `references/training/self-play-and-self-improvement.md`
- `references/training/continual-learning.md`
- `references/training/rag-tuning.md`

Domain playbooks:

- `references/domains/code.md`
- `references/domains/tool-use.md`
- `references/domains/multimodal.md`
- `references/domains/speech-audio.md`

## Trigger Examples

These requests should trigger this skill:

- "Figure out whether this local checkpoint needs prompting changes, finetuning, or full model replacement."
- "Diagnose why my tool-use model fails long tasks and tell me whether the bottleneck is the model, controller, or runtime."
- "Plan the safest route for adding chart understanding without pretending the current architecture already supports vision."
- "Decide whether this retrieval-grounded failure needs RAG tuning, better evidence use, or just evaluation cleanup."
- "Tell me whether continual learning, model editing, or merging is the right update path for this checkpoint."
- "Give me an evaluation-first improvement plan and the smallest next step instead of a generic training recipe."
