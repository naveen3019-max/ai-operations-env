"""
Base grader for tasks.
"""

from abc import ABC, abstractmethod
from env.environment import AIOperationsEnvironment
from env.models import TaskResult


class BaseGrader(ABC):
    """Abstract base class for task graders."""

    def __init__(self, task_name: str):
        """Initialize grader."""
        self.task_name = task_name

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
