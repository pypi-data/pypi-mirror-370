"""Context management for OACP."""

import os
from contextvars import ContextVar
from typing import Any, TYPE_CHECKING
from dataclasses import dataclass

from .contracts import DecisionContract

if TYPE_CHECKING:
    from .trace import TraceWriter


@dataclass
class OacpContext:
    """OACP execution context."""
    run_id: str
    task_id: str | None = None
    node_id: str | None = None
    role: str | None = None
    trace_writer: "TraceWriter | None" = None
    contract: DecisionContract | None = None
    metadata: dict[str, Any] | None = None


# Context variable to store current OACP context
_current_context: ContextVar[OacpContext | None] = ContextVar(
    "oacp_context", default=None
)


def current_context() -> OacpContext:
    """Get the current OACP context."""
    ctx = _current_context.get()
    if ctx is None:
        raise RuntimeError("No OACP context available. Are you inside an @with_oacp decorated function?")
    return ctx


def set_context(context: OacpContext) -> None:
    """Set the current OACP context."""
    _current_context.set(context)


def clear_context() -> None:
    """Clear the current OACP context."""
    _current_context.set(None)


def get_config() -> dict[str, Any]:
    """Get OACP configuration from environment or config file."""
    config = {
        "storage_uri": os.getenv("OACP_STORAGE_URI", "file://./logs"),
        "log_level": os.getenv("OACP_LOG_LEVEL", "INFO"),
        "timezone": os.getenv("OACP_TZ", "UTC"),
        "redact_keys": os.getenv("OACP_REDACT_KEYS", "password,api_key,secret,token").split(","),
        "max_payload_size": int(os.getenv("OACP_MAX_PAYLOAD_SIZE", str(1024 * 1024))),
        "signing_key": os.getenv("OACP_SIGNING_KEY"),
        "tenant_id": os.getenv("OACP_TENANT_ID"),
    }
    
    # Try to load from oacp.toml if it exists
    try:
        import tomllib
        with open("oacp.toml", "rb") as f:
            toml_config = tomllib.load(f)
            config.update(toml_config.get("oacp", {}))
    except (FileNotFoundError, ImportError):
        pass
    
    return config
