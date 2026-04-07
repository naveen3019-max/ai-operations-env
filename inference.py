"""
Inference entrypoint for automated hackathon checks.

Expected environment variables:
- API_BASE_URL (default provided)
- MODEL_NAME (default provided)
- HF_TOKEN (optional, no default)
- LOCAL_IMAGE_NAME (optional, used only for local Docker workflows)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict
from urllib import request

# Defaults are intentionally set only for API_BASE_URL and MODEL_NAME.
API_BASE_URL = os.getenv("API_BASE_URL", "https://naveen3019-max-openenv-ai-operations.hf.space")
MODEL_NAME = os.getenv("MODEL_NAME", "openenv-ai-operations")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")


def _build_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    return headers


def run_inference(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Call the deployed API and return a normalized response payload."""
    url = API_BASE_URL.rstrip("/") + "/"
    req = request.Request(url, headers=_build_headers(), method="GET")

    with request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")

    data: Dict[str, Any]
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        data = {"raw": body}

    return {
        "model_name": MODEL_NAME,
        "api_base_url": API_BASE_URL,
        "local_image_name": LOCAL_IMAGE_NAME,
        "response": data,
    }


if __name__ == "__main__":
    result = run_inference()
    print(json.dumps(result, indent=2))
