"""
Adaptive prompting system for OACP.

This module provides intelligent prompt adaptation based on rejection feedback,
allowing agents to learn from failed consensus attempts and improve their outputs.
"""

import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
from oacp.events import VoteCast, VoteDecision
from oacp.storage.base import IStorage


@dataclass
class RejectionFeedback:
    """Represents feedback from a rejection vote."""
    voter_id: str
    reason: str
    timestamp: float
    run_id: str
    node_id: str
    agent_role: str


@dataclass
class PromptAdaptation:
    """Represents an adaptation to a prompt based on feedback."""
    original_prompt: str
    adapted_prompt: str
    adaptation_reason: str
    feedback_patterns: List[str]
    timestamp: float
    success_rate: float = 0.0


class AdaptivePromptEngine:
    """
    Engine that learns from rejection feedback and adapts prompts to improve consensus.
    
    Features:
    - Collects rejection reasons from failed consensus attempts
    - Identifies common patterns in rejections
    - Generates prompt improvements based on feedback
    - Tracks success rates of adaptations
    - Provides prompt suggestions for retry attempts
    """
    
    def __init__(self, storage: Optional[IStorage] = None):
        self.storage = storage
        self.rejection_history: Dict[str, List[RejectionFeedback]] = defaultdict(list)
        self.prompt_adaptations: Dict[str, List[PromptAdaptation]] = defaultdict(list)
        self.adaptation_patterns: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.Lock()
        
        # Common rejection patterns and their prompt fixes
        self.pattern_fixes = {
            "lacks detail": "Please provide more detailed and comprehensive information",
            "insufficient evidence": "Include specific examples, data points, and evidence to support your points",
            "missing analysis": "Provide deeper analysis and insights beyond just stating facts",
            "no recommendations": "Include specific, actionable recommendations based on your analysis",
            "too generic": "Be more specific and concrete in your response, avoid generic statements",
            "lacks structure": "Organize your response with clear sections and logical flow",
            "missing context": "Provide relevant context and background information",
            "incomplete coverage": "Ensure you address all aspects mentioned in the requirements",
            "weak conclusions": "Draw stronger, more definitive conclusions based on the evidence",
            "lacks critical thinking": "Include critical evaluation and consideration of alternative perspectives"
        }
    
    def record_rejection(self, rejection_feedback: RejectionFeedback) -> None:
        """Record rejection feedback for learning."""
        with self._lock:
            key = f"{rejection_feedback.agent_role}:{rejection_feedback.node_id}"
            self.rejection_history[key].append(rejection_feedback)
            
            # Store in persistent storage if available
            if self.storage:
                try:
                    # Create a custom event for rejection feedback
                    feedback_event = {
                        "event_type": "RejectionFeedback",
                        "timestamp": time.time(),
                        "run_id": rejection_feedback.run_id,
                        "voter_id": rejection_feedback.voter_id,
                        "reason": rejection_feedback.reason,
                        "node_id": rejection_feedback.node_id,
                        "agent_role": rejection_feedback.agent_role
                    }
                    # Note: This would need to be adapted based on storage interface
                    # self.storage.write_event(feedback_event)
                except Exception as e:
                    print(f"⚠️  Failed to store rejection feedback: {e}")
    
    def analyze_rejection_patterns(self, agent_role: str, node_id: str) -> List[str]:
        """Analyze rejection patterns for a specific agent/node."""
        key = f"{agent_role}:{node_id}"
        rejections = self.rejection_history.get(key, [])
        
        if not rejections:
            return []
        
        # Extract common themes from rejection reasons
        patterns = []
        reason_text = " ".join([r.reason.lower() for r in rejections[-5:]])  # Last 5 rejections
        
        for pattern, _ in self.pattern_fixes.items():
            if pattern in reason_text:
                patterns.append(pattern)
        
        return patterns
    
    def generate_prompt_adaptation(
        self, 
        original_prompt: str, 
        agent_role: str, 
        node_id: str,
        rejection_reasons: List[str] = None
    ) -> Optional[str]:
        """
        Generate an adapted prompt based on rejection feedback.
        
        Args:
            original_prompt: The original prompt that led to rejections
            agent_role: Role of the agent
            node_id: Node identifier
            rejection_reasons: Specific rejection reasons to address
            
        Returns:
            Adapted prompt or None if no adaptation needed
        """
        patterns = self.analyze_rejection_patterns(agent_role, node_id)
        
        # Add any specific rejection reasons provided
        if rejection_reasons:
            for reason in rejection_reasons:
                reason_lower = reason.lower()
                for pattern in self.pattern_fixes.keys():
                    if pattern in reason_lower and pattern not in patterns:
                        patterns.append(pattern)
        
        if not patterns:
            return None
        
        # Build adaptation instructions
        adaptations = []
        for pattern in patterns:
            if pattern in self.pattern_fixes:
                adaptations.append(self.pattern_fixes[pattern])
        
        if not adaptations:
            return None
        
        # Create adapted prompt
        adaptation_instructions = "\n".join([f"• {fix}" for fix in adaptations])
        
        adapted_prompt = f"""{original_prompt}

IMPORTANT - Based on previous feedback, please ensure your response addresses these specific concerns:
{adaptation_instructions}

Focus on providing a response that directly addresses the feedback above while maintaining quality and accuracy."""
        
        # Record this adaptation
        adaptation = PromptAdaptation(
            original_prompt=original_prompt,
            adapted_prompt=adapted_prompt,
            adaptation_reason=f"Addressing patterns: {', '.join(patterns)}",
            feedback_patterns=patterns,
            timestamp=time.time()
        )
        
        with self._lock:
            key = f"{agent_role}:{node_id}"
            self.prompt_adaptations[key].append(adaptation)
        
        return adapted_prompt
    
    def get_adaptation_stats(self, agent_role: str, node_id: str) -> Dict[str, Any]:
        """Get statistics about adaptations for an agent/node."""
        key = f"{agent_role}:{node_id}"
        
        rejections = self.rejection_history.get(key, [])
        adaptations = self.prompt_adaptations.get(key, [])
        
        return {
            "total_rejections": len(rejections),
            "total_adaptations": len(adaptations),
            "common_patterns": self.analyze_rejection_patterns(agent_role, node_id),
            "recent_rejections": [
                {"voter": r.voter_id, "reason": r.reason, "timestamp": r.timestamp}
                for r in rejections[-3:]  # Last 3 rejections
            ],
            "adaptation_history": [
                {
                    "patterns": a.feedback_patterns,
                    "reason": a.adaptation_reason,
                    "timestamp": a.timestamp
                }
                for a in adaptations[-3:]  # Last 3 adaptations
            ]
        }
    
    def should_adapt_prompt(self, agent_role: str, node_id: str, attempt: int) -> bool:
        """Determine if prompt adaptation should be used for a retry attempt."""
        # Start adapting from attempt 2 onwards
        if attempt < 2:
            return False
        
        key = f"{agent_role}:{node_id}"
        rejections = self.rejection_history.get(key, [])
        
        # Only adapt if we have recent rejections
        return len(rejections) > 0
    
    def clear_history(self, agent_role: str = None, node_id: str = None) -> None:
        """Clear adaptation history (useful for testing or reset)."""
        with self._lock:
            if agent_role and node_id:
                key = f"{agent_role}:{node_id}"
                self.rejection_history.pop(key, None)
                self.prompt_adaptations.pop(key, None)
            else:
                self.rejection_history.clear()
                self.prompt_adaptations.clear()


# Global adaptive prompt engine instance
_adaptive_engine: Optional[AdaptivePromptEngine] = None
_engine_lock = threading.Lock()


def get_adaptive_engine(storage: Optional[IStorage] = None) -> AdaptivePromptEngine:
    """Get or create the global adaptive prompt engine."""
    global _adaptive_engine
    with _engine_lock:
        if _adaptive_engine is None:
            _adaptive_engine = AdaptivePromptEngine(storage)
        return _adaptive_engine


def record_rejection_feedback(
    voter_id: str,
    reason: str,
    run_id: str,
    node_id: str,
    agent_role: str
) -> None:
    """
    Record rejection feedback for adaptive learning.
    
    This should be called when a vote with REJECT decision is cast.
    """
    engine = get_adaptive_engine()
    feedback = RejectionFeedback(
        voter_id=voter_id,
        reason=reason,
        timestamp=time.time(),
        run_id=run_id,
        node_id=node_id,
        agent_role=agent_role
    )
    engine.record_rejection(feedback)


def adapt_prompt_for_retry(
    original_prompt: str,
    agent_role: str,
    node_id: str,
    attempt: int,
    rejection_reasons: List[str] = None
) -> str:
    """
    Adapt a prompt for retry based on rejection feedback.
    
    Args:
        original_prompt: The original prompt
        agent_role: Role of the agent
        node_id: Node identifier  
        attempt: Current attempt number
        rejection_reasons: Specific rejection reasons to address
        
    Returns:
        Adapted prompt or original prompt if no adaptation needed
    """
    engine = get_adaptive_engine()
    
    if not engine.should_adapt_prompt(agent_role, node_id, attempt):
        return original_prompt
    
    adapted = engine.generate_prompt_adaptation(
        original_prompt, agent_role, node_id, rejection_reasons
    )
    
    return adapted if adapted else original_prompt


def get_adaptation_statistics(agent_role: str, node_id: str) -> Dict[str, Any]:
    """Get adaptation statistics for an agent/node."""
    engine = get_adaptive_engine()
    return engine.get_adaptation_stats(agent_role, node_id)
