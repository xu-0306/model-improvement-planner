#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.artifacts import build_probe_generation_plan_artifact
from lib.parsing import clean
from validate_contracts import VALIDATORS, ValidationError, load_json


def _load_contract(path: Path, contract: str) -> dict:
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


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    normalized = _normalize(text)
    return any(needle in normalized for needle in needles)


def _probe_families(intake: dict, model_profile: dict | None) -> list[str]:
    requested_capability = clean(str(intake.get("requested_capability", "")))
    sub_capabilities = intake.get("sub_capabilities", [])
    input_modalities = intake.get("input_modalities", [])
    output_modalities = intake.get("output_modalities", [])
    capability_hints = []
    if model_profile is not None:
        capability_hints = model_profile.get("capability_hints", [])

    families: list[str] = []
    joined_subcaps = " ".join(
        clean(str(value))
        for value in sub_capabilities
        if isinstance(value, str) and clean(value)
    )
    joined_hints = " ".join(
        clean(str(value))
        for value in capability_hints
        if isinstance(value, str) and clean(value)
    )
    haystack = " ".join([requested_capability, joined_subcaps, joined_hints])

    if any(clean(str(value)) in {"image", "video"} for value in input_modalities) or _contains_any(
        haystack, ("image", "vision", "chart", "multimodal", "ocr", "diagram")
    ):
        families.append("multimodal_grounding")
    if any(clean(str(value)) in {"audio", "speech"} for value in input_modalities + output_modalities) or _contains_any(
        haystack, ("speech", "audio", "stt", "tts", "asr")
    ):
        families.append("speech_pipeline")
    if _contains_any(haystack, ("tool", "skill", "api", "function_call", "agent")):
        families.append("tool_use")
    if _contains_any(haystack, ("code", "coding", "program", "bug", "test", "patch")):
        families.append("coding")
    if _contains_any(
        haystack,
        ("language", "localization", "translation", "traditional_chinese", "zh_hant", "zh_hk", "zh_tw"),
    ):
        families.append("language_localization")

    if not families:
        families.append("general_capability")
    return _unique(families)


def _teacher_roles(evaluation_plan: dict, families: list[str]) -> list[str]:
    roles = ["diagnostician"]
    mode = _normalize(str(evaluation_plan.get("primary_evaluation_mode", "")))
    if mode in {"exact_match", "verifier_based", "execution_based"}:
        roles.append("verifier")
    if mode in {"teacher_review", "rubric_based"}:
        roles.append("critique_teacher")
    if any(family in {"coding", "tool_use", "speech_pipeline"} for family in families):
        roles.append("verifier")
    if "language_localization" in families:
        roles.append("critique_teacher")
    return _unique(roles)


def _evaluation_modes(evaluation_plan: dict) -> list[str]:
    mode = clean(str(evaluation_plan.get("primary_evaluation_mode", "")))
    if mode:
        return [mode]
    return ["rubric-based"]


def _generation_rationale(families: list[str], intake: dict) -> list[str]:
    rationales = [
        "Need a bounded baseline before route selection so prompt, data, and architecture issues are not conflated."
    ]
    if "multimodal_grounding" in families:
        rationales.append("Need to separate perception or grounding failures from answer-generation failures.")
    if "language_localization" in families:
        rationales.append("Need to distinguish target-language mismatch from broader task weakness.")
    if "tool_use" in families:
        rationales.append("Need to distinguish schema or tool-selection failures from general reasoning weakness.")
    if "coding" in families:
        rationales.append("Need at least one execution-oriented signal before assuming code tuning is justified.")
    if not intake.get("sub_capabilities"):
        rationales.append("Sub-capability coverage is still thin, so the first probe batch must stay compact and diagnostic.")
    return _unique(rationales)


def _probe_blueprints(
    families: list[str],
    intake: dict,
    evaluation_modes: list[str],
    target_languages: list[str],
) -> list[str]:
    primary_mode = evaluation_modes[0] if evaluation_modes else "rubric-based"
    blueprints: list[dict[str, object]] = []

    for family in families:
        if family == "multimodal_grounding":
            blueprints.append(
                {
                    "probe_family": family,
                    "pattern": "extract grounded evidence first, then answer a bounded question",
                    "expected_evaluation_mode": primary_mode,
                    "failure_hypothesis": "perception or grounding failure is hiding behind answer-generation quality",
                }
            )
        elif family == "language_localization":
            blueprint: dict[str, object] = {
                "probe_family": family,
                "pattern": "use a likely stronger-language prompt while requiring output in the target language",
                "expected_evaluation_mode": primary_mode,
                "failure_hypothesis": "target-language fidelity is weaker than general task ability",
            }
            if target_languages:
                blueprint["target_languages"] = target_languages
            blueprints.append(blueprint)
        elif family == "tool_use":
            blueprints.append(
                {
                    "probe_family": family,
                    "pattern": "choose a tool, format arguments, and recover from a bad choice",
                    "expected_evaluation_mode": "execution-based" if primary_mode != "execution-based" else primary_mode,
                    "failure_hypothesis": "tool selection and schema handling are weaker than plain text reasoning",
                }
            )
        elif family == "coding":
            blueprints.append(
                {
                    "probe_family": family,
                    "pattern": "generate or repair code with at least one execution-sensitive check",
                    "expected_evaluation_mode": "execution-based" if primary_mode != "execution-based" else primary_mode,
                    "failure_hypothesis": "surface fluency in code hides execution or patch-discipline failures",
                }
            )
        elif family == "speech_pipeline":
            blueprints.append(
                {
                    "probe_family": family,
                    "pattern": "test the full speech pipeline rather than assuming the base model natively supports audio",
                    "expected_evaluation_mode": primary_mode,
                    "failure_hypothesis": "the real bottleneck may be subsystem composition rather than model weights",
                }
            )
        else:
            blueprints.append(
                {
                    "probe_family": family,
                    "pattern": "use a compact baseline task that isolates the main requested behavior",
                    "expected_evaluation_mode": primary_mode,
                    "failure_hypothesis": "the main capability gap is still under-specified",
                }
            )

    if not blueprints:
        blueprints.append(
            {
                "probe_family": "general_capability",
                "pattern": "compact diagnostic baseline",
                "expected_evaluation_mode": primary_mode,
                "failure_hypothesis": "route selection is premature without a baseline",
            }
        )
    return [str(blueprint) if False else __import__("json").dumps(blueprint, ensure_ascii=False) for blueprint in blueprints]


def _acceptance_signals(evaluation_plan: dict, families: list[str]) -> list[str]:
    signals = [
        "Enough scored or judgeable probe outputs exist to identify at least one weak cluster before route selection."
    ]
    acceptance = evaluation_plan.get("acceptance_criteria", [])
    if isinstance(acceptance, list):
        signals.extend(clean(str(item)) for item in acceptance if isinstance(item, str) and clean(item))
    if "multimodal_grounding" in families:
        signals.append("Probe results should separate grounding failures from final-answer failures.")
    return _unique(signals)


def _known_limitations(model_profile: dict | None, target_languages: list[str]) -> list[str]:
    limitations = [
        "This initial probe plan is diagnostic only and does not by itself justify a training route."
    ]
    if not target_languages:
        limitations.append("No explicit target language was provided, so language-specific probe coverage may still be incomplete.")
    if model_profile is None:
        limitations.append("Model-profile evidence is absent, so strongest-language hypotheses remain weak.")
    return _unique(limitations)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit a conservative probe-generation-plan artifact from existing capability and evaluation artifacts."
    )
    parser.add_argument("--capability-intake", required=True, help="Path to capability-intake.json.")
    parser.add_argument("--evaluation-plan", required=True, help="Path to evaluation-plan.json.")
    parser.add_argument("--output", required=True, help="Output path for probe-generation-plan.json.")
    parser.add_argument("--model-profile", default="", help="Optional path to local-model-profile.json.")
    parser.add_argument("--target-language", action="append", default=[], help="Explicit target language. Repeat as needed.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    capability_intake_path = Path(args.capability_intake)
    evaluation_plan_path = Path(args.evaluation_plan)
    output_path = Path(args.output)
    model_profile_path = Path(args.model_profile) if args.model_profile else None

    intake = _load_contract(capability_intake_path, "capability_intake")
    evaluation = _load_contract(evaluation_plan_path, "evaluation_plan")
    model_profile = _load_contract(model_profile_path, "local_model_profile") if model_profile_path is not None else None

    target_capability = clean(str(intake["requested_capability"]))
    probe_families = _probe_families(intake, model_profile)
    evaluation_modes = _evaluation_modes(evaluation)
    teacher_roles = _teacher_roles(evaluation, probe_families)

    target_languages = _unique(args.target_language)
    if not target_languages and model_profile is not None:
        hints = model_profile.get("language_hints", [])
        if isinstance(hints, list):
            target_languages = _unique(
                clean(str(value))
                for value in hints
                if isinstance(value, str) and clean(value)
            )

    payload = build_probe_generation_plan_artifact(
        target_capability=target_capability,
        planning_scope="initial_baseline",
        probe_families=probe_families,
        generation_rationale=_generation_rationale(probe_families, intake),
        teacher_roles=teacher_roles,
        evaluation_modes=evaluation_modes,
        input_modalities=[clean(str(value)) for value in intake.get("input_modalities", []) if clean(str(value))],
        output_modalities=[clean(str(value)) for value in intake.get("output_modalities", []) if clean(str(value))],
        target_languages=target_languages,
        probe_blueprints=_probe_blueprints(probe_families, intake, evaluation_modes, target_languages),
        acceptance_signals=_acceptance_signals(evaluation, probe_families),
        known_limitations=_known_limitations(model_profile, target_languages),
    )

    try:
        VALIDATORS["probe_generation_plan"](payload)
    except ValidationError as exc:
        raise SystemExit(f"probe_generation_plan failed validation: {exc}") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(__import__("json").dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Probe generation plan written: {output_path}")


if __name__ == "__main__":
    main()
