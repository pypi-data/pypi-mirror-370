# String Schema

A simple, LLM-friendly schema definition library for Python that converts intuitive string syntax into structured data schemas.

## 🚀 Quick Start

### Installation

```bash
pip install string-schema
```

### 30-Second Example

```python
from string_schema import string_to_json_schema

# Define a schema with simple, readable syntax
schema = string_to_json_schema("name:string, email:email, age:int?")

# Get a complete JSON Schema ready for validation
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

### Create Pydantic Models Directly

```python
from string_schema import string_to_model

# Create Pydantic model from string syntax
UserModel = string_to_model("name:string, email:email, age:int?")

# Use immediately
user = UserModel(name="Alice", email="alice@example.com")
print(user.model_dump_json())  # {"name": "Alice", "email": "alice@example.com"}
```

## 🎯 What String Schema Does

String Schema takes human-readable text descriptions and converts them into structured schemas for data validation, extraction, and API documentation. Perfect for LLM data extraction, API development, and configuration validation.

**Input:** Human-readable string syntax
**Output:** JSON Schema, Pydantic models, or OpenAPI specifications

## 🚀 Core Functions & Use Cases

### 📝 Schema Conversion Matrix

**Forward Conversions (Source → Target):**

| Function                   | Input            | Output               | Use Case                                    |
| -------------------------- | ---------------- | -------------------- | ------------------------------------------- |
| `string_to_json_schema()`  | String syntax    | JSON Schema dict     | **Main conversion** - string to JSON Schema |
| `string_to_model()`        | String syntax    | Pydantic model class | **Direct path** - string to Pydantic model  |
| `string_to_model_code()`   | String syntax    | Python code string   | **Code generation** - for templates         |
| `string_to_openapi()`      | String syntax    | OpenAPI schema dict  | **Direct path** - string to OpenAPI         |
| `json_schema_to_model()`   | JSON Schema dict | Pydantic model class | When you already have JSON Schema           |
| `json_schema_to_openapi()` | JSON Schema dict | OpenAPI schema dict  | When you already have JSON Schema           |

**Reverse Conversions (Target → Source):**

| Function                   | Input            | Output           | Use Case                                   |
| -------------------------- | ---------------- | ---------------- | ------------------------------------------ |
| `model_to_string()`        | Pydantic model   | String syntax    | **Schema introspection** - model to string |
| `model_to_json_schema()`   | Pydantic model   | JSON Schema dict | **Export** - model to JSON Schema          |
| `json_schema_to_string()`  | JSON Schema dict | String syntax    | **Migration** - JSON Schema to string      |
| `openapi_to_string()`      | OpenAPI schema   | String syntax    | **Import** - OpenAPI to string             |
| `openapi_to_json_schema()` | OpenAPI schema   | JSON Schema dict | **Conversion** - OpenAPI to JSON Schema    |

### 🔍 Data Validation Functions

| Function                   | Input         | Output            | Use Case                          |
| -------------------------- | ------------- | ----------------- | --------------------------------- |
| `validate_to_dict()`       | Data + schema | Validated dict    | **API responses** - clean dicts   |
| `validate_to_model()`      | Data + schema | Pydantic model    | **Business logic** - typed models |
| `validate_string_syntax()` | String syntax | Validation result | Check syntax and get feedback     |

### 🎨 Function Decorators

| Decorator          | Purpose                | Returns        | Use Case           |
| ------------------ | ---------------------- | -------------- | ------------------ |
| `@returns_dict()`  | Auto-validate to dict  | Validated dict | **API endpoints**  |
| `@returns_model()` | Auto-validate to model | Pydantic model | **Business logic** |

### 🔧 Utility Functions

| Function                          | Purpose             | Returns            | Use Case                 |
| --------------------------------- | ------------------- | ------------------ | ------------------------ |
| `get_model_info()`                | Model introspection | Model details dict | **Debugging & analysis** |
| `validate_schema_compatibility()` | Schema validation   | Compatibility info | **Schema validation**    |

### 🎯 Key Scenarios

- **🤖 LLM Data Extraction**: Define extraction schemas that LLMs can easily follow
- **🔧 API Development**: Generate Pydantic models and OpenAPI docs from simple syntax
- **✅ Data Validation**: Create robust validation schemas with minimal code
- **🌍 Timezone-Aware APIs**: Automatic UTC conversion for consistent datetime handling
- **📋 Configuration**: Define and validate application configuration schemas
- **🔄 Data Transformation**: Convert between different schema formats

### ✅ Validate Data

```python
from string_schema import validate_to_dict, validate_to_model

# Example raw data (from API, user input, etc.)
raw_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "age": "25",  # String that needs conversion
    "extra_field": "ignored"  # Will be filtered out
}

# Validate to clean dictionaries (perfect for API responses)
user_dict = validate_to_dict(raw_data, "name:string, email:email, age:int?")
print(user_dict)  # {"name": "John Doe", "email": "john@example.com", "age": 25}

# Validate to typed models (perfect for business logic)
user_model = validate_to_model(raw_data, "name:string, email:email, age:int?")
print(user_model.name)  # "John Doe" - Full type safety
print(user_model.age)   # 25 - Converted to int

# 🌍 Automatic timezone handling for datetime fields
from datetime import datetime
event_data = {"name": "Meeting", "start_time": datetime(2025, 8, 13, 14, 30)}
event_dict = validate_to_dict(event_data, "name:string, start_time:datetime")
print(event_dict)  # {"name": "Meeting", "start_time": "2025-08-13T14:30:00+00:00"}
```

### 🎨 Function Decorators

```python
from string_schema import returns_dict, returns_model
import uuid

# Auto-validate function returns to dicts
@returns_dict("id:string, name:string, active:bool")
def create_user(name):
    # Input: "Alice"
    # Function returns unvalidated dict
    return {"id": str(uuid.uuid4()), "name": name, "active": True, "extra": "ignored"}
    # Output: {"id": "123e4567-...", "name": "Alice", "active": True}
    # Note: 'extra' field filtered out, types validated

# Auto-validate function returns to models
@returns_model("name:string, email:string")
def process_user(raw_input):
    # Input: {"name": "Bob", "email": "bob@test.com", "junk": "data"}
    # Function returns unvalidated dict
    return {"name": raw_input["name"], "email": raw_input["email"], "junk": "data"}
    # Output: UserModel(name="Bob", email="bob@test.com")
    # Note: Returns typed Pydantic model, 'junk' field filtered out

# Usage examples:
user_dict = create_user("Alice")  # Returns validated dict
user_model = process_user({"name": "Bob", "email": "bob@test.com"})  # Returns Pydantic model
print(user_model.name)  # "Bob" - Full type safety
```

### 🌐 FastAPI Integration

```python
from string_schema import string_to_model, returns_dict

# Create models for FastAPI
UserRequest = string_to_model("name:string, email:email")

@app.post("/users")
@returns_dict("id:int, name:string, email:string")
def create_user_endpoint(user: UserRequest):
    return {"id": 123, "name": user.name, "email": user.email}
```

**Features**: Arrays `[{name:string}]`, nested objects `{profile:{bio:text?}}`, enums, constraints, decorators.

[📖 **Complete Documentation**](docs/pydantic-utilities.md)

## 🎓 More Examples

### 🌱 Simple Example - Basic User Data

```python
from string_schema import string_to_json_schema

# Define schema using intuitive string syntax
schema = string_to_json_schema("""
name:string(min=1, max=100),
email:email,
age:int(0, 120)?,
active:bool
""")

# Result: JSON Schema dictionary ready for validation
print(schema)
# {
#   "type": "object",
#   "properties": {
#     "name": {"type": "string", "minLength": 1, "maxLength": 100},
#     "email": {"type": "string", "format": "email"},
#     "age": {"type": "integer", "minimum": 0, "maximum": 120},
#     "active": {"type": "boolean"}
#   },
#   "required": ["name", "email", "active"]
# }
```

### 🌳 Moderately Complex Example - Product Data

```python
# Product with arrays and nested objects
schema = string_to_json_schema("""
{
    id:uuid,
    name:string,
    price:number(min=0),
    tags:[string]?,
    inventory:{
        in_stock:bool,
        quantity:int?
    }
}
""")

# Result: Complete JSON Schema with nested objects and arrays
print(schema)  # Full JSON Schema ready for validation
```

> 📚 **For more examples and advanced syntax**, see our [detailed documentation](docs/string-syntax.md)

## 🔄 Output Formats & Results

### 🐍 Pydantic Models (Python Classes)

```python
from string_schema import string_to_model

# Direct conversion: String syntax → Pydantic model
UserModel = string_to_model("name:string, email:email, active:bool")

# Use the model for validation
user = UserModel(name="John Doe", email="john@example.com", active=True)
print(user.model_dump_json())  # {"name": "John Doe", "email": "john@example.com", "active": true}
```

### 🔧 Code Generation (For Templates & Tools)

```python
from string_schema import string_to_model_code

# Generate Pydantic model code as a string
code = string_to_model_code("User", "name:string, email:email, active:bool")
print(code)

# Output:
# from pydantic import BaseModel
# from typing import Optional
#
# class User(BaseModel):
#     name: str
#     email: str
#     active: bool

# Perfect for code generators, templates, or saving to files
with open('models.py', 'w') as f:
    f.write(code)
```

### 🌐 OpenAPI Schemas (API Documentation)

```python
from string_schema import string_to_openapi

# Direct conversion: String syntax → OpenAPI schema
openapi_schema = string_to_openapi("name:string, email:email")
print(openapi_schema)
# {
#   "type": "object",
#   "properties": {
#     "name": {"type": "string"},
#     "email": {"type": "string", "format": "email"}
#   },
#   "required": ["name", "email"]
# }
```

## 🔄 Reverse Conversions (Universal Schema Converter)

String Schema provides complete bidirectional conversion between all schema formats!

> **⚠️ Information Loss Notice**: Reverse conversions (from JSON Schema/OpenAPI/Pydantic back to string syntax) may lose some information due to format differences. However, the resulting schemas are designed to cover the most common use cases and maintain functional equivalence for typical validation scenarios.

### 🔍 Schema Introspection

```python
from string_schema import model_to_string, string_to_model

# Create a model first
UserModel = string_to_model("name:string, email:email, active:bool")

# Reverse engineer it back to string syntax
schema_string = model_to_string(UserModel)
print(f"Model schema: {schema_string}")
# Output: "name:string, email:email, active:bool"
```

### 📦 Migration & Import

```python
from string_schema import json_schema_to_string

# Example: Convert existing JSON Schema to String Schema syntax
json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer"}
    },
    "required": ["name", "email"]
}

simple_syntax = json_schema_to_string(json_schema)
print(f"Converted: {simple_syntax}")
# Output: "name:string, email:email, age:int?"
```

### 🔧 Schema Comparison & Analysis

```python
from string_schema import string_to_model, model_to_string

# Create two versions of a model
UserV1 = string_to_model("name:string, email:email")
UserV2 = string_to_model("name:string, email:email, active:bool")

# Compare them
v1_str = model_to_string(UserV1)
v2_str = model_to_string(UserV2)

print("Schema changes:")
print(f"V1: {v1_str}")  # "name:string, email:email"
print(f"V2: {v2_str}")  # "name:string, email:email, active:bool"
```

## 🎨 String Syntax Reference

### Basic Types

- `string`, `int`, `number`, `bool` → Basic data types
- `email`, `url`, `datetime`, `date`, `uuid`, `phone` → Special validated types

### Field Modifiers

- `field_name:type` → Required field
- `field_name:type?` → Optional field
- `field_name:type(constraints)` → Field with validation

### Common Patterns

- `string(min=1, max=100)` → Length constraints
- `int(0, 120)` → Range constraints
- `[string]` → Simple arrays
- `[{name:string, email:email}]` → Object arrays
- `status:enum(active, inactive)` → Enum values
- `id:string|uuid` → Union types

> 📖 **Complete syntax guide**: See [docs/string-syntax.md](docs/string-syntax.md) for full reference

## ✅ Validation

```python
from string_schema import validate_string_syntax

# Validate your schema syntax
result = validate_string_syntax("name:string, email:email, age:int?")

print(f"Valid: {result['valid']}")  # True
print(f"Features used: {result['features_used']}")  # ['basic_types', 'optional_fields']
print(f"Field count: {len(result['parsed_fields'])}")  # 3

# Example with invalid syntax
bad_result = validate_string_syntax("name:invalid_type")
print(f"Valid: {bad_result['valid']}")  # False
print(f"Errors: {bad_result['errors']}")  # ['Unknown type: invalid_type']
```

## 🏗️ Common Use Cases

### 🤖 LLM Data Extraction

```python
from string_schema import string_to_json_schema

# Define what data to extract
schema = string_to_json_schema("company:string, employees:[{name:string, email:email}], founded:int?")
# Use schema in LLM prompts for structured data extraction
```

### 🔧 FastAPI Development

```python
from string_schema import string_to_model

# Create model for FastAPI
UserModel = string_to_model("name:string, email:email")

# Use in FastAPI endpoints
@app.post("/users/")
async def create_user(user: UserModel):
    return {"id": 123, "name": user.name, "email": user.email}
```

### 🏗️ Code Generation & Templates

```python
from string_schema import string_to_model_code

# Generate model code
code = string_to_model_code("User", "name:string, email:email")
print(code)
# Output: Complete Pydantic model class as string

# Save to file
with open('user_model.py', 'w') as f:
    f.write(code)
```

### 📋 Configuration Validation

```python
from string_schema import string_to_json_schema

# Validate app configuration
config_schema = string_to_json_schema("database:{host:string, port:int}, debug:bool")
# Use for validating config files
```

## 📚 Documentation

- **[Getting Started](docs/getting-started.md)** - Quick start guide and installation
- **[String Syntax Guide](docs/string-syntax.md)** - Complete syntax reference
- **[API Reference](docs/api-reference.md)** - Full API documentation
- **[Examples](docs/examples.md)** - Practical examples and patterns

## 📋 Example Schemas

Ready-to-use schema examples are available in the `examples/` directory:

```python
# Import example schemas if needed
from string_schema.examples.presets import user_schema, product_schema
from string_schema.examples.recipes import create_ecommerce_product_schema

# Or better yet, use string syntax directly:
user_schema = string_to_json_schema("name:string, email:email, age:int?")
```

## 🧪 Testing

The library includes comprehensive tests covering all functionality:

```bash
# Run tests (requires pytest)
pip install pytest
pytest tests/

# Results: 66 tests passed, 3 skipped (Pydantic tests when not installed)
```

## 🤝 Contributing

Contributions are welcome! The codebase is well-organized and documented:

```
string_schema/
├── core/          # Core functionality (fields, builders, validators)
├── parsing/       # String parsing and syntax
├── integrations/  # Pydantic, JSON Schema, OpenAPI
└── examples/      # Built-in schemas and recipes
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**String Schema** - Making data validation simple, intuitive, and LLM-friendly! 🚀
