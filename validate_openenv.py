"""
Repository validation entrypoint.

Verifies the environment, tasks, graders, and baseline agent can all be
instantiated and run deterministically.
"""

from __future__ import annotations

from typing import Callable, Iterable

from baseline.agent import BaselineAgent
from env.environment import AIOperationsEnvironment
from env.models import ClassifyEmailAction, EmailCategory
from tasks.easy import EasyEmailClassificationTask
from tasks.medium import MediumSupportHandlingTask
from tasks.hard import HardFullOperationsTask


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _validate_environment() -> None:
    env = AIOperationsEnvironment(seed=42, max_steps=5)
    observation = env.reset()

    _assert(observation.step == 0, "reset() must start at step 0")
    _assert(not observation.done, "reset() must return a non-terminal observation")

    env.populate_with_emails(1)
    observation = env._get_observation()
    _assert(len(observation.emails) == 1, "email population failed")

    email = observation.emails[0]
    action = ClassifyEmailAction(
        email_id=email.id,
        category=email.ground_truth_category or EmailCategory.SPAM,
    )
    next_observation, reward, done, info = env.step(action)

    _assert(next_observation.step == 1, "step() must advance the environment")
    _assert(isinstance(reward, float), "step() must return a float reward")
    _assert("reward_components" in info, "step() info must include reward components")
    _assert("classification" in info["reward_components"], "classification reward missing")
    _assert(next_observation.done == done, "observation.done must match the step return value")


def _validate_task(task_factory: Callable[[], object], expected_name: str) -> None:
    task = task_factory()
    env = task.setup_environment()

    agent = BaselineAgent(seed=42)
    total_reward, _ = agent.run_episode(env, max_steps=task.max_steps, verbose=False, reset_env=False)
    result = task.evaluate(env)

    _assert(result.task_name == expected_name, f"unexpected task name: {result.task_name}")
    _assert(0.0 <= result.final_score <= 1.0, f"score out of range for {expected_name}")
    _assert(isinstance(total_reward, float), f"baseline failed for {expected_name}")


def main() -> None:
    checks: Iterable[tuple[str, Callable[[], None]]] = (
        ("environment", _validate_environment),
        ("easy task", lambda: _validate_task(EasyEmailClassificationTask, "Email Classification")),
        ("medium task", lambda: _validate_task(MediumSupportHandlingTask, "Support Handling")),
        ("hard task", lambda: _validate_task(HardFullOperationsTask, "Full Operations Management")),
    )

    print("AI Operations Assistant Environment - Validation")
    print("=" * 60)

    for name, check in checks:
        print(f"[CHECK] {name}")
        check()
        print(f"[OK] {name}")

    print("\nValidation passed")


if __name__ == "__main__":
    main()