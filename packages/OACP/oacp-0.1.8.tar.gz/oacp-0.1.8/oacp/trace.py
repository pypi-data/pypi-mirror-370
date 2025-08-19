"""Trace writing and reading for OACP."""

import logging
from typing import Any

from .storage.base import IStorage
from .storage import create_storage
from .events import EventBase
from .context import get_config
from .errors import OacpStorageError

logger = logging.getLogger(__name__)


class TraceWriter:
    """Writes events to storage backend."""
    
    def __init__(self, storage: IStorage | None = None):
        if storage is None:
            config = get_config()
            storage = create_storage(config["storage_uri"])
        self.storage = storage
    
    def write(self, event: EventBase) -> None:
        """Write an event to storage."""
        try:
            self.storage.append(event)
            logger.debug(f"Wrote event {event.event_type} for run {event.run_id}")
        except Exception as e:
            logger.error(f"Failed to write event: {e}")
            raise OacpStorageError(f"Failed to write event: {e}", run_id=event.run_id)
    
    def close(self) -> None:
        """Close the trace writer."""
        self.storage.close()


class TraceReader:
    """Reads events from storage backend."""
    
    def __init__(self, storage: IStorage | None = None):
        if storage is None:
            config = get_config()
            storage = create_storage(config["storage_uri"])
        self.storage = storage
    
    def read_run(self, run_id: str) -> list[EventBase]:
        """Read all events for a run."""
        try:
            return list(self.storage.iterate(run_id))
        except Exception as e:
            logger.error(f"Failed to read run {run_id}: {e}")
            raise OacpStorageError(f"Failed to read run: {e}", run_id=run_id)
    
    def close(self) -> None:
        """Close the trace reader."""
        self.storage.close()