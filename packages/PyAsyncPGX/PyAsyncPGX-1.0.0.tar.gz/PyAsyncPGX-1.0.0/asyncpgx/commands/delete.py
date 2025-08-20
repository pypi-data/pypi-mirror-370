"""DELETE command implementation for AsyncPGX."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..connection import ConnectionPool


async def delete_command(pool: "ConnectionPool", *keys: str) -> int:
    """Delete one or multiple keys.
    
    Args:
        pool: Database connection pool
        keys: One or more keys to delete
        
    Returns:
        Number of deleted keys
    """
    if not keys:
        return 0
    
    try:
        result = await pool.execute(
            "DELETE FROM asyncpgx_store WHERE key = ANY($1)",
            list(keys)
        )
        # Extract number from "DELETE n" result
        return int(result.split()[-1]) if result else 0
    except Exception:
        return 0