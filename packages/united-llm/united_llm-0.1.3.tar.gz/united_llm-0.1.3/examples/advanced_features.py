#!/usr/bin/env python3
"""
Advanced Features Example - United LLM
Demonstrates advanced configuration, fallbacks, and usage patterns.
"""

from pydantic import BaseModel
from typing import List, Optional
from united_llm import LLMClient, get_settings, get_effective_config

# Complex output models
class CompanyAnalysis(BaseModel):
    company_name: str
    industry: str
    strengths: List[str]
    weaknesses: List[str]
    market_position: str
    growth_potential: float  # 0.0 to 1.0
    recommendations: List[str]

class TechnicalDocument(BaseModel):
    title: str
    abstract: str
    key_concepts: List[str]
    difficulty_level: str  # "Beginner", "Intermediate", "Advanced"
    estimated_reading_time: int  # minutes
    prerequisites: Optional[List[str]] = None

def main():
    """Advanced usage examples"""
    print("⚡ United LLM - Advanced Features")
    print("=" * 50)
    
    print("📋 Example 1: Custom Configuration")
    print("-" * 40)
    
    # Smart config merging - only override what you need
    custom_client = LLMClient(config={
        'log_calls': True,  # Enable logging
        'temperature': 0.2,  # Lower temperature for more consistent results
        'max_tokens': 500,   # Limit response length
        'timeout': 60        # Longer timeout for complex requests
    })
    
    print("✅ Client created with custom config")
    print("💡 Only specified settings are overridden, rest comes from bootstrap")
    
    print("\n📋 Example 2: Configuration Debugging")
    print("-" * 40)
    
    # Debug configuration
    settings = get_settings()
    effective_config = get_effective_config()
    
    print(f"Configured providers: {settings.get_configured_providers()}")
    print(f"Available models: {len(settings.get_available_models())} models")
    print(f"Final config keys: {len(effective_config)} settings")
    print(f"Logging enabled: {effective_config.get('log_calls', False)}")
    
    print("\n📋 Example 3: Model Fallback Strategy")
    print("-" * 40)
    
    try:
        # Try multiple models in order of preference
        result = custom_client.generate_structured(
            prompt="Analyze Tesla as a company: strengths, weaknesses, market position, and growth potential",
            output_model=CompanyAnalysis,
            model="gpt-4o"  # Will try this model first
        )
        
        print(f"✅ Success with fallback strategy!")
        print(f"Company: {result.company_name}")
        print(f"Industry: {result.industry}")
        print(f"Market Position: {result.market_position}")
        print(f"Growth Potential: {result.growth_potential:.1%}")
        print(f"Strengths: {len(result.strengths)} identified")
        print(f"Recommendations: {len(result.recommendations)} provided")
        
    except Exception as e:
        print(f"❌ All models failed: {e}")
    
    print("\n📋 Example 4: Complex Schema with Validation")
    print("-" * 40)
    
    try:
        result = custom_client.generate_structured(
            prompt="Create a technical document about quantum computing for intermediate learners",
            output_model=TechnicalDocument,
            model="gpt-4o-mini"
        )
        
        print(f"✅ Success!")
        print(f"Title: {result.title}")
        print(f"Abstract: {result.abstract[:100]}...")
        print(f"Difficulty: {result.difficulty_level}")
        print(f"Reading Time: {result.estimated_reading_time} minutes")
        print(f"Key Concepts: {len(result.key_concepts)} concepts")
        if result.prerequisites:
            print(f"Prerequisites: {', '.join(result.prerequisites)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📋 Example 5: Batch Processing with Different Models")
    print("-" * 40)
    
    # Process multiple requests with different models
    tasks = [
        {
            "prompt": "Analyze Google as a tech company",
            "model": "gpt-4o-mini",
            "description": "OpenAI Analysis"
        },
        {
            "prompt": "Analyze Microsoft's business strategy",
            "model": "claude-sonnet-4-20250514", 
            "description": "Anthropic Analysis"
        },
        {
            "prompt": "Evaluate Amazon's market dominance",
            "model": "gemini-1.5-flash-latest",
            "description": "Google Analysis"
        }
    ]
    
    for i, task in enumerate(tasks, 1):
        try:
            result = custom_client.generate_structured(
                prompt=task["prompt"],
                output_model=CompanyAnalysis,
                model=task["model"]
            )
            print(f"✅ Task {i} ({task['description']}): {result.company_name}")
            
        except Exception as e:
            print(f"❌ Task {i} failed: {str(e)[:50]}...")
    
    print("\n📋 Example 6: Advanced Dictionary Generation")
    print("-" * 40)
    
    try:
        # Complex nested structure with curly brace syntax
        result = custom_client.generate_dict(
            prompt="Create a software project plan with team, timeline, and tasks",
            schema="""{
                project_name,
                team_lead,
                team_members:[{name, role, experience_years:int}],
                timeline:{start_date, end_date, total_weeks:int},
                tasks:[{task_name, assigned_to, priority, estimated_hours:int}],
                budget:float,
                success_metrics:[string]
            }""",
            model="gpt-4o-mini"
        )
        
        print(f"✅ Success!")
        print(f"Project: {result['project_name']}")
        print(f"Team Lead: {result['team_lead']}")
        print(f"Team Size: {len(result['team_members'])} members")
        print(f"Duration: {result['timeline']['total_weeks']} weeks")
        print(f"Tasks: {len(result['tasks'])} tasks planned")
        print(f"Budget: ${result['budget']:,.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n💡 Advanced Tips:")
    print("• Use get_effective_config() to debug final merged configuration")
    print("• Smart config merging: only override settings you need to change")
    print("• Model fallback provides reliability across different providers")
    print("• Complex nested schemas work with both Pydantic and dictionary output")
    print("• Batch processing allows you to use different models for different tasks")
    print("• Custom clients can have different configurations for different use cases")

if __name__ == "__main__":
    main() 