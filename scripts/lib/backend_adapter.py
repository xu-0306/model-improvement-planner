from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from lib.parsing import clean


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{label} contains invalid JSON: {path} (line {exc.lineno}, column {exc.colno})") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"{label} must decode to a JSON object: {path}")
    return payload


def load_backend_config(path: Path) -> dict[str, Any]:
    payload = load_json_object(path, "backend config")
    backend_type = clean(
        str(payload.get("backend_type", payload.get("adapter_type", payload.get("backend", ""))))
    ).lower().replace("-", "_")
    if not backend_type:
        raise SystemExit("backend config must include backend_type")
    payload["backend_type"] = backend_type
    return payload


def _load_model_profile(model_profile_path: str) -> dict[str, Any]:
    if not model_profile_path:
        return {}
    return load_json_object(Path(model_profile_path), "model profile")


def _build_probe_request(
    *,
    probe_spec: dict[str, Any],
    probe_id: str,
    model_profile_path: str,
    model_profile: dict[str, Any],
) -> dict[str, Any]:
    return {
        "probe_spec": probe_spec,
        "probe_id": probe_id,
        "model_profile_path": model_profile_path,
        "model_profile": model_profile,
    }


def _normalize_backend_response(response_payload: Any, probe_id: str) -> dict[str, Any]:
    if not isinstance(response_payload, dict):
        raise SystemExit(f"Probe backend must return a JSON object for probe_id={probe_id}")

    returned_probe_id = clean(str(response_payload.get("probe_id", "")))
    if returned_probe_id and returned_probe_id != probe_id:
        raise SystemExit(f"Probe backend returned mismatched probe_id for {probe_id}: {returned_probe_id}")

    normalized = dict(response_payload)
    normalized["probe_id"] = probe_id
    return normalized


def _coerce_prompt_text(probe_spec: dict[str, Any]) -> str:
    prompt = probe_spec.get("prompt", probe_spec.get("input"))
    if prompt in ("", None):
        raise SystemExit("Each probe spec must include prompt or input before backend execution")
    if isinstance(prompt, str):
        return prompt
    return json.dumps(prompt, ensure_ascii=False)


def _extract_openai_message_text(payload: dict[str, Any], probe_id: str) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise SystemExit(f"OpenAI-compatible backend returned no choices for probe_id={probe_id}")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise SystemExit(f"OpenAI-compatible backend returned invalid choice payload for probe_id={probe_id}")
    message = first_choice.get("message", {})
    if not isinstance(message, dict):
        raise SystemExit(f"OpenAI-compatible backend returned invalid message payload for probe_id={probe_id}")
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") in ("text", "output_text")
        ]
        return "\n".join(part for part in text_parts if part)
    raise SystemExit(f"OpenAI-compatible backend returned unsupported content payload for probe_id={probe_id}")


def collect_responses_from_command(
    *,
    probe_specs: list[dict[str, Any]],
    model_profile_path: str,
    backend_command: str,
    backend_args: list[str],
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    if not clean(backend_command):
        raise SystemExit("backend_command must be non-empty")

    command = [backend_command, *backend_args]
    model_profile = _load_model_profile(model_profile_path)
    responses: list[dict[str, Any]] = []

    for spec in probe_specs:
        probe_id = clean(str(spec.get("probe_id", "")))
        if not probe_id:
            raise SystemExit("Each probe spec must include a non-empty probe_id before backend execution")

        request_payload = _build_probe_request(
            probe_spec=spec,
            probe_id=probe_id,
            model_profile_path=model_profile_path,
            model_profile=model_profile,
        )
        try:
            result = subprocess.run(
                command,
                input=json.dumps(request_payload, ensure_ascii=False),
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise SystemExit(f"Probe backend timed out after {timeout_seconds:g}s for probe_id={probe_id}") from exc

        if result.returncode != 0:
            stderr = result.stderr.strip()
            stdout = result.stdout.strip()
            detail = stderr or stdout or "no output"
            raise SystemExit(f"Probe backend failed for probe_id={probe_id}: {detail}")

        stdout = result.stdout.strip()
        if not stdout:
            raise SystemExit(f"Probe backend returned empty stdout for probe_id={probe_id}")

        try:
            response_payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise SystemExit(
                f"Probe backend returned invalid JSON for probe_id={probe_id} "
                f"(line {exc.lineno}, column {exc.colno})"
            ) from exc

        responses.append(_normalize_backend_response(response_payload, probe_id))
    return responses


def collect_responses_from_openai_compatible_http(
    *,
    probe_specs: list[dict[str, Any]],
    model_profile_path: str,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    url = clean(str(config.get("url", "")))
    base_url = clean(str(config.get("base_url", "")))
    if not url:
        if not base_url:
            raise SystemExit("openai_compatible_http backend requires url or base_url")
        url = base_url.rstrip("/") + "/v1/chat/completions"

    model = clean(str(config.get("model", "")))
    if not model:
        raise SystemExit("openai_compatible_http backend requires model")

    timeout_seconds = config.get("timeout_seconds", 60.0)
    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
        raise SystemExit("openai_compatible_http timeout_seconds must be a positive number")

    headers = {"Content-Type": "application/json"}
    api_key = clean(str(config.get("api_key", "")))
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    extra_headers = config.get("headers", {})
    if extra_headers:
        if not isinstance(extra_headers, dict):
            raise SystemExit("openai_compatible_http headers must be an object")
        for key, value in extra_headers.items():
            if isinstance(key, str) and isinstance(value, str):
                headers[key] = value

    request_defaults = config.get("request_defaults", {})
    if request_defaults and not isinstance(request_defaults, dict):
        raise SystemExit("openai_compatible_http request_defaults must be an object")

    system_prompt = clean(str(config.get("system_prompt", "")))
    model_profile = _load_model_profile(model_profile_path)
    responses: list[dict[str, Any]] = []

    for spec in probe_specs:
        probe_id = clean(str(spec.get("probe_id", "")))
        if not probe_id:
            raise SystemExit("Each probe spec must include a non-empty probe_id before backend execution")

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": _coerce_prompt_text(spec)})

        body = {
            "model": model,
            "messages": messages,
            **request_defaults,
        }
        raw_request = json.dumps(body, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(url, data=raw_request, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=float(timeout_seconds)) as response:
                raw_response = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            raise SystemExit(f"OpenAI-compatible backend HTTP {exc.code} for probe_id={probe_id}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise SystemExit(f"OpenAI-compatible backend request failed for probe_id={probe_id}: {exc.reason}") from exc

        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise SystemExit(
                f"OpenAI-compatible backend returned invalid JSON for probe_id={probe_id} "
                f"(line {exc.lineno}, column {exc.colno})"
            ) from exc
        if not isinstance(payload, dict):
            raise SystemExit(f"OpenAI-compatible backend must return a JSON object for probe_id={probe_id}")

        response_payload = {
            "probe_id": probe_id,
            "response": _extract_openai_message_text(payload, probe_id),
            "raw_metrics": {"backend": "openai_compatible_http"},
            "notes": clean(str(payload.get("id", ""))),
            "model_profile_reference": model_profile_path,
        }
        if model_profile:
            response_payload["backend_context"] = {"model_id": clean(str(model_profile.get("model_id", "")))}
        responses.append(_normalize_backend_response(response_payload, probe_id))

    return responses


def collect_responses_from_backend_config(
    *,
    probe_specs: list[dict[str, Any]],
    model_profile_path: str,
    backend_config_path: str,
) -> list[dict[str, Any]]:
    config = load_backend_config(Path(backend_config_path))
    backend_type = config["backend_type"]

    if backend_type == "command":
        command = clean(str(config.get("command", "")))
        args = config.get("args", [])
        if args and not isinstance(args, list):
            raise SystemExit("command backend args must be an array")
        normalized_args = [str(item) for item in args] if isinstance(args, list) else []
        timeout_seconds = config.get("timeout_seconds", 60.0)
        if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
            raise SystemExit("command backend timeout_seconds must be a positive number")
        return collect_responses_from_command(
            probe_specs=probe_specs,
            model_profile_path=model_profile_path,
            backend_command=command,
            backend_args=normalized_args,
            timeout_seconds=float(timeout_seconds),
        )

    if backend_type == "openai_compatible_http":
        return collect_responses_from_openai_compatible_http(
            probe_specs=probe_specs,
            model_profile_path=model_profile_path,
            config=config,
        )

    raise SystemExit(
        "Unsupported backend_type in backend config: "
        f"{backend_type}. Supported values: command, openai_compatible_http"
    )
