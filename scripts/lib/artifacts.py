from __future__ import annotations

import json
from typing import Any

from lib.parsing import (
    clean,
    clean_list,
    parse_evaluation_plan_reference,
    parse_json_array_object_or_string,
    parse_json_array_object_or_string_items,
    parse_json_object,
    parse_json_object_or_string,
    parse_number_or_string,
    parse_optional_float,
    parse_string_or_object_items,
)


def _parse_object_items(values: list[str], field_name: str) -> list[dict[str, Any]]:
    parsed: list[dict[str, Any]] = []
    for item in values:
        text = item.strip()
        if not text:
            continue
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{field_name} item must be valid JSON object form") from exc
        if not isinstance(value, dict):
            raise SystemExit(f"{field_name} item must decode to a JSON object")
        parsed.append(value)
    return parsed


def build_capability_intake_artifact(
    *,
    requested_capability: str,
    user_intent: str,
    deployment_context: str,
    constraints: str,
    desired_outcomes: list[str],
    failure_modes: list[str],
    success_criteria: list[str],
    input_modalities: list[str],
    output_modalities: list[str],
    sub_capabilities: list[str],
    external_dependencies: list[str],
    missing_facts: list[str],
) -> dict[str, Any]:
    return {
        "contract": "capability_intake",
        "schema_version": "1.0",
        "requested_capability": clean(requested_capability),
        "desired_outcomes": clean_list(desired_outcomes),
        "failure_modes": clean_list(failure_modes),
        "success_criteria": clean_list(success_criteria),
        "deployment_context": parse_json_object_or_string(deployment_context, "deployment_context"),
        "user_intent": clean(user_intent),
        "input_modalities": clean_list(input_modalities),
        "output_modalities": clean_list(output_modalities),
        "constraints": parse_json_object(constraints, "constraints"),
        "sub_capabilities": clean_list(sub_capabilities),
        "external_dependencies": clean_list(external_dependencies),
        "missing_facts": clean_list(missing_facts),
    }


def build_evaluation_plan_artifact(
    *,
    target_capability: str,
    primary_evaluation_mode: str,
    baseline_probes: list[str],
    heldout_evaluation: list[str],
    success_metrics: list[str],
    acceptance_criteria: list[str],
    regression_checks: list[str],
    unresolved_risks: list[str],
    stop_conditions: list[str],
) -> dict[str, Any]:
    return {
        "contract": "evaluation_plan",
        "schema_version": "1.0",
        "target_capability": clean(target_capability),
        "baseline_probes": parse_string_or_object_items(baseline_probes, "baseline_probes"),
        "heldout_evaluation": parse_string_or_object_items(heldout_evaluation, "heldout_evaluation"),
        "primary_evaluation_mode": clean(primary_evaluation_mode),
        "success_metrics": parse_string_or_object_items(success_metrics, "success_metrics"),
        "acceptance_criteria": clean_list(acceptance_criteria),
        "regression_checks": clean_list(regression_checks),
        "unresolved_risks": clean_list(unresolved_risks),
        "stop_conditions": clean_list(stop_conditions),
    }


def build_model_discovery_artifact(
    *,
    runtime_id: str,
    model_family: str,
    weight_format: str,
    tokenizer_format: str,
    expected_load_path: str,
    inference_library: str,
    training_library_status: str,
    inference_stack: str,
    training_stack: str,
    device_assumptions: list[str],
    runtime_constraints: list[str],
    missing_facts: list[str],
) -> dict[str, Any]:
    resolved_inference_library = clean(inference_library) or clean(inference_stack)
    resolved_training_library = clean(training_library_status) or clean(training_stack)
    return {
        "contract": "model_discovery",
        "schema_version": "1.0",
        "requested_runtime_id": clean(runtime_id),
        "model_family_hint": clean(model_family),
        "checkpoint_format": clean(weight_format),
        "tokenizer_format": clean(tokenizer_format),
        "expected_load_path": clean(expected_load_path),
        "likely_inference_library": resolved_inference_library,
        "likely_training_library_or_status": resolved_training_library,
        "device_runtime_assumptions": clean_list(device_assumptions),
        "runtime_constraints": clean_list(runtime_constraints),
        "missing_facts": clean_list(missing_facts),
    }


def build_environment_discovery_artifact(
    *,
    workspace_root: str,
    package_managers: list[str],
    framework_hints: list[str],
    available_runtimes: list[str],
    source_access_patterns: list[str],
    dependency_files: list[str],
    training_surfaces: list[str],
    serving_surfaces: list[str],
    dataset_surfaces: list[str],
    evaluation_surfaces: list[str],
    constraints: list[str],
    unresolved_gaps: list[str],
    notes: list[str],
) -> dict[str, Any]:
    return {
        "contract": "environment_discovery",
        "schema_version": "1.0",
        "workspace_root": clean(workspace_root),
        "environment_summary": {
            "package_managers": clean_list(package_managers),
            "framework_hints": clean_list(framework_hints),
            "available_runtimes": clean_list(available_runtimes),
            "source_access_patterns": clean_list(source_access_patterns),
        },
        "discovered_surfaces": {
            "dependency_files": parse_string_or_object_items(dependency_files, "dependency_files"),
            "training_surfaces": parse_string_or_object_items(training_surfaces, "training_surfaces"),
            "serving_surfaces": parse_string_or_object_items(serving_surfaces, "serving_surfaces"),
            "dataset_surfaces": parse_string_or_object_items(dataset_surfaces, "dataset_surfaces"),
            "evaluation_surfaces": parse_string_or_object_items(evaluation_surfaces, "evaluation_surfaces"),
        },
        "constraints": clean_list(constraints),
        "unresolved_gaps": clean_list(unresolved_gaps),
        "notes": clean_list(notes),
    }


def build_intervention_decision_artifact(
    *,
    target_capability: str,
    problem_types: list[str],
    chosen_intervention_family: str,
    implementation_direction: str,
    decision_status: str,
    decision_summary: str,
    evidence_basis: list[str],
    rejected_alternatives: list[str],
    key_risks: list[str],
    next_actions: list[str],
    stop_or_continue_reason: str,
) -> dict[str, Any]:
    return {
        "contract": "intervention_decision",
        "schema_version": "1.0",
        "target_capability": clean(target_capability),
        "problem_types": clean_list(problem_types),
        "chosen_intervention_family": clean(chosen_intervention_family),
        "implementation_direction": clean(implementation_direction),
        "decision_status": clean(decision_status),
        "decision_summary": clean(decision_summary),
        "evidence_basis": clean_list(evidence_basis),
        "rejected_alternatives": clean_list(rejected_alternatives),
        "key_risks": clean_list(key_risks),
        "next_actions": clean_list(next_actions),
        "stop_or_continue_reason": clean(stop_or_continue_reason),
    }


def build_generated_script_plan_artifact(
    *,
    target_capability: str,
    plan_status: str,
    selected_flow_kind: str,
    capability_intake_reference: str,
    evaluation_plan_reference: str,
    environment_discovery_reference: str,
    training_plan_reference: str,
    dataset_strategy: str,
    script_steps: list[str],
    assumptions: list[str],
    unresolved_gaps: list[str],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "contract": "generated_script_plan",
        "schema_version": "1.0",
        "target_capability": clean(target_capability),
        "plan_status": clean(plan_status),
        "selected_flow_kind": clean(selected_flow_kind),
        "capability_intake_reference": clean(capability_intake_reference),
        "evaluation_plan_reference": clean(evaluation_plan_reference),
        "environment_discovery_reference": clean(environment_discovery_reference),
        "dataset_strategy": parse_json_object(dataset_strategy, "dataset_strategy"),
        "script_plan": parse_string_or_object_items(script_steps, "script_plan"),
        "assumptions": clean_list(assumptions),
        "unresolved_gaps": clean_list(unresolved_gaps),
    }
    if clean(training_plan_reference):
        payload["training_plan_reference"] = clean(training_plan_reference)
    return payload


def build_research_evidence_artifact(
    *,
    target_capability: str,
    research_scope: str,
    sources: list[str],
    confirmed_facts: list[str],
    unresolved_facts: list[str],
    route_implications: list[str],
    unsupported_assumptions: list[str],
    recommended_followups: list[str],
) -> dict[str, Any]:
    return {
        "contract": "research_evidence",
        "schema_version": "1.0",
        "target_capability": clean(target_capability),
        "research_scope": clean(research_scope),
        "sources": parse_string_or_object_items(sources, "sources"),
        "confirmed_facts": clean_list(confirmed_facts),
        "unresolved_facts": clean_list(unresolved_facts),
        "route_implications": clean_list(route_implications),
        "unsupported_assumptions": clean_list(unsupported_assumptions),
        "recommended_followups": clean_list(recommended_followups),
    }


def build_tool_inventory_artifact(
    *,
    inventory_scope: str,
    workspace_root: str,
    skills: list[str],
    mcp_servers: list[str],
    mcp_resources: list[str],
    local_scripts: list[str],
    runtimes: list[str],
    backend_adapters: list[str],
    network_capabilities: list[str],
    constraints: list[str],
    recommended_usage_notes: list[str],
) -> dict[str, Any]:
    return {
        "contract": "tool_inventory",
        "schema_version": "1.0",
        "inventory_scope": clean(inventory_scope),
        "workspace_root": clean(workspace_root),
        "skills": parse_string_or_object_items(skills, "skills"),
        "mcp_servers": parse_string_or_object_items(mcp_servers, "mcp_servers"),
        "mcp_resources": parse_string_or_object_items(mcp_resources, "mcp_resources"),
        "local_scripts": parse_string_or_object_items(local_scripts, "local_scripts"),
        "runtimes": parse_string_or_object_items(runtimes, "runtimes"),
        "backend_adapters": clean_list(backend_adapters),
        "network_capabilities": clean_list(network_capabilities),
        "constraints": clean_list(constraints),
        "recommended_usage_notes": clean_list(recommended_usage_notes),
    }


def build_probe_generation_plan_artifact(
    *,
    target_capability: str,
    planning_scope: str,
    probe_families: list[str],
    generation_rationale: list[str],
    teacher_roles: list[str],
    evaluation_modes: list[str],
    input_modalities: list[str],
    output_modalities: list[str],
    target_languages: list[str],
    probe_blueprints: list[str],
    acceptance_signals: list[str],
    known_limitations: list[str],
) -> dict[str, Any]:
    return {
        "contract": "probe_generation_plan",
        "schema_version": "1.0",
        "target_capability": clean(target_capability),
        "planning_scope": clean(planning_scope),
        "probe_families": clean_list(probe_families),
        "generation_rationale": clean_list(generation_rationale),
        "teacher_roles": clean_list(teacher_roles),
        "evaluation_modes": clean_list(evaluation_modes),
        "target_modalities": {
            "input": clean_list(input_modalities),
            "output": clean_list(output_modalities),
        },
        "target_languages": clean_list(target_languages),
        "probe_blueprints": parse_string_or_object_items(probe_blueprints, "probe_blueprints"),
        "acceptance_signals": clean_list(acceptance_signals),
        "known_limitations": clean_list(known_limitations),
    }


def build_teacher_loop_plan_artifact(
    *,
    target_capability: str,
    loop_goal: str,
    selected_teacher_roles: list[str],
    loop_steps: list[str],
    input_artifacts: list[str],
    output_artifacts: list[str],
    export_strategy: str,
    quality_gates: list[str],
    stop_conditions: list[str],
    open_questions: list[str],
) -> dict[str, Any]:
    return {
        "contract": "teacher_loop_plan",
        "schema_version": "1.0",
        "target_capability": clean(target_capability),
        "loop_goal": clean(loop_goal),
        "selected_teacher_roles": clean_list(selected_teacher_roles),
        "loop_order": _parse_object_items(loop_steps, "loop_steps"),
        "input_artifacts": clean_list(input_artifacts),
        "output_artifacts": clean_list(output_artifacts),
        "export_strategy": parse_json_object(export_strategy, "export_strategy"),
        "quality_gates": clean_list(quality_gates),
        "stop_conditions": clean_list(stop_conditions),
        "open_questions": clean_list(open_questions),
    }


def build_training_plan_artifact(
    *,
    target_capability: str,
    intervention_family: str,
    implementation_candidates: list[str],
    rejected_alternatives: list[str],
    supervision_shape: str,
    teacher_plan: str,
    data_plan: str,
    evaluation_plan: str,
    base_model_suitability_verdict: str,
    training_stack_suitability_verdict: str,
    serving_compatibility_notes: list[str],
    compute_assumptions: list[str],
    stop_criteria: list[str],
    rollback_criteria: list[str],
    expected_failure_modes: list[str],
) -> dict[str, Any]:
    return {
        "contract": "training_plan",
        "schema_version": "1.0",
        "target_capability": clean(target_capability),
        "intervention_family": clean(intervention_family),
        "implementation_candidates": clean_list(implementation_candidates),
        "rejected_alternatives": clean_list(rejected_alternatives),
        "supervision_shape": clean(supervision_shape),
        "teacher_plan": parse_json_object(teacher_plan, "teacher_plan"),
        "data_plan": parse_json_object(data_plan, "data_plan"),
        "evaluation_plan": parse_evaluation_plan_reference(evaluation_plan, "evaluation_plan"),
        "base_model_suitability_verdict": clean(base_model_suitability_verdict),
        "training_stack_suitability_verdict": clean(training_stack_suitability_verdict),
        "serving_compatibility_notes": clean_list(serving_compatibility_notes),
        "compute_assumptions": clean_list(compute_assumptions),
        "stop_criteria": clean_list(stop_criteria),
        "rollback_criteria": clean_list(rollback_criteria),
        "expected_failure_modes": clean_list(expected_failure_modes),
    }


def build_system_composition_plan_artifact(
    *,
    target_capability: str,
    system_goal: str,
    architecture_summary: str,
    components: list[str],
    interfaces: list[str],
    orchestration_summary: str,
    latency_implications: list[str],
    failure_handling: list[str],
    observability_requirements: list[str],
    evaluation_plan: str,
    unresolved_gaps: list[str],
) -> dict[str, Any]:
    return {
        "contract": "system_composition_plan",
        "schema_version": "1.0",
        "target_capability": clean(target_capability),
        "system_goal": clean(system_goal),
        "architecture_summary": clean(architecture_summary),
        "components": parse_string_or_object_items(components, "components"),
        "interfaces": parse_string_or_object_items(interfaces, "interfaces"),
        "orchestration_summary": clean(orchestration_summary),
        "latency_implications": clean_list(latency_implications),
        "failure_handling": clean_list(failure_handling),
        "observability_requirements": clean_list(observability_requirements),
        "evaluation_plan": parse_evaluation_plan_reference(evaluation_plan, "evaluation_plan"),
        "unresolved_gaps": clean_list(unresolved_gaps),
    }


def build_dataset_record_artifact(
    *,
    input_value: str,
    target_value: str,
    candidates: list[str],
    supervision: str,
    evidence: str,
    dataset_mode: str,
    capability_family: str,
    supervision_shape: str,
    teacher_roles: list[str],
    source_provenance: str,
    evaluator_id: str,
    rubric_reference: str,
    difficulty: str,
    confidence: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "contract": "dataset_record",
        "schema_version": "1.0",
        "input": parse_json_array_object_or_string(input_value, "input"),
    }

    if clean(target_value):
        payload["target"] = parse_json_array_object_or_string(target_value, "target")
    if candidates:
        payload["candidates"] = parse_json_array_object_or_string_items(candidates, "candidates")
    if clean(supervision):
        payload["supervision"] = parse_json_object(supervision, "supervision")
    if clean(evidence):
        payload["evidence"] = parse_json_array_object_or_string(evidence, "evidence")

    if not any(key in payload for key in ("target", "candidates", "supervision")):
        raise SystemExit("dataset_record must include at least one of target, candidates, or supervision")

    cleaned_teacher_roles = clean_list(teacher_roles)
    if not cleaned_teacher_roles:
        raise SystemExit("metadata must include at least one teacher role")

    metadata: dict[str, Any] = {
        "dataset_mode": clean(dataset_mode),
        "capability_family": clean(capability_family),
        "supervision_shape": clean(supervision_shape),
        "source_provenance": parse_json_array_object_or_string(source_provenance, "source_provenance"),
    }

    if len(cleaned_teacher_roles) == 1:
        metadata["teacher_role"] = cleaned_teacher_roles[0]
    else:
        metadata["teacher_roles"] = cleaned_teacher_roles

    if clean(evaluator_id):
        metadata["evaluator_id"] = clean(evaluator_id)
    if clean(rubric_reference):
        metadata["rubric_reference"] = clean(rubric_reference)
    if clean(difficulty):
        metadata["difficulty"] = parse_number_or_string(difficulty, "difficulty")

    parsed_confidence = parse_optional_float(confidence, "confidence")
    if parsed_confidence is not None:
        metadata["confidence"] = parsed_confidence

    payload["metadata"] = metadata
    return payload


def build_evaluator_payload_artifact(
    *,
    subject: str,
    evaluation: str,
    evaluation_mode: str,
    evaluation_summary: str,
    score: str,
    is_correct: str,
    chosen_candidate: str,
    rejected_candidate: str,
    binary_label: str,
    scalar_reward: str,
    verifier_status: str,
    process_label: str,
    mastery_delta: str,
    rationale: str,
    signals: list[str],
    artifacts: str,
    teacher_feedback: str,
    teacher_correction: str,
    mistake_classification: str,
    advance: str,
    confidence: str,
) -> dict[str, Any]:
    if clean(evaluation):
        evaluation_payload = parse_json_object(evaluation, "evaluation")
    else:
        evaluation_payload: dict[str, Any] = {
            "mode": clean(evaluation_mode),
            "summary": clean(evaluation_summary),
        }
        parsed_score = parse_optional_float(score, "score")
        if parsed_score is not None:
            evaluation_payload["score"] = parsed_score
        if clean(is_correct):
            from lib.parsing import parse_bool
            evaluation_payload["is_correct"] = parse_bool(is_correct, "is_correct")
        if clean(chosen_candidate):
            evaluation_payload["chosen_candidate"] = parse_json_array_object_or_string(
                chosen_candidate,
                "chosen_candidate",
            )
        if clean(rejected_candidate):
            evaluation_payload["rejected_candidate"] = parse_json_array_object_or_string(
                rejected_candidate,
                "rejected_candidate",
            )
        if clean(binary_label):
            evaluation_payload["binary_label"] = parse_json_array_object_or_string(binary_label, "binary_label")
        parsed_scalar_reward = parse_optional_float(scalar_reward, "scalar_reward")
        if parsed_scalar_reward is not None:
            evaluation_payload["scalar_reward"] = parsed_scalar_reward
        if clean(verifier_status):
            evaluation_payload["verifier_status"] = clean(verifier_status)
        if clean(process_label):
            evaluation_payload["process_label"] = parse_json_array_object_or_string(process_label, "process_label")
        parsed_mastery_delta = parse_optional_float(mastery_delta, "mastery_delta")
        if parsed_mastery_delta is not None:
            evaluation_payload["mastery_delta"] = parsed_mastery_delta
        if clean(rationale):
            evaluation_payload["rationale"] = clean(rationale)

    payload: dict[str, Any] = {
        "contract": "evaluator_payload",
        "schema_version": "1.0",
        "subject": parse_json_array_object_or_string(subject, "subject"),
        "evaluation": evaluation_payload,
        "signals": parse_string_or_object_items(signals, "signals"),
        "artifacts": parse_json_object(artifacts, "artifacts"),
    }

    if clean(teacher_feedback):
        payload["teacher_feedback"] = clean(teacher_feedback)
    if clean(teacher_correction):
        payload["teacher_correction"] = parse_json_array_object_or_string(teacher_correction, "teacher_correction")
    if clean(mistake_classification):
        payload["mistake_classification"] = parse_json_array_object_or_string(
            mistake_classification,
            "mistake_classification",
        )
    if clean(advance):
        from lib.parsing import parse_bool
        payload["advance"] = parse_bool(advance, "advance")

    parsed_confidence = parse_optional_float(confidence, "confidence")
    if parsed_confidence is not None:
        payload["confidence"] = parsed_confidence

    return payload
