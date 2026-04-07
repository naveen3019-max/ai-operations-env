"""
Baseline agent for the AI Operations Assistant Environment.

A rule-based agent that:
1. Detects email categories using keywords
2. Replies to support emails appropriately
3. Escalates critical tickets
4. Closes routine tickets
5. Schedules meetings
6. Deletes spam

Used for benchmarking and reproducible evaluation.
"""

from datetime import datetime, timedelta
from typing import Optional

from env.environment import AIOperationsEnvironment
from env.models import (
    Observation,
    Action,
    ClassifyEmailAction,
    ReplyEmailAction,
    EscalateTicketAction,
    CloseTicketAction,
    ScheduleMeetingAction,
    DeleteSpamAction,
    EmailCategory,
    TicketStatus,
    TicketSeverity,
    MeetingStatus,
)


class BaselineAgent:
    """
    Rule-based baseline agent for the operations environment.
    
    Strategy:
    1. Process emails first (classify, reply, delete spam)
    2. Process tickets (escalate critical, close routine)
    3. Schedule meetings at appropriate times
    """

    def __init__(self, seed: int = 42):
        """Initialize agent."""
        self.seed = seed
        self.processed_item_ids = set()

    def reset(self):
        """Reset agent state."""
        self.processed_item_ids = set()

    def select_action(self, observation: Observation) -> Optional[Action]:
        """
        Select next action based on observation.
        
        Priority:
        1. Classify unclassified emails
        2. Reply to support emails
        3. Delete spam
        4. Handle tickets
        5. Schedule meetings
        
        Args:
            observation: Current observation
        
        Returns:
            Next action or None if episode is complete
        """
        # ====================================================================
        # Priority 1: Classify unclassified emails
        # ====================================================================
        for email in observation.emails:
            if not email.handled and email.id not in self.processed_item_ids:
                category = self._classify_email(email.subject + " " + email.body)
                action = ClassifyEmailAction(
                    email_id=email.id,
                    category=category,
                )
                self.processed_item_ids.add(email.id)
                return action

        # ====================================================================
        # Priority 2: Reply to support-related emails
        # ====================================================================
        for email in observation.emails:
            if (
                email.handled
                and not email.replied
                and email.category
                in [EmailCategory.TECHNICAL_SUPPORT, EmailCategory.BILLING]
                and email.id not in self.processed_item_ids
            ):
                reply = self._generate_reply(email.category, email.subject)
                action = ReplyEmailAction(
                    email_id=email.id,
                    reply_content=reply,
                )
                self.processed_item_ids.add(email.id)
                return action

        # ====================================================================
        # Priority 3: Delete spam emails
        # ====================================================================
        for email in observation.emails:
            if (
                email.category == EmailCategory.SPAM
                and email.id not in self.processed_item_ids
            ):
                action = DeleteSpamAction(email_id=email.id)
                self.processed_item_ids.add(email.id)
                return action

        # ====================================================================
        # Priority 4: Handle critical tickets first
        # ====================================================================
        for ticket in observation.tickets:
            if ticket.status == TicketStatus.OPEN and ticket.id not in self.processed_item_ids:
                if ticket.severity == TicketSeverity.CRITICAL:
                    action = EscalateTicketAction(
                        ticket_id=ticket.id,
                        escalation_reason=f"Critical severity: {ticket.issue}",
                    )
                    self.processed_item_ids.add(ticket.id)
                    return action

        # ====================================================================
        # Priority 5: Close routine tickets
        # ====================================================================
        for ticket in observation.tickets:
            if (
                ticket.status == TicketStatus.OPEN
                and ticket.severity
                in [TicketSeverity.LOW, TicketSeverity.MEDIUM]
                and ticket.id not in self.processed_item_ids
            ):
                resolution = f"Resolved issue: {ticket.issue}"
                action = CloseTicketAction(
                    ticket_id=ticket.id,
                    resolution=resolution,
                )
                self.processed_item_ids.add(ticket.id)
                return action

        # ====================================================================
        # Priority 6: Schedule urgent meetings
        # ====================================================================
        for meeting in observation.meetings:
            if (
                meeting.status == MeetingStatus.REQUESTED
                and meeting.id not in self.processed_item_ids
            ):
                if meeting.urgency == "high":
                    # Schedule within 24 hours
                    scheduled_time = datetime.now() + timedelta(hours=4)
                else:
                    # Schedule within a week
                    scheduled_time = datetime.now() + timedelta(days=2)

                action = ScheduleMeetingAction(
                    meeting_id=meeting.id,
                    scheduled_time=scheduled_time,
                )
                self.processed_item_ids.add(meeting.id)
                return action

        # ====================================================================
        # No more actions
        # ====================================================================
        return None

    def _classify_email(self, content: str) -> EmailCategory:
        """
        Classify email based on keyword matching.
        
        Args:
            content: Email subject + body
        
        Returns:
            EmailCategory
        """
        content_lower = content.lower()

        # Check for spam first (highest confidence)
        spam_keywords = [
            "claim your",
            "winner",
            "congratulations",
            "free money",
            "act now",
            "limited time",
            "urgency",
            "!!!",
            "click here",
            "unclaimed",
        ]
        if any(keyword in content_lower for keyword in spam_keywords):
            return EmailCategory.SPAM

        # Product inquiry
        product_keywords = [
            "features",
            "pricing",
            "plan",
            "integration",
            "api",
            "how to",
            "can i",
        ]
        if any(keyword in content_lower for keyword in product_keywords):
            return EmailCategory.PRODUCT_INQUIRY

        # Billing
        billing_keywords = [
            "invoice",
            "charge",
            "payment",
            "refund",
            "billing",
            "subscription",
            "account",
        ]
        if any(keyword in content_lower for keyword in billing_keywords):
            return EmailCategory.BILLING

        # Technical support
        support_keywords = [
            "error",
            "crash",
            "bug",
            "not working",
            "broken",
            "issue",
            "problem",
            "slow",
            "timeout",
            "fail",
        ]
        if any(keyword in content_lower for keyword in support_keywords):
            return EmailCategory.TECHNICAL_SUPPORT

        # Feedback
        feedback_keywords = [
            "feedback",
            "suggestion",
            "improve",
            "great",
            "love",
            "like",
            "thank",
            "awesome",
        ]
        if any(keyword in content_lower for keyword in feedback_keywords):
            return EmailCategory.FEEDBACK

        # Default
        return EmailCategory.UNKNOWN

    def _generate_reply(self, category: EmailCategory, subject: str) -> str:
        """
        Generate appropriate reply based on category.
        
        Args:
            category: Email category
            subject: Email subject
        
        Returns:
            Reply text
        """
        replies = {
            EmailCategory.TECHNICAL_SUPPORT: "Thank you for reporting this issue. Our technical team is looking into it. We'll provide an update within 24 hours.",
            EmailCategory.BILLING: "Thank you for your inquiry. We're reviewing your account and will resolve this shortly. Please allow 1-2 business days for processing.",
            EmailCategory.PRODUCT_INQUIRY: "Thank you for your interest in our product. I'd be happy to discuss our features and pricing. Please let me know your specific needs.",
            EmailCategory.FEEDBACK: "Thank you for the feedback! We appreciate your input and will take it into consideration for future improvements.",
        }

        return replies.get(category, "Thank you for your message. We'll get back to you shortly.")

    def run_episode(
        self,
        env: AIOperationsEnvironment,
        max_steps: int = 100,
        verbose: bool = False,
        reset_env: bool = False,
    ) -> tuple:
        """
        Run a complete episode using this agent.
        
        Args:
            env: Environment to run in
            max_steps: Maximum steps
            verbose: Print actions
            reset_env: Whether to call env.reset() (default False for task-managed envs)
        
        Returns:
            (total_reward, final_observation)
        """
        self.reset()
        
        # Only reset if requested (tasks handle their own reset)
        if reset_env:
            observation = env.reset()
        else:
            observation = env._get_observation()
        
        total_reward = 0.0
        step = 0

        while step < max_steps:
            action = self.select_action(observation)

            if action is None:
                if verbose:
                    print(f"Step {step}: No more actions")
                break

            observation, reward, done, info = env.step(action)
            total_reward += reward
            step += 1

            if verbose:
                print(f"Step {step}: {action.action_type} -> reward: {reward:.3f}")

            if done:
                break

        summary = env.get_summary()
        if verbose:
            print(f"\nEpisode Summary:")
            print(f"  Total Reward: {total_reward:.3f}")
            print(f"  Steps: {step}")
            print(f"  Actions: {summary['action_counts']}")

        return total_reward, observation
