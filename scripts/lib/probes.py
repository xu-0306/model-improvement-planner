from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.parsing import clean, clean_list


def load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"{label} not found: {path}")

    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(
                f"{label} contains invalid JSON: {path} line {line_number} (column {exc.colno})"
            ) from exc
        if not isinstance(payload, dict):
            raise SystemExit(f"{label} line {line_number} must decode to a JSON object")
        rows.append(payload)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _format_ratio(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "0/0"
    return f"{numerator}/{denominator}"


def _domain_teacher_role(family: str) -> str:
    mapping = {
        "language-localization": "localization_teacher",
        "coding": "code_repair_teacher",
        "tool-use": "tool_trace_teacher",
        "multimodal": "multimodal_grounding_teacher",
        "speech-audio": "speech_pipeline_teacher",
    }
    return mapping.get(family, "domain_specialist_teacher")


def _summarize_family(
    family: str,
    rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], str | None, str | None, list[str], list[str]]:
    total = len(rows)
    answered = sum(1 for row in rows if clean(str(row.get("response_status", ""))) == "answered")
    missing = total - answered

    numeric_scores = [
        float(row["score"])
        for row in rows
        if isinstance(row.get("score"), (int, float)) and not isinstance(row.get("score"), bool)
    ]
    pass_flags = [row["passed"] for row in rows if isinstance(row.get("passed"), bool)]
    target_languages = sorted(
        {
            clean(str(row.get("target_language", "")))
            for row in rows
            if clean(str(row.get("target_language", "")))
        }
    )
    response_languages = sorted(
        {
            clean(str(row.get("response_language_hint", "")))
            for row in rows
            if clean(str(row.get("response_language_hint", "")))
        }
    )

    average_score = sum(numeric_scores) / len(numeric_scores) if numeric_scores else None
    pass_rate = (sum(1 for value in pass_flags if value) / len(pass_flags)) if pass_flags else None

    diagnosis = "partial_coverage"
    if answered == 0:
        diagnosis = "untested"
    elif missing > 0:
        diagnosis = "partial_coverage"
    elif average_score is not None and average_score < 0.7:
        diagnosis = "clear_weakness"
    elif pass_rate is not None:
        if pass_rate >= 0.75:
            diagnosis = "relative_strength"
        elif pass_rate < 0.7:
            diagnosis = "clear_weakness"
        else:
            diagnosis = "mixed_signal"
    elif average_score is not None:
        if average_score >= 0.75:
            diagnosis = "relative_strength"
        else:
            diagnosis = "mixed_signal"
    else:
        diagnosis = "observed_unscored"

    rationale_bits = [f"answered {_format_ratio(answered, total)}"]
    if average_score is not None:
        rationale_bits.append(f"average_score {average_score:.2f}")
    if pass_rate is not None:
        rationale_bits.append(f"pass_rate {pass_rate:.2f}")
    if target_languages:
        rationale_bits.append(f"target_languages {', '.join(target_languages)}")
    if response_languages:
        rationale_bits.append(f"response_languages {', '.join(response_languages)}")
    rationale = "; ".join(rationale_bits)

    strength = None
    weakness = None
    if diagnosis == "relative_strength":
        strength = f"{family} shows relatively stronger baseline performance ({rationale})"
    elif diagnosis == "clear_weakness":
        weakness = f"{family} is currently a weaker area ({rationale})"
    elif diagnosis in {"partial_coverage", "untested"}:
        weakness = f"{family} still needs stronger baseline coverage ({rationale})"

    local_bottlenecks: list[str] = []
    failure_signatures: list[str] = []
    if missing > 0:
        local_bottlenecks.append("probe_coverage_gap")
        failure_signatures.append("missing_probe_responses")

    response_mismatch = False
    for row in rows:
        target_language = clean(str(row.get("target_language", "")))
        response_language = clean(str(row.get("response_language_hint", "")))
        if target_language and response_language and target_language != response_language:
            response_mismatch = True
            break
    if response_mismatch:
        local_bottlenecks.append("cross_language_alignment_gap")
        failure_signatures.append("target_language_mismatch")

    evaluation_modes = {
        clean(str(row.get("expected_evaluation_mode", "")))
        for row in rows
        if clean(str(row.get("expected_evaluation_mode", "")))
    }
    if "execution-based" in evaluation_modes and pass_rate is not None and pass_rate < 1.0:
        local_bottlenecks.append("execution_reliability_gap")
        failure_signatures.append("execution_failures_detected")
    if "teacher-review" in evaluation_modes and average_score is not None and average_score < 0.75:
        local_bottlenecks.append("teacher_correctable_quality_gap")
        failure_signatures.append("teacher_review_quality_gap")

    family_summary: dict[str, Any] = {
        "total_probes": total,
        "answered_probes": answered,
        "missing_responses": missing,
        "diagnosis": diagnosis,
        "target_languages": target_languages,
        "response_languages": response_languages,
    }
    if average_score is not None:
        family_summary["average_score"] = average_score
    if pass_rate is not None:
        family_summary["pass_rate"] = pass_rate

    return family_summary, strength, weakness, local_bottlenecks, failure_signatures


def _build_route_readiness(
    *,
    total_probes: int,
    answered_probes: int,
    missing_responses: int,
    has_scored_probes: bool,
    has_weaknesses: bool,
) -> dict[str, Any]:
    blocking_gaps: list[str] = []
    if total_probes == 0:
        blocking_gaps.append("no probes were provided")
    if total_probes > 0 and answered_probes == 0:
        blocking_gaps.append("no answered probes were captured")
    if missing_responses > 0:
        blocking_gaps.append(f"{missing_responses} probe responses are still missing")
    if answered_probes > 0 and not has_scored_probes:
        blocking_gaps.append("answered probes are present but no numeric scoring has been captured")

    if blocking_gaps:
        status = "insufficient_evidence" if answered_probes == 0 else "partial_baseline"
        reason = "Baseline evidence is incomplete, so route selection should stay bounded."
        recommended_next_step = "Close the blocking gaps and refresh the probe summary before locking the route."
    elif has_weaknesses:
        status = "baseline_ready"
        reason = "Baseline evidence is sufficient to start a teacher loop or narrow supervised route selection."
        recommended_next_step = "Use the identified weaknesses and bottlenecks to choose teacher roles and supervision."
    else:
        status = "baseline_ready"
        reason = "Baseline evidence is sufficient for route selection and does not show a clear weak cluster yet."
        recommended_next_step = "Proceed to route selection or expand probes if finer-grained differentiation is needed."

    return {
        "status": status,
        "reason": reason,
        "blocking_gaps": blocking_gaps,
        "recommended_next_step": recommended_next_step,
    }


def build_probe_results(
    *,
    probe_specs: list[dict[str, Any]],
    response_rows: list[dict[str, Any]],
    model_profile_path: str,
) -> list[dict[str, Any]]:
    responses_by_id: dict[str, dict[str, Any]] = {}
    for row in response_rows:
        probe_id = clean(str(row.get("probe_id", "")))
        if not probe_id:
            raise SystemExit("Each response row must include a non-empty probe_id")
        if probe_id in responses_by_id:
            raise SystemExit(f"Duplicate probe_id in responses: {probe_id}")
        responses_by_id[probe_id] = row

    results: list[dict[str, Any]] = []
    for spec in probe_specs:
        probe_id = clean(str(spec.get("probe_id", "")))
        if not probe_id:
            raise SystemExit("Each probe spec must include a non-empty probe_id")
        family = clean(str(spec.get("probe_family", "")))
        if not family:
            raise SystemExit(f"Probe spec {probe_id} must include probe_family")
        prompt = spec.get("prompt", spec.get("input"))
        if prompt in ("", None):
            raise SystemExit(f"Probe spec {probe_id} must include prompt or input")

        response_row = responses_by_id.get(probe_id, {})
        has_response = bool(response_row)
        result: dict[str, Any] = {
            "contract": "probe_result",
            "schema_version": "1.0",
            "probe_id": probe_id,
            "probe_family": family,
            "input": prompt,
            "expected_evaluation_mode": clean(str(spec.get("expected_evaluation_mode", ""))),
            "target_capability": clean(str(spec.get("target_capability", ""))),
            "target_language": clean(str(spec.get("target_language", ""))),
            "rubric_reference": clean(str(spec.get("rubric_reference", ""))),
            "tags": clean_list(spec.get("tags", [])) if isinstance(spec.get("tags"), list) else [],
            "metadata": spec.get("metadata", {}) if isinstance(spec.get("metadata"), dict) else {},
            "response_status": "answered" if has_response else "missing",
            "student_response": response_row.get("response", ""),
            "raw_metrics": response_row.get("raw_metrics", {}) if has_response else {},
            "teacher_verdict": response_row.get("teacher_verdict", {}) if has_response else {},
            "evaluator_id": clean(str(response_row.get("evaluator_id", ""))),
            "notes": clean(str(response_row.get("notes", ""))),
            "response_language_hint": clean(str(response_row.get("response_language_hint", ""))),
        }
        if model_profile_path:
            result["model_profile_reference"] = model_profile_path
        if has_response and "score" in response_row:
            result["score"] = response_row["score"]
        if has_response and "passed" in response_row:
            result["passed"] = response_row["passed"]
        results.append(result)
    return results


def build_probe_summary(
    *,
    probe_results: list[dict[str, Any]],
    model_profile_path: str,
) -> dict[str, Any]:
    families: dict[str, int] = {}
    statuses: dict[str, int] = {}
    evaluation_modes: dict[str, int] = {}
    target_languages: dict[str, int] = {}
    response_languages: dict[str, int] = {}
    family_rows: dict[str, list[dict[str, Any]]] = {}

    numeric_scores: list[float] = []
    passed_total = 0
    passed_count = 0

    for row in probe_results:
        family = clean(str(row.get("probe_family", "")))
        status = clean(str(row.get("response_status", "")))
        evaluation_mode = clean(str(row.get("expected_evaluation_mode", "")))
        target_language = clean(str(row.get("target_language", "")))
        response_language = clean(str(row.get("response_language_hint", "")))

        if family:
            families[family] = families.get(family, 0) + 1
            family_rows.setdefault(family, []).append(row)
        if status:
            statuses[status] = statuses.get(status, 0) + 1
        if evaluation_mode:
            evaluation_modes[evaluation_mode] = evaluation_modes.get(evaluation_mode, 0) + 1
        if target_language:
            target_languages[target_language] = target_languages.get(target_language, 0) + 1
        if response_language:
            response_languages[response_language] = response_languages.get(response_language, 0) + 1

        score = row.get("score")
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            numeric_scores.append(float(score))
        if "passed" in row and isinstance(row["passed"], bool):
            passed_total += 1
            if row["passed"]:
                passed_count += 1

    family_diagnostics: dict[str, Any] = {}
    strengths: list[str] = []
    weaknesses: list[str] = []
    failure_signatures: list[str] = []
    suspected_bottlenecks: list[str] = []
    recommended_teacher_roles: list[str] = []
    recommended_supervision_shapes: list[str] = []

    for family in sorted(family_rows):
        family_summary, strength, weakness, local_bottlenecks, local_failure_signatures = _summarize_family(
            family,
            family_rows[family],
        )
        family_diagnostics[family] = family_summary
        if strength is not None:
            strengths.append(strength)
        if weakness is not None:
            weaknesses.append(weakness)
        failure_signatures.extend(local_failure_signatures)
        suspected_bottlenecks.extend(local_bottlenecks)
        recommended_teacher_roles.append(_domain_teacher_role(family))

    scored_families = [
        (family, details)
        for family, details in family_diagnostics.items()
        if isinstance(details.get("average_score"), (int, float)) and details.get("answered_probes", 0) > 0
    ]
    if len(scored_families) >= 2:
        strongest_family, strongest_details = max(scored_families, key=lambda item: float(item[1]["average_score"]))
        weakest_family, weakest_details = min(scored_families, key=lambda item: float(item[1]["average_score"]))
        strongest_score = float(strongest_details["average_score"])
        weakest_score = float(weakest_details["average_score"])
        if strongest_family != weakest_family and (strongest_score - weakest_score) >= 0.1:
            relative_note = (
                f"{weakest_family} is currently a relatively weaker area "
                f"(average_score {weakest_score:.2f} vs {strongest_family} {strongest_score:.2f})"
            )
            if not any(weakest_family in item for item in weaknesses):
                weaknesses.append(relative_note)

    if evaluation_modes.get("teacher-review"):
        recommended_teacher_roles.append("critique_teacher")
        recommended_supervision_shapes.append("critique_then_rewrite")
    if evaluation_modes.get("execution-based"):
        recommended_teacher_roles.append("verifier_teacher")
        recommended_supervision_shapes.append("verifier_outcome")
    if strengths and weaknesses:
        recommended_supervision_shapes.append("preference_pair")
    if weaknesses and not recommended_supervision_shapes:
        recommended_supervision_shapes.append("direct_answer")

    route_readiness = _build_route_readiness(
        total_probes=len(probe_results),
        answered_probes=statuses.get("answered", 0),
        missing_responses=statuses.get("missing", 0),
        has_scored_probes=bool(numeric_scores),
        has_weaknesses=bool(weaknesses),
    )

    summary: dict[str, Any] = {
        "contract": "probe_summary",
        "schema_version": "1.0",
        "total_probes": len(probe_results),
        "answered_probes": statuses.get("answered", 0),
        "missing_responses": statuses.get("missing", 0),
        "families": families,
        "response_statuses": statuses,
        "expected_evaluation_modes": evaluation_modes,
        "target_languages": target_languages,
        "response_languages": response_languages,
        "family_diagnostics": family_diagnostics,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "failure_signatures": sorted(set(clean_list(failure_signatures))),
        "suspected_bottlenecks": sorted(set(suspected_bottlenecks)),
        "recommended_teacher_roles": sorted(set(clean_list(recommended_teacher_roles))),
        "recommended_supervision_shapes": sorted(set(clean_list(recommended_supervision_shapes))),
        "route_readiness": route_readiness,
    }
    if model_profile_path:
        summary["model_profile_reference"] = model_profile_path
    if numeric_scores:
        summary["average_score"] = sum(numeric_scores) / len(numeric_scores)
    if passed_total:
        summary["pass_rate"] = passed_count / passed_total
    return summary
