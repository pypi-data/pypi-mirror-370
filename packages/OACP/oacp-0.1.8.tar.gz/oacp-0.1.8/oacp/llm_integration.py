"""
LLM integration helpers for OACP with adaptive prompting.

This module provides utilities to integrate OACP with LLM-based agents,
including automatic prompt adaptation based on rejection feedback.
"""

import logging
from typing import Any, Callable, Optional, List, Dict
from .context import current_context
from .adaptive_prompting import adapt_prompt_for_retry, get_adaptation_statistics

logger = logging.getLogger(__name__)


class OacpLLMAdapter:
    """
    Adapter for integrating OACP with LLM-based agents.
    
    Provides automatic prompt adaptation based on rejection feedback
    and context-aware prompt management.
    """
    
    def __init__(self, llm_client: Any = None):
        """
        Initialize the adapter.
        
        Args:
            llm_client: Optional LLM client (e.g., OpenAI, Anthropic, Gemini client)
        """
        self.llm_client = llm_client
        self._attempt_count = 0
    
    def generate_with_adaptation(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        llm_generate_func: Optional[Callable] = None,
        **kwargs
    ) -> str:
        """
        Generate LLM response with automatic prompt adaptation.
        
        Args:
            prompt: The base prompt
            system_instruction: Optional system instruction
            llm_generate_func: Function to call for LLM generation
            **kwargs: Additional arguments for the LLM function
            
        Returns:
            Generated response from LLM
            
        Example:
            adapter = OacpLLMAdapter()
            response = adapter.generate_with_adaptation(
                prompt="Analyze this data...",
                llm_generate_func=gemini_client.generate
            )
        """
        try:
            # Get current OACP context
            ctx = current_context()
            if not ctx:
                logger.warning("No OACP context available, using original prompt")
                adapted_prompt = prompt
            else:
                # Get current attempt from context metadata or track internally
                attempt = self._get_current_attempt(ctx)
                
                # Adapt prompt based on rejection feedback
                adapted_prompt = adapt_prompt_for_retry(
                    original_prompt=prompt,
                    agent_role=ctx.role or "unknown",
                    node_id=ctx.node_id or "unknown",
                    attempt=attempt
                )
                
                if adapted_prompt != prompt:
                    logger.info(f"🔄 Prompt adapted for attempt {attempt} based on rejection feedback")
                    logger.debug(f"Original prompt length: {len(prompt)} chars")
                    logger.debug(f"Adapted prompt length: {len(adapted_prompt)} chars")
        
        except Exception as e:
            logger.warning(f"Failed to adapt prompt: {e}, using original")
            adapted_prompt = prompt
        
        # Generate response using provided function or client
        if llm_generate_func:
            return llm_generate_func(adapted_prompt, system_instruction, **kwargs)
        elif self.llm_client and hasattr(self.llm_client, 'generate'):
            return self.llm_client.generate(adapted_prompt, system_instruction, **kwargs)
        else:
            raise ValueError("No LLM generation function or client provided")
    
    def _get_current_attempt(self, ctx) -> int:
        """Get current attempt number from context or internal tracking."""
        # Try to get from context metadata
        if ctx.metadata and 'attempt' in ctx.metadata:
            return ctx.metadata['attempt']
        
        # Fall back to internal tracking (not ideal but works)
        self._attempt_count += 1
        return self._attempt_count
    
    def get_adaptation_insights(self) -> Dict[str, Any]:
        """
        Get insights about prompt adaptations for the current agent.
        
        Returns:
            Dictionary with adaptation statistics and insights
        """
        try:
            ctx = current_context()
            if not ctx:
                return {"error": "No OACP context available"}
            
            stats = get_adaptation_statistics(
                agent_role=ctx.role or "unknown",
                node_id=ctx.node_id or "unknown"
            )
            
            return {
                "agent_role": ctx.role,
                "node_id": ctx.node_id,
                "adaptation_stats": stats,
                "recommendations": self._generate_recommendations(stats)
            }
            
        except Exception as e:
            return {"error": f"Failed to get adaptation insights: {e}"}
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on adaptation statistics."""
        recommendations = []
        
        total_rejections = stats.get('total_rejections', 0)
        common_patterns = stats.get('common_patterns', [])
        
        if total_rejections > 3:
            recommendations.append(
                "Consider reviewing your base prompt - high rejection rate detected"
            )
        
        if 'lacks detail' in common_patterns:
            recommendations.append(
                "Add more specific examples and detailed explanations to your prompts"
            )
        
        if 'insufficient evidence' in common_patterns:
            recommendations.append(
                "Include more data points, sources, and evidence in your responses"
            )
        
        if 'no recommendations' in common_patterns:
            recommendations.append(
                "Ensure your responses include actionable recommendations"
            )
        
        if not recommendations:
            recommendations.append("Your prompts are performing well!")
        
        return recommendations


def create_adaptive_llm_function(
    base_prompt_template: str,
    llm_generate_func: Callable,
    system_instruction: Optional[str] = None
) -> Callable:
    """
    Create a function that automatically adapts prompts based on OACP feedback.
    
    Args:
        base_prompt_template: Template for the base prompt (use {input} for dynamic content)
        llm_generate_func: Function to call for LLM generation
        system_instruction: Optional system instruction
        
    Returns:
        Function that can be used with @with_oacp decorator
        
    Example:
        @with_oacp(role="analyzer", adaptive_prompting=True)
        def analyze_data(data: dict) -> dict:
            llm_func = create_adaptive_llm_function(
                base_prompt_template="Analyze this data: {input}",
                llm_generate_func=gemini_client.generate
            )
            return llm_func(data)
    """
    adapter = OacpLLMAdapter()
    
    def adaptive_function(input_data: Any, **kwargs) -> str:
        # Format prompt with input data
        if isinstance(input_data, dict):
            formatted_prompt = base_prompt_template.format(**input_data)
        else:
            formatted_prompt = base_prompt_template.format(input=input_data)
        
        # Generate with adaptation
        return adapter.generate_with_adaptation(
            prompt=formatted_prompt,
            system_instruction=system_instruction,
            llm_generate_func=llm_generate_func,
            **kwargs
        )
    
    return adaptive_function


def log_adaptation_insights(agent_role: str = None) -> None:
    """
    Log adaptation insights for debugging and monitoring.
    
    Args:
        agent_role: Optional specific agent role to log insights for
    """
    adapter = OacpLLMAdapter()
    insights = adapter.get_adaptation_insights()
    
    if 'error' in insights:
        logger.warning(f"Adaptation insights error: {insights['error']}")
        return
    
    stats = insights.get('adaptation_stats', {})
    recommendations = insights.get('recommendations', [])
    
    logger.info("🧠 OACP Adaptation Insights")
    logger.info(f"   Agent: {insights.get('agent_role', 'unknown')}")
    logger.info(f"   Total Rejections: {stats.get('total_rejections', 0)}")
    logger.info(f"   Total Adaptations: {stats.get('total_adaptations', 0)}")
    logger.info(f"   Common Patterns: {stats.get('common_patterns', [])}")
    
    if recommendations:
        logger.info("💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"   {i}. {rec}")


# Convenience function for backward compatibility
def get_adapted_prompt(original_prompt: str, attempt: int = 1) -> str:
    """
    Get an adapted prompt based on rejection feedback.
    
    Args:
        original_prompt: The original prompt
        attempt: Current attempt number
        
    Returns:
        Adapted prompt or original if no adaptation needed
    """
    try:
        ctx = current_context()
        return adapt_prompt_for_retry(
            original_prompt=original_prompt,
            agent_role=ctx.role or "unknown",
            node_id=ctx.node_id or "unknown", 
            attempt=attempt
        )
    except Exception as e:
        logger.warning(f"Failed to adapt prompt: {e}")
        return original_prompt
