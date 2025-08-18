"""
United LLM - A comprehensive LLM client with search capabilities and FastAPI server.

This package provides:
- Enhanced LLM client supporting multiple providers (OpenAI, Anthropic, Google, Ollama)
- Web search integration (Anthropic web search, DuckDuckGo 3-step search)
- FastAPI HTTP server with structured outputs
- JSON Schema to Pydantic model conversion
- Chinese text optimization
- Comprehensive configuration management
"""

__version__ = "0.1.3"
__author__ = "United LLM Team"
__email__ = "contact@united-llm.com"

# Core exports
from .client import LLMClient, ImageInput  # noqa: F401

# Configuration exports (direct re-export from zero-config)
from .config import (  # noqa: F401
    setup_environment,
    get_config,
    is_initialized,
    get_initialization_info,
    setup_united_llm_environment,
    UNITED_LLM_DEFAULTS,
)

# Database exports
from .utils.database import LLMDatabase, LLMCallRecord  # noqa: F401

# Schema utilities from string-schema package
import string_schema  # noqa: F401
from string_schema import (  # noqa: F401
    # Core schema conversion functions
    json_schema_to_pydantic,
    json_schema_to_model,
    parse_string_schema,
    validate_string_schema,
    string_to_json_schema,
    string_to_model,
    validate_to_dict,
    validate_to_model,
    # Utility functions
    validate_string_syntax,
    get_model_info,
)

# Define SchemaConversionError for backward compatibility
class SchemaConversionError(Exception):
    """Raised when schema conversion fails"""
    pass

# API exports
from .api.schemas import (  # noqa: F401
    DictGenerationRequest,
    DictGenerationResponse,
    UnifiedGenerationRequest,
    SearchType,
    ModelsResponse,
    HealthResponse,
)

# Search exports (imported conditionally to handle missing dependencies)
__all_exports__ = []

try:
    from .search.duckduckgo_search import DuckDuckGoSearch  # noqa: F401

    __all_exports__.append("DuckDuckGoSearch")
except ImportError:
    pass


# Convenience functions for backward compatibility
def data_path(filename: str = "") -> str:
    """Get data directory path."""
    return get_config().data_path(filename)


def logs_path(filename: str = "") -> str:
    """Get logs directory path."""
    return get_config().logs_path(filename)


# Enhanced compatibility functions using string-schema package
def validate_json_schema(schema):
    """Validate JSON Schema using string-schema package"""
    errors = {}

    # Basic validation
    if not isinstance(schema, dict):
        errors["schema"] = "Must be a dictionary"
        return errors

    # Use string-schema package for comprehensive validation
    try:
        # Convert to string schema and validate
        string_schema_str = string_schema.json_schema_to_string(schema)
        validation = string_schema.validate_string_schema(string_schema_str)

        if not validation["valid"]:
            errors["validation"] = f"Schema validation failed: {', '.join(validation['errors'])}"

        # Try to create a model to ensure it's valid for Pydantic
        try:
            string_schema.json_schema_to_model(schema, "ValidationTestModel")
        except Exception as e:
            errors["model_creation"] = f"Cannot create Pydantic model: {str(e)}"

    except Exception as e:
        errors["conversion"] = f"Schema processing failed: {str(e)}"

    return errors


def create_example_from_schema(schema):
    """Create example from JSON Schema using string-schema package"""
    try:
        # Use string-schema package to create a proper model and example
        model = string_schema.json_schema_to_model(schema, "ExampleModel")

        # Create example data based on schema properties
        example = {}
        properties = schema.get("properties", {})

        for prop_name, prop_schema in properties.items():
            prop_type = prop_schema.get("type")
            if prop_type == "string":
                example[prop_name] = "example string"
            elif prop_type == "integer":
                example[prop_name] = 42
            elif prop_type == "number":
                example[prop_name] = 42.5
            elif prop_type == "boolean":
                example[prop_name] = True
            elif prop_type == "array":
                example[prop_name] = []
            elif prop_type == "object":
                example[prop_name] = {}

        # Validate the example against the model to ensure correctness
        validated_example = model(**example)
        return validated_example.model_dump()

    except Exception:
        # Fallback to basic example creation if string-schema fails
        if not isinstance(schema, dict) or schema.get("type") != "object":
            return {}

        example = {}
        properties = schema.get("properties", {})

        for prop_name, prop_schema in properties.items():
            prop_type = prop_schema.get("type")
            if prop_type == "string":
                example[prop_name] = "example string"
            elif prop_type == "integer":
                example[prop_name] = 42
            elif prop_type == "number":
                example[prop_name] = 42.5
            elif prop_type == "boolean":
                example[prop_name] = True
            elif prop_type == "array":
                example[prop_name] = []
            elif prop_type == "object":
                example[prop_name] = {}

        return example


__all__ = [
    # Core
    "LLMClient",
    "ImageInput",
    # Configuration (bootstrap system)
    "setup_environment",
    "get_config",
    "data_path",
    "logs_path",
    # Database
    "LLMDatabase",
    "LLMCallRecord",
    # Schema utilities (from string-schema package)
    "json_schema_to_pydantic",
    "json_schema_to_model",
    "parse_string_schema",
    "validate_string_schema",
    "string_to_json_schema",
    "string_to_model",
    "validate_to_dict",
    "validate_to_model",
    "validate_string_syntax",
    "get_model_info",
    "validate_json_schema",
    "create_example_from_schema",
    "SchemaConversionError",
    # API
    "DictGenerationRequest",
    "DictGenerationResponse",
    "UnifiedGenerationRequest",
    "SearchType",
    "ModelsResponse",
    "HealthResponse",
    # Version
    "__version__",
] + __all_exports__

# Package metadata
__package_info__ = {
    "name": "united-llm",
    "version": __version__,
    "description": "United LLM client with search capabilities and FastAPI server",
    "author": __author__,
    "author_email": __email__,
    "url": "https://github.com/xychenmsn/united-llm",
    "license": "MIT",
    "python_requires": ">=3.8",
    "keywords": ["llm", "openai", "anthropic", "google", "ollama", "fastapi", "search"],
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
}


def get_package_info():
    """Get package information"""
    return __package_info__.copy()


def print_version():
    """Print version information"""
    print(f"United LLM v{__version__}")
    print(f"Author: {__author__}")


# Quick start example
EXAMPLE_USAGE = """
# Quick Start Example

from united_llm import LLMClient, setup_environment
from pydantic import BaseModel

# 1. Basic setup (uses .env.united_llm automatically)
setup_environment()  # Optional - LLMClient does this automatically
client = LLMClient()  # Auto-loads from .env.united_llm

# 2. Define output structure
class UserInfo(BaseModel):
    name: str
    age: int
    city: str

# 3. Generate structured output
result = client.generate_structured(
    prompt="Extract user info: John Doe, 30 years old, from New York",
    output_model=UserInfo,
    model="gpt-3.5-turbo"
)

print(result)  # UserInfo(name="John Doe", age=30, city="New York")

# 4. Simple dict generation (no Pydantic models needed)
dict_result = client.generate_dict(
    prompt="Extract user info: Jane Smith, 25, from Boston",
    schema="{name, age:int, city}",
    model="gpt-4o-mini"
)
print(dict_result)  # {"name": "Jane Smith", "age": 25, "city": "Boston"}

# 5. With search capabilities
result_with_search = client.generate_structured(
    prompt="What are the latest AI developments?",
    output_model=UserInfo,  # Your custom model
    model="gpt-4o-mini",
    duckduckgo_search=True
)

# 6. FastAPI Server
# Run: python -m united_llm.api.server
# Then visit: http://localhost:8818/docs
"""


def print_example():
    """Print usage example"""
    print(EXAMPLE_USAGE)
