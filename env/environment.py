"""
AI Operations Assistant Environment.
OpenEnv-compliant environment for training and evaluating AI agents on business workflows.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

from env.models import (
    Email,
    EmailPriority,
    EmailCategory,
    SupportTicket,
    TicketSeverity,
    TicketStatus,
    MeetingRequest,
    MeetingStatus,
    Action,
    ClassifyEmailAction,
    ReplyEmailAction,
    EscalateTicketAction,
    CloseTicketAction,
    ScheduleMeetingAction,
    DeleteSpamAction,
    Observation,
    EnvironmentState,
    Reward,
)
from env.reward import RewardCalculator


class AIOperationsEnvironment:
    """
    Production-grade OpenEnv environment for AI Operations Assistant.
    
    Simulates enterprise workflows including:
    - Email handling and classification
    - Customer support ticket management
    - Meeting scheduling
    
    OpenEnv Interface:
    - reset() -> Observation
    - step(action: Action) -> (Observation, Reward, done: bool, info: dict)
    - state() -> dict
    """

    def __init__(self, seed: int = 42, max_steps: int = 100):
        """
        Initialize environment.
        
        Args:
            seed: Random seed for reproducibility
            max_steps: Maximum steps per episode
        """
        self.seed_value = seed
        self.max_steps = max_steps
        random.seed(seed)

        # Initialize state (use _state to avoid naming conflict with state() method)
        self._state: EnvironmentState = EnvironmentState()
        self.reward_calculator = RewardCalculator()
        self.action_history: List[Tuple[Action, str]] = []  # (action, target_id)
        self.processed_items: Dict[str, set] = {  # Track what's been processed
            "emails": set(),
            "tickets": set(),
            "meetings": set(),
        }

    @property
    def state_obj(self) -> EnvironmentState:
        """Access internal state object (for internal use)."""
        return self._state

    # ========================================================================
    # OpenEnv Interface
    # ========================================================================

    def reset(self) -> Observation:
        """
        Reset environment to initial state.
        
        Returns:
            Initial observation
        """
        self._state = EnvironmentState()
        self.action_history = []
        self.processed_items = {"emails": set(), "tickets": set(), "meetings": set()}
        return self._get_observation()

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """
        Execute one action in the environment.
        
        Args:
            action: Action to execute
        
        Returns:
            (observation, reward, done, info)
        """
        self._state.step += 1

        # Check if action is valid
        target_id = self._get_action_target_id(action)
        is_duplicate = self._is_duplicate_action(action, target_id)

        # Get related entity
        email = self._find_email(target_id) if isinstance(
            action,
            (ClassifyEmailAction, ReplyEmailAction, DeleteSpamAction),
        ) else None
        ticket = self._find_ticket(target_id) if isinstance(
            action,
            (EscalateTicketAction, CloseTicketAction),
        ) else None
        meeting = self._find_meeting(target_id) if isinstance(
            action,
            ScheduleMeetingAction,
        ) else None

        # Calculate reward
        reward_obj = self.reward_calculator.calculate(
            action=action,
            email=email,
            ticket=ticket,
            meeting=meeting,
            is_duplicate=is_duplicate,
            step=self._state.step,
        )

        # Execute action
        if not is_duplicate:
            self._execute_action(action, email, ticket, meeting)
            self.processed_items[self._get_action_domain(action)].add(target_id)

        # Record action and reward
        self.action_history.append(
            (
                action,
                target_id,
            )
        )
        self._state.reward_history.append(reward_obj.total)
        self._state.episode_reward += reward_obj.total

        # Determine if episode is done
        done = self._state.step >= self.max_steps or self._check_natural_completion()

        # Create info dict
        info = {
            "action_type": action.action_type,
            "reward_components": reward_obj.components,
            "reward_explanation": reward_obj.explanation,
            "is_duplicate": is_duplicate,
            "step": self._state.step,
            "episode_reward": self._state.episode_reward,
        }

        observation = self._get_observation()

        return observation, float(reward_obj.total), done, info

    def state(self) -> Dict[str, Any]:
        """
        Get complete environment state.
        
        Returns:
            Dictionary with full state information
        """
        return {
            "step": self._state.step,
            "episode_reward": self._state.episode_reward,
            "emails": [e.dict() for e in self._state.emails],
            "tickets": [t.dict() for t in self._state.tickets],
            "meetings": [m.dict() for m in self._state.meetings],
            "processed_items": self.processed_items,
            "action_history": [
                {
                    "action": a.dict(),
                    "target_id": t,
                } for a, t in self.action_history
            ],
            "reward_history": self._state.reward_history,
        }

    # ========================================================================
    # Observation Generation
    # ========================================================================

    def _get_observation(self) -> Observation:
        """Generate current observation."""
        return Observation(
            step=self._state.step,
            emails=self._state.emails,
            tickets=self._state.tickets,
            meetings=self._state.meetings,
            done=self._state.step >= self.max_steps or self._check_natural_completion(),
            info={
                "episode_reward": self._state.episode_reward,
                "processed_items": self.processed_items,
            },
        )

    # ========================================================================
    # Population Methods
    # ========================================================================

    def populate_with_emails(self, count: int = 5) -> None:
        """
        Populate environment with random emails.
        
        Args:
            count: Number of emails to generate
        """
        categories = list(EmailCategory)
        priorities = list(EmailPriority)
        senders = [
            "customer@example.com",
            "support@vendor.com",
            "sales@company.com",
            "user123@mail.com",
            "feedback@sender.com",
        ]

        email_templates = {
            EmailCategory.PRODUCT_INQUIRY: [
                "Can you tell me about your pricing?",
                "What features are included in the premium plan?",
                "Is there a free trial available?",
            ],
            EmailCategory.BILLING: [
                "I was charged twice for my subscription.",
                "Can I get an invoice for my purchase?",
                "How do I update my payment method?",
            ],
            EmailCategory.FEEDBACK: [
                "Your product is great, I love the new interface!",
                "I have some suggestions for improvement.",
                "The docs are really helpful, thanks!",
            ],
            EmailCategory.TECHNICAL_SUPPORT: [
                "I'm getting an error when trying to login.",
                "The app crashes when I try to export data.",
                "Performance has been slow recently.",
            ],
            EmailCategory.SPAM: [
                "YOU CAN WIN $1000000 TODAY!!!",
                "Click here for free money!!!",
                "UNCLAIMED INHERITANCE AWAITS YOU",
            ],
        }

        for i in range(count):
            # Randomly select category with spam less likely
            if random.random() < 0.9:
                category = random.choice(categories[:-1])  # Exclude spam
            else:
                category = EmailCategory.SPAM

            subject = email_templates[category][random.randint(0, len(email_templates[category]) - 1)]
            priority = EmailPriority.CRITICAL if category == EmailCategory.TECHNICAL_SUPPORT else random.choice(
                priorities
            )

            email = Email(
                id=f"email_{self._state.step}_{i}",
                sender=random.choice(senders),
                subject=subject[:50],
                body=subject + " This is a longer description of the email content.",
                priority=priority,
                ground_truth_category=category,
                category=None,
            )
            self._state.emails.append(email)

    def populate_with_tickets(self, count: int = 3) -> None:
        """
        Populate environment with random support tickets.
        
        Args:
            count: Number of tickets to generate
        """
        issues = [
            "Cannot login to account",
            "Billing discrepancy",
            "Feature request",
            "Performance issue",
            "Integration not working",
            "Data export failed",
            "Account locked",
        ]

        customers = ["Acme Corp", "TechStart", "Global Industries", "FastCorp", "CloudBase"]
        severities = list(TicketSeverity)

        for i in range(count):
            severity = random.choice(severities)
            ticket = SupportTicket(
                id=f"ticket_{self._state.step}_{i}",
                customer_name=random.choice(customers),
                issue=random.choice(issues),
                severity=severity,
                status=TicketStatus.OPEN,
            )
            self._state.tickets.append(ticket)

    def populate_with_meetings(self, count: int = 2) -> None:
        """
        Populate environment with random meeting requests.
        
        Args:
            count: Number of meetings to generate
        """
        purposes = [
            "Product demo",
            "Budget review",
            "Team sync",
            "Sales call",
            "Technical discussion",
            "Project planning",
        ]

        requesters = ["Alice Johnson", "Bob Smith", "Carol Williams", "David Brown", "Eve Davis"]
        urgencies = ["low", "medium", "high"]

        now = datetime.now()
        for i in range(count):
            # Schedule within next 7 days
            days_ahead = random.randint(0, 7)
            hours_ahead = random.randint(9, 17)
            requested_time = now + timedelta(days=days_ahead, hours=hours_ahead)

            meeting = MeetingRequest(
                id=f"meeting_{self._state.step}_{i}",
                requester=random.choice(requesters),
                participants=[random.choice(requesters), random.choice(requesters)],
                purpose=random.choice(purposes),
                requested_time=requested_time,
                urgency=random.choice(urgencies),
                status=MeetingStatus.REQUESTED,
            )
            self._state.meetings.append(meeting)

    # ========================================================================
    # Action Execution
    # ========================================================================

    def _execute_action(
        self,
        action: Action,
        email: Optional[Email] = None,
        ticket: Optional[SupportTicket] = None,
        meeting: Optional[MeetingRequest] = None,
    ) -> None:
        """Execute the action in the environment."""
        if isinstance(action, ClassifyEmailAction):
            if email:
                email.category = action.category
                email.handled = True

        elif isinstance(action, ReplyEmailAction):
            if email:
                email.replied = True
                email.handled = True

        elif isinstance(action, EscalateTicketAction):
            if ticket:
                ticket.status = TicketStatus.ESCALATED

        elif isinstance(action, CloseTicketAction):
            if ticket:
                ticket.status = TicketStatus.CLOSED
                ticket.resolved_at = datetime.now()
                ticket.resolution = action.resolution

        elif isinstance(action, ScheduleMeetingAction):
            if meeting:
                meeting.status = MeetingStatus.SCHEDULED
                meeting.scheduled_time = action.scheduled_time

        elif isinstance(action, DeleteSpamAction):
            if email:
                # Remove email from list (simulate deletion)
                self._state.emails = [e for e in self._state.emails if e.id != email.id]

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _get_action_target_id(self, action: Action) -> str:
        """Extract target ID from action."""
        if isinstance(action, ClassifyEmailAction):
            return action.email_id
        elif isinstance(action, ReplyEmailAction):
            return action.email_id
        elif isinstance(action, EscalateTicketAction):
            return action.ticket_id
        elif isinstance(action, CloseTicketAction):
            return action.ticket_id
        elif isinstance(action, ScheduleMeetingAction):
            return action.meeting_id
        elif isinstance(action, DeleteSpamAction):
            return action.email_id
        else:
            raise ValueError(f"Unknown action type: {type(action)}")

    def _get_action_domain(self, action: Action) -> str:
        """Get domain (emails, tickets, meetings) for action."""
        if isinstance(action, (ClassifyEmailAction, ReplyEmailAction, DeleteSpamAction)):
            return "emails"
        elif isinstance(action, (EscalateTicketAction, CloseTicketAction)):
            return "tickets"
        elif isinstance(action, ScheduleMeetingAction):
            return "meetings"
        else:
            raise ValueError(f"Unknown action type: {type(action)}")

    def _is_duplicate_action(self, action: Action, target_id: str) -> bool:
        """Check if action on this item has been taken before."""
        domain = self._get_action_domain(action)

        # Certain actions can be repeated
        if isinstance(action, ReplyEmailAction):
            return False
        if isinstance(action, CloseTicketAction):
            return False

        # Classify, escalate, schedule, delete should not be repeated
        return target_id in self.processed_items[domain]

    def _find_email(self, email_id: str) -> Optional[Email]:
        """Find email by ID."""
        for email in self._state.emails:
            if email.id == email_id:
                return email
        return None

    def _find_ticket(self, ticket_id: str) -> Optional[SupportTicket]:
        """Find ticket by ID."""
        for ticket in self._state.tickets:
            if ticket.id == ticket_id:
                return ticket
        return None

    def _find_meeting(self, meeting_id: str) -> Optional[MeetingRequest]:
        """Find meeting by ID."""
        for meeting in self._state.meetings:
            if meeting.id == meeting_id:
                return meeting
        return None

    def _check_natural_completion(self) -> bool:
        """Check if all items have been processed (natural episode end)."""
        if not (self._state.emails or self._state.tickets or self._state.meetings):
            return False

        emails_done = all(email.handled for email in self._state.emails)
        tickets_done = all(
            ticket.status in (TicketStatus.ESCALATED, TicketStatus.CLOSED)
            for ticket in self._state.tickets
        )
        meetings_done = all(
            meeting.status in (MeetingStatus.SCHEDULED, MeetingStatus.CANCELLED, MeetingStatus.COMPLETED)
            for meeting in self._state.meetings
        )

        return emails_done and tickets_done and meetings_done

    def get_summary(self) -> Dict[str, Any]:
        """Get episode summary."""
        action_counts = {}
        for action, _ in self.action_history:
            action_type = action.action_type
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        return {
            "total_reward": self._state.episode_reward,
            "steps": self._state.step,
            "action_counts": action_counts,
            "emails_handled": len([e for e in self._state.emails if e.handled]),
            "tickets_closed": len([t for t in self._state.tickets if t.status == TicketStatus.CLOSED]),
            "meetings_scheduled": len(
                [m for m in self._state.meetings if m.status == MeetingStatus.SCHEDULED]
            ),
            "natural_completion": self._check_natural_completion(),
        }
