# 📚 Examples Directory

This directory contains example files demonstrating how to use the Unified LLM library effectively.

## 🎯 Example Files

### `basic_usage.py`

**Getting started with Unified LLM**

- Core functionality demonstration
- Simple structured output generation
- Dictionary generation with curly brace syntax
- Basic error handling patterns

**Best for:** New users learning the basics

**Usage:**

```bash
source .venv/bin/activate
python examples/basic_usage.py
```

### `web_search.py`

**Web search integration examples**

- DuckDuckGo search with any model
- Anthropic web search with Anthropic models

- Search with dictionary output

**Best for:** Users wanting to add web search capabilities

**Usage:**

```bash
source .venv/bin/activate
python examples/web_search.py
```

### `advanced_features.py`

**Advanced configuration and patterns**

- Custom configuration and smart config merging
- Configuration debugging tools
- Model fallback strategies
- Batch processing with multiple models
- Complex nested schema generation

**Best for:** Advanced users and production deployments

**Usage:**

```bash
source .venv/bin/activate
python examples/advanced_features.py
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Activate virtual environment
source .venv/bin/activate

# Configure API keys
cp env_example.txt .env
# Edit .env with your API keys
```

### 2. Run Examples

```bash
# Start with basics
python examples/basic_usage.py

# Try web search features
python examples/web_search.py

# Explore advanced features
python examples/advanced_features.py
```

## 📋 What Each Example Teaches

| Example                | Key Concepts       | Features Demonstrated                                     |
| ---------------------- | ------------------ | --------------------------------------------------------- |
| `basic_usage.py`       | Core functionality | Structured output, dictionary generation, basic config    |
| `web_search.py`        | Search integration | DuckDuckGo search, Anthropic search, Chinese optimization |
| `advanced_features.py` | Advanced patterns  | Custom config, fallbacks, batch processing, debugging     |

## 🎓 Learning Path

### Beginner

1. **Start with `basic_usage.py`**
   - Learn core concepts
   - Understand structured output
   - Try dictionary generation

### Intermediate

2. **Move to `web_search.py`**
   - Add search capabilities
   - Learn about different search types
   - Understand search optimization

### Advanced

3. **Explore `advanced_features.py`**
   - Master configuration management
   - Implement fallback strategies
   - Build production-ready applications

## 🔧 Development Usage

These examples are also useful for:

- **Feature Testing**: Verify new features work correctly
- **Integration Testing**: Test with real API providers
- **Prototyping**: Quick start for new projects
- **Documentation**: Live examples of library capabilities

## 🌟 Key Features Demonstrated

### Core Features

- ✅ **Multi-provider Support**: OpenAI, Anthropic, Google, Ollama
- ✅ **Structured Outputs**: Pydantic models with validation
- ✅ **Dictionary Generation**: Plain Python dicts with curly brace syntax
- ✅ **Smart Configuration**: Override only what you need

### Search Features

- ✅ **DuckDuckGo Search**: Works with any model
- ✅ **Anthropic Web Search**: Native Anthropic integration
- ✅ **Chinese Optimization**: Automatic query optimization
- ✅ **Search + Generation**: Integrated search and structured output

### Advanced Features

- ✅ **Model Fallbacks**: Automatic failover between models
- ✅ **Batch Processing**: Multiple requests with different models
- ✅ **Configuration Debugging**: Tools to inspect final config
- ✅ **Custom Clients**: Different configurations for different use cases

## 💡 Tips for Using Examples

### Customization

- **Modify prompts** to test your specific use cases
- **Change models** to test different providers
- **Adjust schemas** to match your data structures
- **Add error handling** for your specific needs

### Troubleshooting

- **Check API keys** if examples fail
- **Verify internet connection** for search examples
- **Review error messages** for specific issues
- **Check provider status** if specific models fail

### Best Practices

- **Start simple** and gradually add complexity
- **Test with multiple providers** for reliability
- **Use appropriate models** for your use case
- **Configure logging** for debugging

## 🔗 Next Steps

After running examples:

- **Start the web server**: `python -m united_llm.api.server`
- **Visit admin interface**: `http://localhost:8818`
- **Check API docs**: `http://localhost:8818/docs`
- **Review tests**: See `tests/` directory for validation examples
- **Read documentation**: Check main `README.md` for comprehensive guide

## 🆚 Examples vs Tests

| Purpose         | Examples          | Tests                  |
| --------------- | ----------------- | ---------------------- |
| **Goal**        | Demonstrate usage | Verify functionality   |
| **Focus**       | Education         | Validation             |
| **Audience**    | Users learning    | Developers testing     |
| **Content**     | How-to guides     | Pass/fail verification |
| **When to use** | Learning features | Ensuring quality       |
