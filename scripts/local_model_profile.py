#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from lib.model_profile import inspect_model_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect a local model directory and emit a stable profile.")
    parser.add_argument("--model-path", required=True, help="Path to the local model directory.")
    parser.add_argument("--output", required=True, help="Output path for model-profile.json.")
    parser.add_argument("--model-id", default="", help="Optional stable model identifier.")
    parser.add_argument("--serving-stack", action="append", default=[], help="Serving stack hint. Repeat as needed.")
    parser.add_argument("--training-stack", action="append", default=[], help="Training stack hint. Repeat as needed.")
    parser.add_argument("--language-hint", action="append", default=[], help="Language hint. Repeat as needed.")
    parser.add_argument("--capability-hint", action="append", default=[], help="Capability hint. Repeat as needed.")
    parser.add_argument("--unresolved-fact", action="append", default=[], help="Unresolved fact. Repeat as needed.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = inspect_model_directory(
        model_path=Path(args.model_path),
        model_id=args.model_id,
        serving_stack_hints=args.serving_stack,
        training_stack_hints=args.training_stack,
        language_hints=args.language_hint,
        capability_hints=args.capability_hint,
        unresolved_facts=args.unresolved_fact,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Model profile written: {output_path}")


if __name__ == "__main__":
    main()
