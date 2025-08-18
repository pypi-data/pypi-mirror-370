# 🚀 United LLM

A comprehensive, production-ready LLM client with multi-provider support, web search integration, structured outputs, and comprehensive logging system.

## ✨ Key Features

- **🔄 Multi-Provider Support**: OpenAI (GPT-4o, GPT-4o-mini), Anthropic (Claude Sonnet 4), Google (Gemini 1.5), and Ollama (Qwen3)
- **🔍 Advanced Web Search**:
  - Anthropic native web search integration
  - DuckDuckGo 3-step search with intelligent query optimization
- **🌐 FastAPI Admin Interface**: RESTful API with automatic documentation and database management
- **📋 Structured Outputs**: Pydantic models with instructor library integration
- **🗄️ Comprehensive Logging**:
  - SQLite database logging with detailed metrics
  - TXT file logging with daily organization
  - JSON structured logs for programmatic analysis
  - Rotating application and server logs
- **⚙️ Smart Configuration**: Environment-based settings with automatic model detection and smart config merging
- **🔧 Production Ready**: Rate limiting, error handling, fallback strategies

## 🏗️ Architecture

```
united_llm/
├── client.py                  # Enhanced LLMClient with search & logging
├── config/
│   ├── settings.py           # Environment-based configuration
│   ├── bootstrap.py          # Bootstrap configuration loader
│   └── logging_config.py     # Comprehensive logging setup
├── search/
│   ├── anthropic_search.py   # Anthropic web search integration
│   └── duckduckgo_search.py  # DuckDuckGo 3-step search
├── utils/
│   ├── database.py           # SQLite logging database
│   ├── schema_converter.py   # JSON Schema ↔ Pydantic conversion

│   ├── schema_utils.py       # Local schema utilities (compatibility layer)
│   └── model_manager.py      # Model detection and management
├── api/
│   ├── server.py             # FastAPI server with admin interface
│   ├── admin.py              # Admin interface implementation
│   └── schemas.py            # Request/response models
└── tests/                    # Comprehensive test suite
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/xychenmsn/united_llm.git
cd united_llm

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode (recommended for development)
pip install -e .

# Optional: Install development dependencies
pip install -e ".[dev]"  # Includes pytest, black, flake8, mypy
```

### 2. Configuration

Create a `.env` file with your API keys:

```bash
# Copy example configuration
cp env_example.txt .env

# Edit with your API keys
LLM__OPENAI_API_KEY=your_openai_key_here
LLM__ANTHROPIC_API_KEY=your_anthropic_key_here
LLM__GOOGLE_API_KEY=your_google_key_here
LLM__OLLAMA_BASE_URL=http://localhost:11434/v1

# Optional: Configure default model and logging
LLM__DEFAULT_MODEL=gpt-4o-mini
LLM__LOG_TO_DB=true
LLM__LOG_LEVEL=INFO
```

### 3. Basic Usage

```python
from united_llm import LLMClient
from pydantic import BaseModel

# Recommended: Use automatic configuration
client = LLMClient()  # Automatically loads from environment/config files

# Or override specific settings only (Smart Config Merging)
client = LLMClient(config={'log_calls': True})  # Just enable logging

# Define output structure
class ArticleSummary(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    confidence: float

# Generate structured output
result = client.generate_structured(
    prompt="Summarize the latest developments in AI",
    output_model=ArticleSummary,
    model="gpt-4o-mini"
)

print(result.title)     # "Latest AI Developments"
print(result.summary)   # "Recent advances include..."
```

### 4. Web Search Integration

```python
# DuckDuckGo search with any model (3-step process)
result = client.generate_structured(
    prompt="What are the latest AI breakthroughs in 2024?",
    output_model=ArticleSummary,
    model="gpt-4o-mini",
    duckduckgo_search=True  # Enables intelligent search
)

# Anthropic web search (Anthropic models only)
result = client.generate_structured(
    prompt="Current AI research trends",
    output_model=ArticleSummary,
    model="claude-3-5-sonnet-20241022",
    anthropic_web_search=True
)
```

## 🎯 Smart Configuration System

### Key Insight: Override Only What You Need

The `LLMClient` features **smart config merging** - when you pass a config dictionary, it merges with bootstrap defaults instead of replacing them. This means you only need to specify the settings you want to override!

**Before (old behavior):**

```python
# User had to specify EVERYTHING
config = {
    'openai_api_key': 'your-key',
    'anthropic_api_key': 'your-other-key',
    'google_api_key': 'your-google-key',
    'ollama_base_url': 'http://localhost:11434/v1',
    'log_calls': True,  # This is all they wanted to change!
    'log_to_db': True,
    'db_path': 'custom_path.db'
}
client = LLMClient(config=config)
```

**After (new behavior):**

```python
# User only specifies what they want to change
client = LLMClient(config={'log_calls': True})  # That's it!
# All other settings (API keys, etc.) come from bootstrap automatically
```

### How Config Merging Works

1. **Bootstrap loads first** - API keys, paths, defaults from environment/config files
2. **User config overlays** - Only the keys you specify override bootstrap
3. **Everything else preserved** - Model lists, paths, other API keys stay intact

### Common Use Cases

```python
# Enable logging only
client = LLMClient(config={'log_calls': True})

# Test with different API key
client = LLMClient(config={'openai_api_key': 'test-key-12345'})

# Use remote Ollama
client = LLMClient(config={'ollama_base_url': 'http://remote-server:11434/v1'})

# Development vs Production
dev_client = LLMClient(config={'log_calls': True, 'log_to_db': True})
prod_client = LLMClient(config={'log_calls': False})

# Multiple overrides
client = LLMClient(config={
    'openai_api_key': 'test-key',
    'log_calls': True,
    'log_to_db': False,
    'ollama_base_url': 'http://custom-ollama:11434/v1'
})
```

### Configuration Debugging

```python
from united_llm import setup_environment, get_config

# 🔍 DEBUGGING: Inspect zero-config configuration
setup_environment()  # Optional - LLMClient does this automatically
config = get_config()

print(f"API key: {config.get('openai_api_key', '')[:20]}...")
print(f"Log calls: {config.get('log_calls')}")
print(f"All config keys: {list(config.to_dict().keys())}")

# Check specific configuration values
print(f"Default model: {config.get('default_model')}")
print(f"Database path: {config.get_db_path()}")
print(f"Data path: {config.data_path()}")
print(f"Logs path: {config.logs_path()}")
```

**Configuration Priority Order:**

1. **`.env.united_llm` file** (highest priority)
2. **Environment variables with aliases** (LLM**\*, ADMIN**\_, API\_\_\_, etc.)
3. **Standard API key environment variables** (OPENAI_API_KEY, etc.)
4. **TOML config files** (lowest priority)

## 🌐 FastAPI Admin Interface

### Start the Server

```bash
# Development mode
source .venv/bin/activate
python -m united_llm.api.server

# Or use the console script (after installation)
united-llm-server

# Or use the restart script (kills existing processes and restarts)
./restart.sh

# Production mode
uvicorn united_llm.api.server:app --host 0.0.0.0 --port 8818 --workers 4
```

### Admin Interface Features

Visit `http://localhost:8818` for the admin interface:

- **📊 Enhanced Dashboard**: Real-time statistics, provider charts, model analytics
- **📋 Request History**: Comprehensive LLM call history with advanced filtering
- **📄 Export Functionality**: CSV and JSON export capabilities
- **🔐 Authentication**: HTTP Basic Auth protection (admin:admin by default)
- **🎨 Modern UI**: Responsive design with FontAwesome icons
- **🔍 Search Testing**: Test search capabilities with different models
- **📈 Analytics**: Token usage, response times, error rates
- **🎯 Send Request Dialog**: Interactive form with model selection, schema input, and tabbed output
- **💻 Code Generation**: Generate Python code examples for your specific prompts and schemas
- **📱 Responsive Design**: Works on desktop and mobile devices

### API Endpoints

#### Core Generation Endpoints

- `POST /generate/dict` - Generate plain dictionaries with string schemas
- `POST /generate/united` - **🆕 United schema endpoint with auto-detection** (supports both JSON Schema and string schemas)

#### Admin & Management

- `GET /` - Admin dashboard interface with real-time analytics
- `GET /admin` - Redirect to main dashboard
- `GET /admin/llm_calls` - Enhanced request history with filtering
- `GET /admin/export/csv` - Export call history as CSV
- `GET /admin/export/json` - Export call history as JSON
- `GET /admin/logout` - Admin logout endpoint

#### System Information

- `GET /models` - List available models and their status
- `GET /health` - System health check with provider status
- `GET /stats` - Usage statistics and metrics

#### Validation & Testing

- `POST /validate-schema` - Validate JSON schemas
- `POST /schema/validate-string` - Validate string schemas with optimization
- `POST /test-search` - **🆕 Test search functionality with different providers**

#### Authentication

- `POST /admin/login` - Admin login (HTTP Basic Auth)

### Admin Interface Usage

**Dashboard**: Monitor system health, view statistics, and access quick actions

**Requests Page**:

- View complete request history with filtering by model, provider, date range
- Click "View" to see full request details including schema and response
- Click "Send Request" to open the interactive request dialog
- Export data as CSV or JSON for analysis

**Send Request Dialog**:

- **Model Selection**: Choose from available models with intelligent defaults
- **Schema Input**: Use JSON Schema or string schema syntax (supports curly brace format)
- **Web Search**: Enable DuckDuckGo or Anthropic web search
- **Tabbed Output**: Switch between "Output" (LLM response) and "Code" (Python examples)
- **Generate Code**: Get Python code examples for your specific prompt and schema

**Navigation**: Use the sidebar to switch between Dashboard and Requests pages

## 🆕 New Schema Syntax Features

### United Schema API

The new `/generate/united` endpoint accepts either JSON Schema or string schema definitions with auto-detection:

```python
# Works with JSON Schema
result = client.generate_structured(
    prompt="Extract user info: John Doe, 30, from NYC",
    schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "city": {"type": "string"}
        }
    }
)

# Works with string schema
result = client.generate_structured(
    prompt="Extract user info: John Doe, 30, from NYC",
    schema="name, age:int, city"
)
```

### Curly Brace Syntax (NEW!)

JSON-consistent syntax with `{}` for objects and `[]` for arrays:

```python
# Simple object
result = client.generate_dict(
    prompt="Create user: Alice, 25, alice@example.com",
    schema="{name, age:int, email}",
    model="claude-sonnet-4-20250514"
)
# Returns: {"name": "Alice", "age": 25, "email": "alice@example.com"}

# Array of objects
result = client.generate_dict(
    prompt="Create contact list with 2 people",
    schema="[{name, email}]",
    model="claude-sonnet-4-20250514"
)

# Nested structure
team = client.generate_dict(
    prompt="Engineering team with 2 developers",
    schema="{team, members:[{name, role}]}",
    model="claude-sonnet-4-20250514"
)
```

### Benefits of New Syntax

- **50% less code** for common use cases
- **Direct JSON serialization** (no `.model_dump()` needed)
- **Perfect for web APIs** and microservices
- **Same validation** as Pydantic models
- **JSON consistency**: `{}` = objects, `[]` = arrays
- **100% backward compatibility**: All legacy syntax still works

## 📊 Comprehensive Logging System

The system provides multi-level logging for complete observability:

### 1. Database Logging (SQLite)

- **Location**: `llm_calls.db`
- **Content**: Complete request/response records with metadata
- **Features**: Searchable, exportable, with usage statistics
- **Schema**: Timestamps, models, providers, tokens, duration, errors

### 2. TXT File Logging

- **Location**: `logs/llm_calls/YYYY-MM-DD.txt`
- **Content**: Human-readable call logs organized by date
- **Format**: Structured text with timestamps and metadata
- **Rotation**: Daily log files with automatic cleanup

### 3. JSON Structured Logs

- **Location**: `logs/llm_calls/YYYY-MM-DD.json`
- **Content**: Machine-readable JSON logs for analysis
- **Features**: Programmatic log analysis and monitoring
- **Integration**: Perfect for log aggregation systems

### 4. Application Logs

- **Location**: `logs/api.log`, `logs/api.log.bak`
- **Content**: FastAPI server logs and application events
- **Features**: Automatic backup and rotation
- **Levels**: INFO, DEBUG, WARNING, ERROR

## 🧪 Examples and Testing

### Examples Directory (`examples/`)

Learn how to use the library with organized examples:

- **`basic_usage.py`** - Core functionality and getting started
- **`web_search.py`** - DuckDuckGo and Anthropic web search integration
- **`advanced_features.py`** - Configuration, fallbacks, and advanced patterns

### Tests Directory (`tests/`)

Verify functionality with comprehensive tests:

- **`test_integration.py`** - Real-world integration testing
- **`test_comprehensive.py`** - Complete system test with all providers

See `examples/README.md` and `tests/README.md` for detailed descriptions.

### Running Examples and Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run examples (start here!)
python examples/basic_usage.py
python examples/web_search.py
python examples/advanced_features.py

# Run tests (verify functionality)
python tests/test_integration.py
python tests/test_comprehensive.py
```

## 🔧 Development and Production

### Development Workflow

```bash
# Start development server manually
source .venv/bin/activate
python -m united_llm.api.server

# Or use the restart script
./restart.sh

# View logs in logs/ directory
tail -f logs/api.log
```

### Production Deployment

```bash
# Production mode with uvicorn
source .venv/bin/activate
uvicorn united_llm.api.server:app --host 0.0.0.0 --port 8080 --workers 4

# Or use restart script on different port
API_PORT=8080 ./restart.sh
```

### Environment Variables

The system supports multiple environment variable formats:

#### Standard Format (Recommended)

```bash
# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Configuration
LLM__DEFAULT_MODEL=gpt-4o-mini
LLM__LOG_TO_DB=true
LLM__LOG_CALLS=true
```

#### Domain-Specific Format (`.env.united_llm`)

```bash
# Clean format without prefixes
DEFAULT_MODEL=gpt-4o-mini
LOG_TO_DB=true
LOG_CALLS=true
OPENAI_API_KEY=your_openai_key
```

#### Namespaced Format

```bash
# Full namespace
UNITED_LLM_DEFAULT_MODEL=gpt-4o-mini
UNITED_LLM_LOG_TO_DB=true
UNITED_LLM_OPENAI_API_KEY=your_openai_key
```

## 🚀 Advanced Features

### Chinese Text Optimization

The system includes specialized Chinese text processing:

```python
# Automatic Chinese query optimization
result = client.generate_structured(
    prompt="分析最新的人工智能技术趋势",
    output_model=TechTrend,
    duckduckgo_search=True  # Optimizes Chinese search automatically
)
```

### Model Fallback

Automatic fallback to working models when preferred models are unavailable:

```python
# Will try gpt-4 first, fall back to gpt-3.5-turbo if unavailable
client = LLMClient(config={
    'default_model': 'gpt-4',
    'fallback_models': ['gpt-3.5-turbo', 'claude-3-haiku']
})
```

### Rate Limiting and Error Handling

- Automatic retry with exponential backoff
- Rate limit detection and handling
- Comprehensive error logging and reporting
- Graceful degradation strategies

## 📦 Dependencies & Installation Options

### Core Dependencies

Core dependencies are automatically installed with the base package:

```bash
# Core LLM libraries
instructor>=1.4.3
pydantic>=2.0.0
pydantic-settings>=2.0.0

# LLM Provider SDKs
openai>=1.12.0
anthropic>=0.21.0
google-generativeai>=0.8.0

# Web framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# Search and utilities
duckduckgo-search>=6.1.0
requests>=2.31.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

### Installation Options

```bash
# Basic installation
pip install -e .

# Development installation (includes testing tools)
pip install -e ".[dev]"
# Includes: pytest, pytest-asyncio, pytest-cov, black, flake8, mypy, pre-commit

# Documentation installation
pip install -e ".[docs]"
# Includes: mkdocs, mkdocs-material, mkdocstrings

# Complete installation (everything)
pip install -e ".[all]"
```

### Console Scripts

After installation, you can use these command-line tools:

```bash
# Start the API server
united-llm-server

# CLI interface (if implemented)
united-llm --help
```

## 🏆 Production Readiness

The united LLM project is **production-ready** with:

- **📋 Comprehensive Documentation**: Complete API docs and examples
- **⚙️ Flexible Configuration**: Environment-based settings with smart merging
- **🔧 Error Handling**: Robust error handling and fallbacks
- **📊 Monitoring**: Statistics and logging capabilities
- **🌐 API Server**: Production-ready FastAPI server
- **🔍 Search Integration**: Both Anthropic and DuckDuckGo search
- **🇨🇳 Chinese Support**: Specialized Chinese text processing
- **🔄 Multi-Provider**: Support for all major LLM providers
- **🛡️ Security**: HTTP Basic Auth and input validation
- **📈 Scalability**: Handles thousands of requests efficiently

## 🎉 Recent Updates

### v2.1 - Enhanced Features & Reliability (Current)

- ✅ **Ollama Function Detection**: Automatic detection of function calling capabilities
- ✅ **Search Testing Endpoint**: `/test-search` for validating search functionality
- ✅ **Enhanced Error Handling**: Better fallback strategies and error reporting
- ✅ **Console Scripts**: `united-llm-server` command-line tool
- ✅ **Improved Documentation**: Updated README and development guide
- ✅ **Better Type Hints**: Enhanced type safety throughout codebase

### v2.0 - Schema Unification & Config Improvements

- ✅ **United Schema API**: Single endpoint handles both JSON Schema and string definitions
- ✅ **Curly Brace Syntax**: JSON-consistent `{}` and `[]` syntax
- ✅ **Smart Config Merging**: Override only what you need
- ✅ **Enhanced Admin Interface**: Modern UI with real-time statistics
- ✅ **Improved Debugging**: `get_effective_config()` for final configuration inspection
- ✅ **Namespace Consistency**: All imports from `united_llm`
- ✅ **Pydantic v2 Compatibility**: Eliminated schema field conflicts

### v1.5 - Admin Interface & Logging

- ✅ **Admin Dashboard**: Beautiful web interface with analytics
- ✅ **Database Logging**: SQLite with comprehensive metrics
- ✅ **Export Functionality**: CSV and JSON export capabilities
- ✅ **Search Integration**: DuckDuckGo and Anthropic web search
- ✅ **Multi-Provider Support**: OpenAI, Anthropic, Google, Ollama

## 📞 Support

For issues, questions, or contributions:

1. Check the comprehensive test files for usage examples
2. Review the admin interface for debugging tools
3. Use `get_effective_config()` for configuration debugging
4. Check logs in the `logs/` directory for detailed error information

---

**💡 Pro Tip**: Start with `LLMClient()` for automatic configuration, then use `config={'key': 'value'}` to override only specific settings you need to change!
