"""
String Schema - A simple, LLM-friendly schema definition library

This library provides an intuitive way to define data schemas using simple string syntax
that works well with Large Language Models for data extraction and validation.

Key Features:
- Clear, descriptive function names that tell you exactly what they do
- Direct conversion paths: string → JSON Schema, Pydantic, OpenAPI
- String-based schema syntax parsing
- JSON Schema generation
- Pydantic model integration
- Built-in validation and optimization
"""

# Main conversion functions (clear names)
from .parsing.string_parser import (
    string_to_json_schema,
    validate_string_syntax,
    # Legacy names for backward compatibility
    parse_string_schema,
    validate_string_schema
)

# 🎯 Core Pydantic Utility Functions
from .utilities import (
    string_to_model,        # String → Pydantic model (main utility)
    validate_to_dict,       # Validate data → dict
    validate_to_model,      # Validate data → Pydantic model
    returns_dict,           # Decorator for dict validation
    returns_model,          # Decorator for model validation
    get_model_info,         # Model introspection utility
    validate_schema_compatibility,  # Schema compatibility checker
    # Legacy alias for backward compatibility
    create_model            # Use string_to_model instead
)

# Integration functions (consistent naming)
from .integrations.pydantic import (
    string_to_model_code,
    json_schema_to_model,
    model_to_string,
    model_to_json_schema,
    # Legacy names for backward compatibility
    string_to_pydantic,
    string_to_pydantic_code,
    json_schema_to_pydantic,
    create_pydantic_from_json_schema
)

from .integrations.openapi import (
    string_to_openapi,
    openapi_to_string,
    openapi_to_json_schema
)

from .integrations.json_schema import (
    json_schema_to_openapi,
    json_schema_to_string,
    # Legacy names for backward compatibility
    convert_to_openapi_schema
)

# Note: Built-in presets moved to examples/ directory
# Import them from simple_schema.examples.presets if needed

__version__ = "0.1.0"
__author__ = "importal"

__all__ = [
    # 🎯 Forward conversion functions (source → target)
    "string_to_json_schema",        # String → JSON Schema
    "string_to_model",              # String → Pydantic model (main utility)
    "string_to_model_code",         # String → Pydantic code
    "string_to_openapi",            # String → OpenAPI schema
    "json_schema_to_model",         # JSON Schema → Pydantic model
    "json_schema_to_openapi",       # JSON Schema → OpenAPI schema
    "validate_string_syntax",       # Validate string syntax

    # 🔄 Reverse conversion functions (target → source)
    "model_to_string",              # Pydantic model → String
    "model_to_json_schema",         # Pydantic model → JSON Schema
    "json_schema_to_string",        # JSON Schema → String
    "openapi_to_string",            # OpenAPI schema → String
    "openapi_to_json_schema",       # OpenAPI schema → JSON Schema

    # 🔍 Data validation functions
    "validate_to_dict",             # Validate data → dict
    "validate_to_model",            # Validate data → Pydantic model

    # 🎨 Function decorators
    "returns_dict",                 # Decorator for dict validation
    "returns_model",                # Decorator for model validation

    # 🔧 Utility functions
    "get_model_info",               # Model introspection utility
    "validate_schema_compatibility", # Schema compatibility checker

    # 🔙 Legacy names (for backward compatibility)
    "create_model",                 # Use string_to_model instead
    "string_to_pydantic",           # Use string_to_model instead
    "string_to_pydantic_code",      # Use string_to_model_code instead
    "json_schema_to_pydantic",      # Use json_schema_to_model instead
    "parse_string_schema",
    "validate_string_schema",
    "create_pydantic_from_json_schema",
    "convert_to_openapi_schema",
]
