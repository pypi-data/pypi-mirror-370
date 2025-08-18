# Advanced Usage

This guide covers advanced patterns, optimization techniques, and complex use cases for Simple Schema.

## 🏗️ Complex Schema Patterns

### Enterprise User Management

```python
from string_schema import parse_string_schema

# Complete user management system
user_system_schema = parse_string_schema("""
[{
    id:string|uuid,
    profile:{
        username:string(min=3, max=30),
        email:email,
        first_name:string(min=1, max=50),
        last_name:string(min=1, max=50),
        phone:phone?,
        avatar:url?,
        bio:text(max=500)?,
        social:{
            linkedin:url?,
            twitter:url?,
            github:url?,
            website:url?
        }?
    },
    account:{
        status:enum(active, inactive, suspended, pending_verification),
        role:enum(admin, moderator, user, guest),
        permissions:[string]?,
        email_verified:bool,
        phone_verified:bool?,
        two_factor_enabled:bool,
        last_login:datetime?,
        login_count:int(min=0),
        failed_login_attempts:int(min=0, max=10)
    },
    preferences:{
        theme:choice(light, dark, auto),
        language:string(min=2, max=5),
        timezone:string?,
        notifications:{
            email:bool,
            sms:bool?,
            push:bool,
            marketing:bool?
        }
    }?,
    metadata:{
        created_at:datetime,
        updated_at:datetime,
        created_by:string?,
        last_modified_by:string?,
        tags:[string](max=10)?,
        notes:text?
    }
}](min=1, max=1000)
""")
```

### E-commerce Platform

```python
# Complete e-commerce product schema
ecommerce_schema = parse_string_schema("""
{
    product:{
        id:uuid,
        name:string(min=1, max=200),
        slug:string(min=1, max=200),
        description:text(max=5000)?,
        short_description:text(max=500)?,
        price:{
            amount:number(min=0),
            currency:enum(USD, EUR, GBP, JPY, CAD),
            tax_inclusive:bool?
        },
        category:{
            id:uuid,
            name:string,
            path:[string],
            attributes:[{
                name:string,
                value:string,
                type:enum(text, number, boolean, select)
            }]?
        },
        inventory:{
            sku:string(min=1, max=100),
            in_stock:bool,
            quantity:int(min=0)?,
            low_stock_threshold:int(min=0)?,
            warehouse_locations:[{
                id:string,
                name:string,
                quantity:int(min=0)
            }]?
        },
        media:{
            images:[{
                url:url,
                alt_text:string(max=200)?,
                is_primary:bool?,
                sort_order:int(min=0)?
            }](max=20)?,
            videos:[{
                url:url,
                thumbnail:url?,
                duration:int(min=0)?,
                type:enum(product_demo, unboxing, review)
            }](max=5)?
        },
        seo:{
            meta_title:string(max=60)?,
            meta_description:string(max=160)?,
            keywords:[string](max=20)?,
            canonical_url:url?
        }?,
        reviews:{
            average_rating:number(min=0, max=5)?,
            total_reviews:int(min=0)?,
            rating_distribution:{
                five_star:int(min=0)?,
                four_star:int(min=0)?,
                three_star:int(min=0)?,
                two_star:int(min=0)?,
                one_star:int(min=0)?
            }?
        }?
    },
    variants:[{
        id:uuid,
        name:string,
        sku:string,
        price_adjustment:number?,
        attributes:[{
            name:string,
            value:string
        }],
        inventory:{
            quantity:int(min=0),
            in_stock:bool
        }
    }]?,
    shipping:{
        weight:number(min=0)?,
        dimensions:{
            length:number(min=0)?,
            width:number(min=0)?,
            height:number(min=0)?
        }?,
        shipping_class:string?,
        free_shipping:bool?
    }?,
    metadata:{
        created_at:datetime,
        updated_at:datetime,
        created_by:string,
        status:enum(draft, active, inactive, discontinued),
        featured:bool?,
        tags:[string](max=30)?
    }
}
""")
```

## 🔄 Schema Composition and Reuse

### Building Modular Schemas

```python
from string_schema import SimpleField, simple_schema
from string_schema.examples.recipes import create_api_response_schema

# Define reusable components
address_fields = {
    'street': SimpleField('string', 'Street address', max_length=200),
    'city': SimpleField('string', 'City', max_length=100),
    'state': SimpleField('string', 'State/Province', max_length=100),
    'postal_code': SimpleField('string', 'Postal code', max_length=20),
    'country': SimpleField('string', 'Country code', min_length=2, max_length=3)
}

contact_fields = {
    'email': SimpleField('string', 'Email address', format_hint='email'),
    'phone': SimpleField('string', 'Phone number', format_hint='phone', required=False),
    'website': SimpleField('string', 'Website URL', format_hint='url', required=False)
}

# Compose larger schemas
company_fields = {
    'name': SimpleField('string', 'Company name', min_length=1, max_length=200),
    'industry': SimpleField('string', 'Industry', choices=[
        'technology', 'healthcare', 'finance', 'education', 'retail', 'manufacturing'
    ]),
    'size': SimpleField('string', 'Company size', choices=[
        'startup', 'small', 'medium', 'large', 'enterprise'
    ]),
    'founded_year': SimpleField('integer', 'Founded year', min_val=1800, max_val=2024, required=False)
}

# Combine all components
full_company_schema = simple_schema({
    **company_fields,
    'address': simple_schema(address_fields),
    'contact': simple_schema(contact_fields)
})
```

## 🚀 Performance Optimization

### Schema Caching

```python
from functools import lru_cache
from string_schema import parse_string_schema

@lru_cache(maxsize=128)
def get_cached_schema(schema_string: str):
    """Cache parsed schemas for better performance"""
    return parse_string_schema(schema_string)

# Use cached schemas for frequently used patterns
user_schema = get_cached_schema("name:string, email:email, age:int?")
product_schema = get_cached_schema("name:string, price:number(min=0), category:enum(a,b,c)")
```

### Batch Validation

```python
from string_schema.parsing import validate_string_schema
from string_schema.core.validators import validate_schema

def validate_multiple_schemas(schema_strings: list) -> dict:
    """Validate multiple schemas efficiently"""
    results = {}

    for i, schema_str in enumerate(schema_strings):
        try:
            schema = parse_string_schema(schema_str)
            validation = validate_string_schema(schema_str)

            results[f"schema_{i}"] = {
                'valid': validation['valid'],
                'features': validation['features_used'],
                'field_count': len(validation['parsed_fields']),
                'warnings': validation['warnings']
            }
        except Exception as e:
            results[f"schema_{i}"] = {
                'valid': False,
                'error': str(e)
            }

    return results
```

## 🔍 Advanced Validation Patterns

### Custom Validation Rules

```python
from string_schema.parsing.optimizer import suggest_improvements

def enhanced_schema_validation(schema_str: str) -> dict:
    """Enhanced validation with suggestions"""
    validation = validate_string_schema(schema_str)
    suggestions = suggest_improvements(schema_str)

    # Add custom business logic validation
    custom_warnings = []

    # Check for common anti-patterns
    if 'password' in schema_str.lower() and 'string' in schema_str:
        if 'min=' not in schema_str:
            custom_warnings.append("Password fields should have minimum length constraints")

    if 'email' in schema_str and '@' in schema_str:
        custom_warnings.append("Use 'email' type instead of string for email fields")

    # Check for missing optional markers
    field_count = len(validation.get('parsed_fields', {}))
    if field_count > 5 and '?' not in schema_str:
        custom_warnings.append("Consider marking some fields as optional for flexibility")

    return {
        **validation,
        'suggestions': suggestions,
        'custom_warnings': custom_warnings
    }
```

### Schema Evolution and Migration

```python
def migrate_schema_v1_to_v2(old_schema_str: str) -> str:
    """Migrate schema from v1 to v2 format"""
    # Example migration: old format used 'str' instead of 'string'
    migrated = old_schema_str.replace(':str', ':string')
    migrated = migrated.replace(':int', ':integer')

    # Add new required fields
    if 'created_at' not in migrated:
        migrated = migrated.rstrip('}') + ', created_at:datetime}'

    return migrated

def validate_schema_compatibility(old_schema: str, new_schema: str) -> dict:
    """Check if new schema is backward compatible"""
    old_validation = validate_string_schema(old_schema)
    new_validation = validate_string_schema(new_schema)

    old_fields = set(old_validation.get('parsed_fields', {}).keys())
    new_fields = set(new_validation.get('parsed_fields', {}).keys())

    removed_fields = old_fields - new_fields
    added_fields = new_fields - old_fields

    return {
        'compatible': len(removed_fields) == 0,
        'removed_fields': list(removed_fields),
        'added_fields': list(added_fields),
        'breaking_changes': len(removed_fields) > 0
    }
```

## 🔗 Integration Patterns

### API Documentation Generation

```python
from string_schema.integrations.openapi import (
    create_openapi_path_item,
    create_openapi_parameter,
    generate_openapi_spec
)

def generate_api_docs(endpoints: dict) -> dict:
    """Generate OpenAPI documentation from Simple Schema definitions"""
    paths = {}
    components = {}

    for endpoint_path, config in endpoints.items():
        # Create path item
        path_item = create_openapi_path_item(
            method=config['method'],
            summary=config['summary'],
            description=config['description'],
            request_fields=config.get('request_schema'),
            response_fields=config.get('response_schema'),
            parameters=config.get('parameters', [])
        )
        paths[endpoint_path] = path_item

        # Add to components if reusable
        if config.get('component_name'):
            components[config['component_name']] = config['response_schema']

    return generate_openapi_spec(
        title="API Documentation",
        version="1.0.0",
        description="Generated from Simple Schema",
        paths=paths,
        components={'schemas': components}
    )
```

### Database Schema Generation

```python
def generate_sql_ddl(schema_str: str, table_name: str) -> str:
    """Generate SQL DDL from Simple Schema (basic example)"""
    schema = parse_string_schema(schema_str)

    if schema['type'] != 'object':
        raise ValueError("Only object schemas can be converted to SQL tables")

    columns = []

    for field_name, field_def in schema['properties'].items():
        sql_type = _map_to_sql_type(field_def)
        nullable = "NULL" if field_name not in schema.get('required', []) else "NOT NULL"
        columns.append(f"    {field_name} {sql_type} {nullable}")

    return f"""CREATE TABLE {table_name} (
{',\\n'.join(columns)}
);"""

def _map_to_sql_type(field_def: dict) -> str:
    """Map JSON Schema types to SQL types"""
    type_mapping = {
        'string': 'VARCHAR(255)',
        'integer': 'INTEGER',
        'number': 'DECIMAL(10,2)',
        'boolean': 'BOOLEAN'
    }

    field_type = field_def.get('type', 'string')

    # Handle string length constraints
    if field_type == 'string':
        max_length = field_def.get('maxLength', 255)
        return f'VARCHAR({max_length})'

    return type_mapping.get(field_type, 'TEXT')
```

## 🧪 Testing Advanced Schemas

### Property-Based Testing

```python
import hypothesis
from hypothesis import strategies as st
from string_schema import parse_string_schema

@hypothesis.given(
    name=st.text(min_size=1, max_size=100),
    age=st.integers(min_value=0, max_value=120),
    email=st.emails()
)
def test_user_schema_with_generated_data(name, age, email):
    """Test schema with property-based testing"""
    schema = parse_string_schema("name:string(min=1,max=100), age:int(0,120), email:email")

    # Test that schema can handle generated data
    test_data = {
        'name': name,
        'age': age,
        'email': email
    }

    # Validate against schema (would need JSON Schema validator)
    assert len(test_data['name']) >= 1
    assert len(test_data['name']) <= 100
    assert 0 <= test_data['age'] <= 120
    assert '@' in test_data['email']
```

This advanced usage guide demonstrates how Simple Schema can be used for complex, real-world applications with proper patterns for composition, optimization, and integration.
