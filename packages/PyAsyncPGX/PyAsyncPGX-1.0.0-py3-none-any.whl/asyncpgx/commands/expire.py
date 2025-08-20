"""EXPIRE command implementation for AsyncPGX."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..connection import ConnectionPool


async def expire_command(pool: "ConnectionPool", key: str, seconds: int) -> bool:
    """Set TTL on key.
    
    Args:
        pool: Database connection pool
        key: The key to set TTL on
        seconds: TTL in seconds
        
    Returns:
        True if TTL was set, False if key doesn't exist
    """
    if seconds <= 0:
        return False
    
    expires_at = datetime.now(timezone.utc).timestamp() + seconds
    
    try:
        result = await pool.execute(
            """
            UPDATE asyncpgx_store 
            SET expires_at = $2, updated_at = NOW()
            WHERE key = $1 AND (expires_at IS NULL OR expires_at > NOW())
            """,
            key, datetime.fromtimestamp(expires_at, timezone.utc)
        )
        return int(result.split()[-1]) > 0 if result else False
    except Exception:
        return False