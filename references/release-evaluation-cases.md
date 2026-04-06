# Release Evaluation Cases

Use these cases for manual review before publishing or after meaningful workflow changes.

## Case 1: Training-Bound Code Route

User request:

- "My local coding model fixes simple bugs but still fails repository-grounded patch tasks. Decide whether I need SFT, DPO, or something else."

Expected behavior:

- normalize the target capability and failure modes
- ask for repository grounding, runtime, hardware, and evaluation facts
- define a baseline evaluation path before recommending training
- prefer a narrow training-bound route only if direct demonstrations and validation exist
- keep any bundled training-route emitter in scaffold mode rather than implying one mandatory launcher

Minimum artifacts:

- `capability-intake.json`
- `evaluation-plan.json`
- `intervention-decision.json`
- `training-plan.json` if the route continues into training

Fail this case if:

- the skill jumps straight to LoRA or DPO without bottleneck analysis
- repository grounding is ignored
- no rejected alternatives are emitted

## Case 2: Multimodal Request With Weak Native Support

User request:

- "Improve image-grounded question answering on my local text model."

Expected behavior:

- decompose the request into perception, grounding, and response generation
- check whether the current architecture already supports a credible vision bridge
- prefer system composition or model replacement when multimodal support is absent or doubtful
- refuse to present blind text-only SFT as training-ready

Minimum artifacts:

- `capability-intake.json`
- `evaluation-plan.json`
- `intervention-decision.json`
- `system-composition-plan.json` when composition is the rational route

Fail this case if:

- the skill treats a text-only backbone as naturally multimodal
- grounding checks are missing
- deployment preservation of the multimodal path is ignored

## Case 3: Runtime And Packaging Reality Check

User request:

- "I have a local checkpoint and adapter. Tell me whether my runtime can really serve the resulting route, and scaffold what is missing."

Expected behavior:

- inspect model and tokenizer facts instead of assuming support from model family alone
- separate training readiness from serving compatibility
- emit a bounded runtime scaffold when the loading path is incomplete
- validate artifacts instead of claiming release readiness

Minimum artifacts:

- `model-discovery.json`
- `local-model-profile.json` when a local checkpoint is provided
- `runtime-scaffold/` with `scaffold_manifest.json`
- validation output from `validate_contracts.py` or `validate_runtime_scaffold.py`

Fail this case if:

- training success is treated as deployment success
- adapter compatibility is assumed without runtime evidence
- unresolved packaging gaps are hidden

## Case 4: Environment-Discovery-First Execution Planning

User request:

- "Analyze my workspace, then generate the data and training scaffold that fits what is already here."

Expected behavior:

- inspect the workspace before naming one launcher path as canonical
- emit `environment-discovery.json` before the generated script plan
- generate project-local scaffold steps for collection, generation, curation, training, and evaluation
- keep bundled implementation profiles optional rather than mandatory

Minimum artifacts:

- `capability-intake.json`
- `evaluation-plan.json`
- `environment-discovery.json`
- `generated-script-plan.json`

Fail this case if:

- the skill names one bundled training profile as the only valid route before discovery
- no environment artifact is emitted
- the generated script plan omits data curation or evaluation

## Case 5: Traditional Chinese Capability Shift

User request:

- "My local model is strongest in English, but I want stronger Traditional Chinese instruction following. Decide whether I need prompt changes, SFT, or distillation."

Expected behavior:

- treat the request as a language-localization problem rather than generic text generation
- inspect model metadata, language hints, and baseline evidence before choosing a route
- compare likely stronger-language behavior against the target-language requirement
- emit a probe-generation plan that preserves the strongest-language comparison and target-language output requirement
- emit a teacher-loop plan that makes diagnosis, critique, correction, and verification explicit
- prefer bounded supervised or distillation planning only when the baseline shows a real but trainable weakness

Minimum artifacts:

- `capability-intake.json`
- `evaluation-plan.json`
- `local-model-profile.json`
- `probe-generation-plan.json`
- `probe-summary.json`
- `teacher-loop-plan.json`
- `intervention-decision.json`
- `training-plan.json` if the route continues into training

Fail this case if:

- the skill assumes the strongest language without evidence
- target-language fidelity is not evaluated separately from task correctness
- the teacher loop is described vaguely as "use a teacher model" without explicit roles
- the route jumps to LoRA or full SFT without explaining why prompting or bounded critique-rewrite is insufficient

## Case 6: Tool-Use Recovery And Controller Diagnosis

User request:

- "My local model can answer tool questions in plain text but still fails when it has to choose a tool, format arguments, and recover from bad tool choices."

Expected behavior:

- decompose the request into tool selection, schema understanding, execution control, and recovery
- prefer execution-based or verifier-backed probes instead of only free-form rubric evaluation
- keep the route open between prompt/control, controller/runtime changes, and training, rather than assuming a tuning route
- if training is still justified, emit a probe-generation plan and teacher-loop plan that preserve tool traces and recovery supervision

Minimum artifacts:

- `capability-intake.json`
- `evaluation-plan.json`
- `probe-generation-plan.json`
- `probe-summary.json`
- `intervention-decision.json`
- `teacher-loop-plan.json`
- `training-plan.json` only if a training-bound route is justified

Fail this case if:

- the skill treats tool use as generic text generation
- no execution-based or verifier-style evaluation is proposed
- recovery behavior is ignored
- the route skips over controller or runtime deficiencies and jumps straight to fine-tuning

## Case 7: Speech Request That Really Requires System Composition

User request:

- "I want to talk to my local model with speech input and speech output."

Expected behavior:

- decompose the request into ASR, dialogue state, response generation, TTS, and streaming/runtime orchestration
- check whether the current base model is actually speech-capable or whether the real route is subsystem composition
- research or inspect current runtime support before claiming the route is training-ready
- prefer system composition or model replacement when the architecture is not natively suited to speech I/O

Minimum artifacts:

- `capability-intake.json`
- `evaluation-plan.json`
- `research-evidence.json` when live stack facts matter
- `intervention-decision.json`
- `system-composition-plan.json` when composition is the rational route

Fail this case if:

- the skill treats a text-only base model as naturally capable of STT or TTS
- speech is reduced to "train on more dialogue data"
- the need for external subsystems is hidden

## Phase 4 Regression Coverage

### Case 8 (Phase 4): Traditional Chinese localization with strongest-language comparison

User request:

- "My model answers best in English; now I must lock in fluent Traditional Chinese follow-up without regressing correctness."

Expected behavior:

- confirm the strongest language empirically before targeting zh-Hant, and capture that comparison in `probe-generation-plan.json`.
- ensure `teacher-loop-plan.json` enumerates diagnostician, critique/correction, and verifier stages that enforce the target-language fidelity constraint.
- keep training and script generation conditional on the observed gap rather than assuming Traditional Chinese weakness.

Minimum artifacts:

- `capability-intake.json`
- `probe-generation-plan.json`
- `probe-summary.json`
- `teacher-loop-plan.json`
- `intervention-decision.json`

Fail this case if:

- there is no strongest-language comparison recorded before issuing Traditional Chinese probes.
- the plans omit the target-language fidelity checks or explicit teacher roles.
- the route defaults to training without justifying why prompting or runtime control changes were insufficient.

### Case 9 (Phase 4): Speech + tool-use + system composition

User request:

- "I need speech input/output, dependable tool selection, and recovery when tool calls break in my local controller."

Expected behavior:

- decompose the capability into ASR, tool controller, and TTS/recovery traces before committing to a route, and document each stage in `probe-generation-plan.json`.
- emit a `teacher-loop-plan.json` that records execution-based critiques/verifiers, channels recovery feedback, and keeps tool/system observability explicit.
- prefer system composition (ASR + controller + optional TTS) when the base model lacks native multimodal skills; treat training as a contingent fallback.

Minimum artifacts:

- `capability-intake.json`
- `probe-generation-plan.json`
- `probe-summary.json`
- `teacher-loop-plan.json`
- `intervention-decision.json`
- `system-composition-plan.json`

Fail this case if:

- the speech or tool requirements are glossed as generic text tuning.
- the teacher loop lacks execution-focused verifier or recovery signals.
- system composition is hidden behind unverifiable fine-tuning claims.
