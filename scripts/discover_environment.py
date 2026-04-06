#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from lib.artifacts import build_environment_discovery_artifact


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "tmp",
}

DEPENDENCY_FILENAMES = {
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "package.json": "node",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "package-lock.json": "npm",
    "Cargo.toml": "cargo",
    "go.mod": "go",
    "environment.yml": "conda",
    "environment.yaml": "conda",
    "dockerfile": "docker",
    "docker-compose.yml": "docker",
    "docker-compose.yaml": "docker",
}

FRAMEWORK_KEYWORDS = {
    "transformers": "transformers",
    "trl": "trl",
    "unsloth": "unsloth",
    "accelerate": "accelerate",
    "deepspeed": "deepspeed",
    "pytorch_lightning": "lightning",
    "lightning": "lightning",
    "vllm": "vllm",
    "sglang": "sglang",
    "peft": "peft",
    "datasets": "datasets",
    "fastapi": "fastapi",
    "flask": "flask",
    "gradio": "gradio",
}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        try:
            return path.read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError, OSError):
            return ""


def _is_training_surface(path: Path, text: str) -> bool:
    name = path.name.lower()
    stem = path.stem.lower()
    return any(token in stem or token in name for token in ("train", "finetune", "sft", "dpo", "distill", "ppo", "lora")) or (
        "trainer" in text.lower() and ("fit(" in text or "train(" in text)
    )


def _is_serving_surface(path: Path, text: str) -> bool:
    name = path.name.lower()
    return any(token in name for token in ("serve", "server", "api", "inference")) or any(
        token in text.lower() for token in ("fastapi", "uvicorn", "/v1/chat/completions", "openai", "serve")
    )


def _is_dataset_surface(path: Path, text: str) -> bool:
    name = path.name.lower()
    suffix = path.suffix.lower()
    return any(token in name for token in ("dataset", "corpus", "data", "prompt")) or suffix in {
        ".jsonl",
        ".csv",
        ".tsv",
        ".parquet",
    } or any(token in text.lower() for token in ("load_dataset", "jsonl", "parquet", "csv"))


def _is_evaluation_surface(path: Path, text: str) -> bool:
    name = path.name.lower()
    return any(token in name for token in ("eval", "benchmark", "probe", "judge", "grader", "test")) or any(
        token in text.lower() for token in ("acceptance_criteria", "benchmark", "probe", "grader", "assert")
    )


def _surface_record(root: Path, path: Path, kind: str) -> str:
    rel = path.relative_to(root).as_posix()
    return json.dumps({"path": rel, "kind": kind}, ensure_ascii=False)


def inspect_workspace(root: Path) -> dict[str, object]:
    package_managers: set[str] = set()
    framework_hints: set[str] = set()
    available_runtimes: set[str] = set()
    source_access_patterns: set[str] = set()
    dependency_files: list[str] = []
    training_surfaces: list[str] = []
    serving_surfaces: list[str] = []
    dataset_surfaces: list[str] = []
    evaluation_surfaces: list[str] = []
    constraints: list[str] = []
    unresolved_gaps: list[str] = []
    notes: list[str] = []

    python_present = False

    for current_root, dirs, files in os.walk(root):
        dirs[:] = [item for item in dirs if item not in EXCLUDED_DIRS]
        current_path = Path(current_root)
        for file_name in files:
            path = current_path / file_name
            lowered = file_name.lower()
            if lowered in DEPENDENCY_FILENAMES:
                dependency_files.append(_surface_record(root, path, "dependency_file"))
                package_managers.add(DEPENDENCY_FILENAMES[lowered])
            elif lowered.startswith("requirements") and lowered.endswith(".txt"):
                dependency_files.append(_surface_record(root, path, "dependency_file"))
                package_managers.add("python")

            if path.suffix.lower() == ".py":
                python_present = True

            if path.stat().st_size > 512_000:
                text = ""
            else:
                text = _read_text(path)

            lowered_text = text.lower()
            for keyword, hint in FRAMEWORK_KEYWORDS.items():
                if keyword in lowered_text:
                    framework_hints.add(hint)

            if "requests" in lowered_text or "httpx" in lowered_text or "urllib" in lowered_text:
                source_access_patterns.add("http_api_access")
            if "beautifulsoup" in lowered_text or "bs4" in lowered_text or "scrapy" in lowered_text:
                source_access_patterns.add("html_collection")
            if "datasets" in lowered_text or "huggingface" in lowered_text:
                source_access_patterns.add("dataset_registry_access")
            if any(token in lowered_text for token in ("openai", "chat.completions", "/v1/chat/completions")):
                available_runtimes.add("openai_compatible_http")

            if _is_training_surface(path, text):
                training_surfaces.append(_surface_record(root, path, "training_surface"))
            if _is_serving_surface(path, text):
                serving_surfaces.append(_surface_record(root, path, "serving_surface"))
            if _is_dataset_surface(path, text):
                dataset_surfaces.append(_surface_record(root, path, "dataset_surface"))
            if _is_evaluation_surface(path, text):
                evaluation_surfaces.append(_surface_record(root, path, "evaluation_surface"))

    if python_present:
        available_runtimes.add("python")
    if "node" in package_managers or "npm" in package_managers or "pnpm" in package_managers or "yarn" in package_managers:
        available_runtimes.add("node")
    if not training_surfaces:
        unresolved_gaps.append("No training surface detected in workspace.")
    if not dataset_surfaces:
        unresolved_gaps.append("No dataset surface detected in workspace.")
    if not evaluation_surfaces:
        unresolved_gaps.append("No evaluation surface detected in workspace.")
    if not source_access_patterns:
        source_access_patterns.add("local_files_only")
    if not package_managers:
        notes.append("No standard package-manager manifest detected.")
    if not framework_hints:
        notes.append("No framework-specific hint detected; downstream flow should stay generic.")
    if not serving_surfaces:
        notes.append("No serving surface detected; teacher or verifier access may need an external adapter.")
    if not available_runtimes:
        constraints.append("No callable runtime detected from workspace scan.")

    return build_environment_discovery_artifact(
        workspace_root=str(root),
        package_managers=sorted(package_managers),
        framework_hints=sorted(framework_hints),
        available_runtimes=sorted(available_runtimes),
        source_access_patterns=sorted(source_access_patterns),
        dependency_files=dependency_files,
        training_surfaces=training_surfaces,
        serving_surfaces=serving_surfaces,
        dataset_surfaces=dataset_surfaces,
        evaluation_surfaces=evaluation_surfaces,
        constraints=constraints,
        unresolved_gaps=unresolved_gaps,
        notes=notes,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect a workspace and emit environment-discovery.json.")
    parser.add_argument("--workspace-root", required=True, help="Workspace root to inspect.")
    parser.add_argument("--output", required=True, help="Output path for environment-discovery.json.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    root = Path(args.workspace_root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"workspace root must exist and be a directory: {root}")

    payload = inspect_workspace(root)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Environment discovery written: {output_path}")


if __name__ == "__main__":
    main()
