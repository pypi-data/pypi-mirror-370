"""
Built-in schema presets for Simple Schema

Contains commonly used schema definitions for typical data structures.
"""

from typing import Any, Dict, List, Optional, Union
import logging

from ..core.fields import SimpleField
from ..core.builders import simple_schema, list_of_objects_schema

logger = logging.getLogger(__name__)


def user_schema(include_email: bool = True, include_phone: bool = False, 
               include_profile: bool = False, include_preferences: bool = False) -> Dict[str, Any]:
    """Generate enhanced user schema with special types"""
    fields = {
        'name': SimpleField('string', 'Full name', min_length=1, max_length=100),
        'age': SimpleField('integer', 'Age in years', min_val=13, max_val=120, required=False)
    }
    
    if include_email:
        fields['email'] = SimpleField('string', 'Email address', format_hint='email')
    
    if include_phone:
        fields['phone'] = SimpleField('string', 'Phone number', format_hint='phone', required=False)
    
    if include_profile:
        fields['bio'] = SimpleField('string', 'Biography', max_length=500, required=False)
        fields['avatar'] = SimpleField('string', 'Avatar URL', format_hint='url', required=False)
    
    if include_preferences:
        fields['theme'] = SimpleField('string', 'UI theme', choices=['light', 'dark'], required=False)
        fields['notifications'] = SimpleField('boolean', 'Email notifications enabled', required=False)
    
    return simple_schema(fields)


def product_schema(include_price: bool = True, include_description: bool = True,
                  include_images: bool = False, include_reviews: bool = False) -> Dict[str, Any]:
    """Generate enhanced product schema"""
    fields = {
        'name': SimpleField('string', 'Product name', min_length=1, max_length=200),
        'category': SimpleField('string', 'Product category', 
                               choices=['electronics', 'clothing', 'books', 'home', 'sports'])
    }
    
    if include_price:
        fields['price'] = SimpleField('number', 'Price', min_val=0)
    
    if include_description:
        fields['description'] = SimpleField('string', 'Product description', 
                                          max_length=1000, required=False)
    
    if include_images:
        # This would need to be handled as a nested array, which is complex
        # For now, we'll represent it as a simple field
        fields['image_urls'] = SimpleField('string', 'Comma-separated image URLs', required=False)
    
    if include_reviews:
        # Similarly, this would be a complex nested structure
        fields['avg_rating'] = SimpleField('number', 'Average rating', min_val=1.0, max_val=5.0, required=False)
        fields['review_count'] = SimpleField('integer', 'Number of reviews', min_val=0, required=False)
    
    return simple_schema(fields)


def contact_schema(include_company: bool = False, include_address: bool = False,
                  include_social: bool = False) -> Dict[str, Any]:
    """Generate enhanced contact schema"""
    fields = {
        'name': SimpleField('string', 'Contact name', min_length=1, max_length=100),
        'email': SimpleField('string', 'Email address', format_hint='email'),
        'phone': SimpleField('string', 'Phone number', format_hint='phone', required=False)
    }
    
    if include_company:
        fields['company'] = SimpleField('string', 'Company name', max_length=200, required=False)
        fields['job_title'] = SimpleField('string', 'Job title', max_length=100, required=False)
    
    if include_address:
        fields['address'] = SimpleField('string', 'Full address', max_length=500, required=False)
        fields['city'] = SimpleField('string', 'City', max_length=100, required=False)
        fields['country'] = SimpleField('string', 'Country', max_length=100, required=False)
    
    if include_social:
        fields['linkedin'] = SimpleField('string', 'LinkedIn URL', format_hint='url', required=False)
        fields['twitter'] = SimpleField('string', 'Twitter URL', format_hint='url', required=False)
        fields['website'] = SimpleField('string', 'Personal website', format_hint='url', required=False)
    
    return simple_schema(fields)


def article_schema(include_summary: bool = True, include_tags: bool = False,
                  include_metadata: bool = False) -> Dict[str, Any]:
    """Generate enhanced article schema"""
    fields = {
        'title': SimpleField('string', 'Article title', min_length=1, max_length=200),
        'content': SimpleField('string', 'Article content', min_length=10)
    }
    
    if include_summary:
        fields['summary'] = SimpleField('string', 'Brief summary', max_length=500, required=False)
    
    if include_tags:
        # Represented as comma-separated for simplicity
        fields['tags'] = SimpleField('string', 'Comma-separated tags', max_length=200, required=False)
    
    if include_metadata:
        fields['author'] = SimpleField('string', 'Author name', max_length=100, required=False)
        fields['published_date'] = SimpleField('string', 'Publication date', format_hint='date', required=False)
        fields['word_count'] = SimpleField('integer', 'Word count', min_val=0, required=False)
    
    return simple_schema(fields)


def event_schema(include_location: bool = True, include_attendees: bool = False) -> Dict[str, Any]:
    """Generate enhanced event schema"""
    fields = {
        'title': SimpleField('string', 'Event title', min_length=1, max_length=200),
        'date': SimpleField('string', 'Event date', format_hint='datetime'),
        'status': SimpleField('string', 'Event status', 
                             choices=['planned', 'active', 'completed', 'cancelled'])
    }
    
    if include_location:
        fields['venue'] = SimpleField('string', 'Venue name', max_length=200, required=False)
        fields['address'] = SimpleField('string', 'Event address', max_length=500, required=False)
        fields['is_online'] = SimpleField('boolean', 'Is online event', required=False)
        fields['meeting_url'] = SimpleField('string', 'Meeting URL', format_hint='url', required=False)
    
    if include_attendees:
        fields['max_attendees'] = SimpleField('integer', 'Maximum attendees', min_val=1, required=False)
        fields['current_attendees'] = SimpleField('integer', 'Current attendee count', min_val=0, required=False)
    
    return simple_schema(fields)


# List versions of schemas
def user_list_schema(**kwargs) -> Dict[str, Any]:
    """Generate schema for array of users"""
    user_fields = {}
    user_base = user_schema(**kwargs)
    
    # Convert properties to SimpleField definitions
    for field_name, field_schema in user_base['properties'].items():
        field_type = field_schema['type']
        required = field_name in user_base.get('required', [])
        
        simple_field = SimpleField(field_type, required=required)
        
        # Copy constraints
        if 'minimum' in field_schema:
            simple_field.min_val = field_schema['minimum']
        if 'maximum' in field_schema:
            simple_field.max_val = field_schema['maximum']
        if 'minLength' in field_schema:
            simple_field.min_length = field_schema['minLength']
        if 'maxLength' in field_schema:
            simple_field.max_length = field_schema['maxLength']
        if 'enum' in field_schema:
            simple_field.choices = field_schema['enum']
        if 'format' in field_schema:
            simple_field.format_hint = field_schema['format']
        
        user_fields[field_name] = simple_field
    
    return list_of_objects_schema(user_fields, "List of users")


def product_list_schema(**kwargs) -> Dict[str, Any]:
    """Generate schema for array of products"""
    return _convert_object_to_list_schema(product_schema(**kwargs), "List of products")


def contact_list_schema(**kwargs) -> Dict[str, Any]:
    """Generate schema for array of contacts"""
    return _convert_object_to_list_schema(contact_schema(**kwargs), "List of contacts")


def article_list_schema(**kwargs) -> Dict[str, Any]:
    """Generate schema for array of articles"""
    return _convert_object_to_list_schema(article_schema(**kwargs), "List of articles")


def event_list_schema(**kwargs) -> Dict[str, Any]:
    """Generate schema for array of events"""
    return _convert_object_to_list_schema(event_schema(**kwargs), "List of events")


def _convert_object_to_list_schema(object_schema: Dict[str, Any], description: str) -> Dict[str, Any]:
    """Helper function to convert object schema to list schema"""
    fields = {}
    
    # Convert properties to SimpleField definitions
    for field_name, field_schema in object_schema['properties'].items():
        field_type = field_schema['type']
        required = field_name in object_schema.get('required', [])
        
        simple_field = SimpleField(field_type, required=required)
        
        # Copy constraints
        if 'minimum' in field_schema:
            simple_field.min_val = field_schema['minimum']
        if 'maximum' in field_schema:
            simple_field.max_val = field_schema['maximum']
        if 'minLength' in field_schema:
            simple_field.min_length = field_schema['minLength']
        if 'maxLength' in field_schema:
            simple_field.max_length = field_schema['maxLength']
        if 'enum' in field_schema:
            simple_field.choices = field_schema['enum']
        if 'format' in field_schema:
            simple_field.format_hint = field_schema['format']
        if 'description' in field_schema:
            simple_field.description = field_schema['description']
        
        fields[field_name] = simple_field
    
    return list_of_objects_schema(fields, description)


# Enhanced utility schemas
def simple_list_schema(item_type: str = 'string', description: str = 'List of items',
                      min_items: Optional[int] = None, max_items: Optional[int] = None) -> Dict[str, Any]:
    """Generate schema for simple arrays with enhanced constraints"""
    from ..core.builders import simple_array_schema
    return simple_array_schema(item_type, description, min_items, max_items)


def key_value_schema(description: str = 'Key-value pairs') -> Dict[str, Any]:
    """Generate schema for flexible key-value objects"""
    return {
        "type": "object",
        "description": description,
        "additionalProperties": {"type": "string"}
    }


def enum_schema(field_name: str, values: List[str], description: str = "") -> Dict[str, Any]:
    """Generate schema for a single enum field"""
    fields = {
        field_name: SimpleField('string', description, choices=values)
    }
    return simple_schema(fields)


def union_schema(field_name: str, types: List[str], description: str = "") -> Dict[str, Any]:
    """Generate schema for a single union field"""
    fields = {
        field_name: SimpleField('string', description, union_types=types)
    }
    return simple_schema(fields)


# Enhanced examples with all new features
ENHANCED_EXAMPLES = {
    "simple_user": {
        "description": "Basic user information with special types",
        "schema": user_schema(include_email=True, include_phone=True),
        "prompt_example": "Extract user: John Doe, 25 years old, john@example.com, phone +1-555-0123"
    },
    
    "product_with_enum": {
        "description": "Product with category enum",
        "schema": product_schema(include_price=True, include_description=True),
        "prompt_example": "Product: iPhone 14, $999, Electronics category, Latest smartphone with advanced features"
    },
    
    "contact_with_social": {
        "description": "Contact with social media links",
        "schema": contact_schema(include_company=True, include_social=True),
        "prompt_example": "Contact: Jane Smith, jane@company.org, works at TechCorp as Developer, LinkedIn: linkedin.com/in/janesmith"
    },
    
    "simple_string_array": {
        "description": "Simple array of strings (FIXED!)",
        "schema": simple_list_schema('string', 'List of tags', max_items=5),
        "prompt_example": "Tags: python, javascript, react, machine-learning, AI"
    },
    
    "email_array": {
        "description": "Array of email addresses",
        "schema": simple_list_schema('string', 'List of emails', min_items=1, max_items=3),
        "prompt_example": "Emails: john@example.com, jane@company.org, admin@website.com"
    },
    
    "user_list": {
        "description": "List of user objects",
        "schema": user_list_schema(include_email=True),
        "prompt_example": "Users: John Doe (25, john@example.com), Jane Smith (30, jane@company.org)"
    },
    
    "enum_status": {
        "description": "Simple enum field",
        "schema": enum_schema('status', ['active', 'inactive', 'pending'], 'User status'),
        "prompt_example": "Status: active"
    },
    
    "union_id": {
        "description": "Union type field",
        "schema": union_schema('id', ['string', 'integer'], 'Flexible ID field'),
        "prompt_example": "ID: abc123 or ID: 12345"
    }
}


def get_examples() -> Dict[str, Dict[str, Any]]:
    """Get all enhanced simple schema examples"""
    return ENHANCED_EXAMPLES.copy()


def print_examples():
    """Print all enhanced simple schema examples"""
    print("🔧 Enhanced Simple Schema Examples:")
    print("=" * 60)
    
    for name, example in ENHANCED_EXAMPLES.items():
        print(f"\n📋 {name.upper().replace('_', ' ')}")
        print(f"Description: {example['description']}")
        print(f"Prompt: {example['prompt_example']}")
        print(f"Schema Preview: {_schema_preview(example['schema'])}")
        print("-" * 40)


def _schema_preview(schema: Dict[str, Any]) -> str:
    """Generate a preview of the schema structure"""
    if schema.get('type') == 'object':
        properties = schema.get('properties', {})
        field_names = list(properties.keys())
        if len(field_names) <= 3:
            return f"Object with fields: {', '.join(field_names)}"
        else:
            return f"Object with {len(field_names)} fields: {', '.join(field_names[:3])}..."
    elif schema.get('type') == 'array':
        items = schema.get('items', {})
        if items.get('type') == 'object':
            item_fields = list(items.get('properties', {}).keys())
            return f"Array of objects with fields: {', '.join(item_fields[:3])}"
        else:
            return f"Array of {items.get('type', 'items')}"
    else:
        return f"{schema.get('type', 'unknown')} type"
