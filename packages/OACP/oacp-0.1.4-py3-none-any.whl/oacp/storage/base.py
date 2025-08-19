"""Storage interface for OACP."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Iterator
from datetime import datetime

from ..events import EventBase
from ..contracts import DecisionContract


class IStorage(ABC):
    """Interface for OACP storage backends."""
    
    @abstractmethod
    def append(self, event: EventBase) -> None:
        """Append an event to storage."""
        pass
    
    @abstractmethod
    def iterate(
        self, 
        run_id: str, 
        from_timestamp: datetime | None = None
    ) -> Iterator[EventBase]:
        """Iterate events for a run."""
        pass
    
    @abstractmethod
    def await_votes(
        self, 
        run_id: str, 
        contract: DecisionContract, 
        window_seconds: int
    ) -> dict[str, Any]:
        """Wait for votes and return results."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close storage connection."""
        pass


class IAsyncStorage(ABC):
    """Async interface for OACP storage backends."""
    
    @abstractmethod
    async def append(self, event: EventBase) -> None:
        """Append an event to storage."""
        pass
    
    @abstractmethod
    async def iterate(
        self, 
        run_id: str, 
        from_timestamp: datetime | None = None
    ) -> AsyncIterator[EventBase]:
        """Iterate events for a run."""
        pass
    
    @abstractmethod
    async def await_votes(
        self, 
        run_id: str, 
        contract: DecisionContract, 
        window_seconds: int
    ) -> dict[str, Any]:
        """Wait for votes and return results."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close storage connection."""
        pass
