# Example Runs

Load this reference only when you need concrete command patterns for packaging, release hardening, or debugging the canonical entrypoints.

## Example 1: Bootstrap a Planning Bundle

Use this when the request is still in diagnosis or planning mode and you need the minimum intake plus evaluation artifacts first.

```bash
python3 scripts/artifact_cli.py bundle bootstrap \
  --output-dir artifacts/model-improvement-planner/chart-qa \
  --target-capability "image-grounded chart question answering" \
  --user-intent planning \
  --deployment-context '{"runtime":"local-api","surface":"batch"}' \
  --constraints '{"gpu":"1x24GB","latency_budget_ms":1500}' \
  --desired-outcome "Answer chart questions without hallucinated entities" \
  --failure-mode "Invents values not present in the image" \
  --success-criterion "Held-out exact match >= 0.85" \
  --input-modality image \
  --output-modality text \
  --sub-capability chart-reading \
  --sub-capability grounded-answer-generation \
  --primary-evaluation-mode exact-match \
  --baseline-probe "chart title extraction" \
  --heldout-evaluation "heldout chart benchmark slice" \
  --success-metric "exact match >= 0.85" \
  --acceptance-criterion "No unsupported references in heldout answers" \
  --regression-check "Text-only QA baseline remains stable" \
  --stop-condition "Stop if grounding accuracy stays below 0.70 after route trial"
```

Expected outputs:

- `capability-intake.json`
- `evaluation-plan.json`

## Example 2: Add Evidence Before Choosing a Route

Use this when route choice depends on real model facts or baseline probes.

```bash
python3 scripts/local_model_profile.py \
  --model-path /models/local-vlm \
  --output artifacts/model-improvement-planner/chart-qa/model-profile.json \
  --model-id local-vlm \
  --serving-stack vllm \
  --training-stack transformers \
  --capability-hint multimodal-grounding

python3 scripts/run_capability_probes.py \
  --probe-specs scratch/probe-specs.jsonl \
  --responses-jsonl scratch/probe-responses.jsonl \
  --results-output artifacts/model-improvement-planner/chart-qa/probe-results.jsonl \
  --summary-output artifacts/model-improvement-planner/chart-qa/probe-summary.json \
  --model-profile artifacts/model-improvement-planner/chart-qa/model-profile.json
```

Validate the intermediate artifacts:

```bash
python3 scripts/validate_contracts.py \
  --artifact artifacts/model-improvement-planner/chart-qa/model-profile.json \
  --contract local-model-profile

python3 scripts/validate_contracts.py \
  --artifact artifacts/model-improvement-planner/chart-qa/probe-summary.json \
  --contract probe-summary
```

## Example 3: Discover The Active Environment And Emit Project-Local Scaffolds

Use this when the skill should analyze the current workspace before generating data or training scripts.

```bash
python3 scripts/discover_environment.py \
  --workspace-root . \
  --output artifacts/model-improvement-planner/chart-qa/environment-discovery.json

python3 scripts/emit_generated_script_plan.py \
  --capability-intake artifacts/model-improvement-planner/chart-qa/capability-intake.json \
  --evaluation-plan artifacts/model-improvement-planner/chart-qa/evaluation-plan.json \
  --environment-discovery artifacts/model-improvement-planner/chart-qa/environment-discovery.json \
  --training-plan artifacts/model-improvement-planner/chart-qa/training-plan.json \
  --output artifacts/model-improvement-planner/chart-qa/generated-script-plan.json \
  --script-dir artifacts/model-improvement-planner/chart-qa/generated
```

## Example 4: Emit and Validate a Route

Choose one normalized route family at a time. Optional bundled implementation profiles are callable helpers, not mandatory stack selections.

### Training-bound route

```bash
python3 scripts/artifact_cli.py bundle training-route \
  --decision-output artifacts/model-improvement-planner/chart-qa/intervention-decision.json \
  --training-output artifacts/model-improvement-planner/chart-qa/training-plan.json \
  --target-capability "image-grounded chart question answering" \
  --chosen-intervention-family supervised_learning \
  --implementation-direction "multimodal SFT with grounded chart examples" \
  --decision-status continue \
  --decision-summary "The stack already preserves the multimodal bridge." \
  --stop-or-continue-reason "Baseline probes show recoverable grounding failures rather than architecture absence." \
  --problem-type data_distribution \
  --decision-rejected-alternative model_replacement \
  --training-intervention-family supervised_learning \
  --supervision-shape multimodal_instruction_response \
  --base-model-suitability-verdict suitable_with_grounded_data \
  --training-stack-suitability-verdict suitable_on_existing_stack \
  --teacher-plan '{"teacher_role":"demonstrator","source":"stronger VLM"}' \
  --data-plan '{"dataset_strategy":"grounded chart QA","source":"curated internal charts"}' \
  --evaluation-plan '{"reference_artifact":"evaluation-plan.json"}' \
  --stop-criterion "Stop if held-out exact match does not improve by 0.10" \
  --rollback-criterion "Rollback if text-only regression suite fails"

python3 scripts/emit_training_route.py \
  --training-plan artifacts/model-improvement-planner/chart-qa/training-plan.json \
  --route-family sft \
  --implementation-profile unsloth-sft \
  --output-dir artifacts/model-improvement-planner/chart-qa/training-route \
  --dataset-path artifacts/model-improvement-planner/chart-qa/dataset-records.jsonl \
  --base-model /models/local-vlm
```

### System-composition route

```bash
python3 scripts/artifact_cli.py bundle system-route \
  --decision-output artifacts/model-improvement-planner/chart-qa/system-decision.json \
  --system-output artifacts/model-improvement-planner/chart-qa/system-composition-plan.json \
  --target-capability "image-grounded chart question answering" \
  --chosen-intervention-family system_composition \
  --implementation-direction "external OCR and detector plus text model orchestration" \
  --decision-status continue \
  --decision-summary "Grounding is more rational with an external perception stage." \
  --stop-or-continue-reason "Native multimodal support is insufficient for reliable chart grounding." \
  --problem-type architecture_mismatch \
  --decision-rejected-alternative generic_sft \
  --system-goal "Compose OCR, chart parsing, and response generation into one bounded workflow." \
  --architecture-summary "Vision subsystem extracts structured evidence before answer generation." \
  --orchestration-summary "Controller passes extracted entities into a constrained answer template." \
  --evaluation-plan '{"reference_artifact":"evaluation-plan.json"}' \
  --component '{"name":"ocr","role":"extract text from chart"}' \
  --component '{"name":"vlm","role":"answer from extracted evidence"}' \
  --interface '{"from":"ocr","to":"vlm","payload":"structured chart evidence"}' \
  --failure-handling "Fallback to abstain when OCR confidence is low" \
  --observability-requirement "Log extracted evidence and final answer together"
```

Run the bundled release check when preparing to publish or hand off the skill:

```bash
python3 scripts/smoke_test.py
```

## Example 5: Traditional Chinese Localization Planning

Use this when the user wants the model to stay task-capable while shifting output quality toward Traditional Chinese.

This is a target-specific example. `--target-language zh-Hant` is only appropriate when the optimization goal is Traditional Chinese output; it is not a general default for other users.

```bash
python3 scripts/artifact_cli.py bundle bootstrap \
  --output-dir artifacts/model-improvement-planner/zh-hant-localization \
  --target-capability "Traditional Chinese instruction following" \
  --user-intent planning \
  --deployment-context '{"runtime":"local-chat","surface":"interactive"}' \
  --constraints '{"gpu":"1x24GB","latency_budget_ms":1200}' \
  --desired-outcome "Respond fluently in Traditional Chinese while preserving task correctness" \
  --failure-mode "Falls back to English or Simplified Chinese" \
  --success-criterion "Held-out target-language fidelity and task correctness both improve" \
  --input-modality text \
  --output-modality text \
  --sub-capability cross-language-transfer \
  --sub-capability script-fidelity \
  --sub-capability instruction-following \
  --primary-evaluation-mode teacher-review \
  --baseline-probe "strong-language prompt with Traditional Chinese answer requirement" \
  --heldout-evaluation "zh-Hant regression split" \
  --success-metric "teacher-review score >= 0.80" \
  --acceptance-criterion "Responses stay in Traditional Chinese without obvious script drift"

python3 scripts/local_model_profile.py \
  --model-path /models/local-text-model \
  --output artifacts/model-improvement-planner/zh-hant-localization/model-profile.json \
  --model-id local-text-model \
  --serving-stack vllm \
  --training-stack transformers \
  --language-hint en

python3 scripts/emit_probe_generation_plan.py \
  --capability-intake artifacts/model-improvement-planner/zh-hant-localization/capability-intake.json \
  --evaluation-plan artifacts/model-improvement-planner/zh-hant-localization/evaluation-plan.json \
  --model-profile artifacts/model-improvement-planner/zh-hant-localization/model-profile.json \
  --output artifacts/model-improvement-planner/zh-hant-localization/probe-generation-plan.json \
  --target-language zh-Hant

python3 scripts/emit_teacher_loop_plan.py \
  --capability-intake artifacts/model-improvement-planner/zh-hant-localization/capability-intake.json \
  --evaluation-plan artifacts/model-improvement-planner/zh-hant-localization/evaluation-plan.json \
  --probe-summary artifacts/model-improvement-planner/zh-hant-localization/probe-summary.json \
  --training-plan artifacts/model-improvement-planner/zh-hant-localization/training-plan.json \
  --output artifacts/model-improvement-planner/zh-hant-localization/teacher-loop-plan.json
```

Use this pattern when you need strongest-language comparison, target-language output constraints, and explicit teacher roles before route selection.

## Example 6: Tool-Use Diagnosis Before Training

Use this when the model can talk about tools but still fails on real selection and recovery behavior.

```bash
python3 scripts/artifact_cli.py bundle bootstrap \
  --output-dir artifacts/model-improvement-planner/tool-use-routing \
  --target-capability "tool-use recovery and schema adherence" \
  --user-intent planning \
  --deployment-context '{"runtime":"local-agent","surface":"tool-execution"}' \
  --constraints '{"gpu":"1x16GB","latency_budget_ms":1500}' \
  --desired-outcome "Select the right tool, format arguments correctly, and recover from bad choices" \
  --failure-mode "Chooses the wrong tool or emits invalid arguments" \
  --success-criterion "Execution-based pass rate improves on held-out tool tasks" \
  --input-modality text \
  --output-modality tool_call \
  --sub-capability tool-selection \
  --sub-capability schema-adherence \
  --sub-capability recovery \
  --primary-evaluation-mode execution-based \
  --baseline-probe "tool choice plus recovery regression set" \
  --heldout-evaluation "heldout tool-use execution slice" \
  --success-metric "execution pass rate >= 0.80" \
  --acceptance-criterion "Recovery behavior no longer loops on invalid calls"

python3 scripts/emit_probe_generation_plan.py \
  --capability-intake artifacts/model-improvement-planner/tool-use-routing/capability-intake.json \
  --evaluation-plan artifacts/model-improvement-planner/tool-use-routing/evaluation-plan.json \
  --output artifacts/model-improvement-planner/tool-use-routing/probe-generation-plan.json
```

Use this pattern when you need to preserve the route between controller fixes, runtime fixes, and training instead of defaulting to fine-tuning.

## Example 7: Speech Request Routed To Composition

Use this when the user asks for speech I/O and the architecture fit is still uncertain.

```bash
python3 scripts/artifact_cli.py bundle bootstrap \
  --output-dir artifacts/model-improvement-planner/speech-compose \
  --target-capability "speech conversation with local model" \
  --user-intent planning \
  --deployment-context '{"runtime":"desktop-assistant","surface":"streaming"}' \
  --constraints '{"cpu":"acceptable","gpu":"optional","latency_budget_ms":800}' \
  --desired-outcome "Support speech input and speech output in a bounded local loop" \
  --failure-mode "Pretends a text-only model natively handles audio" \
  --success-criterion "A system-composition route is clearly justified or rejected" \
  --input-modality audio \
  --output-modality speech \
  --sub-capability stt \
  --sub-capability dialogue-state \
  --sub-capability tts \
  --primary-evaluation-mode verifier-based \
  --baseline-probe "speech pipeline feasibility check" \
  --heldout-evaluation "end-to-end speech regression checklist" \
  --acceptance-criterion "Architecture fit is explicit before route selection"

python3 scripts/artifact_cli.py bundle system-route \
  --decision-output artifacts/model-improvement-planner/speech-compose/intervention-decision.json \
  --system-output artifacts/model-improvement-planner/speech-compose/system-composition-plan.json \
  --target-capability "speech conversation with local model" \
  --chosen-intervention-family system_composition \
  --implementation-direction "compose ASR, local text model, and TTS into a bounded streaming loop" \
  --decision-status continue \
  --decision-summary "Speech I/O depends on external subsystems rather than direct weight changes." \
  --stop-or-continue-reason "The current architecture is text-centric and needs explicit ASR/TTS composition." \
  --problem-type missing_subsystem \
  --decision-rejected-alternative generic_sft \
  --system-goal "Compose ASR, response generation, and TTS into one bounded local workflow." \
  --architecture-summary "ASR feeds text into the model, then TTS renders the final response." \
  --orchestration-summary "A controller manages streaming boundaries, turn-taking, and fallbacks." \
  --evaluation-plan '{"reference_artifact":"artifacts/model-improvement-planner/speech-compose/evaluation-plan.json"}' \
  --component '{"name":"asr","role":"speech to text"}' \
  --component '{"name":"llm","role":"response generation"}' \
  --component '{"name":"tts","role":"text to speech"}' \
  --interface '{"from":"asr","to":"llm","payload":"transcript"}' \
  --interface '{"from":"llm","to":"tts","payload":"final response"}' \
  --failure-handling "Fallback to text output when TTS is unavailable" \
  --observability-requirement "Log transcripts and final outputs together"
```

Use this pattern when the right answer is architecture-aware composition, not pretending that generic SFT solves speech.

## Example 8: Phase 4 regression coverage – Traditional Chinese fidelity pipeline

Use this when you need concrete commands that enforce strongest-language comparison probes and teacher loops before any training route is accepted.

This is a regression example for a Traditional Chinese optimization target. Replace `--target-language zh-Hant` with the real target language for the user, or omit it when the target language should be inferred from the request and evidence.

```bash
python3 scripts/artifact_cli.py bundle bootstrap \
  --output-dir artifacts/model-improvement-planner/zh-hant-regression \
  --target-capability "Traditional Chinese instruction following" \
  --user-intent planning \
  --deployment-context '{"runtime":"local-chat","surface":"interactive"}' \
  --constraints '{"gpu":"1x24GB","latency_budget_ms":1200}' \
  --desired-outcome "Strong Traditional Chinese fluency with task correctness" \
  --failure-mode "Fallback to English or simplified Chinese" \
  --success-criterion "Target-language fidelity improves without correctness loss" \
  --baseline-probe "strong-language comparison prompts" \
  --primary-evaluation-mode teacher-review \
  --input-modality text \
  --output-modality text

python3 scripts/emit_probe_generation_plan.py \
  --capability-intake artifacts/model-improvement-planner/zh-hant-regression/capability-intake.json \
  --evaluation-plan artifacts/model-improvement-planner/zh-hant-regression/evaluation-plan.json \
  --output artifacts/model-improvement-planner/zh-hant-regression/probe-generation-plan.json \
  --target-language zh-Hant

python3 scripts/emit_teacher_loop_plan.py \
  --capability-intake artifacts/model-improvement-planner/zh-hant-regression/capability-intake.json \
  --evaluation-plan artifacts/model-improvement-planner/zh-hant-regression/evaluation-plan.json \
  --probe-summary artifacts/model-improvement-planner/zh-hant-regression/probe-summary.json \
  --training-plan artifacts/model-improvement-planner/zh-hant-regression/training-plan.json \
  --output artifacts/model-improvement-planner/zh-hant-regression/teacher-loop-plan.json
```

Use this pattern when the regression suite must ensure the strongest-language comparison and teacher roles are documented before any script emission.

## Example 9: Phase 4 regression coverage – speech/tool/system-composition pipeline

Use this when the regression assurance needs explicit speech, tool, and system composition planning before committing to a route.

```bash
python3 scripts/artifact_cli.py bundle bootstrap \
  --output-dir artifacts/model-improvement-planner/speech-tool-regression \
  --target-capability "speech controller with dependable tool routing" \
  --user-intent planning \
  --deployment-context '{"runtime":"desktop-assistant","surface":"streaming"}' \
  --constraints '{"cpu":"acceptable","gpu":"optional","latency_budget_ms":800}' \
  --desired-outcome "Speech I/O, recovery, and tool execution compose into one bounded loop" \
  --failure-mode "Pretending the text-only model already supports speech/tool sequencing" \
  --success-criterion "System composition plan and recovery verifier are explicit" \
  --input-modality audio \
  --output-modality speech \
  --primary-evaluation-mode verifier-based \
  --baseline-probe "speech+tool execution sketch" \
  --acceptance-criterion "Architecture fit documented before any fine-tuning"

python3 scripts/emit_probe_generation_plan.py \
  --capability-intake artifacts/model-improvement-planner/speech-tool-regression/capability-intake.json \
  --evaluation-plan artifacts/model-improvement-planner/speech-tool-regression/evaluation-plan.json \
  --output artifacts/model-improvement-planner/speech-tool-regression/probe-generation-plan.json

python3 scripts/emit_teacher_loop_plan.py \
  --capability-intake artifacts/model-improvement-planner/speech-tool-regression/capability-intake.json \
  --evaluation-plan artifacts/model-improvement-planner/speech-tool-regression/evaluation-plan.json \
  --probe-summary artifacts/model-improvement-planner/speech-tool-regression/probe-summary.json \
  --training-plan artifacts/model-improvement-planner/speech-tool-regression/training-plan.json \
  --output artifacts/model-improvement-planner/speech-tool-regression/teacher-loop-plan.json

python3 scripts/artifact_cli.py bundle system-route \
  --decision-output artifacts/model-improvement-planner/speech-tool-regression/intervention-decision.json \
  --system-output artifacts/model-improvement-planner/speech-tool-regression/system-composition-plan.json \
  --target-capability "speech controller with dependable tool routing" \
  --chosen-intervention-family system_composition \
  --implementation-direction "Orchestrate ASR, controller, and TTS/tool recovery in one bounded loop" \
  --decision-status continue \
  --decision-summary "Speech and tool recovery need explicit orchestration, not generic tuning." \
  --problem-type missing_subsystem \
  --decision-rejected-alternative generic_sft \
  --system-goal "Compose ASR, tool controller, and TTS plus recovery into a managed workflow." \
  --architecture-summary "Speech -> controller -> tool traces -> fallback TTS" \
  --evaluation-plan '{"reference_artifact":"artifacts/model-improvement-planner/speech-tool-regression/evaluation-plan.json"}'
```

Use this pattern when the regression suite must confirm speech/tool/system composition steps are concrete before release.
