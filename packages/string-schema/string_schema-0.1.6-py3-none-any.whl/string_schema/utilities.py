"""
Pydantic Utility Functions for Simple Schema

This module provides the core utility functions that transform Simple Schema
into a comprehensive Pydantic utility, enabling string-based schema usage
throughout the Python ecosystem.

Key Functions:
- create_model(): String schema → Pydantic model
- validate_to_dict(): Validate data → dict
- validate_to_model(): Validate data → Pydantic model
- returns_dict(): Decorator for dict validation
- returns_model(): Decorator for model validation
"""

import functools
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Type, Union, Callable, Optional, List
import logging

# Optional pydantic import
try:
    from pydantic import BaseModel, ValidationError
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = None
    ValidationError = None

logger = logging.getLogger(__name__)


def _ensure_timezone_aware_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure all datetime values in a dictionary have timezone information.

    This function recursively processes dictionaries and lists to add UTC timezone
    information to naive datetime objects, ensuring consistent API responses.

    Args:
        data: Dictionary that may contain datetime values

    Returns:
        Dictionary with timezone-aware datetime values converted to ISO format
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            # Add UTC timezone to naive datetime objects
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            # Convert to ISO format string for consistent API responses
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            # Recursively process nested dictionaries
            result[key] = _ensure_timezone_aware_dict(value)
        elif isinstance(value, list):
            # Process lists that may contain dictionaries or datetime objects
            result[key] = [
                _ensure_timezone_aware_dict(item) if isinstance(item, dict)
                else item.isoformat() if isinstance(item, datetime) and item.tzinfo is None
                else item.replace(tzinfo=timezone.utc).isoformat() if isinstance(item, datetime)
                else item
                for item in value
            ]
        else:
            result[key] = value

    return result


def string_to_model(schema_str: str, name: Optional[str] = None) -> Type[BaseModel]:
    """
    Create Pydantic model from string schema.

    This is the main utility function that converts string schemas directly
    to Pydantic model classes, eliminating verbose model definitions.

    Args:
        schema_str: String schema definition (e.g., "name:string, email:email, age:int?")
        name: Optional name for the model class. If not provided, generates one.

    Returns:
        Dynamically created Pydantic model class

    Examples:
        # Basic usage
        UserModel = string_to_model("name:string(min=1,max=100), email:email, age:int(0,120)?")
        user = UserModel(name="John", email="john@example.com", age=30)

        # Array schemas
        ProductModel = string_to_model("[{name:string, price:number(min=0), category:enum(electronics,clothing,books)}]")
        products = ProductModel([{"name": "iPhone", "price": 999, "category": "electronics"}])

        # Complex nested schemas
        ProfileModel = string_to_model("name:string, email:email, profile:{bio:text?, avatar:url?}?")
    """
    if not HAS_PYDANTIC:
        raise ImportError("Pydantic is required for string_to_model. Install with: pip install pydantic")

    # Import here to avoid circular imports
    from .parsing.string_parser import parse_string_schema
    from pydantic import create_model as pydantic_create_model, Field
    from typing import List

    # Generate model name if not provided
    if name is None:
        name = f"GeneratedModel_{str(uuid.uuid4()).replace('-', '')[:8]}"

    try:
        # Validate the schema string first
        from .parsing.string_parser import validate_string_schema
        validation_result = validate_string_schema(schema_str)
        if not validation_result['valid']:
            error_msg = "Invalid schema syntax"
            if validation_result['errors']:
                error_msg += f": {', '.join(validation_result['errors'])}"
            raise ValueError(error_msg)

        # Convert string to JSON Schema
        json_schema = parse_string_schema(schema_str)

        # Handle array schemas specially
        if json_schema.get('type') == 'array':
            # For array schemas, use RootModel for Pydantic v2 compatibility
            items_schema = json_schema.get('items', {})

            try:
                # Try Pydantic v2 RootModel first
                from pydantic import RootModel

                if items_schema.get('type') == 'object':
                    # Array of objects: create nested model for items
                    from .integrations.pydantic import create_pydantic_from_json_schema
                    ItemModel = create_pydantic_from_json_schema(items_schema, f"{name}Item")

                    # Create the array model using RootModel
                    class ArrayModel(RootModel[List[ItemModel]]):
                        pass

                    # Set the name
                    ArrayModel.__name__ = name
                    return ArrayModel
                else:
                    # Array of simple types
                    type_mapping = {
                        'string': str,
                        'integer': int,
                        'number': float,
                        'boolean': bool
                    }
                    item_type = type_mapping.get(items_schema.get('type', 'string'), str)

                    # Create the array model using RootModel
                    class ArrayModel(RootModel[List[item_type]]):
                        pass

                    # Set the name
                    ArrayModel.__name__ = name
                    return ArrayModel

            except ImportError:
                # Fallback to Pydantic v1 style with __root__
                if items_schema.get('type') == 'object':
                    # Array of objects: create nested model for items
                    from .integrations.pydantic import create_pydantic_from_json_schema
                    ItemModel = create_pydantic_from_json_schema(items_schema, f"{name}Item")

                    # Create constraints for the array
                    constraints = {}
                    if 'minItems' in json_schema:
                        constraints['min_length'] = json_schema['minItems']
                    if 'maxItems' in json_schema:
                        constraints['max_length'] = json_schema['maxItems']

                    # Create the array model
                    field_info = Field(**constraints) if constraints else Field()
                    return pydantic_create_model(name, __root__=(List[ItemModel], field_info))
                else:
                    # Array of simple types
                    type_mapping = {
                        'string': str,
                        'integer': int,
                        'number': float,
                        'boolean': bool
                    }
                    item_type = type_mapping.get(items_schema.get('type', 'string'), str)

                    # Create constraints for the array
                    constraints = {}
                    if 'minItems' in json_schema:
                        constraints['min_length'] = json_schema['minItems']
                    if 'maxItems' in json_schema:
                        constraints['max_length'] = json_schema['maxItems']

                    field_info = Field(**constraints) if constraints else Field()
                    return pydantic_create_model(name, __root__=(List[item_type], field_info))
        else:
            # Regular object schema
            from .integrations.pydantic import create_pydantic_from_json_schema
            return create_pydantic_from_json_schema(json_schema, name)

    except Exception as e:
        raise ValueError(f"Failed to create model from schema '{schema_str}': {str(e)}") from e


# Legacy alias for backward compatibility
def create_model(schema_str: str, name: Optional[str] = None) -> Type[BaseModel]:
    """
    Create Pydantic model from string schema.

    DEPRECATED: Use string_to_model() instead for consistent naming.
    """
    return string_to_model(schema_str, name)


def validate_to_dict(data: Union[Dict[str, Any], Any], schema_str: str) -> Union[Dict[str, Any], List[Any]]:
    """
    Validate data against string schema and return validated dict or list.

    Perfect for API endpoints and JSON responses where you need validated
    dictionaries rather than model instances.

    Args:
        data: Data to validate (dict, list, model instance, or any object)
        schema_str: String schema definition for validation

    Returns:
        Validated dictionary or list

    Raises:
        ValidationError: If data doesn't match schema
        ValueError: If schema is invalid

    Examples:
        # API endpoint usage
        user_dict = validate_to_dict(raw_data, "name:string, email:email, age:int?")
        # Returns: {"name": "John", "email": "john@example.com", "age": 30}

        # Array validation
        events = validate_to_dict(raw_events, "[{user_id:uuid, event:enum(login,logout,purchase), timestamp:datetime}]")
    """
    if not HAS_PYDANTIC:
        raise ImportError("Pydantic is required for validate_to_dict. Install with: pip install pydantic")

    try:
        # Create temporary model for validation
        TempModel = string_to_model(schema_str, "TempValidationModel")

        # Check if this is an array schema
        from .parsing.string_parser import parse_string_schema
        json_schema = parse_string_schema(schema_str)
        is_array_schema = json_schema.get('type') == 'array'

        if is_array_schema:
            # For array schemas, validate the data directly
            try:
                # Try Pydantic v2 RootModel style
                validated_instance = TempModel(data)
                # Return the validated array data with timezone-aware conversion
                result_data = validated_instance.model_dump() if hasattr(validated_instance, 'model_dump') else validated_instance.dict()
                # Process array items for timezone-aware datetime conversion
                if isinstance(result_data, list):
                    return [_ensure_timezone_aware_dict(item) if isinstance(item, dict) else item for item in result_data]
                return result_data
            except:
                # Fallback to Pydantic v1 style
                validated_instance = TempModel(__root__=data)
                # Return the validated array data with timezone-aware conversion
                result_data = validated_instance.model_dump()['__root__'] if hasattr(validated_instance, 'model_dump') else validated_instance.dict()['__root__']
                # Process array items for timezone-aware datetime conversion
                if isinstance(result_data, list):
                    return [_ensure_timezone_aware_dict(item) if isinstance(item, dict) else item for item in result_data]
                return result_data
        else:
            # Handle different input types for object schemas
            if isinstance(data, dict):
                validated_instance = TempModel(**data)
            elif hasattr(data, '__dict__'):
                # Handle objects with attributes
                validated_instance = TempModel(**data.__dict__)
            else:
                # Try direct validation
                validated_instance = TempModel(data)

            # Return as dictionary with timezone-aware datetime handling
            if hasattr(validated_instance, 'model_dump'):
                result_dict = validated_instance.model_dump()
            else:
                result_dict = validated_instance.dict()

            # Ensure timezone-aware datetime conversion for consistent API responses
            return _ensure_timezone_aware_dict(result_dict)

    except ValidationError as e:
        # Re-raise the original validation error
        raise e
    except Exception as e:
        raise ValueError(f"Failed to validate data against schema '{schema_str}': {str(e)}") from e


def validate_to_model(data: Union[Dict[str, Any], Any], schema_str: str):
    """
    Validate data against string schema and return Pydantic model instance.

    Perfect for business logic where you need full Pydantic model features
    like methods, validators, and type safety.

    Args:
        data: Data to validate (dict, list, model instance, or any object)
        schema_str: String schema definition for validation

    Returns:
        Validated Pydantic model instance

    Raises:
        ValidationError: If data doesn't match schema
        ValueError: If schema is invalid

    Examples:
        # Business logic usage
        user_model = validate_to_model(raw_data, "name:string, email:email, age:int?")
        print(user_model.name)  # Access with full type safety

        # Complex validation
        profile = validate_to_model(data, "name:string, email:email, profile:{bio:text?, avatar:url?}?")
        if profile.profile:
            print(profile.profile.bio)
    """
    if not HAS_PYDANTIC:
        raise ImportError("Pydantic is required for validate_to_model. Install with: pip install pydantic")

    try:
        # Create temporary model for validation
        TempModel = string_to_model(schema_str, "TempValidationModel")

        # Check if this is an array schema
        from .parsing.string_parser import parse_string_schema
        json_schema = parse_string_schema(schema_str)
        is_array_schema = json_schema.get('type') == 'array'

        if is_array_schema:
            # For array schemas, validate the data directly
            try:
                # Try Pydantic v2 RootModel style
                return TempModel(data)
            except:
                # Fallback to Pydantic v1 style
                return TempModel(__root__=data)
        else:
            # Handle different input types for object schemas
            if isinstance(data, dict):
                return TempModel(**data)
            elif hasattr(data, '__dict__'):
                # Handle objects with attributes
                return TempModel(**data.__dict__)
            else:
                # Try direct validation
                return TempModel(data)

    except ValidationError as e:
        # Re-raise the original validation error
        raise e
    except Exception as e:
        raise ValueError(f"Failed to validate data against schema '{schema_str}': {str(e)}") from e


def returns_dict(schema_str: str) -> Callable:
    """
    Decorator that validates function return values to dict format.
    
    Perfect for API endpoints where you want to ensure consistent,
    validated dictionary responses.
    
    Args:
        schema_str: String schema definition for return value validation
    
    Returns:
        Decorator function
    
    Examples:
        # API endpoint decorator
        @returns_dict("id:uuid, name:string, status:enum(created,updated)")
        def create_user(user_data):
            # Business logic here
            return {"id": generate_uuid(), "name": user_data["name"], "status": "created"}
        
        # Data pipeline decorator
        @returns_dict("[{user_id:uuid, event:enum(login,logout,purchase), timestamp:datetime}]")
        def process_event_stream(raw_events):
            # Transform and validate events
            return transformed_events  # Returns list of validated dicts
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                return validate_to_dict(result, schema_str)
            except Exception as e:
                raise ValueError(f"Function '{func.__name__}' returned invalid data for schema '{schema_str}': {str(e)}") from e
        return wrapper
    return decorator


def returns_model(schema_str: str) -> Callable:
    """
    Decorator that validates function return values to Pydantic model instances.
    
    Perfect for business logic functions where you want to ensure type-safe
    model instances with full Pydantic features.
    
    Args:
        schema_str: String schema definition for return value validation
    
    Returns:
        Decorator function
    
    Examples:
        # Business logic decorator
        @returns_model("name:string, email:email, profile:{bio:text?, avatar:url?}?")
        def enrich_user_data(basic_data):
            # Enhancement logic here
            return enhanced_user_data  # Returns validated Pydantic model
        
        # Data processing decorator
        @returns_model("id:uuid, processed_at:datetime, result:{score:float(0,1), confidence:float(0,1)}")
        def process_ml_result(raw_result):
            # ML processing logic
            return processed_result  # Returns validated model with type safety
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                return validate_to_model(result, schema_str)
            except Exception as e:
                raise ValueError(f"Function '{func.__name__}' returned invalid data for schema '{schema_str}': {str(e)}") from e
        return wrapper
    return decorator


# Utility functions for enhanced error handling and debugging

def get_model_info(model_class) -> Dict[str, Any]:
    """
    Get detailed information about a generated Pydantic model.

    Args:
        model_class: Pydantic model class

    Returns:
        Dictionary with model information including fields, types, and constraints
    """
    if not HAS_PYDANTIC or not issubclass(model_class, BaseModel):
        raise ValueError("Input must be a Pydantic model class")

    info = {
        "model_name": model_class.__name__,
        "fields": {},
        "required_fields": [],
        "optional_fields": []
    }

    # Handle both Pydantic v1 and v2
    if hasattr(model_class, 'model_fields'):
        # Pydantic v2
        fields_dict = model_class.model_fields
        for field_name, field_info in fields_dict.items():
            field_data = {
                "type": str(field_info.annotation) if hasattr(field_info, 'annotation') else "unknown",
                "required": field_info.is_required() if hasattr(field_info, 'is_required') else True,
                "default": field_info.default if hasattr(field_info, 'default') and field_info.default is not ... else None,
                "constraints": {}
            }

            # Extract constraints from field_info
            if hasattr(field_info, 'constraints'):
                constraints = field_info.constraints
                for constraint in constraints:
                    if hasattr(constraint, 'ge') and constraint.ge is not None:
                        field_data["constraints"]["min_value"] = constraint.ge
                    if hasattr(constraint, 'le') and constraint.le is not None:
                        field_data["constraints"]["max_value"] = constraint.le
                    if hasattr(constraint, 'min_length') and constraint.min_length is not None:
                        field_data["constraints"]["min_length"] = constraint.min_length
                    if hasattr(constraint, 'max_length') and constraint.max_length is not None:
                        field_data["constraints"]["max_length"] = constraint.max_length

            info["fields"][field_name] = field_data

            if field_data["required"]:
                info["required_fields"].append(field_name)
            else:
                info["optional_fields"].append(field_name)
    else:
        # Pydantic v1 fallback
        fields_dict = getattr(model_class, '__fields__', {})
        for field_name, field_info in fields_dict.items():
            field_data = {
                "type": str(getattr(field_info, 'type_', 'unknown')),
                "required": getattr(field_info, 'required', True),
                "default": getattr(field_info, 'default', None) if getattr(field_info, 'default', ...) is not ... else None,
                "constraints": {}
            }

            info["fields"][field_name] = field_data

            if field_data["required"]:
                info["required_fields"].append(field_name)
            else:
                info["optional_fields"].append(field_name)

    return info


def validate_schema_compatibility(schema_str: str) -> Dict[str, Any]:
    """
    Validate that a string schema is compatible with Pydantic model generation.
    
    Args:
        schema_str: String schema definition to validate
    
    Returns:
        Dictionary with compatibility information and any warnings
    """
    from .parsing.string_parser import validate_string_schema
    
    result = validate_string_schema(schema_str)
    
    # Add Pydantic-specific compatibility checks
    compatibility = {
        "pydantic_compatible": result["valid"],
        "warnings": result.get("warnings", []),
        "errors": result.get("errors", []),
        "features_used": result.get("features_used", []),
        "recommendations": []
    }
    
    # Add recommendations for better Pydantic usage
    if "arrays" in compatibility["features_used"]:
        compatibility["recommendations"].append("Consider using List[Model] type hints for better IDE support")
    
    if "union_types" in compatibility["features_used"]:
        compatibility["recommendations"].append("Union types work well with Pydantic's automatic type coercion")
    
    if "special_types" in compatibility["features_used"]:
        compatibility["recommendations"].append("Special types (email, url, etc.) provide automatic validation")
    
    return compatibility
