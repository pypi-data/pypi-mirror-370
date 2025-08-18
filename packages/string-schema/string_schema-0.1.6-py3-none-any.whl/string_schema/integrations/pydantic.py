"""
Pydantic integration for Simple Schema

Contains functions for creating Pydantic models from Simple Schema definitions.
"""

from typing import Any, Dict, List, Optional, Union, Type
import logging

from ..core.fields import SimpleField

# Optional pydantic import
try:
    from pydantic import BaseModel, Field, create_model
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = None
    Field = None
    create_model = None

logger = logging.getLogger(__name__)


def create_pydantic_model(name: str, fields: Dict[str, Union[str, SimpleField]],
                         base_class: Type = None) -> Type:
    """
    Create Pydantic model from Simple Schema field definitions.

    Args:
        name: Name of the model class
        fields: Dictionary of field definitions
        base_class: Base class to inherit from (default: BaseModel)

    Returns:
        Dynamically created Pydantic model class
    """
    if not HAS_PYDANTIC:
        raise ImportError("Pydantic is required for create_pydantic_model. Install with: pip install pydantic")

    if base_class is None:
        base_class = BaseModel

    pydantic_fields = {}

    for field_name, field_def in fields.items():
        if isinstance(field_def, str):
            field_def = SimpleField(field_def)

        python_type, field_info = _simple_field_to_pydantic(field_def)
        pydantic_fields[field_name] = (python_type, field_info)

    # Create the model with the specified base class
    return create_model(name, __base__=base_class, **pydantic_fields)


def _simple_field_to_pydantic(field: SimpleField) -> tuple:
    """Convert SimpleField to Pydantic field specification"""
    if not HAS_PYDANTIC:
        raise ImportError("Pydantic is required for this function")

    # Type mapping
    type_mapping = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool
    }

    python_type = type_mapping.get(field.field_type, str)

    # Handle union types
    if field.union_types and len(field.union_types) > 1:
        from typing import Union as TypingUnion
        union_python_types = []
        for union_type in field.union_types:
            if union_type == "null":
                union_python_types.append(type(None))
            else:
                union_python_types.append(type_mapping.get(union_type, str))
        python_type = TypingUnion[tuple(union_python_types)]

    # Handle optional fields
    if not field.required:
        python_type = Optional[python_type]

    # Build Field arguments
    field_kwargs = {}

    if field.description:
        field_kwargs['description'] = field.description

    if field.default is not None:
        field_kwargs['default'] = field.default
    elif not field.required:
        field_kwargs['default'] = None

    # Numeric constraints
    if field.min_val is not None:
        field_kwargs['ge'] = field.min_val
    if field.max_val is not None:
        field_kwargs['le'] = field.max_val

    # String constraints
    if field.min_length is not None:
        field_kwargs['min_length'] = field.min_length
    if field.max_length is not None:
        field_kwargs['max_length'] = field.max_length

    return python_type, Field(**field_kwargs) if field_kwargs else Field()


# New consistent naming
def json_schema_to_model(json_schema: Dict[str, Any], name: str) -> Type[BaseModel]:
    """
    Create Pydantic model from JSON Schema dictionary.

    Args:
        json_schema: JSON Schema dictionary
        name: Name of the model class

    Returns:
        Dynamically created Pydantic model class

    Example:
        UserModel = json_schema_to_model(json_schema, 'User')
    """
    return create_pydantic_from_json_schema(json_schema, name)


# Legacy alias for backward compatibility
def json_schema_to_pydantic(json_schema: Dict[str, Any], name: str) -> Type[BaseModel]:
    """
    Create Pydantic model from JSON Schema dictionary.

    DEPRECATED: Use json_schema_to_model() instead for consistent naming.
    """
    return json_schema_to_model(json_schema, name)


def create_pydantic_from_json_schema(json_schema: Dict[str, Any], name: str) -> Type[BaseModel]:
    """
    Create Pydantic model from JSON Schema.

    Args:
        json_schema: JSON Schema dictionary
        name: Name of the model class

    Returns:
        Dynamically created Pydantic model class
    """
    if json_schema.get('type') != 'object':
        raise ValueError("JSON Schema must be of type 'object' to create Pydantic model")
    
    properties = json_schema.get('properties', {})
    required_fields = set(json_schema.get('required', []))
    
    pydantic_fields = {}
    
    for field_name, field_schema in properties.items():
        python_type, field_info = _json_schema_to_pydantic_field(field_schema, field_name in required_fields, f"{name}{field_name.title()}")
        pydantic_fields[field_name] = (python_type, field_info)
    
    return create_model(name, **pydantic_fields)


def _json_schema_to_pydantic_field(field_schema: Dict[str, Any], required: bool = True, parent_name: str = "Nested") -> tuple:
    """Convert JSON Schema field to Pydantic field specification"""
    # Type mapping
    type_mapping = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool
    }

    # Handle union types
    if 'anyOf' in field_schema:
        from typing import Union as TypingUnion
        union_types = []
        for union_option in field_schema['anyOf']:
            option_type = type_mapping.get(union_option.get('type', 'string'), str)
            union_types.append(option_type)
        python_type = TypingUnion[tuple(union_types)]
    elif field_schema.get('type') == 'object':
        # Handle nested objects by creating a nested Pydantic model
        nested_model = create_pydantic_from_json_schema(field_schema, f"{parent_name}Nested")
        python_type = nested_model
    elif field_schema.get('type') == 'array':
        # Handle arrays
        items_schema = field_schema.get('items', {})
        if items_schema.get('type') == 'object':
            # Array of objects
            from typing import List
            item_model = create_pydantic_from_json_schema(items_schema, f"{parent_name}Item")
            python_type = List[item_model]
        else:
            # Array of primitives
            from typing import List
            item_type = type_mapping.get(items_schema.get('type', 'string'), str)
            python_type = List[item_type]
    else:
        field_type = field_schema.get('type', 'string')
        python_type = type_mapping.get(field_type, str)

    # Handle optional fields
    if not required:
        python_type = Optional[python_type]

    # Build Field arguments
    field_kwargs = {}

    if 'description' in field_schema:
        field_kwargs['description'] = field_schema['description']

    if 'default' in field_schema:
        field_kwargs['default'] = field_schema['default']
    elif not required:
        field_kwargs['default'] = None

    # Numeric constraints
    if 'minimum' in field_schema:
        field_kwargs['ge'] = field_schema['minimum']
    if 'maximum' in field_schema:
        field_kwargs['le'] = field_schema['maximum']

    # String constraints
    if 'minLength' in field_schema:
        field_kwargs['min_length'] = field_schema['minLength']
    if 'maxLength' in field_schema:
        field_kwargs['max_length'] = field_schema['maxLength']

    # Format constraints (email, url, etc.)
    if 'format' in field_schema:
        format_type = field_schema['format']
        if format_type == 'email':
            # Use EmailStr for email validation
            try:
                from pydantic import EmailStr
                python_type = EmailStr
                if not required:
                    python_type = Optional[EmailStr]
            except ImportError:
                # Fallback to string with pattern validation
                field_kwargs['pattern'] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        elif format_type in ['uri', 'url']:
            # Use HttpUrl for URL validation
            try:
                from pydantic import HttpUrl
                python_type = HttpUrl
                if not required:
                    python_type = Optional[HttpUrl]
            except ImportError:
                # Fallback to string
                pass
        elif format_type == 'uuid':
            # Use UUID type for UUID validation
            try:
                from uuid import UUID
                python_type = UUID
                if not required:
                    python_type = Optional[UUID]
            except ImportError:
                # Fallback to string
                pass
        elif format_type == 'date-time':
            # Use datetime for datetime validation
            try:
                from datetime import datetime
                python_type = datetime
                if not required:
                    python_type = Optional[datetime]
            except ImportError:
                # Fallback to string
                pass

    # Array constraints
    if 'minItems' in field_schema:
        field_kwargs['min_length'] = field_schema['minItems']
    if 'maxItems' in field_schema:
        field_kwargs['max_length'] = field_schema['maxItems']

    # Enum constraints
    if 'enum' in field_schema:
        # Create a Literal type for enum validation
        from typing import Literal
        enum_values = field_schema['enum']
        if len(enum_values) == 1:
            python_type = Literal[enum_values[0]]
        else:
            python_type = Literal[tuple(enum_values)]

        # Handle optional enum fields
        if not required:
            python_type = Optional[python_type]

    return python_type, Field(**field_kwargs) if field_kwargs else Field()


def model_to_simple_fields(model: Type[BaseModel]) -> Dict[str, SimpleField]:
    """
    Convert Pydantic model to Simple Schema field definitions.
    
    Args:
        model: Pydantic model class
        
    Returns:
        Dictionary of SimpleField objects
    """
    fields = {}
    
    for field_name, field_info in model.model_fields.items():
        simple_field = _pydantic_field_to_simple_field(field_info, field_name)
        fields[field_name] = simple_field
    
    return fields


def _pydantic_field_to_simple_field(field_info: Any, field_name: str) -> SimpleField:
    """Convert Pydantic field info to SimpleField"""
    # This is a simplified conversion - could be enhanced
    
    # Determine field type
    annotation = getattr(field_info, 'annotation', str)
    
    if annotation == str:
        field_type = 'string'
    elif annotation == int:
        field_type = 'integer'
    elif annotation == float:
        field_type = 'number'
    elif annotation == bool:
        field_type = 'boolean'
    else:
        # Handle Optional and Union types
        if hasattr(annotation, '__origin__'):
            if annotation.__origin__ is Union:
                # Union type - use first non-None type
                args = annotation.__args__
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    first_type = non_none_types[0]
                    if first_type == str:
                        field_type = 'string'
                    elif first_type == int:
                        field_type = 'integer'
                    elif first_type == float:
                        field_type = 'number'
                    elif first_type == bool:
                        field_type = 'boolean'
                    else:
                        field_type = 'string'
                else:
                    field_type = 'string'
            else:
                field_type = 'string'
        else:
            field_type = 'string'
    
    # Determine if required
    required = field_info.is_required() if hasattr(field_info, 'is_required') else True
    
    # Get default value
    default = getattr(field_info, 'default', None)
    if default is ...:  # Ellipsis indicates no default
        default = None
    
    # Get description
    description = getattr(field_info, 'description', '')
    
    # Create SimpleField
    simple_field = SimpleField(
        field_type=field_type,
        description=description,
        required=required,
        default=default
    )
    
    return simple_field


def validate_pydantic_compatibility(fields: Dict[str, SimpleField]) -> Dict[str, Any]:
    """
    Validate that Simple Schema fields are compatible with Pydantic.
    
    Args:
        fields: Dictionary of SimpleField objects
        
    Returns:
        Validation result dictionary
    """
    result = {
        'compatible': True,
        'warnings': [],
        'errors': []
    }
    
    for field_name, field in fields.items():
        # Check for unsupported features
        if field.union_types and len(field.union_types) > 2:
            result['warnings'].append(f"Field '{field_name}' has complex union type - may need manual handling")
        
        if field.format_hint and field.format_hint not in ['email', 'url', 'uuid']:
            result['warnings'].append(f"Field '{field_name}' format hint '{field.format_hint}' may not be fully supported")
        
        # Check for conflicting constraints
        if field.min_val is not None and field.max_val is not None:
            if field.min_val > field.max_val:
                result['errors'].append(f"Field '{field_name}' has min_val > max_val")
        
        if field.min_length is not None and field.max_length is not None:
            if field.min_length > field.max_length:
                result['errors'].append(f"Field '{field_name}' has min_length > max_length")
    
    result['compatible'] = len(result['errors']) == 0
    return result


def _string_to_model_with_name(name: str, schema_str: str) -> Type[BaseModel]:
    """
    Create Pydantic model directly from string syntax with explicit name.

    Internal function - use string_to_model from utilities instead.

    Args:
        name: Name of the model class
        schema_str: String schema definition (e.g., "name:string, email:email")

    Returns:
        Dynamically created Pydantic model class

    Example:
        UserModel = _string_to_model_with_name('User', "name:string, email:email, age:int?")
        user = UserModel(name="John", email="john@example.com")
    """
    if not HAS_PYDANTIC:
        raise ImportError("Pydantic is required for _string_to_model_with_name. Install with: pip install pydantic")

    # Import here to avoid circular imports
    from ..parsing.string_parser import parse_string_schema

    # Convert string to JSON Schema, then to Pydantic
    json_schema = parse_string_schema(schema_str)
    return create_pydantic_from_json_schema(json_schema, name)


# Legacy alias for backward compatibility
def string_to_pydantic(name: str, schema_str: str) -> Type[BaseModel]:
    """
    Create Pydantic model directly from string syntax.

    DEPRECATED: Use string_to_model() instead for consistent naming.
    """
    return _string_to_model_with_name(name, schema_str)


def string_to_model_code(name: str, schema_str: str) -> str:
    """
    Generate Pydantic model code directly from string syntax.

    Args:
        name: Name of the model class
        schema_str: String schema definition (e.g., "name:string, email:email")

    Returns:
        Python code string for the Pydantic model

    Example:
        code = string_to_model_code('User', "name:string, email:email, age:int?")
        print(code)
        # Output:
        # from pydantic import BaseModel, Field
        # from typing import Optional, Union
        #
        # class User(BaseModel):
        #     name: str
        #     email: str = Field(format='email')
        #     age: Optional[int] = None
    """
    # Import here to avoid circular imports
    from ..parsing.string_parser import parse_string_schema

    # Convert string to JSON Schema, then to SimpleField objects, then to code
    json_schema = parse_string_schema(schema_str)

    # Convert JSON Schema back to SimpleField objects for code generation
    # This is a bit roundabout, but maintains compatibility with existing code
    properties = json_schema.get('properties', {})
    required_fields = set(json_schema.get('required', []))

    fields = {}
    for field_name, field_schema in properties.items():
        # Convert JSON Schema property back to SimpleField
        simple_field = _json_schema_to_simple_field(field_schema, field_name in required_fields)
        fields[field_name] = simple_field

    return generate_pydantic_code(name, fields)


# Legacy alias for backward compatibility
def string_to_pydantic_code(name: str, schema_str: str) -> str:
    """
    Generate Pydantic model code directly from string syntax.

    DEPRECATED: Use string_to_model_code() instead for consistent naming.
    """
    return string_to_model_code(name, schema_str)


# Reverse conversion functions
def model_to_string(model: Type[BaseModel]) -> str:
    """
    Convert Pydantic model to Simple Schema string syntax.

    Args:
        model: Pydantic model class

    Returns:
        String representation in Simple Schema syntax

    Example:
        UserModel = string_to_model("name:string, email:email, age:int?")
        schema_str = model_to_string(UserModel)
        # Returns: "name:string, email:email, age:int?"
    """
    from .reverse import model_to_string as _model_to_string
    return _model_to_string(model)


def model_to_json_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert Pydantic model to JSON Schema.

    Args:
        model: Pydantic model class

    Returns:
        JSON Schema dictionary

    Example:
        UserModel = string_to_model("name:string, email:email")
        json_schema = model_to_json_schema(UserModel)
    """
    from .reverse import model_to_json_schema as _model_to_json_schema
    return _model_to_json_schema(model)


def _json_schema_to_simple_field(field_schema: Dict[str, Any], required: bool) -> SimpleField:
    """Convert JSON Schema property back to SimpleField for code generation"""
    from ..core.fields import SimpleField

    field_type = field_schema.get('type', 'string')
    format_hint = field_schema.get('format')

    # Handle constraints
    kwargs = {
        'required': required,
        'description': field_schema.get('description', ''),
    }

    if 'minimum' in field_schema:
        kwargs['min_val'] = field_schema['minimum']
    if 'maximum' in field_schema:
        kwargs['max_val'] = field_schema['maximum']
    if 'minLength' in field_schema:
        kwargs['min_length'] = field_schema['minLength']
    if 'maxLength' in field_schema:
        kwargs['max_length'] = field_schema['maxLength']
    if 'enum' in field_schema:
        kwargs['choices'] = field_schema['enum']
    if format_hint:
        kwargs['format_hint'] = format_hint

    return SimpleField(field_type, **kwargs)


def generate_pydantic_code(name: str, fields: Dict[str, SimpleField]) -> str:
    """
    Generate Pydantic model code as a string.
    
    Args:
        name: Name of the model class
        fields: Dictionary of SimpleField objects
        
    Returns:
        Python code string for the Pydantic model
    """
    lines = [
        "from pydantic import BaseModel, Field",
        "from typing import Optional, Union",
        "",
        f"class {name}(BaseModel):"
    ]
    
    if not fields:
        lines.append("    pass")
        return "\n".join(lines)
    
    for field_name, field in fields.items():
        field_line = _generate_pydantic_field_code(field_name, field)
        lines.append(f"    {field_line}")
    
    return "\n".join(lines)


def _generate_pydantic_field_code(field_name: str, field: SimpleField) -> str:
    """Generate code for a single Pydantic field"""
    # Determine Python type
    type_mapping = {
        'string': 'str',
        'integer': 'int', 
        'number': 'float',
        'boolean': 'bool'
    }
    
    python_type = type_mapping.get(field.field_type, 'str')
    
    # Handle union types
    if field.union_types and len(field.union_types) > 1:
        union_types = []
        for union_type in field.union_types:
            if union_type == 'null':
                union_types.append('None')
            else:
                union_types.append(type_mapping.get(union_type, 'str'))
        python_type = f"Union[{', '.join(union_types)}]"
    
    # Handle optional
    if not field.required:
        if 'Union' not in python_type:
            python_type = f"Optional[{python_type}]"
    
    # Build field definition
    field_parts = []
    
    if field.description:
        field_parts.append(f"description='{field.description}'")
    
    if field.default is not None:
        if isinstance(field.default, str):
            field_parts.append(f"default='{field.default}'")
        else:
            field_parts.append(f"default={field.default}")
    elif not field.required:
        field_parts.append("default=None")
    
    # Add constraints
    if field.min_val is not None:
        field_parts.append(f"ge={field.min_val}")
    if field.max_val is not None:
        field_parts.append(f"le={field.max_val}")
    if field.min_length is not None:
        field_parts.append(f"min_length={field.min_length}")
    if field.max_length is not None:
        field_parts.append(f"max_length={field.max_length}")
    
    if field_parts:
        field_def = f"Field({', '.join(field_parts)})"
    else:
        field_def = "Field()"
    
    return f"{field_name}: {python_type} = {field_def}"
