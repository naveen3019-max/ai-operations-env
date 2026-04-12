"""
HARD Task: Full Operations Management

Difficulty: HARD (🔴)
Focus: Complete operations workflow
Goal: Optimize all tasks simultaneously with proper prioritization

Agent must:
1. Classify emails correctly
2. Reply to support requests
3. Close routine tickets
4. Escalate critical issues
5. Schedule meetings at appropriate times
6. Prioritize urgent items
7. Manage complex dependencies
"""

from typing import Dict, Any
from datetime import datetime
from tasks.base_task import BaseTask
from env.models import EmailCategory, TicketStatus, MeetingStatus, TicketSeverity, EmailPriority, TaskResult


class HardFullOperationsTask(BaseTask):
    """
    Hard task: Full operations management.
    
    Environment: 8-10 emails + 3-4 tickets + 2-3 meeting requests
    Objective: Manage all workflow types simultaneously
    Challenges:
    - Prioritization (urgent items first)
    - Dependencies (classify before reply)
    - Resource constraints (limited steps)
    - Realistic action sequences
    """
    grader = "hard"
    grader_path = "graders.grader_hard.HardGrader"
    grader_key = "hard"
    grader_name = "hard"
    grader_module = "graders.grader_hard"
    grader_class = "HardGrader"
    grader_enabled = True

    def __init__(self, max_steps: int = 120):
        """Initialize hard task."""
        super().__init__(
            name="Full Operations Management",
            description="Manage emails, tickets, and meetings with prioritization and efficiency",
            difficulty="hard",
            max_steps=max_steps,
            grader_name="hard",
            grader_module="graders.grader_hard",
            grader_class="HardGrader",
        )
        self.expected_classifications: Dict[str, EmailCategory] = {}
        self.total_emails: int = 0
        self.total_tickets: int = 0
        self.total_meetings: int = 0
        self.urgent_items: Dict[str, int] = {}  # ID -> urgency score

    def _populate_environment(self) -> None:
        """Populate with emails, tickets, and meetings."""
        self.expected_classifications.clear()
        self.urgent_items.clear()

        # Add emails (mix of urgent and routine)
        num_emails = 9
        self.env.populate_with_emails(count=num_emails)
        self.total_emails = num_emails

        for email in self.env._state.emails:
            self.expected_classifications[email.id] = email.ground_truth_category
            # Score urgency: critical=3, high=2, medium=1, low=0
            urgency_map = {"critical": 3, "high": 2, "medium": 1, "low": 0}
            self.urgent_items[email.id] = urgency_map.get(
                email.priority.value, 0
            )

        # Add tickets (including at least one critical)
        num_tickets = 3
        self.env.populate_with_tickets(count=num_tickets)
        self.total_tickets = num_tickets

        # Ensure at least one critical ticket
        if self.env._state.tickets:
            self.env._state.tickets[0].severity = TicketSeverity.CRITICAL
            self.urgent_items[self.env._state.tickets[0].id] = 3

        for ticket in self.env._state.tickets:
            if ticket.id not in self.urgent_items:
                severity_map = {"critical": 3, "high": 2, "medium": 1, "low": 0}
                self.urgent_items[ticket.id] = severity_map.get(
                    ticket.severity.value, 0
                )

        # Add meetings
        num_meetings = 2
        self.env.populate_with_meetings(count=num_meetings)
        self.total_meetings = num_meetings

        for meeting in self.env._state.meetings:
            urgency_map = {"high": 3, "medium": 2, "low": 1}
            self.urgent_items[meeting.id] = urgency_map.get(meeting.urgency, 1)

    def evaluate(self, env) -> TaskResult:
        """
        Evaluate full operations performance.
        
        Scoring based on:
        1. Email classification (25%)
        2. Support email replies (20%)
        3. Ticket escalation/closure decisions (25%)
        4. Meeting scheduling (15%)
        5. Prioritization quality (15%)
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
        ) * 0.25

        # ====================================================================
        # 2. Support Email Replies
        # ====================================================================
        support_emails = [
            e
            for e in env._state.emails
            if e.category in [EmailCategory.TECHNICAL_SUPPORT, EmailCategory.BILLING]
        ]
        replied_count = sum(1 for e in support_emails if e.replied)
        reply_score = (
            (replied_count / len(support_emails) if support_emails else 1.0) * 0.2
        )

        # ====================================================================
        # 3. Ticket Handling Quality
        # ====================================================================
        critical_tickets = [
            t for t in env._state.tickets if t.severity == TicketSeverity.CRITICAL
        ]
        critical_escalated = sum(
            1
            for t in critical_tickets
            if t.status in [TicketStatus.ESCALATED, TicketStatus.CLOSED]
        )
        low_tickets = [
            t for t in env._state.tickets if t.severity == TicketSeverity.LOW
        ]
        low_closed = sum(1 for t in low_tickets if t.status == TicketStatus.CLOSED)

        ticket_quality = 0.0
        if critical_tickets:
            critical_handling = critical_escalated / len(critical_tickets)
            ticket_quality += critical_handling * 0.15

        if low_tickets:
            low_handling = low_closed / len(low_tickets)
            ticket_quality += low_handling * 0.1

        ticket_score = min(ticket_quality, 0.25)

        # ====================================================================
        # 4. Meeting Scheduling
        # ====================================================================
        scheduled_meetings = sum(
            1
            for m in env._state.meetings
            if m.status == MeetingStatus.SCHEDULED
        )
        meeting_score = (
            (
                scheduled_meetings / len(env._state.meetings)
                if env._state.meetings
                else 1.0
            )
            * 0.15
        )

        # ====================================================================
        # 5. Prioritization Quality
        # ====================================================================
        # Check if urgent items were handled earlier in the sequence
        prioritization_score = self._evaluate_prioritization(env)

        # ====================================================================
        # Combine scores
        # ====================================================================
        total_score = (
            classification_score
            + reply_score
            + ticket_score
            + meeting_score
            + prioritization_score
        )

        details = {
            "classification_accuracy": correct_classifications / total_classified if total_classified else 0.0,
            "emails_classified": total_classified,
            "correct_classifications": correct_classifications,
            "support_replies": replied_count,
            "total_support_emails": len(support_emails),
            "critical_tickets_handled": critical_escalated,
            "total_critical": len(critical_tickets),
            "low_tickets_closed": low_closed,
            "total_low": len(low_tickets),
            "meetings_scheduled": scheduled_meetings,
            "total_meetings": len(env._state.meetings),
            "prioritization_score": prioritization_score,
        }

        return TaskResult(
            task_name=self.name,
            total_reward=summary["total_reward"],
            final_score=max(0.0, min(1.0, total_score)),
            steps_taken=summary["steps"],
            action_counts=summary["action_counts"],
            success=total_score > 0.6,
            details=details,
        )

    def _evaluate_prioritization(self, env) -> float:
        """
        Evaluate how well the agent prioritized urgent items.
        
        Urgent items should be processed earlier in the action sequence.
        """
        if not env.action_history:
            return 0.0

        # Build a mapping of when items were processed
        processed_at_step = {}
        for step, (action, target_id) in enumerate(env.action_history):
            if target_id not in processed_at_step:
                processed_at_step[target_id] = step

        # Calculate prioritization score
        score = 0.0
        for item_id, urgency in self.urgent_items.items():
            if item_id in processed_at_step:
                processed_step = processed_at_step[item_id]
                # Higher urgency items processed earlier = better
                # Max 100 steps, so normalize
                step_penalty = processed_step / max(100, len(env.action_history))
                item_score = (urgency / 3.0) * (1.0 - step_penalty * 0.5)
                score += item_score

        # Normalize to 0-0.15 range
        total_urgency = sum(self.urgent_items.values())
        if total_urgency > 0:
            score = (score / total_urgency) * 0.15

        return min(0.15, max(0.0, score))
