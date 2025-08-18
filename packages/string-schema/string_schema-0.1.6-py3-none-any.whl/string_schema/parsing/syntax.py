"""
Syntax definitions and examples for String Schema string parsing

Contains examples and documentation for the string-based schema syntax.
"""

from typing import Dict, Any


# Enhanced examples with all new features
STRING_SCHEMA_EXAMPLES = {
    "simple_arrays": {
        "description": "Simple arrays of basic types (FIXED BUG!)",
        "schema_string": "[string]",
        "prompt_example": "Extract tags: python, javascript, react, vue"
    },
    
    "typed_arrays": {
        "description": "Arrays with specific types",
        "schema_string": "[email]",
        "prompt_example": "Extract emails: john@example.com, jane@company.org"
    },
    
    "constrained_arrays": {
        "description": "Arrays with size constraints",
        "schema_string": "[string](max=5)",
        "prompt_example": "Extract up to 5 tags: python, machine learning, AI, data science"
    },
    
    "object_arrays": {
        "description": "Arrays of objects with constraints",
        "schema_string": "[{name:string, email:email}](min=1,max=10)",
        "prompt_example": "Extract contacts: John Doe (john@example.com), Jane Smith (jane@company.org)"
    },
    
    "special_types": {
        "description": "Special type hints for LLMs",
        "schema_string": "name:string, email:email, website:url?, created:datetime",
        "prompt_example": "User: John Doe, email john@example.com, website https://johndoe.com, created 2024-01-15"
    },
    
    "enums": {
        "description": "Enum types for clear choices",
        "schema_string": "name:string, status:enum(active,inactive,pending), priority:choice(low,medium,high)",
        "prompt_example": "Task: Fix bug, status active, priority high"
    },
    
    "union_types": {
        "description": "Union types for flexible data",
        "schema_string": "id:string|uuid, value:string|int, content:string|null",
        "prompt_example": "Record: id abc123, value 42, content null"
    },
    
    "nested_objects": {
        "description": "Complex nested structures",
        "schema_string": "{user:{name:string, contact:{email:email, phones:[phone]?}}, metadata:{created:datetime, tags:[string](max=5)?}}",
        "prompt_example": "User John Doe, email john@example.com, phone +1-555-0123, created 2024-01-15, tags: developer, python"
    },
    
    "comprehensive_example": {
        "description": "All features combined",
        "schema_string": "[{name:string(min=1,max=100), emails:[email](min=1,max=2), role:enum(admin,user,guest), profile:{bio:text?, social:[url]?}?, active:bool, last_login:datetime?}](min=1,max=20)",
        "prompt_example": "Users: John Doe (john@example.com, admin, active, last login 2024-01-15), Jane Smith (jane@company.org, user, bio: Developer)"
    },
    
    "alternative_syntax": {
        "description": "Alternative array syntax",
        "schema_string": "tags:array(string,max=5), contacts:list(email,min=1)",
        "prompt_example": "Tags: python, react, nodejs. Contacts: john@example.com, jane@company.org"
    }
}


def get_string_schema_examples() -> Dict[str, Dict[str, Any]]:
    """Get all enhanced string schema examples"""
    return STRING_SCHEMA_EXAMPLES.copy()


def print_string_schema_examples():
    """Print all enhanced string schema examples with new features"""
    print("🚀 Enhanced String Schema Examples:")
    print("=" * 60)
    
    for name, example in STRING_SCHEMA_EXAMPLES.items():
        print(f"\n📝 {name.upper().replace('_', ' ')}")
        print(f"Description: {example['description']}")
        print(f"Schema: {example['schema_string']}")
        print(f"Prompt: {example['prompt_example']}")
        print("-" * 40)


def get_syntax_help() -> str:
    """Get comprehensive syntax help for string schemas"""
    return """
🚀 String Schema String Syntax Guide

## Basic Types
- string, str, text    → String type
- int, integer         → Integer type  
- number, float        → Number type
- bool, boolean        → Boolean type

## Special Types (with format hints)
- email               → Email validation
- url, uri            → URL validation
- datetime            → DateTime parsing
- date                → Date parsing
- uuid                → UUID validation
- phone               → Phone formatting

## Field Definitions
- name                → String field (default)
- name:string         → Explicit string field
- age:int             → Integer field
- email:email         → Email field with validation
- website:url?        → Optional URL field

## Arrays
- [string]            → Array of strings
- [email]             → Array of emails
- [int]               → Array of integers
- [{name, email}]     → Array of objects

## Array Constraints
- [string](max=5)     → Max 5 items
- [email](min=1,max=3) → 1-3 items required
- [{name,email}](min=1,max=10) → 1-10 objects

## Alternative Array Syntax
- tags:array(string,max=5)     → Array with constraints
- contacts:list(email,min=1)   → List with constraints

## Enums
- status:enum(active,inactive,pending)
- priority:choice(low,medium,high)
- category:select(tech,business,personal)

## Union Types
- id:string|uuid      → String or UUID
- value:string|int    → String or integer
- response:string|null → Nullable field

## Constraints
- name:string(min=1,max=100)   → String length
- age:int(min=0,max=120)       → Integer range
- rating:float(min=1.0,max=5.0) → Float range

## Objects
- {name:string, age:int}       → Simple object
- user:{name, email, phone?}   → Nested object

## Complex Examples
```
# E-commerce product
{
    name:string(min=1,max=200),
    price:number(min=0),
    category:enum(electronics,clothing,books),
    images:[url](max=5)?,
    reviews:[{rating:int(1,5), comment:text}](max=10)?
}

# User management
[{
    id:string|uuid,
    profile:{name:string, email:email, phone:phone?},
    status:enum(active,inactive,suspended),
    permissions:[string]?
}](min=1,max=100)
```

## Tips
- Use ? for optional fields
- Add constraints for better LLM guidance
- Use special types for validation
- Combine features for complex schemas
"""


def validate_syntax_example(example_name: str) -> bool:
    """Validate that a syntax example is properly formatted"""
    if example_name not in STRING_SCHEMA_EXAMPLES:
        return False
    
    example = STRING_SCHEMA_EXAMPLES[example_name]
    required_keys = ['description', 'schema_string', 'prompt_example']
    
    return all(key in example for key in required_keys)


def get_syntax_patterns() -> Dict[str, str]:
    """Get common syntax patterns for reference"""
    return {
        "simple_field": "name:type",
        "optional_field": "name:type?",
        "constrained_field": "name:type(min=1,max=100)",
        "enum_field": "name:enum(value1,value2,value3)",
        "union_field": "name:type1|type2|type3",
        "simple_array": "[type]",
        "constrained_array": "[type](min=1,max=5)",
        "object_array": "[{field1:type1, field2:type2}]",
        "nested_object": "name:{field1:type1, field2:type2}",
        "alternative_array": "name:array(type,max=5)"
    }


# Built-in enhanced schema generators for string syntax
def user_string_schema(include_email: bool = True, include_phone: bool = False, 
                      include_profile: bool = False) -> str:
    """Generate enhanced user schema string"""
    parts = ["name:string(min=1,max=100)", "age:int(min=13,max=120)"]
    
    if include_email:
        parts.append("email:email")
    if include_phone:
        parts.append("phone:phone?")
    if include_profile:
        parts.append("bio:text(max=500)?")
        parts.append("avatar:url?")
    
    return ", ".join(parts)


def product_string_schema(include_price: bool = True, include_description: bool = True,
                         include_images: bool = False, include_reviews: bool = False) -> str:
    """Generate enhanced product schema string"""
    parts = ["name:string(min=1,max=200)", "category:enum(electronics,clothing,books,home,sports)"]
    
    if include_price:
        parts.append("price:number(min=0)")
    if include_description:
        parts.append("description:text(max=1000)?")
    if include_images:
        parts.append("images:[url](max=5)?")
    if include_reviews:
        parts.append("reviews:[{rating:int(1,5), comment:text(max=500)}](max=10)?")
    
    return ", ".join(parts)


def contact_string_schema(include_company: bool = False, include_social: bool = False) -> str:
    """Generate enhanced contact schema string"""
    parts = ["name:string(min=1,max=100)", "emails:[email](min=1,max=3)", "phones:[phone]?"]
    
    if include_company:
        parts.append("company:{name:string, role:string?, department:string?}?")
    if include_social:
        parts.append("social:{linkedin:url?, twitter:url?, github:url?}?")
    
    return ", ".join(parts)
