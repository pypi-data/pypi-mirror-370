"""Tests for OACP decision contracts and voting strategies."""

import pytest

from oacp.contracts import DecisionContract, VotingStrategy, decision_contract
from oacp.events import VoteDecision


def test_decision_contract_creation():
    """Test creating decision contracts."""
    contract = decision_contract(
        required_approvers=["agent1", "agent2"],
        strategy="unanimous",
        timeout_seconds=60
    )
    
    assert contract.required_approvers == ["agent1", "agent2"]
    assert contract.strategy == "unanimous"
    assert contract.timeout_seconds == 60


def test_weighted_contract_validation():
    """Test weighted contract requires weights."""
    with pytest.raises(ValueError, match="weights to be specified"):
        decision_contract(
            required_approvers=["agent1", "agent2"],
            strategy="weighted"
        )
    
    # Should work with weights
    contract = decision_contract(
        required_approvers=["agent1", "agent2"],
        strategy="weighted",
        weights={"agent1": 2.0, "agent2": 1.0}
    )
    assert contract.weights["agent1"] == 2.0


def test_unanimous_voting_strategy():
    """Test unanimous voting strategy."""
    # All approve - should pass
    votes = {
        "agent1": VoteDecision.APPROVE,
        "agent2": VoteDecision.APPROVE
    }
    result, reason = VotingStrategy.evaluate_unanimous(
        votes, ["agent1", "agent2"]
    )
    assert result is True
    assert "unanimous approval" in reason.lower()
    
    # One reject - should fail
    votes = {
        "agent1": VoteDecision.APPROVE,
        "agent2": VoteDecision.REJECT
    }
    result, reason = VotingStrategy.evaluate_unanimous(
        votes, ["agent1", "agent2"]
    )
    assert result is False
    assert "agent2" in reason


def test_majority_voting_strategy():
    """Test majority voting strategy."""
    # 2/3 approve - should pass
    votes = {
        "agent1": VoteDecision.APPROVE,
        "agent2": VoteDecision.APPROVE,
        "agent3": VoteDecision.REJECT
    }
    result, reason = VotingStrategy.evaluate_majority(
        votes, ["agent1", "agent2", "agent3"]
    )
    assert result is True
    assert "2/3" in reason
    
    # 1/3 approve - should fail
    votes = {
        "agent1": VoteDecision.APPROVE,
        "agent2": VoteDecision.REJECT,
        "agent3": VoteDecision.REJECT
    }
    result, reason = VotingStrategy.evaluate_majority(
        votes, ["agent1", "agent2", "agent3"]
    )
    assert result is False


def test_weighted_voting_strategy():
    """Test weighted voting strategy."""
    weights = {"agent1": 3.0, "agent2": 1.0}
    
    # Agent1 approves (3.0 weight) - should pass
    votes = {
        "agent1": VoteDecision.APPROVE,
        "agent2": VoteDecision.REJECT
    }
    result, reason = VotingStrategy.evaluate_weighted(
        votes, ["agent1", "agent2"], weights
    )
    assert result is True
    assert "3.0/4.0" in reason
    
    # Agent2 approves (1.0 weight) - should fail
    votes = {
        "agent1": VoteDecision.REJECT,
        "agent2": VoteDecision.APPROVE
    }
    result, reason = VotingStrategy.evaluate_weighted(
        votes, ["agent1", "agent2"], weights
    )
    assert result is False

