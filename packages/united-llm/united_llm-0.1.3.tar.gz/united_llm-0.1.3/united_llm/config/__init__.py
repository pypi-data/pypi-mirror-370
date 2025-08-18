"""
United LLM Configuration Module

This module provides a clean interface to the configuration system,
re-exporting zero-config functionality with United LLM defaults.
"""

try:
    # Try the new import style first
    from zero_config import setup_environment, get_config, is_initialized, get_initialization_info
except (ImportError, AttributeError):
    # Fallback to direct module import
    try:
        from zero_config.config import setup_environment, get_config, is_initialized, get_initialization_info
    except ImportError:
        # Last resort - import the module and access attributes
        import zero_config.config as zc
        setup_environment = zc.setup_environment
        get_config = zc.get_config
        is_initialized = zc.is_initialized
        get_initialization_info = zc.get_initialization_info

from .defaults import UNITED_LLM_DEFAULTS

# United LLM setup function
def setup_united_llm_environment():
    """Setup United LLM configuration with defaults and .env.united_llm file."""
    setup_environment(default_config=UNITED_LLM_DEFAULTS, env_files=[".env.united_llm"])


# Export everything
__all__ = [
    "setup_environment",
    "get_config",
    "is_initialized",
    "get_initialization_info",
    "setup_united_llm_environment",
    "UNITED_LLM_DEFAULTS",
]
