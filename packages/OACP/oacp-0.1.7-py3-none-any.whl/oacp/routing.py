"""Retry and routing logic for OACP."""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Any

from .events import RetryScheduled
from .errors import OacpError, OacpRetryExhausted

logger = logging.getLogger(__name__)


class RetryPolicy:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        delay = self.base_delay * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add ±25% jitter
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0.1, delay)  # Minimum 100ms delay


def retry_or_reraise(
    error: OacpError,
    policy: RetryPolicy,
    current_attempt: int = 1,
    trace_writer: Any = None,
) -> None:
    """Handle retry logic for OACP errors.
    
    Args:
        error: The error that occurred
        policy: Retry policy configuration
        current_attempt: Current attempt number (1-based)
        trace_writer: Trace writer to log retry events
        
    Raises:
        OacpRetryExhausted: If max attempts exceeded
        OacpError: The original error if not retryable
    """
    if current_attempt >= policy.max_attempts:
        logger.error(f"Retry exhausted after {current_attempt} attempts: {error}")
        raise OacpRetryExhausted(
            f"Retry exhausted after {current_attempt} attempts: {error}",
            max_attempts=policy.max_attempts,
            run_id=error.run_id,
            node_id=error.node_id,
        )
    
    delay = policy.calculate_delay(current_attempt)
    next_attempt_at = datetime.utcnow() + timedelta(seconds=delay)
    
    logger.info(f"Scheduling retry {current_attempt + 1} in {delay:.2f}s: {error}")
    
    # Log retry event if trace writer available
    if trace_writer and error.run_id and error.node_id:
        retry_event = RetryScheduled(
            run_id=error.run_id,
            node_id=error.node_id,
            attempt_number=current_attempt + 1,
            next_attempt_at=next_attempt_at,
            reason=str(error),
            backoff_ms=int(delay * 1000),
        )
        trace_writer.write(retry_event)
    
    # Sleep for the calculated delay
    time.sleep(delay)