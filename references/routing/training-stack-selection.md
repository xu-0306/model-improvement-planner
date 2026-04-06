# Training Stack Selection

Use this reference when the capability route includes training, adapter merging, verifier-driven optimization, or runtime-dependent serving constraints.

## Goal

Choose a stack that can actually support the selected intervention family, artifact format, and deployment target.

Do not select a training objective in isolation from the implementation stack.

## Routing Questions

Answer these questions before naming a concrete stack:

- Which intervention family was selected?
- Does the route require full finetuning, PEFT, distillation, preference optimization, reward-driven optimization, or system composition?
- What model format, tokenizer format, and checkpoint layout are actually available?
- What hardware is available for training and serving?
- Does the serving target require merged weights, adapters, quantized checkpoints, or a custom runtime bridge?
- Does the route depend on verifier loops, trajectory logging, browser or tool environments, or multimodal components?

## Stack Capabilities

Treat these as representative options, not a closed list.

### Hugging Face Transformers

Good fit when:

- the route needs broad model-family support
- the project needs flexible data pipelines
- custom trainer logic or architecture inspection is required
- the project may later branch into distillation, evaluation, or adapter work

Watch for:

- uneven support across new or custom architectures
- large-memory full finetuning requirements
- serving assumptions that differ from the eventual runtime

### PEFT

Good fit when:

- the objective family is already chosen
- the project needs LoRA, QLoRA-adjacent workflows, adapters, IA3, prompt tuning, or related parameter-efficient mechanisms
- hardware is constrained and the base model is otherwise suitable

Watch for:

- treating PEFT as the objective instead of the mechanism
- target-module mismatches across model families
- serving stacks that cannot load the chosen adapter format cleanly

### TRL

Good fit when:

- the route includes preference optimization or reward-driven optimization
- the project needs DPO-family methods, reward models, PPO-style loops, or related trainer scaffolding

Watch for:

- weak or gameable evaluators
- immature support for the chosen architecture or data shape
- high operational overhead relative to a simpler supervised route

### Unsloth

Good fit when:

- the project needs a pragmatic local finetuning path with strong PEFT ergonomics
- supported model families and training modes already align with the target
- fast iteration on supervised or selected preference workflows matters more than maximum framework generality

Watch for:

- assuming support for every architecture, tokenizer layout, or training method
- assuming reward-driven or multimodal routes are equally mature
- forgetting to confirm compatibility with the final serving stack

### vLLM

Good fit when:

- the serving target needs high-throughput inference
- the project needs batched teacher generation, evaluation, or rollout serving
- the deployment path expects a production-oriented inference runtime

Watch for:

- assuming the serving runtime is also the best training stack
- adapter or quantization support mismatches
- feature gaps for custom tool, verifier, or multimodal integrations

### llama.cpp

Good fit when:

- the deployment target is edge, CPU-heavy, or strongly quantized
- the output of training must land in a compact local inference format

Watch for:

- assuming all training-side artifacts transfer cleanly to GGUF or related export paths
- choosing methods whose outputs are hard to merge or export for the target runtime
- using it as the reason to avoid a stronger upstream training stack when conversion is feasible

### Custom Local Runtimes

Good fit when:

- the host project already depends on a local runtime with custom loaders, controller logic, or serving APIs
- runtime constraints dominate the choice of artifact format

Watch for:

- undocumented feature gaps
- missing support for adapters, verifier loops, or multimodal bridges
- hidden integration cost that should push the route toward system composition or model replacement

## Stack-Aware Routing Rules

- Prefer the stack that can support the chosen intervention family with the least custom glue.
- Prefer broad, inspectable stacks when the route is still changing.
- Prefer narrower ergonomic stacks only after architectural fit and method fit are confirmed.
- Prefer serving-aware planning early when adapter merging, quantization, or export format will affect deployment.
- Prefer system composition over stack contortion when the requested capability depends on subsystems the stack does not natively support.

## Typical Route Patterns

### Supervised Learning

- broad route: `Transformers` plus `PEFT` when flexibility matters
- fast local route: `Unsloth` when the target architecture and training mode are supported
- serving follow-up: validate compatibility with `vLLM`, `llama.cpp`, or the project runtime before committing

### Distillation

- use a stack that can support both teacher generation and student training
- separate teacher serving needs from student finetuning needs when necessary
- do not assume logit or distribution distillation is practical on every local stack

### Preference Optimization

- use `TRL` or an equivalent stack only when the comparison data and evaluators are already credible
- avoid stack-heavy preference routes when the real problem is still direct imitation quality

### Reward-Driven Optimization

- require stack support for rollout logging, reward computation, observability, and failure analysis
- stop if the verifier is weak or the stack cannot surface reward-hacking signals clearly

### Multimodal or Speech Routes

- check architecture support first
- if the stack cannot support the required modality bridge, recommend model replacement or system composition before training

## Anti-Patterns

- choosing a method first and hoping the stack can be forced to support it later
- choosing a stack for popularity rather than fit
- collapsing every local run to `LoRA + one trainer`
- assuming training compatibility implies serving compatibility
- assuming a text-only stack can be stretched into multimodal or speech support without architectural evidence

## Decision Rule

Choose the stack only after these are explicit:

- intervention family
- architecture fit
- artifact format needs
- serving target
- evaluation and observability requirements

If no stack cleanly supports the selected route, prefer:

1. a different intervention family
2. system composition
3. model replacement

Do not proceed with a stack that would hide critical failure modes or make deployment impossible.
