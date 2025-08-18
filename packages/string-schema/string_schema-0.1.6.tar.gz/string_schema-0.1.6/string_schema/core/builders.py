"""
Schema builders for Simple Schema

Contains functions for building schemas from SimpleField definitions.
"""

from typing import Any, Dict, List, Optional, Union, Type
import logging

from .fields import SimpleField

# Optional pydantic import
try:
    from pydantic import BaseModel, Field, create_model
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = None
    Field = None
    create_model = None

logger = logging.getLogger(__name__)


def simple_schema(fields: Dict[str, Union[str, SimpleField]]) -> Dict[str, Any]:
    """Generate JSON Schema from simple field definitions with enhanced support"""
    properties = {}
    required = []
    
    for field_name, field_def in fields.items():
        if isinstance(field_def, str):
            field_def = SimpleField(field_def)
        
        prop_schema = _simple_field_to_json_schema(field_def)
        properties[field_name] = prop_schema
        
        if field_def.required:
            required.append(field_name)
    
    schema = {
        "type": "object",
        "properties": properties
    }
    if required:
        schema["required"] = required
    
    return schema


def _simple_field_to_json_schema(field: SimpleField) -> Dict[str, Any]:
    """Convert SimpleField to JSON Schema property with enhanced features"""
    # Handle union types first
    if field.union_types and len(field.union_types) > 1:
        union_schemas = []
        for union_type in field.union_types:
            if union_type == "null":
                union_schemas.append({"type": "null"})
            else:
                union_schemas.append({"type": union_type})
        prop = {"anyOf": union_schemas}
        
        # Add description to the union
        if field.description:
            prop["description"] = field.description
        
        return prop
    
    # Regular single type
    prop = {"type": field.field_type}
    
    if field.description:
        prop["description"] = field.description
    if field.default is not None:
        prop["default"] = field.default
    
    # Handle enum/choices
    if field.choices:
        prop["enum"] = field.choices
    
    # Add format hints for special types
    if field.format_hint:
        if field.format_hint == "email":
            prop["format"] = "email"
        elif field.format_hint in ["url", "uri"]:
            prop["format"] = "uri"
        elif field.format_hint == "datetime":
            prop["format"] = "date-time"
        elif field.format_hint == "date":
            prop["format"] = "date"
        elif field.format_hint == "uuid":
            prop["format"] = "uuid"
        # Note: phone doesn't have a standard JSON Schema format
    
    # Numeric constraints
    if field.field_type in ["integer", "number"]:
        if field.min_val is not None:
            prop["minimum"] = field.min_val
        if field.max_val is not None:
            prop["maximum"] = field.max_val
    
    # String constraints
    if field.field_type == "string":
        if field.min_length is not None:
            prop["minLength"] = field.min_length
        if field.max_length is not None:
            prop["maxLength"] = field.max_length
    
    # Array constraints (for when this field itself is an array)
    if field.min_items is not None:
        prop["minItems"] = field.min_items
    if field.max_items is not None:
        prop["maxItems"] = field.max_items
    
    return prop


def list_of_objects_schema(item_fields: Dict[str, Union[str, SimpleField]],
                          description: str = "List of objects",
                          min_items: Optional[int] = None,
                          max_items: Optional[int] = None) -> Dict[str, Any]:
    """Generate schema for array of objects with enhanced constraints"""
    item_schema = simple_schema(item_fields)
    
    array_schema = {
        "type": "array",
        "description": description,
        "items": item_schema
    }
    
    # Add array size constraints
    if min_items is not None:
        array_schema["minItems"] = min_items
    if max_items is not None:
        array_schema["maxItems"] = max_items
    
    return array_schema


def simple_array_schema(item_type: str = 'string', description: str = 'Array of items',
                       min_items: Optional[int] = None, max_items: Optional[int] = None,
                       format_hint: Optional[str] = None) -> Dict[str, Any]:
    """Generate schema for simple arrays like [string], [int], [email]"""
    items_schema = {"type": item_type}
    
    # Add format for special types
    if format_hint:
        if format_hint == "email":
            items_schema["format"] = "email"
        elif format_hint in ["url", "uri"]:
            items_schema["format"] = "uri"
        elif format_hint == "datetime":
            items_schema["format"] = "date-time"
        elif format_hint == "date":
            items_schema["format"] = "date"
        elif format_hint == "uuid":
            items_schema["format"] = "uuid"
    
    array_schema = {
        "type": "array",
        "description": description,
        "items": items_schema
    }
    
    # Add array size constraints
    if min_items is not None:
        array_schema["minItems"] = min_items
    if max_items is not None:
        array_schema["maxItems"] = max_items
    
    return array_schema


def quick_pydantic_model(name: str, fields: Dict[str, Union[str, SimpleField]]) -> Type:
    """Create Pydantic model from simple field definitions"""
    if not HAS_PYDANTIC:
        raise ImportError("Pydantic is required for quick_pydantic_model. Install with: pip install pydantic")

    pydantic_fields = {}

    for field_name, field_def in fields.items():
        if isinstance(field_def, str):
            field_def = SimpleField(field_def)

        from ..integrations.pydantic import _simple_field_to_pydantic
        python_type, field_info = _simple_field_to_pydantic(field_def)
        pydantic_fields[field_name] = (python_type, field_info)

    return create_model(name, **pydantic_fields)


def _simple_field_to_pydantic(field: SimpleField) -> tuple:
    """Convert SimpleField to Pydantic field specification"""
    if not HAS_PYDANTIC:
        raise ImportError("Pydantic is required for this function")

    # Type mapping
    type_mapping = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool
    }

    python_type = type_mapping.get(field.field_type, str)

    # Handle union types
    if field.union_types and len(field.union_types) > 1:
        from typing import Union as TypingUnion
        union_python_types = []
        for union_type in field.union_types:
            if union_type == "null":
                union_python_types.append(type(None))
            else:
                union_python_types.append(type_mapping.get(union_type, str))
        python_type = TypingUnion[tuple(union_python_types)]

    # Handle optional fields
    if not field.required:
        python_type = Optional[python_type]

    # Build Field arguments
    field_kwargs = {}

    if field.description:
        field_kwargs['description'] = field.description

    if field.default is not None:
        field_kwargs['default'] = field.default
    elif not field.required:
        field_kwargs['default'] = None

    # Numeric constraints
    if field.min_val is not None:
        field_kwargs['ge'] = field.min_val
    if field.max_val is not None:
        field_kwargs['le'] = field.max_val

    # String constraints
    if field.min_length is not None:
        field_kwargs['min_length'] = field.min_length
    if field.max_length is not None:
        field_kwargs['max_length'] = field.max_length

    return python_type, Field(**field_kwargs) if field_kwargs else Field()
