#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.artifacts import build_tool_inventory_artifact
from lib.parsing import write_json
from validate_contracts import VALIDATORS, ValidationError, load_json


def _load_environment_discovery(path: Path) -> dict:
    payload = load_json(path)
    try:
        VALIDATORS["environment_discovery"](payload)
    except ValidationError as exc:
        raise SystemExit(f"environment_discovery failed validation: {exc}") from exc
    return payload


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit a tool-inventory artifact by combining environment discovery with "
            "explicit current-session tool inputs."
        )
    )
    parser.add_argument("--environment-discovery", required=True, help="Path to environment-discovery.json.")
    parser.add_argument("--output", required=True, help="Output path for tool-inventory.json.")
    parser.add_argument(
        "--inventory-scope",
        default="workspace_plus_session",
        help="Inventory scope such as current_session or workspace_plus_session.",
    )
    parser.add_argument("--skill", action="append", default=[], help="Skill item as plain string or JSON object.")
    parser.add_argument(
        "--mcp-server",
        action="append",
        default=[],
        help="MCP server item as plain string or JSON object.",
    )
    parser.add_argument(
        "--mcp-resource",
        action="append",
        default=[],
        help="MCP resource item as plain string or JSON object.",
    )
    parser.add_argument(
        "--local-script",
        action="append",
        default=[],
        help="Route-relevant local script as plain string or JSON object.",
    )
    parser.add_argument("--runtime", action="append", default=[], help="Runtime item as plain string or JSON object.")
    parser.add_argument(
        "--backend-adapter",
        action="append",
        default=[],
        help="Backend adapter label. Repeat as needed.",
    )
    parser.add_argument(
        "--network-capability",
        action="append",
        default=[],
        help="Network capability label. Repeat as needed.",
    )
    parser.add_argument("--constraint", action="append", default=[], help="Additional constraint. Repeat as needed.")
    parser.add_argument(
        "--recommended-usage-note",
        action="append",
        default=[],
        help="Recommended usage note. Repeat as needed.",
    )
    parser.add_argument(
        "--skip-environment-runtimes",
        action="store_true",
        help="Do not seed runtimes from environment-discovery available_runtimes.",
    )
    parser.add_argument(
        "--skip-environment-constraints",
        action="store_true",
        help="Do not merge environment-discovery constraints and unresolved_gaps into tool-inventory constraints.",
    )
    parser.add_argument(
        "--skip-environment-network-capabilities",
        action="store_true",
        help="Do not seed network_capabilities from environment-discovery source_access_patterns.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    environment_path = Path(args.environment_discovery)
    environment = _load_environment_discovery(environment_path)

    environment_summary = environment["environment_summary"]
    workspace_root = str(environment["workspace_root"])

    runtimes = list(args.runtime)
    if not args.skip_environment_runtimes:
        runtimes.extend(environment_summary.get("available_runtimes", []))

    network_capabilities = list(args.network_capability)
    if not args.skip_environment_network_capabilities:
        network_capabilities.extend(
            item
            for item in environment_summary.get("source_access_patterns", [])
            if isinstance(item, str) and item.strip() and item != "local_files_only"
        )

    constraints = list(args.constraint)
    if not args.skip_environment_constraints:
        constraints.extend(environment.get("constraints", []))
        constraints.extend(environment.get("unresolved_gaps", []))

    usage_notes = list(args.recommended_usage_note)
    usage_notes.extend(
        note
        for note in environment.get("notes", [])
        if isinstance(note, str) and note.strip()
    )
    if not usage_notes:
        usage_notes.append("Use bundled references and local workspace evidence before session tools or external research.")

    payload = build_tool_inventory_artifact(
        inventory_scope=args.inventory_scope,
        workspace_root=workspace_root,
        skills=args.skill,
        mcp_servers=args.mcp_server,
        mcp_resources=args.mcp_resource,
        local_scripts=args.local_script,
        runtimes=_dedupe_preserve_order(runtimes),
        backend_adapters=_dedupe_preserve_order(args.backend_adapter),
        network_capabilities=_dedupe_preserve_order(network_capabilities),
        constraints=_dedupe_preserve_order(constraints),
        recommended_usage_notes=_dedupe_preserve_order(usage_notes),
    )

    try:
        VALIDATORS["tool_inventory"](payload)
    except ValidationError as exc:
        raise SystemExit(f"tool_inventory failed validation: {exc}") from exc

    output_path = Path(args.output)
    write_json(output_path, payload)
    print(f"Tool inventory written: {output_path}")


if __name__ == "__main__":
    main()
