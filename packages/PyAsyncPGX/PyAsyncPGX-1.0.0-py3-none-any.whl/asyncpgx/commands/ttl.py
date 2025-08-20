"""TTL command implementation for AsyncPGX."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..connection import ConnectionPool


async def ttl_command(pool: "ConnectionPool", key: str) -> int:
    """Get remaining TTL.
    
    Args:
        pool: Database connection pool
        key: The key to check TTL for
        
    Returns:
        Remaining seconds, -1 if no TTL, -2 if key doesn't exist
    """
    try:
        row = await pool.fetchrow(
            "SELECT expires_at FROM asyncpgx_store WHERE key = $1",
            key
        )
        
        if row is None:
            return -2  # Key doesn't exist
        
        expires_at = row['expires_at']
        if expires_at is None:
            return -1  # No TTL set
        
        remaining = expires_at.timestamp() - datetime.now(timezone.utc).timestamp()
        if remaining <= 0:
            # Key has expired, delete it
            await pool.execute("DELETE FROM asyncpgx_store WHERE key = $1", key)
            return -2
        
        return int(remaining)
    except Exception:
        return -2