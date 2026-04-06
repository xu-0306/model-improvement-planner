# Method Selection Matrix

Use this reference to pick an optimization family based on operating constraints, not research lineage.

## Quick Routing

Start with the narrowest method that can plausibly close the gap.

| Situation | Route first | Avoid as default because |
| --- | --- | --- |
| Domain knowledge is missing or stale | Continued pretraining (CPT) | Preference tuning will not add missing knowledge |
| Task format or instruction following is weak | Supervised fine-tuning (SFT) | RL-style methods add variance before the model can imitate the task |
| Outputs are mostly correct but ranking between good and better matters | Preference optimization such as DPO | More complex RL is rarely the first move |
| Success is easy to verify with executable checks or clear reward signals | Verifier-guided RL such as GRPO or related policy optimization | Plain preference tuning may plateau when reward is machine-checkable |
| A larger teacher consistently outperforms the target and teacher outputs are available | Distillation | Full RL on the small model is often higher cost for less stability |
| Storage and latency are the main constraints, with a good base model already chosen | Distill, quantize, or prune after capability work | LoRA alone does not solve deployment size or latency targets |
| Hardware is tight and adaptation must be cheap | Parameter-efficient tuning such as LoRA or adapters | Treating PEFT as a capability strategy can hide data or objective problems |

## Decision Factors

| Factor | If this is true | Prefer | Notes |
| --- | --- | --- | --- |
| Capability gap type | Missing facts, terminology, corpus style | CPT | Use when the base model lacks the domain itself |
| Capability gap type | Wrong format, weak tool use, weak instruction following | SFT | Use high-quality demonstrations before preference tuning |
| Capability gap type | Answers are reasonable but not aligned with user preferences | DPO or similar preference tuning | Best when comparing outputs is easier than writing ideal outputs |
| Capability gap type | Multi-step search, planning, or reasoning benefits from iterative reward | RL with a verifier | Only if reward can be defined and monitored |
| Supervision shape | Gold answers exist | SFT | Lowest-friction route when labels are direct |
| Supervision shape | Pairwise or ranked preferences exist | DPO / ORPO / similar | Use when relative quality is easier to label than absolute quality |
| Supervision shape | Only pass/fail or scalar reward exists | RL with a verifier | Reward quality dominates outcome quality |
| Teacher access | Strong teacher available with API or batch access | Distillation, synthetic SFT data, critique-revision loops | Teacher quality and diversity matter more than volume alone |
| Teacher access | No reliable teacher | Human-labeled SFT or verifier-based RL | Do not assume synthetic data will self-correct |
| Verifier availability | Fast, trusted verifier exists | RL or reranking with verifier support | Good fit for code, math, extraction, constrained generation |
| Verifier availability | Verifier is weak, sparse, or easy to game | SFT or DPO first | Reward hacking risk is high |
| Model size | Very small target model | Distillation, narrow-scope SFT | Small models often need stronger simplification of the task |
| Model size | Mid or large target model | SFT, DPO, RL as justified | Larger models can absorb richer objectives |
| VRAM / memory | Limited VRAM | LoRA, QLoRA, adapters, small-batch SFT | Objective choice still comes first |
| VRAM / memory | Ample VRAM and long runs are acceptable | Full fine-tuning or RL if justified | Use only when the gain warrants the cost |
| Runtime support | Training stack does not support stable RL | SFT or DPO | Do not force RL through immature tooling |
| Runtime support | Serving stack supports only merged weights | Full FT or merged adapters | Check deployment packaging early |
| Deployment target | Edge, mobile, or strict latency budget | Distill first, then compact tuning | Optimize for inference footprint and robustness |
| Deployment target | Server inference with relaxed latency | Broader set of methods is viable | Capability objective can dominate efficiency concerns |

## Default Rules

1. Route to `CPT` when the model lacks the domain, vocabulary, or corpus patterns.
2. Route to `SFT` when you can show the behavior you want with high-quality examples.
3. Route to `DPO` or another preference method when outputs are acceptable candidates and the main problem is ranking or style preference.
4. Route to `verifier-guided RL` only when success can be scored reliably, cheaply, and at scale.
5. Route to `distillation` when a stronger teacher is available and the deployment model must be smaller, cheaper, or faster.
6. Route to `PEFT` methods such as `LoRA` when compute is constrained, but pair them with the right objective family rather than treating them as the objective.
7. Prefer the simplest method that matches the signal you actually have.

## Anti-Patterns

### Overusing DPO

- Do not use DPO to compensate for missing domain knowledge. That is usually a CPT or data-quality problem.
- Do not use DPO when you have clear gold outputs and no real preference ambiguity. SFT is simpler and usually more stable.
- Do not use DPO on noisy synthetic comparisons without checking that the preference labels reflect real quality.

### Overusing GRPO or Other RL Variants

- Do not jump to RL because it sounds more capable. If the verifier is weak, slow, or gameable, RL will amplify the wrong behavior.
- Do not use RL before basic imitation quality is acceptable. Weak SFT foundations make RL unstable and expensive.
- Do not use RL when runtime, tooling, or observability cannot support reward debugging and regression checks.

### Overusing LoRA

- Do not treat LoRA as a substitute for choosing the right training objective.
- Do not assume LoRA is always enough for large behavior shifts, deep domain injection, or hard deployment constraints.
- Do not keep stacking adapters to avoid fixing bad data, weak labels, or an unsuitable base model.

## Staged Combinations

Use combinations when the problem changes across stages.

| Common sequence | Use when |
| --- | --- |
| CPT -> SFT | The model first needs domain grounding, then task behavior |
| SFT -> DPO | The model can perform the task, but needs sharper preference alignment |
| SFT -> verifier-guided RL | The task is teachable by examples and later benefits from machine-checkable reward |
| Teacher distill -> SFT | A strong teacher can bootstrap a smaller model, then task-specific examples refine it |
| CPT -> SFT -> DPO -> distill | The target needs domain knowledge, task behavior, preference alignment, and then deployment compression |

Keep the sequence evidence-driven. Add a new stage only when the current stage has likely reached its limit for the available signal.
