# 🛠️ Development Guide

This guide is for developers who want to contribute to the United LLM project or understand its internal architecture.

## 🏗️ Project Architecture

### Core Components

#### 1. LLMClient (`united_llm/client.py`)

The main client class that orchestrates all LLM interactions:

- **Smart Config Merging**: Merges user config with bootstrap defaults
- **Provider Management**: Handles OpenAI, Anthropic, Google, Ollama clients
- **Search Integration**: Coordinates DuckDuckGo and Anthropic web search
- **Logging Orchestration**: Manages database, file, and JSON logging
- **Error Handling**: Implements retry logic and fallback strategies

**Key Methods**:

- `generate_structured()` - Main structured output method
- `generate_dict()` - Returns plain dictionaries (new curly brace syntax)
- `_get_client()` - Provider client factory with caching
- `_log_call()` - Comprehensive logging coordinator

#### 2. Configuration System (`united_llm/config/`)

**Zero-Config Adapter (`zero_config_adapter.py`)**:

- Uses the zero-config library for configuration management
- Loads configuration from multiple sources (.env.united_llm, environment variables)
- Provides complete defaults that get merged with user overrides
- Maintains backward compatibility with the original bootstrap interface

**Settings (`settings.py`)**:

- Pydantic settings for LLM\_\_\* environment variables
- Provider detection and model list management
- `get_settings()` - Returns Pydantic settings (debugging only)
- `get_effective_config()` - Returns final merged config (matches LLMClient)

**Key Insight**: `get_settings()` ≠ LLMClient config. Use `get_effective_config()` for debugging.

#### 3. Schema Processing

**String Schema Package (`string-schema` from PyPI)**:

- Parses curly brace syntax: `{name, age:int}`, `[{name, email}]`
- Converts to JSON Schema for Pydantic model creation
- Handles nested structures and type constraints
- 100% backward compatible with legacy syntax
- Advanced constraint support and validation
- **Used exclusively** - no local schema utilities needed

- Compatibility layer for local schema utilities
- Basic JSON Schema to Pydantic model conversion
- Simple string schema parsing for fallback scenarios

#### 4. Search Integration (`united_llm/search/`)

**DuckDuckGo Search (`duckduckgo_search.py`)**:

- 3-step process: Query optimization → Search → Result integration
- Chinese text optimization with specialized processing
- Rate limit handling and retry strategies
- Works with any LLM model
- Intelligent query optimization based on model capabilities

**Anthropic Search (integrated in client)**:

- Native Anthropic web search using built-in tools
- Only works with Anthropic models (Claude Sonnet 4)
- Integrated directly into the model's context
- Real-time web information retrieval

#### 5. Utilities (`united_llm/utils/`)

**Database & Logging (`database.py`)**:

- SQLite database with automatic schema creation
- Comprehensive call logging with metadata
- Statistics generation and filtering
- Export capabilities (CSV, JSON)
- Efficient querying with indexes

**Model Management (`model_manager.py`)**:

- Simple Ollama model detection via API queries
- Provider detection and validation
- Model availability checking
- No caching - always queries fresh model lists

**Database Schema**:

```sql
CREATE TABLE llm_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    model TEXT NOT NULL,
    provider TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT,
    token_usage TEXT,  -- JSON string
    error TEXT,
    duration_ms INTEGER,
    search_type TEXT,
    request_schema TEXT,  -- JSON string of the schema used
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. FastAPI Server (`united_llm/api/`)

**Server (`server.py`)**:

- Main FastAPI application with all endpoints
- Global exception handling and CORS
- Health checks and statistics endpoints
- Auto-generated OpenAPI documentation

**Admin Interface (`admin.py`)**:

- HTML generation for admin dashboard
- Real-time statistics and analytics
- Request history with filtering and pagination
- CSV/JSON export functionality
- HTTP Basic Auth implementation
- Modal dialogs with tabbed interface (Output/Code tabs)
- Interactive request form with model selection and schema input
- Python code generation for user prompts and schemas

**Schemas (`schemas.py`)**:

- Pydantic request/response models for all endpoints
- Handles the new united schema approach
- Auto-detection of JSON Schema vs string schema
- Search testing request/response models
- Comprehensive error response models

## 🔧 Development Setup

### 1. Environment Setup

```bash
# Clone and setup
git clone https://github.com/xychenmsn/united_llm.git
cd united_llm

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Or install step by step
pip install -e .
pip install pytest pytest-asyncio pytest-cov black flake8 mypy pre-commit
```

### 2. Configuration for Development

Create `.env` file:

```bash
# Development API keys
LLM__OPENAI_API_KEY=your_dev_key
LLM__ANTHROPIC_API_KEY=your_dev_key
LLM__GOOGLE_API_KEY=your_dev_key

# Development settings
LLM__LOG_TO_DB=true
LLM__LOG_CALLS=true
LLM__LOG_LEVEL=DEBUG

# Test database
LLM__DB_PATH=test_llm_calls.db
```

### 3. Running Tests

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run examples (start here!)
python examples/basic_usage.py
python examples/web_search.py
python examples/advanced_features.py

# Run comprehensive tests
python tests/test_integration.py
python tests/test_comprehensive.py

# Run unit tests with pytest (if available)
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=united_llm --cov-report=html

# Test specific functionality
python -c "from united_llm import LLMClient; print('✅ Import successful')"
```

### 4. Development Server

```bash
# Start development server manually
python -m united_llm.api.server

# Or use the console script (after installation)
united-llm-server

# Or use restart script (kills existing processes and restarts)
./restart.sh

# View logs
tail -f logs/api.log

# Check server health
curl http://localhost:8818/health
```

## 🧪 Testing Strategy

### Test Files Structure

**Examples Directory (`examples/`)**:

- `examples/basic_usage.py` - Core functionality and getting started
- `examples/web_search.py` - DuckDuckGo and Anthropic web search integration
- `examples/advanced_features.py` - Configuration, fallbacks, and advanced patterns

**Tests Directory (`tests/`)**:

- `tests/test_integration.py` - Real-world integration testing
- `tests/test_comprehensive.py` - Complete system test with all providers

**Note**: The examples directory has been reorganized for better clarity. Legacy test files may exist but the current structure focuses on clear, educational examples.

### What to Test

1. **Provider Integration**: All 4 providers (OpenAI, Anthropic, Google, Ollama)
2. **Search Functionality**: DuckDuckGo 3-step and Anthropic web search
3. **Schema Processing**: JSON Schema, string schemas, curly brace syntax
4. **Database Logging**: Call recording, statistics, export
5. **Configuration**: Bootstrap, merging, environment variables
6. **Error Handling**: Fallbacks, retries, graceful degradation
7. **Admin Interface**: Dashboard, filtering, authentication
8. **Ollama Function Detection**: Model capability detection and caching
9. **API Endpoints**: All FastAPI endpoints including new united endpoint
10. **Console Scripts**: Command-line tools and server startup

### Test Data Requirements

- Valid API keys for all providers
- Local Ollama installation (optional)
- Test database separate from production
- Network connectivity for search testing

## 🔄 Key Development Patterns

### 1. Smart Config Merging Implementation

```python
# In LLMClient.__init__()
def __init__(self, config: Optional[Dict[str, Any]] = None):
    # 1. Load bootstrap configuration (base)
    bootstrap_config = get_config()

    # 2. Load Pydantic settings (environment variables)
    settings = get_settings()

    # 3. Merge: bootstrap + settings + user overrides
    self.config = {
        **bootstrap_config,  # Base configuration
        **settings.model_dump(),  # Environment overrides
        **(config or {})  # User overrides (highest priority)
    }
```

### 2. Schema Auto-Detection Pattern

```python
def detect_schema_type(schema: Union[Dict[str, Any], str]) -> str:
    """Auto-detect schema type for united endpoint"""
    if isinstance(schema, dict):
        return "json_schema"
    elif isinstance(schema, str):
        if schema.strip().startswith('{') or schema.strip().startswith('['):
            return "curly_brace"
        else:
            return "legacy_string"
    else:
        raise ValueError("Invalid schema type")
```

### 3. Provider Client Factory

```python
def _get_client(self, provider: str):
    """Factory pattern for provider clients with caching"""
    if provider not in self._clients:
        if provider == "openai":
            self._clients[provider] = instructor.from_openai(
                OpenAI(api_key=self.config.get('openai_api_key'))
            )
        elif provider == "anthropic":
            # ... similar pattern

    return self._clients[provider]
```

### 4. Comprehensive Logging Pattern

```python
async def _log_call(self, call_data: Dict[str, Any]):
    """Multi-target logging coordinator"""
    try:
        # Database logging
        if self.config.get('log_to_db'):
            await self.database.log_call(call_data)

        # File logging
        if self.config.get('log_calls'):
            await self._log_to_file(call_data)

        # JSON logging
        if self.config.get('log_json'):
            await self._log_to_json(call_data)

    except Exception as e:
        logger.error(f"Logging failed: {e}")
        # Never let logging failures affect main functionality
```

### 5. Simple Ollama Model Detection Pattern

```python
# Simple Ollama model detection via API
from united_llm.utils import ModelManager

def get_ollama_models(self):
    """Get available Ollama models"""
    if not self.model_manager.has_provider('ollama'):
        return []

    # Simple API query - no caching, no function calling detection
    ollama_base_url = self.config.get('ollama_base_url', 'http://localhost:11434')
    return self.model_manager.get_ollama_models(ollama_base_url)

def _get_ollama_client_for_model(self, model_name: str):
    """Get Ollama client - simplified approach"""
    base_client = self._get_ollama_client()
    # Use JSON mode for all Ollama models (simplified)
    return instructor.patch(base_client, mode=instructor.Mode.JSON)
```

## 🚀 Adding New Features

### 1. Adding a New LLM Provider

1. **Add provider settings** in `united_llm/config/settings.py`
2. **Implement client factory** in `united_llm/client.py`
3. **Add model mappings** and provider detection
4. **Update tests** to include new provider
5. **Add to documentation** and examples

### 2. Adding New Schema Syntax

1. **Extend parser** in `united_llm/utils/string_schemas.py`
2. **Add conversion logic** to JSON Schema
3. **Update united endpoint** in `united_llm/api/server.py`
4. **Add comprehensive tests**
5. **Update API documentation**

### 3. Adding New Search Provider

1. **Create search module** in `united_llm/search/`
2. **Implement 3-step pattern** (optimize → search → integrate)
3. **Add to LLMClient** search parameter handling
4. **Update API schemas** and endpoints
5. **Add tests and documentation**

### 4. Adding Console Scripts

1. **Define entry point** in `setup.py` under `entry_points`
2. **Create CLI module** (e.g., `united_llm/cli.py`)
3. **Implement argument parsing** with argparse or click
4. **Add help documentation** and usage examples
5. **Test installation** with `pip install -e .`

Example entry point:

```python
entry_points={
    "console_scripts": [
        "united-llm=united_llm.cli:main",
        "united-llm-server=united_llm.api.server:main",
    ],
}
```

## 🎨 Admin Interface Development

### Frontend Architecture

The admin interface uses server-side rendered HTML with JavaScript for interactivity:

**Templates Structure**:

- `base.html` - Base layout with navigation and common styles
- `dashboard.html` - Main dashboard with statistics and quick actions
- `admin_dashboard.html` - Admin-specific dashboard features
- `components/modal.html` - Reusable modal dialog with tabbed interface
- `components/modal_scripts.html` - JavaScript for modal functionality

**Key JavaScript Features**:

- **Modal Management**: Stable modal dialogs that only close via explicit actions
- **Tab Switching**: Dynamic switching between Output and Code tabs
- **Code Generation**: Python code generation based on user input
- **Model Selection**: Intelligent default model selection with fallbacks
- **Schema Handling**: Support for JSON Schema and string schema formats

**Development Tips**:

- Modal dialogs automatically refresh the page when closed from requests page
- Default model selection prioritizes: claude-sonnet-4, gpt-4o, gpt-4o-mini
- Code generation detects schema type and generates appropriate client calls
- All forms reset properly when switching between view and send modes

### Adding New Admin Features

1. **Add HTML template** in `united_llm/api/templates/`
2. **Update server routes** in `united_llm/api/server.py`
3. **Add JavaScript functionality** in modal_scripts.html or separate files
4. **Update navigation** in base.html sidebar
5. **Test modal stability** and page refresh behavior

## 🐛 Debugging Common Issues

### Configuration Problems

```python
# Debug configuration issues
from united_llm import setup_environment, get_config

# Check zero-config configuration
setup_environment()
config = get_config()
print(f"Config keys: {list(config.to_dict().keys())}")
print(f"API keys present: {[k for k in config.to_dict() if 'api_key' in k and config.get(k)]}")

# Check specific values
print(f"Default model: {config.get('default_model')}")
print(f"Database path: {config.get_db_path()}")
print(f"Data path: {config.data_path()}")
print(f"Logs path: {config.logs_path()}")
```

### Database Issues

```python
# Check database connection and content
from united_llm import LLMDatabase

db = LLMDatabase()
stats = db.get_statistics()
print(f"Total calls: {stats['total_calls']}")

# Check recent calls
recent = db.get_calls(limit=5)
for call in recent:
    print(f"{call['timestamp']}: {call['model']} - {call.get('error', 'Success')}")
```

### Provider Client Issues

```python
# Test individual providers
client = LLMClient()

# Check which providers are actually configured
for provider in ['openai', 'anthropic', 'google', 'ollama']:
    try:
        provider_client = client._get_client(provider)
        print(f"✅ {provider}: Ready")
    except Exception as e:
        print(f"❌ {provider}: {e}")
```

## 📚 Code Style Guidelines

### 1. Type Hints

```python
# Always use type hints
def generate_structured(
    self,
    prompt: str,
    output_model: Type[BaseModel],
    model: Optional[str] = None,
    **kwargs: Any
) -> BaseModel:
```

### 2. Error Handling

```python
# Comprehensive error handling with logging
try:
    result = await self._make_llm_call(...)
except RateLimitError as e:
    logger.warning(f"Rate limit hit: {e}")
    await asyncio.sleep(self.retry_delay)
    # Retry logic
except Exception as e:
    logger.error(f"LLM call failed: {e}")
    # Fallback or re-raise
```

### 3. Configuration Access

```python
# Always use .get() with defaults for config
max_retries = self.config.get('max_retries', 3)
timeout = self.config.get('timeout', 30)
```

### 4. Logging

```python
# Use structured logging
logger.info(
    "LLM call completed",
    extra={
        'model': model,
        'provider': provider,
        'duration_ms': duration,
        'token_count': tokens
    }
)
```

## 🔒 Security Considerations

### 1. API Key Handling

- Never log API keys (even truncated)
- Store in environment variables only
- Validate presence before client creation
- Support key rotation without restart

### 2. Input Validation

- Validate all user inputs using Pydantic
- Sanitize prompts for logging
- Limit prompt and response sizes
- Validate schema structures

### 3. Admin Interface

- HTTP Basic Auth for admin endpoints
- Configurable admin credentials
- Rate limiting on admin endpoints
- Audit logging for admin actions

## 📦 Release Process

### 1. Version Bumping

- Update version in `setup.py`
- Update version in `united_llm/__init__.py`
- Add changelog entry in README.md

### 2. Testing

- Run comprehensive test suite
- Test with all provider configurations
- Verify admin interface functionality
- Test new features with real API calls

### 3. Documentation

- Update README.md with new features
- Update API documentation
- Add usage examples
- Update development guide if needed

## 🤝 Contributing Guidelines

### 1. Code Changes

- Fork the repository
- Create feature branch: `git checkout -b feature/amazing-feature`
- Follow code style guidelines
- Add comprehensive tests
- Update documentation

### 2. Pull Request Process

- Run full test suite
- Ensure no breaking changes
- Update relevant documentation
- Provide clear PR description
- Include usage examples for new features

### 3. Issue Reporting

- Use issue templates
- Provide minimal reproduction case
- Include configuration details
- Specify expected vs actual behavior

---

**💡 Development Tip**: Always test with multiple providers and both search options to ensure robust functionality across the entire system!
