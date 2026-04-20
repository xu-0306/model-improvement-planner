# Probe Generation Playbook

Use this reference when the skill must design baseline probes before route selection.

## Goal

Generate compact, capability-aware probes that separate relative strengths, weak clusters, modality mismatches, and evaluator needs.

## General Rules

- design probes before naming the optimization route
- prefer small probe batches that isolate a hypothesis
- compare relative strengths when the user asks to shift the model toward a target capability or language
- pair each probe family with an evaluation mode
- record the plan in the evaluation-first planning bundle

## Core Probe Families

### Language Localization

Use when the user wants stronger target-language behavior, terminology fidelity, or script fidelity.

Minimum coverage:

- comprehension in the likely strongest language
- response generation in the target language
- instruction following with target-language output constraints
- script fidelity or locale-sensitive style checks

For target-language improvement:

1. infer candidate strongest languages from metadata and prior evidence
2. design comparison prompts across those likely strong languages
3. require the student output in the target language when appropriate
4. score both task correctness and target-language fidelity

### Coding

Use when the target is code synthesis, repair, tool use inside coding flows, or test compliance.

Minimum coverage:

- direct code generation
- bug-fix or repair task
- execution-based or test-based check where possible
- one instruction-following case that stresses output formatting or patch discipline

### Tool Use

Use when the user wants the model to use skills, tools, or structured actions.

Minimum coverage:

- tool selection
- schema understanding
- argument formatting
- recovery from bad tool choice
- stop-or-continue judgment

Prefer execution-based or verifier-backed evaluation where possible.

### Multimodal Grounding

Use when the target depends on images, charts, diagrams, or mixed-modal inputs.

Minimum coverage:

- simple grounding
- attribute extraction
- grounding plus answer generation
- one hallucination-sensitive probe

Do not treat a text-only model as eligible without architecture evidence.

### Speech Pipeline Behavior

Use when the request mentions STT, TTS, spoken dialogue, or streaming voice interaction.

Probe the pipeline, not just the base model:

- speech recognition quality
- dialogue-state carryover
- response generation quality
- synthesis or streaming behavior

Prefer system-level probes when speech depends on external components.

## Evaluation Mode Selection

Use the narrowest mode that can detect the real failure:

- `exact-match` for small factual or extraction targets
- `rubric-based` for style, localization, or partial-credit judgments
- `teacher-review` when correction quality matters
- `execution-based` for code and tool use
- `verifier-based` when hard checks exist

## Probe Blueprint Shape

Each planned probe pattern should identify:

- `probe_family`
- `target_capability`
- `input_modality`
- `output_modality`
- `target_language` if relevant
- `expected_evaluation_mode`
- `failure_hypothesis`

These families illustrate the required probe shape. The skill is not limited to them; any capability family is valid so long as the plan stays explicit about capability, modality, evaluation mode, and failure hypothesis.

## Stop Rules

Do not lock the route yet when:

- no probes isolate the main suspected bottleneck
- no scored or judgeable outputs are available
- the probe set cannot distinguish architecture mismatch from data weakness
- the probe plan ignores the requested target language or modality
