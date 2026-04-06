# Route Thresholds

Use this reference when baseline evidence exists and the skill must choose the narrowest viable intervention family.

## Goal

Prevent premature training and make route changes more consistent across language, coding, tool-use, multimodal, and speech requests.

## First Decision

Before comparing training routes, decide whether the problem is:

- prompt or control
- data or supervision
- evaluator weakness
- runtime or controller deficiency
- architecture mismatch
- missing subsystem

If architecture mismatch or missing subsystem is still plausible, compare system composition and model replacement before training.

## Prompt Or Probe Expansion

Prefer prompt/control changes or additional probing when:

- the current evidence is thin or contradictory
- failures look formatting- or instruction-bound
- the model shows usable capability but unstable surface behavior
- training feasibility remains uncertain

## SFT

Prefer SFT when:

- the model can already perform the task in principle
- the main issue is weak demonstrations or distribution mismatch
- corrected or teacher-authored targets are stable enough to export
- evaluator quality is sufficient for held-out acceptance checks

## PEFT-SFT

Prefer PEFT-SFT over full SFT when:

- the same conditions as SFT hold
- compute or deployment constraints favor adapters
- the base model architecture and stack already support the adapter route

Do not choose PEFT only because it sounds cheaper. It is an implementation profile, not a justification by itself.

## Distillation

Prefer distillation when:

- the baseline is very weak or unstable
- critique-rewrite is not enough because the student lacks a workable pattern
- a stronger teacher or system exists and can emit reliable targets
- the deployment target still needs a smaller or cheaper student

## Preference Optimization

Prefer preference routes when:

- pairwise ranking is easier or more reliable than writing a single gold target
- the key failures are comparative quality failures rather than pure task absence
- preference labels are stable enough to avoid noisy route selection

Do not use preference optimization as a generic upgrade path when demonstrator data would already solve the problem.

## Reward-Driven Optimization

Prefer reward-driven routes only when:

- outcome-only supervision hides important search or process mistakes
- a meaningful verifier, reward signal, or process labeling strategy exists
- the added route complexity is justified by the task

Avoid reward-driven routes when the same task can be solved with demonstrator, critique, or preference data.

## System Composition

Prefer system composition when:

- the requested capability depends on subsystems the base model does not natively support
- speech, browser, retrieval, tool controllers, or multimodal bridges are the real gap
- the user wants end-to-end behavior, not necessarily weight changes

## Model Replacement

Prefer model replacement when:

- the target capability is structurally misaligned with the current model family
- the current architecture would require disproportionate work compared with using a better base model
- repeated evidence suggests the current base is not a rational training target

## Minimum Evidence Before Training-Bound Routes

Require at least:

- baseline probes that isolate a weak cluster
- a plausible evaluator or held-out acceptance path
- enough stack evidence to believe the route is executable
- a data or teacher plan matching the chosen supervision shape

If any of those are missing, stay bounded and stop before claiming training readiness.
