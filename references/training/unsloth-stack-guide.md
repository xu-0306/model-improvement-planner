# Unsloth Stack Guide

Use this reference when the selected route may be implemented with `Unsloth` and the skill needs a stack-specific fit check before committing to training.

## Goal

Decide whether `Unsloth` is an appropriate execution stack for the chosen capability route, model family, hardware profile, and serving target.

Treat `Unsloth` as a practical stack option, not as a justification for the route itself.

## Start With Method Fit

Before naming `Unsloth`, confirm:

- the intervention family is already chosen
- the base model is otherwise suitable for the target capability
- the planned supervision shape can be expressed in the intended trainer path
- the serving target can consume the resulting artifacts

Do not let stack convenience replace objective selection.

## Good Fit

`Unsloth` is often a good fit when:

- the route is supervised finetuning or instruction tuning on a supported local model family
- the project needs pragmatic local iteration with parameter-efficient tuning
- the hardware budget is constrained and a PEFT-first route is already justified
- the workflow values quick turnaround more than maximum framework breadth
- the project needs a direct local path for adapter-style experiments before broader infrastructure is introduced

## Caution Zones

Use extra caution when:

- the model family or tokenizer layout is unusual, newly added, or custom
- the route depends on preference optimization or reward-driven methods that may be less mature than the supervised path
- the target requires multimodal or speech-native support
- the training plan assumes custom trainer behavior, unusual loss wiring, or nonstandard data flow
- the final serving path depends on adapter merging, quantized export, or runtime-specific packaging

## Poor Fit

`Unsloth` is usually a poor default when:

- the route needs broad architecture flexibility or custom model internals
- the project depends on reward-driven optimization with strong observability requirements
- the target capability is fundamentally system-level rather than model-level
- the route depends on multimodal bridges, speech subsystems, browser environments, or complex external verifier loops
- the serving target requires an artifact format that the planned workflow cannot export cleanly

In those cases, prefer a broader or more inspectable stack, or recommend system composition or model replacement.

## Model-Family and Method-Fit Checks

Confirm all of the following before committing:

- the target model family is supported in practice, not just assumed to be similar to a supported one
- the checkpoint format and tokenizer layout match the expected training path
- the selected intervention family is compatible with the available trainer support
- the planned PEFT mechanism is supported for the target architecture
- the resulting artifacts can be loaded or exported for the intended serving runtime

Do not infer support from brand names, neighboring architectures, or community habit alone.

## PEFT and Supervised Boundaries

`Unsloth` is most natural when:

- the route is supervised learning
- the project already chose a PEFT mechanism such as LoRA-family adaptation
- the expected gain can plausibly come from the planned supervision signal

Do not use `Unsloth` as the reason to choose PEFT.

The correct sequence is:

1. choose the intervention family
2. confirm the supervision shape
3. confirm the base model is suitable
4. only then choose `Unsloth` if it is a good execution path

## Preference and Reward Boundaries

If the route includes preference optimization:

- confirm the required trainer path is supported for the target model family
- confirm the comparison data is already credible
- confirm the evaluation path can detect regressions

If the route includes reward-driven optimization:

- prefer stronger observability and debugging stacks unless `Unsloth` support is concrete and sufficient
- stop when reward hacking, rollout visibility, or verifier integration would be hard to inspect

Do not assume the supervised path and the reward-driven path are equally mature.

## Serving and Export Implications

Before training, confirm:

- whether the target serving runtime expects adapters, merged weights, or exported checkpoints
- whether quantization or export will change serving compatibility
- whether the downstream runtime can load the resulting artifacts without hidden conversion work
- whether inference latency or memory budgets still hold after the planned adaptation

Serving compatibility must be checked explicitly against:

- `vLLM`
- `llama.cpp`
- custom local runtimes
- any adapter-loading production path

## Common Failure Modes

Watch for:

- choosing `Unsloth` because it is familiar rather than because it fits the route
- treating partial architecture similarity as proof of support
- forcing preference or reward routes into a stack better suited to straightforward supervised tuning
- discovering only after training that the serving target cannot consume the artifacts cleanly
- hiding model mismatch behind a PEFT experiment that was never likely to close the capability gap

## Gating Checks

Before a release-ready recommendation, confirm:

- intervention family fit
- model-family fit
- tokenizer and checkpoint fit
- trainer-path fit
- serving compatibility
- rollback path if the quick local route fails

## Stop Rules

Stop and choose a different route or stack when:

- support for the target architecture is unconfirmed
- the route depends on multimodal or speech support beyond the stack's practical scope
- reward-driven or verifier-heavy training would lack sufficient observability
- serving compatibility is unclear or contradicted
- the base model itself is a poor fit and stack convenience is the only reason to continue

## Anti-Patterns

- starting with `Unsloth` and back-solving the method around it
- assuming any PEFT-capable path is enough for a severe capability gap
- using stack ergonomics to avoid comparing system composition or model replacement
- choosing a quick local run when the real issue is evaluator weakness or architecture mismatch

## Decision Rule

Choose `Unsloth` when:

- the route is already method-fit
- the model family and artifact path are supported
- the supervision path is straightforward
- the serving target is compatible
- fast local iteration is genuinely valuable

If any of those fail, prefer:

1. a broader stack
2. a different intervention family
3. system composition
4. model replacement
