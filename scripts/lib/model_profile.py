from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.parsing import clean, clean_list


def _load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON file: {path} (line {exc.lineno}, column {exc.colno})") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object in: {path}")
    return payload


def _parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    lines = text.splitlines()
    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}

    parsed: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in lines[1:end_index]:
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith("- ") and current_key is not None:
            parsed.setdefault(current_key, [])
            if isinstance(parsed[current_key], list):
                parsed[current_key].append(line[2:].strip())
            continue
        if ":" not in line:
            current_key = None
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if not value:
            parsed[key] = []
        else:
            parsed[key] = value
    return parsed


def _read_model_card(model_dir: Path) -> dict[str, Any]:
    for candidate in ("README.md", "README.MD", "readme.md"):
        path = model_dir / candidate
        if path.exists():
            return _parse_frontmatter(path.read_text(encoding="utf-8"))
    return {}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def inspect_model_directory(
    *,
    model_path: Path,
    model_id: str,
    serving_stack_hints: list[str],
    training_stack_hints: list[str],
    language_hints: list[str],
    capability_hints: list[str],
    unresolved_facts: list[str],
) -> dict[str, Any]:
    if not model_path.exists():
        raise SystemExit(f"Model path not found: {model_path}")
    if not model_path.is_dir():
        raise SystemExit(f"Model path must be a directory: {model_path}")

    config = _load_json_if_exists(model_path / "config.json")
    generation_config = _load_json_if_exists(model_path / "generation_config.json")
    tokenizer_config = _load_json_if_exists(model_path / "tokenizer_config.json")
    adapter_config = _load_json_if_exists(model_path / "adapter_config.json")
    model_card = _read_model_card(model_path)

    tokenizer_files = [
        name
        for name in (
            "tokenizer.json",
            "tokenizer.model",
            "special_tokens_map.json",
            "tokenizer_config.json",
        )
        if (model_path / name).exists()
    ]

    inspected_files = sorted(
        path.name
        for path in model_path.iterdir()
        if path.is_file() and path.name in {
            "README.md",
            "README.MD",
            "readme.md",
            "config.json",
            "generation_config.json",
            "tokenizer_config.json",
            "tokenizer.json",
            "tokenizer.model",
            "special_tokens_map.json",
            "adapter_config.json",
        }
    )

    declared_languages = _string_list(model_card.get("language"))
    declared_tags = _string_list(model_card.get("tags"))
    merged_language_hints = sorted(set(clean_list(language_hints) + declared_languages))
    merged_capability_hints = sorted(set(clean_list(capability_hints) + declared_tags))

    inferred_family_hints = clean_list(
        [
            *(config.get("architectures") or [] if isinstance(config.get("architectures"), list) else []),
            clean(str(config.get("model_type", ""))),
            clean(str(adapter_config.get("peft_type", ""))),
        ]
    )

    auto_unresolved = []
    if not declared_languages:
        auto_unresolved.append("model card language metadata missing")
    auto_unresolved.append("empirical baseline probes required to confirm strongest language or capability priors")
    if not tokenizer_config.get("chat_template"):
        auto_unresolved.append("chat template missing or not declared in tokenizer_config.json")

    return {
        "contract": "local_model_profile",
        "schema_version": "1.0",
        "model_id": clean(model_id) or model_path.name,
        "model_path": str(model_path.resolve()),
        "profile_status": "inspected",
        "architecture": {
            "model_type": clean(str(config.get("model_type", ""))),
            "architectures": _string_list(config.get("architectures")),
            "torch_dtype": clean(str(config.get("torch_dtype", ""))),
            "vocab_size": config.get("vocab_size"),
            "max_position_embeddings": config.get("max_position_embeddings"),
        },
        "tokenizer": {
            "tokenizer_class": clean(str(tokenizer_config.get("tokenizer_class", ""))),
            "chat_template_present": bool(tokenizer_config.get("chat_template")),
            "model_max_length": tokenizer_config.get("model_max_length"),
            "files_present": tokenizer_files,
        },
        "generation": {
            "has_generation_config": bool(generation_config),
            "default_max_new_tokens": generation_config.get("max_new_tokens"),
            "default_temperature": generation_config.get("temperature"),
        },
        "model_card": {
            "declared_languages": declared_languages,
            "license": clean(str(model_card.get("license", ""))),
            "tags": declared_tags,
            "base_model": clean(str(model_card.get("base_model", ""))),
        },
        "adapter_presence": {
            "adapter_config_present": bool(adapter_config),
            "peft_type": clean(str(adapter_config.get("peft_type", ""))),
            "base_model_name_or_path": clean(str(adapter_config.get("base_model_name_or_path", ""))),
        },
        "family_hints": sorted(set(inferred_family_hints)),
        "language_hints": merged_language_hints,
        "capability_hints": merged_capability_hints,
        "stack_hints": {
            "serving": clean_list(serving_stack_hints),
            "training": clean_list(training_stack_hints),
        },
        "inspected_files": inspected_files,
        "unresolved_facts": sorted(set(clean_list(unresolved_facts) + auto_unresolved)),
    }
