# 🧪 Tests Directory

This directory contains test files for the Unified LLM library following standard Python testing conventions.

## Test Files

### `test_comprehensive.py`
**Complete system integration test**
- Tests all major features with real API calls
- Multi-provider support (OpenAI, Anthropic, Google, Ollama)
- Search functionality (DuckDuckGo and Anthropic web search)
- Database logging and statistics
- Error handling and fallbacks
- Admin interface functionality

**Usage:**
```bash
# Run from project root
source .venv/bin/activate
python tests/test_comprehensive.py
```

### `test_integration.py`
**Real-world integration testing**
- Practical usage scenarios with real API providers
- Search integration verification
- Database functionality testing
- Multiple model testing
- Structured output validation

**Usage:**
```bash
source .venv/bin/activate
python tests/test_integration.py
```

## Running Tests

### Prerequisites
1. **API Keys configured** in `.env` file
2. **Virtual environment activated**
3. **Dependencies installed**

### Quick Test Run
```bash
# From project root
source .venv/bin/activate

# Run comprehensive tests
python tests/test_comprehensive.py

# Run integration tests
python tests/test_integration.py
```

### Test Coverage
These tests verify:
- ✅ All provider integrations (OpenAI, Anthropic, Google, Ollama)
- ✅ Search functionality (DuckDuckGo 3-step, Anthropic web search)
- ✅ Database logging and retrieval
- ✅ Structured output generation
- ✅ Error handling and model fallbacks
- ✅ Admin interface accessibility
- ✅ Configuration management

### Expected Results
When tests pass, you should see:
- Successful connections to configured providers
- Working search integrations
- Database logging functionality
- Structured output validation
- Admin interface accessibility

### Troubleshooting
If tests fail:
1. Check API keys in `.env` file
2. Verify internet connectivity for search tests
3. Ensure virtual environment is activated
4. Check provider status at their websites
5. Review logs in `logs/` directory

## Adding New Tests

When adding new tests:
1. Use descriptive test names: `test_feature_name.py`
2. Include comprehensive error handling
3. Test both success and failure scenarios
4. Add documentation for what the test covers
5. Update this README with new test descriptions

## Test vs Examples

- **Tests** (`tests/`): Verify functionality works correctly
- **Examples** (`examples/`): Demonstrate how to use features

Tests focus on validation and verification, while examples focus on education and demonstration. 