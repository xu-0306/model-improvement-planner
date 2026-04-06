#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable


SUPPORTED_CONTRACTS = (
    "capability_intake",
    "dataset_record",
    "environment_discovery",
    "evaluation_plan",
    "evaluator_payload",
    "generated_script_plan",
    "intervention_decision",
    "local_model_profile",
    "model_discovery",
    "probe_generation_plan",
    "probe_result",
    "probe_summary",
    "research_evidence",
    "runtime_scaffold_manifest",
    "system_composition_plan",
    "teacher_loop_plan",
    "tool_inventory",
    "training_plan",
    "training_route_manifest",
)

CONTRACT_ALIASES = {
    "capability-intake": "capability_intake",
    "capability_intake": "capability_intake",
    "dataset-record": "dataset_record",
    "dataset_record": "dataset_record",
    "environment-discovery": "environment_discovery",
    "environment_discovery": "environment_discovery",
    "evaluation-plan": "evaluation_plan",
    "evaluation_plan": "evaluation_plan",
    "evaluator-payload": "evaluator_payload",
    "evaluator_payload": "evaluator_payload",
    "generated-script-plan": "generated_script_plan",
    "generated_script_plan": "generated_script_plan",
    "intervention-decision": "intervention_decision",
    "intervention_decision": "intervention_decision",
    "local-model-profile": "local_model_profile",
    "local_model_profile": "local_model_profile",
    "model-discovery": "model_discovery",
    "model_discovery": "model_discovery",
    "probe-generation-plan": "probe_generation_plan",
    "probe_generation_plan": "probe_generation_plan",
    "probe-result": "probe_result",
    "probe_result": "probe_result",
    "probe-summary": "probe_summary",
    "probe_summary": "probe_summary",
    "research-evidence": "research_evidence",
    "research_evidence": "research_evidence",
    "runtime-scaffold-manifest": "runtime_scaffold_manifest",
    "runtime_scaffold_manifest": "runtime_scaffold_manifest",
    "system-composition-plan": "system_composition_plan",
    "system_composition_plan": "system_composition_plan",
    "teacher-loop-plan": "teacher_loop_plan",
    "teacher_loop_plan": "teacher_loop_plan",
    "tool-inventory": "tool_inventory",
    "tool_inventory": "tool_inventory",
    "training-plan": "training_plan",
    "training_plan": "training_plan",
    "training-route-manifest": "training_route_manifest",
    "training_route_manifest": "training_route_manifest",
}

SCHEMA_FILES = {
    "capability_intake": "capability-intake.schema.json",
    "dataset_record": "dataset-record.schema.json",
    "environment_discovery": "environment-discovery.schema.json",
    "evaluation_plan": "evaluation-plan.schema.json",
    "evaluator_payload": "evaluator-payload.schema.json",
    "generated_script_plan": "generated-script-plan.schema.json",
    "intervention_decision": "intervention-decision.schema.json",
    "local_model_profile": "local-model-profile.schema.json",
    "model_discovery": "model-discovery.schema.json",
    "probe_generation_plan": "probe-generation-plan.schema.json",
    "probe_result": "probe-result.schema.json",
    "probe_summary": "probe-summary.schema.json",
    "research_evidence": "research-evidence.schema.json",
    "runtime_scaffold_manifest": "runtime-scaffold-manifest.schema.json",
    "system_composition_plan": "system-composition-plan.schema.json",
    "teacher_loop_plan": "teacher-loop-plan.schema.json",
    "tool_inventory": "tool-inventory.schema.json",
    "training_plan": "training-plan.schema.json",
    "training_route_manifest": "training-route-manifest.schema.json",
}


class ValidationError(ValueError):
    """Raised when a contract check fails."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Artifact not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Artifact is not valid JSON: {path} (line {exc.lineno}, column {exc.colno})"
        ) from exc


def _schema_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "artifacts" / "schemas"


def load_schema(contract: str) -> dict[str, Any]:
    schema_name = SCHEMA_FILES[contract]
    schema_path = _schema_dir() / schema_name
    try:
        return json.loads(schema_path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Schema not found for {contract}: {schema_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Schema is not valid JSON: {schema_path} (line {exc.lineno}, column {exc.colno})"
        ) from exc


def expect_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must be an object")
    return value


def expect_reference_mapping(value: Any, path: str) -> dict[str, Any]:
    mapping = expect_mapping(value, path)
    reference = mapping.get("reference_artifact", mapping.get("artifact"))
    if not isinstance(reference, str) or not reference.strip():
        raise ValidationError(f"{path} must include reference_artifact or artifact as a non-empty string")
    return mapping


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "number":
        return _is_number(value)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True


def _validate_schema(value: Any, schema: dict[str, Any], path: str) -> None:
    if not schema:
        return

    schema_type = schema.get("type")
    if schema_type is not None and not _type_matches(value, schema_type):
        type_names = {
            "object": "an object",
            "array": "an array",
            "string": "a string",
            "number": "a number",
            "boolean": "a boolean",
        }
        raise ValidationError(f"{path} must be {type_names.get(schema_type, schema_type)}")

    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{path} must equal {schema['const']!r}, got {value!r}")

    if schema_type == "string":
        min_length = schema.get("minLength")
        if min_length is not None and len(value.strip()) < min_length:
            raise ValidationError(f"{path} must be a non-empty string")

    if schema_type == "number":
        minimum = schema.get("minimum")
        if minimum is not None and value < minimum:
            raise ValidationError(f"{path} must be >= {minimum}")
        maximum = schema.get("maximum")
        if maximum is not None and value > maximum:
            raise ValidationError(f"{path} must be <= {maximum}")

    if schema_type == "array":
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            raise ValidationError(f"{path} must contain at least {min_items} items")
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                _validate_schema(item, item_schema, f"{path}[{index}]")

    if schema_type == "object":
        required = schema.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            raise ValidationError(f"{path} is missing keys: {', '.join(missing)}")

        min_properties = schema.get("minProperties")
        if min_properties is not None and len(value) < min_properties:
            raise ValidationError(f"{path} must contain at least {min_properties} properties")

        properties = schema.get("properties", {})
        for key, property_schema in properties.items():
            if key in value:
                _validate_schema(value[key], property_schema, f"{path}.{key}")

    one_of = schema.get("oneOf")
    if one_of is not None:
        matches = 0
        last_error: ValidationError | None = None
        for candidate in one_of:
            try:
                _validate_schema(value, candidate, path)
                matches += 1
            except ValidationError as exc:
                last_error = exc
        if matches != 1:
            if last_error is not None:
                raise ValidationError(str(last_error)) from last_error
            raise ValidationError(f"{path} must match exactly one allowed schema branch")

    any_of = schema.get("anyOf")
    if any_of is not None:
        for candidate in any_of:
            try:
                _validate_schema(value, candidate, path)
                break
            except ValidationError:
                continue
        else:
            raise ValidationError(f"{path} must match at least one allowed schema branch")


def _validate_contract_against_schema(contract: str, payload: Any) -> None:
    schema = load_schema(contract)
    _validate_schema(payload, schema, "$")


def _validate_training_plan_semantics(payload: Any) -> None:
    artifact = expect_mapping(payload, "$")
    expect_reference_mapping(artifact["evaluation_plan"], "$.evaluation_plan")


def _validate_system_plan_semantics(payload: Any) -> None:
    artifact = expect_mapping(payload, "$")
    expect_reference_mapping(artifact["evaluation_plan"], "$.evaluation_plan")


def _validate_generated_script_plan_semantics(payload: Any) -> None:
    artifact = expect_mapping(payload, "$")
    for field_name in (
        "capability_intake_reference",
        "evaluation_plan_reference",
        "environment_discovery_reference",
    ):
        value = artifact.get(field_name, "")
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"$.{field_name} must be a non-empty string")

    training_reference = artifact.get("training_plan_reference", "")
    if training_reference != "" and (not isinstance(training_reference, str) or not training_reference.strip()):
        raise ValidationError("$.training_plan_reference must be empty or a non-empty string")

    steps = artifact.get("script_plan", [])
    if not isinstance(steps, list) or not steps:
        raise ValidationError("$.script_plan must contain at least one step")

    for index, step in enumerate(steps):
        mapping = expect_mapping(step, f"$.script_plan[{index}]")
        for required_key in ("script_id", "path", "script_kind", "purpose", "inputs", "outputs", "status"):
            value = mapping.get(required_key)
            if required_key in ("inputs", "outputs"):
                if not isinstance(value, list):
                    raise ValidationError(f"$.script_plan[{index}].{required_key} must be an array")
            elif not isinstance(value, str) or not value.strip():
                raise ValidationError(f"$.script_plan[{index}].{required_key} must be a non-empty string")


SEMANTIC_VALIDATORS: dict[str, Callable[[Any], None]] = {
    "generated_script_plan": _validate_generated_script_plan_semantics,
    "training_plan": _validate_training_plan_semantics,
    "system_composition_plan": _validate_system_plan_semantics,
}


def _make_contract_validator(contract: str) -> Callable[[Any], None]:
    def _validator(payload: Any) -> None:
        _validate_contract_against_schema(contract, payload)
        semantic_validator = SEMANTIC_VALIDATORS.get(contract)
        if semantic_validator is not None:
            semantic_validator(payload)

    return _validator


VALIDATORS = {
    contract: _make_contract_validator(contract)
    for contract in SUPPORTED_CONTRACTS
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a JSON artifact against bundled contract schemas and "
            "a small set of semantic checks."
        )
    )
    parser.add_argument("--artifact", required=True, help="Path to the JSON artifact.")
    parser.add_argument("--contract", required=True, help="Contract type to validate against.")
    parser.add_argument(
        "--print-scope",
        action="store_true",
        help="Print the validator scope before validating.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    canonical_contract = CONTRACT_ALIASES.get(args.contract)
    if canonical_contract is None:
        allowed = ", ".join(sorted(SUPPORTED_CONTRACTS))
        raise SystemExit(f"Unsupported contract: {args.contract}. Supported values: {allowed}")

    if args.print_scope:
        print("Scope: bundled schema subset validation plus small semantic checks.")

    artifact_path = Path(args.artifact)
    payload = load_json(artifact_path)

    try:
        VALIDATORS[canonical_contract](payload)
    except ValidationError as exc:
        raise SystemExit(f"{canonical_contract} validation failed: {exc}") from exc

    print(f"{canonical_contract} validation passed: {artifact_path}")


if __name__ == "__main__":
    main()
