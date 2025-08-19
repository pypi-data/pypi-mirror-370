"""File-based storage backend for OACP."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Iterator, Any
import threading
import time

from .base import IStorage
from ..events import EventBase, VoteCast
from ..contracts import DecisionContract
from ..utils import json_dumps
from ..errors import OacpStorageError


class FileStorage(IStorage):
    """File-based storage implementation using JSONL format."""
    
    def __init__(self, base_path: str = "./logs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._locks: dict[str, threading.Lock] = {}
    
    def _get_lock(self, run_id: str) -> threading.Lock:
        """Get or create a lock for a run."""
        if run_id not in self._locks:
            self._locks[run_id] = threading.Lock()
        return self._locks[run_id]
    
    def _get_file_path(self, run_id: str) -> Path:
        """Get file path for a run."""
        return self.base_path / f"{run_id}.jsonl"
    
    def append(self, event: EventBase) -> None:
        """Append an event to the run's JSONL file."""
        file_path = self._get_file_path(event.run_id)
        lock = self._get_lock(event.run_id)
        
        try:
            with lock:
                with open(file_path, "a", encoding="utf-8") as f:
                    json_line = json_dumps(event.model_dump())
                    f.write(json_line + "\n")
                    f.flush()
                    os.fsync(f.fileno())  # Ensure write to disk
        except Exception as e:
            raise OacpStorageError(f"Failed to append event: {e}", run_id=event.run_id)
    
    def iterate(
        self, 
        run_id: str, 
        from_timestamp: datetime | None = None
    ) -> Iterator[EventBase]:
        """Iterate events from a run's JSONL file."""
        file_path = self._get_file_path(run_id)
        
        if not file_path.exists():
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        event_data = json.loads(line)
                        event = self._deserialize_event(event_data)
                        
                        if from_timestamp and event.timestamp < from_timestamp:
                            continue
                        
                        yield event
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines
        except Exception as e:
            raise OacpStorageError(f"Failed to read events: {e}", run_id=run_id)
    
    def await_votes(
        self, 
        run_id: str, 
        contract: DecisionContract, 
        window_seconds: int
    ) -> dict[str, Any]:
        """Wait for votes by polling the file."""
        start_time = time.time()
        votes: dict[str, VoteCast] = {}
        
        while time.time() - start_time < window_seconds:
            # Read all events and extract votes
            current_votes = {}
            for event in self.iterate(run_id):
                if isinstance(event, VoteCast) and event.voter_id in contract.required_approvers:
                    current_votes[event.voter_id] = event
            
            votes.update(current_votes)
            
            # Check if we have all required votes
            if all(voter in votes for voter in contract.required_approvers):
                break
            
            # Poll interval
            time.sleep(0.5)
        
        return {
            "votes": votes,
            "timeout": time.time() - start_time >= window_seconds,
            "missing_voters": [
                voter for voter in contract.required_approvers 
                if voter not in votes
            ]
        }
    
    def _deserialize_event(self, event_data: dict) -> EventBase:
        """Deserialize event data to appropriate event class."""
        event_type = event_data.get("event_type")
        
        # Import here to avoid circular imports
        from ..events import (
            TaskStart, NodeStart, NodeResult, VoteCast, 
            ConflictRaised, DecisionFinalized, RetryScheduled, RunSummary
        )
        
        event_classes = {
            "TaskStart": TaskStart,
            "NodeStart": NodeStart,
            "NodeResult": NodeResult,
            "VoteCast": VoteCast,
            "ConflictRaised": ConflictRaised,
            "DecisionFinalized": DecisionFinalized,
            "RetryScheduled": RetryScheduled,
            "RunSummary": RunSummary,
        }
        
        event_class = event_classes.get(event_type, EventBase)
        return event_class(**event_data)
    
    def close(self) -> None:
        """Close storage (no-op for file storage)."""
        pass


