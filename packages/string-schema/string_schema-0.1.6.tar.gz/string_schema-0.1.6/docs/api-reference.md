# API Reference

Complete API documentation for String Schema.

## Main Functions

### string_to_json_schema()

```python
def string_to_json_schema(schema_str: str) -> Dict[str, Any]
```

Convert string syntax to JSON Schema.

**Example:**

```python
from string_schema import string_to_json_schema

schema = string_to_json_schema("name:string, email:email, age:int?")
print(schema)  # Complete JSON Schema
```

### string_to_model()

```python
def string_to_model(schema_str: str, model_name: str = "GeneratedModel") -> Type[BaseModel]
```

Convert string syntax to Pydantic model.

**Example:**

```python
from string_schema import string_to_model

UserModel = string_to_model("name:string, email:email, active:bool")
user = UserModel(name="Alice", email="alice@example.com", active=True)
```

### string_to_model_code()

```python
def string_to_model_code(model_name: str, schema_str: str) -> str
```

Generate Pydantic model code as string.

**Example:**

```python
from string_schema import string_to_model_code

code = string_to_model_code("User", "name:string, email:email")
print(code)  # Complete Pydantic model class code
```

### Schema Builders

#### string_schema()

```python
def string_schema(fields: Dict[str, Union[str, SimpleField]]) -> Dict[str, Any]
```

Generate JSON Schema from field definitions.

**Example:**

```python
fields = {
    'name': SimpleField('string', 'Full name'),
    'age': SimpleField('integer', 'Age', min_val=0)
}
schema = string_schema(fields)
```

#### list_of_objects_schema()

```python
def list_of_objects_schema(item_fields: Dict[str, Union[str, SimpleField]],
                          description: str = "List of objects",
                          min_items: Optional[int] = None,
                          max_items: Optional[int] = None) -> Dict[str, Any]
```

Generate schema for array of objects.

#### simple_array_schema()

```python
def simple_array_schema(item_type: str = 'string', description: str = 'Array of items',
                       min_items: Optional[int] = None, max_items: Optional[int] = None,
                       format_hint: Optional[str] = None) -> Dict[str, Any]
```

Generate schema for simple arrays.

#### quick_pydantic_model()

```python
def quick_pydantic_model(name: str, fields: Dict[str, Union[str, SimpleField]]) -> Type[BaseModel]
```

Create Pydantic model from field definitions.

### string_to_openapi()

```python
def string_to_openapi(schema_str: str) -> Dict[str, Any]
```

Convert string syntax to OpenAPI schema.

**Example:**

```python
from string_schema import string_to_openapi

openapi_schema = string_to_openapi("name:string, email:email")
print(openapi_schema)  # OpenAPI-compatible schema
```

## Data Validation Functions

### validate_to_dict()

```python
def validate_to_dict(data: Dict[str, Any], schema_str: str) -> Dict[str, Any]
```

Validate data against schema and return clean dictionary.

**Example:**

```python
from string_schema import validate_to_dict

raw_data = {"name": "John", "email": "john@example.com", "age": "25"}
clean_data = validate_to_dict(raw_data, "name:string, email:email, age:int?")
print(clean_data)  # {"name": "John", "email": "john@example.com", "age": 25}
```

### validate_to_model()

```python
def validate_to_model(data: Dict[str, Any], schema_str: str) -> BaseModel
```

Validate data against schema and return Pydantic model instance.

**Example:**

```python
from string_schema import validate_to_model

raw_data = {"name": "John", "email": "john@example.com", "active": True}
user_model = validate_to_model(raw_data, "name:string, email:email, active:bool")
print(user_model.name)  # "John" - Full type safety
```

### validate_string_syntax()

```python
def validate_string_syntax(schema_str: str) -> Dict[str, Any]
```

Validate string schema syntax and return detailed feedback.

**Example:**

```python
from string_schema import validate_string_syntax

result = validate_string_syntax("name:string, email:email, age:int?")
print(f"Valid: {result['valid']}")  # True
print(f"Features: {result['features_used']}")  # ['basic_types', 'optional_fields']
```

## Reverse Conversion Functions

### model_to_string()

```python
def model_to_string(model: Type[BaseModel]) -> str
```

Convert Pydantic model back to string syntax.

**Example:**

```python
from string_schema import string_to_model, model_to_string

UserModel = string_to_model("name:string, email:email, active:bool")
schema_string = model_to_string(UserModel)
print(schema_string)  # "name:string, email:email, active:bool"
```

### json_schema_to_string()

```python
def json_schema_to_string(json_schema: Dict[str, Any]) -> str
```

Convert JSON Schema to string syntax.

**Example:**

```python
from string_schema import json_schema_to_string

json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "email"]
}
simple_syntax = json_schema_to_string(json_schema)
print(simple_syntax)  # "name:string, email:email"
```

## Function Decorators

### @returns_dict()

```python
def returns_dict(schema_str: str)
```

Decorator that validates function return values to clean dictionaries.

**Example:**

```python
from string_schema import returns_dict

@returns_dict("id:string, name:string, active:bool")
def create_user(name):
    return {"id": "123", "name": name, "active": True, "extra": "ignored"}
    # Returns: {"id": "123", "name": "Alice", "active": True}
    # Note: 'extra' field filtered out
```

### @returns_model()

```python
def returns_model(schema_str: str)
```

Decorator that validates function return values to Pydantic models.

**Example:**

```python
from string_schema import returns_model

@returns_model("name:string, email:string")
def process_user(raw_input):
    return {"name": raw_input["name"], "email": raw_input["email"], "junk": "data"}
    # Returns: UserModel(name="Bob", email="bob@test.com")
    # Note: Returns typed Pydantic model, 'junk' field filtered out
```

## String Syntax Reference

### Basic Types

- `string`, `int`, `number`, `bool` → Basic data types
- `email`, `url`, `datetime`, `date`, `uuid`, `phone` → Special validated types

### Field Modifiers

- `field_name:type` → Required field
- `field_name:type?` → Optional field
- `field_name:type(constraints)` → Field with validation

### Common Patterns

- `string(min=1,max=100)` → Length constraints
- `int(0,120)` → Range constraints
- `[string]` → Simple arrays
- `[{name:string, email:email}]` → Object arrays
- `status:enum(active,inactive)` → Enum values
- `id:string|uuid` → Union types

### Examples

```python
# String schema
"name:string, email:email, age:int?"

# With constraints
"name:string(min=1,max=100), age:int(0,120), email:email"

# Arrays and objects
"tags:[string], user:{name:string, email:email}"

# Enums and unions
"status:enum(active,inactive), id:string|uuid"
```

## Type Hints

String Schema is fully typed:

```python
from typing import Dict, List, Any, Optional, Union, Type
from pydantic import BaseModel
```

## Supported Types

### Basic Types

- `string`, `int`, `number`, `bool`

### Special Types

- `email`, `url`, `datetime`, `date`, `uuid`, `phone`

### Modifiers

- `?` → Optional field
- `(constraints)` → Validation constraints
- `|` → Union types
- `[]` → Arrays
- `{}` → Objects
- `enum()` → Enumerated values

This covers the main String Schema API. For more examples, see the [Examples](examples.md) documentation.
