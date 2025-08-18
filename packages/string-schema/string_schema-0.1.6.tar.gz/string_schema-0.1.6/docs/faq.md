# Frequently Asked Questions

Common questions about String Schema and their answers.

## 🤔 General Questions

### What is String Schema?

String Schema is a Python library designed to make data schema definition intuitive and LLM-friendly. It allows you to define data structures using human-readable syntax that works well with Large Language Models for data extraction and validation.

### Why use String Schema instead of JSON Schema directly?

- **Simpler syntax**: `name:string, age:int` vs verbose JSON Schema
- **LLM-optimized**: Designed specifically for AI data extraction
- **Multiple outputs**: Generate JSON Schema, Pydantic models, OpenAPI specs
- **Built-in validation**: Comprehensive error checking and suggestions
- **Special types**: Email, URL, datetime with automatic format hints

### Is String Schema production-ready?

Yes! String Schema has:

- ✅ 66 passing tests covering all functionality
- ✅ Clean, modular architecture
- ✅ Comprehensive documentation
- ✅ Optional dependencies (works without Pydantic)
- ✅ Multiple output formats

## 🔧 Technical Questions

### Do I need Pydantic to use String Schema?

No! Pydantic is optional. Simple Schema works without any external dependencies for:

- String schema parsing
- JSON Schema generation
- OpenAPI schema generation
- Built-in validation

Pydantic is only required if you want to generate Pydantic models:

```bash
pip install pydantic  # Only if you need Pydantic models
```

### What's the difference between the string syntax and SimpleField objects?

**String syntax** (recommended for LLMs):

```python
schema = parse_string_schema("name:string, age:int, email:email")
```

**SimpleField objects** (programmatic):

```python
fields = {
    'name': SimpleField('string', 'Name'),
    'age': SimpleField('integer', 'Age'),
    'email': SimpleField('string', 'Email', format_hint='email')
}
schema = string_schema(fields)
```

Both produce the same result. String syntax is more concise and LLM-friendly.

### Can I use String Schema with existing JSON Schema validators?

Yes! String Schema generates standard JSON Schema:

```python
from string_schema.integrations.json_schema import to_json_schema
import jsonschema

# Generate JSON Schema
schema = to_json_schema(fields)

# Use with any JSON Schema validator
jsonschema.validate(data, schema)
```

### How do I handle complex nested structures?

Use proper formatting and break down complex schemas:

```python
# Complex but readable
schema = parse_string_schema("""
{
    user: {
        profile: {
            name: string(min=1, max=100),
            contact: {
                email: email,
                phones: [{
                    type: enum(home, work, mobile),
                    number: phone
                }](max=3)?
            }
        },
        preferences: {
            theme: choice(light, dark),
            notifications: bool
        }?
    }
}
""")
```

## 🎯 Usage Questions

### What special types are supported?

Simple Schema supports these special types with automatic format hints:

- `email` → Email validation
- `url`, `uri` → URL validation
- `datetime` → DateTime parsing
- `date` → Date parsing
- `uuid` → UUID validation
- `phone` → Phone formatting

```python
schema = parse_string_schema("""
email: email,
website: url,
created: datetime,
birthday: date,
id: uuid,
contact: phone
""")
```

### How do I make fields optional?

Add `?` after the type:

```python
schema = parse_string_schema("""
name: string,           # Required
email: email,           # Required
phone: phone?,          # Optional
bio: text(max=500)?     # Optional with constraints
""")
```

### How do I define arrays?

Simple Schema supports various array syntaxes:

```python
# Simple arrays
tags = parse_string_schema("[string]")
scores = parse_string_schema("[int]")

# Arrays with constraints
limited_tags = parse_string_schema("[string](max=5)")
emails = parse_string_schema("[email](min=1, max=3)")

# Object arrays
users = parse_string_schema("[{name:string, email:email}]")

# Alternative syntax
tags_alt = parse_string_schema("tags: array(string, max=5)")
```

### How do I use enums and choices?

Use `enum()`, `choice()`, or `select()` - they all work the same:

```python
schema = parse_string_schema("""
status: enum(active, inactive, pending),
priority: choice(low, medium, high, urgent),
category: select(tech, business, personal)
""")
```

### How do I use union types?

Use the pipe (`|`) operator:

```python
schema = parse_string_schema("""
id: string|uuid,                    # String or UUID
value: string|int|float,            # Multiple types
response: string|null,              # Nullable
data: object|array|null             # Complex unions
""")
```

### How do I add constraints?

Use parentheses with named or positional constraints:

```python
schema = parse_string_schema("""
name: string(min=1, max=100),       # Named constraints
age: int(0, 120),                   # Positional constraints
price: number(min=0),               # Single constraint
description: text(max=1000)         # Text with max length
""")
```

## 🔄 Integration Questions

### How do I generate Pydantic models?

```python
from string_schema.integrations.pydantic import create_pydantic_model

# Define fields
fields = {
    'name': SimpleField('string', 'Name'),
    'email': SimpleField('string', 'Email', format_hint='email')
}

# Create Pydantic model
UserModel = create_pydantic_model('User', fields)

# Use the model
user = UserModel(name="John Doe", email="john@example.com")
```

### How do I generate OpenAPI documentation?

```python
from string_schema.integrations.openapi import to_openapi_schema

# Convert to OpenAPI format
openapi_schema = to_openapi_schema(fields, title="User Schema")

# Use in OpenAPI spec
spec = {
    "openapi": "3.0.3",
    "info": {"title": "My API", "version": "1.0.0"},
    "components": {
        "schemas": {
            "User": openapi_schema
        }
    }
}
```

### Can I use Simple Schema with FastAPI?

Yes! Generate Pydantic models and use them directly:

```python
from fastapi import FastAPI
from string_schema.integrations.pydantic import create_pydantic_model

# Create Pydantic model from String Schema
UserModel = create_pydantic_model('User', user_fields)

app = FastAPI()

@app.post("/users/")
async def create_user(user: UserModel):
    return {"user": user}
```

## 🚀 Performance Questions

### Is Simple Schema fast enough for production?

Yes! Simple Schema is designed for performance:

- Efficient parsing algorithms
- Built-in caching support
- Minimal dependencies
- Optimized for common use cases

For high-performance scenarios, use caching:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_schema(schema_str: str):
    return parse_string_schema(schema_str)
```

### How do I optimize large schemas?

```python
from string_schema.parsing.optimizer import optimize_string_schema, suggest_improvements

# Optimize schema
optimized = optimize_string_schema(large_schema)

# Get optimization suggestions
suggestions = suggest_improvements(large_schema)
```

## 🐛 Troubleshooting Questions

### My array parsing isn't working. What's wrong?

Common array syntax issues:

```python
# ❌ Wrong
"[string"           # Missing closing bracket
"string]"           # Missing opening bracket
"[string(max=5)]"   # Constraints inside brackets

# ✅ Correct
"[string]"          # Simple array
"[string](max=5)"   # Array with constraints
"[{name:string}]"   # Object array
```

### Why aren't my constraints working?

Check constraint syntax:

```python
# ❌ Wrong
"name:string(1,100)"        # Missing constraint names
"age:int(min=0 max=120)"    # Missing comma

# ✅ Correct
"name:string(min=1,max=100)" # Named constraints
"age:int(0,120)"            # Positional constraints
```

### How do I debug parsing issues?

Enable debug logging and use validation:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from string_schema.parsing import validate_string_schema

result = validate_string_schema(your_schema)
print("Valid:", result['valid'])
print("Errors:", result['errors'])
print("Features:", result['features_used'])
```

## 📚 Learning Questions

### Where can I find more examples?

- **README.md**: Progressive examples from simple to complex
- **docs/examples.md**: Real-world use cases and patterns
- **tests/**: Comprehensive test examples
- **examples/demo.py**: Working demonstration script

### How do I contribute to String Schema?

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

The codebase is well-organized and documented for easy contribution.

### What's the roadmap for String Schema?

String Schema is feature-complete for most use cases. Future enhancements might include:

- Additional special types
- More integration options
- Performance optimizations
- Extended validation rules

Check the repository for current development status and feature requests.
