# Capability Intake and Routing

Use this reference at the start of every run.

## Goal

Normalize arbitrary user requests into a stable decision format before choosing methods.

## Intake Fields

Capture at least:

- requested capability
- desired behavior
- unacceptable failure modes
- success criteria
- deployment target
- latency and hardware constraints
- whether the user wants diagnosis, planning, data generation, training, integration, or end-to-end execution

## Capability Decomposition

Break the request into:

- required inputs
- required outputs
- sub-capabilities
- external dependencies
- likely evaluation signals

Examples:

- text capability requests may decompose into comprehension, generation, control, terminology, or style
- coding requests may decompose into synthesis, repair, test compliance, tool use, or planning
- multimodal requests may decompose into perception, grounding, fusion, response generation, and subsystem integration
- tool-use requests may decompose into selection, schema understanding, execution control, and recovery

## Bottleneck Classes

Assign one or more bottleneck hypotheses:

- prompt/control
- data/distribution
- weak supervision
- evaluator/verifier
- objective mismatch
- runtime support
- controller/tooling
- architecture mismatch
- missing subsystem
- deployment mismatch

Do not choose a method before assigning bottleneck classes.

## Default Response Bundle

Return:

- normalized target
- decomposition summary
- bottleneck hypothesis
- confirmed facts
- missing facts
- next evaluation step
- candidate intervention family

## Stop Rules

See `references/orchestration/stop-and-confirmation-policy.md` for the full stop and confirmation policy.

Stop and emit a bounded memo here specifically when:

- the target capability is underspecified
- decomposition is incomplete
- no evaluation path exists yet
