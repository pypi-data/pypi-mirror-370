"""Utility functions for OACP."""

import hashlib
import json
from datetime import datetime
from typing import Any
import ulid


def generate_id() -> str:
    """Generate a unique ULID."""
    return ulid.new().str


def generate_idempotency_key(inputs: dict[str, Any]) -> str:
    """Generate idempotency key from inputs."""
    # Create stable hash of inputs
    json_str = json.dumps(inputs, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


def json_dumps(obj: Any) -> str:
    """JSON serialization with datetime and enum support."""
    def default_serializer(o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, 'value'):  # Enum
            return o.value
        raise TypeError(f"Object of type {type(o)} is not JSON serializable")
    
    return json.dumps(obj, default=default_serializer, sort_keys=True)


def redact_sensitive_data(
    data: Any, 
    redact_keys: list[str] | None = None
) -> Any:
    """Redact sensitive keys from data."""
    if not redact_keys:
        redact_keys = ["password", "api_key", "secret", "token"]
    
    # Only redact if data is a dictionary
    if isinstance(data, dict):
        redacted = data.copy()
        for key in redact_keys:
            if key in redacted:
                redacted[key] = "***REDACTED***"
        return redacted
    
    # For non-dict data, return as-is
    return data


def truncate_large_payload(data: Any, max_size: int = 1024 * 1024) -> tuple[Any, bool]:
    """Truncate large payloads and return (truncated_data, was_truncated)."""
    json_str = json_dumps(data)
    
    if len(json_str) <= max_size:
        return data, False
    
    # Return truncated version with hash
    truncated = {
        "_truncated": True,
        "_original_size": len(json_str),
        "_hash": hashlib.sha256(json_str.encode()).hexdigest(),
        "_preview": json_str[:max_size // 2] + "...[TRUNCATED]..."
    }
    return truncated, True


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()

