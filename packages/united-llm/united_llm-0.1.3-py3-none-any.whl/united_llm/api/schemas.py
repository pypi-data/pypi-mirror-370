"""
API Schemas for United LLM FastAPI Server
Request and response models for structured LLM interactions.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum


class SearchType(str, Enum):
    """Available search types"""

    NONE = "none"
    ANTHROPIC = "anthropic"
    DUCKDUCKGO = "duckduckgo"


class DictGenerationRequest(BaseModel):
    """Request model for dict-based generation using string schemas with new curly brace syntax"""

    prompt: str = Field(..., description="The input prompt for generation", min_length=1)
    schema_definition: str = Field(
        ..., description="String schema definition with JSON-consistent syntax", min_length=1
    )
    model: Optional[str] = Field(None, description="Model to use (defaults to configured default)")
    temperature: float = Field(0.0, description="Sampling temperature", ge=0.0, le=2.0)
    max_retries: int = Field(1, description="Maximum number of retries", ge=0, le=5)
    search_type: SearchType = Field(SearchType.NONE, description="Type of web search to use")
    fallback_models: Optional[List[str]] = Field(None, description="Fallback models to try if primary fails")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Create a user profile for John Doe, 30 years old, john@example.com",
                "schema_definition": "{name, age:int, email?}",
                "model": "gpt-4o-mini",
                "temperature": 0.0,
                "search_type": "none",
            },
            "examples": [
                {
                    "summary": "Single object (NEW syntax)",
                    "value": {
                        "prompt": "Create user profile: John Doe, 30, john@example.com",
                        "schema_definition": "{name, age:int, email?}",
                        "model": "gpt-4o-mini",
                    },
                },
                {
                    "summary": "Array of objects (NEW syntax)",
                    "value": {
                        "prompt": "Extract team members: Alice (Developer), Bob (Designer)",
                        "schema_definition": "[{name, role}]",
                        "model": "gpt-4o-mini",
                    },
                },
                {
                    "summary": "Nested structures (NEW syntax)",
                    "value": {
                        "prompt": "Create team data with members",
                        "schema_definition": "{team, members:[{name, role}]}",
                        "model": "gpt-4o-mini",
                    },
                },
                {
                    "summary": "Simple arrays (NEW syntax)",
                    "value": {
                        "prompt": "List programming languages",
                        "schema_definition": "[string]",
                        "model": "gpt-4o-mini",
                    },
                },
                {
                    "summary": "Complex nested (NEW syntax)",
                    "value": {
                        "prompt": "Create order with items",
                        "schema_definition": "{order_id, customer, items:[{product, quantity:int, price:number}]}",
                        "model": "gpt-4o-mini",
                    },
                },
                {
                    "summary": "Legacy format (still works)",
                    "value": {
                        "prompt": "Extract: John Doe, 30, john@example.com",
                        "schema_definition": "name, age:int, email?",
                        "model": "gpt-4o-mini",
                    },
                },
            ],
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Extract information about the latest AI developments",
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Main title"},
                        "summary": {"type": "string", "description": "Brief summary"},
                        "key_points": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of key points",
                        },
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1, "description": "Confidence score"},
                    },
                    "required": ["title", "summary", "key_points"],
                },
                "model": "gpt-3.5-turbo",
                "temperature": 0.1,
                "search_type": "duckduckgo",
            }
        }
    )

    @field_validator("search_type")
    @classmethod
    def validate_search_type(cls, value, info):
        """Validate search type based on model"""
        if value == SearchType.ANTHROPIC and info.data and "model" in info.data:
            model = info.data["model"]
            if model and not any(anthropic_model in model for anthropic_model in ["claude"]):
                raise ValueError("Anthropic search can only be used with Anthropic (Claude) models")
        return value


class DictGenerationResponse(BaseModel):
    """Response model for dict-based generation (returns plain dictionaries)"""

    success: bool = Field(..., description="Whether the generation was successful")
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]], List[Any]]] = Field(
        None, description="Generated data as plain Python dict/list"
    )
    model_used: Optional[str] = Field(None, description="Model that was actually used")
    search_used: Optional[str] = Field(None, description="Search type that was used")
    generation_time: float = Field(..., description="Time taken for generation in seconds")
    token_usage: Optional[Dict[str, int]] = Field(None, description="Token usage statistics")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    schema_used: Optional[Dict[str, Any]] = Field(None, description="JSON Schema that was used for validation")
    string_schema: Optional[str] = Field(None, description="Original string schema used")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "summary": "Single object response",
                    "value": {
                        "success": True,
                        "data": {"name": "John Doe", "age": 30, "email": "john@example.com"},
                        "model_used": "gpt-4o-mini",
                        "generation_time": 1.2,
                        "string_schema": "{name, age:int, email?}",
                    },
                },
                {
                    "summary": "Array of objects response",
                    "value": {
                        "success": True,
                        "data": [{"name": "Alice", "role": "Developer"}, {"name": "Bob", "role": "Designer"}],
                        "model_used": "gpt-4o-mini",
                        "generation_time": 1.5,
                        "string_schema": "[{name, role}]",
                    },
                },
                {
                    "summary": "Nested structure response",
                    "value": {
                        "success": True,
                        "data": {
                            "team": "Engineering",
                            "members": [{"name": "Alice", "role": "Developer"}, {"name": "Bob", "role": "Designer"}],
                        },
                        "model_used": "gpt-4o-mini",
                        "generation_time": 2.1,
                        "string_schema": "{team, members:[{name, role}]}",
                    },
                },
            ]
        }
    )


class ModelInfo(BaseModel):
    """Information about a specific model"""

    model_name: str = Field(..., description="Name of the model")
    provider: str = Field(..., description="Provider (openai, anthropic, google, ollama)")
    configured: bool = Field(..., description="Whether the model is properly configured")
    supports_anthropic_web_search: bool = Field(False, description="Whether model supports Anthropic web search")
    supports_duckduckgo_search: bool = Field(True, description="Whether model supports DuckDuckGo search")
    error: Optional[str] = Field(None, description="Configuration error if any")


class ModelsResponse(BaseModel):
    """Response model for available models"""

    models: List[ModelInfo] = Field(..., description="List of available models")
    default_model: str = Field(..., description="Default model name")
    configured_providers: List[str] = Field(..., description="List of configured providers")


class GroupedModelsResponse(BaseModel):
    """Response model for models grouped by provider"""

    grouped_models: Dict[str, List[str]] = Field(
        ..., description="Models grouped by provider (anthropic, google, openai, ollama)"
    )
    default_model: str = Field(..., description="Default model name")
    configured_providers: List[str] = Field(..., description="List of configured providers")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grouped_models": {
                    "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
                    "google": ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest"],
                    "openai": ["gpt-4o", "gpt-4o-mini"],
                    "ollama": ["llama3.2:3b", "qwen3:0.6b", "mistral:7b"],
                },
                "default_model": "gpt-4o-mini",
                "configured_providers": ["anthropic", "google", "openai", "ollama"],
            }
        }
    )


class HealthResponse(BaseModel):
    """Response model for health check"""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current timestamp")
    configured_providers: List[str] = Field(..., description="List of configured providers")
    available_models_count: int = Field(..., description="Number of available models")


class SchemaValidationRequest(BaseModel):
    """Request model for schema validation"""

    json_schema: Dict[str, Any] = Field(..., description="JSON Schema to validate")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "json_schema": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "age": {"type": "integer", "minimum": 0}},
                    "required": ["name"],
                }
            }
        }
    )


class SchemaValidationResponse(BaseModel):
    """Response model for schema validation"""

    valid: bool = Field(..., description="Whether the schema is valid")
    errors: Dict[str, str] = Field(default_factory=dict, description="Validation errors if any")
    example: Optional[Dict[str, Any]] = Field(None, description="Generated example data")

    model_config = ConfigDict(
        json_schema_extra={"example": {"valid": True, "errors": {}, "example": {"name": "John Doe", "age": 30}}}
    )


class StringSchemaValidationRequest(BaseModel):
    """Request model for string schema validation"""

    schema_definition: str = Field(..., description="String schema to validate (e.g., 'name:string, age:int')")
    is_list: bool = Field(False, description="Whether this is for a list of objects")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"schema_definition": "name, age:int(0,120), email?", "is_list": False},
            "examples": [
                {
                    "summary": "Single object",
                    "value": {"schema_definition": "name, age:int(0,120), email?", "is_list": False},
                },
                {"summary": "Ultra-simple array", "value": {"schema_definition": "[name, email]", "is_list": False}},
                {
                    "summary": "Array with constraints",
                    "value": {"schema_definition": "[name:string(1,50), price:number(0,1000)]", "is_list": False},
                },
            ],
        }
    )


class StringSchemaValidationResponse(BaseModel):
    """Response model for string schema validation"""

    valid: bool = Field(..., description="Whether the string schema is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors if any")
    parsed_fields: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Parsed field information")
    generated_schema: Optional[Dict[str, Any]] = Field(None, description="Generated JSON Schema")
    optimized_string: Optional[str] = Field(None, description="Optimized string schema")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "valid": True,
                "errors": [],
                "parsed_fields": {
                    "name": {"type": "string", "required": True, "constraints": {}},
                    "age": {"type": "integer", "required": True, "constraints": {"minimum": 0, "maximum": 120}},
                },
                "generated_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer", "minimum": 0, "maximum": 120},
                    },
                    "required": ["name", "age"],
                },
                "optimized_string": "name:string, age:int(0,120)",
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response model"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "ValidationError",
                "message": "Invalid JSON schema provided",
                "details": {"field": "schema.properties.age.type", "reason": "Invalid type specified"},
                "timestamp": "2024-01-01T12:00:00Z",
            }
        }
    )


class SearchTestRequest(BaseModel):
    """Request model for testing search functionality"""

    query: str = Field(..., description="Search query to test", min_length=1)
    search_type: SearchType = Field(..., description="Type of search to test")
    model: Optional[str] = Field(None, description="Model to use for search optimization")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "latest developments in artificial intelligence",
                "search_type": "duckduckgo",
                "model": "gpt-3.5-turbo",
            }
        }
    )


class SearchTestResponse(BaseModel):
    """Response model for search testing"""

    success: bool = Field(..., description="Whether search was successful")
    optimized_query: Optional[str] = Field(None, description="Optimized search query")
    results_count: int = Field(0, description="Number of search results found")
    search_time: float = Field(..., description="Time taken for search in seconds")
    results_preview: Optional[List[Dict[str, str]]] = Field(None, description="Preview of search results")
    error: Optional[str] = Field(None, description="Error message if search failed")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "optimized_query": "artificial intelligence developments 2024",
                "results_count": 5,
                "search_time": 2.1,
                "results_preview": [
                    {
                        "title": "AI Breakthroughs in 2024",
                        "url": "https://example.com/ai-2024",
                        "snippet": "Latest developments in AI technology...",
                    }
                ],
            }
        }
    )


class ConfigUpdateRequest(BaseModel):
    """Request model for updating configuration"""

    setting_name: str = Field(..., description="Name of the setting to update")
    setting_value: Union[str, int, float, bool, List[str]] = Field(..., description="New value for the setting")

    @field_validator("setting_name")
    @classmethod
    def validate_setting_name(cls, value):
        allowed_settings = {
            "default_model",
            "temperature",
            "max_retries",
            "duckduckgo_max_results",
            "duckduckgo_timeout",
            "rate_limit_requests",
            "log_level",
        }
        if value not in allowed_settings:
            raise ValueError(f"Setting '{value}' is not allowed to be updated via API")
        return value


class ConfigUpdateResponse(BaseModel):
    """Response model for configuration updates"""

    success: bool = Field(..., description="Whether the update was successful")
    setting_name: str = Field(..., description="Name of the updated setting")
    old_value: Optional[Any] = Field(None, description="Previous value")
    new_value: Any = Field(..., description="New value")
    message: str = Field(..., description="Update result message")


class StatsResponse(BaseModel):
    """Response model for API statistics"""

    total_requests: int = Field(..., description="Total number of requests processed")
    successful_requests: int = Field(..., description="Number of successful requests")
    failed_requests: int = Field(..., description="Number of failed requests")
    average_response_time: float = Field(..., description="Average response time in seconds")
    models_usage: Dict[str, int] = Field(..., description="Usage count by model")
    search_usage: Dict[str, int] = Field(..., description="Usage count by search type")
    uptime_seconds: float = Field(..., description="API uptime in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_requests": 150,
                "successful_requests": 145,
                "failed_requests": 5,
                "average_response_time": 2.3,
                "models_usage": {"gpt-3.5-turbo": 80, "claude-3-haiku": 45, "qwen3:4b": 25},
                "search_usage": {"none": 90, "duckduckgo": 45, "anthropic": 15},
                "uptime_seconds": 86400,
            }
        }
    )


class UnifiedGenerationRequest(BaseModel):
    """United request model that accepts both JSON Schema and string schema definitions"""

    prompt: str = Field(..., description="The input prompt for generation", min_length=1)
    schema_data: Union[Dict[str, Any], str] = Field(
        ..., alias="schema", description="Schema definition - can be JSON Schema (dict) or string schema (str)"
    )
    model: Optional[str] = Field(None, description="Model to use (defaults to configured default)")
    temperature: float = Field(0.0, description="Sampling temperature", ge=0.0, le=2.0)
    max_retries: int = Field(1, description="Maximum number of retries", ge=0, le=5)
    enable_web_search: bool = Field(
        False, description="Enable web search (automatically chooses best search method for model)"
    )
    fallback_models: Optional[List[str]] = Field(None, description="Fallback models to try if primary fails")

    # Keep search_type for backward compatibility but make it optional
    search_type: Optional[SearchType] = Field(None, description="[DEPRECATED] Use enable_web_search instead")
    is_list: bool = Field(False, description="Whether to generate a list of objects (only applies to string schemas)")

    @field_validator("schema_data", mode="before")
    @classmethod
    def validate_schema_format(cls, value):
        """Validate that schema is either a valid JSON Schema dict or a string schema"""
        if isinstance(value, dict):
            # Basic JSON Schema validation - must have 'type' property
            if "type" not in value:
                raise ValueError("JSON Schema must have a 'type' property")
            return value
        elif isinstance(value, str):
            # Basic string schema validation - must not be empty
            if not value.strip():
                raise ValueError("String schema cannot be empty")
            return value.strip()
        else:
            raise ValueError("Schema must be either a JSON Schema (dict) or string schema (str)")

    def is_json_schema(self) -> bool:
        """Check if the schema is a JSON Schema (dict) or string schema"""
        return isinstance(self.schema_data, dict)

    def get_json_schema(self) -> Dict[str, Any]:
        """Get the schema as a JSON Schema dict"""
        if self.is_json_schema():
            return self.schema_data
        else:
            raise ValueError("Schema is a string schema, not JSON Schema")

    def get_schema_definition(self) -> str:
        """Get the schema as a string definition"""
        if not self.is_json_schema():
            return self.schema_data
        else:
            raise ValueError("Schema is a JSON Schema, not string definition")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Extract user information: John Doe, 30 years old, john@example.com",
                "schema": "name, age:int, email?",
                "model": "gpt-4o-mini",
                "temperature": 0.0,
                "search_type": "none",
            },
            "examples": [
                {
                    "summary": "String schema (simple)",
                    "value": {
                        "prompt": "Extract: John Doe, 30, john@example.com",
                        "schema": "name, age:int, email?",
                        "model": "gpt-4o-mini",
                    },
                },
                {
                    "summary": "String schema (curly brace syntax)",
                    "value": {
                        "prompt": "Create user profile: John Doe, 30, john@example.com",
                        "schema": "{name, age:int, email?}",
                        "model": "gpt-4o-mini",
                    },
                },
                {
                    "summary": "String schema (array)",
                    "value": {
                        "prompt": "Extract team members: Alice (Developer), Bob (Designer)",
                        "schema": "[{name, role}]",
                        "model": "gpt-4o-mini",
                    },
                },
                {
                    "summary": "JSON Schema",
                    "value": {
                        "prompt": "Extract user information",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "age": {"type": "integer", "minimum": 0},
                                "email": {"type": "string", "format": "email"},
                            },
                            "required": ["name", "age"],
                        },
                        "model": "gpt-4o-mini",
                    },
                },
            ],
        }
    )
