"""Main client class for AsyncPGX."""

import asyncio
from datetime import datetime, timezone
from typing import Any, List, Optional, Union

from .connection import ConnectionPool
from .utils.schema import ensure_table_exists, cleanup_expired_keys
from .utils.serialization import serialize_value, deserialize_value, ensure_numeric
from .utils.patterns import optimize_pattern_query


class AsyncPostgresClient:
    """High-performance asynchronous PostgreSQL client with Redis-like API."""
    
    def __init__(
        self,
        url: str,
        min_connections: int = 5,
        max_connections: int = 20,
        command_timeout: float = 60.0,
        auto_cleanup: bool = True,
        cleanup_interval: int = 300  # 5 minutes
    ):
        """Initialize AsyncPostgresClient.
        
        Args:
            url: PostgreSQL connection URL
            min_connections: Minimum connections in pool
            max_connections: Maximum connections in pool
            command_timeout: Command timeout in seconds
            auto_cleanup: Enable automatic cleanup of expired keys
            cleanup_interval: Cleanup interval in seconds
        """
        self.pool = ConnectionPool(
            url=url,
            min_size=min_connections,
            max_size=max_connections,
            command_timeout=command_timeout
        )
        self.auto_cleanup = auto_cleanup
        self.cleanup_interval = cleanup_interval
        self._cleanup_task: Optional[asyncio.Task] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to PostgreSQL and initialize schema."""
        if self._connected:
            return
        
        await self.pool.connect()
        await ensure_table_exists(self.pool)
        
        if self.auto_cleanup:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        self._connected = True
    
    async def disconnect(self) -> None:
        """Disconnect from PostgreSQL."""
        if not self._connected:
            return
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        await self.pool.disconnect()
        self._connected = False
    
    async def _cleanup_loop(self) -> None:
        """Background task to clean up expired keys."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await cleanup_expired_keys(self.pool)
            except asyncio.CancelledError:
                break
            except Exception:
                # Continue cleanup loop even if one iteration fails
                continue
    
    async def _ensure_connected(self) -> None:
        """Ensure client is connected."""
        if not self._connected:
            await self.connect()
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Store a key with a value.
        
        Args:
            key: The key to store
            value: The value to store (must be serializable)
            expire: TTL in seconds (optional)
            
        Returns:
            True if stored successfully
        """
        await self._ensure_connected()
        
        serialized_value, value_type = serialize_value(value)
        expires_at = None
        
        if expire is not None and expire > 0:
            expires_at = datetime.now(timezone.utc).timestamp() + expire
        
        try:
            await self.pool.execute(
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
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value of key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value if exists and not expired, else None
        """
        await self._ensure_connected()
        
        try:
            row = await self.pool.fetchrow(
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
    
    async def delete(self, *keys: str) -> int:
        """Delete one or multiple keys.
        
        Args:
            keys: One or more keys to delete
            
        Returns:
            Number of deleted keys
        """
        await self._ensure_connected()
        
        if not keys:
            return 0
        
        try:
            result = await self.pool.execute(
                "DELETE FROM asyncpgx_store WHERE key = ANY($1)",
                list(keys)
            )
            # Extract number from "DELETE n" result
            return int(result.split()[-1]) if result else 0
        except Exception:
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists.
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists and not expired
        """
        await self._ensure_connected()
        
        try:
            result = await self.pool.fetchval(
                """
                SELECT 1 FROM asyncpgx_store 
                WHERE key = $1 AND (expires_at IS NULL OR expires_at > NOW())
                """,
                key
            )
            return result is not None
        except Exception:
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """List all keys matching a pattern.
        
        Args:
            pattern: Glob-style pattern (default: "*" for all keys)
            
        Returns:
            List of matching keys
        """
        await self._ensure_connected()
        
        try:
            query, params = optimize_pattern_query(pattern)
            rows = await self.pool.fetch(query, *params)
            return [row['key'] for row in rows]
        except Exception:
            return []
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set TTL on key.
        
        Args:
            key: The key to set TTL on
            seconds: TTL in seconds
            
        Returns:
            True if TTL was set, False if key doesn't exist
        """
        await self._ensure_connected()
        
        if seconds <= 0:
            return False
        
        expires_at = datetime.now(timezone.utc).timestamp() + seconds
        
        try:
            result = await self.pool.execute(
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
    
    async def ttl(self, key: str) -> int:
        """Get remaining TTL.
        
        Args:
            key: The key to check TTL for
            
        Returns:
            Remaining seconds, -1 if no TTL, -2 if key doesn't exist
        """
        await self._ensure_connected()
        
        try:
            row = await self.pool.fetchrow(
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
                await self.delete(key)
                return -2
            
            return int(remaining)
        except Exception:
            return -2
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment integer value.
        
        Args:
            key: The key to increment
            amount: Amount to increment by (default: 1)
            
        Returns:
            New value after increment
        """
        await self._ensure_connected()
        
        try:
            # Try to get current value
            current = await self.get(key)
            if current is None:
                new_value = amount
            else:
                current_num = ensure_numeric(current)
                new_value = int(current_num) + amount
            
            await self.set(key, new_value)
            return new_value
        except Exception as e:
            raise ValueError(f"Cannot increment key '{key}': {e}")
    
    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement integer value.
        
        Args:
            key: The key to decrement
            amount: Amount to decrement by (default: 1)
            
        Returns:
            New value after decrement
        """
        return await self.incr(key, -amount)
    
    async def flushall(self) -> bool:
        """Remove all keys from storage.
        
        Returns:
            True if operation succeeds
        """
        await self._ensure_connected()
        
        try:
            await self.pool.execute("TRUNCATE TABLE asyncpgx_store")
            return True
        except Exception:
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Alias for compatibility
PostgresClient = AsyncPostgresClient