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
            "model_type": "qwen2",
            "architectures": ["QwenForConditionalGeneration"],
            "torch_dtype": "fp16",
            "vocab_size": 151938,
            "max_position_embeddings": 16384,
        },
    )
    write_json(
        model_dir / "generation_config.json",
        {
            "max_new_tokens": 128,
            "temperature": 0.3,
        },
    )
    write_json(
        model_dir / "tokenizer_config.json",
        {
            "tokenizer_class": "QwenTokenizer",
            "model_max_length": 16384,
            "chat_template": "{{ bos_token }}{{ messages }}",
        },
    )
    (model_dir / "README.md").write_text(
        """---
language:
- en
- zh-Hant
tags:
- localization
- planning
license: apache-2.0
base_model: demo/local-qwen
---

Demo localization model.
""",
        encoding="utf-8",
    )


def build_probe_summary(path: Path, model_profile_path: Path) -> None:
    payload = {
        "contract": "probe_summary",
        "schema_version": "1",
        "total_probes": 2,
        "answered_probes": 2,
        "missing_responses": 0,
        "families": {"language_localization": {"passed": 1, "failed": 1}},
        "response_statuses": {"passed": 1, "failed": 1},
        "expected_evaluation_modes": {"rubric-based": 2},
        "target_languages": {"zh-Hant": 2},
        "response_languages": {"zh-Hant": 2},
        "family_diagnostics": {"language_localization": {"tone_consistency": "needs_review"}},
        "model_profile_reference": str(model_profile_path),
        "average_score": 0.75,
        "pass_rate": 0.5,
        "strengths": ["term selection stays consistent"],
        "weaknesses": ["tone and register drift between sections"],
        "failure_signatures": ["literal English phrasing leaked"],
        "suspected_bottlenecks": ["insufficient context for cultural references"],
        "recommended_teacher_roles": ["critique_teacher"],
        "recommended_supervision_shapes": ["instruction_refinement"],
        "route_readiness": {"status": "partial_baseline", "confidence": 0.6},
    }
    write_json(path, payload)


def validate_contract(path: Path, contract: str) -> None:
    run_python("validate_contracts.py", "--artifact", str(path), "--contract", contract)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a Traditional Chinese localization regression scenario.")
    parser.add_argument(
        "--keep-tempdir",
        default="",
        help="Optional directory to keep the generated workspace instead of using a temporary directory.",
    )
    args = parser.parse_args()

    temp_manager = None
    temp_root: Path | None = None
    try:
        if args.keep_tempdir:
            work_dir = Path(args.keep_tempdir).resolve()
            if work_dir.exists():
                shutil.rmtree(work_dir)
            work_dir.mkdir(parents=True, exist_ok=True)
        else:
            temp_manager = tempfile.TemporaryDirectory(prefix="aco-regression-")
            temp_root = Path(temp_manager.name)
            work_dir = temp_root

        artifacts_dir = work_dir / "artifacts"
        bootstrap_dir = artifacts_dir / "traditional-chinese-localization"
        model_dir = work_dir / "fake-model"

        build_fake_model(model_dir)

        run_python(
            "artifact_cli.py",
            "bundle",
            "bootstrap",
            "--output-dir",
            str(bootstrap_dir),
            "--target-capability",
            "traditional-chinese localization",
            "--user-intent",
            "planning",
            "--deployment-context",
            json.dumps({"runtime": "planning_simulation"}),
            "--constraints",
            json.dumps({"resources": "planning_only", "approval": "pending"}),
            "--desired-outcome",
            "Structured localization plan for zh-Hant",
            "--failure-mode",
            "Target-tone drift",
            "--success-criterion",
            "High rubric score for zh-Hant segments",
            "--input-modality",
            "text",
            "--output-modality",
            "text",
            "--sub-capability",
            "translation",
            "--sub-capability",
            "culture-aware localization",
            "--external-dependency",
            "glossary-review-board",
            "--missing-fact",
            "target-audience-persona",
            "--primary-evaluation-mode",
            "rubric-based",
            "--baseline-probe",
            "Translate feature story to zh-Hant with localized idioms",
            "--heldout-evaluation",
            "zh-Hant localization benchmark set",
            "--success-metric",
            "rubric score >= 0.8",
            "--acceptance-criterion",
            "Tone and terminology align with brand voice",
            "--regression-check",
            "zh-Hant plan stability",
            "--unresolved-risk",
            "Limited zh-Hant annotators",
            "--stop-condition",
            "Stop if rubric < 0.6 twice",
        )

        capability_intake_path = bootstrap_dir / "capability-intake.json"
        evaluation_plan_path = bootstrap_dir / "evaluation-plan.json"
        validate_contract(capability_intake_path, "capability-intake")
        validate_contract(evaluation_plan_path, "evaluation-plan")

        model_profile_path = bootstrap_dir / "model-profile.json"
        run_python(
            "local_model_profile.py",
            "--model-path",
            str(model_dir),
            "--output",
            str(model_profile_path),
            "--model-id",
            "demo-local-zh-hant",
            "--serving-stack",
            "transformers",
            "--training-stack",
            "transformers",
            "--language-hint",
            "en",
            "--language-hint",
            "zh-Hant",
            "--capability-hint",
            "language_localization",
        )
        validate_contract(model_profile_path, "local-model-profile")

        probe_generation_plan_path = bootstrap_dir / "probe-generation-plan.json"
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
            "zh-Hant",
        )
        validate_contract(probe_generation_plan_path, "probe-generation-plan")

        probe_summary_path = bootstrap_dir / "probe-summary.json"
        build_probe_summary(probe_summary_path, model_profile_path)
        validate_contract(probe_summary_path, "probe-summary")

        decision_path = bootstrap_dir / "intervention-decision.json"
        training_plan_path = bootstrap_dir / "training-plan.json"
        evaluation_reference = json.dumps({"reference_artifact": str(evaluation_plan_path)})
        run_python(
            "artifact_cli.py",
            "bundle",
            "training-route",
            "--decision-output",
            str(decision_path),
            "--training-output",
            str(training_plan_path),
            "--target-capability",
            "traditional-chinese localization",
            "--chosen-intervention-family",
            "planning",
            "--implementation-direction",
            "Structured localization planning before execution",
            "--decision-status",
            "continue",
            "--decision-summary",
            "Need a bounded plan before running localization tuning.",
            "--stop-or-continue-reason",
            "Baseline planning evidence remains partial.",
            "--problem-type",
            "planning",
            "--evidence-basis",
            "Probe summary signals tone drift in zh-Hant outputs.",
            "--decision-rejected-alternative",
            "model_replacement",
            "--key-risk",
            "Planning fails to maintain localized tone.",
            "--next-action",
            "Collect annotated glossaries and style guide samples.",
            "--training-intervention-family",
            "planning",
            "--supervision-shape",
            "instruction_refinement",
            "--base-model-suitability-verdict",
            "suitable_for_planning",
            "--training-stack-suitability-verdict",
            "suitable_with_existing_stack",
            "--teacher-plan",
            json.dumps({"teacher_role": "critique_teacher"}),
            "--data-plan",
            json.dumps({"dataset_strategy": "localized_strings_review"}),
            "--evaluation-plan",
            evaluation_reference,
            "--implementation-candidate",
            "localized_instruction_refinement",
            "--training-rejected-alternative",
            "generic_tuning",
            "--serving-compatibility-note",
            "Planning outputs feed into zh-Hant localization pipeline.",
            "--compute-assumption",
            "planning runs on CPU",
            "--stop-criterion",
            "Stop when rubric >= 0.85",
            "--rollback-criterion",
            "Rollback if rubric falls below baseline",
            "--expected-failure-mode",
            "Missing tone guidelines",
        )
        validate_contract(decision_path, "intervention-decision")
        validate_contract(training_plan_path, "training-plan")

        teacher_loop_plan_path = bootstrap_dir / "teacher-loop-plan.json"
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
            "validate_artifact_chain.py",
            "--intake",
            str(capability_intake_path),
            "--evaluation",
            str(evaluation_plan_path),
            "--decision",
            str(decision_path),
            "--training",
            str(training_plan_path),
            "--model-profile",
            str(model_profile_path),
            "--probe-summary",
            str(probe_summary_path),
            "--probe-generation-plan",
            str(probe_generation_plan_path),
            "--teacher-loop-plan",
            str(teacher_loop_plan_path),
        )

        print(f"Localization regression test passed: {work_dir}")
    finally:
        if temp_manager is not None:
            temp_manager.cleanup()


if __name__ == "__main__":
    main()
