"""Schema management utilities for AsyncPGX."""

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..connection import ConnectionPool


# Optimized schema for high-performance key-value storage
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS asyncpgx_store (
    key TEXT PRIMARY KEY,
    value BYTEA NOT NULL,
    value_type SMALLINT NOT NULL DEFAULT 0,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

# Index for efficient TTL cleanup
CREATE_EXPIRES_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_asyncpgx_store_expires_at 
ON asyncpgx_store (expires_at) 
WHERE expires_at IS NOT NULL;
"""

# Index for pattern matching (keys command)
CREATE_KEY_PATTERN_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_asyncpgx_store_key_pattern 
ON asyncpgx_store USING gin (key gin_trgm_ops);
"""

# Enable trigram extension for pattern matching
CREATE_TRIGRAM_EXTENSION_SQL = """
CREATE EXTENSION IF NOT EXISTS pg_trgm;
"""

# Function to automatically update updated_at timestamp
CREATE_UPDATE_TIMESTAMP_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
"""

# Trigger to automatically update updated_at
CREATE_UPDATE_TRIGGER_SQL = """
DROP TRIGGER IF EXISTS update_asyncpgx_store_updated_at ON asyncpgx_store;
CREATE TRIGGER update_asyncpgx_store_updated_at
    BEFORE UPDATE ON asyncpgx_store
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""

# Cleanup expired keys function for better performance
CREATE_CLEANUP_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION cleanup_expired_keys(batch_size INTEGER DEFAULT 1000)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM asyncpgx_store 
    WHERE expires_at IS NOT NULL 
    AND expires_at <= NOW()
    AND key IN (
        SELECT key FROM asyncpgx_store 
        WHERE expires_at IS NOT NULL 
        AND expires_at <= NOW()
        LIMIT batch_size
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
"""


async def create_schema(pool: "ConnectionPool") -> None:
    """Create the complete schema for AsyncPGX.
    
    Args:
        pool: Database connection pool
    """
    try:
        # Create trigram extension first (may require superuser privileges)
        try:
            await pool.execute(CREATE_TRIGRAM_EXTENSION_SQL)
        except Exception:
            # If we can't create the extension, pattern matching will still work
            # but may be slower for complex patterns
            pass
        
        # Create main table
        await pool.execute(CREATE_TABLE_SQL)
        
        # Create indexes
        await pool.execute(CREATE_EXPIRES_INDEX_SQL)
        
        # Try to create pattern index (requires pg_trgm)
        try:
            await pool.execute(CREATE_KEY_PATTERN_INDEX_SQL)
        except Exception:
            # If trigram extension is not available, skip this index
            pass
        
        # Create functions and triggers
        await pool.execute(CREATE_UPDATE_TIMESTAMP_FUNCTION_SQL)
        await pool.execute(CREATE_UPDATE_TRIGGER_SQL)
        await pool.execute(CREATE_CLEANUP_FUNCTION_SQL)
        
    except Exception as e:
        raise RuntimeError(f"Failed to create schema: {e}")


async def ensure_table_exists(pool: "ConnectionPool") -> None:
    """Ensure the main table exists (lightweight check).
    
    Args:
        pool: Database connection pool
    """
    try:
        # Quick check if table exists
        result = await pool.fetchval(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'asyncpgx_store')"
        )
        
        if not result:
            await create_schema(pool)
    except Exception as e:
        raise RuntimeError(f"Failed to ensure table exists: {e}")


async def cleanup_expired_keys(pool: "ConnectionPool", batch_size: int = 1000) -> int:
    """Clean up expired keys from the database.
    
    Args:
        pool: Database connection pool
        batch_size: Number of keys to delete in one batch
        
    Returns:
        Number of deleted keys
    """
    try:
        return await pool.fetchval("SELECT cleanup_expired_keys($1)", batch_size)
    except Exception as e:
        # Fallback to direct DELETE if function doesn't exist
        return await pool.fetchval(
            "DELETE FROM asyncpgx_store WHERE expires_at IS NOT NULL AND expires_at <= NOW()"
        ) or 0