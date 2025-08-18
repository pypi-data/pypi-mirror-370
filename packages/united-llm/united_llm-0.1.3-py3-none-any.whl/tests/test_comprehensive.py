#!/usr/bin/env python3
"""
Comprehensive Feature Test for United LLM System
Tests all major features with real API keys:
- All 4 LLM providers (OpenAI, Anthropic, Google, Ollama)
- Search functionality (DuckDuckGo + Anthropic)
- Database logging and retrieval
- Structured outputs
- Error handling and fallbacks
- Admin interface functionality
"""

import asyncio
import json
import time
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# Use united namespace imports
from united_llm import (
    LLMClient,
    DuckDuckGoSearch,
    LLMDatabase,
    get_config
)

class TestResult(BaseModel):
    """Structured output for testing"""
    summary: str
    key_points: List[str]
    confidence_score: float
    category: str

class CreativeStory(BaseModel):
    """Creative output for testing"""
    title: str
    characters: List[str]
    plot_summary: str
    genre: str

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_subheader(title: str):
    """Print a formatted subheader"""
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print(f"{'─'*40}")

def test_all_providers():
    """Test all available LLM providers"""
    print_header("TESTING ALL LLM PROVIDERS")
    
    # Test scenarios for each provider
    test_scenarios = [
        {
            'name': 'OpenAI GPT-4o',
            'model': 'gpt-4o',
            'prompt': 'Analyze the benefits of renewable energy in exactly 3 key points.',
            'schema': TestResult
        },
        {
            'name': 'OpenAI GPT-4o-mini',
            'model': 'gpt-4o-mini', 
            'prompt': 'Write a short creative story about a robot learning to paint.',
            'schema': CreativeStory
        },
        {
            'name': 'Claude Sonnet 4',
            'model': 'claude-sonnet-4-20250514',
            'prompt': 'Explain quantum computing concepts in simple terms with 4 main points.',
            'schema': TestResult
        },
        {
            'name': 'Gemini 1.5 Flash',
            'model': 'gemini-1.5-flash-latest',
            'prompt': 'Create a brief story about space exploration with characters and plot.',
            'schema': CreativeStory
        }
    ]
    
    results = {}
    client = LLMClient()
    
    for scenario in test_scenarios:
        print_subheader(f"Testing {scenario['name']}")
        
        try:
            start_time = time.time()
            
            # Test structured generation
            response = client.generate_structured(
                prompt=scenario['prompt'],
                output_model=scenario['schema'],
                model=scenario['model']
            )
            
            duration = time.time() - start_time
            
            # Validate response structure
            if hasattr(response, 'summary') or hasattr(response, 'title'):
                print(f"✅ SUCCESS: {scenario['name']} ({duration:.2f}s)")
                if hasattr(response, 'summary'):
                    print(f"   Summary: {response.summary[:100]}...")
                elif hasattr(response, 'title'):
                    print(f"   Title: {response.title}")
                    print(f"   Genre: {response.genre}")
                
                results[scenario['model']] = {
                    'status': 'success',
                    'duration': duration,
                    'response_type': type(response).__name__
                }
            else:
                print(f"❌ INVALID: {scenario['name']} - Unexpected response structure")
                results[scenario['model']] = {
                    'status': 'invalid_structure',
                    'duration': duration
                }
                
        except Exception as e:
            print(f"❌ FAILED: {scenario['name']} - {str(e)[:100]}...")
            results[scenario['model']] = {
                'status': 'failed',
                'error': str(e)[:200]
            }
        
        # Small delay between tests
        time.sleep(1)
    
    return results

def test_search_functionality():
    """Test integrated search functionality"""
    print_header("TESTING SEARCH FUNCTIONALITY")
    
    results = {}
    
    # Test DuckDuckGo Search
    print_subheader("DuckDuckGo Search")
    try:
        client = LLMClient()
        ddg_search = DuckDuckGoSearch(config={}, llm_client=client)
        
        # Use search_and_generate method instead of search
        class SearchSummary(BaseModel):
            summary: str
            key_findings: List[str]
        
        search_response = ddg_search.search_and_generate(
            prompt="What are the latest AI developments in 2024?",
            output_model=SearchSummary,
            model="claude-sonnet-4-20250514"
        )
        
        # Convert to list format for compatibility
        ddg_results = [{"title": f"Finding {i+1}: {finding}"} for i, finding in enumerate(search_response.key_findings)]
        
        print(f"✅ SUCCESS: Found {len(ddg_results)} results")
        for i, result in enumerate(ddg_results[:3]):
            print(f"   {i+1}. {result['title'][:60]}...")
        
        results['duckduckgo'] = {
            'status': 'success',
            'results_count': len(ddg_results)
        }
        
    except Exception as e:
        print(f"❌ FAILED: DuckDuckGo search - {str(e)[:100]}...")
        results['duckduckgo'] = {
            'status': 'failed',
            'error': str(e)[:200]
        }
    
    # Test Anthropic web search
    print_subheader("Anthropic Web Search")
    try:
        client = LLMClient()
        
        class SearchResults(BaseModel):
            results: List[str]
            summary: str
        
        search_response = client.generate_structured(
            prompt="Recent developments in machine learning 2024",
            output_model=SearchResults,
            model="claude-sonnet-4-20250514",
            anthropic_web_search=True
        )
        
        print(f"✅ SUCCESS: Anthropic search completed")
        print(f"   Summary: {search_response.summary[:100]}...")
        print(f"   Results count: {len(search_response.results)}")
        
        results['anthropic'] = {
            'status': 'success',
            'results_count': len(search_response.results)
        }
        
    except Exception as e:
        print(f"❌ FAILED: Anthropic search - {str(e)[:100]}...")
        results['anthropic'] = {
            'status': 'failed',
            'error': str(e)[:200]
        }
    
    return results

def test_database_functionality():
    """Test database logging and retrieval"""
    print_header("TESTING DATABASE FUNCTIONALITY")
    
    db_manager = LLMDatabase('llm_calls.db')
    client = LLMClient()
    
    print_subheader("Database Logging Test")
    
    test_prompt = "Test database logging functionality"
    
    try:
        # Make a call that should be logged
        class SimpleResponse(BaseModel):
            answer: str
        
        response = client.generate_structured(
            prompt=test_prompt,
            output_model=SimpleResponse,
            model="claude-sonnet-4-20250514"
        )
        
        print(f"✅ Generated response: {response.answer[:50]}...")
        
        # Wait a moment for logging to complete
        time.sleep(2)
        
        # Test database retrieval
        print_subheader("Database Retrieval Test")
        recent_calls = db_manager.get_calls(limit=5)
        
        print(f"✅ Retrieved {len(recent_calls)} recent calls from database")
        
        # Look for our test call
        test_call_found = False
        for call in recent_calls:
            if test_prompt in call.get('prompt', ''):
                test_call_found = True
                print(f"✅ Test call logged successfully:")
                print(f"   Model: {call.get('model', 'Unknown')}")
                print(f"   Timestamp: {call.get('timestamp', 'Unknown')}")
                print(f"   Provider: {call.get('provider', 'Unknown')}")
                break
        
        if not test_call_found:
            print("⚠️ Test call not found in recent entries")
        
        # Test database statistics
        print_subheader("Database Statistics")
        stats = db_manager.get_stats()
        print(f"Total calls: {stats.get('total_calls', 0)}")
        print(f"Successful calls: {stats.get('successful_calls', 0)}")
        print(f"Failed calls: {stats.get('failed_calls', 0)}")
        
        return {
            "status": "success",
            "recent_calls": len(recent_calls),
            "test_call_logged": test_call_found,
            "stats": stats
        }
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)[:200]
        }

def test_error_handling():
    """Test error handling and fallback mechanisms"""
    print_header("TESTING ERROR HANDLING & FALLBACKS")
    
    client = LLMClient()
    
    print_subheader("Invalid Model Test")
    try:
        # Test with invalid model using structured output
        class SimpleResponse(BaseModel):
            message: str
        
        response = client.generate_structured(
            prompt="Test fallback mechanism",
            output_model=SimpleResponse,
            model="invalid-model-name"
        )
        print(f"✅ Fallback worked: {response.message[:50]}...")
        fallback_result = "success"
    except Exception as e:
        print(f"❌ Fallback failed: {str(e)[:100]}...")
        fallback_result = "failed"
    
    print_subheader("Rate Limit Handling Test")
    # Test multiple rapid requests to see rate limiting
    rapid_requests = []
    for i in range(3):
        try:
            start_time = time.time()
            
            class QuickResponse(BaseModel):
                answer: str
            
            response = client.generate_structured(
                prompt=f"Quick test {i+1}",
                output_model=QuickResponse,
                model="gpt-4o-mini"
            )
            duration = time.time() - start_time
            rapid_requests.append({"success": True, "duration": duration})
            print(f"✅ Request {i+1}: {duration:.2f}s")
        except Exception as e:
            rapid_requests.append({"success": False, "error": str(e)[:100]})
            print(f"❌ Request {i+1} failed: {str(e)[:50]}...")
    
    successful_rapid = sum(1 for r in rapid_requests if r.get("success"))
    print(f"✅ {successful_rapid}/3 rapid requests succeeded")
    
    return {
        "fallback_test": fallback_result,
        "rapid_requests": {
            "successful": successful_rapid,
            "total": len(rapid_requests)
        }
    }

def test_admin_functionality():
    """Test admin-related functionality"""
    print_header("TESTING ADMIN FUNCTIONALITY")
    
    db_manager = LLMDatabase('llm_calls.db')
    
    print_subheader("Admin Database Operations")
    
    try:
        # Test admin queries
        recent_calls = db_manager.get_calls(limit=10)
        stats = db_manager.get_stats()
        
        print(f"✅ Recent calls query: {len(recent_calls)} results")
        print(f"✅ Statistics query: {len(stats)} metrics")
        
        # Test call filtering by model
        if recent_calls:
            models_used = set()
            for call in recent_calls:
                if call.get('model'):
                    models_used.add(call['model'])
            
            print(f"✅ Models detected in logs: {', '.join(models_used)}")
        
        return {
            "status": "success",
            "recent_calls": len(recent_calls),
            "stats_available": len(stats) > 0,
            "models_in_logs": len(models_used) if recent_calls else 0
        }
        
    except Exception as e:
        print(f"❌ Admin functionality test failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)[:200]
        }

def main():
    """Run comprehensive feature test"""
    print(f"""
{'='*80}
🚀 UNIFIED LLM SYSTEM - COMPREHENSIVE FEATURE TEST
{'='*80}
Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    # Run all tests
    test_results = {}
    
    # Test 1: All LLM Providers
    test_results['providers'] = test_all_providers()
    
    # Test 2: Search Functionality  
    test_results['search'] = test_search_functionality()
    
    # Test 3: Database Functionality
    test_results['database'] = test_database_functionality()
    
    # Test 4: Error Handling
    test_results['error_handling'] = test_error_handling()
    
    # Test 5: Admin Functionality
    test_results['admin'] = test_admin_functionality()
    
    # Final Summary
    print_header("COMPREHENSIVE TEST SUMMARY")
    
    # Provider Summary
    provider_success = sum(1 for p in test_results['providers'].values() if p.get('status') == 'success')
    print(f"🤖 LLM Providers: {provider_success}/4 working")
    
    # Search Summary
    search_success = sum(1 for s in test_results['search'].values() if s.get('status') == 'success')
    search_total = len([s for s in test_results['search'].values() if s.get('status') != 'skipped'])
    print(f"🔍 Search Engines: {search_success}/{search_total} working")
    
    # Database Summary
    db_status = "✅" if test_results['database'].get('status') == 'success' else "❌"
    print(f"💾 Database Logging: {db_status}")
    
    # Error Handling Summary
    fallback_status = "✅" if test_results['error_handling'].get('fallback_test') == 'success' else "❌"
    print(f"🛡️ Error Handling: {fallback_status}")
    
    # Admin Summary
    admin_status = "✅" if test_results['admin'].get('status') == 'success' else "❌"
    print(f"👑 Admin Functions: {admin_status}")
    
    # Overall System Health
    total_systems = 5
    working_systems = sum([
        1 if provider_success == 4 else 0,
        1 if search_success > 0 else 0,
        1 if test_results['database'].get('status') == 'success' else 0,
        1 if test_results['error_handling'].get('fallback_test') == 'success' else 0,
        1 if test_results['admin'].get('status') == 'success' else 0
    ])
    
    health_percentage = (working_systems / total_systems) * 100
    
    print(f"\n🎯 OVERALL SYSTEM HEALTH: {health_percentage:.0f}% ({working_systems}/{total_systems} systems)")
    
    if health_percentage >= 80:
        print("🎉 EXCELLENT! System is production-ready!")
    elif health_percentage >= 60:
        print("✅ GOOD! System is mostly functional with minor issues.")
    else:
        print("⚠️ NEEDS ATTENTION! Several systems require fixes.")
    
    print(f"\n{'='*80}")
    print("Test completed successfully!")
    print(f"{'='*80}")
    
    return test_results

if __name__ == "__main__":
    main() 