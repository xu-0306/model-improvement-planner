# Speech and Audio Playbook

Use this reference when the requested capability involves speech-to-text, text-to-speech, spoken dialogue, audio understanding, or streaming voice interaction.

## Goal

Route speech and audio requests without collapsing them into ordinary text-model finetuning, and design evaluation against the full system boundary when speech IO is part of the task.

## Start With System Boundaries

Clarify:

- whether the target is ASR, TTS, speech dialogue, audio grounding, or a composed loop
- whether the base model is text-only or audio-capable
- whether the route is model finetuning, subsystem composition, or model replacement
- whether the target is offline, streaming, or real-time interaction

Break the request into components such as:

- speech capture
- speech-to-text
- dialogue or reasoning
- text-to-speech
- turn-taking
- streaming orchestration
- interruption handling
- latency control

If the task is a dialogue loop, evaluate the loop, not only one component.

## Architecture-Fit Check

Ask these questions first:

- is audio understanding actually required, or only transcript-based dialogue
- is low-latency streaming required
- would composition with external ASR and TTS systems satisfy the request
- does the current stack support audio-native processing if direct audio reasoning is required

If the base model is text-only, prefer system composition with ASR and TTS before recommending language-model finetuning.

## Common Route Patterns

Representative route patterns:

- transcript-based voice assistants built as ASR + LLM + TTS composition
- audio understanding tasks that require direct reasoning over audio properties
- low-latency spoken dialogue with explicit turn-taking and fallback behavior
- speech-conditioned assistants where downstream tool use or task success matters

Do not present text-only tuning as a substitute for missing ASR or TTS components.

## Evaluation Targets and Forms

Potential targets include:

- transcription quality
- speech intelligibility
- dialogue coherence
- grounding to audio events
- robustness to noise, accents, or channel variation
- latency and turn-taking behavior
- interruption and recovery behavior
- end-to-end user task success

Use the strongest available evaluators:

- transcription metrics for ASR-style tasks
- intelligibility and naturalness review for TTS-style tasks
- latency and interruption metrics for streaming systems
- system-level task success for dialogue loops
- verifier-backed checks for tool-coupled or structured downstream tasks
- human review when naturalness or conversational timing matters

If the system includes ASR and TTS, evaluate both component quality and end-to-end interaction quality.

## Data Shapes and Teacher Roles

Useful shapes include:

- speech-text pairs for ASR
- text-audio pairs for TTS
- dialogue turn records with timing metadata
- critique-rewrite records for transcription or response correction
- verifier outcomes tied to downstream task success
- trajectory records for multi-turn spoken workflows

Useful roles include:

- `diagnostician` for component-boundary and latency analysis
- `demonstrator` for target transcripts, responses, or spoken outputs
- `critique teacher` for error correction and dialogue repair
- `verifier` for downstream task success, formatting, or tool-coupled checks
- `runtime researcher` when stack support, streaming capability, or component selection is unclear

Preserve timing, channel, and modality metadata when those details affect behavior.

## Streaming and Deployment Checks

When the system is interactive, evaluate:

- first-token or first-audio latency
- end-of-turn detection behavior
- interruption and overlap handling
- recovery after ASR uncertainty
- consistency of transcript-to-response handoff
- TTS completion time relative to the interaction budget

Streaming requirements can invalidate otherwise reasonable offline methods.

## Composition Versus Finetuning

Prefer composition or replacement when:

- the base model is text-only and the target requires speech IO
- ASR or TTS quality dominates the user experience
- the main bottleneck is streaming latency or audio subsystem quality
- the current stack does not support audio-native processing

Tune the text model only for the parts that are truly text-model bottlenecks, such as dialogue behavior or concise spoken response style.

## Gating Checks

Before training:

- confirm whether the target is system-level or model-level
- confirm evaluation for latency and interaction quality
- confirm that dataset shape preserves timing or modality cues when needed
- confirm the deployment path can support the selected components
- confirm whether the real route is composition rather than tuning

## Stop Rules

Stop and emit a bounded recommendation when:

- speech IO depends on subsystems that are not yet chosen
- only text metrics are available for an audio or dialogue target
- latency requirements would dominate the route but are unmeasured
- the correct recommendation is system composition or model replacement

## Anti-Patterns

- treating speech tasks as plain text finetuning
- evaluating only transcript quality for full dialogue systems
- ignoring streaming latency and turn-taking
- treating one clean-channel result as proof of robust speech capability
- recommending RL or complex optimization before the base speech pipeline is reliable

## Decision Rule

For speech and audio requests:

1. decompose the pipeline and system boundary first
2. check whether composition solves the problem before tuning
3. choose end-to-end evaluation before route selection
4. optimize the text model only for the parts that are genuinely text-model bottlenecks
