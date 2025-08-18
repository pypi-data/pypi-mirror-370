"""
United LLM API Client

A simple client for interacting with the United LLM API service.
"""

import requests
import json
from typing import Dict, Any, List, Optional, Union


class UnitedLLMClient:
    """Client for the United LLM API service"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:8818"):
        """
        Initialize the United LLM API client.
        
        Args:
            api_url: Base URL for the API service (default: http://127.0.0.1:8818)
        """
        self.api_url = api_url.rstrip('/')
        
    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        enable_search: bool = False,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Generate text using the LLM with a simple string schema.

        Args:
            prompt: The input prompt
            model: Model to use (defaults to server's default model)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (not used by current API)
            enable_search: Whether to enable web search
            timeout: Request timeout in seconds

        Returns:
            Response dictionary with text and metadata
        """
        # Use a simple string schema for plain text generation
        payload = {
            "prompt": prompt,
            "schema_definition": "string",  # Simple string schema
            "temperature": temperature,
            "max_retries": 1,
            "enable_web_search": enable_search
        }

        if model:
            payload["model"] = model

        response = requests.post(
            f"{self.api_url}/generate/dict",
            json=payload,
            timeout=timeout
        )

        if response.status_code != 200:
            self._handle_error_response(response)

        result = response.json()

        # Extract the text from the structured response
        if result.get("success") and "data" in result:
            # For simple string schema, the data might be wrapped in a dict with 'string' key
            data = result["data"]
            if isinstance(data, dict) and "string" in data:
                text = data["string"]
            else:
                text = data

            return {
                "text": text,
                "model_used": result.get("model_used"),
                "search_used": result.get("search_used"),
                "generation_time": result.get("generation_time")
            }
        else:
            raise Exception(result.get("error", "Unknown error occurred"))
    
    def generate_structured(
        self,
        prompt: str,
        schema: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 3,
        enable_search: bool = False,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Generate structured output using string schema.

        Args:
            prompt: The input prompt
            schema: String schema definition (e.g., "{name, age:int, email?}")
            model: Model to use (defaults to server's default model)
            temperature: Sampling temperature (0.0 to 1.0)
            max_retries: Maximum number of retries
            enable_search: Whether to enable web search
            timeout: Request timeout in seconds

        Returns:
            Response dictionary with structured result and metadata
        """
        payload = {
            "prompt": prompt,
            "schema_definition": schema,
            "temperature": temperature,
            "max_retries": max_retries,
            "enable_web_search": enable_search
        }

        if model:
            payload["model"] = model

        response = requests.post(
            f"{self.api_url}/generate/dict",
            json=payload,
            timeout=timeout
        )

        if response.status_code != 200:
            self._handle_error_response(response)

        result = response.json()

        # Return the structured result with metadata
        if result.get("success"):
            return {
                "result": result.get("data"),
                "model_used": result.get("model_used"),
                "search_used": result.get("search_used"),
                "generation_time": result.get("generation_time"),
                "schema_used": result.get("schema_used")
            }
        else:
            raise Exception(result.get("error", "Unknown error occurred"))
    
    def get_models(self) -> Dict[str, Any]:
        """
        Get available models from the API.
        
        Returns:
            Dictionary with available models information
        """
        response = requests.get(f"{self.api_url}/models")
        
        if response.status_code != 200:
            self._handle_error_response(response)
            
        return response.json()
    
    def get_health(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Dictionary with health information
        """
        response = requests.get(f"{self.api_url}/health")
        
        if response.status_code != 200:
            self._handle_error_response(response)
            
        return response.json()
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle error responses from the API"""
        try:
            error_data = response.json()
            error_message = error_data.get('detail', f"API error: {response.status_code}")
        except:
            error_message = f"API error: {response.status_code} - {response.text}"
            
        raise Exception(error_message)


# Example usage
if __name__ == "__main__":
    # Create client
    client = UnitedLLMClient()
    
    # Check health
    try:
        health = client.get_health()
        print(f"API Status: {health['status']}")
    except Exception as e:
        print(f"Health check failed: {e}")
        exit(1)
    
    # Get available models
    try:
        models_info = client.get_models()
        print(f"Available models: {', '.join([m['model_name'] for m in models_info['models']])}")
    except Exception as e:
        print(f"Failed to get models: {e}")
    
    # Generate text
    try:
        result = client.generate_text(
            prompt="Explain quantum computing in simple terms",
            model="gpt-4o-mini",
            temperature=0.5,
            enable_search=True  # Enable web search
        )
        print("\nText Generation:")
        print(result['text'])
    except Exception as e:
        print(f"Text generation failed: {e}")
    
    # Generate structured output
    try:
        schema = "{summary:string, key_points:string[], difficulty_level:string}"
        result = client.generate_structured(
            prompt="Explain CRISPR gene editing technology",
            schema=schema,
            enable_search=True  # Enable web search
        )
        print("\nStructured Generation:")
        print(json.dumps(result['result'], indent=2))
    except Exception as e:
        print(f"Structured generation failed: {e}")