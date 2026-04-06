#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from lib.artifacts import build_teacher_loop_plan_artifact
from lib.parsing import clean
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


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = clean(value)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result


def _training_teacher_roles(training_plan: dict[str, Any] | None) -> list[str]:
    if training_plan is None:
        return []

    teacher_plan = training_plan.get("teacher_plan", {})
    roles: list[str] = []
    if isinstance(teacher_plan, dict):
        primary_role = clean(str(teacher_plan.get("teacher_role", "")))
        if primary_role:
            roles.append(primary_role)

    family = _normalize(str(training_plan.get("intervention_family", "")))
    supervision_shape = _normalize(str(training_plan.get("supervision_shape", "")))

    if "distill" in family or "distill" in supervision_shape:
        roles.append("distillation_teacher")
    elif "preference" in family or "preference" in supervision_shape:
        roles.append("preference_judge")
    elif "reward" in family:
        roles.append("process_reward_teacher")
    elif family:
        roles.append("demonstrator")

    return roles


def _probe_teacher_roles(probe_summary: dict[str, Any] | None) -> list[str]:
    if probe_summary is None:
        return []

    roles: list[str] = []
    recommended_roles = probe_summary.get("recommended_teacher_roles", [])
    if isinstance(recommended_roles, list):
        roles.extend(
            clean(str(value))
            for value in recommended_roles
            if isinstance(value, str) and clean(value)
        )

    weaknesses = probe_summary.get("weaknesses", [])
    if isinstance(weaknesses, list) and weaknesses:
        roles.append("critique_teacher")

    route_readiness = probe_summary.get("route_readiness", {})
    if isinstance(route_readiness, dict):
        status = _normalize(str(route_readiness.get("status", "")))
        if status in {"insufficient_evidence", "partial_baseline"}:
            roles.append("diagnostician")

    return roles


def _evaluation_roles(evaluation_plan: dict[str, Any]) -> list[str]:
    modes: list[str] = []
    primary_mode = clean(str(evaluation_plan.get("primary_evaluation_mode", "")))
    if primary_mode:
        modes.append(primary_mode)

    roles: list[str] = []
    normalized_modes = {_normalize(mode) for mode in modes}
    if {"verifier_based", "execution_based", "exact_match"} & normalized_modes:
        roles.append("verifier")
    if "teacher_review" in normalized_modes:
        roles.append("critique_teacher")
    return roles


def _selected_teacher_roles(
    *,
    evaluation_plan: dict[str, Any],
    probe_summary: dict[str, Any] | None,
    training_plan: dict[str, Any] | None,
) -> list[str]:
    roles = ["diagnostician"]
    roles.extend(_probe_teacher_roles(probe_summary))
    roles.extend(_training_teacher_roles(training_plan))
    roles.extend(_evaluation_roles(evaluation_plan))

    if not any(role in roles for role in ("demonstrator", "critique_teacher", "distillation_teacher")):
        roles.append("demonstrator")
    if probe_summary is not None:
        weak = probe_summary.get("weaknesses", [])
        if isinstance(weak, list) and weak and "verifier" not in roles:
            roles.append("verifier")

    return _unique(roles)


def _loop_steps(
    *,
    roles: list[str],
    probe_summary: dict[str, Any] | None,
    training_plan: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []

    if "diagnostician" in roles:
        steps.append(
            {
                "step_id": "diagnose",
                "teacher_role": "diagnostician",
                "purpose": "Identify the main failure mode and confirm whether the next loop should critique, demonstrate, distill, or defer.",
                "emits": ["failure_modes", "missing_skills", "confidence", "suggested_next_probes"],
            }
        )

    if "distillation_teacher" in roles:
        steps.append(
            {
                "step_id": "distill_target",
                "teacher_role": "distillation_teacher",
                "purpose": "Emit stronger teacher targets when the student baseline is too weak for critique-rewrite alone.",
                "emits": ["distilled_target", "salient_rationale", "teacher_confidence"],
            }
        )
    elif "critique_teacher" in roles:
        steps.append(
            {
                "step_id": "critique_and_rewrite",
                "teacher_role": "critique_teacher",
                "purpose": "Repair observed student failures and preserve mistake-aware supervision.",
                "emits": ["observed_defects", "rewrite_guidance", "corrected_output"],
            }
        )
    elif "demonstrator" in roles:
        steps.append(
            {
                "step_id": "demonstrate",
                "teacher_role": "demonstrator",
                "purpose": "Provide concise target behavior for direct supervised records.",
                "emits": ["prompt_or_task", "target_output", "style_or_policy_notes"],
            }
        )

    if "preference_judge" in roles:
        steps.append(
            {
                "step_id": "rank_candidates",
                "teacher_role": "preference_judge",
                "purpose": "Choose the better candidate when pairwise ranking is more stable than single gold targets.",
                "emits": ["chosen_candidate", "rejected_candidate", "comparison_basis", "confidence"],
            }
        )

    if "process_reward_teacher" in roles:
        steps.append(
            {
                "step_id": "label_process",
                "teacher_role": "process_reward_teacher",
                "purpose": "Label intermediate search or tool-use behavior when outcome-only supervision is insufficient.",
                "emits": ["step_level_critique", "approved_patterns", "terminal_summary"],
            }
        )

    if "verifier" in roles:
        steps.append(
            {
                "step_id": "verify",
                "teacher_role": "verifier",
                "purpose": "Confirm whether corrected or demonstrated outputs satisfy task constraints and acceptance checks.",
                "emits": ["verdict", "checks_run", "failed_checks", "confidence"],
            }
        )

    if not steps:
        # Defensive fallback; schema requires at least one step.
        steps.append(
            {
                "step_id": "bounded_diagnosis",
                "teacher_role": "diagnostician",
                "purpose": "Emit a bounded diagnosis because current evidence is insufficient for a richer teacher loop.",
                "emits": ["failure_modes", "confidence", "suggested_next_probes"],
            }
        )

    # If the training plan already fixed a primary teacher role, keep it visible in the loop.
    if training_plan is not None:
        teacher_plan = training_plan.get("teacher_plan", {})
        if isinstance(teacher_plan, dict):
            primary_role = clean(str(teacher_plan.get("teacher_role", "")))
            if primary_role and all(step["teacher_role"] != primary_role for step in steps):
                steps.insert(
                    min(1, len(steps)),
                    {
                        "step_id": "training_teacher",
                        "teacher_role": primary_role,
                        "purpose": "Honor the explicitly selected training teacher role from the training plan.",
                        "emits": ["role_specific_signal"],
                    },
                )

    return steps


def _loop_goal(target_capability: str, roles: list[str]) -> str:
    if "distillation_teacher" in roles:
        return f"Bootstrap a stronger teacher signal for {target_capability} before lower-capacity student supervision is exported."
    if "critique_teacher" in roles and "verifier" in roles:
        return f"Diagnose, repair, and verify outputs for {target_capability} before exporting training or evaluator records."
    if "demonstrator" in roles:
        return f"Produce bounded target behavior for {target_capability} and keep the resulting supervision export-friendly."
    return f"Bound the teacher strategy for {target_capability} without overclaiming training readiness."


def _input_artifacts(
    *,
    capability_intake_path: Path,
    evaluation_plan_path: Path,
    probe_summary_path: Path | None,
    training_plan_path: Path | None,
) -> list[str]:
    items = [str(capability_intake_path), str(evaluation_plan_path)]
    if probe_summary_path is not None:
        items.append(str(probe_summary_path))
    if training_plan_path is not None:
        items.append(str(training_plan_path))
    return items


def _output_artifacts(roles: list[str]) -> list[str]:
    outputs: list[str] = []
    if any(role in roles for role in ("demonstrator", "critique_teacher", "distillation_teacher", "preference_judge")):
        outputs.append("dataset-records.jsonl")
    if any(role in roles for role in ("verifier", "process_reward_teacher", "preference_judge")):
        outputs.append("evaluator-payloads.jsonl")
    if not outputs:
        outputs.append("teacher-loop-plan.json")
    return outputs


def _export_strategy(roles: list[str], training_plan: dict[str, Any] | None) -> dict[str, Any]:
    strategy: dict[str, Any] = {}
    if any(role in roles for role in ("demonstrator", "critique_teacher", "distillation_teacher")):
        strategy["dataset_record"] = "export bounded teacher supervision only when the emitted signal is concrete and confidence is sufficient"
    if "preference_judge" in roles:
        strategy["dataset_record_preference"] = "export pairwise chosen/rejected examples only when comparison_basis is explicit"
    if any(role in roles for role in ("verifier", "process_reward_teacher")):
        strategy["evaluator_payload"] = "export verifier checks or process labels separately from stylistic preference"

    if training_plan is not None:
        strategy["training_plan_alignment"] = {
            "intervention_family": clean(str(training_plan.get("intervention_family", ""))),
            "supervision_shape": clean(str(training_plan.get("supervision_shape", ""))),
        }
    return strategy or {"bounded_output": "emit only the teacher-loop plan until richer evidence exists"}


def _quality_gates(roles: list[str]) -> list[str]:
    gates = [
        "keep each teacher role explicit rather than merging diagnosis, correction, and verification into one opaque step",
        "do not export low-confidence teacher outputs as training data",
    ]
    if "critique_teacher" in roles:
        gates.append("keep critique and correction separated")
    if "verifier" in roles:
        gates.append("preserve verifier evidence and failed checks separately from stylistic preference")
    if "preference_judge" in roles:
        gates.append("require explicit comparison_basis before exporting preference pairs")
    if "distillation_teacher" in roles:
        gates.append("record that teacher targets are distilled rather than ground truth")
    return _unique(gates)


def _stop_conditions(
    *,
    probe_summary: dict[str, Any] | None,
    training_plan: dict[str, Any] | None,
) -> list[str]:
    conditions = [
        "stop if the teacher cannot emit a concrete role-specific signal",
        "stop if evidence is insufficient and the next step should be probe expansion rather than data export",
    ]

    if probe_summary is not None:
        readiness = probe_summary.get("route_readiness", {})
        if isinstance(readiness, dict):
            status = _normalize(str(readiness.get("status", "")))
            if status in {"insufficient_evidence", "partial_baseline"}:
                conditions.append("stop if baseline evidence remains incomplete after diagnosis")

    if training_plan is not None:
        family = _normalize(str(training_plan.get("intervention_family", "")))
        if family in {"model_replacement", "system_composition"}:
            conditions.append("stop if the correct next route is replacement or system composition rather than teacher-generated supervision")

    return _unique(conditions)


def _open_questions(
    *,
    probe_summary: dict[str, Any] | None,
    training_plan: dict[str, Any] | None,
) -> list[str]:
    questions: list[str] = []
    if probe_summary is None:
        questions.append("Whether the current teacher loop should stay diagnostic until baseline probe evidence exists.")
    if training_plan is None:
        questions.append("Whether downstream supervision should become SFT, preference, distillation, or remain bounded planning only.")
    else:
        family = clean(str(training_plan.get("intervention_family", "")))
        if family:
            questions.append(f"Whether the selected teacher loop is sufficiently aligned with the chosen intervention family: {family}.")
    return questions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit a conservative teacher-loop-plan artifact from existing route artifacts.")
    parser.add_argument("--capability-intake", required=True, help="Path to capability-intake.json.")
    parser.add_argument("--evaluation-plan", required=True, help="Path to evaluation-plan.json.")
    parser.add_argument("--output", required=True, help="Output path for teacher-loop-plan.json.")
    parser.add_argument("--probe-summary", default="", help="Optional path to probe-summary.json.")
    parser.add_argument("--training-plan", default="", help="Optional path to training-plan.json.")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    capability_intake_path = Path(args.capability_intake)
    evaluation_plan_path = Path(args.evaluation_plan)
    output_path = Path(args.output)
    probe_summary_path = Path(args.probe_summary) if args.probe_summary else None
    training_plan_path = Path(args.training_plan) if args.training_plan else None

    intake = _load_contract(capability_intake_path, "capability_intake")
    evaluation = _load_contract(evaluation_plan_path, "evaluation_plan")
    probe_summary = _load_contract(probe_summary_path, "probe_summary") if probe_summary_path is not None else None
    training_plan = _load_contract(training_plan_path, "training_plan") if training_plan_path is not None else None

    roles = _selected_teacher_roles(
        evaluation_plan=evaluation,
        probe_summary=probe_summary,
        training_plan=training_plan,
    )
    payload = build_teacher_loop_plan_artifact(
        target_capability=intake["requested_capability"],
        loop_goal=_loop_goal(intake["requested_capability"], roles),
        selected_teacher_roles=roles,
        loop_steps=[
            __import__("json").dumps(step, ensure_ascii=False)
            for step in _loop_steps(
                roles=roles,
                probe_summary=probe_summary,
                training_plan=training_plan,
            )
        ],
        input_artifacts=_input_artifacts(
            capability_intake_path=capability_intake_path,
            evaluation_plan_path=evaluation_plan_path,
            probe_summary_path=probe_summary_path,
            training_plan_path=training_plan_path,
        ),
        output_artifacts=_output_artifacts(roles),
        export_strategy=__import__("json").dumps(
            _export_strategy(roles, training_plan),
            ensure_ascii=False,
        ),
        quality_gates=_quality_gates(roles),
        stop_conditions=_stop_conditions(
            probe_summary=probe_summary,
            training_plan=training_plan,
        ),
        open_questions=_open_questions(
            probe_summary=probe_summary,
            training_plan=training_plan,
        ),
    )

    try:
        VALIDATORS["teacher_loop_plan"](payload)
    except ValidationError as exc:
        raise SystemExit(f"teacher_loop_plan failed validation: {exc}") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(__import__("json").dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Teacher loop plan written: {output_path}")


if __name__ == "__main__":
    main()
