#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from lib.artifacts import (
    build_capability_intake_artifact,
    build_dataset_record_artifact,
    build_environment_discovery_artifact,
    build_evaluation_plan_artifact,
    build_evaluator_payload_artifact,
    build_generated_script_plan_artifact,
    build_intervention_decision_artifact,
    build_model_discovery_artifact,
    build_probe_generation_plan_artifact,
    build_research_evidence_artifact,
    build_system_composition_plan_artifact,
    build_teacher_loop_plan_artifact,
    build_tool_inventory_artifact,
    build_training_plan_artifact,
)
from lib.parsing import write_json


def add_capability_intake_arguments(
    parser: argparse.ArgumentParser,
    *,
    output_required: bool,
    include_requested_capability: bool,
) -> None:
    if output_required:
        parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    if include_requested_capability:
        parser.add_argument("--requested-capability", required=True, help="Normalized requested capability.")
    parser.add_argument("--user-intent", required=True, help="User intent such as planning or execution.")
    parser.add_argument(
        "--deployment-context",
        default="{}",
        help="JSON object or plain string describing the deployment context.",
    )
    parser.add_argument(
        "--constraints",
        default="{}",
        help="JSON object describing constraints such as hardware, policy, or latency.",
    )
    parser.add_argument("--desired-outcome", action="append", default=[], help="Desired outcome. Repeat as needed.")
    parser.add_argument("--failure-mode", action="append", default=[], help="Failure mode to avoid. Repeat as needed.")
    parser.add_argument("--success-criterion", action="append", default=[], help="Success criterion. Repeat as needed.")
    parser.add_argument("--input-modality", action="append", default=[], help="Input modality. Repeat as needed.")
    parser.add_argument("--output-modality", action="append", default=[], help="Output modality. Repeat as needed.")
    parser.add_argument("--sub-capability", action="append", default=[], help="Sub-capability. Repeat as needed.")
    parser.add_argument(
        "--external-dependency",
        action="append",
        default=[],
        help="External dependency. Repeat as needed.",
    )
    parser.add_argument("--missing-fact", action="append", default=[], help="Missing fact. Repeat as needed.")


def add_evaluation_plan_arguments(
    parser: argparse.ArgumentParser,
    *,
    output_required: bool,
    include_target_capability: bool,
) -> None:
    if output_required:
        parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    if include_target_capability:
        parser.add_argument("--target-capability", required=True, help="Target capability under evaluation.")
    parser.add_argument("--primary-evaluation-mode", required=True, help="Primary evaluation mode.")
    parser.add_argument("--baseline-probe", action="append", default=[], help="Baseline probe. Repeat as needed.")
    parser.add_argument(
        "--heldout-evaluation",
        action="append",
        default=[],
        help="Held-out evaluation item. Repeat as needed.",
    )
    parser.add_argument("--success-metric", action="append", default=[], help="Success metric. Repeat as needed.")
    parser.add_argument(
        "--acceptance-criterion",
        action="append",
        default=[],
        help="Acceptance criterion. Repeat as needed.",
    )
    parser.add_argument("--regression-check", action="append", default=[], help="Regression check. Repeat as needed.")
    parser.add_argument("--unresolved-risk", action="append", default=[], help="Unresolved risk. Repeat as needed.")
    parser.add_argument("--stop-condition", action="append", default=[], help="Stop condition. Repeat as needed.")


def add_model_discovery_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    parser.add_argument("--runtime-id", required=True, help="Requested runtime identifier.")
    parser.add_argument("--model-family", default="", help="Model family or architecture hint.")
    parser.add_argument("--weight-format", default="", help="Checkpoint or weight format.")
    parser.add_argument("--tokenizer-format", default="", help="Tokenizer format.")
    parser.add_argument("--expected-load-path", default="", help="Expected model load path or loading pattern.")
    parser.add_argument("--inference-library", default="", help="Likely inference library.")
    parser.add_argument("--training-library-status", default="", help="Likely training library or unsupported status.")
    parser.add_argument("--inference-stack", default="", help="Deprecated alias for --inference-library.")
    parser.add_argument("--training-stack", default="", help="Deprecated alias for --training-library-status.")
    parser.add_argument("--device-assumption", action="append", default=[], help="Device assumption. Repeat as needed.")
    parser.add_argument("--runtime-constraint", action="append", default=[], help="Runtime constraint. Repeat as needed.")
    parser.add_argument("--missing-fact", action="append", default=[], help="Missing fact. Repeat as needed.")


def add_environment_discovery_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    parser.add_argument("--workspace-root", required=True, help="Root directory that was inspected.")
    parser.add_argument("--package-manager", action="append", default=[], help="Package manager hint. Repeat as needed.")
    parser.add_argument("--framework-hint", action="append", default=[], help="Framework hint. Repeat as needed.")
    parser.add_argument("--available-runtime", action="append", default=[], help="Runtime hint. Repeat as needed.")
    parser.add_argument(
        "--source-access-pattern",
        action="append",
        default=[],
        help="Allowed source-access pattern. Repeat as needed.",
    )
    parser.add_argument("--dependency-file", action="append", default=[], help="Dependency file. Repeat as needed.")
    parser.add_argument("--training-surface", action="append", default=[], help="Training surface. Repeat as needed.")
    parser.add_argument("--serving-surface", action="append", default=[], help="Serving surface. Repeat as needed.")
    parser.add_argument("--dataset-surface", action="append", default=[], help="Dataset surface. Repeat as needed.")
    parser.add_argument("--evaluation-surface", action="append", default=[], help="Evaluation surface. Repeat as needed.")
    parser.add_argument("--constraint", action="append", default=[], help="Constraint. Repeat as needed.")
    parser.add_argument("--unresolved-gap", action="append", default=[], help="Unresolved gap. Repeat as needed.")
    parser.add_argument("--note", action="append", default=[], help="Note. Repeat as needed.")


def add_intervention_decision_arguments(
    parser: argparse.ArgumentParser,
    *,
    output_required: bool,
    include_target_capability: bool,
) -> None:
    if output_required:
        parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    if include_target_capability:
        parser.add_argument("--target-capability", required=True, help="Target capability under decision.")
    parser.add_argument("--chosen-intervention-family", required=True, help="Chosen intervention family.")
    parser.add_argument("--implementation-direction", required=True, help="Concrete implementation direction.")
    parser.add_argument("--decision-status", required=True, help="Decision status such as continue, stop, or defer.")
    parser.add_argument("--decision-summary", required=True, help="Short decision summary.")
    parser.add_argument("--stop-or-continue-reason", required=True, help="Concrete execution-boundary reason.")
    parser.add_argument("--problem-type", action="append", default=[], help="Problem type. Repeat as needed.")
    parser.add_argument("--evidence-basis", action="append", default=[], help="Evidence basis. Repeat as needed.")
    parser.add_argument(
        "--decision-rejected-alternative",
        "--rejected-alternative",
        dest="rejected_alternative",
        action="append",
        default=[],
        help="Rejected alternative. Repeat as needed.",
    )
    parser.add_argument("--key-risk", action="append", default=[], help="Key risk. Repeat as needed.")
    parser.add_argument("--next-action", action="append", default=[], help="Next action. Repeat as needed.")


def add_research_evidence_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    parser.add_argument("--target-capability", required=True, help="Target capability being researched.")
    parser.add_argument("--research-scope", required=True, help="Research scope or question.")
    parser.add_argument("--source", action="append", default=[], help="Source item. Repeat as needed.")
    parser.add_argument("--confirmed-fact", action="append", default=[], help="Confirmed fact. Repeat as needed.")
    parser.add_argument("--unresolved-fact", action="append", default=[], help="Unresolved fact. Repeat as needed.")
    parser.add_argument("--route-implication", action="append", default=[], help="Route implication. Repeat as needed.")
    parser.add_argument(
        "--unsupported-assumption",
        action="append",
        default=[],
        help="Unsupported assumption. Repeat as needed.",
    )
    parser.add_argument(
        "--recommended-followup",
        action="append",
        default=[],
        help="Recommended followup. Repeat as needed.",
    )


def add_tool_inventory_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    parser.add_argument("--inventory-scope", required=True, help="Inventory scope such as current_session.")
    parser.add_argument("--workspace-root", required=True, help="Workspace root associated with the inventory.")
    parser.add_argument("--skill", action="append", default=[], help="Skill item as plain string or JSON object.")
    parser.add_argument(
        "--mcp-server",
        action="append",
        default=[],
        help="MCP server item as plain string or JSON object.",
    )
    parser.add_argument(
        "--mcp-resource",
        action="append",
        default=[],
        help="MCP resource item as plain string or JSON object.",
    )
    parser.add_argument(
        "--local-script",
        action="append",
        default=[],
        help="Local script item as plain string or JSON object.",
    )
    parser.add_argument("--runtime", action="append", default=[], help="Runtime item as plain string or JSON object.")
    parser.add_argument("--backend-adapter", action="append", default=[], help="Backend adapter. Repeat as needed.")
    parser.add_argument(
        "--network-capability",
        action="append",
        default=[],
        help="Network capability. Repeat as needed.",
    )
    parser.add_argument("--constraint", action="append", default=[], help="Constraint. Repeat as needed.")
    parser.add_argument(
        "--recommended-usage-note",
        action="append",
        default=[],
        help="Recommended usage note. Repeat as needed.",
    )


def add_probe_generation_plan_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    parser.add_argument("--target-capability", required=True, help="Target capability under planning.")
    parser.add_argument("--planning-scope", required=True, help="Planning scope such as initial_baseline.")
    parser.add_argument("--probe-family", action="append", default=[], help="Probe family. Repeat as needed.")
    parser.add_argument(
        "--generation-rationale",
        action="append",
        default=[],
        help="Generation rationale. Repeat as needed.",
    )
    parser.add_argument("--teacher-role", action="append", default=[], help="Teacher role. Repeat as needed.")
    parser.add_argument(
        "--evaluation-mode",
        action="append",
        default=[],
        help="Evaluation mode. Repeat as needed.",
    )
    parser.add_argument("--input-modality", action="append", default=[], help="Input modality. Repeat as needed.")
    parser.add_argument("--output-modality", action="append", default=[], help="Output modality. Repeat as needed.")
    parser.add_argument("--target-language", action="append", default=[], help="Target language. Repeat as needed.")
    parser.add_argument(
        "--probe-blueprint",
        action="append",
        default=[],
        help="Probe blueprint as plain string or JSON object. Repeat as needed.",
    )
    parser.add_argument(
        "--acceptance-signal",
        action="append",
        default=[],
        help="Acceptance signal. Repeat as needed.",
    )
    parser.add_argument(
        "--known-limitation",
        action="append",
        default=[],
        help="Known limitation. Repeat as needed.",
    )


def add_teacher_loop_plan_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    parser.add_argument("--target-capability", required=True, help="Target capability served by the loop.")
    parser.add_argument("--loop-goal", required=True, help="Goal of the teacher loop.")
    parser.add_argument(
        "--selected-teacher-role",
        action="append",
        default=[],
        help="Selected teacher role. Repeat as needed.",
    )
    parser.add_argument(
        "--loop-step",
        action="append",
        default=[],
        help="Loop step as JSON object. Repeat as needed.",
    )
    parser.add_argument("--input-artifact", action="append", default=[], help="Input artifact. Repeat as needed.")
    parser.add_argument("--output-artifact", action="append", default=[], help="Output artifact. Repeat as needed.")
    parser.add_argument("--export-strategy", required=True, help="JSON object describing export strategy.")
    parser.add_argument("--quality-gate", action="append", default=[], help="Quality gate. Repeat as needed.")
    parser.add_argument("--stop-condition", action="append", default=[], help="Stop condition. Repeat as needed.")
    parser.add_argument("--open-question", action="append", default=[], help="Open question. Repeat as needed.")


def add_training_plan_arguments(
    parser: argparse.ArgumentParser,
    *,
    output_required: bool,
    include_target_capability: bool,
    intervention_family_arg: str,
    intervention_family_dest: str,
    rejected_alternative_arg: str,
    rejected_alternative_dest: str,
) -> None:
    if output_required:
        parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    if include_target_capability:
        parser.add_argument("--target-capability", required=True, help="Target capability.")
    parser.add_argument(
        intervention_family_arg,
        dest=intervention_family_dest,
        required=True,
        help="Intervention family.",
    )
    parser.add_argument("--supervision-shape", required=True, help="Supervision shape.")
    parser.add_argument("--base-model-suitability-verdict", required=True, help="Base-model suitability verdict.")
    parser.add_argument(
        "--training-stack-suitability-verdict",
        required=True,
        help="Training-stack suitability verdict.",
    )
    parser.add_argument("--teacher-plan", required=True, help="JSON object describing the teacher plan.")
    parser.add_argument("--data-plan", required=True, help="JSON object describing the data plan.")
    parser.add_argument("--evaluation-plan", required=True, help="JSON object describing the evaluation-plan reference.")
    parser.add_argument(
        "--implementation-candidate",
        action="append",
        default=[],
        help="Implementation candidate. Repeat as needed.",
    )
    parser.add_argument(
        rejected_alternative_arg,
        dest=rejected_alternative_dest,
        action="append",
        default=[],
        help="Rejected alternative. Repeat as needed.",
    )
    parser.add_argument(
        "--serving-compatibility-note",
        action="append",
        default=[],
        help="Serving compatibility note. Repeat as needed.",
    )
    parser.add_argument("--compute-assumption", action="append", default=[], help="Compute assumption. Repeat as needed.")
    parser.add_argument("--stop-criterion", action="append", default=[], help="Stop criterion. Repeat as needed.")
    parser.add_argument("--rollback-criterion", action="append", default=[], help="Rollback criterion. Repeat as needed.")
    parser.add_argument(
        "--expected-failure-mode",
        action="append",
        default=[],
        help="Expected failure mode. Repeat as needed.",
    )


def add_system_plan_arguments(
    parser: argparse.ArgumentParser,
    *,
    output_required: bool,
    include_target_capability: bool,
) -> None:
    if output_required:
        parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    if include_target_capability:
        parser.add_argument("--target-capability", required=True, help="Target capability.")
    parser.add_argument("--system-goal", required=True, help="System goal.")
    parser.add_argument("--architecture-summary", required=True, help="Architecture summary.")
    parser.add_argument("--orchestration-summary", required=True, help="Orchestration summary.")
    parser.add_argument("--evaluation-plan", required=True, help="JSON object describing the evaluation-plan reference.")
    parser.add_argument("--component", action="append", default=[], help="Component as plain string or JSON object.")
    parser.add_argument("--interface", action="append", default=[], help="Interface as plain string or JSON object.")
    parser.add_argument("--latency-implication", action="append", default=[], help="Latency implication. Repeat as needed.")
    parser.add_argument("--failure-handling", action="append", default=[], help="Failure handling step. Repeat as needed.")
    parser.add_argument(
        "--observability-requirement",
        action="append",
        default=[],
        help="Observability requirement. Repeat as needed.",
    )
    parser.add_argument("--unresolved-gap", action="append", default=[], help="Unresolved gap. Repeat as needed.")


def add_dataset_record_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    parser.add_argument("--input", required=True, help="Input as plain string, JSON object, or JSON array.")
    parser.add_argument("--target", default="", help="Optional target as plain string, JSON object, or JSON array.")
    parser.add_argument(
        "--candidate",
        action="append",
        default=[],
        help="Optional candidate as plain string, JSON object, or JSON array. Repeat as needed.",
    )
    parser.add_argument("--supervision", default="", help="Optional JSON object describing supervision.")
    parser.add_argument(
        "--evidence",
        default="",
        help="Optional evidence as plain string, JSON object, or JSON array.",
    )
    parser.add_argument("--dataset-mode", required=True, help="Dataset mode such as direct_answer or preference_pair.")
    parser.add_argument("--capability-family", required=True, help="Capability family label.")
    parser.add_argument("--supervision-shape", required=True, help="Supervision shape label.")
    parser.add_argument("--teacher-role", action="append", default=[], help="Teacher role. Repeat as needed.")
    parser.add_argument(
        "--source-provenance",
        required=True,
        help="Source provenance as plain string, JSON object, or JSON array.",
    )
    parser.add_argument("--evaluator-id", default="", help="Optional evaluator identifier.")
    parser.add_argument("--rubric-reference", default="", help="Optional rubric reference.")
    parser.add_argument("--difficulty", default="", help="Optional difficulty as string or number.")
    parser.add_argument("--confidence", default="", help="Optional confidence in the range [0, 1].")


def add_evaluator_payload_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    parser.add_argument("--subject", required=True, help="Subject as plain string, JSON object, or JSON array.")
    parser.add_argument("--evaluation", default="", help="Optional evaluation JSON object.")
    parser.add_argument("--evaluation-mode", default="", help="Evaluation mode when --evaluation is not provided.")
    parser.add_argument(
        "--evaluation-summary",
        "--summary",
        dest="evaluation_summary",
        default="",
        help="Evaluation summary when --evaluation is not provided.",
    )
    parser.add_argument("--score", default="", help="Optional numeric score.")
    parser.add_argument("--is-correct", default="", help="Optional boolean string: true or false.")
    parser.add_argument(
        "--chosen-candidate",
        default="",
        help="Optional chosen candidate as plain string, JSON object, or JSON array.",
    )
    parser.add_argument(
        "--rejected-candidate",
        default="",
        help="Optional rejected candidate as plain string, JSON object, or JSON array.",
    )
    parser.add_argument(
        "--binary-label",
        default="",
        help="Optional binary label as plain string, JSON object, or JSON array.",
    )
    parser.add_argument("--scalar-reward", default="", help="Optional numeric scalar reward.")
    parser.add_argument("--verifier-status", default="", help="Optional verifier status.")
    parser.add_argument(
        "--process-label",
        default="",
        help="Optional process label as plain string, JSON object, or JSON array.",
    )
    parser.add_argument("--mastery-delta", default="", help="Optional numeric mastery delta.")
    parser.add_argument("--rationale", default="", help="Optional rationale string.")
    parser.add_argument(
        "--signal",
        action="append",
        default=[],
        help="Signal as plain string or JSON object. Repeat as needed.",
    )
    parser.add_argument("--artifacts", default="{}", help="JSON object describing produced artifacts.")
    parser.add_argument("--teacher-feedback", default="", help="Optional teacher feedback.")
    parser.add_argument(
        "--teacher-correction",
        default="",
        help="Optional teacher correction as plain string, JSON object, or JSON array.",
    )
    parser.add_argument(
        "--mistake-classification",
        default="",
        help="Optional mistake classification as plain string, JSON object, or JSON array.",
    )
    parser.add_argument("--advance", default="", help="Optional boolean string: true or false.")
    parser.add_argument("--confidence", default="", help="Optional confidence in the range [0, 1].")


def add_generated_script_plan_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, help="Path to the JSON artifact to write.")
    parser.add_argument("--target-capability", required=True, help="Target capability.")
    parser.add_argument("--plan-status", required=True, help="Plan status such as scaffold_only or ready_for_review.")
    parser.add_argument("--selected-flow-kind", required=True, help="Selected flow kind.")
    parser.add_argument("--capability-intake-reference", required=True, help="Reference path to capability-intake.json.")
    parser.add_argument("--evaluation-plan-reference", required=True, help="Reference path to evaluation-plan.json.")
    parser.add_argument(
        "--environment-discovery-reference",
        required=True,
        help="Reference path to environment-discovery.json.",
    )
    parser.add_argument("--training-plan-reference", default="", help="Optional reference path to training-plan.json.")
    parser.add_argument("--dataset-strategy", required=True, help="JSON object describing dataset strategy.")
    parser.add_argument(
        "--script-step",
        action="append",
        default=[],
        help="Script plan step as plain string or JSON object. Repeat as needed.",
    )
    parser.add_argument("--assumption", action="append", default=[], help="Assumption. Repeat as needed.")
    parser.add_argument("--unresolved-gap", action="append", default=[], help="Unresolved gap. Repeat as needed.")


def handle_write_capability_intake(args: argparse.Namespace) -> int:
    payload = build_capability_intake_artifact(
        requested_capability=args.requested_capability,
        user_intent=args.user_intent,
        deployment_context=args.deployment_context,
        constraints=args.constraints,
        desired_outcomes=args.desired_outcome,
        failure_modes=args.failure_mode,
        success_criteria=args.success_criterion,
        input_modalities=args.input_modality,
        output_modalities=args.output_modality,
        sub_capabilities=args.sub_capability,
        external_dependencies=args.external_dependency,
        missing_facts=args.missing_fact,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_evaluation_plan(args: argparse.Namespace) -> int:
    payload = build_evaluation_plan_artifact(
        target_capability=args.target_capability,
        primary_evaluation_mode=args.primary_evaluation_mode,
        baseline_probes=args.baseline_probe,
        heldout_evaluation=args.heldout_evaluation,
        success_metrics=args.success_metric,
        acceptance_criteria=args.acceptance_criterion,
        regression_checks=args.regression_check,
        unresolved_risks=args.unresolved_risk,
        stop_conditions=args.stop_condition,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_model_discovery(args: argparse.Namespace) -> int:
    payload = build_model_discovery_artifact(
        runtime_id=args.runtime_id,
        model_family=args.model_family,
        weight_format=args.weight_format,
        tokenizer_format=args.tokenizer_format,
        expected_load_path=args.expected_load_path,
        inference_library=args.inference_library,
        training_library_status=args.training_library_status,
        inference_stack=args.inference_stack,
        training_stack=args.training_stack,
        device_assumptions=args.device_assumption,
        runtime_constraints=args.runtime_constraint,
        missing_facts=args.missing_fact,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_environment_discovery(args: argparse.Namespace) -> int:
    payload = build_environment_discovery_artifact(
        workspace_root=args.workspace_root,
        package_managers=args.package_manager,
        framework_hints=args.framework_hint,
        available_runtimes=args.available_runtime,
        source_access_patterns=args.source_access_pattern,
        dependency_files=args.dependency_file,
        training_surfaces=args.training_surface,
        serving_surfaces=args.serving_surface,
        dataset_surfaces=args.dataset_surface,
        evaluation_surfaces=args.evaluation_surface,
        constraints=args.constraint,
        unresolved_gaps=args.unresolved_gap,
        notes=args.note,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_intervention_decision(args: argparse.Namespace) -> int:
    payload = build_intervention_decision_artifact(
        target_capability=args.target_capability,
        chosen_intervention_family=args.chosen_intervention_family,
        implementation_direction=args.implementation_direction,
        decision_status=args.decision_status,
        decision_summary=args.decision_summary,
        stop_or_continue_reason=args.stop_or_continue_reason,
        problem_types=args.problem_type,
        evidence_basis=args.evidence_basis,
        rejected_alternatives=args.rejected_alternative,
        key_risks=args.key_risk,
        next_actions=args.next_action,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_research_evidence(args: argparse.Namespace) -> int:
    payload = build_research_evidence_artifact(
        target_capability=args.target_capability,
        research_scope=args.research_scope,
        sources=args.source,
        confirmed_facts=args.confirmed_fact,
        unresolved_facts=args.unresolved_fact,
        route_implications=args.route_implication,
        unsupported_assumptions=args.unsupported_assumption,
        recommended_followups=args.recommended_followup,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_tool_inventory(args: argparse.Namespace) -> int:
    payload = build_tool_inventory_artifact(
        inventory_scope=args.inventory_scope,
        workspace_root=args.workspace_root,
        skills=args.skill,
        mcp_servers=args.mcp_server,
        mcp_resources=args.mcp_resource,
        local_scripts=args.local_script,
        runtimes=args.runtime,
        backend_adapters=args.backend_adapter,
        network_capabilities=args.network_capability,
        constraints=args.constraint,
        recommended_usage_notes=args.recommended_usage_note,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_probe_generation_plan(args: argparse.Namespace) -> int:
    payload = build_probe_generation_plan_artifact(
        target_capability=args.target_capability,
        planning_scope=args.planning_scope,
        probe_families=args.probe_family,
        generation_rationale=args.generation_rationale,
        teacher_roles=args.teacher_role,
        evaluation_modes=args.evaluation_mode,
        input_modalities=args.input_modality,
        output_modalities=args.output_modality,
        target_languages=args.target_language,
        probe_blueprints=args.probe_blueprint,
        acceptance_signals=args.acceptance_signal,
        known_limitations=args.known_limitation,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_teacher_loop_plan(args: argparse.Namespace) -> int:
    payload = build_teacher_loop_plan_artifact(
        target_capability=args.target_capability,
        loop_goal=args.loop_goal,
        selected_teacher_roles=args.selected_teacher_role,
        loop_steps=args.loop_step,
        input_artifacts=args.input_artifact,
        output_artifacts=args.output_artifact,
        export_strategy=args.export_strategy,
        quality_gates=args.quality_gate,
        stop_conditions=args.stop_condition,
        open_questions=args.open_question,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_training_plan(args: argparse.Namespace) -> int:
    payload = build_training_plan_artifact(
        target_capability=args.target_capability,
        intervention_family=args.intervention_family,
        supervision_shape=args.supervision_shape,
        base_model_suitability_verdict=args.base_model_suitability_verdict,
        training_stack_suitability_verdict=args.training_stack_suitability_verdict,
        teacher_plan=args.teacher_plan,
        data_plan=args.data_plan,
        evaluation_plan=args.evaluation_plan,
        implementation_candidates=args.implementation_candidate,
        rejected_alternatives=args.rejected_alternative,
        serving_compatibility_notes=args.serving_compatibility_note,
        compute_assumptions=args.compute_assumption,
        stop_criteria=args.stop_criterion,
        rollback_criteria=args.rollback_criterion,
        expected_failure_modes=args.expected_failure_mode,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_system_plan(args: argparse.Namespace) -> int:
    payload = build_system_composition_plan_artifact(
        target_capability=args.target_capability,
        system_goal=args.system_goal,
        architecture_summary=args.architecture_summary,
        orchestration_summary=args.orchestration_summary,
        evaluation_plan=args.evaluation_plan,
        components=args.component,
        interfaces=args.interface,
        latency_implications=args.latency_implication,
        failure_handling=args.failure_handling,
        observability_requirements=args.observability_requirement,
        unresolved_gaps=args.unresolved_gap,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_dataset_record(args: argparse.Namespace) -> int:
    payload = build_dataset_record_artifact(
        input_value=args.input,
        target_value=args.target,
        candidates=args.candidate,
        supervision=args.supervision,
        evidence=args.evidence,
        dataset_mode=args.dataset_mode,
        capability_family=args.capability_family,
        supervision_shape=args.supervision_shape,
        teacher_roles=args.teacher_role,
        source_provenance=args.source_provenance,
        evaluator_id=args.evaluator_id,
        rubric_reference=args.rubric_reference,
        difficulty=args.difficulty,
        confidence=args.confidence,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_evaluator_payload(args: argparse.Namespace) -> int:
    payload = build_evaluator_payload_artifact(
        subject=args.subject,
        evaluation=args.evaluation,
        evaluation_mode=args.evaluation_mode,
        evaluation_summary=args.evaluation_summary,
        score=args.score,
        is_correct=args.is_correct,
        chosen_candidate=args.chosen_candidate,
        rejected_candidate=args.rejected_candidate,
        binary_label=args.binary_label,
        scalar_reward=args.scalar_reward,
        verifier_status=args.verifier_status,
        process_label=args.process_label,
        mastery_delta=args.mastery_delta,
        rationale=args.rationale,
        signals=args.signal,
        artifacts=args.artifacts,
        teacher_feedback=args.teacher_feedback,
        teacher_correction=args.teacher_correction,
        mistake_classification=args.mistake_classification,
        advance=args.advance,
        confidence=args.confidence,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_write_generated_script_plan(args: argparse.Namespace) -> int:
    payload = build_generated_script_plan_artifact(
        target_capability=args.target_capability,
        plan_status=args.plan_status,
        selected_flow_kind=args.selected_flow_kind,
        capability_intake_reference=args.capability_intake_reference,
        evaluation_plan_reference=args.evaluation_plan_reference,
        environment_discovery_reference=args.environment_discovery_reference,
        training_plan_reference=args.training_plan_reference,
        dataset_strategy=args.dataset_strategy,
        script_steps=args.script_step,
        assumptions=args.assumption,
        unresolved_gaps=args.unresolved_gap,
    )
    write_json(Path(args.output), payload)
    return 0


def handle_bundle_bootstrap(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    intake_payload = build_capability_intake_artifact(
        requested_capability=args.target_capability,
        user_intent=args.user_intent,
        deployment_context=args.deployment_context,
        constraints=args.constraints,
        desired_outcomes=args.desired_outcome,
        failure_modes=args.failure_mode,
        success_criteria=args.success_criterion,
        input_modalities=args.input_modality,
        output_modalities=args.output_modality,
        sub_capabilities=args.sub_capability,
        external_dependencies=args.external_dependency,
        missing_facts=args.missing_fact,
    )
    evaluation_payload = build_evaluation_plan_artifact(
        target_capability=args.target_capability,
        primary_evaluation_mode=args.primary_evaluation_mode,
        baseline_probes=args.baseline_probe,
        heldout_evaluation=args.heldout_evaluation,
        success_metrics=args.success_metric,
        acceptance_criteria=args.acceptance_criterion,
        regression_checks=args.regression_check,
        unresolved_risks=args.unresolved_risk,
        stop_conditions=args.stop_condition,
    )
    write_json(output_dir / "capability-intake.json", intake_payload)
    write_json(output_dir / "evaluation-plan.json", evaluation_payload)
    return 0


def handle_bundle_training_route(args: argparse.Namespace) -> int:
    decision_payload = build_intervention_decision_artifact(
        target_capability=args.target_capability,
        chosen_intervention_family=args.chosen_intervention_family,
        implementation_direction=args.implementation_direction,
        decision_status=args.decision_status,
        decision_summary=args.decision_summary,
        stop_or_continue_reason=args.stop_or_continue_reason,
        problem_types=args.problem_type,
        evidence_basis=args.evidence_basis,
        rejected_alternatives=args.rejected_alternative,
        key_risks=args.key_risk,
        next_actions=args.next_action,
    )
    training_payload = build_training_plan_artifact(
        target_capability=args.target_capability,
        intervention_family=args.training_intervention_family,
        supervision_shape=args.supervision_shape,
        base_model_suitability_verdict=args.base_model_suitability_verdict,
        training_stack_suitability_verdict=args.training_stack_suitability_verdict,
        teacher_plan=args.teacher_plan,
        data_plan=args.data_plan,
        evaluation_plan=args.evaluation_plan,
        implementation_candidates=args.implementation_candidate,
        rejected_alternatives=args.training_rejected_alternative,
        serving_compatibility_notes=args.serving_compatibility_note,
        compute_assumptions=args.compute_assumption,
        stop_criteria=args.stop_criterion,
        rollback_criteria=args.rollback_criterion,
        expected_failure_modes=args.expected_failure_mode,
    )
    write_json(Path(args.decision_output), decision_payload)
    write_json(Path(args.training_output), training_payload)
    return 0


def handle_bundle_system_route(args: argparse.Namespace) -> int:
    decision_payload = build_intervention_decision_artifact(
        target_capability=args.target_capability,
        chosen_intervention_family=args.chosen_intervention_family,
        implementation_direction=args.implementation_direction,
        decision_status=args.decision_status,
        decision_summary=args.decision_summary,
        stop_or_continue_reason=args.stop_or_continue_reason,
        problem_types=args.problem_type,
        evidence_basis=args.evidence_basis,
        rejected_alternatives=args.rejected_alternative,
        key_risks=args.key_risk,
        next_actions=args.next_action,
    )
    system_payload = build_system_composition_plan_artifact(
        target_capability=args.target_capability,
        system_goal=args.system_goal,
        architecture_summary=args.architecture_summary,
        orchestration_summary=args.orchestration_summary,
        evaluation_plan=args.evaluation_plan,
        components=args.component,
        interfaces=args.interface,
        latency_implications=args.latency_implication,
        failure_handling=args.failure_handling,
        observability_requirements=args.observability_requirement,
        unresolved_gaps=args.unresolved_gap,
    )
    write_json(Path(args.decision_output), decision_payload)
    write_json(Path(args.system_output), system_payload)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write consolidated capability-optimizer artifacts.")
    top_level = parser.add_subparsers(dest="command", required=True)

    write_parser = top_level.add_parser("write", help="Write a single artifact.")
    write_subparsers = write_parser.add_subparsers(dest="artifact", required=True)

    capability_parser = write_subparsers.add_parser("capability-intake", help="Write capability-intake.")
    add_capability_intake_arguments(capability_parser, output_required=True, include_requested_capability=True)
    capability_parser.set_defaults(handler=handle_write_capability_intake)

    evaluation_parser = write_subparsers.add_parser("evaluation-plan", help="Write evaluation-plan.")
    add_evaluation_plan_arguments(evaluation_parser, output_required=True, include_target_capability=True)
    evaluation_parser.set_defaults(handler=handle_write_evaluation_plan)

    discovery_parser = write_subparsers.add_parser("model-discovery", help="Write model-discovery.")
    add_model_discovery_arguments(discovery_parser)
    discovery_parser.set_defaults(handler=handle_write_model_discovery)

    environment_parser = write_subparsers.add_parser("environment-discovery", help="Write environment-discovery.")
    add_environment_discovery_arguments(environment_parser)
    environment_parser.set_defaults(handler=handle_write_environment_discovery)

    decision_parser = write_subparsers.add_parser("intervention-decision", help="Write intervention-decision.")
    add_intervention_decision_arguments(decision_parser, output_required=True, include_target_capability=True)
    decision_parser.set_defaults(handler=handle_write_intervention_decision)

    research_parser = write_subparsers.add_parser("research-evidence", help="Write research-evidence.")
    add_research_evidence_arguments(research_parser)
    research_parser.set_defaults(handler=handle_write_research_evidence)

    tool_inventory_parser = write_subparsers.add_parser("tool-inventory", help="Write tool-inventory.")
    add_tool_inventory_arguments(tool_inventory_parser)
    tool_inventory_parser.set_defaults(handler=handle_write_tool_inventory)

    probe_generation_plan_parser = write_subparsers.add_parser(
        "probe-generation-plan",
        help="Write probe-generation-plan.",
    )
    add_probe_generation_plan_arguments(probe_generation_plan_parser)
    probe_generation_plan_parser.set_defaults(handler=handle_write_probe_generation_plan)

    teacher_loop_plan_parser = write_subparsers.add_parser("teacher-loop-plan", help="Write teacher-loop-plan.")
    add_teacher_loop_plan_arguments(teacher_loop_plan_parser)
    teacher_loop_plan_parser.set_defaults(handler=handle_write_teacher_loop_plan)

    dataset_parser = write_subparsers.add_parser("dataset-record", help="Write dataset-record.")
    add_dataset_record_arguments(dataset_parser)
    dataset_parser.set_defaults(handler=handle_write_dataset_record)

    evaluator_payload_parser = write_subparsers.add_parser("evaluator-payload", help="Write evaluator-payload.")
    add_evaluator_payload_arguments(evaluator_payload_parser)
    evaluator_payload_parser.set_defaults(handler=handle_write_evaluator_payload)

    generated_script_plan_parser = write_subparsers.add_parser(
        "generated-script-plan",
        help="Write generated-script-plan.",
    )
    add_generated_script_plan_arguments(generated_script_plan_parser)
    generated_script_plan_parser.set_defaults(handler=handle_write_generated_script_plan)

    training_parser = write_subparsers.add_parser("training-plan", help="Write training-plan.")
    add_training_plan_arguments(
        training_parser,
        output_required=True,
        include_target_capability=True,
        intervention_family_arg="--intervention-family",
        intervention_family_dest="intervention_family",
        rejected_alternative_arg="--rejected-alternative",
        rejected_alternative_dest="rejected_alternative",
    )
    training_parser.set_defaults(handler=handle_write_training_plan)

    system_parser = write_subparsers.add_parser("system-composition-plan", help="Write system-composition-plan.")
    add_system_plan_arguments(system_parser, output_required=True, include_target_capability=True)
    system_parser.set_defaults(handler=handle_write_system_plan)

    bundle_parser = top_level.add_parser("bundle", help="Write a predefined artifact bundle.")
    bundle_subparsers = bundle_parser.add_subparsers(dest="bundle_name", required=True)

    bootstrap_parser = bundle_subparsers.add_parser("bootstrap", help="Write intake and evaluation together.")
    bootstrap_parser.add_argument("--output-dir", required=True, help="Directory for bundled artifacts.")
    bootstrap_parser.add_argument("--target-capability", required=True, help="Normalized target capability.")
    add_capability_intake_arguments(bootstrap_parser, output_required=False, include_requested_capability=False)
    add_evaluation_plan_arguments(bootstrap_parser, output_required=False, include_target_capability=False)
    bootstrap_parser.set_defaults(handler=handle_bundle_bootstrap)

    training_route_parser = bundle_subparsers.add_parser("training-route", help="Write decision and training plan.")
    training_route_parser.add_argument("--decision-output", required=True, help="Path to intervention-decision JSON.")
    training_route_parser.add_argument("--training-output", required=True, help="Path to training-plan JSON.")
    training_route_parser.add_argument("--target-capability", required=True, help="Target capability.")
    add_intervention_decision_arguments(
        training_route_parser,
        output_required=False,
        include_target_capability=False,
    )
    add_training_plan_arguments(
        training_route_parser,
        output_required=False,
        include_target_capability=False,
        intervention_family_arg="--training-intervention-family",
        intervention_family_dest="training_intervention_family",
        rejected_alternative_arg="--training-rejected-alternative",
        rejected_alternative_dest="training_rejected_alternative",
    )
    training_route_parser.set_defaults(handler=handle_bundle_training_route)

    system_route_parser = bundle_subparsers.add_parser("system-route", help="Write decision and system plan.")
    system_route_parser.add_argument("--decision-output", required=True, help="Path to intervention-decision JSON.")
    system_route_parser.add_argument("--system-output", required=True, help="Path to system-plan JSON.")
    system_route_parser.add_argument("--target-capability", required=True, help="Target capability.")
    add_intervention_decision_arguments(
        system_route_parser,
        output_required=False,
        include_target_capability=False,
    )
    add_system_plan_arguments(system_route_parser, output_required=False, include_target_capability=False)
    system_route_parser.set_defaults(handler=handle_bundle_system_route)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
