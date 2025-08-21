"""Utility for parsing arguments from various formats"""

import json
import re
import logging
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)


def parse_arguments(arguments: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Parse arguments from various formats into a dictionary.
    
    Handles:
    1. Dict objects (passthrough)
    2. JSON strings
    3. Newline-separated key=value format
    4. Simple string values (wrapped in appropriate key)
    """
    # If already a dict, return as-is
    if isinstance(arguments, dict):
        return arguments
    
    # If not a string, convert to string
    if not isinstance(arguments, str):
        arguments = str(arguments)
    
    # Try JSON first
    try:
        return json.loads(arguments)
    except json.JSONDecodeError:
        pass
    
    # Try key=value format
    if '=' in arguments and '\n' in arguments:
        return parse_key_value_format(arguments)
    
    # If single line with =, might be single key=value
    if '=' in arguments and '\n' not in arguments:
        lines = [arguments]
    else:
        lines = arguments.strip().split('\n')
    
    # Try to parse as key=value
    if any('=' in line for line in lines):
        return parse_key_value_format(arguments)
    
    # If it's just a simple string, return empty dict or wrapped value
    return {}


def parse_key_value_format(text: str) -> Dict[str, Any]:
    """Parse newline-separated key=value format."""
    result = {}
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or '=' not in line:
            continue
            
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Parse the value
        parsed_value = parse_value(value)
        result[key] = parsed_value
    
    return result


def parse_value(value: str) -> Any:
    """Parse a value string into appropriate Python type."""
    value = value.strip()
    
    # Handle None/null
    if value.lower() in ('none', 'null'):
        return None
    
    # Handle booleans
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    
    # Handle numbers
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    # Handle arrays
    if value.startswith('[') and value.endswith(']'):
        return parse_array(value)
    
    # Handle objects
    if value.startswith('{') and value.endswith('}'):
        return parse_object(value)
    
    # Default to string
    return value


def parse_array(value: str) -> list:
    """Parse array-like string into list."""
    # Remove brackets
    content = value[1:-1].strip()
    if not content:
        return []
    
    # Try JSON parsing first
    try:
        return json.loads(value)
    except:
        pass
    
    # Handle simple comma-separated values
    if not any(c in content for c in ['{', '[', ':']):
        items = [item.strip() for item in content.split(',')]
        return [parse_value(item) for item in items if item]
    
    # Handle array of objects with simplified syntax
    # e.g., [{field: created_at_month}]
    if '{' in content:
        # Convert to proper JSON
        json_str = value
        # Add quotes around keys
        json_str = re.sub(r'(\w+):', r'"\1":', json_str)
        # Add quotes around unquoted string values
        json_str = re.sub(r':\s*([a-zA-Z_]\w*)', r': "\1"', json_str)
        
        try:
            return json.loads(json_str)
        except:
            logger.warning(f"Failed to parse array: {value}")
            return []
    
    return []


def parse_object(value: str) -> dict:
    """Parse object-like string into dict."""
    try:
        # Try JSON first
        return json.loads(value)
    except:
        pass
    
    # Convert simplified object syntax to JSON
    json_str = value
    # Add quotes around keys
    json_str = re.sub(r'(\w+):', r'"\1":', json_str)
    # Add quotes around unquoted string values
    json_str = re.sub(r':\s*([a-zA-Z_]\w*)', r': "\1"', json_str)
    
    try:
        return json.loads(json_str)
    except:
        logger.warning(f"Failed to parse object: {value}")
        return {}