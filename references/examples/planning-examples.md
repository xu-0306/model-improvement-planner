# Planning Examples

Use these examples to calibrate how the public skill should reason. Keep them planning-first: diagnose the capability gap, define the first evaluation move, choose the narrowest route, and state when to stop.

## Example 1: Prompting Or Tooling Route

### Request summary

The user has a local agent that can describe available tools in plain language, but real tool calls fail because arguments are malformed and recovery loops never converge.

### Decomposition

- tool selection
- argument/schema adherence
- controller-side execution and retry handling
- answer synthesis from tool results

### Bottleneck

The likely bottleneck is not raw world knowledge. It is either prompt/controller policy or runtime orchestration around tool calls.

### Evaluation-first move

Design an execution-based probe set with at least three slices: correct tool choice, malformed-argument recovery, and final answer grounding on returned tool output. Require traces that separate model output from controller behavior.

### Recommended route

Start with a prompting/tooling route: tighten tool descriptions, argument expectations, controller retry policy, and observability before considering training.

### Why not alternatives

- Not finetuning first: there is no evidence yet that the weights are the primary failure point.
- Not model replacement first: the failure may disappear once controller traces and recovery policy are fixed.

### Stop gate or risk

Stop escalation into training if controller-side fixes restore execution pass rate on held-out tasks. Do not continue if tool traces are missing, because controller vs model attribution will stay ambiguous.

## Example 2: Finetuning Or Distillation Route

### Request summary

The user has a local coding model that handles small edits but fails repository-grounded patch tasks that require reading project context and producing valid multi-file fixes.

### Decomposition

- repository grounding
- patch planning across files
- code edit accuracy
- regression avoidance

### Bottleneck

The base model appears structurally capable of code generation, but weak on project-grounded demonstrations and long-horizon patch behavior.

### Evaluation-first move

Build a held-out repository-grounded patch benchmark with baseline pass rate, patch validity, and regression checks. Confirm whether failures come from missing demonstrations, weak critique/rewrite behavior, or insufficient context handling.

### Recommended route

Use a narrow training-bound route only after the benchmark confirms a repeatable model-side gap. Prefer PEFT-SFT when strong demonstrations exist; prefer distillation when a stronger teacher can supply high-quality repository-grounded traces more reliably than the student can generate them.

### Why not alternatives

- Not prompt-only first if repeated failures persist on the same grounded benchmark despite better task framing.
- Not system composition first if the core issue is not missing tools but weak project-conditioned generation.
- Not DPO or RL first unless the real target is preference shaping rather than correctness on supervised patch tasks.

### Stop gate or risk

Stop if you cannot produce trustworthy grounded demonstrations or teacher traces. Stop if the training route improves toy tasks but not held-out repository-grounded patches.

## Example 3: System Composition Route

### Request summary

The user wants speech input, speech output, and dependable tool use from a local text-centric assistant.

### Decomposition

- speech recognition
- dialogue and tool planning
- tool execution and recovery
- speech synthesis
- streaming/runtime orchestration

### Bottleneck

The request spans multiple subsystems. The likely bottleneck is architecture and controller composition, not a single missing text capability inside the base model.

### Evaluation-first move

Separate the target into subsystem evaluations: ASR quality, tool-use execution pass rate, response quality after tool results, and TTS/output latency. Verify what the current stack natively supports before selecting any training family.

### Recommended route

Choose system composition: combine ASR, a text model or tool-capable controller, tool runtime, and TTS with explicit interfaces and failure handling.

### Why not alternatives

- Not plain SFT first: extra dialogue data does not add ASR or TTS subsystems.
- Not model editing first: the gap is not a narrow factual defect.
- Not full model replacement first if the existing text model is still usable as one subsystem inside the pipeline.

### Stop gate or risk

Stop if the deployment target cannot support the required subsystem chain with acceptable latency or observability. Do not promise an end-to-end model route without evidence that a single model can actually cover speech and tool execution.

## Example 4: Stop Or Model Replacement Route

### Request summary

The user asks a local text-only 7B model to directly consume 3D CAD drawings and explain form factors.

### Decomposition

- visual or geometric perception
- grounding on drawing structure
- domain explanation
- deployment compatibility for the required modality

### Bottleneck

This is an architecture mismatch. A text-only model does not have a credible native path to consume CAD drawings directly.

### Evaluation-first move

Confirm the current model and serving stack are text-only, then define the minimum evidence needed for a viable route: either a vision-capable replacement or an external perception subsystem that can transform drawings into structured evidence.

### Recommended route

Recommend stopping the current tuning path and either replacing the base model with a modality-appropriate model or reframing the solution as a perception-plus-language system composition problem.

### Why not alternatives

- Not finetuning first: supervised examples do not create a missing visual subsystem.
- Not distillation first: a student without the required modality bridge cannot absorb the target behavior in a meaningful way.
- Not prompt engineering first: prompting cannot compensate for absent perception.

### Stop gate or risk

Stop immediately if the user expects direct CAD understanding from the existing text-only checkpoint. Escalate only after confirming a viable replacement model or an explicit external perception stage.
