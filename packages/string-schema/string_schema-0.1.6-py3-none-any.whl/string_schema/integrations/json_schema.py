"""
JSON Schema integration for Simple Schema

Contains functions for converting Simple Schema definitions to standard JSON Schema.
"""

from typing import Any, Dict, List, Union
import logging

from ..core.fields import SimpleField
from ..core.builders import simple_schema, _simple_field_to_json_schema

logger = logging.getLogger(__name__)


def to_json_schema(fields: Dict[str, Union[str, SimpleField]], 
                  title: str = "Generated Schema",
                  description: str = "",
                  schema_version: str = "https://json-schema.org/draft/2020-12/schema") -> Dict[str, Any]:
    """
    Convert Simple Schema fields to standard JSON Schema.
    
    Args:
        fields: Dictionary of field definitions
        title: Schema title
        description: Schema description
        schema_version: JSON Schema version URI
        
    Returns:
        Standard JSON Schema dictionary
    """
    # Generate the basic schema
    schema = simple_schema(fields)
    
    # Add JSON Schema metadata
    schema["$schema"] = schema_version
    schema["title"] = title
    
    if description:
        schema["description"] = description
    
    # Add additional properties control
    schema["additionalProperties"] = False
    
    return schema


def to_json_schema_with_examples(fields: Dict[str, Union[str, SimpleField]],
                                examples: List[Dict[str, Any]] = None,
                                title: str = "Generated Schema",
                                description: str = "") -> Dict[str, Any]:
    """
    Convert Simple Schema fields to JSON Schema with examples.
    
    Args:
        fields: Dictionary of field definitions
        examples: List of example data objects
        title: Schema title
        description: Schema description
        
    Returns:
        JSON Schema with examples
    """
    schema = to_json_schema(fields, title, description)
    
    if examples:
        schema["examples"] = examples
    
    return schema


def validate_json_schema_compliance(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that a schema complies with JSON Schema standards.
    
    Args:
        schema: Schema dictionary to validate
        
    Returns:
        Validation result dictionary
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'compliance_level': 'full'
    }
    
    # Check required top-level fields
    if 'type' not in schema:
        result['errors'].append("Missing required 'type' field")
    
    # Check schema version
    if '$schema' not in schema:
        result['warnings'].append("Missing '$schema' field - recommended for JSON Schema")
    
    # Validate object schema
    if schema.get('type') == 'object':
        result.update(_validate_object_schema_compliance(schema))
    elif schema.get('type') == 'array':
        result.update(_validate_array_schema_compliance(schema))
    
    # Check for non-standard extensions
    non_standard_fields = []
    for key in schema.keys():
        if key.startswith('x-') or key not in _get_standard_json_schema_fields():
            non_standard_fields.append(key)
    
    if non_standard_fields:
        result['warnings'].append(f"Non-standard fields detected: {', '.join(non_standard_fields)}")
        result['compliance_level'] = 'partial'
    
    result['valid'] = len(result['errors']) == 0
    return result


def _validate_object_schema_compliance(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate object schema compliance"""
    result = {'errors': [], 'warnings': []}
    
    properties = schema.get('properties', {})
    required = schema.get('required', [])
    
    # Validate properties
    for field_name, field_schema in properties.items():
        if not isinstance(field_schema, dict):
            result['errors'].append(f"Property '{field_name}' must be an object")
            continue
        
        if 'type' not in field_schema and 'anyOf' not in field_schema and '$ref' not in field_schema:
            result['warnings'].append(f"Property '{field_name}' missing type information")
    
    # Validate required fields
    for req_field in required:
        if req_field not in properties:
            result['errors'].append(f"Required field '{req_field}' not found in properties")
    
    return result


def _validate_array_schema_compliance(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate array schema compliance"""
    result = {'errors': [], 'warnings': []}
    
    if 'items' not in schema:
        result['errors'].append("Array schema must have 'items' definition")
    
    items = schema.get('items', {})
    if items and not isinstance(items, dict):
        result['errors'].append("Array 'items' must be an object")
    
    return result


def _get_standard_json_schema_fields() -> set:
    """Get set of standard JSON Schema fields"""
    return {
        '$schema', '$id', '$ref', '$defs', 'title', 'description', 'type', 'properties',
        'required', 'additionalProperties', 'items', 'minItems', 'maxItems', 'uniqueItems',
        'minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum', 'multipleOf',
        'minLength', 'maxLength', 'pattern', 'format', 'enum', 'const', 'anyOf', 'oneOf',
        'allOf', 'not', 'if', 'then', 'else', 'examples', 'default', 'readOnly', 'writeOnly'
    }


def optimize_json_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize JSON Schema for better performance and readability.
    
    Args:
        schema: JSON Schema to optimize
        
    Returns:
        Optimized JSON Schema
    """
    optimized = schema.copy()
    
    # Remove empty arrays and objects
    optimized = _remove_empty_values(optimized)
    
    # Consolidate similar constraints
    optimized = _consolidate_constraints(optimized)
    
    # Order fields for better readability
    optimized = _order_schema_fields(optimized)
    
    return optimized


def _remove_empty_values(obj: Any) -> Any:
    """Remove empty arrays and objects from schema"""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            cleaned_value = _remove_empty_values(value)
            if cleaned_value is not None and cleaned_value != [] and cleaned_value != {}:
                result[key] = cleaned_value
        return result
    elif isinstance(obj, list):
        return [_remove_empty_values(item) for item in obj if item is not None]
    else:
        return obj


def _consolidate_constraints(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Consolidate similar constraints in schema"""
    # This is a placeholder for more sophisticated optimization
    return schema


def _order_schema_fields(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Order schema fields for better readability"""
    if not isinstance(schema, dict):
        return schema
    
    # Define preferred field order
    field_order = [
        '$schema', '$id', 'title', 'description', 'type', 'properties', 'required',
        'items', 'minItems', 'maxItems', 'minimum', 'maximum', 'minLength', 'maxLength',
        'format', 'enum', 'anyOf', 'oneOf', 'allOf', 'examples', 'default',
        'additionalProperties'
    ]
    
    ordered = {}
    
    # Add fields in preferred order
    for field in field_order:
        if field in schema:
            value = schema[field]
            if isinstance(value, dict):
                ordered[field] = _order_schema_fields(value)
            elif isinstance(value, list):
                ordered[field] = [_order_schema_fields(item) if isinstance(item, dict) else item for item in value]
            else:
                ordered[field] = value
    
    # Add any remaining fields
    for field, value in schema.items():
        if field not in ordered:
            if isinstance(value, dict):
                ordered[field] = _order_schema_fields(value)
            elif isinstance(value, list):
                ordered[field] = [_order_schema_fields(item) if isinstance(item, dict) else item for item in value]
            else:
                ordered[field] = value
    
    return ordered


# Clear function name alias
def json_schema_to_openapi(json_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert JSON Schema to OpenAPI 3.0 schema format.

    Args:
        json_schema: Standard JSON Schema dictionary

    Returns:
        OpenAPI compatible schema dictionary

    Example:
        openapi_schema = json_schema_to_openapi(json_schema)
    """
    return convert_to_openapi_schema(json_schema)


# Reverse conversion functions
def json_schema_to_string(json_schema: Dict[str, Any]) -> str:
    """
    Convert JSON Schema to Simple Schema string syntax.

    Args:
        json_schema: JSON Schema dictionary

    Returns:
        String representation in Simple Schema syntax

    Example:
        json_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        schema_str = json_schema_to_string(json_schema)
        # Returns: "name:string"
    """
    from .reverse import json_schema_to_string as _json_schema_to_string
    return _json_schema_to_string(json_schema)


def convert_to_openapi_schema(json_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert JSON Schema to OpenAPI 3.0 schema format.
    
    Args:
        json_schema: Standard JSON Schema
        
    Returns:
        OpenAPI compatible schema
    """
    openapi_schema = json_schema.copy()
    
    # Remove JSON Schema specific fields that aren't supported in OpenAPI
    fields_to_remove = ['$schema', '$id']
    for field in fields_to_remove:
        openapi_schema.pop(field, None)
    
    # Convert format fields if needed
    if 'properties' in openapi_schema:
        for prop_name, prop_schema in openapi_schema['properties'].items():
            if isinstance(prop_schema, dict):
                openapi_schema['properties'][prop_name] = _convert_property_to_openapi(prop_schema)
    
    return openapi_schema


def _convert_property_to_openapi(prop_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Convert individual property to OpenAPI format"""
    openapi_prop = prop_schema.copy()
    
    # OpenAPI 3.0 doesn't support some JSON Schema features
    # This is a basic conversion - could be enhanced
    
    return openapi_prop


def generate_schema_documentation(schema: Dict[str, Any]) -> str:
    """
    Generate human-readable documentation from JSON Schema.
    
    Args:
        schema: JSON Schema to document
        
    Returns:
        Markdown documentation string
    """
    lines = []
    
    # Title and description
    title = schema.get('title', 'Schema Documentation')
    lines.append(f"# {title}")
    
    if 'description' in schema:
        lines.append(f"\n{schema['description']}")
    
    # Schema type
    schema_type = schema.get('type', 'unknown')
    lines.append(f"\n**Type:** {schema_type}")
    
    # Properties
    if schema_type == 'object' and 'properties' in schema:
        lines.append("\n## Properties")
        
        properties = schema['properties']
        required_fields = set(schema.get('required', []))
        
        for prop_name, prop_schema in properties.items():
            lines.append(f"\n### {prop_name}")
            
            # Required indicator
            if prop_name in required_fields:
                lines.append("**Required**")
            else:
                lines.append("*Optional*")
            
            # Type and description
            prop_type = prop_schema.get('type', 'unknown')
            lines.append(f"- **Type:** {prop_type}")
            
            if 'description' in prop_schema:
                lines.append(f"- **Description:** {prop_schema['description']}")
            
            # Constraints
            constraints = []
            if 'minimum' in prop_schema:
                constraints.append(f"minimum: {prop_schema['minimum']}")
            if 'maximum' in prop_schema:
                constraints.append(f"maximum: {prop_schema['maximum']}")
            if 'minLength' in prop_schema:
                constraints.append(f"min length: {prop_schema['minLength']}")
            if 'maxLength' in prop_schema:
                constraints.append(f"max length: {prop_schema['maxLength']}")
            if 'enum' in prop_schema:
                constraints.append(f"allowed values: {', '.join(map(str, prop_schema['enum']))}")
            
            if constraints:
                lines.append(f"- **Constraints:** {', '.join(constraints)}")
    
    return '\n'.join(lines)
