"""Tests for OACP decorators."""

import pytest

from oacp.decorators import with_oacp
from oacp.contracts import decision_contract
from oacp.votes import vote, VoteDecision
from oacp.context import current_context
from oacp.errors import OacpConsensusError, OacpRetryExhausted


def test_simple_decorator():
    """Test basic decorator functionality."""
    @with_oacp(role="test-node")
    def simple_function(x: int) -> int:
        return x * 2
    
    result = simple_function(5)
    assert result == 10


def test_decorator_with_context():
    """Test decorator provides context."""
    @with_oacp(role="context-test")
    def context_function() -> str:
        ctx = current_context()
        return ctx.role
    
    result = context_function()
    assert result == "context-test"


def test_decorator_with_contract(file_storage):
    """Test decorator with voting contract."""
    contract = decision_contract(
        required_approvers=["approver1"],
        strategy="unanimous",
        timeout_seconds=1  # Short timeout for test
    )
    
    @with_oacp(role="voting-node", contract=contract)
    def voting_function() -> str:
        ctx = current_context()
        
        # Cast approval vote
        vote(
            run_id=ctx.run_id,
            voter_id="approver1",
            decision=VoteDecision.APPROVE,
            reason="Looks good"
        )
        
        return "success"
    
    # This should work with approval
    result = voting_function()
    assert result == "success"


def test_decorator_consensus_failure(file_storage):
    """Test decorator behavior on consensus failure."""
    contract = decision_contract(
        required_approvers=["approver1"],
        strategy="unanimous",
        timeout_seconds=1
    )
    
    @with_oacp(role="failing-node", contract=contract)
    def failing_function() -> str:
        ctx = current_context()
        
        # Cast rejection vote
        vote(
            run_id=ctx.run_id,
            voter_id="approver1",
            decision=VoteDecision.REJECT,
            reason="Not good enough"
        )
        
        return "success"
    
    # This should fail due to rejection after retries
    with pytest.raises(OacpRetryExhausted):
        failing_function()