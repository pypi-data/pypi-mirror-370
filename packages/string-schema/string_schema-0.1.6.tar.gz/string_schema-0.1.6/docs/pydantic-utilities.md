# 🎯 Pydantic Utility Enhancement

Transform your String Schema implementation into a comprehensive **Pydantic utility** that eliminates verbose model definitions and enables string-based schema usage throughout the Python ecosystem.

## 🚀 Quick Start

```python
from string_schema import string_to_model, validate_to_dict, returns_dict

# Create Pydantic models from string schemas
UserModel = string_to_model("name:string(min=1,max=100), email:email, age:int(0,120)?")
user = UserModel(name="John", email="john@example.com", age=30)

# Validate data to dictionaries
user_dict = validate_to_dict(raw_data, "name:string, email:email, age:int?")

# Use decorators for automatic validation
@returns_dict("id:uuid, name:string, status:enum(created,updated)")
def create_user(user_data):
    return {"id": generate_uuid(), "name": user_data["name"], "status": "created"}
```

## 📦 Core Functions

### 1. `string_to_model(schema_str, name=None)`

**The main utility function** - converts string schemas directly to Pydantic model classes.

```python
# Basic usage
UserModel = string_to_model("name:string, email:email, age:int?")

# Array schemas
ProductModel = string_to_model("[{name:string, price:number(min=0)}]")

# Complex nested schemas
ProfileModel = string_to_model("name:string, profile:{bio:text?, avatar:url?, social:{twitter:string?, github:string?}?}?")
```

**Features:**

- ✅ Basic types: `string`, `int`, `number`, `boolean`
- ✅ Special types: `email`, `url`, `uuid`, `datetime`, `phone`
- ✅ **Timezone-aware datetime**: Automatic UTC conversion for consistent API responses
- ✅ Arrays: `[string]`, `[{name:string, price:number}]`
- ✅ Nested objects: `profile:{bio:text?, avatar:url?}`
- ✅ Enums: `status:enum(active,inactive,pending)`
- ✅ Constraints: `name:string(min=1,max=100)`, `age:int(0,120)`
- ✅ Optional fields: `age:int?`
- ✅ Union types: `id:string|uuid`

### 2. `validate_to_dict(data, schema_str)`

**Perfect for API endpoints** - validates data and returns clean dictionaries.

```python
# API endpoint usage
user_dict = validate_to_dict(raw_data, "name:string, email:email, age:int?")
# Returns: {"name": "John", "email": "john@example.com", "age": 30}

# Automatic timezone handling for datetime fields
event_data = {"name": "Meeting", "start_time": datetime(2025, 8, 13, 14, 30)}
event_dict = validate_to_dict(event_data, "name:string, start_time:datetime")
# Returns: {"name": "Meeting", "start_time": "2025-08-13T14:30:00+00:00"}

# Array validation
events = validate_to_dict(raw_events, "[{user_id:uuid, event:enum(login,logout,purchase)}]")

# Filters out extra fields automatically
clean_data = validate_to_dict(messy_data, "name:string, email:email")
```

### 3. `validate_to_model(data, schema_str)`

**Perfect for business logic** - validates data and returns Pydantic model instances.

```python
# Business logic usage
user_model = validate_to_model(raw_data, "name:string, email:email, age:int?")
print(user_model.name)  # Full type safety and IDE support

# Access nested data
profile = validate_to_model(data, "name:string, profile:{bio:text?, avatar:url?}?")
if profile.profile:
    print(profile.profile.bio)
```

## 🌍 Timezone Handling

String Schema automatically ensures all datetime fields include timezone information for consistent, timezone-aware API responses.

### **Automatic UTC Conversion**

```python
from datetime import datetime
from string_schema import validate_to_dict

# Naive datetime gets UTC timezone
data = {"event": "Meeting", "time": datetime(2025, 8, 13, 14, 30)}
result = validate_to_dict(data, "event:string, time:datetime")
# Returns: {"event": "Meeting", "time": "2025-08-13T14:30:00+00:00"}

# Timezone-aware datetime preserved
from datetime import timezone
utc_time = datetime(2025, 8, 13, 14, 30, tzinfo=timezone.utc)
data = {"event": "UTC Meeting", "time": utc_time}
result = validate_to_dict(data, "event:string, time:datetime")
# Returns: {"event": "UTC Meeting", "time": "2025-08-13T14:30:00+00:00"}
```

### **Nested and Array Support**

```python
# Nested datetime handling
user_data = {
    "name": "John",
    "profile": {
        "created_at": datetime(2025, 8, 13, 10, 0),
        "last_login": datetime(2025, 8, 13, 12, 0)
    }
}
result = validate_to_dict(user_data, "name:string, profile:{created_at:datetime, last_login:datetime}")
# All nested datetime fields get timezone info automatically

# Array datetime handling
events = [
    {"id": 1, "timestamp": datetime(2025, 8, 13, 9, 0)},
    {"id": 2, "timestamp": datetime(2025, 8, 13, 10, 0)}
]
result = validate_to_dict(events, "[{id:int, timestamp:datetime}]")
# All timestamps in array items get timezone info
```

### **Benefits**

- ✅ **Consistent API Responses**: All datetime fields include timezone information
- ✅ **Global Application Support**: Works correctly across all timezones
- ✅ **Frontend Compatibility**: JavaScript automatically handles timezone conversion
- ✅ **Zero Configuration**: Works automatically for all datetime fields
- ✅ **Performance Optimized**: Minimal overhead with maximum benefit

## 🎨 Decorators

### 4. `@returns_dict(schema_str)`

**Automatic dict validation** for function return values.

```python
@returns_dict("id:uuid, name:string, status:enum(created,updated)")
def create_user(user_data):
    return {"id": generate_uuid(), "name": user_data["name"], "status": "created"}

# Array responses
@returns_dict("[{processed_at:datetime, score:float(0,1)}]")
def process_ml_results(raw_results):
    return transformed_results  # Auto-validated list of dicts
```

### 5. `@returns_model(schema_str)`

**Automatic model validation** for function return values.

```python
@returns_model("name:string, email:email, profile:{bio:text?, avatar:url?}?")
def enrich_user_data(basic_data):
    return enhanced_user_data  # Returns validated Pydantic model
```

## 🔧 Utility Functions

### 6. `get_model_info(model_class)`

**Model introspection** - get detailed information about generated models.

```python
UserModel = create_model("name:string, email:email, age:int?")
info = get_model_info(UserModel)

print(f"Model: {info['model_name']}")
print(f"Required: {info['required_fields']}")
print(f"Optional: {info['optional_fields']}")
```

### 7. `validate_schema_compatibility(schema_str)`

**Schema validation** - check compatibility and get recommendations.

```python
compatibility = validate_schema_compatibility("name:string, tags:[string]?, profile:{bio:text?}?")
print(f"Compatible: {compatibility['pydantic_compatible']}")
print(f"Features: {compatibility['features_used']}")
print(f"Recommendations: {compatibility['recommendations']}")
```

## 🌐 FastAPI Integration

### Seamless FastAPI Development

```python
from fastapi import FastAPI
from string_schema import string_to_model, returns_dict

app = FastAPI()

# Create models from string schemas
CreateUserRequest = string_to_model("name:string(min=1), email:email, age:int?")
UserResponse = string_to_model("id:uuid, name:string, email:email, created:datetime")

@app.post("/users", response_model=UserResponse)
def create_user(request: CreateUserRequest):
    return UserResponse(
        id=generate_uuid(),
        name=request.name,
        email=request.email,
        created=datetime.now()
    )

# Direct dict responses with validation
@app.get("/users/{user_id}")
@returns_dict("id:uuid, name:string, email:email, last_login:datetime?")
def get_user(user_id: str):
    return fetch_user_data(user_id)  # Auto-validated dict response
```

## 🎯 Key Use Cases

### 1. **Rapid API Development**

```python
@app.post("/products")
@returns_dict("id:uuid, name:string, status:enum(created,exists)")
def create_product(product: create_model("name:string, price:number(min=0)")):
    return process_product_creation(product)
```

### 2. **Dynamic Schema Generation**

```python
def create_form_model(field_config: str):
    return create_model(field_config)

ContactForm = create_form_model("name:string(min=1), email:email, message:text(max=500)")
```

### 3. **LLM Data Extraction**

```python
ExtractionModel = create_model("[{person:string, sentiment:enum(positive,negative,neutral)}]")
result = llm_client.extract(text, response_model=ExtractionModel)
```

### 4. **Data Pipeline Validation**

```python
@returns_dict("[{user_id:uuid, event:enum(login,logout,purchase), timestamp:datetime}]")
def process_event_stream(raw_events):
    return transformed_events  # Returns list of validated dicts
```

## 💡 Value Proposition

### **Before (Traditional Pydantic)**

```python
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: Optional[int] = Field(None, ge=0, le=120)
    status: Status
```

### **After (String Schema Utility)**

```python
from string_schema import string_to_model

User = string_to_model("name:string(min=1,max=100), email:email, age:int(0,120)?, status:enum(active,inactive)")
```

**Result**: 90% less code, same functionality, better readability.

## 🔄 Migration Guide

### From Existing String Schema

```python
# Old way
from string_schema import string_to_pydantic
UserModel = string_to_pydantic('User', "name:string, email:email")

# New way (consistent naming)
from string_schema import string_to_model
UserModel = string_to_model("name:string, email:email", name='User')
```

### From Pure Pydantic

```python
# Old way
class User(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None

# New way
from string_schema import create_model
User = create_model("name:string, email:email, age:int?")
```

## 🚀 Advanced Features

### Array Handling

```python
# Simple arrays
TagModel = create_model("[string]")
tags = TagModel(["python", "ai", "web"])

# Object arrays
ProductModel = create_model("[{name:string, price:number}]")
products = ProductModel([{"name": "iPhone", "price": 999}])
```

### Nested Objects

```python
ProfileModel = create_model("""
user:{
    name:string,
    email:email,
    profile:{
        bio:text?,
        social:{
            twitter:string?,
            github:string?
        }?
    }?
}
""")
```

### Constraints & Validation

```python
# String constraints
create_model("name:string(min=1,max=100)")

# Numeric constraints
create_model("age:int(0,120), score:float(0,1)")

# Array constraints
create_model("tags:[string](max=5)")

# Email/URL validation (automatic)
create_model("email:email, website:url")
```

## 🎉 Benefits

- **90% Less Code**: Eliminate verbose Pydantic class definitions
- **Better Readability**: Human-readable schema strings
- **Rapid Prototyping**: Create models in seconds, not minutes
- **Full Pydantic Power**: All validation, serialization, and type safety
- **FastAPI Ready**: Perfect integration with FastAPI endpoints
- **LLM Friendly**: Ideal for AI/ML data extraction workflows
- **Developer Productivity**: Focus on business logic, not boilerplate

Transform your development workflow with String Schema's Pydantic utilities! 🚀
