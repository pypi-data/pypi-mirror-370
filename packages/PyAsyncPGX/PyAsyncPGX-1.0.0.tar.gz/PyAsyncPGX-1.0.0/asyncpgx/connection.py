"""Connection pooling module for AsyncPGX."""

import asyncio
import asyncpg
from typing import Optional, Dict, Any
from urllib.parse import urlparse


class ConnectionPool:
    """High-performance connection pool for PostgreSQL."""
    
    def __init__(
        self,
        url: str,
        min_size: int = 5,
        max_size: int = 20,
        command_timeout: float = 60.0,
        server_settings: Optional[Dict[str, str]] = None
    ):
        """Initialize connection pool.
        
        Args:
            url: PostgreSQL connection URL
            min_size: Minimum number of connections in pool
            max_size: Maximum number of connections in pool
            command_timeout: Command timeout in seconds
            server_settings: Additional server settings
        """
        self.url = url
        self.min_size = min_size
        self.max_size = max_size
        self.command_timeout = command_timeout
        self.server_settings = server_settings or {}
        self._pool: Optional[asyncpg.Pool] = None
        self._lock = asyncio.Lock()
    
    async def connect(self) -> None:
        """Create and initialize the connection pool."""
        if self._pool is not None:
            return
        
        async with self._lock:
            if self._pool is not None:
                return
            
            # Parse connection URL to extract components
            parsed = urlparse(self.url)
            
            connection_kwargs = {
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path.lstrip('/') if parsed.path else 'postgres',
                'min_size': self.min_size,
                'max_size': self.max_size,
                'command_timeout': self.command_timeout,
                'server_settings': self.server_settings
            }
            
            # Remove None values
            connection_kwargs = {k: v for k, v in connection_kwargs.items() if v is not None}
            
            try:
                self._pool = await asyncpg.create_pool(**connection_kwargs)
            except Exception as e:
                raise ConnectionError(f"Failed to create connection pool: {e}")
    
    async def disconnect(self) -> None:
        """Close the connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
    
    async def acquire(self) -> asyncpg.Connection:
        """Acquire a connection from the pool."""
        if self._pool is None:
            await self.connect()
        
        return await self._pool.acquire()
    
    async def release(self, connection: asyncpg.Connection) -> None:
        """Release a connection back to the pool."""
        if self._pool is not None:
            await self._pool.release(connection)
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query and return the result."""
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> list:
        """Fetch multiple rows from a query."""
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch a single row from a query."""
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args) -> Any:
        """Fetch a single value from a query."""
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    @property
    def is_connected(self) -> bool:
        """Check if the pool is connected."""
        return self._pool is not None and not self._pool._closed
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()