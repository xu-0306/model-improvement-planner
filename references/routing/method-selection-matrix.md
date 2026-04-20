# Method Selection Matrix

Use this reference after the bottleneck is clear enough to choose a route first.

## Route-First Matrix

| Observed bottleneck | Route first | Do not jump to | Stop gate |
| --- | --- | --- | --- |
| The model lacks domain facts, terminology, or corpus style | `continued_pretraining` | `DPO`, `RL`, or `LoRA` as a substitute for missing knowledge | Stop if the real failure is task behavior, not missing domain content |
| The model must learn new material without losing older capabilities across repeated updates | `continual_learning` | Plain next-stage finetuning | Stop if retention is required but no retention eval exists |
| The task behavior is weak, but good demonstrations are available | `SFT` | Preference or RL methods before imitation works | Stop if examples are too noisy or inconsistent to teach the task |
| Retrieval is already part of deployment, but the model ignores evidence or gets distracted by context | `rag_tuning` | More retrieval plumbing when retrieval quality is already acceptable | Stop if retrieval recall or document quality is still the main failure |
| Outputs are usually plausible, and the main problem is ranking good vs. better | `preference_optimization` | CPT or RL by default | Stop if comparisons are low-trust or preference labels do not reflect real quality |
| Success is machine-checkable with a credible verifier or reward | `verifier_guided_rl` | Preference tuning when reward is the real source of signal | Stop if reward is easy to game, slow, or poorly observed |
| A stronger teacher reliably outperforms the target and transfer to a smaller or cheaper model matters | `distillation` | RL on the weaker student without first using the teacher | Stop if teacher quality, coverage, or transfer format is unclear |
| The required change is narrow and collateral drift must stay small | `model_editing` | Broad retraining for a bounded patch | Stop if locality and drawdown cannot be measured |
| Compatible adapted checkpoints already exist and avoiding new training is the point | `model_merging` | Fresh training or naive averaging without compatibility checks | Stop if architecture, tokenizer, or task framing differ |
| The capability needs external tools, modality bridges, or controller logic the model does not natively have | `system_composition` or `model_replacement` | Forcing a text-only or unsupported stack to "learn it anyway" | Stop if the route assumes unsupported architecture or modality support |

## Decision Rules

- Choose the simplest route that matches the signal you actually have.
- `PEFT` is an implementation choice, not the route. Decide the objective family first.
- Prefer `SFT` before preference or RL when the model still cannot imitate the task.
- Prefer `system_composition` or `model_replacement` when the blocker is architectural, not data or objective choice.
- Escalate to `explicit_deferral` when key facts are missing and the route would otherwise be guesswork.

## Anti-Patterns

- Using `DPO` or `RL` to compensate for missing domain knowledge. That is usually a CPT or data problem.
- Treating `LoRA` as the answer when the real question is objective choice, model fit, or data quality.
- Calling repeated finetuning "continual learning" without retention evaluation.
- Using `model_editing` for broad behavior change, domain acquisition, or large policy rewrites.
- Treating `self_play` as self-validating. If evaluator quality is weak, the loop is not trustworthy.
- Using `model_merging` to avoid compatibility checks or regression measurement.

## When Routes Combine

Use staged routes only when each stage solves a different bottleneck.

| Sequence | Use when |
| --- | --- |
| `CPT -> SFT` | Domain knowledge is missing first, then task behavior must be taught |
| `SFT -> preference_optimization` | The model can do the task, but ranking or style still lags |
| `SFT -> verifier_guided_rl` | Examples establish the behavior, then machine-checkable reward sharpens it |
| `retrieval pipeline -> rag_tuning` | Retrieval exists, but grounding under retrieved evidence is still weak |
| `teacher distill -> SFT` | A strong teacher bootstraps the student, then task-specific data tightens behavior |
| `SFT -> model_editing` | Broad behavior is acceptable, but a few bounded patches remain |

Add a stage only when the current stage has likely reached its limit for the available signal.
