# AsyncPGX

**High-performance asynchronous PostgreSQL wrapper with Redis-like API**

AsyncPGX is a Python library that provides a Redis-like interface for PostgreSQL, built on top of `asyncpg` for maximum performance. It offers familiar key-value operations while leveraging PostgreSQL's reliability and ACID properties.

## Features

- 🚀 **High Performance**: Built on `asyncpg` with minimal overhead
- 🔄 **Fully Async**: Native `asyncio` support with connection pooling
- 🎯 **Redis-like API**: Familiar interface for easy adoption
- ⏰ **TTL Support**: Automatic key expiration with background cleanup
- 🔢 **Atomic Operations**: Thread-safe increment/decrement operations
- 🔍 **Pattern Matching**: Glob-style key pattern matching
- 📊 **Multiple Data Types**: Support for strings, numbers, JSON, and Python objects
- 🛡️ **Production Ready**: Comprehensive error handling and connection management

## Installation

```bash
pip install asyncpgx
```

### Requirements

- Python 3.8+
- PostgreSQL 10+
- asyncpg 0.29.0+

## Quick Start

```python
import asyncio
from asyncpgx import AsyncPostgresClient

async def main():
    # Connect to PostgreSQL
    db = AsyncPostgresClient("postgresql://user:password@localhost:5432/dbname")
    
    # Basic operations
    await db.set("user:1", {"name": "Alice", "age": 30})
    user = await db.get("user:1")
    print(user)  # {'name': 'Alice', 'age': 30}
    
    # TTL operations
    await db.set("session:abc", "session_data", expire=3600)  # 1 hour TTL
    ttl = await db.ttl("session:abc")
    print(f"Session expires in {ttl} seconds")
    
    # Atomic operations
    await db.incr("page_views", 1)
    views = await db.get("page_views")
    print(f"Page views: {views}")
    
    # Pattern matching
    await db.set("user:1:profile", "profile_data")
    await db.set("user:2:profile", "profile_data")
    user_keys = await db.keys("user:*:profile")
    print(user_keys)  # ['user:1:profile', 'user:2:profile']
    
    # Cleanup
    await db.disconnect()

asyncio.run(main())
```

## API Reference

### Connection

```python
db = AsyncPostgresClient(
    url="postgresql://user:password@host:port/database",
    min_connections=5,      # Minimum connections in pool
    max_connections=20,     # Maximum connections in pool
    command_timeout=60.0,   # Command timeout in seconds
    auto_cleanup=True,      # Enable automatic TTL cleanup
    cleanup_interval=300    # Cleanup interval in seconds
)

# Manual connection management
await db.connect()
await db.disconnect()

# Or use context manager (recommended)
async with AsyncPostgresClient(url) as db:
    await db.set("key", "value")
```

### Core Operations

#### `set(key, value, expire=None)`
Store a key-value pair with optional TTL.

```python
# Basic set
await db.set("name", "Alice")

# With TTL (expires in 60 seconds)
await db.set("temp_key", "temp_value", expire=60)

# Different data types
await db.set("user", {"id": 1, "name": "Alice"})
await db.set("numbers", [1, 2, 3, 4, 5])
await db.set("flag", True)
```

#### `get(key)`
Retrieve a value by key.

```python
value = await db.get("name")  # Returns "Alice" or None
user = await db.get("user")   # Returns dict or None
```

#### `delete(*keys)`
Delete one or more keys.

```python
# Delete single key
deleted = await db.delete("name")  # Returns 1 if deleted, 0 if not found

# Delete multiple keys
deleted = await db.delete("key1", "key2", "key3")  # Returns count of deleted keys
```

#### `exists(key)`
Check if a key exists.

```python
if await db.exists("user:1"):
    print("User exists")
```

#### `keys(pattern="*")`
List keys matching a glob pattern.

```python
all_keys = await db.keys()              # All keys
user_keys = await db.keys("user:*")     # Keys starting with "user:"
profiles = await db.keys("*:profile")   # Keys ending with ":profile"
sessions = await db.keys("session:??")  # Sessions with 2-char IDs
```

### TTL Operations

#### `expire(key, seconds)`
Set TTL on an existing key.

```python
# Set 1 hour TTL
success = await db.expire("user:1", 3600)
```

#### `ttl(key)`
Get remaining TTL for a key.

```python
ttl = await db.ttl("user:1")
# Returns: remaining seconds, -1 if no TTL, -2 if key doesn't exist
```

### Numeric Operations

#### `incr(key, amount=1)`
Increment a numeric value.

```python
# Increment by 1 (default)
new_value = await db.incr("counter")

# Increment by custom amount
new_value = await db.incr("score", 10)

# Works with string numbers too
await db.set("string_num", "42")
result = await db.incr("string_num", 8)  # Returns 50
```

#### `decr(key, amount=1)`
Decrement a numeric value.

```python
new_value = await db.decr("lives")      # Decrement by 1
new_value = await db.decr("score", 5)   # Decrement by 5
```

### Utility Operations

#### `flushall()`
Remove all keys from storage.

```python
success = await db.flushall()  # Returns True if successful
```

## Data Types

AsyncPGX automatically handles serialization for various Python data types:

- **Strings**: Stored as UTF-8 text
- **Integers**: Stored efficiently as text
- **Floats**: Stored with full precision
- **Booleans**: Stored as "True"/"False"
- **Lists/Tuples**: JSON serialization
- **Dictionaries**: JSON serialization
- **Other Objects**: Pickle serialization (fallback)

## Performance

AsyncPGX is designed for high performance:

- **Connection Pooling**: Efficient connection reuse
- **Optimized Queries**: Minimal SQL overhead
- **Batch Operations**: Support for concurrent operations
- **Efficient Serialization**: Type-aware serialization
- **Index Optimization**: Automatic indexing for TTL and pattern matching

### Benchmarks

Typical performance on modern hardware:

- **SET operations**: 10,000+ ops/sec
- **GET operations**: 15,000+ ops/sec
- **Pattern matching**: Optimized with PostgreSQL indexes
- **TTL cleanup**: Background processing with minimal impact

## Error Handling

```python
try:
    await db.set("key", "value")
except ConnectionError:
    print("Database connection failed")
except ValueError as e:
    print(f"Invalid operation: {e}")
```

Common exceptions:
- `ConnectionError`: Database connection issues
- `ValueError`: Invalid data types or operations
- `RuntimeError`: Schema or configuration errors

## Advanced Usage

### Custom Connection Settings

```python
db = AsyncPostgresClient(
    url="postgresql://user:password@host:port/database",
    min_connections=10,
    max_connections=100,
    command_timeout=30.0,
    auto_cleanup=True,
    cleanup_interval=60  # Clean expired keys every minute
)
```

### Concurrent Operations

```python
# Concurrent writes
tasks = [
    db.set(f"key:{i}", f"value:{i}")
    for i in range(100)
]
await asyncio.gather(*tasks)

# Concurrent reads
tasks = [
    db.get(f"key:{i}")
    for i in range(100)
]
results = await asyncio.gather(*tasks)
```

### Context Manager Usage

```python
# Automatic connection management
async with AsyncPostgresClient(url) as db:
    await db.set("key", "value")
    value = await db.get("key")
# Connection automatically closed
```

## Examples

See the `examples/` directory for complete usage examples:

- `basic_usage.py`: Basic operations and data types
- `advanced_usage.py`: Concurrent operations, error handling, and TTL

## Requirements

Create a PostgreSQL database and ensure the connection URL is correct:

```sql
CREATE DATABASE asyncpgx_test;
```

The library will automatically create the required tables and indexes.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## Support

For issues and questions:
- GitHub Issues: [Report bugs](https://github.com/asyncpgx/asyncpgx/issues)
- Documentation: [Read the docs](https://asyncpgx.readthedocs.io/)