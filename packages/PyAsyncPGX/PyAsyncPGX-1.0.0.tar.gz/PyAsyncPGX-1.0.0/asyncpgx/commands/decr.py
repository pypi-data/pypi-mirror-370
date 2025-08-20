"""DECR command implementation for AsyncPGX."""

from typing import TYPE_CHECKING
from .incr import incr_command

if TYPE_CHECKING:
    from ..connection import ConnectionPool


async def decr_command(pool: "ConnectionPool", key: str, amount: int = 1) -> int:
    """Decrement integer value.
    
    Args:
        pool: Database connection pool
        key: The key to decrement
        amount: Amount to decrement by (default: 1)
        
    Returns:
        New value after decrement
    """
    return await incr_command(pool, key, -amount)