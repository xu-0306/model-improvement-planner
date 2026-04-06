from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SUPPORTED_ROUTE_FAMILIES = (
    "sft",
    "distill",
    "peft-sft",
    "preference",
    "reward",
)

SUPPORTED_IMPLEMENTATION_PROFILES = (
    "generic",
    "unsloth-sft",
    "trl-preference",
    "trl-reward",
)

ROUTE_PROFILE_ALIASES = {
    "unsloth-sft": ("sft", "unsloth-sft"),
    "trl-preference": ("preference", "trl-preference"),
    "trl-reward": ("reward", "trl-reward"),
}


def load_training_plan(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise SystemExit(f"training plan not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"training plan is not valid JSON: {path} (line {exc.lineno}, column {exc.colno})"
        ) from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"training plan must decode to a JSON object: {path}")
    if payload.get("contract") != "training_plan":
        raise SystemExit("training plan contract must equal training_plan")
    return payload


def normalize_route_selection(
    route_family: str,
    implementation_profile: str,
) -> tuple[str, str]:
    normalized_route = route_family.strip().lower().replace("_", "-")
    normalized_profile = implementation_profile.strip().lower().replace("_", "-")

    if normalized_route in ROUTE_PROFILE_ALIASES:
        aliased_route, aliased_profile = ROUTE_PROFILE_ALIASES[normalized_route]
        if normalized_profile == "generic":
            normalized_profile = ""
        if normalized_profile and normalized_profile != aliased_profile:
            raise SystemExit(
                "route_family alias and implementation_profile disagree:"
                f" route_family={route_family!r}, implementation_profile={implementation_profile!r}"
            )
        normalized_route = aliased_route
        normalized_profile = aliased_profile

    if not normalized_profile:
        normalized_profile = "generic"

    if normalized_route not in SUPPORTED_ROUTE_FAMILIES:
        supported = ", ".join(SUPPORTED_ROUTE_FAMILIES + SUPPORTED_IMPLEMENTATION_PROFILES)
        raise SystemExit(
            f"Unsupported route_family: {route_family}. Supported route families and aliases: {supported}"
        )
    if normalized_profile not in SUPPORTED_IMPLEMENTATION_PROFILES:
        supported_profiles = ", ".join(SUPPORTED_IMPLEMENTATION_PROFILES)
        raise SystemExit(
            f"Unsupported implementation_profile: {implementation_profile}. "
            f"Supported profiles: {supported_profiles}"
        )

    if normalized_profile == "unsloth-sft" and normalized_route != "sft":
        raise SystemExit("implementation_profile unsloth-sft requires route_family sft")
    if normalized_profile == "trl-preference" and normalized_route != "preference":
        raise SystemExit("implementation_profile trl-preference requires route_family preference")
    if normalized_profile == "trl-reward" and normalized_route != "reward":
        raise SystemExit("implementation_profile trl-reward requires route_family reward")

    return normalized_route, normalized_profile


def _route_stack(implementation_profile: str) -> str:
    if implementation_profile == "unsloth-sft":
        return "unsloth"
    if implementation_profile.startswith("trl-"):
        return "trl"
    return "generic"


def _entrypoint(output_dir: Path) -> str:
    return str(output_dir / "project-local-launch.sh")


def _profile_command_hint(implementation_profile: str) -> str:
    mapping = {
        "generic": "python train.py --config train_config.json",
        "unsloth-sft": "python train_unsloth_sft.py --config train_config.json",
        "trl-preference": "python train_trl_preference.py --config train_config.json",
        "trl-reward": "python train_trl_reward.py --config train_config.json",
    }
    return mapping[implementation_profile]


def _required_dataset_kind(route_family: str) -> str:
    if route_family == "preference":
        return "chosen_rejected_or_preference_pairs"
    if route_family == "reward":
        return "scalar_reward_or_verifier_outcome"
    if route_family == "distill":
        return "teacher_targets_or_distillation_records"
    return "demonstration_or_instruction_records"


def _route_objective(route_family: str) -> str:
    mapping = {
        "sft": "supervised_finetuning",
        "distill": "distillation",
        "peft-sft": "parameter_efficient_sft",
        "preference": "preference_optimization",
        "reward": "reward_driven_optimization",
    }
    return mapping[route_family]


def _bundled_profile_details(route_family: str, implementation_profile: str) -> dict[str, Any]:
    details: dict[str, Any] = {
        "stack": _route_stack(implementation_profile),
        "command_hint": _profile_command_hint(implementation_profile),
        "is_optional": True,
    }
    if implementation_profile == "unsloth-sft":
        details.update({"adapter_type": "lora", "load_in_4bit": True})
    elif implementation_profile == "trl-preference":
        details.update({"trainer_type": "dpo_or_orpo", "requires_preferences": True})
    elif implementation_profile == "trl-reward":
        details.update({"trainer_type": "reward_or_ppo", "requires_reward_signal": True})
    elif route_family == "distill":
        details.update({"teacher_student_mode": "distillation"})
    elif route_family == "peft-sft":
        details.update({"adapter_type": "lora"})
    else:
        details.update({"trainer_type": route_family})
    return details


def _route_specific_config(
    route_family: str,
    implementation_profile: str,
    training_plan: dict[str, Any],
) -> dict[str, Any]:
    return {
        "objective": _route_objective(route_family),
        "supervision_shape": training_plan.get("supervision_shape", ""),
        "implementation_candidates": training_plan.get("implementation_candidates", []),
        "teacher_plan": training_plan.get("teacher_plan", {}),
        "data_plan": training_plan.get("data_plan", {}),
        "launcher_strategy": "generate_project_local_launcher",
        "implementation_profile": implementation_profile,
        "bundled_profile": _bundled_profile_details(route_family, implementation_profile),
    }


def build_training_route_manifest(
    *,
    route_family: str,
    implementation_profile: str,
    training_plan: dict[str, Any],
    training_plan_path: Path,
    output_dir: Path,
    dataset_path: str,
    base_model: str,
) -> dict[str, Any]:
    unresolved_gaps: list[str] = []
    if not dataset_path:
        unresolved_gaps.append("dataset_path not provided")
    if not base_model:
        unresolved_gaps.append("base_model not provided")
    if implementation_profile == "generic":
        unresolved_gaps.append("project-local launcher still needs to be selected or generated")

    return {
        "contract": "training_route_manifest",
        "schema_version": "1.0",
        "route_family": route_family,
        "target_capability": training_plan.get("target_capability", ""),
        "training_plan_reference": str(training_plan_path),
        "intervention_family": training_plan.get("intervention_family", ""),
        "trainer_stack": _route_stack(implementation_profile),
        "supervision_shape": training_plan.get("supervision_shape", ""),
        "implementation_candidates": training_plan.get("implementation_candidates", []),
        "required_dataset_kind": _required_dataset_kind(route_family),
        "entrypoint": _entrypoint(output_dir),
        "implementation_profile": implementation_profile,
        "profile_is_optional": True,
        "bundled_profile_command_hint": _profile_command_hint(implementation_profile),
        "dataset_path": dataset_path,
        "base_model": base_model,
        "output_dir": str(output_dir),
        "base_model_suitability_verdict": training_plan.get("base_model_suitability_verdict", ""),
        "training_stack_suitability_verdict": training_plan.get("training_stack_suitability_verdict", ""),
        "serving_compatibility_notes": training_plan.get("serving_compatibility_notes", []),
        "stop_criteria": training_plan.get("stop_criteria", []),
        "rollback_criteria": training_plan.get("rollback_criteria", []),
        "expected_failure_modes": training_plan.get("expected_failure_modes", []),
        "unresolved_gaps": unresolved_gaps,
        "status": "scaffold_only",
    }


def build_training_route_config(
    *,
    route_family: str,
    implementation_profile: str,
    training_plan: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "route_family": route_family,
        "implementation_profile": implementation_profile,
        "target_capability": manifest["target_capability"],
        "base_model": manifest["base_model"],
        "dataset_path": manifest["dataset_path"],
        "output_dir": manifest["output_dir"],
        "evaluation_plan": training_plan.get("evaluation_plan", {}),
        "compute_assumptions": training_plan.get("compute_assumptions", []),
        "route": _route_specific_config(route_family, implementation_profile, training_plan),
    }


def build_launch_script(*, manifest: dict[str, Any]) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

BASE_MODEL="${{BASE_MODEL:-{manifest['base_model']}}}"
DATASET_PATH="${{DATASET_PATH:-{manifest['dataset_path']}}}"
OUTPUT_DIR="${{OUTPUT_DIR:-{manifest['output_dir']}}}"

if [ -z "$BASE_MODEL" ]; then
  echo "BASE_MODEL is required" >&2
  exit 1
fi

if [ -z "$DATASET_PATH" ]; then
  echo "DATASET_PATH is required" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

cat <<'EOF'
This launcher is a project-local scaffold, not a canonical training command.

Route family:
  {manifest['route_family']}

Selected bundled implementation profile:
  {manifest['implementation_profile']}

Optional command hint for adapting the scaffold:
  {manifest['bundled_profile_command_hint']}

Next step:
  Replace this placeholder with the launcher that matches the discovered
  project environment, or generate a project-local launcher from the emitted plan.
EOF
"""
