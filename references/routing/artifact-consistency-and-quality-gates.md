# Artifact Consistency and Quality Gates

Use this reference before treating generated artifacts as release-ready or execution-ready.

## Goal

Prevent the skill from producing internally inconsistent plans such as:

- an evaluation plan that does not measure the chosen target
- a training plan that ignores architecture or stack constraints
- a system-composition plan that conflicts with the intervention decision
- a research artifact that leaves route-critical uncertainty unresolved

## Core Principle

Every downstream artifact must remain consistent with the artifacts that came before it.

Do not allow a later artifact to silently overwrite the logic of an earlier one.

## Required Cross-Artifact Checks

### Intake to Evaluation

Check that:

- the evaluation target matches the intake target capability
- the evaluation mode fits the input and output modalities
- the acceptance criteria address the user-stated failure modes
- the held-out or baseline probes actually test the decomposed sub-capabilities

Stop when:

- the evaluation plan measures a different task from the intake
- no evaluator exists for the claimed success condition

### Intake to Intervention Decision

Check that:

- the problem types follow from the intake and decomposition
- the chosen intervention family matches the identified bottleneck
- rejected alternatives are plausible alternatives, not strawmen
- the decision summary reflects the current evidence boundary

Stop when:

- the chosen family does not match the bottleneck hypothesis
- the route depends on assumptions that were still marked unresolved

### Evaluation to Training Plan

Check that:

- the training objective is capable of improving the chosen evaluation metrics
- the supervision shape matches the available evaluation signal
- stop criteria and rollback criteria refer to real evaluation thresholds
- the teacher plan can emit the data shape the training plan requires

Stop when:

- training is proposed without a credible baseline and held-out check
- the objective family is incompatible with the available signal

### Evaluation to System Composition Plan

Check that:

- the evaluation plan judges the whole composed system when the route is system-level
- component interfaces support the measured behavior
- latency and failure handling are reflected in the evaluation criteria

Stop when:

- only the base model is evaluated even though the target capability depends on multiple components

### Research to Decision

Check that:

- the intervention decision cites only confirmed research facts as evidence
- unresolved facts are either fenced by the decision status or routed into followups
- unsupported assumptions are not silently treated as true

Stop when:

- route-critical uncertainty remains unresolved but the decision is marked execution-ready

## Stack-Fit Gates

Before allowing a training or runtime route, confirm:

- the chosen stack supports the intervention family
- the stack supports the architecture or checkpoint format
- the serving target can consume the planned artifacts
- any adapter or quantization assumptions are explicit

Stop when:

- the route assumes stack support that has not been evidenced
- training and serving compatibility are in direct conflict

## Architecture-Fit Gates

Before allowing a route that changes model capability, confirm:

- the current base model can plausibly support the requested modality or action
- architecture changes are considered when the target is beyond the current model class
- system composition or model replacement has been compared when appropriate

Stop when:

- a text-only model is treated as if it can natively acquire speech or vision through ordinary text finetuning alone
- a controller problem is misrouted as a pure language-model objective problem

## Release Gates

Treat the skill as not ready for release unless these conditions hold:

- the invariant workflow is reflected in `SKILL.md`
- core artifact contracts exist and are referenced
- core schemas exist and are referenced
- writer scripts exist for release-critical artifacts
- validator support exists for the release-critical machine-readable artifacts
- domain playbooks exist for the most likely high-variance request families
- unknown-case handling is documented explicitly

## Minimal Artifact Set for a Nontrivial Route

For most nontrivial requests, expect at least:

- capability intake
- evaluation plan
- intervention decision

Then add one of:

- training plan
- system composition plan

And add:

- research evidence

when external research materially influenced route selection.

## Escalation Rules

See `references/orchestration/stop-and-confirmation-policy.md` for the full stop and confirmation policy.

Escalate to a bounded output instead of continuing when any of the artifact-chain checks above fail, specifically:

- intake and evaluation disagree on the target
- intervention choice is unsupported by evidence
- stack support is unclear
- architecture fit is doubtful
- training plan lacks rollback conditions
- system plan has no observability or failure handling

## Anti-Patterns

- treating artifact generation as success even when the artifacts disagree
- writing a training plan before evaluation design exists
- writing a system plan that ignores deployment latency
- writing a decision artifact that hides unresolved facts
- allowing stack convenience to override architecture reality

## Decision Rule

Proceed only when the artifacts agree on:

- target capability
- evaluation path
- intervention family
- execution boundary

If they do not agree, stop and repair the artifact chain before continuing.

## Automation

Use `scripts/validate_artifact_chain.py` after base contract validation whenever more than one release-critical artifact is part of the route.

Treat the chain validator as a hard gate for:

- intake + evaluation + intervention decision
- intake + evaluation + intervention decision + training plan
- intake + evaluation + intervention decision + system composition plan
- any of the above plus research evidence when external research changed the route

Per-artifact validation alone is not sufficient when the artifact chain still disagrees on target capability, route, or execution boundary.
