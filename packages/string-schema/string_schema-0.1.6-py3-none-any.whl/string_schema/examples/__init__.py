"""
Examples module for String Schema

Contains built-in schema presets and common patterns.
"""

from .presets import (
    user_schema,
    product_schema,
    contact_schema,
    article_schema,
    event_schema,
    get_examples
)
from .recipes import (
    create_list_schema,
    create_nested_schema,
    create_enum_schema,
    create_union_schema
)

__all__ = [
    # Presets
    "user_schema",
    "product_schema", 
    "contact_schema",
    "article_schema",
    "event_schema",
    "get_examples",
    
    # Recipes
    "create_list_schema",
    "create_nested_schema",
    "create_enum_schema", 
    "create_union_schema"
]
