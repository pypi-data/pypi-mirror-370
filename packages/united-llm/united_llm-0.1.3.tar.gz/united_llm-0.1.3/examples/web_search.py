#!/usr/bin/env python3
"""
Web Search Integration Example - United LLM
Demonstrates DuckDuckGo and Anthropic web search capabilities.
"""

from pydantic import BaseModel
from typing import List
from united_llm import LLMClient

# Output models for search results
class NewsArticle(BaseModel):
    title: str
    summary: str
    key_points: List[str]
    relevance_score: float

class TechTrend(BaseModel):
    trend_name: str
    description: str
    impact_level: str  # "High", "Medium", "Low"
    related_technologies: List[str]

def main():
    """Web search examples"""
    print("🔍 United LLM - Web Search Examples")
    print("=" * 50)
    
    # Initialize client
    client = LLMClient()
    
    print("📋 Example 1: DuckDuckGo Search (Works with any model)")
    print("-" * 40)
    
    try:
        result = client.generate_structured(
            prompt="What are the latest developments in artificial intelligence in 2024?",
            output_model=NewsArticle,
            model="gpt-4o-mini",
            duckduckgo_search=True  # Enable DuckDuckGo search
        )
        
        print(f"✅ Success!")
        print(f"Title: {result.title}")
        print(f"Summary: {result.summary}")
        print(f"Key Points: {len(result.key_points)} points")
        for i, point in enumerate(result.key_points[:3], 1):
            print(f"  {i}. {point}")
        print(f"Relevance Score: {result.relevance_score}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have internet connectivity and API keys configured")
    
    print("\n📋 Example 2: Anthropic Web Search (Anthropic models only)")
    print("-" * 40)
    
    try:
        result = client.generate_structured(
            prompt="Current trends in machine learning and deep learning research",
            output_model=TechTrend,
            model="claude-sonnet-4-20250514",  # Use valid Anthropic model
            anthropic_web_search=True  # Enable Anthropic web search
        )
        
        print(f"✅ Success!")
        print(f"Trend: {result.trend_name}")
        print(f"Description: {result.description}")
        print(f"Impact Level: {result.impact_level}")
        print(f"Related Technologies: {', '.join(result.related_technologies)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have Anthropic API key configured")
    
    print("\n📋 Example 3: Chinese Text Search (Auto-optimized)")
    print("-" * 40)
    
    try:
        result = client.generate_structured(
            prompt="分析最新的人工智能技术趋势和发展方向",
            output_model=TechTrend,
            model="gpt-4o-mini",
            duckduckgo_search=True  # Automatically optimizes Chinese queries
        )
        
        print(f"✅ Success!")
        print(f"趋势名称: {result.trend_name}")
        print(f"描述: {result.description}")
        print(f"影响程度: {result.impact_level}")
        print(f"相关技术: {', '.join(result.related_technologies)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📋 Example 4: Dictionary Output with Search")
    print("-" * 40)
    
    try:
        result = client.generate_dict(
            prompt="Find the latest news about renewable energy developments",
            schema="{title, summary, main_points:[string], confidence:float}",
            model="gpt-4o-mini",
            duckduckgo_search=True
        )
        
        print(f"✅ Success!")
        print(f"Title: {result['title']}")
        print(f"Summary: {result['summary'][:100]}...")
        print(f"Main Points: {len(result['main_points'])} points")
        print(f"Confidence: {result['confidence']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n💡 Search Tips:")
    print("• DuckDuckGo search works with any model (OpenAI, Google, Ollama, etc.)")
    print("• Anthropic web search only works with Anthropic models")
    print("• Chinese text is automatically optimized for better search results")
    print("• Search results are integrated into the LLM's context for better responses")
    print("• Both search types work with structured outputs and dictionary generation")

if __name__ == "__main__":
    main() 