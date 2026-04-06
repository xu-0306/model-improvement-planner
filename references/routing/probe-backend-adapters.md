# Probe Backend Adapters

Use this reference when `run_capability_probes.py` should execute probes through a live backend instead of consuming a prebuilt `responses.jsonl`.

## Goal

Provide one small adapter surface for local execution without hardcoding a single runtime stack.

## Supported Backends

- `command`
  Use a local executable that reads one JSON request from stdin and writes one JSON response to stdout.
- `openai_compatible_http`
  Use a local or remote OpenAI-compatible chat completions endpoint.

## Minimal Config Shapes

### `command`

```json
{
  "backend_type": "command",
  "command": "python3",
  "args": ["local_runner.py"],
  "timeout_seconds": 30
}
```

### `openai_compatible_http`

```json
{
  "backend_type": "openai_compatible_http",
  "url": "http://127.0.0.1:8000/v1/chat/completions",
  "model": "local-model-id",
  "system_prompt": "Answer concisely.",
  "request_defaults": {
    "temperature": 0
  },
  "timeout_seconds": 30
}
```

## Selection Rule

- Prefer `command` when the local stack already has a thin runner script or a non-HTTP interface.
- Prefer `openai_compatible_http` when the model is already exposed through a chat-completions-compatible server.
- Keep backend config small. It should choose an adapter, not become a second orchestration language.
