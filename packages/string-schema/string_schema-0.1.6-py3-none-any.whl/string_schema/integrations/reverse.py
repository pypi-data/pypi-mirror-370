"""
Reverse conversion functions for String Schema

This module provides functions to convert from various schema formats back to
String Schema string syntax, completing the conversion matrix.

Conversion Matrix:
- model_to_string()         # Pydantic model → String syntax
- model_to_json_schema()    # Pydantic model → JSON Schema  
- json_schema_to_string()   # JSON Schema → String syntax
- openapi_to_string()       # OpenAPI schema → String syntax
- openapi_to_json_schema()  # OpenAPI schema → JSON Schema

Note: Some information loss is expected and acceptable when converting
from more complex formats to simpler string syntax.
"""

from typing import Any, Dict, List, Union, Optional, Type
import logging

# Optional pydantic import
try:
    from pydantic import BaseModel
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = None

logger = logging.getLogger(__name__)


def model_to_string(model: Type[BaseModel], include_name: bool = False) -> str:
    """
    Convert Pydantic model to String Schema string syntax.

    Args:
        model: Pydantic model class
        include_name: Whether to include model name in output

    Returns:
        String representation in String Schema syntax

    Example:
        UserModel = create_model("name:string, email:email, age:int?")
        schema_str = model_to_string(UserModel)
        # Returns: "name:string, email:email, age:int?"
    """
    if not HAS_PYDANTIC:
        raise ImportError("Pydantic is required for model_to_string. Install with: pip install pydantic")
    
    # First convert to JSON Schema, then to string
    json_schema = model_to_json_schema(model)
    return json_schema_to_string(json_schema)


def model_to_json_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert Pydantic model to JSON Schema.
    
    Args:
        model: Pydantic model class
        
    Returns:
        JSON Schema dictionary
        
    Example:
        UserModel = create_model("name:string, email:email")
        json_schema = model_to_json_schema(UserModel)
    """
    if not HAS_PYDANTIC:
        raise ImportError("Pydantic is required for model_to_json_schema. Install with: pip install pydantic")
    
    try:
        # Use Pydantic's built-in JSON Schema generation
        if hasattr(model, 'model_json_schema'):
            # Pydantic v2
            return model.model_json_schema()
        elif hasattr(model, 'schema'):
            # Pydantic v1
            return model.schema()
        else:
            raise ValueError(f"Unable to extract JSON Schema from model {model}")
    except Exception as e:
        raise ValueError(f"Failed to convert model to JSON Schema: {str(e)}") from e


def json_schema_to_string(json_schema: Dict[str, Any]) -> str:
    """
    Convert JSON Schema to String Schema string syntax.

    Args:
        json_schema: JSON Schema dictionary

    Returns:
        String representation in String Schema syntax

    Example:
        json_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        schema_str = json_schema_to_string(json_schema)
        # Returns: "name:string"
    """
    if json_schema.get('type') == 'array':
        return _convert_array_schema_to_string(json_schema)
    elif json_schema.get('type') == 'object':
        return _convert_object_schema_to_string(json_schema)
    else:
        # Single field schema
        return _convert_field_schema_to_string('field', json_schema)


def openapi_to_string(openapi_schema: Dict[str, Any]) -> str:
    """
    Convert OpenAPI schema to String Schema string syntax.

    Args:
        openapi_schema: OpenAPI schema dictionary

    Returns:
        String representation in String Schema syntax

    Example:
        openapi_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        schema_str = openapi_to_string(openapi_schema)
        # Returns: "name:string"
    """
    # OpenAPI schemas are very similar to JSON Schema
    # First convert to JSON Schema format, then to string
    json_schema = openapi_to_json_schema(openapi_schema)
    return json_schema_to_string(json_schema)


def openapi_to_json_schema(openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert OpenAPI schema to JSON Schema.
    
    Args:
        openapi_schema: OpenAPI schema dictionary
        
    Returns:
        JSON Schema dictionary
        
    Example:
        openapi_schema = {"type": "string", "format": "email"}
        json_schema = openapi_to_json_schema(openapi_schema)
    """
    # OpenAPI 3.0 schemas are mostly compatible with JSON Schema
    # Just need to handle some OpenAPI-specific keywords
    json_schema = openapi_schema.copy()
    
    # Remove OpenAPI-specific keywords that aren't in JSON Schema
    openapi_only_keywords = [
        'example', 'examples', 'discriminator', 'xml', 'externalDocs'
    ]
    
    for keyword in openapi_only_keywords:
        json_schema.pop(keyword, None)
    
    # Handle nested properties recursively
    if 'properties' in json_schema:
        for prop_name, prop_schema in json_schema['properties'].items():
            json_schema['properties'][prop_name] = openapi_to_json_schema(prop_schema)
    
    # Handle array items
    if 'items' in json_schema:
        json_schema['items'] = openapi_to_json_schema(json_schema['items'])
    
    return json_schema


# Helper functions for JSON Schema to string conversion

def _convert_object_schema_to_string(json_schema: Dict[str, Any]) -> str:
    """Convert object-type JSON Schema to string syntax."""
    properties = json_schema.get('properties', {})
    required_fields = set(json_schema.get('required', []))
    
    if not properties:
        return "{}"
    
    field_strings = []
    for field_name, field_schema in properties.items():
        field_str = _convert_field_schema_to_string(field_name, field_schema)
        if field_name not in required_fields:
            field_str += "?"
        field_strings.append(field_str)
    
    # Check if this should be wrapped in braces (nested object)
    if len(field_strings) > 1 or any(':' in fs for fs in field_strings):
        return "{" + ", ".join(field_strings) + "}"
    else:
        return ", ".join(field_strings)


def _convert_array_schema_to_string(json_schema: Dict[str, Any]) -> str:
    """Convert array-type JSON Schema to string syntax."""
    items_schema = json_schema.get('items', {})
    
    if items_schema.get('type') == 'object':
        # Array of objects
        object_str = _convert_object_schema_to_string(items_schema)
        return f"[{object_str}]"
    else:
        # Array of primitives
        item_type = _get_simple_type_from_json_schema(items_schema)
        return f"[{item_type}]"


def _convert_field_schema_to_string(field_name: str, field_schema: Dict[str, Any]) -> str:
    """Convert a single field's JSON Schema to string syntax."""
    field_type = _get_simple_type_from_json_schema(field_schema)
    constraints = _extract_constraints_from_json_schema(field_schema)
    
    if constraints:
        constraint_str = ",".join(f"{k}={v}" for k, v in constraints.items())
        return f"{field_name}:{field_type}({constraint_str})"
    else:
        return f"{field_name}:{field_type}"


def _get_simple_type_from_json_schema(field_schema: Dict[str, Any]) -> str:
    """Extract simple type from JSON Schema field."""
    json_type = field_schema.get('type', 'string')
    format_hint = field_schema.get('format')
    
    # Handle special formats
    if format_hint:
        format_mapping = {
            'email': 'email',
            'uri': 'url', 
            'url': 'url',
            'date-time': 'datetime',
            'date': 'date',
            'uuid': 'uuid',
            'phone': 'phone'
        }
        if format_hint in format_mapping:
            return format_mapping[format_hint]
    
    # Handle enums
    if 'enum' in field_schema:
        enum_values = field_schema['enum']
        return f"enum({','.join(str(v) for v in enum_values)})"
    
    # Handle basic types
    type_mapping = {
        'string': 'string',
        'integer': 'int',
        'number': 'number',
        'boolean': 'bool'
    }
    
    return type_mapping.get(json_type, 'string')


def _extract_constraints_from_json_schema(field_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Extract constraints from JSON Schema field."""
    constraints = {}
    
    # String constraints
    if 'minLength' in field_schema:
        constraints['min'] = field_schema['minLength']
    if 'maxLength' in field_schema:
        constraints['max'] = field_schema['maxLength']
    
    # Number constraints  
    if 'minimum' in field_schema:
        constraints['min'] = field_schema['minimum']
    if 'maximum' in field_schema:
        constraints['max'] = field_schema['maximum']
    
    # Pattern constraint
    if 'pattern' in field_schema:
        constraints['pattern'] = f"'{field_schema['pattern']}'"
    
    return constraints
