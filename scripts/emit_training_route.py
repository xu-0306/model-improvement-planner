#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from lib.training_emitters import (
    SUPPORTED_IMPLEMENTATION_PROFILES,
    SUPPORTED_ROUTE_FAMILIES,
    build_launch_script,
    build_training_route_config,
    build_training_route_manifest,
    load_training_plan,
    normalize_route_selection,
)
from validate_contracts import VALIDATORS, ValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit a stable training-route scaffold from a training plan.")
    parser.add_argument("--training-plan", required=True, help="Path to training-plan.json.")
    parser.add_argument(
        "--route-family",
        required=True,
        help=(
            "Normalized route family to emit. Supported families: "
            + ", ".join(SUPPORTED_ROUTE_FAMILIES)
            + ". Legacy aliases such as unsloth-sft or trl-preference are still accepted."
        ),
    )
    parser.add_argument(
        "--implementation-profile",
        default="generic",
        help=(
            "Optional bundled implementation profile to use as a callable hint. "
            "Supported profiles: " + ", ".join(SUPPORTED_IMPLEMENTATION_PROFILES)
        ),
    )
    parser.add_argument("--output-dir", required=True, help="Directory where the scaffold should be written.")
    parser.add_argument("--dataset-path", default="", help="Optional dataset path for launch scaffold.")
    parser.add_argument("--base-model", default="", help="Optional base model identifier or path.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    route_family, implementation_profile = normalize_route_selection(
        args.route_family,
        args.implementation_profile,
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    training_plan_path = Path(args.training_plan)
    training_plan = load_training_plan(training_plan_path)
    try:
        VALIDATORS["training_plan"](training_plan)
    except ValidationError as exc:
        raise SystemExit(f"training plan failed validation: {exc}") from exc
    manifest = build_training_route_manifest(
        route_family=route_family,
        implementation_profile=implementation_profile,
        training_plan=training_plan,
        training_plan_path=training_plan_path,
        output_dir=output_dir,
        dataset_path=args.dataset_path.strip(),
        base_model=args.base_model.strip(),
    )
    config = build_training_route_config(
        route_family=route_family,
        implementation_profile=implementation_profile,
        training_plan=training_plan,
        manifest=manifest,
    )

    (output_dir / "training-route-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "train_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    launch_path = output_dir / "launch.sh"
    launch_path.write_text(build_launch_script(manifest=manifest), encoding="utf-8")
    launch_path.chmod(0o755)

    print(f"Training route manifest written: {output_dir / 'training-route-manifest.json'}")
    print(f"Training route config written: {output_dir / 'train_config.json'}")
    print(f"Training route launcher written: {launch_path}")


if __name__ == "__main__":
    main()
