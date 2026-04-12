"""
Grader for HARD task: Full Operations Management
"""

from graders.base_grader import BaseGrader
from env.environment import AIOperationsEnvironment
from env.models import TaskResult, EmailCategory, TicketStatus, TicketSeverity, MeetingStatus


class HardGrader(BaseGrader):
    """
    Grades full operations management task.
    
    Deterministic scoring based on:
    1. Email classification accuracy (25%)
    2. Support reply rate (20%)
    3. Critical ticket handling (20%)
    4. Low ticket closure (10%)
    5. Meeting scheduling (15%)
    6. Efficiency bonus (10%)
    """

    def __init__(self):
        """Initialize hard grader."""
        super().__init__("Full Operations Management")

    def grade(self, env: AIOperationsEnvironment, total_reward: float) -> TaskResult:
        """
        Grade full operations performance deterministically.
        
        Returns:
            TaskResult with deterministic score 0.0-1.0
        """
        state = env.state_obj

        # ====================================================================
        # 1. Email Classification Accuracy (25%)
        # ====================================================================
        correct_classifications = 0
        total_classified = 0

        for email in state.emails:
            if email.handled and email.category is not None:
                total_classified += 1
                if email.category == email.ground_truth_category:
                    correct_classifications += 1

        classification_score = (
            correct_classifications / total_classified if total_classified > 0 else 0.0
        ) * 0.25

        # ====================================================================
        # 2. Support Email Replies (20%)
        # ====================================================================
        support_emails = [
            e
            for e in state.emails
            if e.category
            in [EmailCategory.TECHNICAL_SUPPORT, EmailCategory.BILLING]
        ]
        replied_count = sum(1 for e in support_emails if e.replied)
        reply_score = (
            (replied_count / len(support_emails) if support_emails else 1.0) * 0.20
        )

        # ====================================================================
        # 3. Critical Ticket Handling (20%)
        # ====================================================================
        critical_tickets = [
            t for t in state.tickets if t.severity == TicketSeverity.CRITICAL
        ]
        critical_handled = sum(
            1
            for t in critical_tickets
            if t.status in [TicketStatus.ESCALATED, TicketStatus.CLOSED]
        )
        critical_score = (
            (critical_handled / len(critical_tickets) if critical_tickets else 1.0)
            * 0.20
        )

        # ====================================================================
        # 4. Low Ticket Closure (10%)
        # ====================================================================
        low_tickets = [
            t for t in state.tickets if t.severity == TicketSeverity.LOW
        ]
        low_closed = sum(1 for t in low_tickets if t.status == TicketStatus.CLOSED)
        low_score = (
            (low_closed / len(low_tickets) if low_tickets else 1.0) * 0.10
        )

        # ====================================================================
        # 5. Meeting Scheduling (15%)
        # ====================================================================
        scheduled_meetings = sum(
            1
            for m in state.meetings
            if m.status == MeetingStatus.SCHEDULED
        )
        meeting_score = (
            (
                scheduled_meetings / len(state.meetings)
                if state.meetings
                else 1.0
            )
            * 0.15
        )

        # ====================================================================
        # 6. Efficiency Bonus (10%)
        # ====================================================================
        # Bonus for using fewer steps (max 120)
        steps_ratio = min(1.0, state.step / 120.0)
        efficiency_bonus = (1.0 - steps_ratio * 0.3) * 0.10  # Up to 10% if very efficient

        # ====================================================================
        # Combine all scores
        # ====================================================================
        final_score = (
            classification_score
            + reply_score
            + critical_score
            + low_score
            + meeting_score
            + efficiency_bonus
        )

        summary = env.get_summary()

        return TaskResult(
            task_name=self.task_name,
            total_reward=total_reward,
            final_score=self.strict_score(final_score),
            steps_taken=summary["steps"],
            action_counts=summary["action_counts"],
            success=final_score > 0.60,
            details=self.sanitize_metrics(
                {
                    "classification_accuracy": correct_classifications / total_classified if total_classified else 0.0,
                    "reply_rate": replied_count / len(support_emails) if support_emails else 1.0,
                    "critical_handling_rate": critical_handled / len(critical_tickets) if critical_tickets else 1.0,
                    "low_closure_rate": low_closed / len(low_tickets) if low_tickets else 1.0,
                    "meeting_scheduling_rate": scheduled_meetings / len(state.meetings) if state.meetings else 1.0,
                    "efficiency_score": efficiency_bonus,
                    "total_emails": len(state.emails),
                    "total_tickets": len(state.tickets),
                    "total_meetings": len(state.meetings),
                }
            ),
        )
