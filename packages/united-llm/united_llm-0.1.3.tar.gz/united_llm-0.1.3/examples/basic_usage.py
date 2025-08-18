#!/usr/bin/env python3
"""
Basic Usage Example - United LLM
Demonstrates the core functionality of the united LLM library.
"""

from pydantic import BaseModel
from typing import List
from united_llm import LLMClient

# Example output models
class UserProfile(BaseModel):
    name: str
    age: int
    email: str
    interests: List[str]

class ProductInfo(BaseModel):
    name: str
    price: float
    category: str
    features: List[str]

def main():
    """Basic usage examples"""
    print("🚀 Unified LLM - Basic Usage Examples")
    print("=" * 50)
    
    # Initialize client (uses environment variables and config files automatically)
    client = LLMClient()
    
    print("📋 Example 1: Extract User Information")
    print("-" * 40)
    
    try:
        result = client.generate_structured(
            prompt="Extract info: Sarah Johnson, 28, sarah@example.com, likes photography and hiking",
            output_model=UserProfile,
            model="gpt-4o-mini"  # You can use any configured model
        )
        
        print(f"✅ Success!")
        print(f"Name: {result.name}")
        print(f"Age: {result.age}")
        print(f"Email: {result.email}")
        print(f"Interests: {', '.join(result.interests)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have API keys configured in your .env file")
    
    print("\n📋 Example 2: Extract Product Information")
    print("-" * 40)
    
    try:
        result = client.generate_structured(
            prompt="Product: iPhone 15 Pro, $999, smartphone category, features: A17 chip, titanium design, USB-C",
            output_model=ProductInfo,
            model="gpt-4o-mini"
        )
        
        print(f"✅ Success!")
        print(f"Product: {result.name}")
        print(f"Price: ${result.price}")
        print(f"Category: {result.category}")
        print(f"Features: {', '.join(result.features)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📋 Example 3: Using Dictionary Output (Simple)")
    print("-" * 40)
    
    try:
        # New curly brace syntax - returns plain dictionary
        result = client.generate_dict(
            prompt="Extract: John Doe, 35, Software Engineer",
            schema="{name, age:int, job_title}",
            model="gpt-4o-mini"
        )
        
        print(f"✅ Success!")
        print(f"Result: {result}")
        print(f"Type: {type(result)} (plain Python dict)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n💡 Next Steps:")
    print("• Check examples/web_search.py for search integration")
    print("• Check examples/advanced_features.py for advanced usage")
    print("• Start the web server: python -m united_llm.api.server")
    print("• Visit: http://localhost:8818 for the admin interface")

if __name__ == "__main__":
    main() 