# Training Stack Selection

Use this reference only after the intervention family is chosen and the route actually requires implementation work.

## Decision Order

Make these explicit before naming a stack:

1. intervention family
2. model architecture and checkpoint format
3. target output form: full weights, adapter, merged weights, quantized export, or serving wrapper
4. deployment target: local, server, edge, or custom runtime
5. evaluation and observability needs

If any item is still unknown, stop and resolve that first.

## Stack-Fit Matrix

| Stack shape | Good fit when | Poor fit when | Stop gate |
| --- | --- | --- | --- |
| General training framework (`Transformers` + `PEFT`-style components) | The route may change, architecture inspection matters, or you need a flexible baseline for SFT, distillation, or adapter work | You only chose it because it is familiar, not because it fits the model and output path | Stop if the architecture or checkpoint is not actually supported |
| Ergonomic local PEFT stack (`Unsloth`-like) | The model family is supported, the route is mostly supervised or lightweight preference work, and fast local iteration matters | You need broad method coverage, unusual architectures, or research-heavy objectives | Stop if support for the exact model, tokenizer, or training mode is unclear |
| Preference or RL trainer (`TRL`-like) | The route already needs comparison training or verifier-driven optimization, and the supervision signal is credible | The task still needs basic imitation learning or reward quality is weak | Stop if the stack cannot surface reward failures, logging, and regressions clearly |
| Research or task-specific codebase | The route depends on model editing, advanced merging, self-play, or custom update logic not cleanly exposed in generic trainers | You are using research code to avoid a simpler supported route | Stop if the code path is not reproducible enough for the intended use |
| Serving-first runtime (`vLLM`-like) | You need teacher generation, batched evaluation, or production inference throughput | You are confusing the serving runtime with the training stack | Stop if the serving runtime cannot load the required output form |
| Edge or export-oriented runtime (`llama.cpp`-like) | Deployment needs compact local inference or a strict export format such as GGUF | The training route depends on outputs that do not export cleanly | Stop if export becomes the reason to pick a worse upstream training route |
| Project-local or custom runtime | The host project already constrains loader, adapter, or packaging choices | The runtime is undocumented and would force unstable custom glue into the route | Stop if runtime fit cannot be evidenced before training |

## Route-to-Stack Rules

- `SFT`, `distillation`, and most adapter work usually start in a general training framework unless a narrower stack is already proven to fit.
- Ergonomic local PEFT stacks are good for supported-model iteration, not for every family by default.
- `preference_optimization` and `verifier_guided_rl` require stack support for comparisons, rollout logging, reward computation, and regression review.
- `model_editing`, `model_merging`, and `self_play` often need research-grade code. Treat execution readiness as unproven until the exact method support is evidenced.
- `rag_tuning` needs explicit handling of retrieved context, negatives, and grounding evaluation. Do not assume plain SFT plumbing already does that.
- `continual_learning` needs replay, retention tracking, or teacher-retention support. Plain stage-two finetuning is not enough.
- Serving and training can use different stacks. Separate "how to train" from "how to serve".

## Typical Situations

| Situation | Stack fit |
| --- | --- |
| Supported open-weight model, limited VRAM, behavior-teaching problem | Ergonomic local PEFT stack or general framework with adapters |
| Route still uncertain, model support unclear, or evaluation needs custom hooks | General training framework first |
| Pairwise comparisons are ready and the model already imitates reasonably well | Preference or RL trainer |
| Need batched teacher generation for distillation or large eval runs | Serving-first runtime for generation plus a separate training stack |
| Target deployment is GGUF or CPU-heavy local inference | Train in a supported upstream stack, then export to an edge runtime |
| Method depends on editing, merging, or self-play papers | Research or task-specific codebase, with bounded claims only |

## Anti-Patterns

- Choosing a stack first and then bending the method to fit it.
- Collapsing every route to `LoRA + one trainer`.
- Assuming training compatibility implies serving compatibility.
- Forcing a text-only stack into multimodal or speech work without architectural evidence.
- Accepting unstable custom glue when `system_composition` or `model_replacement` is the cleaner answer.

## Escalation Rule

If no stack cleanly supports the selected route, prefer in this order:

1. change the intervention family
2. use system composition
3. replace the model
4. defer until missing support is evidenced
