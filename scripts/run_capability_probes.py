#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.backend_adapter import collect_responses_from_backend_config, collect_responses_from_command
from lib.probes import build_probe_results, build_probe_summary, load_jsonl, write_json, write_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize probe specs plus either captured responses or a backend adapter into "
            "stable probe results and summary artifacts."
        )
    )
    parser.add_argument("--probe-specs", required=True, help="JSONL file containing probe specifications.")
    parser.add_argument(
        "--responses-jsonl",
        default="",
        help="Optional JSONL file containing captured responses keyed by probe_id.",
    )
    parser.add_argument("--results-output", required=True, help="Output JSONL path for normalized probe results.")
    parser.add_argument("--summary-output", required=True, help="Output JSON path for probe summary.")
    parser.add_argument("--model-profile", default="", help="Optional model-profile.json reference path.")
    parser.add_argument(
        "--backend-config",
        default="",
        help="Optional JSON config path for a backend adapter such as command or openai_compatible_http.",
    )
    parser.add_argument(
        "--backend-command",
        default="",
        help="Legacy command backend executable used to collect one response per probe via stdin/stdout JSON.",
    )
    parser.add_argument(
        "--backend-arg",
        action="append",
        default=[],
        help="Optional argument for --backend-command. Repeat as needed.",
    )
    parser.add_argument(
        "--backend-timeout-seconds",
        type=float,
        default=60.0,
        help="Timeout in seconds for each backend probe call.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    backend_modes = [bool(args.backend_config), bool(args.backend_command)]
    if args.responses_jsonl and any(backend_modes):
        raise SystemExit("Use either --responses-jsonl or a backend adapter, not both")
    if sum(1 for mode in backend_modes if mode) > 1:
        raise SystemExit("Use either --backend-config or legacy --backend-command flags, not both")

    probe_specs = load_jsonl(Path(args.probe_specs), "probe specs")
    if args.backend_config:
        response_rows = collect_responses_from_backend_config(
            probe_specs=probe_specs,
            model_profile_path=args.model_profile,
            backend_config_path=args.backend_config,
        )
    elif args.backend_command:
        response_rows = collect_responses_from_command(
            probe_specs=probe_specs,
            model_profile_path=args.model_profile,
            backend_command=args.backend_command,
            backend_args=args.backend_arg,
            timeout_seconds=args.backend_timeout_seconds,
        )
    else:
        response_rows = load_jsonl(Path(args.responses_jsonl), "probe responses") if args.responses_jsonl else []

    results = build_probe_results(
        probe_specs=probe_specs,
        response_rows=response_rows,
        model_profile_path=args.model_profile,
    )
    summary = build_probe_summary(
        probe_results=results,
        model_profile_path=args.model_profile,
    )

    write_jsonl(Path(args.results_output), results)
    write_json(Path(args.summary_output), summary)
    print(f"Probe results written: {args.results_output}")
    print(f"Probe summary written: {args.summary_output}")


if __name__ == "__main__":
    main()
