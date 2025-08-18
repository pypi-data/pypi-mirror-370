"""
String-based schema parsing for String Schema

Contains functionality for parsing human-readable schema strings into JSON Schema.
"""

import re
from typing import Dict, Any, List, Union, Optional
import logging

from ..core.fields import SimpleField
from ..core.builders import simple_schema, list_of_objects_schema

logger = logging.getLogger(__name__)


def parse_string_schema(schema_str: str, is_list: bool = False) -> Dict[str, Any]:
    """Parse enhanced string schema with support for arrays, enums, unions, and special types"""
    schema_str = schema_str.strip()
    parsed_structure = _parse_schema_structure(schema_str)
    return _structure_to_json_schema(parsed_structure)


def _parse_schema_structure(schema_str: str) -> Dict[str, Any]:
    """Parse the overall structure of the schema with enhanced syntax support"""
    schema_str = schema_str.strip()
    
    # Handle curly brace syntax: {field1, field2}
    if schema_str.startswith('{') and schema_str.endswith('}'):
        inner_content = schema_str[1:-1].strip()
        fields = _parse_object_fields(inner_content)
        return {
            "type": "object",
            "fields": fields
        }
    
    # Handle array syntax: [type] or [{field1, field2}] with optional constraints
    elif schema_str.startswith('['):
        # Check for array constraints like [string](max=5)
        array_constraints = {}

        # Extract constraints if present: [type](constraints)
        constraint_match = re.match(r'^\[([^\]]+)\]\(([^)]+)\)$', schema_str)
        if constraint_match:
            inner_content = constraint_match.group(1).strip()
            constraint_str = constraint_match.group(2).strip()
            array_constraints = _parse_array_constraints(constraint_str)
        elif schema_str.endswith(']'):
            # Simple array without constraints
            inner_content = schema_str[1:-1].strip()
        else:
            # Malformed array syntax
            return {"type": "object", "fields": {}}  # Fallback
        
        # Array of objects: [{field1, field2}]
        if inner_content.startswith('{') and inner_content.endswith('}'):
            object_fields = _parse_object_fields(inner_content[1:-1].strip())
            return {
                "type": "array",
                "items": {
                    "type": "object",
                    "fields": object_fields
                },
                "constraints": array_constraints
            }
        
        # Array of simple types: [string], [int], [email], etc.
        elif _is_simple_type(inner_content):
            original_type = inner_content.strip().lower()
            normalized_type = _normalize_type_name(original_type)
            return {
                "type": "array",
                "items": {
                    "type": "simple",
                    "simple_type": normalized_type,
                    "original_type": original_type  # Keep original for format hints
                },
                "constraints": array_constraints
            }
        
        # Array of complex fields: [name:string, age:int]
        else:
            fields = _parse_object_fields(inner_content)
            return {
                "type": "array",
                "items": {
                    "type": "object",
                    "fields": fields
                },
                "constraints": array_constraints
            }
    
    # Simple object fields: name, age:int, email
    else:
        fields = _parse_object_fields(schema_str)
        return {
            "type": "object",
            "fields": fields
        }


def _parse_array_constraints(constraint_str: str) -> Dict[str, Any]:
    """Parse array constraints like 'min=1,max=5'"""
    constraints = {}
    parts = [part.strip() for part in constraint_str.split(',')]
    
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            try:
                if key in ['min', 'max']:
                    constraints[key] = int(value)
                else:
                    constraints[key] = value
            except ValueError:
                logger.warning(f"Invalid array constraint: {part}")
    
    return constraints


def _parse_object_fields(fields_str: str) -> Dict[str, Any]:
    """Parse object fields with enhanced syntax"""
    fields_str = _normalize_string_schema(fields_str)
    field_parts = _split_field_definitions_with_nesting(fields_str)
    
    fields = {}
    for field_part in field_parts:
        field_name, field_def = _parse_single_field_with_nesting(field_part.strip())
        if field_name:
            fields[field_name] = field_def
    
    return fields


def _parse_single_field_with_nesting(field_str: str) -> tuple:
    """Parse a single field with enhanced syntax support"""
    if not field_str:
        return None, None
    
    # Check for optional marker
    required = True
    if field_str.endswith('?'):
        required = False
        field_str = field_str[:-1].strip()
    
    # Split field name and definition
    if ':' in field_str:
        field_name, field_def = field_str.split(':', 1)
        field_name = field_name.strip()
        field_def = field_def.strip()
        
        # Handle nested structures
        if field_def.startswith('[') or field_def.startswith('{'):
            nested_structure = _parse_schema_structure(field_def)
            nested_structure['required'] = required
            return field_name, nested_structure
        
        # Handle union types: string|int|null
        elif '|' in field_def:
            union_types = [t.strip() for t in field_def.split('|')]
            field_type = _normalize_type_name(union_types[0])  # Use first type as primary
            
            # Create field with union support
            field_obj = SimpleField(
                field_type=field_type,
                required=required
            )
            # Store union info for JSON schema generation
            field_obj.union_types = [_normalize_type_name(t) for t in union_types]
            return field_name, field_obj
        
        # Handle enum types: enum(value1,value2,value3) or choice(...)
        elif field_def.startswith(('enum(', 'choice(', 'select(')):
            enum_values = _parse_enum_values(field_def)
            field_obj = SimpleField(
                field_type="string",  # Enums are string-based
                required=required,
                choices=enum_values
            )
            return field_name, field_obj
        
        # Handle array types: array(string,max=5) or list(int,min=1)
        elif field_def.startswith(('array(', 'list(')):
            array_type, constraints = _parse_array_type_definition(field_def)
            # Return as nested array structure
            return field_name, {
                "type": "array",
                "items": {
                    "type": "simple",
                    "simple_type": array_type
                },
                "constraints": constraints,
                "required": required
            }
        
        # Handle regular type with constraints
        else:
            original_type = field_def.split('(')[0].strip()  # Get type before any constraints
            field_type, constraints = _parse_type_definition(field_def)

            # Add format hint for special types
            if original_type in ['email', 'url', 'uri', 'datetime', 'date', 'uuid', 'phone']:
                constraints['format_hint'] = original_type
                field_type = 'string'  # All special types are strings with format hints

            field_obj = SimpleField(
                field_type=field_type,
                required=required,
                **constraints
            )
            return field_name, field_obj
    
    # Field name only (default to string)
    else:
        field_name = field_str.strip()
        field_obj = SimpleField(
            field_type="string",
            required=required
        )
        return field_name, field_obj


def _parse_enum_values(enum_def: str) -> List[str]:
    """Parse enum values from enum(value1,value2,value3)"""
    # Extract content between parentheses
    match = re.match(r'^(?:enum|choice|select)\(([^)]+)\)$', enum_def)
    if not match:
        return []
    
    values_str = match.group(1)
    values = [v.strip() for v in values_str.split(',')]
    return values


def _parse_array_type_definition(array_def: str) -> tuple:
    """Parse array(type,constraints) or list(type,constraints)"""
    # Extract content between parentheses
    match = re.match(r'^(?:array|list)\(([^)]+)\)$', array_def)
    if not match:
        return "string", {}
    
    content = match.group(1)
    parts = [p.strip() for p in content.split(',')]
    
    # First part is the type
    array_type = _normalize_type_name(parts[0]) if parts else "string"
    
    # Remaining parts are constraints
    constraints = {}
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            try:
                if key in ['min', 'max']:
                    constraints[key] = int(value)
                else:
                    constraints[key] = value
            except ValueError:
                logger.warning(f"Invalid array constraint: {part}")
    
    return array_type, constraints


def _is_simple_type(type_str: str) -> bool:
    """Check if string represents a simple type"""
    simple_types = [
        'string', 'str', 'text', 'int', 'integer', 'number', 'float', 'decimal',
        'bool', 'boolean', 'email', 'url', 'uri', 'datetime', 'date', 'uuid', 'phone'
    ]
    return type_str.strip().lower() in simple_types


def _structure_to_json_schema(structure: Dict[str, Any]) -> Dict[str, Any]:
    """Convert parsed structure to JSON Schema"""
    if structure["type"] == "object":
        return _object_structure_to_schema(structure)
    elif structure["type"] == "array":
        return _array_structure_to_schema(structure)
    else:
        raise ValueError(f"Unknown structure type: {structure['type']}")


def _object_structure_to_schema(structure: Dict[str, Any]) -> Dict[str, Any]:
    """Convert object structure to JSON Schema"""
    properties = {}
    required = []

    for field_name, field_def in structure["fields"].items():
        if isinstance(field_def, SimpleField):
            prop_schema = _simple_field_to_json_schema(field_def)
            properties[field_name] = prop_schema
            if field_def.required:
                required.append(field_name)
        else:
            # Nested structure
            prop_schema = _structure_to_json_schema(field_def)
            properties[field_name] = prop_schema
            if field_def.get('required', True):
                required.append(field_name)

    schema = {
        "type": "object",
        "properties": properties
    }
    if required:
        schema["required"] = required

    return schema


def _array_structure_to_schema(structure: Dict[str, Any]) -> Dict[str, Any]:
    """Convert array structure to JSON Schema"""
    items_structure = structure["items"]
    constraints = structure.get("constraints", {})

    # Simple array: [string], [int], etc.
    if items_structure["type"] == "simple":
        simple_type = items_structure["simple_type"]
        original_type = items_structure.get("original_type", simple_type)
        items_schema = {"type": simple_type}

        # Add format for special types
        if simple_type == "string" and original_type in ['email', 'url', 'uri', 'datetime', 'date', 'uuid']:
            if original_type == "email":
                items_schema["format"] = "email"
            elif original_type in ["url", "uri"]:
                items_schema["format"] = "uri"
            elif original_type == "datetime":
                items_schema["format"] = "date-time"
            elif original_type == "date":
                items_schema["format"] = "date"
            elif original_type == "uuid":
                items_schema["format"] = "uuid"

    else:
        # Complex array: [{field1, field2}]
        items_schema = _structure_to_json_schema(items_structure)

    array_schema = {
        "type": "array",
        "items": items_schema
    }

    # Add array constraints
    if "min" in constraints:
        array_schema["minItems"] = constraints["min"]
    if "max" in constraints:
        array_schema["maxItems"] = constraints["max"]

    return array_schema


def _simple_field_to_json_schema(field: SimpleField) -> Dict[str, Any]:
    """Convert SimpleField to JSON Schema property with enhanced features"""
    prop = {"type": field.field_type}

    # Basic metadata
    if field.description:
        prop["description"] = field.description
    if field.default is not None:
        prop["default"] = field.default

    # Handle union types
    if hasattr(field, 'union_types') and field.union_types and len(field.union_types) > 1:
        # Create anyOf for union types
        union_schemas = []
        for union_type in field.union_types:
            if union_type == "null":
                union_schemas.append({"type": "null"})
            else:
                union_schemas.append({"type": union_type})
        prop = {"anyOf": union_schemas}

    # Handle enum/choices
    if field.choices:
        prop["enum"] = field.choices

    # Add format hints for special types
    if hasattr(field, 'format_hint') and field.format_hint:
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

    return prop


def _split_field_definitions_with_nesting(schema_str: str) -> List[str]:
    """Split field definitions while respecting nesting"""
    parts = []
    current_part = ""
    bracket_depth = 0
    brace_depth = 0
    paren_depth = 0

    for char in schema_str:
        if char == '[':
            bracket_depth += 1
        elif char == ']':
            bracket_depth -= 1
        elif char == '{':
            brace_depth += 1
        elif char == '}':
            brace_depth -= 1
        elif char == '(':
            paren_depth += 1
        elif char == ')':
            paren_depth -= 1
        elif char == ',' and bracket_depth == 0 and brace_depth == 0 and paren_depth == 0:
            if current_part.strip():
                parts.append(current_part.strip())
            current_part = ""
            continue

        current_part += char

    if current_part.strip():
        parts.append(current_part.strip())

    return parts


def _normalize_string_schema(schema_str: str) -> str:
    """Normalize string schema by removing comments and extra whitespace"""
    # Remove triple quotes
    schema_str = re.sub(r'^[\'\"]{3}|[\'\"]{3}$', '', schema_str.strip())

    # Process line by line
    lines = schema_str.split('\n')
    normalized_parts = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Remove inline comments
        if ' #' in line:
            line = line.split(' #')[0].strip()
        elif '#' in line and not line.startswith('#'):
            line = line.split('#')[0].strip()

        normalized_parts.append(line)

    # Join with commas and clean up
    result = ', '.join(part.rstrip(',') for part in normalized_parts)
    return result


def _parse_type_definition(type_def: str) -> tuple:
    """Parse enhanced type definitions with constraints"""
    constraints = {}

    # Handle constraints in parentheses: type(min=1,max=10)
    constraint_match = re.match(r'^(\w+)\(([^)]+)\)$', type_def)
    if constraint_match:
        base_type = constraint_match.group(1)
        constraint_str = constraint_match.group(2)

        # Parse constraints
        constraint_parts = [part.strip() for part in constraint_str.split(',')]

        # Handle positional constraints like int(0,120) -> min=0, max=120
        if len(constraint_parts) == 2 and all('=' not in part for part in constraint_parts):
            try:
                min_val = float(constraint_parts[0]) if '.' in constraint_parts[0] else int(constraint_parts[0])
                max_val = float(constraint_parts[1]) if '.' in constraint_parts[1] else int(constraint_parts[1])

                if base_type in ['string', 'str', 'text']:
                    constraints['min_length'] = min_val
                    constraints['max_length'] = max_val
                else:
                    constraints['min_val'] = min_val
                    constraints['max_val'] = max_val
            except ValueError as e:
                logger.warning(f"Invalid positional constraints '{constraint_str}': {e}")
        else:
            # Handle named constraints like string(min=1,max=100)
            for part in constraint_parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    try:
                        if key in ['min', 'max']:
                            if base_type in ['string', 'str', 'text']:
                                constraints[f'{key}_length'] = int(value)
                            else:
                                constraints[f'{key}_val'] = float(value) if '.' in value else int(value)
                        else:
                            constraints[key] = value
                    except ValueError as e:
                        logger.warning(f"Invalid constraint '{part}': {e}")
                else:
                    # Single value constraint (treat as max)
                    try:
                        if base_type in ['string', 'str', 'text']:
                            constraints['max_length'] = int(part)
                        else:
                            constraints['max_val'] = float(part) if '.' in part else int(part)
                    except ValueError as e:
                        logger.warning(f"Invalid constraint value '{part}': {e}")
    else:
        base_type = type_def

    # Normalize type name
    normalized_type = _normalize_type_name(base_type)

    return normalized_type, constraints


def _normalize_type_name(type_name: str) -> str:
    """Normalize type names with enhanced support"""
    type_mapping = {
        # Basic types
        'str': 'string',
        'string': 'string',
        'text': 'string',
        'int': 'integer',
        'integer': 'integer',
        'num': 'number',
        'number': 'number',
        'float': 'number',
        'double': 'number',
        'decimal': 'number',
        'bool': 'boolean',
        'boolean': 'boolean',

        # Special types (normalized to string, format handled separately)
        'email': 'string',
        'url': 'string',
        'uri': 'string',
        'datetime': 'string',
        'date': 'string',
        'uuid': 'string',
        'phone': 'string',
        'tel': 'string',
        'null': 'null',
    }

    return type_mapping.get(type_name.lower(), 'string')


# Clear function name aliases
def string_to_json_schema(schema_str: str) -> Dict[str, Any]:
    """
    Convert string syntax to JSON Schema dictionary.

    Args:
        schema_str: String schema definition (e.g., "name:string, email:email")

    Returns:
        JSON Schema dictionary

    Example:
        schema = string_to_json_schema("name:string, email:email")
    """
    return parse_string_schema(schema_str)


def validate_string_syntax(schema_str: str) -> Dict[str, Any]:
    """
    Validate string schema syntax and return detailed feedback.

    Args:
        schema_str: String schema definition to validate

    Returns:
        Dictionary with validation results: valid, errors, warnings, features_used, etc.

    Example:
        result = validate_string_syntax("name:string, email:email")
        print(f"Valid: {result['valid']}")
    """
    return validate_string_schema(schema_str)


def validate_string_schema(schema_str: str) -> Dict[str, Any]:
    """Validate enhanced string schema with detailed feedback"""
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'parsed_fields': {},
        'generated_schema': None,
        'features_used': []
    }

    try:
        # Parse the schema
        schema = parse_string_schema(schema_str)
        result['generated_schema'] = schema
        result['valid'] = True

        # Analyze features used
        features = set()
        if '[' in schema_str and ']' in schema_str:
            features.add('arrays')
        if '{' in schema_str and '}' in schema_str:
            features.add('objects')
        if '?' in schema_str:
            features.add('optional_fields')
        if 'enum(' in schema_str or 'choice(' in schema_str or 'select(' in schema_str:
            features.add('enums')
        if '|' in schema_str:
            features.add('union_types')
        if any(t in schema_str for t in ['email', 'url', 'datetime', 'date', 'uuid', 'phone']):
            features.add('special_types')
        # Check for constraints more carefully
        constraint_patterns = [
            r'string\([^)]+\)',  # string(min=1,max=100)
            r'int\([^)]+\)',     # int(0,120)
            r'number\([^)]+\)',  # number(min=0)
            r'text\([^)]+\)',    # text(max=500)
            r'\]\([^)]+\)'       # [string](max=5)
        ]
        if any(re.search(pattern, schema_str) for pattern in constraint_patterns):
            features.add('constraints')

        result['features_used'] = list(features)

        # Extract field information
        _extract_field_info(schema, result['parsed_fields'], "")

        # Add warnings for potential issues
        if len(result['parsed_fields']) > 20:
            result['warnings'].append("Schema has many fields (>20), consider simplifying")

        if 'arrays' in features and 'constraints' not in features:
            result['warnings'].append("Consider adding array size constraints for better LLM guidance")

    except Exception as e:
        result['errors'].append(str(e))

    return result


def _extract_field_info(schema: Dict[str, Any], fields_dict: Dict[str, Any], prefix: str = ""):
    """Extract field information from generated schema"""
    if schema.get('type') == 'object' and 'properties' in schema:
        required_fields = set(schema.get('required', []))

        for field_name, field_schema in schema['properties'].items():
            full_name = f"{prefix}.{field_name}" if prefix else field_name

            field_info = {
                'type': field_schema.get('type', 'unknown'),
                'required': field_name in required_fields,
                'constraints': {}
            }

            # Extract constraints
            for key in ['minimum', 'maximum', 'minLength', 'maxLength', 'minItems', 'maxItems', 'format', 'enum']:
                if key in field_schema:
                    field_info['constraints'][key] = field_schema[key]

            # Handle union types
            if 'anyOf' in field_schema:
                field_info['type'] = 'union'
                field_info['union_types'] = [item.get('type', 'unknown') for item in field_schema['anyOf']]

            fields_dict[full_name] = field_info

            # Recurse into nested objects
            if field_schema.get('type') == 'object':
                _extract_field_info(field_schema, fields_dict, full_name)
            elif field_schema.get('type') == 'array' and 'items' in field_schema:
                items_schema = field_schema['items']
                if items_schema.get('type') == 'object':
                    _extract_field_info(items_schema, fields_dict, f"{full_name}[]")

    elif schema.get('type') == 'array' and 'items' in schema:
        items_schema = schema['items']
        if items_schema.get('type') == 'object':
            _extract_field_info(items_schema, fields_dict, f"{prefix}[]" if prefix else "[]")
