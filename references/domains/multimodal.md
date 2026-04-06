# Multimodal Playbook

Use this reference when the requested capability depends on image, video, audio-visual, or broader multimodal grounding rather than text alone.

## Goal

Route multimodal requests by architecture fit, subsystem needs, evaluation design, and deployment constraints before recommending training.

## Start With Decomposition

Break the request into:

- input modalities
- output modalities
- grounding requirements
- perception requirements
- fusion requirements
- generation requirements
- controller or subsystem needs

Do not reduce a multimodal request to "make the model see images" without decomposing what must actually happen.

## Architecture-Fit Check

Ask these questions first:

- is the base model text-only, multimodal-native, or composed with external encoders
- does the current architecture already support the required encoder, projector, or cross-modal path
- is there existing runtime support for the required modality bridge
- is the task perception, grounding, description, retrieval, action, or generation
- is system composition more rational than attempting direct adaptation

If the model is text-only and has no credible multimodal bridge, do not assume ordinary SFT will make it multimodal.

Compare these routes first:

- model replacement with a multimodal-native architecture
- system composition with an external perception model
- architecture adaptation with a supported projector or encoder path

## Common Route Patterns

Representative route patterns:

- image understanding
- image-grounded question answering
- chart or diagram interpretation
- OCR-adjacent extraction
- video event understanding
- audio-text grounding
- multimodal instruction following
- multimodal tool selection or navigation

If the task controls downstream actions, evaluate both the grounding step and the downstream action.

## Evaluation Targets and Grounding Checks

Select evaluation targets that match the real capability:

- perception accuracy
- grounding fidelity
- cross-modal consistency
- instruction adherence
- localization of referenced entities
- hallucination resistance
- OCR or extraction accuracy when relevant
- action or tool correctness when multimodal inputs drive downstream steps

Prefer the strongest available evaluator:

- exact or structured match for extraction tasks
- grounding checks for referenced objects or regions
- rubric-based review for descriptive tasks
- benchmark tasks when representative
- verifier-backed checks when multimodal outputs drive a tool or action
- human review when subtle grounding or salience matters

If grounding cannot be tested credibly, do not present the route as training-ready.

## Data Shapes and Teacher Roles

Useful supervision shapes include:

- multimodal instruction-response pairs
- grounded extraction records
- critique-rewrite records for hallucination correction
- chosen-rejected preference pairs for competing grounded outputs
- verifier outcomes for structured or tool-coupled tasks
- trajectory records when multimodal inputs drive multi-step workflows

Useful roles include:

- `diagnostician` for architecture-fit and failure mode analysis
- `demonstrator` for grounded target outputs
- `critique teacher` for hallucination and grounding errors
- `verifier` for structured extraction, constrained outputs, or downstream action checks
- `preference judge` when relative grounding quality is easier to assess than absolute quality

Choose the data shape that preserves the actual evidence the model is supposed to use.

## Composition Versus Training

Prefer system composition or model replacement when:

- the base model is text-only and the requested modality is native to the task
- the current stack cannot support the necessary encoder or projector path
- the target requires reliable multimodal grounding beyond what lightweight adaptation can plausibly recover
- the deployment model must already be multimodal at inference time

Prefer training or architecture adaptation when:

- the chosen stack already supports the required multimodal path
- integrated behavior is a real requirement
- the evaluation plan can distinguish grounding gains from style changes
- serving and deployment can preserve the multimodal path

## Gating Checks

Before training:

- confirm architecture fit
- confirm the evaluation path
- confirm the data shape matches the actual multimodal task
- confirm hallucination checks exist
- confirm serving or deployment can preserve the multimodal path

## Stop Rules

Stop and emit a bounded recommendation when:

- modality support is absent or doubtful
- grounding cannot be evaluated credibly
- the correct answer is model replacement or system composition
- the available data only measures stylistic quality, not multimodal correctness

## Anti-Patterns

- treating multimodal work as text-only instruction tuning
- evaluating only output fluency while ignoring grounding
- assuming a projector or adapter alone proves real multimodal competence
- using preference tuning before direct grounded behavior is established
- hiding architecture mismatch behind a generic finetuning plan

## Decision Rule

For multimodal requests:

1. check architecture fit first
2. choose evaluation before training
3. prefer composition or replacement when native support is weak
4. train only when the modality bridge and deployment path are both credible
