# Examples

Practical examples and use cases for String Schema.

## Basic Examples

### Simple User Schema

```python
from string_schema import string_to_json_schema

# Define user schema using string syntax
user_schema = string_to_json_schema("name:string, email:email, age:int?")
print(user_schema)
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

### Create Pydantic Models

```python
from string_schema import string_to_model

# Create Pydantic model from string syntax
UserModel = string_to_model("name:string, email:email, active:bool")

# Use the model
user = UserModel(name="Alice", email="alice@example.com", active=True)
print(user.model_dump_json())  # {"name": "Alice", "email": "alice@example.com", "active": true}
```

## Array Examples

### Simple Arrays

```python
from string_schema import string_to_json_schema

# Array of strings
tags_schema = string_to_json_schema("[string]")
print(tags_schema)  # Array schema

# Array with constraints
limited_tags = string_to_json_schema("[string](max=5)")
print(limited_tags)  # Array with max 5 items

# Array of emails
emails_schema = string_to_json_schema("[email](min=1,max=3)")
print(emails_schema)  # Array of 1-3 emails
```

### Object Arrays

```python
# Array of user objects
users_schema = string_to_json_schema("[{name:string, email:email, role:enum(admin,user,guest)}]")
print(users_schema)  # Array of user objects schema
```

## Special Types

### Format Hints

```python
# Special types provide format validation
schema = string_to_json_schema("email:email, website:url, created:datetime, id:uuid")
print(schema)  # Schema with format hints
```

### Enum Types

```python
# Status field with specific choices
status_schema = string_to_json_schema("status:enum(active,inactive,pending), priority:enum(low,medium,high)")
print(status_schema)  # Enum schema
```

### Union Types

```python
# Flexible field types
flexible_schema = string_to_json_schema("id:string|uuid, value:string|int, response:string|null")
print(flexible_schema)  # Union type schema
```

## Real-World Examples

### E-commerce Product

```python
# Simple product schema
product_schema = string_to_json_schema("""
{
    id: uuid,
    name: string,
    price: number(min=0),
    category: enum(electronics,clothing,books),
    in_stock: bool,
    tags: [string]?
}
""")
print(product_schema)  # Product schema ready for validation
```

### User Management

```python
# Simple user management schema
user_schema = string_to_json_schema("""
{
    id: uuid,
    profile: {
        name: string,
        email: email,
        phone: phone?
    },
    account: {
        status: enum(active,inactive),
        role: enum(admin,user),
        verified: bool
    }
}
""")
print(user_schema)  # User management schema
```

### API Response

```python
# Simple API response schema
api_response_schema = string_to_json_schema("""
{
    success: bool,
    data: object|null,
    message: string?,
    timestamp: datetime
}
""")
print(api_response_schema)  # API response schema
```

### Blog Post

```python
# Simple blog post schema
blog_schema = string_to_json_schema("""
{
    id: uuid,
    title: string,
    content: text,
    author: {
        name: string,
        email: email
    },
    status: enum(draft,published),
    tags: [string]?,
    created: datetime
}
""")
print(blog_schema)  # Blog post schema
```

## Integration Examples

### Code Generation

```python
from string_schema import string_to_model_code

# Generate Pydantic model code
code = string_to_model_code("User", "name:string, email:email, active:bool")
print(code)
# Output: Complete Pydantic model class as string

# Save to file
with open('user_model.py', 'w') as f:
    f.write(code)
```

### OpenAPI Schema

```python
from string_schema import string_to_openapi

# Generate OpenAPI schema
openapi_schema = string_to_openapi("name:string, email:email, active:bool")
print(openapi_schema)  # OpenAPI-compatible schema
```

### Reverse Conversion

```python
from string_schema import model_to_string, string_to_model

# Create model and convert back to string
UserModel = string_to_model("name:string, email:email, active:bool")
schema_string = model_to_string(UserModel)
print(schema_string)  # "name:string, email:email, active:bool"
```

## Data Validation Examples

### Validate Raw Data

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

### Schema Syntax Validation

```python
from string_schema import validate_string_syntax

# Validate schema syntax
result = validate_string_syntax("name:string, email:email, age:int?")
print(f"Valid: {result['valid']}")  # True
print(f"Features used: {result['features_used']}")  # ['basic_types', 'optional_fields']

# Example with invalid syntax
bad_result = validate_string_syntax("name:invalid_type")
print(f"Valid: {bad_result['valid']}")  # False
print(f"Errors: {bad_result['errors']}")  # ['Unknown type: invalid_type']
```

## Function Decorators

```python
from string_schema import returns_dict, returns_model
import uuid

# Auto-validate function returns to dicts
@returns_dict("id:string, name:string, active:bool")
def create_user(name):
    # Input: "Alice"
    return {"id": str(uuid.uuid4()), "name": name, "active": True, "extra": "ignored"}
    # Output: {"id": "123e4567-...", "name": "Alice", "active": True}
    # Note: 'extra' field filtered out

# Auto-validate function returns to models
@returns_model("name:string, email:string")
def process_user(raw_input):
    # Input: {"name": "Bob", "email": "bob@test.com", "junk": "data"}
    return {"name": raw_input["name"], "email": raw_input["email"], "junk": "data"}
    # Output: UserModel(name="Bob", email="bob@test.com")
    # Note: Returns typed Pydantic model, 'junk' field filtered out
```

These examples demonstrate String Schema's flexibility for defining data structures that work well with both traditional validation and LLM-based data extraction.
