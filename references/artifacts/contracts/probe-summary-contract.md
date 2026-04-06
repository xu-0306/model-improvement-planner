# Probe Summary Contract

Use this contract for aggregated baseline evidence across a probe run.

## Goal

Summarize probe coverage and observed response patterns without losing the underlying per-probe records.

## Machine-Readable Contract

Emit one JSON object with:

- `contract`: `probe_summary`
- `schema_version`
- `total_probes`
- `answered_probes`
- `missing_responses`
- `families`
- `response_statuses`
- `expected_evaluation_modes`
- `target_languages`
- `response_languages`
- `family_diagnostics`
- optional `model_profile_reference`
- optional `average_score`
- optional `pass_rate`
- `strengths`
- `weaknesses`
- `failure_signatures`
- `suspected_bottlenecks`
- `recommended_teacher_roles`
- `recommended_supervision_shapes`
- `route_readiness`

## Minimal Diagnosis Fields

Keep diagnosis compact and reusable across domains.

- `strengths`: short list of capability, language, or evaluation areas where the current baseline looks comparatively stronger
- `weaknesses`: short list of capability, language, or evaluation areas where the baseline looks comparatively weaker or missing
- `family_diagnostics`: per-family compact breakdown of answered coverage, missing coverage, and basic score or pass-rate signals
- `failure_signatures`: normalized failure labels such as `missing_probe_responses`, `target_language_mismatch`, `execution_failures_detected`, or `teacher_review_quality_gap`
- `suspected_bottlenecks`: short list of bottleneck hypotheses such as localization transfer, format compliance, weak instruction following, weak tool grounding, or missing runtime support
- `recommended_teacher_roles`: short list of teacher or verifier roles suggested by the observed failures
- `recommended_supervision_shapes`: short list of supervision shapes suggested by the current evidence, such as `direct_answer`, `critique_then_rewrite`, `preference_pair`, or `verifier_outcome`
- `route_readiness`: compact object summarizing whether the current baseline evidence is sufficient to proceed toward a route decision

`route_readiness` should stay bounded. Prefer a shape like:

- `status`: `insufficient_evidence`, `partial_baseline`, `baseline_ready`, or another small normalized status
- `reason`: short explanation grounded in the current probe coverage
- `blocking_gaps`: remaining evidence gaps that should be closed before escalating
- `recommended_next_step`: the next bounded move, such as more probes, teacher review, or route selection

## Required Interpretation Rule

- Use this artifact to confirm that baseline evidence exists before escalating to training or system routes.
- Keep diagnosis bounded and evidence-facing. `probe_summary` may include compact bottleneck hypotheses and route readiness, but should not expand into a free-form training or system plan.
