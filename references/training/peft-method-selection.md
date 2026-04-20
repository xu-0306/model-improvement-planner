# PEFT Method Selection

Use this reference when PEFT is already chosen and the remaining question is which adapter family is the least risky fit.

## Goal

Choose the simplest PEFT mechanism that fits memory limits and deployment constraints.

## Choose When

- The base model is already close enough that a lightweight update is plausible.
- Full fine-tuning is unnecessary or too expensive.
- Adapter-based serving or merge is acceptable downstream.

Mechanism boundary:
- Use LoRA as the default baseline.
- Use QLoRA when VRAM is the main blocker.
- Consider DoRA, PiSSA, or MoRA only if a solid LoRA baseline underfits and extra complexity is justified.
- Consider IA3 or VeRA only when minimizing trainable state is more important than maximal flexibility.

## Avoid When

- The base model is missing the capability in a broader way.
- The serving path cannot host or merge the chosen adapter cleanly.
- PEFT choice is being used to avoid fixing data quality or objective mismatch.

## Require Before Proceeding

- A LoRA baseline or a concrete reason not to use one.
- Known target modules and architecture compatibility.
- A clear memory budget for training and a clear format for serving.
- Evaluation against both the untuned model and the plain LoRA baseline.

## Key Risks

- A specialized adapter hides a base-model mismatch.
- Training format and serving format diverge.
- Tooling support is weaker than expected for non-default methods.
- Apparent gains disappear when compared against a properly tuned LoRA baseline.
