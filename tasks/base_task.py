"""
Base task class for AI Operations Assistant Environment tasks.
"""

from abc import ABC, abstractmethod
from importlib import import_module
import random
from typing import Dict, Any, Optional
from env.environment import AIOperationsEnvironment
from env.models import Observation, Reward, TaskResult


class BaseTask(ABC):
    """Abstract base class for tasks."""

    EPSILON = 1e-6

    def __init__(
        self,
        name: str,
        description: str,
        difficulty: str,
        max_steps: int = 100,
        grader_name: str = "",
        grader_module: str = "",
        grader_class: str = "",
    ):
        """
        Initialize task.
        
        Args:
            name: Task name
            description: Task description
            difficulty: 'easy', 'medium', or 'hard'
            max_steps: Maximum steps per episode
        """
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.max_steps = max_steps
        self.grader_name = grader_name
        self.grader_module = grader_module
        self.grader_class = grader_class
        self.grader_path = (
            f"{grader_module}.{grader_class}"
            if grader_module and grader_class
            else ""
        )
        if grader_name:
            self.grader = grader_name
        elif self.grader_path:
            self.grader = self.grader_path
        elif grader_module:
            self.grader = grader_module
        else:
            self.grader = ""
        self.env: AIOperationsEnvironment = None
        self.episode_data: Dict[str, Any] = {}

    def create_grader(self) -> Optional[Any]:
        """Instantiate the configured grader, if one is declared."""
        if not self.grader_module or not self.grader_class:
            return None

        module = import_module(self.grader_module)
        grader_cls = getattr(module, self.grader_class)
        return grader_cls()

    @classmethod
    def strict_score(cls, score: float) -> float:
        """Clamp score to the strict open interval (0, 1)."""
        return max(cls.EPSILON, min(1.0 - cls.EPSILON, float(score)))

    def setup_environment(self) -> AIOperationsEnvironment:
        """
        Create and configure environment for this task.
        
        Returns:
            Configured environment
        """
        self.env = AIOperationsEnvironment(max_steps=self.max_steps)
        self._populate_environment()
        return self.env

    @abstractmethod
    def _populate_environment(self) -> None:
        """Populate environment with initial entities. Implemented by subclasses."""
        pass

    @abstractmethod
    def evaluate(self, env: AIOperationsEnvironment) -> TaskResult:
        """
        Evaluate agent performance on this task.
        
        Args:
            env: Environment after episode completion
        
        Returns:
            TaskResult with score and details
        """
        pass

    def reset(self) -> Observation:
        """Reset task environment."""
        if self.env is None:
            self.setup_environment()
        else:
            # Reset and repopulate
            self.env.reset()
            random.seed(self.env.seed_value)
            self._populate_environment()
        return self.env._get_observation()
