"""
OACP (Open Agent Compliance Protocol)

A governance layer for LangGraph that adds voting, consensus, and audit trails
to multi-agent workflows.
"""

from .decorators import with_oacp, wrap_node
from .contracts import decision_contract, DecisionContract
from .votes import vote, VoteDecision
from .context import current_context
from .errors import (
    OacpError,
    OacpConsensusError,
    OacpTimeout,
    OacpStorageError,
    OacpRetryExhausted,
    OacpInvalidVote,
)
from .events import EventBase, VoteCast, NodeResult, DecisionFinalized
from .llm_integration import (
    OacpLLMAdapter, create_adaptive_llm_function, 
    get_adapted_prompt, log_adaptation_insights
)
from .adaptive_prompting import (
    get_adaptation_statistics, record_rejection_feedback
)

__version__ = "0.1.0"
__all__ = [
    "with_oacp",
    "wrap_node",
    "decision_contract",
    "DecisionContract",
    "vote",
    "VoteDecision",
    "current_context",
    "OacpError",
    "OacpConsensusError", 
    "OacpTimeout",
    "OacpStorageError",
    "OacpRetryExhausted",
    "OacpInvalidVote",
    "EventBase",
    "VoteCast",
    "NodeResult",
    "DecisionFinalized",
    # Adaptive prompting
    "OacpLLMAdapter",
    "create_adaptive_llm_function",
    "get_adapted_prompt",
    "log_adaptation_insights",
    "get_adaptation_statistics",
    "record_rejection_feedback",
]

