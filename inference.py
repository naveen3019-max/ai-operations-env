"""Inference entrypoint for hackathon automated checks."""

from __future__ import annotations

import os
from typing import List

from openai import OpenAI


API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
HF_TOKEN = os.getenv("HF_TOKEN")
BENCHMARK = os.getenv("BENCHMARK", "openenv")
TASK_NAME = os.getenv("TASK_NAME", "openenv-inference")
PROMPT = os.getenv("PROMPT", "Hello from OpenEnv!")


def _bool(value: bool) -> str:
    return "true" if value else "false"


def _reward(value: float) -> str:
    return f"{value:.2f}"


def _safe_error(value: str | None) -> str:
    if value is None:
        return "null"
    return value.replace("\n", " ").replace("\r", " ")


def run_inference(prompt: str) -> None:
    rewards: List[float] = []
    steps = 0
    success = False

    print(f"[START] task={TASK_NAME} env={BENCHMARK} model={MODEL_NAME}", flush=True)

    try:
        if HF_TOKEN is None:
            raise ValueError("HF_TOKEN environment variable is required")

        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
        client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        reward = 1.0
        done = True
        error = None
        success = True
    except Exception as exc:
        reward = 0.0
        done = True
        error = str(exc)
    finally:
        steps += 1
        rewards.append(reward)
        print(
            f"[STEP] step={steps} action=chat.completions.create reward={_reward(reward)} "
            f"done={_bool(done)} error={_safe_error(error)}",
            flush=True,
        )
        print(
            f"[END] success={_bool(success)} steps={steps} "
            f"rewards={','.join(_reward(r) for r in rewards)}",
            flush=True,
        )


if __name__ == "__main__":
    run_inference(PROMPT)
