"""SET command implementation for AsyncPGX."""

from datetime import datetime, timezone
from typing import Any, Optional, TYPE_CHECKING
from ..utils.serialization import serialize_value

if TYPE_CHECKING:
    from ..connection import ConnectionPool


async def set_command(
    pool: "ConnectionPool", 
    key: str, 
    value: Any, 
    expire: Optional[int] = None
) -> bool:
    """Store a key with a value.
    
    Args:
        pool: Database connection pool
        key: The key to store
        value: The value to store (must be serializable)
        expire: TTL in seconds (optional)
        
    Returns:
        True if stored successfully
    """
    serialized_value, value_type = serialize_value(value)
    expires_at = None
    
    if expire is not None and expire > 0:
        expires_at = datetime.now(timezone.utc).timestamp() + expire
    
    try:
        await pool.execute(
            """
            INSERT INTO asyncpgx_store (key, value, value_type, expires_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (key) DO UPDATE SET
                value = EXCLUDED.value,
                value_type = EXCLUDED.value_type,
                expires_at = EXCLUDED.expires_at,
                updated_at = NOW()
            """,
            key, serialized_value, value_type, 
            datetime.fromtimestamp(expires_at, timezone.utc) if expires_at else None
        )
        return True
    except Exception:
        return False