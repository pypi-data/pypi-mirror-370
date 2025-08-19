"""PostgreSQL storage backend for OACP."""

import json
import time
from datetime import datetime
from typing import Iterator, Any

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None

from .base import IStorage
from ..events import EventBase, VoteCast
from ..contracts import DecisionContract
from ..utils import json_dumps
from ..errors import OacpStorageError


class PostgreSQLStorage(IStorage):
    """PostgreSQL storage implementation."""
    
    def __init__(self, connection_string: str):
        if psycopg is None:
            raise ImportError("psycopg is required for PostgreSQL storage. Install with: pip install oacp[postgres]")
        
        self.connection_string = connection_string
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        try:
            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS events (
                            event_id TEXT PRIMARY KEY,
                            run_id TEXT NOT NULL,
                            timestamp TIMESTAMPTZ NOT NULL,
                            event_type TEXT NOT NULL,
                            payload JSONB NOT NULL
                        )
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_events_run_id 
                        ON events(run_id)
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_events_timestamp 
                        ON events(run_id, timestamp)
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_events_type 
                        ON events(run_id, event_type)
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_events_payload 
                        ON events USING GIN(payload)
                    """)
                    
                    conn.commit()
        except Exception as e:
            raise OacpStorageError(f"Failed to initialize database: {e}")
    
    def append(self, event: EventBase) -> None:
        """Append an event to the database."""
        try:
            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO events 
                        (event_id, run_id, timestamp, event_type, payload)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (event_id) DO UPDATE SET
                            timestamp = EXCLUDED.timestamp,
                            payload = EXCLUDED.payload
                        """,
                        (
                            event.event_id,
                            event.run_id,
                            event.timestamp,
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
            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    if from_timestamp:
                        cur.execute(
                            """
                            SELECT payload FROM events 
                            WHERE run_id = %s AND timestamp >= %s
                            ORDER BY timestamp
                            """,
                            (run_id, from_timestamp)
                        )
                    else:
                        cur.execute(
                            """
                            SELECT payload FROM events 
                            WHERE run_id = %s
                            ORDER BY timestamp
                            """,
                            (run_id,)
                        )
                    
                    for row in cur:
                        try:
                            event_data = row["payload"]
                            yield self._deserialize_event(event_data)
                        except (TypeError, KeyError):
                            continue
        except Exception as e:
            raise OacpStorageError(f"Failed to read events: {e}", run_id=run_id)
    
    def await_votes(
        self, 
        run_id: str, 
        contract: DecisionContract, 
        window_seconds: int
    ) -> dict[str, Any]:
        """Wait for votes using PostgreSQL NOTIFY/LISTEN."""
        start_time = time.time()
        votes: dict[str, VoteCast] = {}
        
        try:
            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    while time.time() - start_time < window_seconds:
                        cur.execute(
                            """
                            SELECT payload FROM events 
                            WHERE run_id = %s AND event_type = 'VoteCast'
                            ORDER BY timestamp
                            """,
                            (run_id,)
                        )
                        
                        current_votes = {}
                        for row in cur:
                            try:
                                event_data = row["payload"]
                                vote = VoteCast(**event_data)
                                if vote.voter_id in contract.required_approvers:
                                    current_votes[vote.voter_id] = vote
                            except (TypeError, KeyError):
                                continue
                        
                        votes.update(current_votes)
                        
                        # Check if we have all required votes
                        if all(voter in votes for voter in contract.required_approvers):
                            break
                        
                        time.sleep(0.5)
                        
        except Exception:
            pass  # Continue with what we have
        
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
        pass
