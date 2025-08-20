"""FLUSHALL command implementation for AsyncPGX."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..connection import ConnectionPool


async def flushall_command(pool: "ConnectionPool") -> bool:
    """Remove all keys from storage.
    
    Args:
        pool: Database connection pool
        
    Returns:
        True if operation succeeds
    """
    try:
        await pool.execute("TRUNCATE TABLE asyncpgx_store")
        return True
    except Exception:
        return False