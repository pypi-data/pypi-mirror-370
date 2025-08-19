"""Tests for OACP event models."""

import pytest
from datetime import datetime

from oacp.events import (
    EventBase, NodeStart, NodeResult, VoteCast, VoteDecision,
    ConflictRaised, DecisionFinalized
)


def test_event_base_creation():
    """Test creating base event."""
    event = EventBase(
        run_id="test-run",
        event_type="TestEvent"
    )
    
    assert event.run_id == "test-run"
    assert event.event_type == "TestEvent"
    assert event.schema_version == "1.0"
    assert isinstance(event.timestamp, datetime)
    assert len(event.event_id) > 0


def test_node_start_event():
    """Test NodeStart event creation."""
    event = NodeStart(
        run_id="test-run",
        node_id="test-node",
        role="test-role",
        inputs={"key": "value"}
    )
    
    assert event.event_type == "NodeStart"
    assert event.node_id == "test-node"
    assert event.role == "test-role"
    assert event.inputs == {"key": "value"}


def test_vote_cast_event():
    """Test VoteCast event creation."""
    event = VoteCast(
        run_id="test-run",
        voter_id="test-voter",
        decision=VoteDecision.APPROVE,
        reason="Looks good",
        fix_suggestions=["suggestion1", "suggestion2"]
    )
    
    assert event.event_type == "VoteCast"
    assert event.voter_id == "test-voter"
    assert event.decision == VoteDecision.APPROVE
    assert event.reason == "Looks good"
    assert len(event.fix_suggestions) == 2


def test_event_serialization():
    """Test event JSON serialization."""
    event = NodeResult(
        run_id="test-run",
        node_id="test-node",
        output={"result": "success"},
        success=True
    )
    
    # Test dict conversion
    event_dict = event.model_dump()
    assert event_dict["run_id"] == "test-run"
    assert event_dict["event_type"] == "NodeResult"
    assert event_dict["success"] is True

