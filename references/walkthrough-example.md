# End-to-End Walkthrough

> This walkthrough demonstrates the flow from capability request to execution artifacts. The request values are illustrative, not prescriptive; the structure applies to any capability optimization path.

## Example Request
"Improve my local Qwen2.5-7B model's ability to remain consistent in multi-step reasoning while supporting structured tool calls."

## Stage 0: Environment & Model Discovery

- command: `python3 scripts/discover_environment.py --workspace-root "$WORKSPACE" --output artifacts/<slug>/environment-discovery.json`
- expected output: `environment-discovery.json` listing available GPUs, datasets, runtimes, and discovered scripts; include a `tool_inventory` section enumerating callable backends
- fixed: always run discovery before assuming tooling; dynamic: the actual backends listed depend on `discover_environment`

## Stage 1: Generate Probe Specs

- command: build a JSONL such as `artifacts/<slug>/probe-specs.jsonl` following `references/probes/probe-spec-template.jsonl` shape
- include multiple `probe_family` entries covering reasoning, tool use, and localization, and note which evaluation mode (`teacher-review`, `execution-based`, etc.) applies
- fixed: the schema shape, expected evaluation metadata, and use of `probe_generation_plan` are consistent; dynamic: the prompts, languages, and rubrics reflect the specific capability gap

## Stage 2: Connect to Student Model

- inspect `references/routing/student-model-connection-guide.md` and generated `backend_config.json`
- if the model is served, use `openai_compatible_http` adapter; if only weights exist, emit a short-lived script that loads the weights, exposes a REST endpoint, and writes `backend_config.json`
- dynamic: the backend adapter (Ollama, vLLM, custom) depends on the discovery output; fixed: always record the chosen backend URL inside `backend_config.json`

## Stage 3: Run Probes & Analyze Results

- command: `python3 scripts/run_capability_probes.py --probe-specs artifacts/<slug>/probe-specs.jsonl --backend-config artifacts/<slug>/backend_config.json --results-output artifacts/<slug>/probe-results.jsonl --summary-output artifacts/<slug>/probe-summary.json`
- outputs: `probe-results.jsonl` and `probe-summary.json`; the summary fields (`failure_signatures`, `suspected_bottlenecks`, `route_readiness`) must align with existing contracts
- fixed: rely on `run_capability_probes.py` to normalize results; dynamic: the backend and rubric references vary per capability

## Stage 4: Route Selection

- read `probe-summary.json` and select an intervention family; write `artifacts/<slug>/intervention-decision.json` via `python3 scripts/artifact_cli.py write intervention-decision ...`
- include `chosen_intervention_family`, `decision_summary`, and `rejected_alternatives`; note whether the bottleneck is runtime, controller, or data
- dynamic: the chosen intervention depends on `probe_summary.failure_modes`; fixed: documentation always records the decision in the artifact and links to `references/orchestration/dynamic-script-generation.md` if scripts are required

## Stage 5: Teacher Loop

- teacher persona: the running reading model acts as `diagnostician`, `critique teacher`, and `verifier` in order
- use `run_capability_probes.py` outputs, then apply the templates from `references/training/teacher-loop-execution-guide.md`
- artifact flow: `probe-results.jsonl` -> `teacher-review` corrections -> `dataset-records.jsonl`; include teacher scores, error types, and corrections using the dataset contract mapping (`probe_result.input` -> `dataset_record.input`, `teacher_correction` -> `dataset_record.target`)
- intermediate artifact example — teacher review of one probe result:
```json
{
  "probe_id": "probe-reasoning-007",
  "student_response": "The answer is 42 because...",
  "teacher_role": "critique_teacher",
  "score": 0.35,
  "passed": false,
  "observed_defects": ["reasoning_gap", "unsupported_conclusion"],
  "corrected_output": "To solve this step by step: first we identify...",
  "confidence": 0.9
}
```
- the above review is then converted into a dataset record:
```json
{
  "contract": "dataset_record",
  "schema_version": "1.0",
  "input": "Explain the multi-step reasoning required to...",
  "target": "To solve this step by step: first we identify...",
  "metadata": {
    "dataset_mode": "direct_answer",
    "capability_family": "reasoning",
    "supervision_shape": "critique_then_rewrite",
    "source_provenance": "teacher_loop_probe_reasoning_007",
    "teacher_role": "critique_teacher"
  }
}
```
- stop condition: once average score exceeds the threshold in the plan, write `teacher-loop-plan.json` noting the switch to `demonstrator` or `preference judge` if diversity drops

## Stage 6: Dataset Conversion

- the reading model generates a project-local `convert_dataset.py` script (this script does NOT exist inside the skill package; it is dynamically created for the user's project following `references/data/dataset-format-guide.md`)
- run the generated script to turn `dataset-records.jsonl` into the required formats (Alpaca, ChatML, TRL DPO, tokenized HF)
- conversion choices follow `training-plan.json` `intervention_family` and `supervision_shape`; record the chosen format and rationale inside `training-plan.outcome`
- the script writes both the converted file and a contract summary referencing `references/data/dataset-format-guide.md`

## Stage 7: Generate Training Script

- command: `python3 scripts/emit_generated_script_plan.py --capability-intake artifacts/<slug>/capability-intake.json --evaluation-plan artifacts/<slug>/evaluation-plan.json --environment-discovery artifacts/<slug>/environment-discovery.json --training-plan artifacts/<slug>/training-plan.json --output artifacts/<slug>/generated-script-plan.json --script-dir "$WORKSPACE/generated/<slug>"`
- emits `generated-script-plan.json` describing each script, inputs, outputs, readiness, validation command, and preconditions
- fixed: script header always states purpose and validation; dynamic: the chosen script set depends on the discovered tools, e.g., whether PEFT tooling is present

## Stage 8: Validation

- commands: `python3 scripts/validate_contracts.py --artifact artifacts/<slug>/training-plan.json --contract training_plan` and `python3 scripts/validate_artifact_chain.py --bundle artifacts/<slug>`
- verify that new artifacts reference each other consistently; the validation paths are constant, but the artifacts themselves depend on the earlier stages
