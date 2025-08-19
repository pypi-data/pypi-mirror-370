"""Event models for OACP audit trail."""

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field, field_serializer
import ulid


class VoteDecision(str, Enum):
    """Vote decision enumeration."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


class EventBase(BaseModel):
    """Base class for all OACP events."""
    schema_version: Literal["1.0"] = "1.0"
    event_id: str = Field(default_factory=lambda: ulid.new().str)
    run_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    causality: list[str] = Field(default_factory=list)
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, timestamp: datetime) -> str:
        """Serialize datetime to ISO format."""
        return timestamp.isoformat()


class TaskStart(EventBase):
    """Event emitted when a task/run begins."""
    event_type: Literal["TaskStart"] = "TaskStart"
    graph_name: str | None = None
    initial_state: dict[str, Any] | None = None


class NodeStart(EventBase):
    """Event emitted when a node begins execution."""
    event_type: Literal["NodeStart"] = "NodeStart"
    node_id: str
    role: str | None = None
    inputs: dict[str, Any] | None = None
    idempotency_key: str | None = None


class NodeResult(EventBase):
    """Event emitted when a node completes execution."""
    event_type: Literal["NodeResult"] = "NodeResult"
    node_id: str
    role: str | None = None
    output: Any = None
    summary: str | None = None
    duration_ms: int | None = None
    success: bool = True
    error: str | None = None


class VoteCast(EventBase):
    """Event emitted when a vote is cast."""
    event_type: Literal["VoteCast"] = "VoteCast"
    voter_id: str
    decision: VoteDecision
    reason: str | None = None
    target_ref: str | None = None
    fix_suggestions: list[str] = Field(default_factory=list)


class ConflictRaised(EventBase):
    """Event emitted when consensus fails."""
    event_type: Literal["ConflictRaised"] = "ConflictRaised"
    node_id: str
    reason_summary: str
    votes_cast: int
    approvals: int
    rejections: int
    abstentions: int
    missing_voters: list[str] = Field(default_factory=list)


class DecisionFinalized(EventBase):
    """Event emitted when consensus is reached."""
    event_type: Literal["DecisionFinalized"] = "DecisionFinalized"
    node_id: str
    approved: bool
    votes_cast: int
    consensus_strategy: str
    duration_ms: int | None = None


class RetryScheduled(EventBase):
    """Event emitted when a retry is scheduled."""
    event_type: Literal["RetryScheduled"] = "RetryScheduled"
    node_id: str
    attempt_number: int
    next_attempt_at: datetime
    reason: str
    backoff_ms: int


class RunSummary(EventBase):
    """Event emitted at the end of a run."""
    event_type: Literal["RunSummary"] = "RunSummary"
    status: Literal["completed", "failed", "cancelled"]
    total_events: int
    total_nodes: int
    total_votes: int
    consensus_reached: int
    conflicts_raised: int
    retries_executed: int
    duration_ms: int

