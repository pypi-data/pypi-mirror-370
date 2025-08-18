"""
OpenAPI integration for Simple Schema

Contains functions for creating OpenAPI schema definitions from Simple Schema.
"""

from typing import Any, Dict, List, Union, Optional
import logging

from ..core.fields import SimpleField
from .json_schema import to_json_schema, convert_to_openapi_schema

logger = logging.getLogger(__name__)


def to_openapi_schema(fields: Dict[str, Union[str, SimpleField]],
                     title: str = "Generated Schema",
                     description: str = "",
                     version: str = "1.0.0") -> Dict[str, Any]:
    """
    Convert Simple Schema fields to OpenAPI 3.0 schema format.
    
    Args:
        fields: Dictionary of field definitions
        title: Schema title
        description: Schema description
        version: Schema version
        
    Returns:
        OpenAPI 3.0 compatible schema
    """
    # First convert to JSON Schema
    json_schema = to_json_schema(fields, title, description)
    
    # Then convert to OpenAPI format
    openapi_schema = convert_to_openapi_schema(json_schema)
    
    # Add OpenAPI specific metadata
    if version:
        openapi_schema["version"] = version
    
    return openapi_schema


def create_openapi_component(name: str, 
                           fields: Dict[str, Union[str, SimpleField]],
                           description: str = "") -> Dict[str, Any]:
    """
    Create an OpenAPI component schema.
    
    Args:
        name: Component name
        fields: Dictionary of field definitions
        description: Component description
        
    Returns:
        OpenAPI component definition
    """
    schema = to_openapi_schema(fields, name, description)
    
    return {
        name: schema
    }


def create_openapi_request_body(fields: Dict[str, Union[str, SimpleField]],
                               description: str = "Request body",
                               content_type: str = "application/json",
                               required: bool = True) -> Dict[str, Any]:
    """
    Create OpenAPI request body definition.
    
    Args:
        fields: Dictionary of field definitions
        description: Request body description
        content_type: Content type (default: application/json)
        required: Whether request body is required
        
    Returns:
        OpenAPI request body definition
    """
    schema = to_openapi_schema(fields)
    
    return {
        "description": description,
        "required": required,
        "content": {
            content_type: {
                "schema": schema
            }
        }
    }


def string_to_openapi(schema_str: str, title: str = "Generated Schema",
                     description: str = "", version: str = "1.0.0") -> Dict[str, Any]:
    """
    Create OpenAPI schema directly from string syntax.

    Args:
        schema_str: String schema definition (e.g., "name:string, email:email")
        title: Schema title
        description: Schema description
        version: Schema version

    Returns:
        OpenAPI 3.0 compatible schema dictionary

    Example:
        openapi_schema = string_to_openapi("name:string, email:email", title="User Schema")
    """
    # Import here to avoid circular imports
    from ..parsing.string_parser import parse_string_schema
    from .json_schema import convert_to_openapi_schema

    # Convert string to JSON Schema, then to OpenAPI
    json_schema = parse_string_schema(schema_str)
    return convert_to_openapi_schema(json_schema)


# Reverse conversion functions
def openapi_to_string(openapi_schema: Dict[str, Any]) -> str:
    """
    Convert OpenAPI schema to Simple Schema string syntax.

    Args:
        openapi_schema: OpenAPI schema dictionary

    Returns:
        String representation in Simple Schema syntax

    Example:
        openapi_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        schema_str = openapi_to_string(openapi_schema)
        # Returns: "name:string"
    """
    from .reverse import openapi_to_string as _openapi_to_string
    return _openapi_to_string(openapi_schema)


def openapi_to_json_schema(openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert OpenAPI schema to JSON Schema.

    Args:
        openapi_schema: OpenAPI schema dictionary

    Returns:
        JSON Schema dictionary

    Example:
        openapi_schema = {"type": "string", "format": "email"}
        json_schema = openapi_to_json_schema(openapi_schema)
    """
    from .reverse import openapi_to_json_schema as _openapi_to_json_schema
    return _openapi_to_json_schema(openapi_schema)


def create_openapi_response(fields: Dict[str, Union[str, SimpleField]],
                          description: str = "Successful response",
                          status_code: str = "200",
                          content_type: str = "application/json") -> Dict[str, Any]:
    """
    Create OpenAPI response definition.
    
    Args:
        fields: Dictionary of field definitions
        description: Response description
        status_code: HTTP status code
        content_type: Content type (default: application/json)
        
    Returns:
        OpenAPI response definition
    """
    schema = to_openapi_schema(fields)
    
    return {
        status_code: {
            "description": description,
            "content": {
                content_type: {
                    "schema": schema
                }
            }
        }
    }


def create_openapi_parameter(field_name: str,
                           field: Union[str, SimpleField],
                           location: str = "query",
                           description: str = "",
                           required: bool = False) -> Dict[str, Any]:
    """
    Create OpenAPI parameter definition.
    
    Args:
        field_name: Parameter name
        field: Field definition
        location: Parameter location (query, path, header, cookie)
        description: Parameter description
        required: Whether parameter is required
        
    Returns:
        OpenAPI parameter definition
    """
    if isinstance(field, str):
        field = SimpleField(field)
    
    # Convert field to basic schema
    schema = {
        "type": field.field_type
    }
    
    if field.format_hint:
        if field.format_hint == "email":
            schema["format"] = "email"
        elif field.format_hint in ["url", "uri"]:
            schema["format"] = "uri"
        elif field.format_hint == "datetime":
            schema["format"] = "date-time"
        elif field.format_hint == "date":
            schema["format"] = "date"
        elif field.format_hint == "uuid":
            schema["format"] = "uuid"
    
    if field.choices:
        schema["enum"] = field.choices
    
    # Add constraints
    if field.min_val is not None:
        schema["minimum"] = field.min_val
    if field.max_val is not None:
        schema["maximum"] = field.max_val
    if field.min_length is not None:
        schema["minLength"] = field.min_length
    if field.max_length is not None:
        schema["maxLength"] = field.max_length
    
    parameter = {
        "name": field_name,
        "in": location,
        "required": required or field.required,
        "schema": schema
    }
    
    if description or field.description:
        parameter["description"] = description or field.description
    
    return parameter


def create_openapi_path_item(method: str,
                           summary: str = "",
                           description: str = "",
                           request_fields: Optional[Dict[str, Union[str, SimpleField]]] = None,
                           response_fields: Optional[Dict[str, Union[str, SimpleField]]] = None,
                           parameters: Optional[List[Dict[str, Any]]] = None,
                           tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create OpenAPI path item definition.
    
    Args:
        method: HTTP method (get, post, put, delete, etc.)
        summary: Operation summary
        description: Operation description
        request_fields: Request body field definitions
        response_fields: Response field definitions
        parameters: List of parameter definitions
        tags: List of operation tags
        
    Returns:
        OpenAPI path item definition
    """
    operation = {}
    
    if summary:
        operation["summary"] = summary
    if description:
        operation["description"] = description
    if tags:
        operation["tags"] = tags
    
    # Add parameters
    if parameters:
        operation["parameters"] = parameters
    
    # Add request body
    if request_fields and method.lower() in ["post", "put", "patch"]:
        operation["requestBody"] = create_openapi_request_body(request_fields)
    
    # Add responses
    responses = {}
    if response_fields:
        responses.update(create_openapi_response(response_fields))
    else:
        # Default response
        responses["200"] = {
            "description": "Successful operation"
        }
    
    operation["responses"] = responses
    
    return {method.lower(): operation}


def generate_openapi_spec(title: str,
                         version: str = "1.0.0",
                         description: str = "",
                         paths: Optional[Dict[str, Any]] = None,
                         components: Optional[Dict[str, Any]] = None,
                         servers: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Generate complete OpenAPI specification.
    
    Args:
        title: API title
        version: API version
        description: API description
        paths: Path definitions
        components: Component definitions
        servers: Server definitions
        
    Returns:
        Complete OpenAPI specification
    """
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": title,
            "version": version
        }
    }
    
    if description:
        spec["info"]["description"] = description
    
    if servers:
        spec["servers"] = servers
    else:
        spec["servers"] = [{"url": "https://api.example.com"}]
    
    if paths:
        spec["paths"] = paths
    else:
        spec["paths"] = {}
    
    if components:
        spec["components"] = components
    
    return spec


def validate_openapi_compatibility(fields: Dict[str, SimpleField]) -> Dict[str, Any]:
    """
    Validate that Simple Schema fields are compatible with OpenAPI.
    
    Args:
        fields: Dictionary of SimpleField objects
        
    Returns:
        Validation result dictionary
    """
    result = {
        'compatible': True,
        'warnings': [],
        'errors': [],
        'unsupported_features': []
    }
    
    for field_name, field in fields.items():
        # Check for unsupported union types
        if field.union_types and len(field.union_types) > 1:
            # OpenAPI 3.0 supports oneOf/anyOf but it's more complex
            result['warnings'].append(f"Field '{field_name}' uses union types - consider using oneOf/anyOf")
        
        # Check for unsupported format hints
        unsupported_formats = ['phone']  # OpenAPI doesn't have standard phone format
        if field.format_hint in unsupported_formats:
            result['warnings'].append(f"Field '{field_name}' format '{field.format_hint}' not standard in OpenAPI")
        
        # Check for complex constraints
        if field.min_items is not None or field.max_items is not None:
            if field.field_type != 'array':
                result['warnings'].append(f"Field '{field_name}' has array constraints but is not array type")
    
    return result


def generate_openapi_documentation(spec: Dict[str, Any]) -> str:
    """
    Generate human-readable documentation from OpenAPI spec.
    
    Args:
        spec: OpenAPI specification
        
    Returns:
        Markdown documentation string
    """
    lines = []
    
    # API info
    info = spec.get('info', {})
    title = info.get('title', 'API Documentation')
    lines.append(f"# {title}")
    
    version = info.get('version', 'Unknown')
    lines.append(f"**Version:** {version}")
    
    if 'description' in info:
        lines.append(f"\n{info['description']}")
    
    # Servers
    servers = spec.get('servers', [])
    if servers:
        lines.append("\n## Servers")
        for server in servers:
            url = server.get('url', '')
            description = server.get('description', '')
            if description:
                lines.append(f"- {url} - {description}")
            else:
                lines.append(f"- {url}")
    
    # Paths
    paths = spec.get('paths', {})
    if paths:
        lines.append("\n## Endpoints")
        
        for path, path_item in paths.items():
            lines.append(f"\n### {path}")
            
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    lines.append(f"\n#### {method.upper()}")
                    
                    if 'summary' in operation:
                        lines.append(f"**Summary:** {operation['summary']}")
                    
                    if 'description' in operation:
                        lines.append(f"**Description:** {operation['description']}")
                    
                    # Parameters
                    if 'parameters' in operation:
                        lines.append("**Parameters:**")
                        for param in operation['parameters']:
                            param_name = param.get('name', '')
                            param_type = param.get('schema', {}).get('type', 'unknown')
                            param_required = param.get('required', False)
                            param_desc = param.get('description', '')
                            
                            required_text = " (required)" if param_required else " (optional)"
                            lines.append(f"- `{param_name}` ({param_type}){required_text}: {param_desc}")
                    
                    # Responses
                    if 'responses' in operation:
                        lines.append("**Responses:**")
                        for status_code, response in operation['responses'].items():
                            response_desc = response.get('description', '')
                            lines.append(f"- `{status_code}`: {response_desc}")
    
    # Components
    components = spec.get('components', {})
    if 'schemas' in components:
        lines.append("\n## Schemas")
        
        for schema_name, schema_def in components['schemas'].items():
            lines.append(f"\n### {schema_name}")
            
            if 'description' in schema_def:
                lines.append(schema_def['description'])
            
            if 'properties' in schema_def:
                lines.append("**Properties:**")
                required_fields = set(schema_def.get('required', []))
                
                for prop_name, prop_schema in schema_def['properties'].items():
                    prop_type = prop_schema.get('type', 'unknown')
                    required_text = " (required)" if prop_name in required_fields else " (optional)"
                    prop_desc = prop_schema.get('description', '')
                    
                    lines.append(f"- `{prop_name}` ({prop_type}){required_text}: {prop_desc}")
    
    return '\n'.join(lines)
