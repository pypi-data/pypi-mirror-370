# Troubleshooting

Common issues and solutions when using String Schema.

## 🐛 Common Issues

### Array Parsing Issues

**Problem**: Arrays not parsing correctly

```python
# This might fail
schema = parse_string_schema("[string")  # Missing closing bracket
```

**Solution**: Ensure proper bracket syntax

```python
# Correct syntax
schema = parse_string_schema("[string]")           # Simple array
schema = parse_string_schema("[string](max=5)")    # Array with constraints
schema = parse_string_schema("[{name:string}]")    # Object array
```

### Constraint Syntax Errors

**Problem**: Constraints not being recognized

```python
# These might not work as expected
schema = parse_string_schema("name:string(1,100)")     # Missing constraint names
schema = parse_string_schema("age:int(min=0 max=120)") # Missing comma
```

**Solution**: Use proper constraint syntax

```python
# Correct constraint syntax
schema = parse_string_schema("name:string(min=1,max=100)")  # Named constraints
schema = parse_string_schema("age:int(0,120)")             # Positional constraints
schema = parse_string_schema("price:number(min=0)")        # Single constraint
```

### Special Type Format Issues

**Problem**: Special types not getting proper format hints

```python
# This creates a string field without email format
schema = parse_string_schema("contact:string")
```

**Solution**: Use special type names

```python
# This creates a string field with email format
schema = parse_string_schema("contact:email")
schema = parse_string_schema("website:url")
schema = parse_string_schema("created:datetime")
```

### Enum Syntax Problems

**Problem**: Enum values not being recognized

```python
# These might fail
schema = parse_string_schema("status:enum active,inactive")  # Missing parentheses
schema = parse_string_schema("status:enum(active inactive)") # Missing commas
```

**Solution**: Use proper enum syntax

```python
# Correct enum syntax
schema = parse_string_schema("status:enum(active,inactive,pending)")
schema = parse_string_schema("priority:choice(low,medium,high)")
schema = parse_string_schema("category:select(tech,business,personal)")
```

### Union Type Issues

**Problem**: Union types not working

```python
# This might not create a proper union
schema = parse_string_schema("id:string or uuid")  # Wrong syntax
```

**Solution**: Use pipe (|) for unions

```python
# Correct union syntax
schema = parse_string_schema("id:string|uuid")
schema = parse_string_schema("value:string|int|float")
schema = parse_string_schema("response:string|null")
```

## 🔧 Import and Installation Issues

### Pydantic Import Errors

**Problem**: ImportError when using Pydantic features

```
ImportError: Pydantic is required for create_pydantic_model
```

**Solution**: Install Pydantic or use alternative methods

```bash
# Install Pydantic
pip install pydantic

# Or use JSON Schema instead
from string_schema.integrations.json_schema import to_json_schema
schema = to_json_schema(fields)
```

### Module Not Found Errors

**Problem**: Cannot import String Schema modules

```
ModuleNotFoundError: No module named 'string_schema'
```

**Solution**: Check installation and Python path

```bash
# Reinstall the package
pip uninstall string-schema
pip install string-schema

# For development installation
pip install -e .

# Check if installed
pip list | grep string-schema
```

## 🧪 Validation and Testing Issues

### Schema Validation Failures

**Problem**: Schema validation returns false positives

```python
result = validate_string_schema("name:string, age:int")
# result['valid'] might be False unexpectedly
```

**Solution**: Check validation details

```python
from string_schema.parsing import validate_string_schema

result = validate_string_schema("name:string, age:int")

if not result['valid']:
    print("Errors:", result['errors'])
    print("Warnings:", result['warnings'])

# Check what features were detected
print("Features used:", result['features_used'])
print("Parsed fields:", result['parsed_fields'])
```

### Complex Schema Parsing

**Problem**: Complex nested schemas fail to parse

```python
# This might be too complex and fail
complex_schema = """
{user:{profile:{name:string,contact:{email:email,phones:[{type:enum(home,work),number:phone}]}}}}
"""
```

**Solution**: Break down complex schemas or add whitespace

```python
# Add proper formatting and spacing
complex_schema = """
{
    user: {
        profile: {
            name: string,
            contact: {
                email: email,
                phones: [{
                    type: enum(home, work),
                    number: phone
                }]
            }
        }
    }
}
"""

# Or build incrementally
from string_schema import SimpleField, string_schema

phone_fields = {
    'type': SimpleField('string', choices=['home', 'work']),
    'number': SimpleField('string', format_hint='phone')
}

contact_fields = {
    'email': SimpleField('string', format_hint='email'),
    'phones': list_of_objects_schema(phone_fields)
}

# Continue building up...
```

## 🔄 Integration Issues

### JSON Schema Compatibility

**Problem**: Generated JSON Schema not compatible with validators

```python
schema = string_schema(fields)
# Schema might not validate with external JSON Schema validators
```

**Solution**: Use JSON Schema integration module

```python
from string_schema.integrations.json_schema import (
    to_json_schema,
    validate_json_schema_compliance
)

# Generate compliant JSON Schema
schema = to_json_schema(fields, title="My Schema")

# Validate compliance
compliance = validate_json_schema_compliance(schema)
if not compliance['valid']:
    print("Compliance issues:", compliance['errors'])
```

### OpenAPI Integration Problems

**Problem**: OpenAPI schema generation fails

```python
# Might fail with complex union types
fields_with_complex_unions = {
    'data': SimpleField('string', union_types=['string', 'int', 'bool', 'null'])
}
```

**Solution**: Simplify unions or use OpenAPI-specific methods

```python
from string_schema.integrations.openapi import (
    to_openapi_schema,
    validate_openapi_compatibility
)

# Check compatibility first
compatibility = validate_openapi_compatibility(fields)
if not compatibility['compatible']:
    print("OpenAPI warnings:", compatibility['warnings'])

# Generate OpenAPI schema
openapi_schema = to_openapi_schema(fields)
```

## 🚀 Performance Issues

### Slow Schema Parsing

**Problem**: Large schemas take too long to parse

```python
# This might be slow for very large schemas
huge_schema = "field1:string, field2:string, ..." * 1000
```

**Solution**: Use caching and optimization

```python
from functools import lru_cache
from string_schema.parsing.optimizer import optimize_string_schema

@lru_cache(maxsize=128)
def cached_parse(schema_str: str):
    return parse_string_schema(schema_str)

# Optimize schema first
optimized = optimize_string_schema(huge_schema)
schema = cached_parse(optimized)
```

### Memory Usage with Large Schemas

**Problem**: High memory usage with complex schemas

```python
# Creating many large schemas
schemas = [parse_string_schema(large_schema) for _ in range(1000)]
```

**Solution**: Use generators and cleanup

```python
def schema_generator(schema_strings):
    for schema_str in schema_strings:
        yield parse_string_schema(schema_str)

# Process one at a time
for schema in schema_generator(schema_strings):
    process_schema(schema)
    # Schema is garbage collected after each iteration
```

## 🔍 Debugging Tips

### Enable Debug Logging

```python
import logging

# Enable debug logging for String Schema
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('string_schema')
logger.setLevel(logging.DEBUG)

# Now parsing will show debug information
schema = parse_string_schema("name:string, age:int")
```

### Inspect Parsed Results

```python
from string_schema.parsing import validate_string_schema

# Get detailed parsing information
result = validate_string_schema("""
[{
    name: string(min=1, max=100),
    emails: [email](min=1, max=3),
    role: enum(admin, user, guest)
}](min=1, max=20)
""")

print("Validation result:")
print(f"  Valid: {result['valid']}")
print(f"  Features used: {result['features_used']}")
print(f"  Field count: {len(result['parsed_fields'])}")
print(f"  Parsed fields: {list(result['parsed_fields'].keys())}")

if result['warnings']:
    print("  Warnings:")
    for warning in result['warnings']:
        print(f"    - {warning}")

if result['errors']:
    print("  Errors:")
    for error in result['errors']:
        print(f"    - {error}")
```

### Test Individual Components

```python
# Test individual parsing functions
from string_schema.parsing.string_parser import (
    _normalize_type_name,
    _parse_enum_values,
    _parse_type_definition
)

# Test type normalization
print(_normalize_type_name('str'))  # Should return 'string'
print(_normalize_type_name('int'))  # Should return 'integer'

# Test enum parsing
print(_parse_enum_values('enum(active,inactive)'))  # Should return ['active', 'inactive']

# Test constraint parsing
print(_parse_type_definition('string(min=1,max=100)'))  # Should return type and constraints
```

## 📞 Getting Help

If you're still having issues:

1. **Check the test suite**: Look at `tests/` for examples of correct usage
2. **Review examples**: Check `examples/` and `docs/examples.md` for patterns
3. **Enable logging**: Use debug logging to see what's happening internally
4. **Simplify**: Break complex schemas into smaller parts to isolate issues
5. **Validate step by step**: Use validation functions to check each part

## 🐛 Reporting Bugs

When reporting issues, please include:

1. **Simple Schema version**: `pip show simple-schema`
2. **Python version**: `python --version`
3. **Minimal example**: Smallest code that reproduces the issue
4. **Expected behavior**: What you expected to happen
5. **Actual behavior**: What actually happened
6. **Error messages**: Full error traceback if applicable

This helps maintainers quickly identify and fix issues.
