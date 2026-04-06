# Student Model Connection Guide

Use this reference when you must connect the reading model to the student checkpoint, whether it is served, raw, or API-only.

## Status Detection

Collect two sources to know the student state:

1. `scripts/local_model_profile.py` - exposes weight paths, runtime hints, and adapter metadata.
2. `scripts/discover_environment.py` - shows runtime availability, command hooks, and backend adapters.

Feed their output into this decision table:

| Student state | Action |
|---------------|--------|
| backend already running and callable | use `openai_compatible_http` backend with the discovered endpoint |
| raw weights on disk | generate a loader+server script or guide the user to deploy via Ollama/vLLM/LMStudio |
| model name only | request download path or redirect the user to provide the checkpoint |
| API-only access (Groq, Together, OpenRouter, etc.) | compose the API endpoint and credentials into `backend_config.json` |

Document the selected path in `tool_inventory` or `research_evidence` before running probes.

## Scenario A: Backend Already Hosted

Prefer this when the backend responds to the discovered adapter command or URL.

### Backend config examples

- **Ollama** (default `http://localhost:11434`):
```json
{
  "backend_type": "openai_compatible_http",
  "url": "http://localhost:11434/v1/chat/completions",
  "request_defaults": {
    "temperature": 0
  },
  "headers": {
    "X-Ollama-Client": "model-improvement-planner"
  },
  "timeout_seconds": 30
}
```
- **vLLM**:
```json
{
  "backend_type": "openai_compatible_http",
  "url": "http://localhost:8000/v1/chat/completions",
  "model": "qwen2.5-30b",
  "request_defaults": {
    "temperature": 0
  },
  "timeout_seconds": 30
}
```
- **text-generation-inference**:
```json
{
  "backend_type": "openai_compatible_http",
  "url": "http://localhost:8080/v1/chat/completions",
  "model": "mixtral-instruct-8x7b",
  "timeout_seconds": 30
}
```
- **LMStudio**:
```json
{
  "backend_type": "openai_compatible_http",
  "url": "http://localhost:1234/v1/chat/completions",
  "model": "local-model-id",
  "timeout_seconds": 30
}
```
- **Custom OpenAI-compatible server**:
```json
{
  "backend_type": "openai_compatible_http",
  "url": "<custom-url>",
  "headers": {
    "Authorization": "Bearer <token>"
  },
  "timeout_seconds": 30
}
```

Update `backend_config.json` with the selected snippet and run a health check before emitting probes.

## Scenario B: Raw Weights on Disk

When only checkpoints exist (`.safetensors`, `.bin`, `.pt`, `.pth`, `.ckpt`, `.gguf`, `.ggml`), generate a project-local script that:

1. Loads the checkpoint via `transformers` (or `ggml` loader), e.g., `from transformers import AutoModelForCausalLM, AutoTokenizer`.
2. Applies adapters via `peft` when metadata lists LoRA/IA3/QLoRA checkpoints.
3. Starts a minimal OpenAI-compatible HTTP server (e.g., using `uvicorn` + `fastapi` or the bundled `scripts/generate_runtime_scaffold.py` template).
4. Writes the server URL into `backend_config.json` for downstream probes.

Alternatively, guide the user to deploy the weights to Ollama/vLLM/LMStudio:

- **Ollama**: emit a `Modelfile` referencing the checkpoint and run `ollama create <model-name> -f Modelfile`.
- **vLLM**: emit a `serve.py` or command: `python -m vllm.entrypoints.api --model <path> --port 8000`.
- **LMStudio**: point to the folder containing the checkpoint and run the GUI or CLI serve command.

When deploying raw weights, also emit a minimal `generated_script_plan` entry describing the loader and server scripts, their inputs, and validation command.

## Scenario C: API-only Access

If the reading model only knows an API endpoint, craft `backend_config.json` using `backend_type: openai_compatible_http` plus the URL, headers, model name, and any security tokens (Groq, Together, OpenRouter, etc.). Record credential sources in `tool_inventory`.

## Auto-Detection Strategy

Combine `discover_environment.py` and `local_model_profile.py` output:

- look for `backends` or `adapter_commands` in the environment discovery report
- look for `checkpoint_paths`, `adapter_files`, or `model_tags` in the model profile
- reconcile them to pick between calling a backend or generating a loader script

If both sources disagree, emit `research_evidence` summarizing the conflict before choosing a path.
