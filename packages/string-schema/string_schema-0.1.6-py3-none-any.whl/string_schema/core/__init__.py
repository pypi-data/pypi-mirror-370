"""
Core module for String Schema

Contains the fundamental classes and functions for schema definition and building.
"""

from .fields import SimpleField
from .builders import (
    simple_schema,
    list_of_objects_schema,
    simple_array_schema,
    quick_pydantic_model
)
from .validators import validate_schema

__all__ = [
    "SimpleField",
    "simple_schema",
    "list_of_objects_schema",
    "simple_array_schema", 
    "quick_pydantic_model",
    "validate_schema"
]
