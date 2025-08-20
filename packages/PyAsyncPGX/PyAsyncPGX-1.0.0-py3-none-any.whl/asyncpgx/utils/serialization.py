"""Serialization utilities for AsyncPGX."""

import json
import pickle
from typing import Any, Tuple, Union

# Value type constants for efficient storage
VALUE_TYPE_STRING = 0
VALUE_TYPE_INTEGER = 1
VALUE_TYPE_FLOAT = 2
VALUE_TYPE_BOOLEAN = 3
VALUE_TYPE_JSON = 4
VALUE_TYPE_PICKLE = 5


def serialize_value(value: Any) -> Tuple[bytes, int]:
    """Serialize a value for storage in PostgreSQL.
    
    Args:
        value: The value to serialize
        
    Returns:
        Tuple of (serialized_bytes, value_type)
    """
    if isinstance(value, str):
        return value.encode('utf-8'), VALUE_TYPE_STRING
    elif isinstance(value, int):
        return str(value).encode('utf-8'), VALUE_TYPE_INTEGER
    elif isinstance(value, float):
        return str(value).encode('utf-8'), VALUE_TYPE_FLOAT
    elif isinstance(value, bool):
        return str(value).encode('utf-8'), VALUE_TYPE_BOOLEAN
    elif isinstance(value, (dict, list, tuple)):
        try:
            # Try JSON first for better interoperability
            return json.dumps(value, separators=(',', ':')).encode('utf-8'), VALUE_TYPE_JSON
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL), VALUE_TYPE_PICKLE
    else:
        # Use pickle for all other types
        return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL), VALUE_TYPE_PICKLE


def deserialize_value(data: bytes, value_type: int) -> Any:
    """Deserialize a value from PostgreSQL storage.
    
    Args:
        data: The serialized bytes
        value_type: The value type constant
        
    Returns:
        The deserialized value
    """
    if value_type == VALUE_TYPE_STRING:
        return data.decode('utf-8')
    elif value_type == VALUE_TYPE_INTEGER:
        return int(data.decode('utf-8'))
    elif value_type == VALUE_TYPE_FLOAT:
        return float(data.decode('utf-8'))
    elif value_type == VALUE_TYPE_BOOLEAN:
        return data.decode('utf-8') == 'True'
    elif value_type == VALUE_TYPE_JSON:
        return json.loads(data.decode('utf-8'))
    elif value_type == VALUE_TYPE_PICKLE:
        return pickle.loads(data)
    else:
        # Default to pickle for unknown types
        return pickle.loads(data)


def is_numeric_value(value: Any) -> bool:
    """Check if a value can be used in numeric operations.
    
    Args:
        value: The value to check
        
    Returns:
        True if the value is numeric
    """
    return isinstance(value, (int, float))


def ensure_numeric(value: Any) -> Union[int, float]:
    """Ensure a value is numeric, converting if possible.
    
    Args:
        value: The value to convert
        
    Returns:
        Numeric value
        
    Raises:
        ValueError: If value cannot be converted to numeric
    """
    if isinstance(value, (int, float)):
        return value
    elif isinstance(value, str):
        try:
            # Try integer first
            if '.' not in value:
                return int(value)
            else:
                return float(value)
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to numeric")
    else:
        raise ValueError(f"Cannot convert {type(value).__name__} to numeric")