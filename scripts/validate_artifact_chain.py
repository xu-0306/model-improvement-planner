#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from validate_contracts import VALIDATORS, ValidationError, load_json


NON_TRAINING_FAMILIES = {
    "explicit_deferral",
    "model_replacement",
    "prompt_and_control_interventions",
    "retrieval_and_external_knowledge_interventions",
    "runtime_and_serving_interventions",
    "system_composition",
}

EXECUTION_READY_STATUSES = {
    "execution_ready",
    "ready_for_execution",
    "ready",
    "execute",
    "approved_for_execution",
}
BLOCKED_STATUSES = {
    "defer",
    "deferred",
    "stop",
    "stopped",
    "blocked",
}


class ChainValidationError(ValueError):
    """Raised when artifact-chain checks fail."""


def _normalize(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _load_contract(path_value: str, contract: str) -> dict[str, Any]:
    payload = load_json(Path(path_value))
    try:
        VALIDATORS[contract](payload)
    except ValidationError as exc:
        raise ChainValidationError(f"{contract} artifact failed base validation: {exc}") from exc
    return payload


def _non_empty_list(payload: dict[str, Any], field_name: str, label: str) -> None:
    values = payload[field_name]
    if not values:
        raise ChainValidationError(f"{label} must not be empty")


def _require_same_target(expected: str, actual: str, label: str) -> None:
    if expected != actual:
        raise ChainValidationError(
            f"{label} target mismatch: expected {expected!r}, got {actual!r}"
        )


def _status_is_blocked(status: str) -> bool:
    return _normalize(status) in BLOCKED_STATUSES


def _status_is_execution_ready(status: str) -> bool:
    return _normalize(status) in EXECUTION_READY_STATUSES


def _require_reference_alignment(
    nested_evaluation: dict[str, Any],
    evaluation_path: Path,
    label: str,
) -> None:
    if not nested_evaluation:
        raise ChainValidationError(f"{label} evaluation_plan must not be empty")

    reference = nested_evaluation.get("reference_artifact")
    if reference is None:
        reference = nested_evaluation.get("artifact")
    if reference is None:
        raise ChainValidationError(
            f"{label} evaluation_plan must include reference_artifact or artifact"
        )
    if not isinstance(reference, str) or not reference.strip():
        raise ChainValidationError(
            f"{label} evaluation_plan reference must be a non-empty string"
        )
    if Path(reference).name != evaluation_path.name:
        raise ChainValidationError(
            f"{label} evaluation reference mismatch: expected basename {evaluation_path.name!r}, got {reference!r}"
        )


def _require_non_negative_verdict(verdict: str, label: str) -> None:
    normalized = _normalize(verdict)
    negative_tokens = (
        "not_suitable",
        "unsupported",
        "incompatible",
        "impossible",
        "not_supported",
        "not_viable",
    )
    if any(token in normalized for token in negative_tokens):
        raise ChainValidationError(f"{label} is negative for a continuing route: {verdict!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate cross-artifact consistency across capability-optimizer release artifacts."
    )
    parser.add_argument("--intake", required=True, help="Path to capability-intake JSON.")
    parser.add_argument("--evaluation", required=True, help="Path to evaluation-plan JSON.")
    parser.add_argument("--decision", help="Path to intervention-decision JSON.")
    parser.add_argument("--training", help="Path to training-plan JSON.")
    parser.add_argument("--system", help="Path to system-composition-plan JSON.")
    parser.add_argument("--research", help="Path to research-evidence JSON.")
    parser.add_argument("--environment-discovery", help="Optional path to environment-discovery JSON.")
    parser.add_argument("--tool-inventory", help="Optional path to tool-inventory JSON.")
    parser.add_argument("--probe-generation-plan", help="Optional path to probe-generation-plan JSON.")
    parser.add_argument("--teacher-loop-plan", help="Optional path to teacher-loop-plan JSON.")
    parser.add_argument("--generated-script-plan", help="Optional path to generated-script-plan JSON.")
    parser.add_argument("--model-profile", help="Optional path to local-model-profile JSON.")
    parser.add_argument("--probe-summary", help="Optional path to probe-summary JSON.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    failures: list[str] = []

    try:
        if args.training and args.system:
            raise ChainValidationError("Provide at most one route-plan artifact: --training or --system")

        intake = _load_contract(args.intake, "capability_intake")
        evaluation = _load_contract(args.evaluation, "evaluation_plan")
        decision = _load_contract(args.decision, "intervention_decision") if args.decision else None
        training = _load_contract(args.training, "training_plan") if args.training else None
        system = _load_contract(args.system, "system_composition_plan") if args.system else None
        research = _load_contract(args.research, "research_evidence") if args.research else None
        environment_discovery = (
            _load_contract(args.environment_discovery, "environment_discovery")
            if args.environment_discovery
            else None
        )
        tool_inventory = _load_contract(args.tool_inventory, "tool_inventory") if args.tool_inventory else None
        probe_generation_plan = (
            _load_contract(args.probe_generation_plan, "probe_generation_plan")
            if args.probe_generation_plan
            else None
        )
        teacher_loop_plan = (
            _load_contract(args.teacher_loop_plan, "teacher_loop_plan")
            if args.teacher_loop_plan
            else None
        )
        generated_script_plan = (
            _load_contract(args.generated_script_plan, "generated_script_plan")
            if args.generated_script_plan
            else None
        )
        model_profile = _load_contract(args.model_profile, "local_model_profile") if args.model_profile else None
        probe_summary = _load_contract(args.probe_summary, "probe_summary") if args.probe_summary else None

        target_capability = intake["requested_capability"]
        evaluation_path = Path(args.evaluation)

        _require_same_target(target_capability, evaluation["target_capability"], "evaluation_plan")
        _non_empty_list(intake, "sub_capabilities", "capability_intake.sub_capabilities")
        _non_empty_list(evaluation, "acceptance_criteria", "evaluation_plan.acceptance_criteria")

        if decision is not None:
            _require_same_target(target_capability, decision["target_capability"], "intervention_decision")
            _non_empty_list(decision, "problem_types", "intervention_decision.problem_types")
            _non_empty_list(
                decision,
                "rejected_alternatives",
                "intervention_decision.rejected_alternatives",
            )

        if training is not None:
            if decision is None:
                raise ChainValidationError("training_plan requires a matching intervention_decision artifact")
            _require_same_target(target_capability, training["target_capability"], "training_plan")
            if _status_is_blocked(decision["decision_status"]):
                raise ChainValidationError(
                    "training_plan cannot be paired with a blocked intervention_decision status"
                )

            chosen_family = _normalize(decision["chosen_intervention_family"])
            training_family = _normalize(training["intervention_family"])
            if chosen_family != training_family:
                raise ChainValidationError(
                    "training_plan.intervention_family must match intervention_decision.chosen_intervention_family"
                )
            if chosen_family in NON_TRAINING_FAMILIES:
                raise ChainValidationError(
                    "training_plan is incompatible with a non-training intervention family"
                )

            _non_empty_list(evaluation, "baseline_probes", "evaluation_plan.baseline_probes")
            _non_empty_list(evaluation, "heldout_evaluation", "evaluation_plan.heldout_evaluation")
            _non_empty_list(training, "stop_criteria", "training_plan.stop_criteria")
            _non_empty_list(training, "rollback_criteria", "training_plan.rollback_criteria")
            _require_reference_alignment(training["evaluation_plan"], evaluation_path, "training_plan")
            _require_non_negative_verdict(
                training["base_model_suitability_verdict"],
                "training_plan.base_model_suitability_verdict",
            )
            _require_non_negative_verdict(
                training["training_stack_suitability_verdict"],
                "training_plan.training_stack_suitability_verdict",
            )

        if system is not None:
            if decision is None:
                raise ChainValidationError(
                    "system_composition_plan requires a matching intervention_decision artifact"
                )
            _require_same_target(target_capability, system["target_capability"], "system_composition_plan")
            if _status_is_blocked(decision["decision_status"]):
                raise ChainValidationError(
                    "system_composition_plan cannot be paired with a blocked intervention_decision status"
                )

            chosen_family = _normalize(decision["chosen_intervention_family"])
            if chosen_family != "system_composition":
                raise ChainValidationError(
                    "system_composition_plan requires intervention_decision.chosen_intervention_family to be system_composition"
                )

            _non_empty_list(evaluation, "baseline_probes", "evaluation_plan.baseline_probes")
            _non_empty_list(system, "components", "system_composition_plan.components")
            _non_empty_list(system, "interfaces", "system_composition_plan.interfaces")
            _non_empty_list(system, "failure_handling", "system_composition_plan.failure_handling")
            _non_empty_list(
                system,
                "observability_requirements",
                "system_composition_plan.observability_requirements",
            )
            _require_reference_alignment(
                system["evaluation_plan"],
                evaluation_path,
                "system_composition_plan",
            )

        if research is not None:
            _require_same_target(target_capability, research["target_capability"], "research_evidence")
            if decision is not None and _status_is_execution_ready(decision["decision_status"]):
                if research["unresolved_facts"]:
                    raise ChainValidationError(
                        "research_evidence.unresolved_facts must be empty when intervention_decision is execution-ready"
                    )
                if research["unsupported_assumptions"]:
                    raise ChainValidationError(
                        "research_evidence.unsupported_assumptions must be empty when intervention_decision is execution-ready"
                    )

        if environment_discovery is not None:
            workspace_root = environment_discovery["workspace_root"]
            if not workspace_root:
                raise ChainValidationError("environment_discovery.workspace_root must be non-empty")

        if tool_inventory is not None:
            workspace_root = tool_inventory["workspace_root"]
            if not workspace_root:
                raise ChainValidationError("tool_inventory.workspace_root must be non-empty")
            if environment_discovery is not None and workspace_root != environment_discovery["workspace_root"]:
                raise ChainValidationError(
                    "tool_inventory.workspace_root must match environment_discovery.workspace_root"
                )
            _non_empty_list(tool_inventory, "skills", "tool_inventory.skills")
            _non_empty_list(tool_inventory, "runtimes", "tool_inventory.runtimes")
            _non_empty_list(
                tool_inventory,
                "recommended_usage_notes",
                "tool_inventory.recommended_usage_notes",
            )

        if probe_generation_plan is not None:
            _require_same_target(
                target_capability,
                probe_generation_plan["target_capability"],
                "probe_generation_plan",
            )
            _non_empty_list(
                probe_generation_plan,
                "probe_families",
                "probe_generation_plan.probe_families",
            )
            _non_empty_list(
                probe_generation_plan,
                "probe_blueprints",
                "probe_generation_plan.probe_blueprints",
            )
            _non_empty_list(
                probe_generation_plan,
                "acceptance_signals",
                "probe_generation_plan.acceptance_signals",
            )
            target_modalities = probe_generation_plan["target_modalities"]
            if not isinstance(target_modalities, dict):
                raise ChainValidationError("probe_generation_plan.target_modalities must be an object")
            planned_inputs = target_modalities.get("input", [])
            planned_outputs = target_modalities.get("output", [])
            if not isinstance(planned_inputs, list) or not planned_inputs:
                raise ChainValidationError("probe_generation_plan.target_modalities.input must be a non-empty array")
            if not isinstance(planned_outputs, list) or not planned_outputs:
                raise ChainValidationError("probe_generation_plan.target_modalities.output must be a non-empty array")
            for modality in intake["input_modalities"]:
                if modality not in planned_inputs:
                    raise ChainValidationError(
                        f"probe_generation_plan.target_modalities.input must include intake input modality {modality!r}"
                    )
            for modality in intake["output_modalities"]:
                if modality not in planned_outputs:
                    raise ChainValidationError(
                        f"probe_generation_plan.target_modalities.output must include intake output modality {modality!r}"
                    )

        if teacher_loop_plan is not None:
            _require_same_target(
                target_capability,
                teacher_loop_plan["target_capability"],
                "teacher_loop_plan",
            )
            _non_empty_list(
                teacher_loop_plan,
                "selected_teacher_roles",
                "teacher_loop_plan.selected_teacher_roles",
            )
            _non_empty_list(
                teacher_loop_plan,
                "quality_gates",
                "teacher_loop_plan.quality_gates",
            )
            if training is not None:
                teacher_role = training["teacher_plan"].get("teacher_role", "")
                if isinstance(teacher_role, str) and teacher_role.strip():
                    if teacher_role not in teacher_loop_plan["selected_teacher_roles"]:
                        raise ChainValidationError(
                            "teacher_loop_plan.selected_teacher_roles must include training_plan.teacher_plan.teacher_role"
                        )
            if probe_generation_plan is not None:
                shared_roles = set(teacher_loop_plan["selected_teacher_roles"]).intersection(
                    set(probe_generation_plan["teacher_roles"])
                )
                if not shared_roles:
                    raise ChainValidationError(
                        "teacher_loop_plan.selected_teacher_roles must overlap with probe_generation_plan.teacher_roles"
                    )

        if generated_script_plan is not None:
            _require_same_target(
                target_capability,
                generated_script_plan["target_capability"],
                "generated_script_plan",
            )
            if Path(generated_script_plan["capability_intake_reference"]).name != Path(args.intake).name:
                raise ChainValidationError(
                    "generated_script_plan.capability_intake_reference must align with the provided intake artifact"
                )
            if Path(generated_script_plan["evaluation_plan_reference"]).name != evaluation_path.name:
                raise ChainValidationError(
                    "generated_script_plan.evaluation_plan_reference must align with the provided evaluation artifact"
                )
            if environment_discovery is None:
                raise ChainValidationError(
                    "generated_script_plan requires a matching environment_discovery artifact"
                )
            if Path(generated_script_plan["environment_discovery_reference"]).name != Path(args.environment_discovery).name:
                raise ChainValidationError(
                    "generated_script_plan.environment_discovery_reference must align with the provided environment-discovery artifact"
                )
            training_reference = generated_script_plan.get("training_plan_reference", "")
            if training_reference:
                if training is None:
                    raise ChainValidationError(
                        "generated_script_plan.training_plan_reference requires a provided training artifact"
                    )
                if Path(training_reference).name != Path(args.training).name:
                    raise ChainValidationError(
                        "generated_script_plan.training_plan_reference must align with the provided training artifact"
                    )
            if training is not None and not training_reference:
                raise ChainValidationError(
                    "generated_script_plan must carry training_plan_reference when a training artifact is validated"
                )

        if probe_summary is not None:
            if model_profile is not None:
                reference = probe_summary.get("model_profile_reference", "")
                if isinstance(reference, str) and reference.strip():
                    if Path(reference).name != Path(args.model_profile).name:
                        raise ChainValidationError(
                            "probe_summary.model_profile_reference must align with the provided model-profile artifact"
                        )
            if training is not None or system is not None:
                if probe_summary["total_probes"] < 1:
                    raise ChainValidationError(
                        "probe_summary.total_probes must be >= 1 when validating an execution route"
                    )
                if probe_summary["answered_probes"] < 1:
                    raise ChainValidationError(
                        "probe_summary.answered_probes must be >= 1 when validating an execution route"
                    )

        print(
            "artifact chain validation passed:"
            f" intake={args.intake}, evaluation={args.evaluation},"
            f" decision={args.decision or '-'}, training={args.training or '-'},"
            f" system={args.system or '-'}, research={args.research or '-'},"
            f" environment_discovery={args.environment_discovery or '-'},"
            f" tool_inventory={args.tool_inventory or '-'},"
            f" probe_generation_plan={args.probe_generation_plan or '-'},"
            f" teacher_loop_plan={args.teacher_loop_plan or '-'},"
            f" generated_script_plan={args.generated_script_plan or '-'},"
            f" model_profile={args.model_profile or '-'}, probe_summary={args.probe_summary or '-'}"
        )
    except ChainValidationError as exc:
        failures.append(str(exc))

    if failures:
        formatted = "\n".join(f"- {item}" for item in failures)
        raise SystemExit(f"artifact chain validation failed:\n{formatted}")


if __name__ == "__main__":
    main()
