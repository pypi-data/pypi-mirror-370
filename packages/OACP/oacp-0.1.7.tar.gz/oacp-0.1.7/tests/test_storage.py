"""Tests for OACP storage backends."""

import pytest
from datetime import datetime

from oacp.events import NodeStart, VoteCast, VoteDecision
from oacp.contracts import DecisionContract


def test_file_storage_append_and_iterate(file_storage):
    """Test file storage append and iterate operations."""
    run_id = "test-run-123"
    
    # Create test events
    event1 = NodeStart(
        run_id=run_id,
        node_id="node1",
        role="test-role"
    )
    
    event2 = VoteCast(
        run_id=run_id,
        voter_id="voter1",
        decision=VoteDecision.APPROVE
    )
    
    # Append events
    file_storage.append(event1)
    file_storage.append(event2)
    
    # Read events back
    events = list(file_storage.iterate(run_id))
    
    assert len(events) == 2
    assert events[0].event_type == "NodeStart"
    assert events[1].event_type == "VoteCast"
    assert events[0].run_id == run_id
    assert events[1].run_id == run_id


def test_sqlite_storage_append_and_iterate(sqlite_storage):
    """Test SQLite storage append and iterate operations."""
    run_id = "test-run-456"
    
    # Create test events
    event1 = NodeStart(
        run_id=run_id,
        node_id="node1",
        role="test-role"
    )
    
    event2 = VoteCast(
        run_id=run_id,
        voter_id="voter1",
        decision=VoteDecision.REJECT,
        reason="Needs improvement"
    )
    
    # Append events
    sqlite_storage.append(event1)
    sqlite_storage.append(event2)
    
    # Read events back
    events = list(sqlite_storage.iterate(run_id))
    
    assert len(events) == 2
    assert events[0].event_type == "NodeStart"
    assert events[1].event_type == "VoteCast"
    assert events[1].reason == "Needs improvement"


def test_storage_await_votes(file_storage):
    """Test waiting for votes functionality."""
    run_id = "test-run-votes"
    
    # Create contract
    contract = DecisionContract(
        required_approvers=["voter1", "voter2"],
        strategy="unanimous"
    )
    
    # Add some votes
    vote1 = VoteCast(
        run_id=run_id,
        voter_id="voter1",
        decision=VoteDecision.APPROVE
    )
    vote2 = VoteCast(
        run_id=run_id,
        voter_id="voter2", 
        decision=VoteDecision.APPROVE
    )
    
    file_storage.append(vote1)
    file_storage.append(vote2)
    
    # Wait for votes with short timeout
    result = file_storage.await_votes(run_id, contract, window_seconds=1)
    
    assert not result["timeout"]
    assert len(result["votes"]) == 2
    assert len(result["missing_voters"]) == 0


