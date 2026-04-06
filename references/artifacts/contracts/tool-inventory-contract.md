# Tool Inventory Contract

Use this contract when the skill must record which tools are actually available in the current session before choosing a research, probing, generation, or execution route.

## Goal

Capture a bounded inventory of route-relevant tools without hardcoding a closed skill, MCP, or runtime map into the skill itself.

## Machine-Readable Contract

Emit one JSON object with:

- `contract`: `tool_inventory`
- `schema_version`
- `inventory_scope`
- `workspace_root`
- `skills`
- `mcp_servers`
- `mcp_resources`
- `local_scripts`
- `runtimes`
- `backend_adapters`
- `network_capabilities`
- `constraints`
- `recommended_usage_notes`

## Interpretation Rules

- `inventory_scope` should state what was inspected, such as `current_session` or `workspace_plus_session`.
- `skills` should list currently discoverable skills only. Do not include hypothetical or remembered skills.
- `mcp_servers` and `mcp_resources` should record only what is available now.
- `local_scripts` should focus on scripts that are plausibly useful for the current route rather than dumping every file in the workspace.
- `runtimes` should describe callable local runtimes or serving endpoints, not generic language names without evidence.
- `backend_adapters` should reflect currently usable probe or inference adapter surfaces.
- `constraints` should record route-relevant gaps such as missing network access, missing MCP support, or unavailable local serving.

## Default Output Path

- `artifacts/model-improvement-planner/<target-slug>/tool-inventory.json`

## Worked Example

```json
{
  "contract": "tool_inventory",
  "schema_version": "1.0",
  "inventory_scope": "workspace_plus_session",
  "workspace_root": "/workspace/project",
  "skills": [
    {
      "name": "model-improvement-planner",
      "availability": "present"
    },
    {
      "name": "openai-docs",
      "availability": "present"
    }
  ],
  "mcp_servers": [
    {
      "name": "context7",
      "availability": "present"
    }
  ],
  "mcp_resources": [
    "context7 library docs lookup"
  ],
  "local_scripts": [
    {
      "path": "scripts/run_capability_probes.py",
      "role": "baseline_probing"
    }
  ],
  "runtimes": [
    {
      "runtime_id": "openai_compatible_http",
      "availability": "present"
    }
  ],
  "backend_adapters": [
    "command",
    "openai_compatible_http"
  ],
  "network_capabilities": [
    "official_doc_research"
  ],
  "constraints": [
    "No image collection path has been approved by the user yet."
  ],
  "recommended_usage_notes": [
    "Use local references first, then Context7 for stack-specific docs."
  ]
}
```
