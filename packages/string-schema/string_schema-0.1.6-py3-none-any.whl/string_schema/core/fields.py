"""
Core field definitions for Simple Schema

Contains the SimpleField class and related field utilities.
"""

from typing import Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class SimpleField:
    """Enhanced SimpleField with support for all new features"""
    
    def __init__(self, field_type: str, description: str = "", required: bool = True,
                 default: Any = None, min_val: Optional[Union[int, float]] = None,
                 max_val: Optional[Union[int, float]] = None, min_length: Optional[int] = None,
                 max_length: Optional[int] = None, choices: Optional[List[Any]] = None,
                 min_items: Optional[int] = None, max_items: Optional[int] = None,
                 format_hint: Optional[str] = None, union_types: Optional[List[str]] = None):
        """
        Initialize a SimpleField with comprehensive validation options.
        
        Args:
            field_type: The base type (string, integer, number, boolean)
            description: Human-readable description of the field
            required: Whether the field is required (default: True)
            default: Default value if field is not provided
            min_val: Minimum value for numeric types
            max_val: Maximum value for numeric types
            min_length: Minimum length for string types
            max_length: Maximum length for string types
            choices: List of allowed values (enum)
            min_items: Minimum items for array types
            max_items: Maximum items for array types
            format_hint: Special format hint (email, url, datetime, etc.)
            union_types: List of types for union fields
        """
        self.field_type = field_type
        self.description = description
        self.required = required
        self.default = default
        self.min_val = min_val
        self.max_val = max_val
        self.min_length = min_length
        self.max_length = max_length
        self.choices = choices
        self.min_items = min_items
        self.max_items = max_items
        self.format_hint = format_hint
        self.union_types = union_types or []
    
    def __repr__(self):
        """String representation of the field"""
        parts = [f"type={self.field_type}"]
        if self.description:
            parts.append(f"desc='{self.description}'")
        if not self.required:
            parts.append("optional")
        if self.choices:
            parts.append(f"choices={self.choices}")
        if self.union_types:
            parts.append(f"union={self.union_types}")
        return f"SimpleField({', '.join(parts)})"
    
    def to_dict(self) -> dict:
        """Convert field to dictionary representation"""
        result = {
            'type': self.field_type,
            'required': self.required
        }
        
        if self.description:
            result['description'] = self.description
        if self.default is not None:
            result['default'] = self.default
        if self.min_val is not None:
            result['min_val'] = self.min_val
        if self.max_val is not None:
            result['max_val'] = self.max_val
        if self.min_length is not None:
            result['min_length'] = self.min_length
        if self.max_length is not None:
            result['max_length'] = self.max_length
        if self.choices:
            result['choices'] = self.choices
        if self.min_items is not None:
            result['min_items'] = self.min_items
        if self.max_items is not None:
            result['max_items'] = self.max_items
        if self.format_hint:
            result['format_hint'] = self.format_hint
        if self.union_types:
            result['union_types'] = self.union_types
            
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SimpleField':
        """Create SimpleField from dictionary representation"""
        return cls(
            field_type=data['type'],
            description=data.get('description', ''),
            required=data.get('required', True),
            default=data.get('default'),
            min_val=data.get('min_val'),
            max_val=data.get('max_val'),
            min_length=data.get('min_length'),
            max_length=data.get('max_length'),
            choices=data.get('choices'),
            min_items=data.get('min_items'),
            max_items=data.get('max_items'),
            format_hint=data.get('format_hint'),
            union_types=data.get('union_types')
        )


# Utility functions for creating common field types
def create_enhanced_field(field_type: str, **kwargs) -> SimpleField:
    """Create enhanced SimpleField with all features"""
    return SimpleField(field_type, **kwargs)


def create_special_type_field(special_type: str, required: bool = True, **kwargs) -> SimpleField:
    """Create field with special type hints"""
    return SimpleField('string', format_hint=special_type, required=required, **kwargs)


def create_enum_field(values: List[str], required: bool = True, **kwargs) -> SimpleField:
    """Create enum field with specific values"""
    return SimpleField('string', choices=values, required=required, **kwargs)


def create_union_field(types: List[str], required: bool = True, **kwargs) -> SimpleField:
    """Create union field with multiple types"""
    primary_type = types[0] if types else 'string'
    return SimpleField(primary_type, union_types=types, required=required, **kwargs)
