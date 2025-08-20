"""GET command implementation for AsyncPGX."""

from typing import Any, Optional, TYPE_CHECKING
from ..utils.serialization import deserialize_value

if TYPE_CHECKING:
    from ..connection import ConnectionPool


async def get_command(pool: "ConnectionPool", key: str) -> Optional[Any]:
    """Retrieve value of key.
    
    Args:
        pool: Database connection pool
        key: The key to retrieve
        
    Returns:
        The value if exists and not expired, else None
    """
    try:
        row = await pool.fetchrow(
            """
            SELECT value, value_type FROM asyncpgx_store 
            WHERE key = $1 AND (expires_at IS NULL OR expires_at > NOW())
            """,
            key
        )
        
        if row is None:
            return None
        
        return deserialize_value(bytes(row['value']), row['value_type'])
    except Exception:
        return None