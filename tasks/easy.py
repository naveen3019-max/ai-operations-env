"""
EASY Task: Email Classification

Difficulty: EASY (🟢)
Focus: Email classification only
Goal: Correctly classify all emails

Agent must:
1. Classify each email with correct category
2. Maximize accuracy
3. Handle both spam and legitimate emails
"""

from typing import Dict, Any
from tasks.base_task import BaseTask
from env.models import EmailCategory, TaskResult


class EasyEmailClassificationTask(BaseTask):
    """
    Easy task: email classification.
    
    Environment: Only emails (5-8)
    Objective: Correctly classify all emails
    Rewards: +0.3 per correct, -0.3 per incorrect
    """

    def __init__(self, max_steps: int = 50):
        """Initialize easy task."""
        super().__init__(
            name="Email Classification",
            description="Classify emails into categories (Product, Billing, Feedback, Support, Spam)",
            difficulty="easy",
            max_steps=max_steps,
            grader_module="graders.grader_easy",
            grader_class="EasyGrader",
        )
        self.expected_classifications: Dict[str, EmailCategory] = {}
        self.total_emails: int = 0

    def _populate_environment(self) -> None:
        """Populate with emails only."""
        self.expected_classifications.clear()

        # Generate 6-8 emails
        num_emails = 7
        self.env.populate_with_emails(count=num_emails)
        self.total_emails = num_emails

        # Store ground truth for evaluation
        for email in self.env._state.emails:
            self.expected_classifications[email.id] = email.ground_truth_category

    def evaluate(self, env) -> TaskResult:
        """
        Evaluate classification accuracy.
        
        Scoring:
        - Correct classifications / Total emails
        - 0.0 if no classifications attempted
        - 1.0 if all correct
        """
        correct_count = 0
        total_classified = 0

        for email in env._state.emails:
            if email.handled and email.category is not None:
                total_classified += 1
                expected = self.expected_classifications.get(email.id)
                if email.category == expected:
                    correct_count += 1

        # Calculate score
        if total_classified == 0:
            score = 0.0
            details = {"classified": 0, "total": self.total_emails, "accuracy": 0.0}
        else:
            accuracy = correct_count / total_classified
            # Also penalize if not all emails were classified
            coverage_multiplier = total_classified / self.total_emails
            score = accuracy * coverage_multiplier
            details = {
                "classified": total_classified,
                "correct": correct_count,
                "total": self.total_emails,
                "accuracy": accuracy,
                "coverage": coverage_multiplier,
            }

        summary = env.get_summary()

        return TaskResult(
            task_name=self.name,
            total_reward=summary["total_reward"],
            final_score=max(0.0, min(1.0, score)),
            steps_taken=summary["steps"],
            action_counts=summary["action_counts"],
            success=score > 0.7,
            details=details,
        )
