"""EXISTS command implementation for AsyncPGX."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..connection import ConnectionPool


async def exists_command(pool: "ConnectionPool", key: str) -> bool:
    """Check if key exists.
    
    Args:
        pool: Database connection pool
        key: The key to check
        
    Returns:
        True if key exists and not expired
    """
    try:
        result = await pool.fetchval(
            """
            SELECT 1 FROM asyncpgx_store 
            WHERE key = $1 AND (expires_at IS NULL OR expires_at > NOW())
            """,
            key
        )
        return result is not None
    except Exception:
        return False