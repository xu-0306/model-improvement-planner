#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import py_compile
from pathlib import Path
from types import ModuleType


REQUIRED_FILES = (
    "__init__.py",
    "runtime.py",
    "SCAFFOLD_NOTE.md",
    "VALIDATION.md",
    "scaffold_manifest.json",
)

REQUIRED_MANIFEST_KEYS = (
    "contract",
    "schema_version",
    "runtime_id",
    "model_family",
    "supported_checkpoint_formats",
    "supported_tokenizer_formats",
    "inference_loading_strategy",
    "training_support_status",
    "assumptions",
    "unresolved_gaps",
    "status",
)


def expect_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise SystemExit(f"{field_name} must be a string")
    return value


def expect_string_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise SystemExit(f"{field_name} must be a list")
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise SystemExit(f"{field_name}[{index}] must be a string")
    return value


def load_runtime_module(runtime_path: Path) -> ModuleType:
    try:
        py_compile.compile(str(runtime_path), doraise=True)
    except py_compile.PyCompileError as exc:
        raise SystemExit(f"runtime.py is not valid Python: {exc.msg}") from exc

    spec = importlib.util.spec_from_file_location("generated_runtime_scaffold", runtime_path)
    if spec is None or spec.loader is None:
        raise SystemExit("Could not load runtime.py as a Python module")

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise SystemExit(f"runtime.py could not be imported: {exc}") from exc
    return module


def load_manifest(manifest_path: Path) -> dict[str, object]:
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise SystemExit(f"scaffold_manifest.json not found: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(
            "scaffold_manifest.json is not valid JSON: "
            f"{manifest_path} (line {exc.lineno}, column {exc.colno})"
        ) from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a generated runtime scaffold.")
    parser.add_argument("--scaffold-dir", required=True, help="Directory to validate.")
    args = parser.parse_args()

    scaffold_dir = Path(args.scaffold_dir)
    missing = [name for name in REQUIRED_FILES if not (scaffold_dir / name).exists()]
    if missing:
        raise SystemExit(f"Missing scaffold files: {', '.join(missing)}")

    runtime_path = scaffold_dir / "runtime.py"
    runtime_module = load_runtime_module(runtime_path)
    if not hasattr(runtime_module, "RUNTIME"):
        raise SystemExit("runtime.py does not define RUNTIME")

    manifest = load_manifest(scaffold_dir / "scaffold_manifest.json")
    missing_manifest_keys = [key for key in REQUIRED_MANIFEST_KEYS if key not in manifest]
    if missing_manifest_keys:
        raise SystemExit(f"scaffold_manifest.json is missing keys: {', '.join(missing_manifest_keys)}")

    if not expect_string(manifest["runtime_id"], "runtime_id"):
        raise SystemExit("scaffold_manifest.json must declare a non-empty runtime_id")
    if expect_string(manifest["contract"], "contract") != "runtime_scaffold_manifest":
        raise SystemExit("scaffold_manifest.json contract must equal runtime_scaffold_manifest")
    if not expect_string(manifest["schema_version"], "schema_version"):
        raise SystemExit("scaffold_manifest.json must declare schema_version explicitly")
    if not expect_string(manifest["training_support_status"], "training_support_status"):
        raise SystemExit("scaffold_manifest.json must declare training_support_status explicitly")
    expect_string(manifest["model_family"], "model_family")
    expect_string(manifest["inference_loading_strategy"], "inference_loading_strategy")
    expect_string(manifest["status"], "status")
    expect_string_list(manifest["supported_checkpoint_formats"], "supported_checkpoint_formats")
    expect_string_list(manifest["supported_tokenizer_formats"], "supported_tokenizer_formats")
    expect_string_list(manifest["assumptions"], "assumptions")
    expect_string_list(manifest["unresolved_gaps"], "unresolved_gaps")

    runtime_obj = runtime_module.RUNTIME
    for field_name in (
        "runtime_id",
        "model_family",
        "supported_checkpoint_formats",
        "supported_tokenizer_formats",
        "inference_loading_strategy",
        "training_support_status",
        "assumptions",
        "unresolved_gaps",
    ):
        if not hasattr(runtime_obj, field_name):
            raise SystemExit(f"RUNTIME is missing attribute: {field_name}")

    runtime_id = expect_string(runtime_obj.runtime_id, "RUNTIME.runtime_id")
    model_family = expect_string(runtime_obj.model_family, "RUNTIME.model_family")
    supported_checkpoint_formats = expect_string_list(
        runtime_obj.supported_checkpoint_formats,
        "RUNTIME.supported_checkpoint_formats",
    )
    supported_tokenizer_formats = expect_string_list(
        runtime_obj.supported_tokenizer_formats,
        "RUNTIME.supported_tokenizer_formats",
    )
    inference_loading_strategy = expect_string(
        runtime_obj.inference_loading_strategy,
        "RUNTIME.inference_loading_strategy",
    )
    training_support_status = expect_string(
        runtime_obj.training_support_status,
        "RUNTIME.training_support_status",
    )
    assumptions = expect_string_list(runtime_obj.assumptions, "RUNTIME.assumptions")
    unresolved_gaps = expect_string_list(runtime_obj.unresolved_gaps, "RUNTIME.unresolved_gaps")

    if runtime_id != manifest["runtime_id"]:
        raise SystemExit("runtime.py runtime_id does not match scaffold_manifest.json")
    if model_family != manifest["model_family"]:
        raise SystemExit("runtime.py model_family does not match scaffold_manifest.json")
    if supported_checkpoint_formats != manifest["supported_checkpoint_formats"]:
        raise SystemExit("runtime.py supported_checkpoint_formats do not match scaffold_manifest.json")
    if supported_tokenizer_formats != manifest["supported_tokenizer_formats"]:
        raise SystemExit("runtime.py supported_tokenizer_formats do not match scaffold_manifest.json")
    if inference_loading_strategy != manifest["inference_loading_strategy"]:
        raise SystemExit("runtime.py inference_loading_strategy does not match scaffold_manifest.json")
    if training_support_status != manifest["training_support_status"]:
        raise SystemExit("runtime.py training_support_status does not match scaffold_manifest.json")
    if assumptions != manifest["assumptions"]:
        raise SystemExit("runtime.py assumptions do not match scaffold_manifest.json")
    if unresolved_gaps != manifest["unresolved_gaps"]:
        raise SystemExit("runtime.py unresolved_gaps do not match scaffold_manifest.json")

    print("Scaffold is valid.")


if __name__ == "__main__":
    main()
