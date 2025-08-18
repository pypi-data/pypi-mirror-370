"""
Model management utilities for LLM providers and model validation.

This module contains the ModelManager class and utilities for:
- Detecting which provider a model belongs to
- Validating model availability and provider configuration
- Managing provider credentials and model lists
- Organizing model information during initialization

The ModelManager class is completely separate from configuration management
and requires config data to be passed during instantiation.
"""

from typing import Dict, Any, List
import requests
import logging


class ModelManager:
    """Utility class for managing, detecting and validating LLM models and providers."""

    def __init__(self, config_data: Dict[str, Any]):
        """Initialize with configuration data and combine model information."""
        self._config_data = config_data

        # Combine and organize model information during initialization
        self._provider_models = {
            "openai": config_data.get("openai_models", []),
            "anthropic": config_data.get("anthropic_models", []),
            "google": config_data.get("google_models", []),
        }

        self._provider_credentials = {
            "openai": config_data.get("openai_api_key"),
            "anthropic": config_data.get("anthropic_api_key"),
            "google": config_data.get("google_api_key"),
            "ollama": config_data.get("ollama_base_url"),
        }

    def has_provider(self, provider: str) -> bool:
        """Check if a provider is configured and available."""
        return bool(self._provider_credentials.get(provider.lower()))

    def get_configured_providers(self) -> List[str]:
        """Get list of all configured providers."""
        return [provider for provider, credential in self._provider_credentials.items() if credential]

    def get_provider_models(self, provider: str) -> List[str]:
        """Get list of models for a specific provider."""
        return self._provider_models.get(provider.lower(), [])

    def get_all_models(self) -> Dict[str, List[str]]:
        """Get all models organized by provider."""
        return self._provider_models.copy()

    def get_ollama_models(self, ollama_base_url: str = None, timeout: int = 5) -> List[str]:
        """
        Get list of available Ollama models by querying the Ollama API.

        Args:
            ollama_base_url: Ollama server URL (defaults to config value)
            timeout: Request timeout in seconds

        Returns:
            List of model names in alphabetical order
        """
        if not ollama_base_url:
            ollama_base_url = self._config_data.get("ollama_base_url", "http://localhost:11434")

        # Remove trailing slash and /v1 if present
        base_url = ollama_base_url.rstrip("/").replace("/v1", "")
        api_url = f"{base_url}/api/tags"

        logger = logging.getLogger(__name__)

        try:
            response = requests.get(api_url, timeout=timeout)
            response.raise_for_status()

            data = response.json()
            models = data.get("models", [])

            # Extract model names and sort alphabetically
            model_names = [model.get("name", "") for model in models if model.get("name")]
            model_names = [name for name in model_names if name]  # Filter out empty names

            logger.debug(f"Retrieved {len(model_names)} models from Ollama at {api_url}")
            return sorted(model_names)

        except requests.exceptions.ConnectionError:
            logger.warning(f"Cannot connect to Ollama at {api_url}")
            return []
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout connecting to Ollama at {api_url}")
            return []
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error querying Ollama models: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error querying Ollama models: {e}")
            return []

    def detect_model_provider(self, model: str) -> str:
        """Detect which provider a model belongs to based on model name."""
        model_lower = model.lower()

        # Check against configured model lists
        for provider, models in self._provider_models.items():
            if any(
                provider_model.lower() in model_lower or model_lower in provider_model.lower()
                for provider_model in models
            ):
                return provider

        # Pattern-based fallback
        if any(pattern in model_lower for pattern in ["gpt", "openai"]):
            return "openai"
        elif any(pattern in model_lower for pattern in ["claude", "anthropic"]):
            return "anthropic"
        elif any(pattern in model_lower for pattern in ["gemini", "google"]):
            return "google"
        else:
            return "ollama"

    def validate_model_available(self, model: str) -> bool:
        """Validate that a model is available and the provider is configured."""
        provider = self.detect_model_provider(model)

        if provider in self._provider_models:
            if model not in self._provider_models[provider]:
                raise ValueError(
                    f"{provider.title()} model '{model}' is not in the configured model list. "
                    f"Available {provider.title()} models: {self._provider_models[provider]}. "
                    f"Add it to {provider}_models in your .env.united_llm file."
                )
            return self.has_provider(provider)
        elif provider == "ollama":
            return self.has_provider("ollama")

        return True
