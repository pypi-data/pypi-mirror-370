"""SQLite storage backend for OACP."""

import json
import sqlite3
import time
from datetime import datetime
from typing import Iterator, Any

from .base import IStorage
from ..events import EventBase, VoteCast
from ..contracts import DecisionContract
from ..utils import json_dumps
from ..errors import OacpStorageError


class SQLiteStorage(IStorage):
    """SQLite storage implementation."""
    
    def __init__(self, db_path: str = "oacp.db"):
        self.db_path = db_path
        self._connection = None
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        event_id TEXT PRIMARY KEY,
                        run_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        payload TEXT NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_run_id 
                    ON events(run_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_timestamp 
                    ON events(run_id, timestamp)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_type 
                    ON events(run_id, event_type)
                """)
                
                conn.commit()
        except Exception as e:
            raise OacpStorageError(f"Failed to initialize database: {e}")
    
    def append(self, event: EventBase) -> None:
        """Append an event to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO events 
                    (event_id, run_id, timestamp, event_type, payload)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        event.event_id,
                        event.run_id,
                        event.timestamp.isoformat(),
                        event.event_type,
                        json_dumps(event.model_dump())
                    )
                )
                conn.commit()
        except Exception as e:
            raise OacpStorageError(f"Failed to append event: {e}", run_id=event.run_id)
    
    def iterate(
        self, 
        run_id: str, 
        from_timestamp: datetime | None = None
    ) -> Iterator[EventBase]:
        """Iterate events from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if from_timestamp:
                    cursor = conn.execute(
                        """
                        SELECT payload FROM events 
                        WHERE run_id = ? AND timestamp >= ?
                        ORDER BY timestamp
                        """,
                        (run_id, from_timestamp.isoformat())
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT payload FROM events 
                        WHERE run_id = ?
                        ORDER BY timestamp
                        """,
                        (run_id,)
                    )
                
                for (payload,) in cursor:
                    try:
                        event_data = json.loads(payload)
                        yield self._deserialize_event(event_data)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            raise OacpStorageError(f"Failed to read events: {e}", run_id=run_id)
    
    def await_votes(
        self, 
        run_id: str, 
        contract: DecisionContract, 
        window_seconds: int
    ) -> dict[str, Any]:
        """Wait for votes by polling the database."""
        start_time = time.time()
        votes: dict[str, VoteCast] = {}
        
        while time.time() - start_time < window_seconds:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        """
                        SELECT payload FROM events 
                        WHERE run_id = ? AND event_type = 'VoteCast'
                        ORDER BY timestamp
                        """,
                        (run_id,)
                    )
                    
                    current_votes = {}
                    for (payload,) in cursor:
                        try:
                            event_data = json.loads(payload)
                            vote = VoteCast(**event_data)
                            if vote.voter_id in contract.required_approvers:
                                current_votes[vote.voter_id] = vote
                        except (json.JSONDecodeError, TypeError):
                            continue
                    
                    votes.update(current_votes)
                    
                    # Check if we have all required votes
                    if all(voter in votes for voter in contract.required_approvers):
                        break
                    
            except Exception:
                pass  # Continue polling on error
            
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
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

