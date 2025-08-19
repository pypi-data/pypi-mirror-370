"""Decision contracts and voting strategies."""

from typing import Literal
from pydantic import BaseModel, Field


class DecisionContract(BaseModel):
    """Contract defining voting requirements for a node."""
    required_approvers: list[str]
    strategy: Literal["unanimous", "majority", "weighted"] = "unanimous"
    timeout_seconds: int = 120
    weights: dict[str, float] = Field(default_factory=dict)
    
    def validate_strategy(self) -> None:
        """Validate contract configuration."""
        if self.strategy == "weighted" and not self.weights:
            raise ValueError("Weighted strategy requires weights to be specified")
        
        if self.strategy == "weighted":
            for approver in self.required_approvers:
                if approver not in self.weights:
                    raise ValueError(f"No weight specified for required approver: {approver}")


def decision_contract(
    required_approvers: list[str],
    strategy: Literal["unanimous", "majority", "weighted"] = "unanimous",
    timeout_seconds: int = 120,
    weights: dict[str, float] | None = None,
) -> DecisionContract:
    """Factory function to create a decision contract."""
    contract = DecisionContract(
        required_approvers=required_approvers,
        strategy=strategy,
        timeout_seconds=timeout_seconds,
        weights=weights or {},
    )
    contract.validate_strategy()
    return contract


class VotingStrategy:
    """Voting strategy implementations."""
    
    @staticmethod
    def evaluate_unanimous(
        votes: dict[str, "VoteDecision"],  # type: ignore
        required_approvers: list[str],
        weights: dict[str, float] | None = None,
    ) -> tuple[bool, str]:
        """Evaluate unanimous consensus."""
        from .events import VoteDecision
        
        # All required approvers must vote APPROVE
        for approver in required_approvers:
            if approver not in votes:
                return False, f"Missing vote from {approver}"
            if votes[approver] != VoteDecision.APPROVE:
                return False, f"Non-approval from {approver}: {votes[approver]}"
        
        return True, "Unanimous approval achieved"
    
    @staticmethod
    def evaluate_majority(
        votes: dict[str, "VoteDecision"],  # type: ignore
        required_approvers: list[str],
        weights: dict[str, float] | None = None,
    ) -> tuple[bool, str]:
        """Evaluate majority consensus."""
        from .events import VoteDecision
        
        total_approvers = len(required_approvers)
        approvals = sum(
            1 for approver in required_approvers
            if votes.get(approver) == VoteDecision.APPROVE
        )
        
        threshold = total_approvers / 2
        if approvals > threshold:
            return True, f"Majority approval: {approvals}/{total_approvers}"
        else:
            return False, f"Insufficient approvals: {approvals}/{total_approvers} (need >{threshold})"
    
    @staticmethod
    def evaluate_weighted(
        votes: dict[str, "VoteDecision"],  # type: ignore
        required_approvers: list[str],
        weights: dict[str, float] | None = None,
    ) -> tuple[bool, str]:
        """Evaluate weighted consensus."""
        from .events import VoteDecision
        
        if not weights:
            raise ValueError("Weights required for weighted strategy")
        
        total_weight = sum(weights.get(approver, 0.0) for approver in required_approvers)
        approval_weight = sum(
            weights.get(approver, 0.0)
            for approver in required_approvers
            if votes.get(approver) == VoteDecision.APPROVE
        )
        
        threshold = total_weight / 2
        if approval_weight > threshold:
            return True, f"Weighted approval: {approval_weight}/{total_weight}"
        else:
            return False, f"Insufficient weight: {approval_weight}/{total_weight} (need >{threshold})"


