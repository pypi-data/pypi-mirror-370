"""
United LLM configuration defaults.

This module contains only the default configuration values for United LLM.
All actual configuration management is handled by zero-config directly.
"""

# United LLM defaults
UNITED_LLM_DEFAULTS = {
    # Core LLM Settings
    "default_model": "gpt-4o-mini",
    "fallback_models": ["gpt-4o-mini", "claude-3-5-sonnet-20241022"],
    "temperature": 0.0,
    "max_tokens": 1024,
    "timeout": 30,
    "max_retries": 3,
    # Provider Settings
    "ollama_base_url": "http://localhost:11434/v1",
    "openai_base_url": "",  # Empty means use default
    "anthropic_base_url": "",  # Empty means use default
    # API Keys (empty by default, loaded from env/config)
    "openai_api_key": "",
    "anthropic_api_key": "",
    "google_api_key": "",
    # Model Lists (comprehensive for 0-config)
    "openai_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    "anthropic_models": [
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307",
        "claude-sonnet-4-20250514",
        "claude-3-7-sonnet-20250219",
    ],
    "google_models": [
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
        "gemini-2.5-pro-preview-05-06",
        "gemini-2.5-flash-preview-05-20",
    ],
    # Logging Settings
    "log_calls": False,
    "log_to_db": True,
    "log_json": False,
    "log_level": "INFO",
    "db_path": "llm_calls.db",
    # Search Settings
    "duckduckgo_max_results": 5,
    "duckduckgo_timeout": 10,
    # API Server Settings
    "api_host": "0.0.0.0",
    "api_port": 8818,
    "admin_username": "admin",
    "admin_password": "admin",
}
