"""
Common schema patterns and recipes for Simple Schema

Contains reusable patterns and helper functions for creating complex schemas.
"""

from typing import Any, Dict, List, Optional, Union
import logging

from ..core.fields import SimpleField
from ..core.builders import simple_schema, list_of_objects_schema, simple_array_schema

logger = logging.getLogger(__name__)


def create_list_schema(item_fields: Dict[str, Union[str, SimpleField]],
                      description: str = "List of items",
                      min_items: Optional[int] = None,
                      max_items: Optional[int] = None) -> Dict[str, Any]:
    """
    Create a schema for a list of objects.
    
    Args:
        item_fields: Field definitions for each item in the list
        description: Description of the list
        min_items: Minimum number of items
        max_items: Maximum number of items
        
    Returns:
        JSON Schema for list of objects
    """
    return list_of_objects_schema(item_fields, description, min_items, max_items)


def create_nested_schema(base_fields: Dict[str, Union[str, SimpleField]],
                        nested_objects: Dict[str, Dict[str, Union[str, SimpleField]]]) -> Dict[str, Any]:
    """
    Create a schema with nested objects.
    
    Args:
        base_fields: Top-level field definitions
        nested_objects: Dictionary of nested object definitions
        
    Returns:
        JSON Schema with nested structure
    """
    all_fields = base_fields.copy()
    
    for nested_name, nested_fields in nested_objects.items():
        # Create a nested object field
        nested_schema = simple_schema(nested_fields)
        # This is a simplified approach - in a full implementation,
        # we'd need to handle this as a proper nested structure
        all_fields[nested_name] = SimpleField('object', f'Nested {nested_name} object')
    
    return simple_schema(all_fields)


def create_enum_schema(field_name: str, 
                      values: List[str],
                      description: str = "",
                      required: bool = True) -> Dict[str, Any]:
    """
    Create a schema with an enum field.
    
    Args:
        field_name: Name of the enum field
        values: List of allowed values
        description: Field description
        required: Whether the field is required
        
    Returns:
        JSON Schema with enum field
    """
    fields = {
        field_name: SimpleField('string', description, required=required, choices=values)
    }
    return simple_schema(fields)


def create_union_schema(field_name: str,
                       types: List[str],
                       description: str = "",
                       required: bool = True) -> Dict[str, Any]:
    """
    Create a schema with a union type field.
    
    Args:
        field_name: Name of the union field
        types: List of allowed types
        description: Field description
        required: Whether the field is required
        
    Returns:
        JSON Schema with union field
    """
    primary_type = types[0] if types else 'string'
    fields = {
        field_name: SimpleField(primary_type, description, required=required, union_types=types)
    }
    return simple_schema(fields)


def create_pagination_schema(item_fields: Dict[str, Union[str, SimpleField]],
                           include_metadata: bool = True) -> Dict[str, Any]:
    """
    Create a paginated response schema.
    
    Args:
        item_fields: Field definitions for each item
        include_metadata: Whether to include pagination metadata
        
    Returns:
        JSON Schema for paginated response
    """
    fields = {
        'items': SimpleField('array', 'List of items')
    }
    
    if include_metadata:
        fields.update({
            'total': SimpleField('integer', 'Total number of items', min_val=0),
            'page': SimpleField('integer', 'Current page number', min_val=1),
            'per_page': SimpleField('integer', 'Items per page', min_val=1),
            'has_next': SimpleField('boolean', 'Whether there are more pages'),
            'has_prev': SimpleField('boolean', 'Whether there are previous pages')
        })
    
    # Note: In a full implementation, we'd properly handle the nested array schema
    return simple_schema(fields)


def create_api_response_schema(data_fields: Dict[str, Union[str, SimpleField]],
                             include_status: bool = True,
                             include_metadata: bool = False) -> Dict[str, Any]:
    """
    Create a standard API response schema.
    
    Args:
        data_fields: Field definitions for the data payload
        include_status: Whether to include status information
        include_metadata: Whether to include response metadata
        
    Returns:
        JSON Schema for API response
    """
    fields = {
        'data': SimpleField('object', 'Response data payload')
    }
    
    if include_status:
        fields.update({
            'success': SimpleField('boolean', 'Whether the request was successful'),
            'message': SimpleField('string', 'Response message', required=False)
        })
    
    if include_metadata:
        fields.update({
            'timestamp': SimpleField('string', 'Response timestamp', format_hint='datetime'),
            'request_id': SimpleField('string', 'Unique request identifier', format_hint='uuid', required=False)
        })
    
    return simple_schema(fields)


def create_error_schema(include_details: bool = True) -> Dict[str, Any]:
    """
    Create a standard error response schema.
    
    Args:
        include_details: Whether to include detailed error information
        
    Returns:
        JSON Schema for error response
    """
    fields = {
        'error': SimpleField('boolean', 'Error indicator', default=True),
        'message': SimpleField('string', 'Error message'),
        'code': SimpleField('string', 'Error code', required=False)
    }
    
    if include_details:
        fields.update({
            'details': SimpleField('string', 'Detailed error information', required=False),
            'timestamp': SimpleField('string', 'Error timestamp', format_hint='datetime'),
            'path': SimpleField('string', 'Request path that caused the error', required=False)
        })
    
    return simple_schema(fields)


def create_search_schema(result_fields: Dict[str, Union[str, SimpleField]],
                        include_facets: bool = False) -> Dict[str, Any]:
    """
    Create a search results schema.
    
    Args:
        result_fields: Field definitions for each search result
        include_facets: Whether to include search facets
        
    Returns:
        JSON Schema for search results
    """
    fields = {
        'query': SimpleField('string', 'Search query'),
        'results': SimpleField('array', 'Search results'),
        'total_results': SimpleField('integer', 'Total number of results', min_val=0),
        'took': SimpleField('number', 'Search time in milliseconds', min_val=0, required=False)
    }
    
    if include_facets:
        fields['facets'] = SimpleField('object', 'Search facets', required=False)
    
    return simple_schema(fields)


def create_audit_schema(entity_fields: Dict[str, Union[str, SimpleField]]) -> Dict[str, Any]:
    """
    Create an audit log schema.
    
    Args:
        entity_fields: Field definitions for the audited entity
        
    Returns:
        JSON Schema for audit log entry
    """
    fields = {
        'id': SimpleField('string', 'Audit log entry ID', format_hint='uuid'),
        'entity_type': SimpleField('string', 'Type of entity being audited'),
        'entity_id': SimpleField('string', 'ID of the audited entity'),
        'action': SimpleField('string', 'Action performed', 
                             choices=['create', 'update', 'delete', 'view']),
        'user_id': SimpleField('string', 'ID of user who performed the action'),
        'timestamp': SimpleField('string', 'When the action occurred', format_hint='datetime'),
        'changes': SimpleField('object', 'What changed', required=False),
        'metadata': SimpleField('object', 'Additional metadata', required=False)
    }
    
    return simple_schema(fields)


def create_notification_schema(include_delivery: bool = True) -> Dict[str, Any]:
    """
    Create a notification schema.
    
    Args:
        include_delivery: Whether to include delivery information
        
    Returns:
        JSON Schema for notification
    """
    fields = {
        'id': SimpleField('string', 'Notification ID', format_hint='uuid'),
        'type': SimpleField('string', 'Notification type',
                           choices=['info', 'warning', 'error', 'success']),
        'title': SimpleField('string', 'Notification title', max_length=200),
        'message': SimpleField('string', 'Notification message', max_length=1000),
        'recipient_id': SimpleField('string', 'Recipient user ID'),
        'created_at': SimpleField('string', 'Creation timestamp', format_hint='datetime'),
        'read': SimpleField('boolean', 'Whether notification has been read', default=False)
    }
    
    if include_delivery:
        fields.update({
            'delivery_method': SimpleField('string', 'How notification was delivered',
                                         choices=['email', 'sms', 'push', 'in_app'], required=False),
            'delivered_at': SimpleField('string', 'Delivery timestamp', 
                                       format_hint='datetime', required=False)
        })
    
    return simple_schema(fields)


def create_file_metadata_schema(include_content_info: bool = True) -> Dict[str, Any]:
    """
    Create a file metadata schema.
    
    Args:
        include_content_info: Whether to include content analysis information
        
    Returns:
        JSON Schema for file metadata
    """
    fields = {
        'filename': SimpleField('string', 'Original filename', max_length=255),
        'size': SimpleField('integer', 'File size in bytes', min_val=0),
        'mime_type': SimpleField('string', 'MIME type', max_length=100),
        'uploaded_at': SimpleField('string', 'Upload timestamp', format_hint='datetime'),
        'uploaded_by': SimpleField('string', 'User who uploaded the file'),
        'checksum': SimpleField('string', 'File checksum (MD5/SHA256)', required=False)
    }
    
    if include_content_info:
        fields.update({
            'width': SimpleField('integer', 'Image width in pixels', min_val=0, required=False),
            'height': SimpleField('integer', 'Image height in pixels', min_val=0, required=False),
            'duration': SimpleField('number', 'Media duration in seconds', min_val=0, required=False),
            'encoding': SimpleField('string', 'File encoding', required=False)
        })
    
    return simple_schema(fields)


def create_settings_schema(setting_groups: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Create a user settings schema.
    
    Args:
        setting_groups: Dictionary mapping group names to setting names
        
    Returns:
        JSON Schema for user settings
    """
    fields = {}
    
    for group_name, setting_names in setting_groups.items():
        for setting_name in setting_names:
            # Create flexible setting fields that can hold various types
            fields[f"{group_name}_{setting_name}"] = SimpleField(
                'string', f'{group_name} {setting_name} setting', required=False
            )
    
    # Add common settings metadata
    fields.update({
        'user_id': SimpleField('string', 'User ID'),
        'updated_at': SimpleField('string', 'Last update timestamp', format_hint='datetime'),
        'version': SimpleField('integer', 'Settings version', min_val=1, default=1)
    })
    
    return simple_schema(fields)


# Recipe combinations for common use cases
def create_ecommerce_product_schema() -> Dict[str, Any]:
    """Create a comprehensive e-commerce product schema"""
    fields = {
        'id': SimpleField('string', 'Product ID', format_hint='uuid'),
        'sku': SimpleField('string', 'Stock keeping unit', max_length=50),
        'name': SimpleField('string', 'Product name', min_length=1, max_length=200),
        'description': SimpleField('string', 'Product description', max_length=2000, required=False),
        'category': SimpleField('string', 'Product category',
                               choices=['electronics', 'clothing', 'books', 'home', 'sports']),
        'price': SimpleField('number', 'Product price', min_val=0),
        'currency': SimpleField('string', 'Price currency', choices=['USD', 'EUR', 'GBP'], default='USD'),
        'in_stock': SimpleField('boolean', 'Whether product is in stock', default=True),
        'stock_quantity': SimpleField('integer', 'Available quantity', min_val=0, required=False),
        'weight': SimpleField('number', 'Product weight in kg', min_val=0, required=False),
        'dimensions': SimpleField('string', 'Product dimensions', required=False),
        'brand': SimpleField('string', 'Product brand', max_length=100, required=False),
        'tags': SimpleField('string', 'Comma-separated tags', required=False),
        'created_at': SimpleField('string', 'Creation timestamp', format_hint='datetime'),
        'updated_at': SimpleField('string', 'Last update timestamp', format_hint='datetime')
    }
    
    return simple_schema(fields)


def create_blog_post_schema() -> Dict[str, Any]:
    """Create a comprehensive blog post schema"""
    fields = {
        'id': SimpleField('string', 'Post ID', format_hint='uuid'),
        'title': SimpleField('string', 'Post title', min_length=1, max_length=200),
        'slug': SimpleField('string', 'URL slug', max_length=200),
        'content': SimpleField('string', 'Post content', min_length=10),
        'excerpt': SimpleField('string', 'Post excerpt', max_length=500, required=False),
        'author_id': SimpleField('string', 'Author ID'),
        'author_name': SimpleField('string', 'Author name', max_length=100),
        'status': SimpleField('string', 'Post status',
                             choices=['draft', 'published', 'archived'], default='draft'),
        'category': SimpleField('string', 'Post category', max_length=100, required=False),
        'tags': SimpleField('string', 'Comma-separated tags', required=False),
        'featured_image': SimpleField('string', 'Featured image URL', format_hint='url', required=False),
        'published_at': SimpleField('string', 'Publication timestamp', format_hint='datetime', required=False),
        'created_at': SimpleField('string', 'Creation timestamp', format_hint='datetime'),
        'updated_at': SimpleField('string', 'Last update timestamp', format_hint='datetime'),
        'view_count': SimpleField('integer', 'Number of views', min_val=0, default=0),
        'comment_count': SimpleField('integer', 'Number of comments', min_val=0, default=0)
    }
    
    return simple_schema(fields)
