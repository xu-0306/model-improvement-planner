from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def clean(value: str) -> str:
    return value.strip()


def clean_list(values: list[str]) -> list[str]:
    return [item.strip() for item in values if item.strip()]


def parse_json_object(value: str, field_name: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{field_name} must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise SystemExit(f"{field_name} must decode to a JSON object")
    return parsed


def parse_json_object_or_string(value: str, field_name: str) -> Any:
    text = value.strip()
    if not text:
        return ""
    if text.startswith("{"):
        return parse_json_object(text, field_name)
    return text


def parse_json_array_object_or_string(value: str, field_name: str) -> Any:
    text = value.strip()
    if not text:
        return ""
    if text.startswith("{") or text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{field_name} must be valid JSON when using object or array form") from exc
        if not isinstance(parsed, (dict, list)):
            raise SystemExit(f"{field_name} JSON value must decode to an object or array")
        return parsed
    return text


def parse_json_array_object_or_string_items(values: list[str], field_name: str) -> list[Any]:
    parsed: list[Any] = []
    for item in values:
        text = item.strip()
        if not text:
            continue
        if text.startswith("{") or text.startswith("["):
            try:
                value = json.loads(text)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{field_name} item must be valid JSON when using object or array form") from exc
            if not isinstance(value, (dict, list)):
                raise SystemExit(f"{field_name} JSON item must decode to an object or array")
            parsed.append(value)
        else:
            parsed.append(text)
    return parsed


def parse_string_or_object_items(values: list[str], field_name: str) -> list[Any]:
    parsed: list[Any] = []
    for item in values:
        text = item.strip()
        if not text:
            continue
        if text.startswith("{"):
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{field_name} item must be valid JSON when using object form") from exc
            if not isinstance(obj, dict):
                raise SystemExit(f"{field_name} JSON item must decode to an object")
            parsed.append(obj)
        else:
            parsed.append(text)
    return parsed


def parse_evaluation_plan_reference(value: str, field_name: str) -> dict[str, Any]:
    parsed = parse_json_object(value, field_name)
    reference = parsed.get("reference_artifact", parsed.get("artifact"))
    if not isinstance(reference, str) or not reference.strip():
        raise SystemExit(f"{field_name} must include reference_artifact or artifact as a non-empty string")
    return parsed


def parse_bool(value: str, field_name: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise SystemExit(f"{field_name} must be 'true' or 'false'")


def parse_optional_float(value: str, field_name: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError as exc:
        raise SystemExit(f"{field_name} must be a valid number") from exc


def parse_number_or_string(value: str, field_name: str) -> Any:
    text = value.strip()
    if not text:
        return ""
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
