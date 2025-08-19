"""Voting API for OACP."""

import logging
from datetime import datetime

from .events import VoteCast, VoteDecision
from .context import current_context
from .trace import TraceWriter
from .errors import OacpInvalidVote
from .adaptive_prompting import record_rejection_feedback

logger = logging.getLogger(__name__)


def vote(
    run_id: str,
    voter_id: str,
    decision: VoteDecision,
    reason: str | None = None,
    fix_suggestions: list[str] | None = None,
    target_ref: str | None = None,
) -> None:
    """Cast a vote for a decision.
    
    Args:
        run_id: The run ID to vote on
        voter_id: ID of the voting agent
        decision: Vote decision (APPROVE, REJECT, ABSTAIN)
        reason: Optional reason for the vote
        fix_suggestions: Optional list of suggested fixes
        target_ref: Optional reference to what is being voted on
    """
    try:
        # Try to get current context for trace writer
        ctx = current_context()
        trace_writer = ctx.trace_writer
    except RuntimeError:
        # No context available, create new trace writer
        trace_writer = TraceWriter()
    
    if not trace_writer:
        trace_writer = TraceWriter()
    
    # Create vote event
    vote_event = VoteCast(
        run_id=run_id,
        voter_id=voter_id,
        decision=decision,
        reason=reason,
        fix_suggestions=fix_suggestions or [],
        target_ref=target_ref,
    )
    
    try:
        trace_writer.write(vote_event)
        logger.info(f"Vote cast by {voter_id} for run {run_id}: {decision}")
        
        # Record rejection feedback for adaptive learning
        if decision == VoteDecision.REJECT and reason:
            try:
                ctx = current_context()
                if ctx and ctx.node_id and ctx.role:
                    record_rejection_feedback(
                        voter_id=voter_id,
                        reason=reason,
                        run_id=run_id,
                        node_id=ctx.node_id,
                        agent_role=ctx.role
                    )
            except Exception as feedback_error:
                # Don't fail the vote if feedback recording fails
                logger.warning(f"Failed to record rejection feedback: {feedback_error}")
        
    except Exception as e:
        raise OacpInvalidVote(
            f"Failed to cast vote: {e}",
            voter_id=voter_id,
            run_id=run_id
        )

