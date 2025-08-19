"""OACP storage backends."""

from .base import IStorage, IAsyncStorage
from .file import FileStorage
from .sqlite import SQLiteStorage

__all__ = ["IStorage", "IAsyncStorage", "FileStorage", "SQLiteStorage"]

# Conditionally export PostgreSQL storage if available
try:
    from .postgres import PostgreSQLStorage
    __all__.append("PostgreSQLStorage")
except ImportError:
    pass


def create_storage(uri: str) -> IStorage:
    """Factory function to create storage backend from URI."""
    if uri.startswith("file://"):
        path = uri[7:]  # Remove "file://" prefix
        return FileStorage(path)
    elif uri.startswith("sqlite:///"):
        path = uri[10:]  # Remove "sqlite:///" prefix
        return SQLiteStorage(path)
    elif uri.startswith("postgresql://"):
        return PostgreSQLStorage(uri)
    else:
        raise ValueError(f"Unsupported storage URI: {uri}")

