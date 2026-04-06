#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lib.artifacts import build_generated_script_plan_artifact
from validate_contracts import VALIDATORS, ValidationError, load_json


def _load_contract(path: Path, contract: str) -> dict[str, Any]:
    payload = load_json(path)
    try:
        VALIDATORS[contract](payload)
    except ValidationError as exc:
        raise SystemExit(f"{contract} failed validation: {exc}") from exc
    return payload


def _normalize(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _choose_flow_kind(training_plan: dict[str, Any] | None) -> str:
    if training_plan is None:
        return "data_and_evaluation_scaffold"
    family = _normalize(training_plan.get("intervention_family", ""))
    supervision_shape = _normalize(training_plan.get("supervision_shape", ""))
    if "distill" in family or "distill" in supervision_shape:
        return "teacher_bootstrap_training"
    if "preference" in family or "preference" in supervision_shape:
        return "preference_training"
    if "reward" in family:
        return "reward_driven_training"
    return "supervised_or_adaptation_training"


def _derive_dataset_strategy(
    *,
    intake: dict[str, Any],
    evaluation: dict[str, Any],
    environment: dict[str, Any],
    training_plan: dict[str, Any] | None,
) -> dict[str, Any]:
    environment_surfaces = environment["discovered_surfaces"]
    source_strategy = "reuse_detected_project_surfaces" if environment_surfaces["dataset_surfaces"] else "collect_or_generate_project_local_data"
    supervision_shape = training_plan.get("supervision_shape", "") if training_plan is not None else "undecided"
    collection_modes = ["local_workspace_scan"]
    access_patterns = environment["environment_summary"]["source_access_patterns"]
    if "dataset_registry_access" in access_patterns:
        collection_modes.append("dataset_registry_ingest")
    if "http_api_access" in access_patterns:
        collection_modes.append("api_collection")
    generation_modes = ["teacher_generation", "critique_and_revision"]
    if "preference" in _normalize(supervision_shape):
        generation_modes.append("pairwise_ranking")
    if "distill" in _normalize(supervision_shape):
        generation_modes.append("teacher_target_capture")

    return {
        "source_strategy": source_strategy,
        "collection_modes": collection_modes,
        "generation_modes": generation_modes,
        "quality_gates": [
            "schema_validation",
            "deduplication",
            "heldout_split_protection",
            "evaluator_or_verifier_review",
        ],
        "evaluation_mode": evaluation["primary_evaluation_mode"],
        "supervision_shape": supervision_shape,
        "modalities": {
            "input": intake["input_modalities"],
            "output": intake["output_modalities"],
        },
    }


def _script_step(
    *,
    script_id: str,
    path: Path,
    script_kind: str,
    purpose: str,
    inputs: list[str],
    outputs: list[str],
    status: str,
    notes: list[str],
) -> dict[str, Any]:
    return {
        "script_id": script_id,
        "path": str(path),
        "script_kind": script_kind,
        "purpose": purpose,
        "inputs": inputs,
        "outputs": outputs,
        "status": status,
        "notes": notes,
    }


def _write_python_scaffold(path: Path, description: str, body_lines: list[str]) -> None:
    text = [
        "#!/usr/bin/env python3",
        "from __future__ import annotations",
        "",
        '"""',
        description,
        '"""',
        "",
        "import argparse",
        "",
        "",
        "def build_parser() -> argparse.ArgumentParser:",
        f"    parser = argparse.ArgumentParser(description={description!r})",
        "    parser.add_argument('--workspace-root', required=True)",
        "    parser.add_argument('--output', required=True)",
        "    return parser",
        "",
        "",
        "def main() -> None:",
        "    args = build_parser().parse_args()",
    ]
    text.extend(body_lines)
    text.extend(
        [
            "",
            "",
            "if __name__ == '__main__':",
            "    main()",
            "",
        ]
    )
    path.write_text("\n".join(text), encoding="utf-8")
    path.chmod(0o755)


def _write_shell_scaffold(path: Path, lines: list[str]) -> None:
    text = "\n".join(["#!/usr/bin/env bash", "set -euo pipefail", "", *lines, ""])
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def _emit_scaffold_scripts(
    *,
    script_dir: Path,
    dataset_strategy: dict[str, Any],
    environment: dict[str, Any],
    training_plan: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    script_dir.mkdir(parents=True, exist_ok=True)
    script_plan: list[dict[str, Any]] = []

    collect_path = script_dir / "01_collect_sources.py"
    _write_python_scaffold(
        collect_path,
        "Collect project-local or allowlisted external sources into a source manifest.",
        [
            "    print('Scaffold: collect sources for the current project environment.')",
            f"    print('Collection modes: {', '.join(dataset_strategy['collection_modes'])}')",
            f"    print('Discovered dataset surfaces: {len(environment['discovered_surfaces']['dataset_surfaces'])}')",
            "    print(f'Write source manifest to: {args.output}')",
        ],
    )
    script_plan.append(
        _script_step(
            script_id="collect_sources",
            path=collect_path,
            script_kind="python",
            purpose="Collect or enumerate candidate training sources.",
            inputs=["workspace_root", "allowlisted sources", "collection policy"],
            outputs=["source-manifest.json"],
            status="scaffold_only",
            notes=["Reuse detected project surfaces before adding new sources."],
        )
    )

    generate_path = script_dir / "02_generate_dataset.py"
    _write_python_scaffold(
        generate_path,
        "Generate dataset-record compatible supervision from collected sources.",
        [
            "    print('Scaffold: generate dataset records for the selected capability.')",
            f"    print('Generation modes: {', '.join(dataset_strategy['generation_modes'])}')",
            f"    print('Expected supervision shape: {dataset_strategy['supervision_shape']}')",
            "    print(f'Write dataset records to: {args.output}')",
        ],
    )
    script_plan.append(
        _script_step(
            script_id="generate_dataset",
            path=generate_path,
            script_kind="python",
            purpose="Generate or transform supervision into dataset records.",
            inputs=["source-manifest.json", "teacher backend", "generation policy"],
            outputs=["dataset-records.jsonl"],
            status="scaffold_only",
            notes=["Keep teacher prompting and verifier logic project-local."],
        )
    )

    curate_path = script_dir / "03_curate_dataset.py"
    _write_python_scaffold(
        curate_path,
        "Curate generated supervision before training or evaluation.",
        [
            "    print('Scaffold: curate generated dataset records.')",
            "    print('Apply schema validation, deduplication, and heldout split protection.')",
            "    print(f'Write curated dataset or report to: {args.output}')",
        ],
    )
    script_plan.append(
        _script_step(
            script_id="curate_dataset",
            path=curate_path,
            script_kind="python",
            purpose="Validate, filter, and split generated data.",
            inputs=["dataset-records.jsonl", "quality policy"],
            outputs=["curated-dataset.jsonl", "dataset-qa-report.json"],
            status="scaffold_only",
            notes=["Quality gates should run before any training launcher."],
        )
    )

    if training_plan is not None:
        launch_path = script_dir / "04_launch_training.sh"
        candidates = training_plan.get("implementation_candidates", [])
        detected_training_surfaces = environment["discovered_surfaces"]["training_surfaces"]
        _write_shell_scaffold(
            launch_path,
            [
                "echo 'Scaffold: launch project-local training flow after environment review.'",
                f"echo 'Implementation candidates: {', '.join(candidates) if candidates else 'none declared'}'",
                f"echo 'Detected training surfaces: {len(detected_training_surfaces)}'",
                "echo 'Fill in the final launcher after selecting the project-local implementation path.'",
            ],
        )
        script_plan.append(
            _script_step(
                script_id="launch_training",
                path=launch_path,
                script_kind="shell",
                purpose="Launch the selected project-local training implementation.",
                inputs=["curated-dataset.jsonl", "selected implementation profile", "base model"],
                outputs=["checkpoints/", "training logs"],
                status="scaffold_only",
                notes=["Bundled launchers are optional implementation profiles, not the only valid path."],
            )
        )

    eval_path = script_dir / "05_run_evaluation.sh"
    _write_shell_scaffold(
        eval_path,
        [
            "echo 'Scaffold: run post-training or post-generation evaluation.'",
            "echo 'Use the evaluation artifact referenced by generated-script-plan.json.'",
        ],
    )
    script_plan.append(
        _script_step(
            script_id="run_evaluation",
            path=eval_path,
            script_kind="shell",
            purpose="Execute the agreed evaluation plan after data or training work.",
            inputs=["evaluation-plan.json", "model or generated outputs"],
            outputs=["evaluation-report.json"],
            status="scaffold_only",
            notes=["Use the existing project evaluator when one was discovered."],
        )
    )

    return script_plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit a generated script plan and project-local scaffold scripts.")
    parser.add_argument("--capability-intake", required=True, help="Path to capability-intake.json.")
    parser.add_argument("--evaluation-plan", required=True, help="Path to evaluation-plan.json.")
    parser.add_argument("--environment-discovery", required=True, help="Path to environment-discovery.json.")
    parser.add_argument("--training-plan", default="", help="Optional path to training-plan.json.")
    parser.add_argument("--output", required=True, help="Output path for generated-script-plan.json.")
    parser.add_argument(
        "--script-dir",
        default="",
        help="Optional directory where generated project-local scaffold scripts should be written.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    intake_path = Path(args.capability_intake)
    evaluation_path = Path(args.evaluation_plan)
    environment_path = Path(args.environment_discovery)
    training_path = Path(args.training_plan) if args.training_plan else None
    output_path = Path(args.output)
    script_dir = Path(args.script_dir) if args.script_dir else output_path.parent / "generated"

    intake = _load_contract(intake_path, "capability_intake")
    evaluation = _load_contract(evaluation_path, "evaluation_plan")
    environment = _load_contract(environment_path, "environment_discovery")
    training_plan = _load_contract(training_path, "training_plan") if training_path is not None else None

    dataset_strategy = _derive_dataset_strategy(
        intake=intake,
        evaluation=evaluation,
        environment=environment,
        training_plan=training_plan,
    )
    script_plan = _emit_scaffold_scripts(
        script_dir=script_dir,
        dataset_strategy=dataset_strategy,
        environment=environment,
        training_plan=training_plan,
    )

    unresolved_gaps = list(environment["unresolved_gaps"])
    if training_plan is None:
        unresolved_gaps.append("No training plan provided; generated scripts stop at scaffold selection.")
    assumptions = [
        "Generated scripts are project-local scaffolds, not proof of end-to-end execution readiness.",
        "Detected training or serving surfaces should be reviewed before wiring final launch commands.",
    ]

    payload = build_generated_script_plan_artifact(
        target_capability=intake["requested_capability"],
        plan_status="scaffold_only",
        selected_flow_kind=_choose_flow_kind(training_plan),
        capability_intake_reference=str(intake_path),
        evaluation_plan_reference=str(evaluation_path),
        environment_discovery_reference=str(environment_path),
        training_plan_reference=str(training_path) if training_path is not None else "",
        dataset_strategy=json.dumps(dataset_strategy, ensure_ascii=False),
        script_steps=[json.dumps(step, ensure_ascii=False) for step in script_plan],
        assumptions=assumptions,
        unresolved_gaps=unresolved_gaps,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated script plan written: {output_path}")
    print(f"Generated project-local scripts written under: {script_dir}")


if __name__ == "__main__":
    main()
