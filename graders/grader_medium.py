"""
Grader for MEDIUM task: Support Handling
"""

from graders.base_grader import BaseGrader
from env.environment import AIOperationsEnvironment
from env.models import TaskResult, EmailCategory, TicketStatus


class MediumGrader(BaseGrader):
    """
    Grades support handling task.
    
    Deterministic scoring based on:
    1. Email classification accuracy (40%)
    2. Support reply rate (30%)
    3. Ticket resolution rate (30%)
    """

    def __init__(self):
        """Initialize medium grader."""
        super().__init__("Support Handling")

    def grade(self, env: AIOperationsEnvironment, total_reward: float) -> TaskResult:
        """
        Grade support handling performance.
        
        Returns:
            TaskResult with deterministic score 0.0-1.0
        """
        # ====================================================================
        # 1. Classification Accuracy
        # ====================================================================
        correct_classifications = 0
        total_classified = 0

        for email in env.state.emails:
            if email.handled and email.category is not None:
                total_classified += 1
                if email.category == email.ground_truth_category:
                    correct_classifications += 1

        classification_score = (
            correct_classifications / total_classified if total_classified > 0 else 0.0
        )

        # ====================================================================
        # 2. Support Email Replies
        # ====================================================================
        support_emails = [
            e
            for e in env.state.emails
            if e.category
            in [EmailCategory.TECHNICAL_SUPPORT, EmailCategory.BILLING]
        ]
        replied_count = sum(1 for e in support_emails if e.replied)
        reply_score = replied_count / len(support_emails) if support_emails else 1.0

        # ====================================================================
        # 3. Ticket Resolution
        # ====================================================================
        closed_tickets = sum(
            1
            for t in env.state.tickets
            if t.status == TicketStatus.CLOSED
        )
        total_tickets = len(env.state.tickets)
        resolution_score = (
            closed_tickets / total_tickets if total_tickets > 0 else 1.0
        )

        # ====================================================================
        # Combine
        # ====================================================================
        final_score = (
            classification_score * 0.4
            + reply_score * 0.3
            + resolution_score * 0.3
        )

        summary = env.get_summary()

        return TaskResult(
            task_name=self.task_name,
            total_reward=total_reward,
            final_score=max(0.0, min(1.0, final_score)),
            steps_taken=summary["steps"],
            action_counts=summary["action_counts"],
            success=final_score > 0.65,
            details={
                "classification_accuracy": classification_score,
                "reply_rate": reply_score,
                "resolution_rate": resolution_score,
                "emails_classified": total_classified,
                "emails_correct": correct_classifications,
                "support_emails_replied": replied_count,
                "tickets_closed": closed_tickets,
            },
        )
