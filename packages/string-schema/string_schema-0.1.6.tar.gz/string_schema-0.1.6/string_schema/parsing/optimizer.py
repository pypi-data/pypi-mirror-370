"""
Schema optimization utilities for Simple Schema

Contains functions for optimizing and improving schema definitions.
"""

import re
from typing import Dict, Any, List, Optional
import logging

from .string_parser import validate_string_schema

logger = logging.getLogger(__name__)


def optimize_string_schema(schema_str: str) -> str:
    """Optimize enhanced schema string for better readability"""
    try:
        validation = validate_string_schema(schema_str)
        if not validation['valid']:
            return schema_str
        
        # For now, return the original schema
        # Future: Could implement smart formatting, type inference, etc.
        optimized = _format_schema_string(schema_str)
        return optimized
        
    except Exception as e:
        logger.warning(f"Failed to optimize schema string: {e}")
        return schema_str


def _format_schema_string(schema_str: str) -> str:
    """Format schema string for better readability"""
    # Remove extra whitespace
    schema_str = re.sub(r'\s+', ' ', schema_str.strip())
    
    # Add spacing around operators
    schema_str = re.sub(r'([:|,])', r'\1 ', schema_str)
    schema_str = re.sub(r'\s+', ' ', schema_str)
    
    # Format nested structures
    if '{' in schema_str and '}' in schema_str:
        schema_str = _format_nested_objects(schema_str)
    
    return schema_str.strip()


def _format_nested_objects(schema_str: str) -> str:
    """Format nested object structures with proper indentation"""
    # This is a simplified formatter - could be enhanced
    result = ""
    indent_level = 0
    
    for char in schema_str:
        if char == '{':
            result += char + '\n' + '  ' * (indent_level + 1)
            indent_level += 1
        elif char == '}':
            indent_level -= 1
            result += '\n' + '  ' * indent_level + char
        elif char == ',':
            result += char + '\n' + '  ' * indent_level
        else:
            result += char
    
    return result


def suggest_improvements(schema_str: str) -> List[str]:
    """Suggest improvements for a schema string"""
    suggestions = []
    
    try:
        validation = validate_string_schema(schema_str)
        
        # Check for missing constraints
        if 'arrays' in validation.get('features_used', []):
            if 'constraints' not in validation.get('features_used', []):
                suggestions.append("Consider adding array size constraints (e.g., [string](max=5)) for better LLM guidance")
        
        # Check for missing special types
        if 'email' in schema_str.lower() and 'special_types' not in validation.get('features_used', []):
            suggestions.append("Use 'email' type instead of 'string' for email fields")
        
        if 'url' in schema_str.lower() and 'special_types' not in validation.get('features_used', []):
            suggestions.append("Use 'url' type instead of 'string' for URL fields")
        
        # Check for overly complex schemas
        field_count = len(validation.get('parsed_fields', {}))
        if field_count > 15:
            suggestions.append("Consider breaking down complex schemas into smaller, focused schemas")
        
        # Check for missing optional markers
        if '?' not in schema_str and field_count > 5:
            suggestions.append("Consider marking some fields as optional with '?' for more flexible extraction")
        
        # Check for enum opportunities
        if 'status' in schema_str.lower() and 'enums' not in validation.get('features_used', []):
            suggestions.append("Consider using enum for status fields (e.g., status:enum(active,inactive))")
        
    except Exception as e:
        logger.warning(f"Failed to generate suggestions: {e}")
    
    return suggestions


def simplify_schema(schema_str: str, max_fields: int = 10) -> str:
    """Simplify a complex schema by reducing fields"""
    try:
        validation = validate_string_schema(schema_str)
        parsed_fields = validation.get('parsed_fields', {})
        
        if len(parsed_fields) <= max_fields:
            return schema_str
        
        # This is a basic implementation - could be enhanced with smarter field selection
        logger.info(f"Schema has {len(parsed_fields)} fields, simplifying to {max_fields}")
        
        # For now, just return the original schema with a warning
        return schema_str + " # Note: Consider simplifying this schema"
        
    except Exception as e:
        logger.warning(f"Failed to simplify schema: {e}")
        return schema_str


def infer_types(data_sample: Dict[str, Any]) -> str:
    """Infer schema string from a data sample"""
    fields = []
    
    for key, value in data_sample.items():
        field_def = _infer_field_type(key, value)
        fields.append(field_def)
    
    return ", ".join(fields)


def _infer_field_type(field_name: str, value: Any) -> str:
    """Infer field type from a value"""
    if value is None:
        return f"{field_name}:string?"
    
    if isinstance(value, bool):
        return f"{field_name}:bool"
    
    if isinstance(value, int):
        return f"{field_name}:int"
    
    if isinstance(value, float):
        return f"{field_name}:number"
    
    if isinstance(value, str):
        # Try to infer special types
        if '@' in value and '.' in value:
            return f"{field_name}:email"
        elif value.startswith(('http://', 'https://')):
            return f"{field_name}:url"
        elif re.match(r'^\d{4}-\d{2}-\d{2}', value):
            return f"{field_name}:date"
        else:
            return f"{field_name}:string"
    
    if isinstance(value, list):
        if not value:
            return f"{field_name}:[string]"
        
        # Infer from first item
        first_item = value[0]
        if isinstance(first_item, dict):
            # Object array - this would need more complex inference
            return f"{field_name}:[object]"
        else:
            item_type = _infer_simple_type(first_item)
            return f"{field_name}:[{item_type}]"
    
    if isinstance(value, dict):
        # Nested object - would need recursive inference
        return f"{field_name}:object"
    
    return f"{field_name}:string"


def _infer_simple_type(value: Any) -> str:
    """Infer simple type from a value"""
    if isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, str):
        if '@' in value and '.' in value:
            return "email"
        elif value.startswith(('http://', 'https://')):
            return "url"
        else:
            return "string"
    else:
        return "string"


def validate_optimization(original: str, optimized: str) -> Dict[str, Any]:
    """Validate that optimization preserves schema semantics"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'changes': []
    }
    
    try:
        original_validation = validate_string_schema(original)
        optimized_validation = validate_string_schema(optimized)
        
        if not original_validation['valid']:
            result['errors'].append("Original schema is invalid")
        
        if not optimized_validation['valid']:
            result['errors'].append("Optimized schema is invalid")
        
        # Compare field counts
        orig_fields = len(original_validation.get('parsed_fields', {}))
        opt_fields = len(optimized_validation.get('parsed_fields', {}))
        
        if orig_fields != opt_fields:
            result['warnings'].append(f"Field count changed: {orig_fields} → {opt_fields}")
        
        # Compare features
        orig_features = set(original_validation.get('features_used', []))
        opt_features = set(optimized_validation.get('features_used', []))
        
        if orig_features != opt_features:
            added = opt_features - orig_features
            removed = orig_features - opt_features
            
            if added:
                result['changes'].append(f"Added features: {', '.join(added)}")
            if removed:
                result['changes'].append(f"Removed features: {', '.join(removed)}")
        
    except Exception as e:
        result['errors'].append(f"Validation error: {str(e)}")
    
    result['valid'] = len(result['errors']) == 0
    return result
