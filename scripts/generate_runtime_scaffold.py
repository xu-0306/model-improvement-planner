#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _py_literal(value: str) -> str:
    return repr(value)


def _module_text(
    runtime_id: str,
    model_family: str,
    weight_format: str,
    tokenizer_format: str,
    inference_loading_strategy: str,
    training_support_status: str,
    assumptions: list[str],
    unresolved_gaps: list[str],
) -> str:
    checkpoint_formats = [weight_format] if weight_format else []
    tokenizer_formats = [tokenizer_format] if tokenizer_format else []
    return f'''from __future__ import annotations


class GeneratedRuntime:
    runtime_id = {_py_literal(runtime_id)}
    model_family = {_py_literal(model_family)}
    supported_checkpoint_formats = {checkpoint_formats!r}
    supported_tokenizer_formats = {tokenizer_formats!r}
    inference_loading_strategy = {_py_literal(inference_loading_strategy)}
    training_support_status = {_py_literal(training_support_status)}
    assumptions = {assumptions!r}
    unresolved_gaps = {unresolved_gaps!r}

    def describe(self) -> dict[str, str]:
        return {{
            "runtime_id": self.runtime_id,
            "model_family": self.model_family,
            "supported_checkpoint_formats": ", ".join(self.supported_checkpoint_formats),
            "supported_tokenizer_formats": ", ".join(self.supported_tokenizer_formats),
            "inference_loading_strategy": self.inference_loading_strategy,
            "training_support_status": self.training_support_status,
            "assumptions": " | ".join(self.assumptions),
            "unresolved_gaps": " | ".join(self.unresolved_gaps),
        }}


RUNTIME = GeneratedRuntime()
'''


def _bullet_lines(values: list[str]) -> str:
    if not values:
        return "- none declared"
    return "\n".join(f"- {value}" for value in values)


def _note_text(
    runtime_id: str,
    model_family: str,
    weight_format: str,
    tokenizer_format: str,
    inference_loading_strategy: str,
    training_support_status: str,
    assumptions: list[str],
    unresolved_gaps: list[str],
) -> str:
    return f"""# Runtime Scaffold Note

- runtime_id: {runtime_id}
- model_family: {model_family}
- supported_checkpoint_formats: {weight_format or "unspecified"}
- supported_tokenizer_formats: {tokenizer_format or "unspecified"}
- inference_loading_strategy: {inference_loading_strategy or "unspecified"}
- training_support_status: {training_support_status}
- status: scaffold_only

## Assumptions

{_bullet_lines(assumptions)}

## Unresolved Gaps

{_bullet_lines(unresolved_gaps)}

Review and fill in loading, inference, and training details before production use. Do not claim support until the gaps are resolved or explicitly accepted.
"""


def _validation_text(runtime_id: str) -> str:
    return f"""# Validation Commands

- Import the generated module for `{runtime_id}`.
- Verify runtime id matches the expected value.
- Add a model-specific smoke test for loading and one for answer generation.
- If training is supported, add a dry-run validation command before full training.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a generic external runtime scaffold.")
    parser.add_argument("--output-dir", required=True, help="Directory where the scaffold should be written.")
    parser.add_argument("--runtime-id", required=True, help="Runtime identifier.")
    parser.add_argument("--model-family", default="", help="Model family or architecture hint.")
    parser.add_argument("--weight-format", default="", help="Checkpoint or weight format.")
    parser.add_argument("--tokenizer-format", default="", help="Tokenizer format.")
    parser.add_argument(
        "--inference-loading-strategy",
        default="",
        help="Short description of how inference loading is expected to work.",
    )
    parser.add_argument(
        "--training-support-status",
        default="unsupported",
        help="Training support declaration, for example supported, partial, or unsupported.",
    )
    parser.add_argument(
        "--assumption",
        action="append",
        default=[],
        help="Assumption carried by this scaffold. May be passed multiple times.",
    )
    parser.add_argument(
        "--unresolved-gap",
        action="append",
        default=[],
        help="Known unresolved gap. May be passed multiple times.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "__init__.py").write_text("from .runtime import RUNTIME\n", encoding="utf-8")
    (output_dir / "runtime.py").write_text(
        _module_text(
            runtime_id=args.runtime_id.strip(),
            model_family=args.model_family.strip(),
            weight_format=args.weight_format.strip(),
            tokenizer_format=args.tokenizer_format.strip(),
            inference_loading_strategy=args.inference_loading_strategy.strip(),
            training_support_status=args.training_support_status.strip(),
            assumptions=[item.strip() for item in args.assumption if item.strip()],
            unresolved_gaps=[item.strip() for item in args.unresolved_gap if item.strip()],
        ),
        encoding="utf-8",
    )
    (output_dir / "SCAFFOLD_NOTE.md").write_text(
        _note_text(
            runtime_id=args.runtime_id.strip(),
            model_family=args.model_family.strip(),
            weight_format=args.weight_format.strip(),
            tokenizer_format=args.tokenizer_format.strip(),
            inference_loading_strategy=args.inference_loading_strategy.strip(),
            training_support_status=args.training_support_status.strip(),
            assumptions=[item.strip() for item in args.assumption if item.strip()],
            unresolved_gaps=[item.strip() for item in args.unresolved_gap if item.strip()],
        ),
        encoding="utf-8",
    )
    (output_dir / "VALIDATION.md").write_text(_validation_text(args.runtime_id.strip()), encoding="utf-8")
    (output_dir / "scaffold_manifest.json").write_text(
        json.dumps(
            {
                "contract": "runtime_scaffold_manifest",
                "schema_version": "1.0",
                "runtime_id": args.runtime_id.strip(),
                "model_family": args.model_family.strip(),
                "supported_checkpoint_formats": [args.weight_format.strip()] if args.weight_format.strip() else [],
                "supported_tokenizer_formats": [args.tokenizer_format.strip()] if args.tokenizer_format.strip() else [],
                "inference_loading_strategy": args.inference_loading_strategy.strip(),
                "training_support_status": args.training_support_status.strip(),
                "assumptions": [item.strip() for item in args.assumption if item.strip()],
                "unresolved_gaps": [item.strip() for item in args.unresolved_gap if item.strip()],
                "status": "scaffold_only",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
