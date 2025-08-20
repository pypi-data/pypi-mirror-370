"""INCR command implementation for AsyncPGX."""

from typing import TYPE_CHECKING
from ..utils.serialization import deserialize_value, serialize_value, ensure_numeric

if TYPE_CHECKING:
    from ..connection import ConnectionPool


async def incr_command(pool: "ConnectionPool", key: str, amount: int = 1) -> int:
    """Increment integer value.
    
    Args:
        pool: Database connection pool
        key: The key to increment
        amount: Amount to increment by (default: 1)
        
    Returns:
        New value after increment
    """
    try:
        # Try to get current value
        row = await pool.fetchrow(
            """
            SELECT value, value_type FROM asyncpgx_store 
            WHERE key = $1 AND (expires_at IS NULL OR expires_at > NOW())
            """,
            key
        )
        
        if row is None:
            new_value = amount
        else:
            current = deserialize_value(bytes(row['value']), row['value_type'])
            current_num = ensure_numeric(current)
            new_value = int(current_num) + amount
        
        # Store the new value
        serialized_value, value_type = serialize_value(new_value)
        await pool.execute(
            """
            INSERT INTO asyncpgx_store (key, value, value_type)
            VALUES ($1, $2, $3)
            ON CONFLICT (key) DO UPDATE SET
                value = EXCLUDED.value,
                value_type = EXCLUDED.value_type,
                updated_at = NOW()
            """,
            key, serialized_value, value_type
        )
        
        return new_value
    except Exception as e:
        raise ValueError(f"Cannot increment key '{key}': {e}")