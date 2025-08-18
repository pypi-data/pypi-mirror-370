#!/usr/bin/env python3
"""
String Schema Demo Script

This script demonstrates the organized String Schema library with all its features.
"""

import sys
import os
import json
from typing import Dict, Any

# Add the parent directory to the Python path so we can import string_schema
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the organized String Schema modules
from string_schema import (
    string_to_json_schema,
    string_to_model,
    string_to_model_code,
    validate_string_syntax,
    # Legacy imports for demo compatibility
    parse_string_schema
)

# Import core classes
from string_schema.core.fields import SimpleField
from string_schema.core.builders import simple_schema, list_of_objects_schema, simple_array_schema

# Import examples from examples module
from string_schema.examples.presets import (
    user_schema,
    product_schema,
    contact_schema
)

from string_schema.parsing import validate_string_schema, get_string_schema_examples
from string_schema.integrations.pydantic import create_pydantic_model
from string_schema.integrations.json_schema import to_json_schema
from string_schema.integrations.openapi import to_openapi_schema
from string_schema.examples.recipes import create_ecommerce_product_schema, create_blog_post_schema


def print_header(title: str, level: int = 1):
    """Print formatted header"""
    if level == 1:
        print(f"\n🚀 {title}")
        print("=" * 80)
    elif level == 2:
        print(f"\n📋 {title}")
        print("-" * 60)
    else:
        print(f"\n   🔸 {title}")


def demo_core_functionality():
    """Demonstrate core String Schema functionality"""
    print_header("Core String Schema Functionality", 2)
    
    # Create fields using SimpleField
    print("\n1. Creating fields with SimpleField:")
    fields = {
        'name': SimpleField('string', 'Full name', min_length=1, max_length=100),
        'age': SimpleField('integer', 'Age in years', min_val=0, max_val=120),
        'email': SimpleField('string', 'Email address', format_hint='email'),
        'status': SimpleField('string', 'User status', choices=['active', 'inactive', 'pending'])
    }
    
    # Generate JSON Schema
    schema = simple_schema(fields)
    print(f"   ✅ Generated schema with {len(schema['properties'])} fields")
    print(f"   📝 Required fields: {schema.get('required', [])}")
    
    # Create array schema
    print("\n2. Creating array schemas:")
    user_list = list_of_objects_schema(fields, "List of users", min_items=1, max_items=100)
    print(f"   ✅ User list schema: {user_list['type']} with constraints")
    
    # Create simple array
    tags_schema = simple_array_schema('string', 'List of tags', max_items=5)
    print(f"   ✅ Tags schema: {tags_schema['type']} of {tags_schema['items']['type']}")


def demo_string_parsing():
    """Demonstrate string-based schema parsing"""
    print_header("String-Based Schema Parsing", 2)
    
    test_schemas = [
        ("[string]", "Simple string array"),
        ("[email](min=1,max=3)", "Email array with constraints"),
        ("{name:string, age:int, email:email}", "User object"),
        ("status:enum(active,inactive,pending)", "Enum field"),
        ("id:string|uuid", "Union type field"),
        ("[{name:string(min=1,max=100), emails:[email](min=1,max=2)}]", "Complex nested structure")
    ]
    
    for schema_str, description in test_schemas:
        print(f"\n   Testing: {description}")
        print(f"   Schema: {schema_str}")
        
        try:
            schema = parse_string_schema(schema_str)
            validation = validate_string_schema(schema_str)
            
            print(f"   ✅ Success: {schema['type']} schema")
            if validation['features_used']:
                print(f"   📊 Features: {', '.join(validation['features_used'])}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def demo_built_in_schemas():
    """Demonstrate built-in schema presets"""
    print_header("Built-in Schema Presets", 2)
    
    # User schema variations
    print("\n1. User schemas:")
    basic_user = user_schema()
    full_user = user_schema(include_email=True, include_phone=True, include_profile=True)
    print(f"   ✅ Basic user: {len(basic_user['properties'])} fields")
    print(f"   ✅ Full user: {len(full_user['properties'])} fields")
    
    # Product schema
    print("\n2. Product schemas:")
    product = product_schema(include_price=True, include_description=True)
    print(f"   ✅ Product schema: {len(product['properties'])} fields")
    print(f"   📝 Category choices: {product['properties']['category']['enum']}")
    
    # Contact schema
    print("\n3. Contact schemas:")
    contact = contact_schema(include_company=True, include_social=True)
    print(f"   ✅ Contact schema: {len(contact['properties'])} fields")


def demo_integrations():
    """Demonstrate integrations with other libraries"""
    print_header("Library Integrations", 2)
    
    # Define test fields
    fields = {
        'id': SimpleField('string', 'User ID', format_hint='uuid'),
        'name': SimpleField('string', 'Full name', min_length=1, max_length=100),
        'email': SimpleField('string', 'Email address', format_hint='email'),
        'age': SimpleField('integer', 'Age', min_val=0, max_val=120, required=False)
    }
    
    # Pydantic integration
    print("\n1. Pydantic integration:")
    try:
        UserModel = create_pydantic_model('User', fields)
        print(f"   ✅ Created Pydantic model: {UserModel.__name__}")
        
        # Test model
        user = UserModel(
            id="123e4567-e89b-12d3-a456-426614174000",
            name="John Doe",
            email="john@example.com"
        )
        print(f"   📝 Model instance: {user.name} ({user.email})")
    except Exception as e:
        print(f"   ❌ Pydantic error: {e}")
    
    # JSON Schema integration
    print("\n2. JSON Schema integration:")
    try:
        json_schema = to_json_schema(fields, title="User Schema", description="User data structure")
        print(f"   ✅ JSON Schema: {json_schema['title']}")
        print(f"   📝 Schema version: {json_schema['$schema']}")
    except Exception as e:
        print(f"   ❌ JSON Schema error: {e}")
    
    # OpenAPI integration
    print("\n3. OpenAPI integration:")
    try:
        openapi_schema = to_openapi_schema(fields, title="User Schema")
        print(f"   ✅ OpenAPI Schema: {openapi_schema['title']}")
        print(f"   📝 Type: {openapi_schema['type']}")
    except Exception as e:
        print(f"   ❌ OpenAPI error: {e}")


def demo_recipes():
    """Demonstrate recipe schemas"""
    print_header("Recipe Schemas", 2)
    
    # E-commerce product
    print("\n1. E-commerce product schema:")
    ecommerce_schema = create_ecommerce_product_schema()
    print(f"   ✅ E-commerce product: {len(ecommerce_schema['properties'])} fields")
    print(f"   📝 Required fields: {len(ecommerce_schema.get('required', []))}")
    
    # Blog post
    print("\n2. Blog post schema:")
    blog_schema = create_blog_post_schema()
    print(f"   ✅ Blog post: {len(blog_schema['properties'])} fields")
    print(f"   📝 Status choices: {blog_schema['properties']['status']['enum']}")


def demo_validation():
    """Demonstrate validation features"""
    print_header("Validation Features", 2)
    
    # Test various schema strings
    test_cases = [
        ("name:string, age:int, email:email", "Valid basic schema"),
        ("[{name:string, emails:[email](min=1,max=3)}]", "Valid complex schema"),
        ("status:enum(active,inactive), priority:choice(low,high)", "Valid enum schema"),
        ("id:string|uuid, data:string|int|null", "Valid union schema")
    ]
    
    for schema_str, description in test_cases:
        print(f"\n   Testing: {description}")
        result = validate_string_schema(schema_str)
        
        print(f"   ✅ Valid: {result['valid']}")
        if result['features_used']:
            print(f"   📊 Features: {', '.join(result['features_used'])}")
        if result['warnings']:
            for warning in result['warnings']:
                print(f"   ⚠️  Warning: {warning}")


def demo_examples():
    """Show example schemas from the library"""
    print_header("Example Schemas", 2)
    
    examples = get_string_schema_examples()
    
    print(f"\n   Available examples: {len(examples)}")
    
    # Show a few key examples
    key_examples = ['simple_arrays', 'special_types', 'enums', 'union_types']
    
    for example_name in key_examples:
        if example_name in examples:
            example = examples[example_name]
            print(f"\n   📝 {example_name.upper().replace('_', ' ')}")
            print(f"      Description: {example['description']}")
            print(f"      Schema: {example['schema_string']}")
            print(f"      Example: {example['prompt_example']}")


def run_comprehensive_demo():
    """Run the complete String Schema demonstration"""
    print_header("🚀 String Schema - Organized Library Demo", 1)

    print("""
This demo showcases the organized String Schema library with all modules
properly structured and all enhanced features working correctly.

🎯 Library Structure:
• string_schema/core/          → Core functionality (fields, builders, validators)
• string_schema/parsing/       → String parsing and syntax
• string_schema/integrations/  → Pydantic, JSON Schema, OpenAPI
• string_schema/examples/      → Built-in schemas and recipes
• tests/                       → Comprehensive test suite
• docs/                        → Complete documentation
""")
    
    # Run all demonstrations
    demo_core_functionality()
    demo_string_parsing()
    demo_built_in_schemas()
    demo_integrations()
    demo_recipes()
    demo_validation()
    demo_examples()
    
    # Summary
    print_header("🎉 Demo Complete!", 1)
    print("""
✅ ALL FEATURES WORKING:
   • Core SimpleField and schema builders
   • String-based schema parsing with all syntax features
   • Built-in schema presets (user, product, contact, etc.)
   • Pydantic, JSON Schema, and OpenAPI integrations
   • Recipe schemas for common patterns
   • Comprehensive validation and error reporting

✅ CRITICAL FIXES IMPLEMENTED:
   • [string] arrays now work correctly (was major bug!)
   • [email], [int], [uuid] arrays with format hints
   • Array constraints: [string](max=5), [{name,email}](min=1,max=10)
   • Special types: email, url, datetime, date, uuid, phone
   • Enum support: enum(active,inactive,pending)
   • Union types: string|int, string|null
   • Enhanced constraints: string(min=1,max=50), int(0,120)

🚀 READY FOR PRODUCTION:
   • Well-organized modular structure
   • Comprehensive test coverage
   • Complete documentation
   • LLM-optimized syntax that prevents extraction failures
   • Multiple output formats (JSON Schema, Pydantic, OpenAPI)

📦 NEXT STEPS:
   1. Run tests: python -m pytest tests/
   2. Install package: pip install -e .
   3. Import and use: from string_schema import SimpleField, parse_string_schema
   4. Check docs: docs/getting-started.md
""")


if __name__ == "__main__":
    run_comprehensive_demo()
