#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_python(script_name: str, *args: str) -> str:
    command = [sys.executable, str(SCRIPTS_DIR / script_name), *args]
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        raise SystemExit(f"Command failed: {' '.join(command)}\n{detail}")
    return result.stdout.strip()


def build_fake_model(model_dir: Path) -> None:
    model_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        model_dir / "config.json",
        {
            "model_type": "qwen2_vl",
            "architectures": ["Qwen2VLForConditionalGeneration"],
            "torch_dtype": "bfloat16",
            "vocab_size": 151936,
            "max_position_embeddings": 32768,
        },
    )
    write_json(
        model_dir / "generation_config.json",
        {
            "max_new_tokens": 256,
            "temperature": 0.2,
        },
    )
    write_json(
        model_dir / "tokenizer_config.json",
        {
            "tokenizer_class": "Qwen2Tokenizer",
            "model_max_length": 32768,
            "chat_template": "{{ bos_token }}{{ messages }}",
        },
    )
    (model_dir / "README.md").write_text(
        """---
language:
- en
tags:
- multimodal
- chart-qa
license: apache-2.0
base_model: demo/local-vlm
---

Smoke-test model card.
""",
        encoding="utf-8",
    )


def build_fake_workspace_surfaces(work_dir: Path) -> None:
    project_dir = work_dir / "project"
    (project_dir / "app").mkdir(parents=True, exist_ok=True)
    (project_dir / "data").mkdir(parents=True, exist_ok=True)
    (project_dir / "eval").mkdir(parents=True, exist_ok=True)
    (project_dir / "pyproject.toml").write_text(
        "[project]\nname = 'aco-smoke-demo'\nversion = '0.1.0'\n",
        encoding="utf-8",
    )
    (project_dir / "app" / "train_adapter.py").write_text(
        "from transformers import Trainer\n\ndef train():\n    pass\n",
        encoding="utf-8",
    )
    (project_dir / "app" / "serve_api.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n",
        encoding="utf-8",
    )
    (project_dir / "data" / "seed.jsonl").write_text(
        json.dumps({"prompt": "hello", "target": "world"}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (project_dir / "eval" / "run_eval.py").write_text(
        "def benchmark():\n    assert True\n",
        encoding="utf-8",
    )


def build_probe_inputs(work_dir: Path) -> tuple[Path, Path]:
    probe_specs_path = work_dir / "probe-specs.jsonl"
    probe_responses_path = work_dir / "probe-responses.jsonl"
    write_jsonl(
        probe_specs_path,
        [
            {
                "probe_id": "chart-title",
                "probe_family": "multimodal_grounding",
                "prompt": "Read the chart title from the supplied image.",
                "expected_evaluation_mode": "exact-match",
                "target_capability": "image-grounded chart question answering",
                "target_language": "en",
                "tags": ["chart", "grounding"],
            },
            {
                "probe_id": "legend-color",
                "probe_family": "multimodal_grounding",
                "prompt": "Identify which legend color corresponds to revenue.",
                "expected_evaluation_mode": "exact-match",
                "target_capability": "image-grounded chart question answering",
                "target_language": "en",
                "tags": ["chart", "legend"],
            },
        ],
    )
    write_jsonl(
        probe_responses_path,
        [
            {
                "probe_id": "chart-title",
                "response": "Revenue by Quarter",
                "score": 0.9,
                "passed": True,
                "response_language_hint": "en",
                "notes": "exact title match",
            },
            {
                "probe_id": "legend-color",
                "response": "Blue",
                "score": 0.8,
                "passed": True,
                "response_language_hint": "en",
                "notes": "legend color identified correctly",
            },
        ],
    )
    return probe_specs_path, probe_responses_path


def validate_contract(path: Path, contract: str) -> None:
    run_python("validate_contracts.py", "--artifact", str(path), "--contract", contract)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a bundled smoke test for model-improvement-planner.")
    parser.add_argument(
        "--keep-tempdir",
        default="",
        help="Optional directory to keep the generated smoke-test workspace instead of using a temporary directory.",
    )
    args = parser.parse_args()

    temp_root: Path | None = None
    temp_manager = None
    try:
        if args.keep_tempdir:
            work_dir = Path(args.keep_tempdir).resolve()
            if work_dir.exists():
                shutil.rmtree(work_dir)
            work_dir.mkdir(parents=True, exist_ok=True)
        else:
            temp_manager = tempfile.TemporaryDirectory(prefix="aco-smoke-")
            temp_root = Path(temp_manager.name)
            work_dir = temp_root

        model_dir = work_dir / "fake-model"
        project_dir = work_dir / "project"
        artifacts_dir = work_dir / "artifacts"
        bootstrap_dir = artifacts_dir / "chart-qa"
        training_route_dir = bootstrap_dir / "training-route"
        runtime_scaffold_dir = bootstrap_dir / "runtime-scaffold"
        generated_script_dir = bootstrap_dir / "generated"

        build_fake_model(model_dir)
        build_fake_workspace_surfaces(work_dir)
        probe_specs_path, probe_responses_path = build_probe_inputs(work_dir)

        model_profile_path = bootstrap_dir / "model-profile.json"
        run_python(
            "local_model_profile.py",
            "--model-path",
            str(model_dir),
            "--output",
            str(model_profile_path),
            "--model-id",
            "demo-local-vlm",
            "--serving-stack",
            "vllm",
            "--training-stack",
            "transformers",
            "--capability-hint",
            "multimodal-grounding",
            "--language-hint",
            "en",
        )
        validate_contract(model_profile_path, "local-model-profile")

        probe_results_path = bootstrap_dir / "probe-results.jsonl"
        probe_summary_path = bootstrap_dir / "probe-summary.json"
        run_python(
            "run_capability_probes.py",
            "--probe-specs",
            str(probe_specs_path),
            "--responses-jsonl",
            str(probe_responses_path),
            "--results-output",
            str(probe_results_path),
            "--summary-output",
            str(probe_summary_path),
            "--model-profile",
            str(model_profile_path),
        )
        validate_contract(probe_summary_path, "probe-summary")

        run_python(
            "artifact_cli.py",
            "bundle",
            "bootstrap",
            "--output-dir",
            str(bootstrap_dir),
            "--target-capability",
            "image-grounded chart question answering",
            "--user-intent",
            "planning",
            "--deployment-context",
            json.dumps({"runtime": "local-api", "surface": "batch"}),
            "--constraints",
            json.dumps({"gpu": "1x24GB", "latency_budget_ms": 1500}),
            "--desired-outcome",
            "Answer chart questions without hallucinated entities.",
            "--failure-mode",
            "Invents entities not present in the chart.",
            "--success-criterion",
            "Held-out exact match >= 0.85.",
            "--input-modality",
            "image",
            "--output-modality",
            "text",
            "--sub-capability",
            "chart-reading",
            "--sub-capability",
            "grounded-answer-generation",
            "--external-dependency",
            "multimodal runtime bridge",
            "--missing-fact",
            "final serving runtime loader",
            "--primary-evaluation-mode",
            "exact-match",
            "--baseline-probe",
            "chart title extraction",
            "--heldout-evaluation",
            "heldout chart benchmark slice",
            "--success-metric",
            "exact match >= 0.85",
            "--acceptance-criterion",
            "No unsupported references in heldout answers",
            "--regression-check",
            "Text-only QA baseline remains stable",
            "--unresolved-risk",
            "OCR on tiny legends remains fragile",
            "--stop-condition",
            "Stop if grounding accuracy stays below 0.70 after route trial",
        )

        capability_intake_path = bootstrap_dir / "capability-intake.json"
        evaluation_plan_path = bootstrap_dir / "evaluation-plan.json"
        validate_contract(capability_intake_path, "capability-intake")
        validate_contract(evaluation_plan_path, "evaluation-plan")

        evaluation_reference = json.dumps({"reference_artifact": str(evaluation_plan_path)})
        decision_path = bootstrap_dir / "intervention-decision.json"
        training_plan_path = bootstrap_dir / "training-plan.json"
        run_python(
            "artifact_cli.py",
            "bundle",
            "training-route",
            "--decision-output",
            str(decision_path),
            "--training-output",
            str(training_plan_path),
            "--target-capability",
            "image-grounded chart question answering",
            "--chosen-intervention-family",
            "supervised_learning",
            "--implementation-direction",
            "Multimodal SFT with grounded chart QA records.",
            "--decision-status",
            "continue",
            "--decision-summary",
            "The current stack already preserves the multimodal path.",
            "--stop-or-continue-reason",
            "Baseline probes show recoverable grounding errors rather than missing modality support.",
            "--problem-type",
            "data_distribution",
            "--evidence-basis",
            "probe_summary indicates stable multimodal responses with chart grounding gaps.",
            "--decision-rejected-alternative",
            "model_replacement",
            "--key-risk",
            "Grounding gains may not survive deployment packaging.",
            "--next-action",
            "Generate grounded multimodal training records.",
            "--training-intervention-family",
            "supervised_learning",
            "--supervision-shape",
            "multimodal_instruction_response",
            "--base-model-suitability-verdict",
            "suitable_with_grounded_data",
            "--training-stack-suitability-verdict",
            "suitable_on_existing_stack",
            "--teacher-plan",
            json.dumps({"teacher_role": "demonstrator", "source": "stronger-vlm"}),
            "--data-plan",
            json.dumps({"dataset_strategy": "grounded chart QA", "source": "curated internal charts"}),
            "--evaluation-plan",
            evaluation_reference,
            "--implementation-candidate",
            "unsloth_sft",
            "--training-rejected-alternative",
            "generic_preference_tuning",
            "--serving-compatibility-note",
            "Validate projector packaging before release.",
            "--compute-assumption",
            "single 24GB GPU",
            "--stop-criterion",
            "Stop if held-out exact match does not improve by 0.10.",
            "--rollback-criterion",
            "Rollback if the text-only regression suite fails.",
            "--expected-failure-mode",
            "Legend OCR remains weak on tiny fonts.",
        )
        validate_contract(decision_path, "intervention-decision")
        validate_contract(training_plan_path, "training-plan")

        environment_discovery_path = bootstrap_dir / "environment-discovery.json"
        tool_inventory_path = bootstrap_dir / "tool-inventory.json"
        probe_generation_plan_path = bootstrap_dir / "probe-generation-plan.json"
        teacher_loop_plan_path = bootstrap_dir / "teacher-loop-plan.json"
        generated_script_plan_path = bootstrap_dir / "generated-script-plan.json"
        run_python(
            "discover_environment.py",
            "--workspace-root",
            str(project_dir),
            "--output",
            str(environment_discovery_path),
        )
        validate_contract(environment_discovery_path, "environment-discovery")

        run_python(
            "emit_tool_inventory.py",
            "--environment-discovery",
            str(environment_discovery_path),
            "--output",
            str(tool_inventory_path),
            "--inventory-scope",
            "workspace_plus_session",
            "--skill",
            json.dumps({"name": "model-improvement-planner", "availability": "present"}),
            "--mcp-server",
            json.dumps({"name": "context7", "availability": "present"}),
            "--mcp-resource",
            "context7 library docs lookup",
            "--local-script",
            json.dumps({"path": "scripts/run_capability_probes.py", "role": "baseline_probing"}),
            "--runtime",
            json.dumps({"runtime_id": "openai_compatible_http", "availability": "present"}),
            "--backend-adapter",
            "command",
            "--backend-adapter",
            "openai_compatible_http",
            "--network-capability",
            "official_doc_research",
            "--constraint",
            "No image collection path has been approved by the user yet.",
            "--recommended-usage-note",
            "Use local references first, then current-session tools for stack-specific docs.",
        )
        validate_contract(tool_inventory_path, "tool-inventory")

        run_python(
            "emit_probe_generation_plan.py",
            "--capability-intake",
            str(capability_intake_path),
            "--evaluation-plan",
            str(evaluation_plan_path),
            "--model-profile",
            str(model_profile_path),
            "--output",
            str(probe_generation_plan_path),
            "--target-language",
            "en",
        )
        validate_contract(probe_generation_plan_path, "probe-generation-plan")

        run_python(
            "emit_teacher_loop_plan.py",
            "--capability-intake",
            str(capability_intake_path),
            "--evaluation-plan",
            str(evaluation_plan_path),
            "--probe-summary",
            str(probe_summary_path),
            "--training-plan",
            str(training_plan_path),
            "--output",
            str(teacher_loop_plan_path),
        )
        validate_contract(teacher_loop_plan_path, "teacher-loop-plan")

        run_python(
            "emit_generated_script_plan.py",
            "--capability-intake",
            str(capability_intake_path),
            "--evaluation-plan",
            str(evaluation_plan_path),
            "--environment-discovery",
            str(environment_discovery_path),
            "--training-plan",
            str(training_plan_path),
            "--output",
            str(generated_script_plan_path),
            "--script-dir",
            str(generated_script_dir),
        )
        validate_contract(generated_script_plan_path, "generated-script-plan")
        run_python(
            "validate_artifact_chain.py",
            "--intake",
            str(capability_intake_path),
            "--evaluation",
            str(evaluation_plan_path),
            "--decision",
            str(decision_path),
            "--training",
            str(training_plan_path),
            "--environment-discovery",
            str(environment_discovery_path),
            "--tool-inventory",
            str(tool_inventory_path),
            "--probe-generation-plan",
            str(probe_generation_plan_path),
            "--teacher-loop-plan",
            str(teacher_loop_plan_path),
            "--generated-script-plan",
            str(generated_script_plan_path),
            "--model-profile",
            str(model_profile_path),
            "--probe-summary",
            str(probe_summary_path),
        )

        run_python(
            "emit_training_route.py",
            "--training-plan",
            str(training_plan_path),
            "--route-family",
            "unsloth-sft",
            "--output-dir",
            str(training_route_dir),
            "--dataset-path",
            str(bootstrap_dir / "dataset-records.jsonl"),
            "--base-model",
            str(model_dir),
        )
        validate_contract(training_route_dir / "training-route-manifest.json", "training-route-manifest")

        system_decision_path = bootstrap_dir / "system-decision.json"
        system_plan_path = bootstrap_dir / "system-composition-plan.json"
        run_python(
            "artifact_cli.py",
            "bundle",
            "system-route",
            "--decision-output",
            str(system_decision_path),
            "--system-output",
            str(system_plan_path),
            "--target-capability",
            "image-grounded chart question answering",
            "--chosen-intervention-family",
            "system_composition",
            "--implementation-direction",
            "External OCR plus chart parser feeding a constrained answer model.",
            "--decision-status",
            "continue",
            "--decision-summary",
            "A composed perception stage is more rational for chart-heavy inputs.",
            "--stop-or-continue-reason",
            "Native multimodal support remains insufficient for reliable chart grounding.",
            "--problem-type",
            "architecture_mismatch",
            "--evidence-basis",
            "Probe weaknesses concentrate in perception and OCR-adjacent failures.",
            "--decision-rejected-alternative",
            "generic_sft",
            "--key-risk",
            "OCR latency may exceed the interaction budget.",
            "--next-action",
            "Prototype the perception plus answer-generation chain.",
            "--system-goal",
            "Compose OCR, chart parsing, and answer generation into a bounded workflow.",
            "--architecture-summary",
            "The perception stage extracts structured evidence before answer generation.",
            "--orchestration-summary",
            "A controller passes extracted entities into a constrained answer template.",
            "--evaluation-plan",
            evaluation_reference,
            "--component",
            json.dumps({"name": "ocr", "role": "extract chart text"}),
            "--component",
            json.dumps({"name": "vlm", "role": "answer from extracted evidence"}),
            "--interface",
            json.dumps({"from": "ocr", "to": "vlm", "payload": "structured chart evidence"}),
            "--latency-implication",
            "Two-stage inference adds preprocessing cost.",
            "--failure-handling",
            "Abstain when OCR confidence falls below threshold.",
            "--observability-requirement",
            "Log extracted evidence with the final answer.",
            "--unresolved-gap",
            "OCR confidence calibration remains unvalidated.",
        )
        validate_contract(system_decision_path, "intervention-decision")
        validate_contract(system_plan_path, "system-composition-plan")
        run_python(
            "validate_artifact_chain.py",
            "--intake",
            str(capability_intake_path),
            "--evaluation",
            str(evaluation_plan_path),
            "--decision",
            str(system_decision_path),
            "--system",
            str(system_plan_path),
            "--model-profile",
            str(model_profile_path),
            "--probe-summary",
            str(probe_summary_path),
        )

        run_python(
            "generate_runtime_scaffold.py",
            "--output-dir",
            str(runtime_scaffold_dir),
            "--runtime-id",
            "demo-local-runtime",
            "--model-family",
            "qwen2-vl",
            "--weight-format",
            "safetensors",
            "--tokenizer-format",
            "hf_tokenizer",
            "--inference-loading-strategy",
            "Load via local Transformers-compatible runtime wrapper.",
            "--training-support-status",
            "partial",
            "--assumption",
            "Projector weights ship with the main checkpoint.",
            "--unresolved-gap",
            "Export path to the final serving runtime is not validated.",
        )
        validate_contract(runtime_scaffold_dir / "scaffold_manifest.json", "runtime-scaffold-manifest")
        run_python("validate_runtime_scaffold.py", "--scaffold-dir", str(runtime_scaffold_dir))

        print(f"Smoke test passed: {work_dir}")
    finally:
        if temp_manager is not None:
            temp_manager.cleanup()


if __name__ == "__main__":
    main()
