"""Pattern matching utilities for AsyncPGX."""

import re
from typing import List


def glob_to_sql_pattern(pattern: str) -> str:
    """Convert a glob pattern to SQL LIKE pattern.
    
    Args:
        pattern: Glob-style pattern (e.g., "user:*", "cache:?:data")
        
    Returns:
        SQL LIKE pattern
    """
    # Escape SQL special characters first
    sql_pattern = pattern.replace('%', '\\%').replace('_', '\\_')
    
    # Convert glob wildcards to SQL wildcards
    sql_pattern = sql_pattern.replace('*', '%').replace('?', '_')
    
    return sql_pattern


def glob_to_regex(pattern: str) -> str:
    """Convert a glob pattern to regex pattern for more complex matching.
    
    Args:
        pattern: Glob-style pattern
        
    Returns:
        Regex pattern string
    """
    # Escape regex special characters except * and ?
    regex_chars = r'[\\^$+{}|()[\].'
    for char in regex_chars:
        pattern = pattern.replace(char, '\\' + char)
    
    # Convert glob wildcards to regex
    pattern = pattern.replace('*', '.*').replace('?', '.')
    
    # Anchor the pattern
    return f'^{pattern}$'


def is_simple_pattern(pattern: str) -> bool:
    """Check if a pattern is simple enough for SQL LIKE.
    
    Args:
        pattern: The pattern to check
        
    Returns:
        True if pattern can use SQL LIKE efficiently
    """
    # Simple patterns are those with only * and ? wildcards
    # and no complex regex features
    return not any(char in pattern for char in r'[\^$+{}|().')


def should_use_trigram(pattern: str) -> bool:
    """Determine if trigram index should be used for pattern matching.
    
    Args:
        pattern: The pattern to check
        
    Returns:
        True if trigram index would be beneficial
    """
    # Trigram is beneficial for patterns with at least 3 consecutive characters
    # Remove wildcards and check for consecutive chars
    clean_pattern = re.sub(r'[*?]', '', pattern)
    return len(clean_pattern) >= 3


def extract_prefix(pattern: str) -> str:
    """Extract the fixed prefix from a pattern for index optimization.
    
    Args:
        pattern: The pattern to analyze
        
    Returns:
        Fixed prefix that can be used for index range scan
    """
    prefix = ''
    for char in pattern:
        if char in '*?':
            break
        prefix += char
    return prefix


def optimize_pattern_query(pattern: str) -> tuple[str, List[str]]:
    """Generate optimized SQL query for pattern matching.
    
    Args:
        pattern: The glob pattern
        
    Returns:
        Tuple of (SQL query, parameters)
    """
    if pattern == '*':
        # Match all keys
        return "SELECT key FROM asyncpgx_store WHERE expires_at IS NULL OR expires_at > NOW()", []
    
    prefix = extract_prefix(pattern)
    
    if prefix and len(prefix) > 2:
        # Use prefix optimization for better index usage
        if pattern == prefix + '*':
            # Simple prefix match - use LIKE instead of range for simplicity
            return (
                "SELECT key FROM asyncpgx_store WHERE key LIKE $1 AND (expires_at IS NULL OR expires_at > NOW())",
                [prefix + '%']
            )
    
    if is_simple_pattern(pattern):
        # Use LIKE for simple patterns
        sql_pattern = glob_to_sql_pattern(pattern)
        return (
            "SELECT key FROM asyncpgx_store WHERE key LIKE $1 AND (expires_at IS NULL OR expires_at > NOW())",
            [sql_pattern]
        )
    else:
        # Use regex for complex patterns
        regex_pattern = glob_to_regex(pattern)
        return (
            "SELECT key FROM asyncpgx_store WHERE key ~ $1 AND (expires_at IS NULL OR expires_at > NOW())",
            [regex_pattern]
        )