"""
Grader for EASY task: Email Classification
"""

from graders.base_grader import BaseGrader
from env.environment import AIOperationsEnvironment
from env.models import TaskResult, EmailCategory


class EasyGrader(BaseGrader):
    """
    Grades email classification task.
    
    Deterministic scoring:
    - Accuracy = correctly_classified / total_classified
    - Score = accuracy (0.0 - 1.0)
    """

    def __init__(self):
        """Initialize easy grader."""
        super().__init__("Email Classification")

    def grade(self, env: AIOperationsEnvironment, total_reward: float) -> TaskResult:
        """
        Grade email classification performance.
        
        Returns:
            TaskResult with deterministic score
        """
        state = env.state_obj

        # Ground truth is stored separately from the agent-assigned category.
        correct = 0
        total = 0

        for email in state.emails:
            if email.category is not None:
                total += 1
                if email.category == email.ground_truth_category:
                    correct += 1

        accuracy = correct / total if total > 0 else 0.0
        score = accuracy

        summary = env.get_summary()

        return TaskResult(
            task_name=self.task_name,
            total_reward=total_reward,
            final_score=max(0.0, min(1.0, score)),
            steps_taken=summary["steps"],
            action_counts=summary["action_counts"],
            success=score > 0.7,
            details={
                "accuracy": accuracy,
                "classified": total,
                "total_possible": len(state.emails),
            },
        )
