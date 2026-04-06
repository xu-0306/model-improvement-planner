# Planner Orchestration Guide

Use this reference when chaining the release-critical artifacts through lightweight planner scripts rather than creating each artifact manually.

## Goal

Provide a bounded orchestration layer that can:

- bootstrap the first artifacts from a normalized request
- carry forward only the fields needed by downstream planners
- stop when the artifact chain is not yet safe to continue
- keep later planners from silently rewriting earlier decisions

These planners are orchestration helpers, not a replacement for capability decomposition, evaluation-first routing, or evidence gathering.

## Planner Chain

Use the planners in this order:

1. bootstrap capability workflow
2. refine or validate intake and evaluation artifacts as needed
3. choose a route
4. run either the training-route planner or the system-route planner

Do not continue automatically past a point where the current artifacts still contain route-critical uncertainty.

## Planner Ownership

### Bootstrap Planner

The bootstrap planner should own:

- initial capability intake artifact
- initial evaluation-plan artifact
- default output paths
- the first bounded decomposition and measurement skeleton

It should not own:

- final method choice
- final stack choice
- final training-plan or system-composition-plan details

### Training-Route Planner

The training-route planner should own:

- intervention decision for a training-bound route
- training-plan artifact
- linkage to evaluation and research artifacts
- explicit rejected alternatives and execution boundary

It should not own:

- system composition design
- runtime scaffolding for unsupported architectures
- evidence fabrication when research is incomplete

### System-Route Planner

The system-route planner should own:

- intervention decision for a system-composition route
- system-composition-plan artifact
- linkage to evaluation and research artifacts
- explicit reasons why training is not the immediate next step

It should not own:

- a training plan that the current route has not justified
- architecture claims unsupported by the current artifacts

## Artifact Preconditions

For the full cross-artifact consistency checks, see `references/routing/artifact-consistency-and-quality-gates.md`.

### Before Bootstrap

Require at least:

- target capability
- user intent
- minimal deployment context or declared unknowns

### Before Training-Route Planning

Require at least:

- capability intake artifact
- evaluation plan artifact
- enough evidence to justify a training-bound intervention family

Prefer also:

- research evidence when external sources materially shaped the route

### Before System-Route Planning

Require at least:

- capability intake artifact
- evaluation plan artifact
- enough evidence to justify a system-composition route

Prefer also:

- research evidence when subsystem selection or architecture fit depends on external sources

## Chaining Rules

- carry forward target capability unchanged unless the earlier artifact was explicitly corrected
- keep the intervention decision aligned with the intake bottleneck hypothesis and evaluation path
- keep the execution boundary explicit at each step
- keep rejected alternatives visible rather than silently discarding them
- keep research-derived uncertainty visible if it still affects the route

## Stop Instead Of Chaining Further

See `references/orchestration/stop-and-confirmation-policy.md` for the full stop and confirmation policy.

Stop and emit a bounded artifact chain specifically when:

- intake and evaluation disagree on the actual target capability
- the evaluation path does not support the claimed route
- architecture fit is still unresolved
- stack support is still unresolved for a training-bound route
- the route depends on research that has not yet been completed
- the correct answer is still "defer", "replace model", or "compose externally"

When any of those are true, emit a bounded artifact chain and stop rather than forcing a downstream plan.

## Typical Flow Patterns

### Early Planning

`bootstrap -> manual review -> intervention decision`

Use when:

- the task is still being classified
- evaluation design is more important than immediate execution

### Training-Bound Flow

`bootstrap -> research/evaluation refinement -> training-route planner`

Use when:

- the chosen route is supervised, distillation, preference, or reward-driven
- the base model and stack appear viable

### System-Bound Flow

`bootstrap -> research/evaluation refinement -> system-route planner`

Use when:

- the requested capability depends on subsystems, controllers, or modality bridges
- direct model tuning is not yet the rational next step

## Anti-Patterns

- letting the bootstrap planner imply a final method choice
- running both route planners as if the route were unresolved
- using the training-route planner when architecture fit is still doubtful
- using the system-route planner while silently assuming a training route will happen anyway
- chaining artifacts even after the quality gates say to stop

## Decision Rule

Use planners to make artifact generation more consistent, not to bypass judgment.

If the current artifacts do not justify the next planner, stop, repair the artifact chain, and only then continue.
