# Serving Compatibility Guide

Use this reference when a capability route already looks feasible in training but deployment compatibility is still uncertain.

## Goal

Check whether the planned outputs can actually survive the path from training to serving.

Do not treat a successful training run as proof that the result can be packaged, loaded, monitored, and shipped in the target runtime.

## Start With Deployment Reality

Answer these questions before approving a route as release-ready:

- does the serving target expect merged weights, adapters, quantized exports, or custom wrappers
- does the runtime support the tokenizer, checkpoint format, and model family as produced by training
- does the route depend on multimodal encoders, projectors, browser controllers, or external subsystems
- does deployment require CPU, GPU, edge, mobile, or high-throughput server inference
- does the route need function calling, structured output, verifier hooks, or trajectory logging at inference time

## Compatibility Surface

Treat serving compatibility as a surface with multiple failure points:

- weight format
- adapter format
- tokenizer assets
- config fields
- quantization format
- runtime loader behavior
- subsystem interfaces
- observability hooks

Do not approve a route until the critical parts of that surface are either evidenced or explicitly marked unresolved.

## Common Decision Boundaries

### Merged weights vs adapters

Prefer merged weights when:

- the serving runtime cannot reliably load adapters
- deployment packaging must stay simple
- the release target expects one self-contained checkpoint

Prefer adapters when:

- the runtime can load them cleanly
- modular task isolation matters
- multiple variants must coexist without duplicating the full base weights

Watch for:
- adapter formats that are supported in training but not in the serving runtime
- merged checkpoints that break quantization or export assumptions
- silent drift between base model revision and adapter target revision

### Quantization and export

Quantization or export should be treated as a separate compatibility problem, not a postscript.

Check:

- whether the target runtime supports the planned quantization format
- whether merged or adapter-based outputs can be exported without losing required behavior
- whether tokenizer files, config fields, and special tokens survive export
- whether multimodal projectors, tool schemas, or controller hooks survive the packaging path

Watch for:

- training outputs that are valid upstream but cannot be exported to the deployment runtime
- quantization changing structured-output reliability or tool-call formatting
- export paths that drop multimodal or subsystem-specific metadata

If quantization or export is mandatory for deployment, validate that path early.

### Packaging and runtime loading

Serving readiness depends on more than weights.

Validate:

- checkpoint or merged weights
- adapter files if used
- tokenizer assets
- config files
- prompt or controller templates when they affect behavior
- external component definitions for composed systems

Do not let the release rely on undocumented local shell state or one developer machine layout.

### Tokenizer compatibility

Explicitly verify:

- tokenizer family
- special tokens
- chat template assumptions
- structured-output delimiters
- function-call or tool-call formatting tokens

Watch for:

- training on one tokenizer revision and serving on another
- export paths that alter token ids or template assumptions
- serving runtimes that normalize or ignore tokenizer-side chat formatting

Tokenizer mismatch can invalidate an otherwise correct training route.

### Multimodal and subsystem preservation

If the route depends on multimodal capability, confirm that the full serving path preserves:

- encoder selection
- projector or bridge configuration
- modality-specific preprocessing
- runtime interfaces for image, audio, or video inputs

Stop when:

- the serving runtime can only load the text backbone
- the multimodal bridge exists only in training code
- deployment loses the modality-specific preprocessing path

Do not describe a multimodal route as release-ready if inference preserves only the text half.

Check:

- browser or tool controller interfaces
- ASR / TTS integration points
- verifier service interfaces
- logging and observability paths
- failure fallback behavior

Watch for:

- training plans that assume tool use, but serving lacks a controller
- runtime packages that hide verifier outputs needed for safe deployment
- subsystem latency that breaks the interaction budget

If the target capability depends on multiple components, approve the serving route only after checking the whole chain.

## Release Gates

Before calling a route release-ready, confirm:

- the serving runtime can load the produced outputs
- the tokenizer and config path is stable
- merged versus adapter decisions are explicit
- quantization or export requirements are validated
- multimodal or subsystem paths survive inference packaging
- observability and fallback behavior exist for the deployed route

## Stop Rules

Stop and emit a bounded recommendation when:

- training succeeded but deployment format is still uncertain
- adapter support is ambiguous in the serving runtime
- quantization or export is required but unvalidated
- tokenizer compatibility is doubtful
- multimodal or controller paths do not survive packaging
- the serving stack cannot support the route without unstable custom glue

## Anti-Patterns

- treating training success as deployment success
- choosing adapters without checking runtime loader support
- postponing quantization or export validation until after tuning
- assuming tokenizer compatibility across runtimes
- claiming multimodal serving readiness when only the backbone can be loaded
- ignoring controller or subsystem dependencies in release planning

## Decision Rule

Mark a route as serving-compatible only when:

- output form is explicit
- runtime loading path is evidenced
- tokenizer and config compatibility are checked
- deployment constraints are respected
- multimodal, controller, or subsystem dependencies are preserved

If those conditions are not met, keep the route in planning or prototype status rather than calling it release-ready.
