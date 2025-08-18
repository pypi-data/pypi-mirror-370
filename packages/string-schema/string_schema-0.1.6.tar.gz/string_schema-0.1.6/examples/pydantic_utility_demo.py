"""
Pydantic Utility Enhancement Demo

This example demonstrates the new Pydantic utility functions that transform
String Schema into a comprehensive Pydantic utility for rapid development.

Features demonstrated:
- create_model(): String schema → Pydantic model
- validate_to_dict(): Validate data → dict
- validate_to_model(): Validate data → Pydantic model
- @returns_dict: Decorator for dict validation
- @returns_model: Decorator for model validation
"""

from string_schema import (
    string_to_model,
    validate_to_dict,
    validate_to_model,
    returns_dict,
    returns_model,
    get_model_info,
    validate_schema_compatibility
)
import uuid
from datetime import datetime
from typing import Dict, Any, List


def demo_string_to_model():
    """Demonstrate string_to_model() function - the main utility"""
    print("🎯 Demo: string_to_model() - String Schema → Pydantic Model")
    print("=" * 60)

    # Example 1: Basic user model
    print("\n1. Basic User Model:")
    UserModel = string_to_model("name:string(min=1,max=100), email:email, age:int(0,120)?")

    user = UserModel(name="John Doe", email="john@example.com", age=30)
    print(f"   Created user: {user}")
    print(f"   User name: {user.name}")
    print(f"   User email: {user.email}")
    print(f"   User age: {user.age}")

    # Example 2: Product array model
    print("\n2. Product Array Model:")
    ProductModel = string_to_model("[{name:string, price:number(min=0), category:enum(electronics,clothing,books)}]")
    
    products_data = [
        {"name": "iPhone", "price": 999, "category": "electronics"},
        {"name": "T-Shirt", "price": 25, "category": "clothing"}
    ]
    products = ProductModel(products_data)
    print(f"   Created products: {products}")
    
    # Example 3: Complex nested model
    print("\n3. Complex Nested Model:")
    ProfileModel = string_to_model("name:string, email:email, profile:{bio:text?, avatar:url?, social:{twitter:string?, github:string?}?}?")
    
    profile_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "profile": {
            "bio": "Software developer passionate about AI",
            "avatar": "https://example.com/avatar.jpg",
            "social": {"github": "janesmith"}
        }
    }
    profile = ProfileModel(**profile_data)
    print(f"   Created profile: {profile}")
    if profile.profile and profile.profile.social:
        print(f"   GitHub: {profile.profile.social.github}")


def demo_validation_functions():
    """Demonstrate validate_to_dict() and validate_to_model() functions"""
    print("\n\n🔍 Demo: Validation Functions")
    print("=" * 60)
    
    # Sample raw data (like from API request)
    raw_user_data = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "age": 28,
        "extra_field": "ignored"  # This will be filtered out
    }
    
    schema = "name:string, email:email, age:int?"
    
    # Example 1: validate_to_dict - perfect for API responses
    print("\n1. validate_to_dict() - For API Responses:")
    user_dict = validate_to_dict(raw_user_data, schema)
    print(f"   Input: {raw_user_data}")
    print(f"   Validated dict: {user_dict}")
    print(f"   Type: {type(user_dict)}")
    
    # Example 2: validate_to_model - perfect for business logic
    print("\n2. validate_to_model() - For Business Logic:")
    user_model = validate_to_model(raw_user_data, schema)
    print(f"   Validated model: {user_model}")
    print(f"   Type: {type(user_model)}")
    print(f"   Access name: {user_model.name}")
    print(f"   Access email: {user_model.email}")
    
    # Example 3: Array validation
    print("\n3. Array Validation:")
    raw_events = [
        {"user_id": str(uuid.uuid4()), "event": "login", "timestamp": datetime.now().isoformat()},
        {"user_id": str(uuid.uuid4()), "event": "purchase", "timestamp": datetime.now().isoformat()}
    ]
    
    event_schema = "[{user_id:uuid, event:enum(login,logout,purchase), timestamp:datetime}]"
    validated_events = validate_to_dict(raw_events, event_schema)
    print(f"   Validated events: {validated_events}")


def demo_decorators():
    """Demonstrate @returns_dict and @returns_model decorators"""
    print("\n\n🎨 Demo: Function Decorators")
    print("=" * 60)
    
    # Example 1: @returns_dict for API endpoints
    @returns_dict("id:uuid, name:string, status:enum(created,updated)")
    def create_user_api(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate API endpoint that creates a user"""
        return {
            "id": str(uuid.uuid4()),
            "name": user_data["name"],
            "status": "created"
        }
    
    print("\n1. @returns_dict Decorator - API Endpoint:")
    result = create_user_api({"name": "Bob Wilson"})
    print(f"   API Response: {result}")
    print(f"   Type: {type(result)}")
    
    # Example 2: @returns_model for business logic
    @returns_model("name:string, email:email, profile:{bio:text?, avatar:url?}?")
    def enrich_user_data(basic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate business logic that enriches user data"""
        enriched = basic_data.copy()
        enriched["profile"] = {
            "bio": f"User profile for {basic_data['name']}",
            "avatar": f"https://api.example.com/avatar/{basic_data['name'].lower().replace(' ', '')}"
        }
        return enriched
    
    print("\n2. @returns_model Decorator - Business Logic:")
    enriched_user = enrich_user_data({"name": "Carol Davis", "email": "carol@example.com"})
    print(f"   Enriched user: {enriched_user}")
    print(f"   Type: {type(enriched_user)}")
    print(f"   Bio: {enriched_user.profile.bio}")
    
    # Example 3: Data pipeline with array processing
    @returns_dict("[{processed_at:datetime, score:float(0,1), confidence:float(0,1)}]")
    def process_ml_results(raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simulate ML result processing"""
        processed = []
        for result in raw_results:
            processed.append({
                "processed_at": datetime.now().isoformat(),
                "score": min(1.0, max(0.0, result.get("raw_score", 0.5))),
                "confidence": min(1.0, max(0.0, result.get("raw_confidence", 0.8)))
            })
        return processed
    
    print("\n3. @returns_dict with Arrays - Data Pipeline:")
    ml_results = process_ml_results([
        {"raw_score": 0.85, "raw_confidence": 0.92},
        {"raw_score": 0.73, "raw_confidence": 0.88}
    ])
    print(f"   ML Results: {ml_results}")


def demo_utility_functions():
    """Demonstrate utility functions for debugging and introspection"""
    print("\n\n🔧 Demo: Utility Functions")
    print("=" * 60)
    
    # Create a model for inspection
    UserModel = string_to_model("name:string(min=1,max=100), email:email, age:int(0,120)?, status:enum(active,inactive)")
    
    # Example 1: Model introspection
    print("\n1. get_model_info() - Model Introspection:")
    model_info = get_model_info(UserModel)
    print(f"   Model name: {model_info['model_name']}")
    print(f"   Required fields: {model_info['required_fields']}")
    print(f"   Optional fields: {model_info['optional_fields']}")
    print("   Field details:")
    for field_name, field_info in model_info['fields'].items():
        print(f"     {field_name}: {field_info['type']} (required: {field_info['required']})")
        if field_info['constraints']:
            print(f"       Constraints: {field_info['constraints']}")
    
    # Example 2: Schema compatibility checking
    print("\n2. validate_schema_compatibility() - Schema Validation:")
    schema_str = "name:string, email:email, tags:[string](max=5)?, profile:{bio:text?, social:{twitter:string?, github:string?}?}?"
    compatibility = validate_schema_compatibility(schema_str)
    print(f"   Pydantic compatible: {compatibility['pydantic_compatible']}")
    print(f"   Features used: {compatibility['features_used']}")
    if compatibility['recommendations']:
        print("   Recommendations:")
        for rec in compatibility['recommendations']:
            print(f"     - {rec}")


def demo_fastapi_integration():
    """Demonstrate FastAPI integration patterns"""
    print("\n\n🚀 Demo: FastAPI Integration Patterns")
    print("=" * 60)
    
    print("\n1. FastAPI Model Creation:")
    print("   # Create request/response models from string schemas")
    print("   CreateUserRequest = create_model('name:string(min=1), email:email, age:int?')")
    print("   UserResponse = create_model('id:uuid, name:string, email:email, created:datetime')")
    
    print("\n2. FastAPI Endpoint with Decorators:")
    print("   @app.get('/users/{user_id}')")
    print("   @returns_dict('id:uuid, name:string, email:email, last_login:datetime?')")
    print("   def get_user(user_id: str):")
    print("       return fetch_user_data(user_id)  # Auto-validated dict response")
    
    print("\n3. Complex FastAPI Response:")
    print("   @app.post('/products')")
    print("   @returns_dict('id:uuid, name:string, status:enum(created,exists)')")
    print("   def create_product(product: create_model('name:string, price:number(min=0), tags:[string]?')):")
    print("       return process_product_creation(product)")


if __name__ == "__main__":
    print("🎯 String Schema - Pydantic Utility Enhancement Demo")
    print("=" * 80)
    print("Transform string schemas into powerful Pydantic utilities!")
    
    try:
        demo_string_to_model()
        demo_validation_functions()
        demo_decorators()
        demo_utility_functions()
        demo_fastapi_integration()
        
        print("\n\n✅ Demo completed successfully!")
        print("🎉 You now have powerful Pydantic utilities at your fingertips!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
