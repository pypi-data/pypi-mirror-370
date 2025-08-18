# Getting Started with String Schema

String Schema is a Python library that makes it easy to define data schemas using intuitive string syntax that works well with Large Language Models (LLMs) for data extraction and validation.

## Installation

```bash
pip install string-schema
```

Optional dependencies:

```bash
pip install pydantic  # For Pydantic model generation
```

## Your First Schema

Let's start with a simple example:

```python
from string_schema import string_to_json_schema

# Define schema using intuitive string syntax
schema = string_to_json_schema("name:string, email:email, age:int?")

print(schema)
# {
#   "type": "object",
#   "properties": {
#     "name": {"type": "string"},
#     "email": {"type": "string", "format": "email"},
#     "age": {"type": "integer"}
#   },
#   "required": ["name", "email"]
# }
```

## Create Pydantic Models

```python
from string_schema import string_to_model

# Create Pydantic model from string syntax
UserModel = string_to_model("name:string, email:email, active:bool")

# Use immediately
user = UserModel(name="Alice", email="alice@example.com", active=True)
print(user.model_dump_json())  # {"name": "Alice", "email": "alice@example.com", "active": true}
```

## Data Validation

```python
from string_schema import validate_to_dict, validate_to_model

# Example raw data
raw_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "age": "25",  # String that needs conversion
    "extra": "ignored"  # Will be filtered out
}

# Validate to clean dictionaries
user_dict = validate_to_dict(raw_data, "name:string, email:email, age:int?")
print(user_dict)  # {"name": "John Doe", "email": "john@example.com", "age": 25}

# Validate to typed models
user_model = validate_to_model(raw_data, "name:string, email:email, age:int?")
print(user_model.name)  # "John Doe" - Full type safety
```

## Working with Arrays

```python
# Simple arrays
tags_schema = string_to_json_schema("[string]")
print(tags_schema)  # Array of strings schema

# Arrays with constraints
limited_tags = string_to_json_schema("[string](max=5)")
print(limited_tags)  # Array with max 5 items

# Arrays of objects
users_schema = string_to_json_schema("[{name:string, email:email}]")
print(users_schema)  # Array of user objects schema
```

## Special Types

```python
# Special types provide format hints
schema = string_to_json_schema("email:email, website:url, created:datetime, id:uuid")
print(schema)  # Schema with format validation
```

## Enum and Union Types

```python
# Enum types for specific choices
status_schema = string_to_json_schema("status:enum(active,inactive,pending)")
print(status_schema)  # Enum schema

# Union types for flexible data
id_schema = string_to_json_schema("id:string|uuid")
print(id_schema)  # Union type schema
```

## Code Generation

```python
from string_schema import string_to_model_code

# Generate Pydantic model code as string
code = string_to_model_code("User", "name:string, email:email, active:bool")
print(code)
# Output: Complete Pydantic model class as string

# Save to file
with open('user_model.py', 'w') as f:
    f.write(code)
```

## Validation

```python
from string_schema import validate_string_syntax

# Validate string schema syntax
result = validate_string_syntax("name:string, email:email, age:int?")
print(f"Valid: {result['valid']}")  # True
print(f"Features used: {result['features_used']}")  # ['basic_types', 'optional_fields']

# Example with invalid syntax
bad_result = validate_string_syntax("name:invalid_type")
print(f"Valid: {bad_result['valid']}")  # False
print(f"Errors: {bad_result['errors']}")  # ['Unknown type: invalid_type']
```

## Progressive Examples

### 1. Single Field

```python
from string_schema import string_to_json_schema

schema = string_to_json_schema("name:string")
print(schema)  # Basic string field schema
```

### 2. Multiple Fields

```python
schema = string_to_json_schema("name:string, age:int, active:bool")
print(schema)  # Multi-field object schema
```

### 3. With Constraints

```python
schema = string_to_json_schema("name:string(min=1,max=100), age:int(0,120), email:email")
print(schema)  # Schema with validation constraints
```

### 4. Optional Fields

```python
schema = string_to_json_schema("name:string, email:email, phone:phone?")
print(schema)  # Schema with optional fields (marked with ?)
```

### 5. Arrays

```python
# Simple array
tags_schema = string_to_json_schema("[string]")
print(tags_schema)  # Array of strings

# Array with constraints
limited_tags = string_to_json_schema("[string](max=5)")
print(limited_tags)  # Array with max 5 items
```

### 6. Nested Objects

```python
schema = string_to_json_schema("user:{name:string, email:email}, active:bool")
print(schema)  # Schema with nested object
```

## Common Patterns

### User Data

```python
user_schema = string_to_json_schema("name:string, email:email, active:bool")
print(user_schema)  # User schema
```

### API Response

```python
api_schema = string_to_json_schema("success:bool, data:object, message:string?")
print(api_schema)  # API response schema
```

### Product Data

```python
product_schema = string_to_json_schema("id:uuid, name:string, price:number(min=0), in_stock:bool")
print(product_schema)  # Product schema
```

## Next Steps

1. **[String Syntax Guide](string-syntax.md)** - Complete syntax reference
2. **[Examples](examples.md)** - Real-world use cases and patterns
3. **[API Reference](api-reference.md)** - Complete API documentation

String Schema makes it easy to define clear, validated data structures that work well with both traditional APIs and LLM-based data extraction.
