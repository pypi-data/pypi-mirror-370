"""AsyncPGX - High-performance asynchronous PostgreSQL wrapper with Redis-like API."""

from .client import AsyncPostgresClient
from .client import PostgresClient  # Alias for compatibility

__version__ = "1.0.0"
__author__ = "AsyncPGX Team"
__description__ = "Fast asynchronous PostgreSQL wrapper with Redis-like API"

# Export main classes
__all__ = [
    "AsyncPostgresClient",
    "PostgresClient",
]

# For convenience, create an alias
asyncpgx = AsyncPostgresClient