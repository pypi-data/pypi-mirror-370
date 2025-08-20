"""KEYS command implementation for AsyncPGX."""

from typing import List, TYPE_CHECKING
from ..utils.patterns import optimize_pattern_query

if TYPE_CHECKING:
    from ..connection import ConnectionPool


async def keys_command(pool: "ConnectionPool", pattern: str = "*") -> List[str]:
    """List all keys matching a pattern.
    
    Args:
        pool: Database connection pool
        pattern: Glob-style pattern (default: "*" for all keys)
        
    Returns:
        List of matching keys
    """
    try:
        query, params = optimize_pattern_query(pattern)
        rows = await pool.fetch(query, *params)
        return [row['key'] for row in rows]
    except Exception:
        return []