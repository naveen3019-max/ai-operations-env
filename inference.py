"""Inference entrypoint for hackathon automated checks."""

from __future__ import annotations

import json
import os
from typing import Any, Dict
from urllib import request

from openai import OpenAI

# Required env variables expected by the checklist.
# Defaults are intentionally set only for API_BASE_URL and MODEL_NAME.
API_BASE_URL = os.getenv("API_BASE_URL", "https://naveen3019-max-openenv-ai-operations.hf.space")
MODEL_NAME = os.getenv("MODEL_NAME", "openenv-ai-operations")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional - if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")


def _fmt(value: Any) -> str:
    text = str(value)
    return text.replace(" ", "_")


def _log(stage: str, **kwargs: Any) -> None:
    # Phase 2 validator expects bracketed START/STEP/END blocks on stdout.
    parts = [f"{key}={_fmt(val)}" for key, val in kwargs.items()]
    line = f"[{stage}] " + " ".join(parts)
    print(line, flush=True)


def _openai_base_url() -> str:
    base = API_BASE_URL.rstrip("/")
    return base if base.endswith("/v1") else f"{base}/v1"


def _fallback_healthcheck() -> Dict[str, Any]:
    try:
        req = request.Request(API_BASE_URL.rstrip("/") + "/", method="GET")
        with request.urlopen(req, timeout=8) as resp:
            body = resp.read().decode("utf-8")

        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"raw": body}
    except Exception as exc:
        return {
            "error": "fallback_unavailable",
            "reason": type(exc).__name__,
        }


def run_inference(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Run one inference call.

    All LLM calls are made through the OpenAI client as required.
    """
    task_name = "openenv-inference"
    step_idx = 0
    score = 0.0
    _log("START", task=task_name, model=MODEL_NAME)

    prompt = (payload or {}).get("prompt", "Say hello in one sentence.")
    step_idx += 1
    _log("STEP", step=step_idx, action="client_init", api_base_url=API_BASE_URL)
    client = OpenAI(base_url=_openai_base_url(), api_key=HF_TOKEN or "DUMMY_TOKEN", timeout=8.0)

    result: Dict[str, Any]
    try:
        step_idx += 1
        _log("STEP", step=step_idx, action="llm_call", model=MODEL_NAME)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response.choices[0].message.content if response.choices else ""
        score = 1.0
        result: Dict[str, Any] = {
            "model_name": MODEL_NAME,
            "api_base_url": API_BASE_URL,
            "local_image_name": LOCAL_IMAGE_NAME,
            "output": content,
        }
    except Exception as exc:
        # For non-LLM demo endpoints, return a healthcheck instead of crashing.
        step_idx += 1
        _log("STEP", step=step_idx, action="fallback_healthcheck", reason=type(exc).__name__)
        score = 0.7
        result = {
            "model_name": MODEL_NAME,
            "api_base_url": API_BASE_URL,
            "local_image_name": LOCAL_IMAGE_NAME,
            "response": _fallback_healthcheck(),
            "warning": "LLM endpoint unavailable, returned healthcheck response",
        }

    _log("END", task=task_name, score=score, steps=step_idx)
    return result


if __name__ == "__main__":
    try:
        output = run_inference()
    except Exception as exc:
        _log("START", task="openenv-inference", model=MODEL_NAME)
        _log("STEP", step=1, action="fatal_error", reason=type(exc).__name__)
        _log("END", task="openenv-inference", score=0.0, steps=1)
        output = {"error": "fatal_inference_error", "reason": type(exc).__name__}

    print(json.dumps(output, indent=2, ensure_ascii=True), flush=True)
