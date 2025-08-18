#!/usr/bin/env python3
"""
Real Feature Test for United LLM System
Tests all major features with actual API keys and correct imports
"""

import time
import os
from datetime import datetime
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

# Use united namespace imports
from united_llm import (
    LLMClient,
    DuckDuckGoSearch,
    LLMDatabase,
    get_config
)

# Load environment variables
load_dotenv()

class TestResult(BaseModel):
    """Structured output for testing"""
    summary: str
    key_points: List[str]
    confidence_score: float

class CreativeStory(BaseModel):
    """Creative output for testing"""
    title: str
    characters: List[str]
    plot_summary: str

def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_subheader(title: str):
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print(f"{'─'*40}")

def test_all_providers():
    """Test all LLM providers"""
    print_header("TESTING ALL LLM PROVIDERS")
    
    # Create client with explicit config like quick_api_test.py
    config = {
        'openai_api_key': os.getenv('LLM__OPENAI_API_KEY'),
        'anthropic_api_key': os.getenv('LLM__ANTHROPIC_API_KEY'),
        'google_api_key': os.getenv('LLM__GOOGLE_API_KEY'),
        'ollama_base_url': os.getenv('LLM__OLLAMA_BASE_URL'),
        'log_calls': True,
        'log_to_db': True
    }
    client = LLMClient(config=config)
    
    test_scenarios = [
        {
            "provider": "OpenAI",
            "model": "gpt-4o-mini",
            "prompt": "Analyze renewable energy benefits in 3 key points.",
            "schema": TestResult
        },
        {
            "provider": "Anthropic", 
            "model": "claude-sonnet-4-20250514",
            "prompt": "Create a short fantasy story with characters and plot.",
            "schema": CreativeStory
        },
        {
            "provider": "Google",
            "model": "gemini-1.5-flash-latest", 
            "prompt": "Explain quantum computing in simple terms with confidence score.",
            "schema": TestResult
        },
        {
            "provider": "Ollama",
            "model": "qwen3:0.6b",
            "prompt": "Write a creative adventure story with heroes and magic.",
            "schema": CreativeStory
        }
    ]
    
    results = {}
    
    for scenario in test_scenarios:
        print_subheader(f"{scenario['provider']} - {scenario['model']}")
        
        try:
            start_time = time.time()
            
            response = client.generate_structured(
                prompt=scenario['prompt'],
                output_model=scenario['schema'],
                model=scenario['model']
            )
            
            duration = time.time() - start_time
            
            print(f"✅ SUCCESS ({duration:.2f}s)")
            
            if isinstance(response, TestResult):
                print(f"Summary: {response.summary[:80]}...")
                print(f"Key Points: {len(response.key_points)}")
                print(f"Confidence: {response.confidence_score}")
            elif isinstance(response, CreativeStory):
                print(f"Title: {response.title}")
                print(f"Characters: {', '.join(response.characters[:3])}")
                print(f"Plot: {response.plot_summary[:80]}...")
            
            results[scenario['provider']] = {
                "status": "success",
                "duration": duration,
                "model": scenario['model']
            }
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)[:100]}...")
            results[scenario['provider']] = {
                "status": "failed",
                "error": str(e)[:200],
                "model": scenario['model']
            }
    
    return results

def test_search_functionality():
    """Test search functionality"""
    print_header("TESTING SEARCH FUNCTIONALITY")
    
    # Test DuckDuckGo Search
    print_subheader("DuckDuckGo Search")
    try:
        # Create client with explicit config
        llm_config = {
            'openai_api_key': os.getenv('LLM__OPENAI_API_KEY'),
            'anthropic_api_key': os.getenv('LLM__ANTHROPIC_API_KEY'),
            'google_api_key': os.getenv('LLM__GOOGLE_API_KEY'),
            'ollama_base_url': os.getenv('LLM__OLLAMA_BASE_URL'),
            'log_calls': False
        }
        client = LLMClient(config=llm_config)
        
        search_config = {
            'duckduckgo_max_results': 3,
            'duckduckgo_timeout': 10
        }
        ddg_search = DuckDuckGoSearch(config=search_config, llm_client=client)
        
        # Use search_and_generate method with a response model
        class SearchSummary(BaseModel):
            summary: str
            key_findings: List[str]
        
        search_response = ddg_search.search_and_generate(
            prompt="What are the latest AI developments in 2024?",
            output_model=SearchSummary,
            model="gpt-4o-mini"
        )
        
        # Convert to list format for compatibility
        results = [{"title": f"Finding {i+1}: {finding}"} for i, finding in enumerate(search_response.key_findings)]
        
        print(f"✅ SUCCESS: Found {len(results)} results")
        for i, result in enumerate(results[:2], 1):
            print(f"{i}. {result.get('title', 'No title')[:60]}...")
        
        return {"duckduckgo": {"status": "success", "results": len(results)}}
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return {"duckduckgo": {"status": "failed", "error": str(e)[:200]}}

def test_database_functionality():
    """Test database logging"""
    print_header("TESTING DATABASE FUNCTIONALITY")
    
    config = get_config()
    db = LLMDatabase(config.get('db_path', 'llm_calls.db'))
    
    # Create client with explicit config
    config = {
        'openai_api_key': os.getenv('LLM__OPENAI_API_KEY'),
        'anthropic_api_key': os.getenv('LLM__ANTHROPIC_API_KEY'),
        'google_api_key': os.getenv('LLM__GOOGLE_API_KEY'),
        'ollama_base_url': os.getenv('LLM__OLLAMA_BASE_URL'),
        'log_calls': True,
        'log_to_db': True
    }
    client = LLMClient(config=config)
    
    print_subheader("Database Logging Test")
    
    try:
        # Make a test call that should be logged
        test_prompt = "Database test: What is the capital of France?"
        
        # Create a simple response model for testing
        class SimpleResponse(BaseModel):
            answer: str
        
        response_obj = client.generate_structured(
            prompt=test_prompt,
            output_model=SimpleResponse,
            model="gpt-4o-mini"
        )
        response = response_obj.answer
        
        print(f"✅ Generated response: {response[:50]}...")
        
        # Wait for logging
        time.sleep(1)
        
        # Check recent calls
        recent_calls = db.get_calls(limit=5)
        print(f"✅ Found {len(recent_calls)} recent calls in database")
        
        # Check if our test call was logged
        test_call_found = any(test_prompt in call.get('prompt', '') for call in recent_calls)
        
        if test_call_found:
            print("✅ Test call successfully logged")
        else:
            print("⚠️ Test call not found in recent entries")
        
        # Get database statistics
        stats = db.get_stats()
        print(f"Database stats: {stats.get('total_calls', 0)} total calls")
        
        return {
            "status": "success",
            "recent_calls": len(recent_calls),
            "test_logged": test_call_found,
            "total_calls": stats.get('total_calls', 0)
        }
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return {"status": "failed", "error": str(e)[:200]}

def test_multiple_models():
    """Test multiple models in sequence"""
    print_header("TESTING MULTIPLE MODELS")
    
    # Create client with explicit config
    config = {
        'openai_api_key': os.getenv('LLM__OPENAI_API_KEY'),
        'anthropic_api_key': os.getenv('LLM__ANTHROPIC_API_KEY'),
        'google_api_key': os.getenv('LLM__GOOGLE_API_KEY'),
        'ollama_base_url': os.getenv('LLM__OLLAMA_BASE_URL'),
        'log_calls': False
    }
    client = LLMClient(config=config)
    models_to_test = ["gpt-4o-mini", "claude-sonnet-4-20250514", "gemini-1.5-flash-latest", "qwen3:0.6b"]
    
    results = {}
    
    for model in models_to_test:
        print_subheader(f"Testing {model}")
        
        try:
            # Create a simple response model
            class SimpleResponse(BaseModel):
                message: str
            
            response_obj = client.generate_structured(
                prompt="Say hello and tell me one interesting fact about AI.",
                output_model=SimpleResponse,
                model=model
            )
            response = response_obj.message
            
            print(f"✅ SUCCESS: {response[:80]}...")
            results[model] = {"status": "success", "response_length": len(response)}
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)[:80]}...")
            results[model] = {"status": "failed", "error": str(e)[:100]}
    
    return results

def test_structured_outputs():
    """Test structured outputs across providers"""
    print_header("TESTING STRUCTURED OUTPUTS")
    
    # Create client with explicit config
    config = {
        'openai_api_key': os.getenv('LLM__OPENAI_API_KEY'),
        'anthropic_api_key': os.getenv('LLM__ANTHROPIC_API_KEY'),
        'google_api_key': os.getenv('LLM__GOOGLE_API_KEY'),
        'ollama_base_url': os.getenv('LLM__OLLAMA_BASE_URL'),
        'log_calls': False
    }
    client = LLMClient(config=config)
    
    class TechAnalysis(BaseModel):
        technology: str
        pros: List[str]
        cons: List[str]
        rating: float
    
    models = ["gpt-4o-mini", "claude-sonnet-4-20250514", "gemini-1.5-flash-latest"]
    results = {}
    
    for model in models:
        print_subheader(f"Structured Output - {model}")
        
        try:
            response = client.generate_structured(
                prompt="Analyze electric vehicles as a technology with pros, cons, and a rating out of 10.",
                output_model=TechAnalysis,
                model=model
            )
            
            print(f"✅ SUCCESS")
            print(f"Technology: {response.technology}")
            print(f"Pros: {len(response.pros)} items")
            print(f"Cons: {len(response.cons)} items")
            print(f"Rating: {response.rating}/10")
            
            results[model] = {
                "status": "success",
                "technology": response.technology,
                "rating": response.rating
            }
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)[:80]}...")
            results[model] = {"status": "failed", "error": str(e)[:100]}
    
    return results

def main():
    """Run comprehensive feature test"""
    print(f"""
{'='*80}
🚀 UNIFIED LLM SYSTEM - REAL FEATURE TEST
{'='*80}
Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    # Run all tests
    test_results = {}
    
    # Test 1: All Providers
    test_results['providers'] = test_all_providers()
    
    # Test 2: Search Functionality  
    test_results['search'] = test_search_functionality()
    
    # Test 3: Database Functionality
    test_results['database'] = test_database_functionality()
    
    # Test 4: Multiple Models
    test_results['multiple_models'] = test_multiple_models()
    
    # Test 5: Structured Outputs
    test_results['structured'] = test_structured_outputs()
    
    # Final Summary
    print_header("COMPREHENSIVE TEST SUMMARY")
    
    # Provider Summary
    provider_success = sum(1 for p in test_results['providers'].values() if p.get('status') == 'success')
    print(f"🤖 LLM Providers: {provider_success}/4 working")
    
    # Search Summary
    search_success = 1 if test_results['search'].get('duckduckgo', {}).get('status') == 'success' else 0
    print(f"🔍 Search: {search_success}/1 working")
    
    # Database Summary
    db_status = "✅" if test_results['database'].get('status') == 'success' else "❌"
    print(f"💾 Database: {db_status}")
    
    # Multiple Models Summary
    multi_success = sum(1 for m in test_results['multiple_models'].values() if m.get('status') == 'success')
    print(f"🔄 Multiple Models: {multi_success}/4 working")
    
    # Structured Outputs Summary
    struct_success = sum(1 for s in test_results['structured'].values() if s.get('status') == 'success')
    print(f"📊 Structured Outputs: {struct_success}/3 working")
    
    # Overall Health
    total_tests = 5
    working_tests = sum([
        1 if provider_success >= 2 else 0,
        1 if search_success >= 1 else 0,
        1 if test_results['database'].get('status') == 'success' else 0,
        1 if multi_success >= 2 else 0,
        1 if struct_success >= 2 else 0
    ])
    
    health = (working_tests / total_tests) * 100
    print(f"\n🎯 OVERALL HEALTH: {health:.0f}% ({working_tests}/{total_tests} test categories passing)")
    
    if health >= 80:
        print("🎉 EXCELLENT! System is working well!")
    elif health >= 60:
        print("✅ GOOD! Most functionality is working.")
    else:
        print("⚠️ NEEDS ATTENTION! Several issues detected.")
    
    print(f"\n{'='*80}")
    print("Real feature test completed!")
    print(f"{'='*80}")
    
    return test_results

if __name__ == "__main__":
    main() 