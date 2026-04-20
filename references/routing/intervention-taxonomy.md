# Intervention Taxonomy

Use this reference to classify the intervention family before choosing a concrete method or stack.

## Decision Rule

Pick the narrowest family that can plausibly close the gap.
Do not treat `LoRA`, a trainer, or a serving runtime as the family decision.

## Families

| Family | Choose when | Do not choose when | Stop gate |
| --- | --- | --- | --- |
| Prompt and control | The base model is mostly capable and failures look like instruction, decomposition, or output-shape issues | The model lacks task knowledge or cannot perform even with good scaffolding | Stop if better prompting does not move held-out evals |
| Retrieval and context construction | The missing piece is external knowledge access or better context selection at inference time | The real problem is weak use of already-retrieved evidence | Stop if retrieval quality itself is still unresolved |
| Data-centric improvement | The task is right but labels, coverage, difficulty mix, or formatting are poor | The base model or route is fundamentally wrong for the capability | Stop if you cannot show that data quality is the bottleneck |
| Continued pretraining | The model lacks domain knowledge, vocabulary, or corpus style | The request is mainly behavior shaping or a narrow correction | Stop if the gap is task behavior rather than missing domain content |
| Supervised finetuning | You can show the target behavior with good demonstrations | The task depends mostly on ranking, reward search, or external subsystems | Stop if gold examples are weak, inconsistent, or too sparse |
| RAG-tuning | Retrieval is part of deployment and the model mishandles evidence, grounding, or distractors | Retrieval is not part of the real task, or retrieval quality is still the main failure | Stop if you are still debugging the retrieval pipeline itself |
| Distillation | A stronger teacher is available and the target must inherit behavior more cheaply or in a smaller model | There is no credible teacher advantage or the teacher output is too noisy | Stop if teacher quality, coverage, or transfer target is unclear |
| Preference optimization | Outputs are often acceptable but ranking good vs. better matters more than writing ideal answers | Direct demonstrations are easier and less ambiguous | Stop if preference labels are noisy or synthetic comparisons are not trusted |
| Reward-driven optimization | Success can be scored reliably with a verifier or reward signal | Reward is sparse, slow, weak, or gameable | Stop if you cannot monitor reward hacking and regressions |
| Continual learning | Updates are sequential and preserving prior capability is a hard requirement | A one-off finetune is enough and retention is not critical | Stop if there is no retention evaluation or replay/distillation plan |
| Model editing | The requested change is narrow, bounded, and locality matters | The goal is broad capability gain or domain adaptation | Stop if locality and collateral-damage checks are unavailable |
| Model merging | Compatible checkpoints already exist and avoiding another training run is valuable | Compatibility is unknown or the merge is being used to dodge evaluation | Stop if architecture, tokenizer, or task assumptions diverge |
| Self-play and self-improvement loops | A strong evaluator already exists and iterative generation is part of the method | The model is being asked to grade or bootstrap itself without reliable external checks | Stop if collapse, bias amplification, or judge leakage cannot be measured |
| Runtime and serving adaptation | The model is good enough, but loader, tokenizer, quantization, latency, or packaging constraints block deployment | The main gap is still capability, not deployment fit | Stop if deployment requirements imply a different family or different model |
| System composition | The capability depends on external tools or subsystems the model does not natively support | The missing piece can be solved inside the model with a narrower route | Stop if the plan relies on unsupported modality or tool assumptions |
| Model replacement | The current base model is a poor fit for the modality, scale, or domain | A narrower intervention is still plausible and cheaper | Stop if replacement is being used to avoid basic diagnosis |
| Explicit deferral | Key facts are missing and any route choice would be guesswork | Enough evidence already exists to commit to a narrower route | Stop if the missing facts can be gathered cheaply now |

## Scope Boundary

- `intervention-taxonomy.md` answers "which family?"
- `method-selection-matrix.md` answers "which route first under this evidence?"
- `training-stack-selection.md` answers "which implementation stack can actually support that route?"
