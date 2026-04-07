"""
Reward calculation system for the AI Operations Assistant Environment.
Implements a dense, meaningful reward function with multiple components.
"""

from typing import Dict, Optional
from env.models import (
    Email,
    SupportTicket,
    MeetingRequest,
    Action,
    ClassifyEmailAction,
    ReplyEmailAction,
    EscalateTicketAction,
    CloseTicketAction,
    ScheduleMeetingAction,
    DeleteSpamAction,
    EmailCategory,
    TicketStatus,
    Reward,
)


class RewardCalculator:
    """
    Calculates reward for actions taken by the agent.
    
    Reward components:
    - Classification accuracy: +0.3 for correct, -0.3 for incorrect
    - Reply quality: +0.4 for appropriate, -0.2 for inappropriate
    - Ticket resolution: +0.5 for correct, -0.5 for incorrect escalation
    - Meeting scheduling: +0.3 for correct time, -0.2 for wrong time
    - Spam deletion: +0.2 for correct, -0.1 for false positive
    - Step penalty: -0.05 per step (encourages efficiency)
    """

    # ========================================================================
    # Configuration
    # ========================================================================

    # Base rewards for actions
    CORRECT_CLASSIFICATION = 0.3
    INCORRECT_CLASSIFICATION = -0.3
    APPROPRIATE_REPLY = 0.4
    INAPPROPRIATE_REPLY = -0.2
    CORRECT_RESOLUTION = 0.5
    INCORRECT_ESCALATION = -0.5
    CORRECT_MEETING_SCHEDULE = 0.3
    WRONG_MEETING_TIME = -0.2
    CORRECT_SPAM_DELETION = 0.2
    FALSE_POSITIVE_SPAM = -0.1
    STEP_PENALTY = -0.05
    DUPLICATE_ACTION_PENALTY = -0.2

    def __init__(self):
        """Initialize reward calculator."""
        self.email_ground_truth: Dict[str, EmailCategory] = {}
        self.ticket_ground_truth: Dict[str, bool] = {}  # True = should be escalated

    def calculate(
        self,
        action: Action,
        email: Optional[Email] = None,
        ticket: Optional[SupportTicket] = None,
        meeting: Optional[MeetingRequest] = None,
        is_duplicate: bool = False,
        step: int = 0,
    ) -> Reward:
        """
        Calculate reward for an action.
        
        Args:
            action: The action taken by the agent
            email: Related email (if applicable)
            ticket: Related ticket (if applicable)
            meeting: Related meeting (if applicable)
            is_duplicate: Whether this action was already taken on this item
            step: Current step number (for penalties)
        
        Returns:
            Reward object with total and breakdown
        """
        components = {}
        total_reward = 0.0

        # Add step penalty for efficiency
        components["step_penalty"] = self.STEP_PENALTY
        total_reward += self.STEP_PENALTY

        # Handle duplicate actions
        if is_duplicate:
            components["duplicate_penalty"] = self.DUPLICATE_ACTION_PENALTY
            return Reward(
                total=self.DUPLICATE_ACTION_PENALTY,
                components=components,
                explanation="Duplicate action on same item",
            )

        # ====================================================================
        # Classify Email Action
        # ====================================================================
        if isinstance(action, ClassifyEmailAction):
            assert email is not None, "Email required for classification action"
            reward = self._reward_classify_email(action, email, components)
            total_reward += reward

        # ====================================================================
        # Reply Email Action
        # ====================================================================
        elif isinstance(action, ReplyEmailAction):
            assert email is not None, "Email required for reply action"
            reward = self._reward_reply_email(action, email, components)
            total_reward += reward

        # ====================================================================
        # Escalate Ticket Action
        # ====================================================================
        elif isinstance(action, EscalateTicketAction):
            assert ticket is not None, "Ticket required for escalation action"
            reward = self._reward_escalate_ticket(action, ticket, components)
            total_reward += reward

        # ====================================================================
        # Close Ticket Action
        # ====================================================================
        elif isinstance(action, CloseTicketAction):
            assert ticket is not None, "Ticket required for close action"
            reward = self._reward_close_ticket(action, ticket, components)
            total_reward += reward

        # ====================================================================
        # Schedule Meeting Action
        # ====================================================================
        elif isinstance(action, ScheduleMeetingAction):
            assert meeting is not None, "Meeting required for scheduling action"
            reward = self._reward_schedule_meeting(action, meeting, components)
            total_reward += reward

        # ====================================================================
        # Delete Spam Action
        # ====================================================================
        elif isinstance(action, DeleteSpamAction):
            assert email is not None, "Email required for spam deletion action"
            reward = self._reward_delete_spam(action, email, components)
            total_reward += reward

        else:
            raise ValueError(f"Unknown action type: {type(action)}")

        explanation = self._build_explanation(action, components)

        return Reward(
            total=total_reward,
            components=components,
            explanation=explanation,
        )

    # ========================================================================
    # Individual Reward Calculators
    # ========================================================================

    def _reward_classify_email(
        self,
        action: ClassifyEmailAction,
        email: Email,
        components: Dict[str, float],
    ) -> float:
        """Reward for email classification."""
        # Ground truth is stored separately from the agent-assigned category.
        expected_category = email.ground_truth_category or email.category

        if action.category == expected_category:
            reward = self.CORRECT_CLASSIFICATION
            components["classification"] = reward
            return reward
        else:
            reward = self.INCORRECT_CLASSIFICATION
            components["classification"] = reward
            return reward

    def _reward_reply_email(
        self,
        action: ReplyEmailAction,
        email: Email,
        components: Dict[str, float],
    ) -> float:
        """Reward for replying to email."""
        # Heuristics for appropriate reply
        reward = 0.0

        # Check if reply content is substantial
        reply_length = len(action.reply_content.strip().split())
        if reply_length < 2:
            reward = self.INAPPROPRIATE_REPLY
            components["reply_quality"] = reward
            return reward

        # Check for keywords that suggest quality response
        positive_keywords = ["thank", "help", "please", "solution", "contact", "support"]
        negative_keywords = ["spam", "scam", "delete", "ignore"]

        reply_lower = action.reply_content.lower()
        has_positive = any(kw in reply_lower for kw in positive_keywords)
        has_negative = any(kw in reply_lower for kw in negative_keywords)

        if has_negative:
            reward = self.INAPPROPRIATE_REPLY
        elif has_positive or reply_length > 5:
            reward = self.APPROPRIATE_REPLY
        else:
            reward = self.APPROPRIATE_REPLY * 0.7  # Partial credit

        components["reply_quality"] = reward
        return reward

    def _reward_escalate_ticket(
        self,
        action: EscalateTicketAction,
        ticket: SupportTicket,
        components: Dict[str, float],
    ) -> float:
        """Reward for escalating a ticket."""
        # Check if escalation reason makes sense for severity
        reason_lower = action.escalation_reason.lower()
        urgency_keywords = {"critical": ["urgent", "critical", "emergency", "immediate"],
                           "high": ["high", "important", "urgent", "important"],
                           "medium": ["issue", "problem", "needs attention"]}

        severity_str = ticket.severity.value
        appropriate_keywords = urgency_keywords.get(severity_str, [])
        has_appropriate_reason = any(kw in reason_lower for kw in appropriate_keywords)

        # Critical and high severity should be escalated, low should not
        if ticket.severity.value in ["critical", "high"]:
            if has_appropriate_reason:
                reward = 0.2  # Good escalation
            else:
                reward = 0.1  # Escalation was right but reason weak
        else:
            reward = self.INCORRECT_ESCALATION  # Unnecessary escalation

        components["escalation"] = reward
        return reward

    def _reward_close_ticket(
        self,
        action: CloseTicketAction,
        ticket: SupportTicket,
        components: Dict[str, float],
    ) -> float:
        """Reward for closing a ticket."""
        # Check if resolution is substantial
        resolution_length = len(action.resolution.strip().split())
        if resolution_length < 3:
            reward = -0.2
            components["ticket_resolution"] = reward
            return reward

        # Check resolution quality based on severity
        resolution_lower = action.resolution.lower()
        resolution_keywords = ["fixed", "resolved", "solved", "addressed", "provided", "explained"]
        has_resolution = any(kw in resolution_lower for kw in resolution_keywords)

        if has_resolution:
            # Higher severity = higher reward for resolution
            severity_multiplier = {
                "critical": 1.5,
                "high": 1.2,
                "medium": 1.0,
                "low": 0.8,
            }.get(ticket.severity.value, 1.0)

            reward = self.CORRECT_RESOLUTION * severity_multiplier * 0.6
        else:
            reward = 0.1  # Partial credit for attempt

        components["ticket_resolution"] = reward
        return reward

    def _reward_schedule_meeting(
        self,
        action: ScheduleMeetingAction,
        meeting: MeetingRequest,
        components: Dict[str, float],
    ) -> float:
        """Reward for scheduling a meeting."""
        # Check if scheduled time is reasonable (not in the past, reasonable urgency match)
        import datetime as dt

        now = dt.datetime.now() if action.scheduled_time.tzinfo is None else dt.datetime.now(
            dt.timezone.utc
        )
        if action.scheduled_time < now:
            reward = -0.3
        elif action.scheduled_time < action.scheduled_time.replace(hour=8):
            # Before work hours
            reward = -0.1
        else:
            # Check urgency match
            time_to_meeting = (action.scheduled_time - now).total_seconds() / 3600
            if meeting.urgency == "high" and time_to_meeting > 24:
                reward = self.CORRECT_MEETING_SCHEDULE * 0.7  # Scheduled but delayed
            else:
                reward = self.CORRECT_MEETING_SCHEDULE

        components["meeting_scheduling"] = reward
        return reward

    def _reward_delete_spam(
        self,
        action: DeleteSpamAction,
        email: Email,
        components: Dict[str, float],
    ) -> float:
        """Reward for deleting spam."""
        # Check if email is actually spam
        ground_truth_category = email.ground_truth_category or email.category
        if ground_truth_category == EmailCategory.SPAM:
            reward = self.CORRECT_SPAM_DELETION
        else:
            reward = self.FALSE_POSITIVE_SPAM  # Wrongly deleted legitimate email

        components["spam_deletion"] = reward
        return reward

    # ========================================================================
    # Utilities
    # ========================================================================

    def _build_explanation(self, action: Action, components: Dict[str, float]) -> str:
        """Build human-readable explanation of reward."""
        parts = []
        action_type = action.action_type

        if action_type == "classify_email":
            if components.get("classification", 0) > 0:
                parts.append("Correct email classification")
            else:
                parts.append("Incorrect email classification")

        elif action_type == "reply_email":
            quality = components.get("reply_quality", 0)
            if quality > 0.2:
                parts.append("Good quality reply sent")
            elif quality > 0:
                parts.append("Adequate reply sent")
            else:
                parts.append("Poor quality reply")

        elif action_type == "escalate_ticket":
            parts.append(f"Ticket escalation (reason quality: {components.get('escalation', 0):.2f})")

        elif action_type == "close_ticket":
            resolution = components.get("ticket_resolution", 0)
            parts.append(f"Ticket closed (resolution quality: {resolution:.2f})")

        elif action_type == "schedule_meeting":
            parts.append("Meeting scheduled")

        elif action_type == "delete_spam":
            if components.get("spam_deletion", 0) > 0:
                parts.append("Correctly identified and deleted spam")
            else:
                parts.append("False positive: deleted legitimate email")

        # Add step penalty note
        if components.get("step_penalty", 0) < 0:
            parts.append(f"Step efficiency penalty: {components.get('step_penalty', 0):.2f}")

        return "; ".join(parts) if parts else "Action processed"

    def set_email_ground_truth(self, email_id: str, category: EmailCategory) -> None:
        """Set ground truth for an email."""
        self.email_ground_truth[email_id] = category

    def set_ticket_ground_truth(self, ticket_id: str, should_escalate: bool) -> None:
        """Set ground truth for a ticket."""
        self.ticket_ground_truth[ticket_id] = should_escalate
