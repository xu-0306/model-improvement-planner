# Artifact Contract Index

This index maps every model-improvement-planner contract to its schema and highlights the handful of required fields so that readers know what is guaranteed by each artifact without opening the schema directly.

1. **capability_intake**
   - Contract doc: `references/artifacts/contracts/capability-intake-contract.md`
   - Schema: `references/artifacts/schemas/capability-intake.schema.json`
   - Purpose: normalize a random capability request into requested capability, desired outcomes, failure modes, modalities, constraints, sub-capabilities, dependencies, and missing facts before routing.
   - Required fields: `contract`, `schema_version`, `requested_capability`, `desired_outcomes`, `failure_modes`, `success_criteria`, `deployment_context`, `user_intent`, `input_modalities`, `output_modalities`, `constraints`, `sub_capabilities`, `external_dependencies`, `missing_facts`.

2. **dataset_record**
   - Contract doc: `references/artifacts/contracts/dataset-contract.md`
   - Schema: `references/artifacts/schemas/dataset-record.schema.json`
   - Purpose: capture teacher-supervised data exports (direct answers, critiques, preferences, verifier outcomes, etc.) with provenance.
   - Required fields: `contract`, `schema_version`, `input`, `metadata` (metadata must include `dataset_mode`, `capability_family`, `supervision_shape`, `source_provenance`, and either `teacher_role` or `teacher_roles`), plus at least one of `target`, `candidates`, or `supervision`.

3. **environment_discovery**
   - Contract doc: `references/artifacts/contracts/environment-discovery-contract.md`
   - Schema: `references/artifacts/schemas/environment-discovery.schema.json`
   - Purpose: describe the current workspace root, discovered reusable surfaces, constraints, and unresolved gaps before emitting execution artifacts.
   - Required fields: `contract`, `schema_version`, `workspace_root`, `environment_summary`, `discovered_surfaces`, `constraints`, `unresolved_gaps`, `notes`.

4. **evaluation_plan**
   - Contract doc: `references/artifacts/contracts/evaluation-plan-contract.md`
   - Schema: `references/artifacts/schemas/evaluation-plan.schema.json`
   - Purpose: define baseline probes, held-out evaluation, success metrics, acceptance criteria, regression checks, and stop conditions before tuning.
   - Required fields: `contract`, `schema_version`, `target_capability`, `baseline_probes`, `heldout_evaluation`, `primary_evaluation_mode`, `success_metrics`, `acceptance_criteria`, `regression_checks`, `unresolved_risks`, `stop_conditions`.

5. **evaluator_payload**
   - Contract doc: `references/artifacts/contracts/evaluator-contract.md`
   - Schema: `references/artifacts/schemas/evaluator-payload.schema.json`
   - Purpose: emit scorer/verifier/preference judgments with subject, evaluation summary, supporting signals, and artifacts.
   - Required fields: `contract`, `schema_version`, `subject`, `evaluation` (must include `mode` and `summary`), `signals`, `artifacts`.

6. **generated_script_plan**
   - Contract doc: `references/artifacts/contracts/generated-script-plan-contract.md`
   - Schema: `references/artifacts/schemas/generated-script-plan.schema.json`
   - Purpose: plan project-local scripts (purpose, inputs, outputs, readiness) that tie intake, evaluation, environment, and data/teacher plans.
   - Required fields: `contract`, `schema_version`, `target_capability`, `plan_status`, `selected_flow_kind`, `capability_intake_reference`, `evaluation_plan_reference`, `environment_discovery_reference`, `dataset_strategy`, `script_plan`, `assumptions`, `unresolved_gaps`.

7. **intervention_decision**
   - Contract doc: `references/artifacts/contracts/intervention-decision-contract.md`
   - Schema: `references/artifacts/schemas/intervention-decision.schema.json`
   - Purpose: document the chosen intervention family, evidence basis, rejected alternatives, key risks, and next actions.
   - Required fields: `contract`, `schema_version`, `target_capability`, `problem_types`, `chosen_intervention_family`, `implementation_direction`, `decision_status`, `decision_summary`, `evidence_basis`, `rejected_alternatives`, `key_risks`, `next_actions`, `stop_or_continue_reason`.

8. **local_model_profile**
   - Contract doc: `references/artifacts/contracts/local-model-profile-contract.md`
   - Schema: `references/artifacts/schemas/local-model-profile.schema.json`
   - Purpose: record inspected metadata about the local checkpoint, tokenizer, adapters, and stack hints before trusting capabilities.
   - Required fields: `contract`, `schema_version`, `model_id`, `model_path`, `profile_status`, `architecture`, `tokenizer`, `generation`, `model_card`, `adapter_presence`, `family_hints`, `language_hints`, `capability_hints`, `stack_hints`, `inspected_files`, `unresolved_facts`.

9. **probe_generation_plan**
   - Contract doc: `references/artifacts/contracts/probe-generation-plan-contract.md`
   - Schema: `references/artifacts/schemas/probe-generation-plan.schema.json`
   - Purpose: explain how baseline probes were designed, including families, modalities, languages, teacher roles, evaluation modes, and known limitations.
   - Required fields: `contract`, `schema_version`, `target_capability`, `planning_scope`, `probe_families`, `generation_rationale`, `teacher_roles`, `evaluation_modes`, `target_modalities`, `target_languages`, `probe_blueprints`, `acceptance_signals`, `known_limitations`.

10. **probe_result**
    - Contract doc: `references/artifacts/contracts/probe-result-contract.md`
    - Schema: `references/artifacts/schemas/probe-result.schema.json`
    - Purpose: capture per-probe evidence (student response, evaluation mode, metrics, verdicts, scores) so teacher loops can export consistent records.
    - Required fields: `contract`, `schema_version`, `probe_id`, `probe_family`, `input`, `expected_evaluation_mode`, `target_capability`, `target_language`, `rubric_reference`, `tags`, `metadata`, `response_status`, `student_response`, `raw_metrics`, `teacher_verdict`, `evaluator_id`, `notes`, `response_language_hint`.

11. **probe_summary**
    - Contract doc: `references/artifacts/contracts/probe-summary-contract.md`
    - Schema: `references/artifacts/schemas/probe-summary.schema.json`
    - Purpose: aggregate probe coverage, status, diagnostics, and readiness signals before routing to a teacher loop.
    - Required fields: `contract`, `schema_version`, `total_probes`, `answered_probes`, `missing_responses`, `families`, `response_statuses`, `expected_evaluation_modes`, `target_languages`, `response_languages`, `family_diagnostics`, `strengths`, `weaknesses`, `failure_signatures`, `suspected_bottlenecks`, `recommended_teacher_roles`, `recommended_supervision_shapes`, `route_readiness`.

12. **research_evidence**
    - Contract doc: `references/artifacts/contracts/research-evidence-contract.md`
    - Schema: `references/artifacts/schemas/research-evidence.schema.json`
    - Purpose: log which sources were consulted, confirmed vs unresolved facts, route implications, unsupported assumptions, and recommended follow-ups when external information is needed.
    - Required fields: `contract`, `schema_version`, `target_capability`, `research_scope`, `sources`, `confirmed_facts`, `unresolved_facts`, `route_implications`, `unsupported_assumptions`, `recommended_followups`.

13. **runtime_scaffold_manifest**
    - Contract doc: `references/artifacts/contracts/runtime-scaffold-contract.md`
    - Schema: `references/artifacts/schemas/runtime-scaffold-manifest.schema.json`
    - Purpose: describe generated runtime adapters (checkpoint/tokenizer formats, inference/loading strategy, training support) that live outside the skill.
    - Required fields: `contract`, `schema_version`, `runtime_id`, `model_family`, `supported_checkpoint_formats`, `supported_tokenizer_formats`, `inference_loading_strategy`, `training_support_status`, `assumptions`, `unresolved_gaps`, `status`.

14. **system_composition_plan**
    - Contract doc: `references/artifacts/contracts/system-composition-plan-contract.md`
    - Schema: `references/artifacts/schemas/system-composition-plan.schema.json`
    - Purpose: capture components, interfaces, orchestration summary, latency, failure handling, observability, and evaluation when the capability requires multiple systems.
    - Required fields: `contract`, `schema_version`, `target_capability`, `system_goal`, `architecture_summary`, `components`, `interfaces`, `orchestration_summary`, `latency_implications`, `failure_handling`, `observability_requirements`, `evaluation_plan`, `unresolved_gaps`.

15. **teacher_loop_plan**
    - Contract doc: `references/artifacts/contracts/teacher-loop-plan-contract.md`
    - Schema: `references/artifacts/schemas/teacher-loop-plan.schema.json`
    - Purpose: specify the teacher roles, loop order, exported artifacts, export strategy, quality gates, and stop conditions used to form dataset records or evaluation payloads.
    - Required fields: `contract`, `schema_version`, `target_capability`, `loop_goal`, `selected_teacher_roles`, `loop_order`, `input_artifacts`, `output_artifacts`, `export_strategy`, `quality_gates`, `stop_conditions`, `open_questions`.

16. **tool_inventory**
    - Contract doc: `references/artifacts/contracts/tool-inventory-contract.md`
    - Schema: `references/artifacts/schemas/tool-inventory.schema.json`
    - Purpose: record what skills, MCP servers/resources, scripts, runtimes, adapters, and network capabilities are actually discoverable before choosing a route.
    - Required fields: `contract`, `schema_version`, `inventory_scope`, `workspace_root`, `skills`, `mcp_servers`, `mcp_resources`, `local_scripts`, `runtimes`, `backend_adapters`, `network_capabilities`, `constraints`, `recommended_usage_notes`.

17. **training_plan**
    - Contract doc: `references/artifacts/contracts/training-plan-contract.md`
    - Schema: `references/artifacts/schemas/training-plan.schema.json`
    - Purpose: capture intervention family, implementation candidates, supervision shape, teacher/data/evaluation plans, stack suitability, compute assumptions, stop/rollback criteria, and expected failure modes when training is justified.
    - Required fields: `contract`, `schema_version`, `target_capability`, `intervention_family`, `implementation_candidates`, `rejected_alternatives`, `supervision_shape`, `teacher_plan`, `data_plan`, `evaluation_plan`, `base_model_suitability_verdict`, `training_stack_suitability_verdict`, `serving_compatibility_notes`, `compute_assumptions`, `stop_criteria`, `rollback_criteria`, `expected_failure_modes`.

18. **training_route_manifest**
    - Contract doc: `references/artifacts/contracts/training-route-manifest-contract.md`
    - Schema: `references/artifacts/schemas/training-route-manifest.schema.json`
    - Purpose: turn a training plan into a repeatable route manifest with route family, trainer stack, dataset paths, base model, outputs, status, and unresolved gaps.
    - Required fields: `contract`, `schema_version`, `route_family`, `target_capability`, `training_plan_reference`, `intervention_family`, `trainer_stack`, `supervision_shape`, `implementation_candidates`, `required_dataset_kind`, `entrypoint`, `implementation_profile`, `dataset_path`, `base_model`, `output_dir`, `base_model_suitability_verdict`, `training_stack_suitability_verdict`, `serving_compatibility_notes`, `stop_criteria`, `rollback_criteria`, `expected_failure_modes`, `unresolved_gaps`, `status`.
