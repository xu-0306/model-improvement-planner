# Supervision Shapes

Use this reference when mapping available data into a training or evaluation method.

## Goal

Recognize the supervision shape first, then choose methods that match the evidence it actually provides.

## Common Shapes

### Unlabeled Corpus

Shape:

- raw text, actions, traces, or multimodal records without explicit quality labels

Supports:

- domain adaptation
- language or behavior modeling
- representation learning
- synthetic relabeling pipelines

Pitfalls:

- quality is unknown
- spurious style can dominate capability
- hidden contamination or duplication can distort results

### Demonstration Pair

Shape:

- task input plus expert target output or action

Supports:

- imitation learning
- supervised fine-tuning
- bootstrapping a baseline policy

Pitfalls:

- demonstrations may encode one style rather than the full task distribution
- weak demonstrations cap downstream quality

### Instruction-Response Pair

Shape:

- instruction or prompt plus response, usually without explicit comparison or critique

Supports:

- instruction following
- assistant tuning
- response formatting alignment

Pitfalls:

- latent quality varies
- underspecified instructions produce noisy targets

### Critique-Rewrite

Shape:

- imperfect output, critique, and rewrite or correction

Supports:

- self-correction training
- critique-conditioned editing
- mistake-aware fine-tuning

Pitfalls:

- critique may be vague or inconsistent with the rewrite
- rewrite can fix the answer while preserving the wrong process

### Chosen-Rejected

Shape:

- two or more candidates with a marked winner and loser

Supports:

- preference optimization
- ranking losses
- reward-model training from comparisons

Pitfalls:

- only relative quality is observed
- hard negatives and near-ties should not be mixed casually

### Binary Desirable-Undesirable

Shape:

- single item labeled acceptable or unacceptable

Supports:

- binary classification
- filtering
- safety gating
- simple reward modeling

Pitfalls:

- lacks preference strength
- label definitions drift easily across annotators

### Scalar Reward

Shape:

- single item with numeric score

Supports:

- reward modeling
- ranking if scales are comparable
- regression-based filtering or reranking

Pitfalls:

- scales are often inconsistent across tasks or raters
- score compression can hide meaningful differences

### Verifier Result

Shape:

- output plus external pass or fail signal, checks, or execution result

Supports:

- outcome verification
- rejection sampling
- verifier-guided search
- correctness filtering

Pitfalls:

- verified does not always mean high quality
- unverifiable parts of the task may remain wrong

### Process-Step Label

Shape:

- intermediate step with local label, reward, or annotation

Supports:

- process supervision
- trajectory scoring
- decomposition training

Pitfalls:

- local labels can conflict with global success
- annotation cost rises quickly with trajectory length

### Rationale or Trajectory Distillation

Shape:

- final answer paired with rationale, chain, tool trace, or full trajectory from a stronger source

Supports:

- policy distillation
- rationale-conditioned training
- trajectory compression

Pitfalls:

- copied rationales may be verbose, brittle, or post-hoc
- exposing full trajectories can teach artifacts instead of principles

### Distribution Targets

Shape:

- soft targets such as token distributions, action probabilities, or ensemble votes

Supports:

- knowledge distillation
- calibration transfer
- uncertainty-aware training

Pitfalls:

- teacher uncertainty can be misread as desired ambiguity
- mismatched tokenization or action spaces can corrupt targets

## Mapping Rules

- Prefer `demonstration pair` or `instruction-response pair` for direct supervised learning.
- Prefer `chosen-rejected` when relative preference is easier to judge than absolute quality.
- Prefer `verifier result` when correctness can be checked externally.
- Prefer `process-step label` when the path matters, not only the endpoint.
- Prefer `distribution targets` or `rationale or trajectory distillation` when compressing a stronger teacher.
- Use `unlabeled corpus` mainly as pretraining, adaptation, or input for later relabeling.

## Shape Conversion Notes

- A `critique-rewrite` record can produce a `demonstration pair`, a `binary desirable-undesirable` label, or a `process-step label` if decomposed carefully.
- `chosen-rejected` data can train a reward model, but it does not become calibrated `scalar reward` without extra assumptions.
- `verifier result` can be attached to almost any other shape as an extra signal.
- `unlabeled corpus` becomes more useful when paired with teacher-generated labels, critiques, or preferences.
