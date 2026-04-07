"""
Pydantic models for the AI Operations Assistant Environment.
Defines all data structures with full type safety and validation.
"""

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class EmailPriority(str, Enum):
    """Email priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EmailCategory(str, Enum):
    """Email categories for classification."""
    PRODUCT_INQUIRY = "product_inquiry"
    BILLING = "billing"
    FEEDBACK = "feedback"
    TECHNICAL_SUPPORT = "technical_support"
    SPAM = "spam"
    UNKNOWN = "unknown"


class TicketSeverity(str, Enum):
    """Support ticket severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    """Support ticket status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MeetingStatus(str, Enum):
    """Meeting request status."""
    REQUESTED = "requested"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


# ============================================================================
# ENTITIES
# ============================================================================

class Email(BaseModel):
    """Represents an email message."""
    id: str = Field(..., description="Unique email identifier")
    sender: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    priority: EmailPriority = Field(default=EmailPriority.MEDIUM)
    ground_truth_category: Optional[EmailCategory] = Field(
        default=None, description="Original category label used for evaluation"
    )
    category: Optional[EmailCategory] = Field(
        default=None, description="Agent-assigned category"
    )
    handled: bool = Field(default=False, description="Whether email has been handled")
    replied: bool = Field(default=False, description="Whether email has been replied to")
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SupportTicket(BaseModel):
    """Represents a customer support ticket."""
    id: str = Field(..., description="Unique ticket identifier")
    customer_name: str = Field(..., description="Customer name")
    issue: str = Field(..., description="Issue description")
    severity: TicketSeverity = Field(default=TicketSeverity.MEDIUM)
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = Field(default=None)
    resolution: Optional[str] = Field(default=None, description="How the ticket was resolved")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class MeetingRequest(BaseModel):
    """Represents a meeting request."""
    id: str = Field(..., description="Unique meeting identifier")
    requester: str = Field(..., description="Person requesting the meeting")
    participants: List[str] = Field(default_factory=list, description="Participants list")
    purpose: str = Field(..., description="Meeting purpose")
    requested_time: datetime = Field(..., description="Requested meeting time")
    urgency: Literal["low", "medium", "high"] = Field(default="medium")
    status: MeetingStatus = Field(default=MeetingStatus.REQUESTED)
    scheduled_time: Optional[datetime] = Field(default=None)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================================================
# ACTIONS
# ============================================================================

class Action(BaseModel):
    """Base action model."""
    action_type: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ClassifyEmailAction(Action):
    """Action to classify an email."""
    action_type: Literal["classify_email"] = "classify_email"
    email_id: str = Field(..., description="ID of email to classify")
    category: EmailCategory = Field(..., description="Predicted category")


class ReplyEmailAction(Action):
    """Action to reply to an email."""
    action_type: Literal["reply_email"] = "reply_email"
    email_id: str = Field(..., description="ID of email to reply to")
    reply_content: str = Field(..., description="Reply message content")


class EscalateTicketAction(Action):
    """Action to escalate a support ticket."""
    action_type: Literal["escalate_ticket"] = "escalate_ticket"
    ticket_id: str = Field(..., description="ID of ticket to escalate")
    escalation_reason: str = Field(..., description="Reason for escalation")


class CloseTicketAction(Action):
    """Action to close/resolve a support ticket."""
    action_type: Literal["close_ticket"] = "close_ticket"
    ticket_id: str = Field(..., description="ID of ticket to close")
    resolution: str = Field(..., description="How the issue was resolved")


class ScheduleMeetingAction(Action):
    """Action to schedule a meeting."""
    action_type: Literal["schedule_meeting"] = "schedule_meeting"
    meeting_id: str = Field(..., description="ID of meeting request")
    scheduled_time: datetime = Field(..., description="Time to schedule meeting")


class DeleteSpamAction(Action):
    """Action to delete/ignore spam."""
    action_type: Literal["delete_spam"] = "delete_spam"
    email_id: str = Field(..., description="ID of email to delete")


# Union of all possible actions
ActionUnion = (
    ClassifyEmailAction
    | ReplyEmailAction
    | EscalateTicketAction
    | CloseTicketAction
    | ScheduleMeetingAction
    | DeleteSpamAction
)


# ============================================================================
# OBSERVATIONS
# ============================================================================

class Observation(BaseModel):
    """Current environment state observation."""
    step: int = Field(..., description="Current step number")
    emails: List[Email] = Field(default_factory=list, description="List of emails")
    tickets: List[SupportTicket] = Field(default_factory=list, description="List of support tickets")
    meetings: List[MeetingRequest] = Field(default_factory=list, description="List of meetings")
    done: bool = Field(default=False, description="Whether episode is done")
    info: Dict = Field(default_factory=dict, description="Additional info")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================================================
# REWARD
# ============================================================================

class Reward(BaseModel):
    """Structured reward signal."""
    total: float = Field(..., description="Total reward for this step")
    components: Dict[str, float] = Field(
        default_factory=dict,
        description="Breakdown of reward components"
    )
    explanation: str = Field(default="", description="Human-readable explanation")

    def __float__(self) -> float:
        """Allow using Reward as a float."""
        return self.total


# ============================================================================
# ENVIRONMENT STATE
# ============================================================================

class EnvironmentState(BaseModel):
    """Complete internal environment state."""
    step: int = Field(default=0)
    episode_reward: float = Field(default=0.0)
    emails: List[Email] = Field(default_factory=list)
    tickets: List[SupportTicket] = Field(default_factory=list)
    meetings: List[MeetingRequest] = Field(default_factory=list)
    action_history: List[Dict] = Field(default_factory=list)
    reward_history: List[float] = Field(default_factory=list)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================================================
# TASK DEFINITIONS
# ============================================================================

class TaskDefinition(BaseModel):
    """Definition of a task."""
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    difficulty: Literal["easy", "medium", "hard"] = Field(...)
    max_steps: int = Field(default=100, description="Max steps per episode")
    initial_emails: int = Field(default=5)
    initial_tickets: int = Field(default=0)
    initial_meetings: int = Field(default=0)


class TaskResult(BaseModel):
    """Result of running a task."""
    task_name: str = Field(...)
    total_reward: float = Field(...)
    final_score: float = Field(..., description="Score from 0.0 to 1.0")
    steps_taken: int = Field(...)
    action_counts: Dict[str, int] = Field(default_factory=dict)
    success: bool = Field(...)
    details: Dict = Field(default_factory=dict)
