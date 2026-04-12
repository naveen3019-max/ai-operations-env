"""
MEDIUM Task: Support Ticket and Email Handling

Difficulty: MEDIUM (🟡)
Focus: Email classification + ticket resolution
Goal: Classify emails, reply where appropriate, and resolve tickets

Agent must:
1. Classify emails
2. Reply to support-related emails appropriately
3. Close low-priority tickets
4. Handle dependencies (must classify before replying)
"""

from typing import Dict, Any
from tasks.base_task import BaseTask
from env.models import EmailCategory, TicketStatus, TaskResult


class MediumSupportHandlingTask(BaseTask):
    """
    Medium task: email classification and ticket resolution.
    
    Environment: 5-7 emails + 2-3 tickets
    Objective: Classify emails, reply appropriately, resolve tickets
    Challenges: Dependencies, prioritization, appropriate responses
    """

    def __init__(self, max_steps: int = 75):
        """Initialize medium task."""
        super().__init__(
            name="Support Handling",
            description="Classify emails, reply to support requests, and resolve tickets efficiently",
            difficulty="medium",
            max_steps=max_steps,
            grader_name="medium",
            grader_module="graders.grader_medium",
            grader_class="MediumGrader",
        )
        self.expected_classifications: Dict[str, EmailCategory] = {}
        self.total_emails: int = 0
        self.total_tickets: int = 0
        self.support_email_ids = set()  # Email IDs that are support tickets

    def _populate_environment(self) -> None:
        """Populate with emails and tickets."""
        self.expected_classifications.clear()
        self.support_email_ids.clear()

        # Add emails
        num_emails = 6
        self.env.populate_with_emails(count=num_emails)
        self.total_emails = num_emails

        # Identify support-related emails for reply grading
        for email in self.env._state.emails:
            self.expected_classifications[email.id] = email.ground_truth_category
            if email.ground_truth_category in [
                EmailCategory.TECHNICAL_SUPPORT,
                EmailCategory.BILLING,
            ]:
                self.support_email_ids.add(email.id)

        # Add tickets
        num_tickets = 2
        self.env.populate_with_tickets(count=num_tickets)
        self.total_tickets = num_tickets

    def evaluate(self, env) -> TaskResult:
        """
        Evaluate support handling performance.
        
        Scoring based on:
        1. Email classification accuracy (40%)
        2. Support email replies quality (30%)
        3. Ticket resolution rate (30%)
        """
        summary = env.get_summary()

        # ====================================================================
        # 1. Email Classification Accuracy
        # ====================================================================
        correct_classifications = 0
        total_classified = 0

        for email in env._state.emails:
            if email.handled and email.category is not None:
                total_classified += 1
                expected = self.expected_classifications.get(email.id)
                if email.category == expected:
                    correct_classifications += 1

        classification_score = (
            correct_classifications / total_classified
            if total_classified > 0
            else 0.0
        )

        # ====================================================================
        # 2. Support Email Reply Quality
        # ====================================================================
        replied_support_emails = 0
        for email in env._state.emails:
            if email.id in self.support_email_ids and email.replied:
                replied_support_emails += 1

        reply_coverage = (
            replied_support_emails / len(self.support_email_ids)
            if self.support_email_ids
            else 0.0
        )

        # ====================================================================
        # 3. Ticket Resolution
        # ====================================================================
        closed_tickets = 0
        for ticket in env._state.tickets:
            if ticket.status == TicketStatus.CLOSED:
                closed_tickets += 1

        ticket_resolution_rate = closed_tickets / self.total_tickets if self.total_tickets > 0 else 0.0

        # ====================================================================
        # Combine scores
        # ====================================================================
        score = (
            classification_score * 0.4
            + reply_coverage * 0.3
            + ticket_resolution_rate * 0.3
        )

        details = {
            "classification_accuracy": classification_score,
            "support_reply_coverage": reply_coverage,
            "ticket_resolution_rate": ticket_resolution_rate,
            "emails_classified": total_classified,
            "correct_classifications": correct_classifications,
            "support_emails_replied": replied_support_emails,
            "tickets_closed": closed_tickets,
            "total_tickets": self.total_tickets,
        }

        return TaskResult(
            task_name=self.name,
            total_reward=summary["total_reward"],
            final_score=max(0.0, min(1.0, score)),
            steps_taken=summary["steps"],
            action_counts=summary["action_counts"],
            success=score > 0.65,
            details=details,
        )
