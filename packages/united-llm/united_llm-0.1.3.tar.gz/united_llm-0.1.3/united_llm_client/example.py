#!/usr/bin/env python3
"""
Example usage of the United LLM Client

This script demonstrates how to use the United LLM Client to interact
with a United LLM API server for text generation and structured output.
"""

import json
from client import UnitedLLMClient


def main():
    """Main example function"""
    print("🚀 United LLM Client Example")
    print("=" * 40)
    
    # Create client instance
    # Make sure the United LLM server is running on http://127.0.0.1:8818
    client = UnitedLLMClient()
    
    try:
        # 1. Health Check
        print("\n1️⃣ Health Check")
        health = client.get_health()
        print(f"✅ Server Status: {health['status']}")
        
        # 2. Get Available Models
        print("\n2️⃣ Available Models")
        models_info = client.get_models()
        models = [m['model_name'] for m in models_info['models']]
        print(f"✅ Found {len(models)} models")
        print(f"📋 First 5 models: {', '.join(models[:5])}")
        
        # Choose a fast model for examples
        example_model = "gpt-4o-mini" if "gpt-4o-mini" in models else models[0]
        print(f"🎯 Using model: {example_model}")
        
        # 3. Simple Text Generation
        print("\n3️⃣ Simple Text Generation")
        result = client.generate_text(
            prompt="Write a short poem about artificial intelligence",
            model=example_model,
            temperature=0.8
        )
        print(f"✅ Generated in {result['generation_time']:.2f}s")
        print(f"📝 Poem:\n{result['text']}")
        
        # 4. Structured Output Generation
        print("\n4️⃣ Structured Output Generation")
        schema = "{name:string, age:int, profession:string, skills:[string], available:bool}"
        result = client.generate_structured(
            prompt="Create a profile for a software engineer named Sarah who specializes in machine learning",
            schema=schema,
            model=example_model,
            temperature=0.5
        )
        print(f"✅ Generated in {result['generation_time']:.2f}s")
        print(f"📊 Structured Profile:")
        print(json.dumps(result['result'], indent=2))
        
        # 5. Complex Nested Structure
        print("\n5️⃣ Complex Nested Structure")
        complex_schema = """{
            project_name:string,
            description:string,
            team:[{
                name:string,
                role:string,
                experience_years:int
            }],
            technologies:[string],
            status:string,
            estimated_completion_months:int
        }"""
        
        result = client.generate_structured(
            prompt="Create a software project plan for developing a mobile app for food delivery",
            schema=complex_schema,
            model=example_model,
            temperature=0.3
        )
        print(f"✅ Generated in {result['generation_time']:.2f}s")
        print(f"📋 Project Plan:")
        print(json.dumps(result['result'], indent=2))
        
        # 6. Text Generation with Search (if available)
        print("\n6️⃣ Text Generation with Search")
        result = client.generate_text(
            prompt="What are the latest trends in AI development?",
            model=example_model,
            enable_search=True,
            temperature=0.3
        )
        print(f"✅ Generated in {result['generation_time']:.2f}s")
        print(f"🔍 Search used: {result['search_used']}")
        print(f"📰 Response: {result['text'][:200]}...")
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure the United LLM server is running:")
        print("   1. Install: pip install united-llm")
        print("   2. Start server: united-llm-server")
        print("   3. Server should be at: http://127.0.0.1:8818")


if __name__ == "__main__":
    main()
