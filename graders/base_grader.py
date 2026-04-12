"""
Base grader for tasks.
"""

from abc import ABC, abstractmethod
from typing import Any
from env.environment import AIOperationsEnvironment
from env.models import TaskResult


class BaseGrader(ABC):
    """Abstract base class for task graders."""

    EPSILON = 1e-6
    SCORE_FIELD_TOKENS = ("score", "rate", "accuracy", "coverage")

    def __init__(self, task_name: str):
        """Initialize grader."""
        self.task_name = task_name

    @classmethod
    def strict_score(cls, score: float) -> float:
        """Clamp score to the strict open interval (0, 1)."""
        return max(cls.EPSILON, min(1.0 - cls.EPSILON, float(score)))

    @classmethod
    def sanitize_metrics(cls, value: Any, key_name: str = "") -> Any:
        """Recursively clamp score-like metrics to the strict open interval."""
        if isinstance(value, dict):
            return {k: cls.sanitize_metrics(v, k) for k, v in value.items()}

        if isinstance(value, list):
            return [cls.sanitize_metrics(v, key_name) for v in value]

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            metric_key = key_name.lower()
            if any(token in metric_key for token in cls.SCORE_FIELD_TOKENS):
                return cls.strict_score(value)

        return value

    @abstractmethod
    def grade(self, env: AIOperationsEnvironment, total_reward: float) -> TaskResult:
        """
        Grade agent performance on the task.
        
        Args:
            env: Environment after episode
            total_reward: Total reward accumulated
        
        Returns:
            TaskResult with score 0.0-1.0
        """
        pass
