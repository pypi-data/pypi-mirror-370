"""
Enhanced LLM Client with united search capabilities.
Extends the original LLMClient with Anthropic web search and DuckDuckGo search integration.
"""

import os
import logging
from typing import Dict, Any, List, Type, TypeVar, Optional, Union
import json
import time
import random
from datetime import datetime
from pydantic import BaseModel
import traceback
import base64
import requests
from pathlib import Path

import instructor  # Main library for structured outputs

# Database logging
from .utils.database import LLMDatabase, LLMCallRecord

# Model management
from .utils.model_manager import ModelManager

# Type variable for generic handling of Pydantic models
T = TypeVar("T", bound=BaseModel)


class ImageInput:
    """Represents an image input with metadata for vision models"""

    def __init__(
        self,
        data: Union[str, bytes, Path],
        mime_type: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Initialize image input

        Args:
            data: Base64 string, bytes, file path, or URL
            mime_type: MIME type (auto-detected if not provided)
            name: Optional name for the image (e.g., "001_img_1")
            description: Optional description
        """
        self.name = name
        self.description = description

        if isinstance(data, (str, Path)) and str(data).startswith('http'):
            # URL
            self.base64_data, self.mime_type = self._load_from_source(data)
        elif isinstance(data, Path) or (isinstance(data, str) and len(data) < 500 and not data.startswith('http') and Path(data).exists()):
            # File path (check length to avoid base64 strings being treated as paths)
            self.base64_data, self.mime_type = self._load_from_source(data)
        elif isinstance(data, bytes):
            # Raw bytes
            self.base64_data = base64.b64encode(data).decode('utf-8')
            self.mime_type = mime_type or "image/jpeg"
        elif isinstance(data, str):
            # Assume base64 string (for long strings or non-file paths)
            self.base64_data = data
            self.mime_type = mime_type or "image/jpeg"
        else:
            raise ValueError("Invalid image data format")

    def _load_from_source(self, source: Union[str, Path]) -> tuple[str, str]:
        """Load image from URL or file path"""
        if str(source).startswith('http'):
            # Download from URL
            response = requests.get(str(source), timeout=30)
            response.raise_for_status()

            content_type = response.headers.get('content-type', 'image/jpeg')
            base64_data = base64.b64encode(response.content).decode('utf-8')

            return base64_data, content_type
        else:
            # Load from file
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")

            # Determine MIME type from extension
            ext = path.suffix.lower()
            mime_map = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.png': 'image/png', '.gif': 'image/gif',
                '.webp': 'image/webp', '.bmp': 'image/bmp'
            }
            mime_type = mime_map.get(ext, 'image/jpeg')

            with open(path, 'rb') as f:
                base64_data = base64.b64encode(f.read()).decode('utf-8')

            return base64_data, mime_type


def get_ollama_context(input_text: str) -> int:
    """Calculate appropriate context size for Ollama based on input length"""
    estimated_tokens = len(input_text) // 3
    needed = estimated_tokens * 2
    if needed <= 8192:
        return 8192
    elif needed <= 16384:
        return 16384
    elif needed <= 32768:
        return 32768
    else:
        return 65536


class LLMClient:
    """
    Enhanced LLM client with united search capabilities.
    Supports structured outputs with optional web search integration.
    """

    def __init__(self, config: Union[Dict[str, Any], None] = None, log_calls: Optional[bool] = None):
        self.logger = logging.getLogger(__name__)

        # Use clean config interface
        try:
            from .config import setup_united_llm_environment, get_config

            # Always call setup with United LLM defaults - zero-config prevents multiple setups automatically
            setup_united_llm_environment()
            self.bootstrap_config = get_config()

            self.logger.info("Configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load bootstrap config: {e}")
            raise RuntimeError(f"Configuration system failed to initialize: {e}")

        # Handle user config overrides
        if config is None:
            # No user config, use bootstrap as-is
            self.config = self.bootstrap_config.to_dict()
            self.logger.info("Using bootstrap configuration for LLMClient")
        elif isinstance(config, dict):
            # Handle dictionary config - merge with bootstrap (user config overrides)
            self.config = {**self.bootstrap_config.to_dict(), **config}
            user_keys = list(config.keys())
            self.logger.info(f"Merged user config with bootstrap configuration (overriding: {user_keys})")
        else:
            raise ValueError(f"Invalid config parameter. Expected dict or None. Got {type(config)}: {config}")

        # Store bootstrap config for direct access to helper methods
        self.bootstrap = self.bootstrap_config

        # Initialize model manager with current config
        self.model_manager = ModelManager(self.config)

        self.log_calls = log_calls if log_calls is not None else self.config.get("log_calls", False)
        self.log_to_db = self.config.get("log_to_db", True)
        self.log_json = self.config.get("log_json", False)

        # Initialize txt file logging directories
        self.txt_log_folder = None
        self.json_log_folder = None
        if self.log_calls:
            # Setup txt file logging directories using bootstrap paths
            self.txt_log_folder = self.bootstrap.logs_path("llm_calls/txt")
            self.json_log_folder = self.bootstrap.logs_path("llm_calls/json")
            try:
                os.makedirs(self.txt_log_folder, exist_ok=True)
                if self.log_json:
                    os.makedirs(self.json_log_folder, exist_ok=True)
                self.logger.info(f"TXT file logging enabled: {self.txt_log_folder}")
            except OSError as e:
                self.logger.error(f"Could not create LLM log dirs: {e}. Disabling file logging.")
                self.log_calls = self.log_json = False

        # Initialize database if logging is enabled
        self.db = None
        if self.log_to_db:
            db_path = self.bootstrap.get_db_path()
            try:
                self.db = LLMDatabase(db_path)
                self.logger.info(f"Database logging enabled: {db_path}")
            except Exception as e:
                self.logger.error(f"Failed to initialize database: {e}")
                self.log_to_db = False

        # Use bootstrap-based model lists
        self.OPENAI_MODELS = set(self.bootstrap.get("openai_models", []))
        self.ANTHROPIC_MODELS = set(self.bootstrap.get("anthropic_models", []))
        self.GOOGLE_MODELS = set(self.bootstrap.get("google_models", []))

        self._verify_configuration()

        # Initialize search modules
        self._duckduckgo_search = None

    def _verify_configuration(self):
        # Check and log for each provider
        self.has_openai = bool(self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY"))
        if not self.has_openai:
            self.logger.warning("OpenAI API key not found or not configured.")

        self.has_anthropic = bool(self.config.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY"))
        if not self.has_anthropic:
            self.logger.warning("Anthropic API key not found or not configured.")

        self.has_google = bool(self.config.get("google_api_key") or os.environ.get("GOOGLE_API_KEY"))
        if not self.has_google:
            self.logger.warning("Google API key not found or not configured.")

        # For Ollama, check if the base_url is explicitly set to something other than None/empty or the default True
        ollama_base_url_config = self.config.get("ollama_base_url")
        if ollama_base_url_config is None or ollama_base_url_config is True:
            if not isinstance(ollama_base_url_config, str):
                self.logger.warning(
                    "Ollama base URL not explicitly configured as a string. It might fall back to default if used."
                )
                self.has_ollama = False
            else:
                self.has_ollama = True
        elif not ollama_base_url_config:
            self.logger.warning("Ollama base URL is configured as an empty string, disabling Ollama.")
            self.has_ollama = False
        else:
            self.has_ollama = True

        if not any([self.has_openai, self.has_anthropic, self.has_google, self.has_ollama]):
            self.logger.warning("No LLM providers configured.")
        else:
            self.logger.info(
                f"LLM Providers: OpenAI={self.has_openai}, Anthropic={self.has_anthropic}, "
                f"Google={self.has_google}, Ollama={self.has_ollama}"
            )

    def _get_openai_client(self):
        """Create a new Instructor-enhanced OpenAI client for each request."""
        if not self.has_openai:
            raise ValueError("OpenAI API key not configured.")
        try:
            from openai import OpenAI

            api_key = self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
            kwargs = {"api_key": api_key}
            openai_base_url = self.config.get("openai_base_url")
            if openai_base_url:
                kwargs["base_url"] = openai_base_url
            return instructor.from_openai(OpenAI(**kwargs))
        except ImportError:
            self.logger.error("OpenAI lib not found. pip install openai")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create OpenAI client: {e}")
            raise

    def _get_anthropic_client(self, with_search: bool = False):
        """Create a new Instructor-enhanced Anthropic client for each request."""
        if not self.has_anthropic:
            raise ValueError("Anthropic API key not configured.")
        try:
            from anthropic import Anthropic

            api_key = self.config.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY")
            kwargs = {"api_key": api_key}
            anthropic_base_url = self.config.get("anthropic_base_url")
            if anthropic_base_url:
                kwargs["base_url"] = anthropic_base_url

            anthropic_client = Anthropic(**kwargs)
            if with_search:
                # Enable web search for Anthropic
                return instructor.from_anthropic(anthropic_client, mode=instructor.Mode.ANTHROPIC_JSON)
            else:
                return instructor.from_anthropic(anthropic_client)
        except ImportError:
            self.logger.error("Anthropic lib not found. pip install anthropic")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create Anthropic client: {e}")
            raise

    def _get_ollama_client(self):
        """Create a new plain Ollama client for each request."""
        try:
            from openai import OpenAI

            base_url = self.config.get("ollama_base_url")
            if not base_url:
                raise ValueError("Ollama base_url not configured.")

            return OpenAI(base_url=base_url, api_key="ollama")
        except ImportError:
            self.logger.error("OpenAI lib (for Ollama) not found. pip install openai")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create Ollama client: {e}")
            raise

    def _get_ollama_client_for_model(self, model_name: str):
        """Create a new Instructor-wrapped Ollama client for the specific model."""
        try:
            # Get the base Ollama client
            base_client = self._get_ollama_client()

            # Use JSON mode for all Ollama models (simplified approach)
            # This works reliably for structured outputs without complex function calling detection
            return instructor.patch(base_client, mode=instructor.Mode.JSON)

        except Exception as e:
            self.logger.error(f"Failed to create Ollama client for {model_name}: {e}")
            raise

    def _get_google_client(self, model_name: str = "models/gemini-1.5-flash-latest"):
        """Create a new Instructor-enhanced Google client for the specific model."""
        if not self.has_google:
            raise ValueError("Google API key not configured.")
        try:
            import google.generativeai as genai

            api_key = self.config.get("google_api_key") or os.environ.get("GOOGLE_API_KEY")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=model_name)
            return instructor.from_gemini(
                client=model,
                mode=instructor.Mode.GEMINI_JSON,
            )
        except ImportError:
            self.logger.error("Google GenAI lib not found. pip install google-generativeai")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create Google client for {model_name}: {e}")
            raise

    def determine_provider(self, model: str) -> tuple[str, str]:
        """
        Smart model provider detection using bootstrap configuration.
        Validates that big three models are in configured lists.
        """
        # First, validate the model is available in our configuration
        try:
            self.model_manager.validate_model_available(model)
        except ValueError as e:
            raise ValueError(str(e))

        # Use smart detection to determine provider
        provider = self.model_manager.detect_model_provider(model)

        if provider == "openai":
            return "openai", model
        elif provider == "anthropic":
            return "anthropic", model
        elif provider == "google":
            # Google model mapping for API compatibility
            google_model_mapping = {
                "gemini-2.5-pro-preview-05-06": "models/gemini-1.5-pro-latest",
                "gemini-2.5-flash-preview-05-20": "models/gemini-1.5-flash-latest",
                "gemini-pro": "models/gemini-1.5-pro-latest",
                "gemini-1.5-pro": "models/gemini-1.5-pro-latest",
                "gemini-1.5-flash": "models/gemini-1.5-flash-latest",
            }
            actual_model = google_model_mapping.get(model, f"models/{model}")
            return "google", actual_model
        elif provider == "ollama":
            if not self.has_ollama:
                raise ValueError(f"Ollama provider not configured but model '{model}' routes to Ollama")
            return "ollama", model
        else:
            raise ValueError(f"Unknown provider '{provider}' for model '{model}'")

    def _get_client_for_model(self, model: str, enable_anthropic_search: bool = False):
        provider, model_name = self.determine_provider(model)
        if provider == "openai":
            return self._get_openai_client()
        if provider == "anthropic":
            return self._get_anthropic_client(with_search=enable_anthropic_search)
        if provider == "google":
            return self._get_google_client(model_name)
        if provider == "ollama":
            return self._get_ollama_client_for_model(model_name)
        raise ValueError(f"Unknown provider: {provider}")

    def _validate_search_parameters(self, anthropic_web_search: bool, duckduckgo_search: bool, model: str):
        """Validate search parameters and model compatibility"""
        if anthropic_web_search and duckduckgo_search:
            raise ValueError("Cannot use both anthropic_web_search and duckduckgo_search simultaneously")

        if anthropic_web_search:
            provider, _ = self.determine_provider(model)
            if provider != "anthropic":
                raise ValueError(f"Anthropic web search is only supported with Anthropic models, not {model}")

    def _get_duckduckgo_search(self):
        """Lazy loading of DuckDuckGo search module"""
        if self._duckduckgo_search is None:
            from .search.duckduckgo_search import DuckDuckGoSearch

            self._duckduckgo_search = DuckDuckGoSearch(self.config, self)
        return self._duckduckgo_search

    def _log_interaction(
        self,
        model: str,
        prompt: str,
        response: Any = None,
        token_usage: dict = None,
        error_info: str = None,
        duration_ms: int = None,
        search_type: str = None,
        request_schema: str = None,
        is_before_call: bool = False,
        txt_filepath: Optional[str] = None,
        json_filepath: Optional[str] = None,
    ):
        """Log LLM interaction to both database and txt files if logging is enabled."""

        # Log to database
        if self.log_to_db and self.db and not is_before_call:
            try:
                # Determine provider
                provider = self.model_manager.detect_model_provider(model)

                # Convert response to string if it's a BaseModel
                response_str = None
                if response is not None:
                    if isinstance(response, BaseModel):
                        response_str = json.dumps(response.model_dump(), indent=2, default=str)
                    else:
                        response_str = (
                            json.dumps(response, indent=2, default=str)
                            if isinstance(response, (dict, list))
                            else str(response)
                        )

                # Create record
                record = LLMCallRecord(
                    timestamp=datetime.now(),
                    model=model,
                    provider=provider,
                    prompt=prompt,
                    response=response_str,
                    token_usage=token_usage,
                    error=error_info,
                    duration_ms=duration_ms,
                    search_type=search_type,
                    request_schema=request_schema,
                )

                # Log to database
                self.db.log_call(record)

            except Exception as e:
                self.logger.error(f"Failed to log interaction to database: {e}")

        # Log to txt files (similar to original implementation)
        if not self.log_calls or not self.txt_log_folder:
            return None, None

        try:
            now = datetime.now()
            date_folder = now.strftime("%Y-%m-%d")
            # New format: YYYYMMDD-HH:MM:SS_random(0-9)_model_name
            timestamp = now.strftime("%Y%m%d-%H:%M:%S")
            random_digit = str(random.randint(0, 9))
            current_txt_log_dir = os.path.join(self.txt_log_folder, date_folder)
            os.makedirs(current_txt_log_dir, exist_ok=True)
            base_filename = f"{timestamp}_{random_digit}_{model.replace(':', '_').replace('/', '_')}"

            # Initialize log paths
            final_txt_log_path = txt_filepath or os.path.join(current_txt_log_dir, f"{base_filename}.txt")
            final_json_log_path = None

            log_entry = f"Timestamp: {now.isoformat()}\nModel: {model}\n"
            if search_type:
                log_entry += f"Search Type: {search_type}\n"
            if duration_ms:
                log_entry += f"Duration: {duration_ms}ms\n"
            log_entry += (
                f"Prompt/Messages:\n{json.dumps(prompt, indent=2, ensure_ascii=False) if isinstance(prompt, (dict, list)) else prompt}\n\n"
            )

            if is_before_call:
                log_entry += "--- Waiting for response ---\n"
            else:
                response_data = (
                    response.model_dump() if isinstance(response, BaseModel) else response
                    if response is not None
                    else "N/A"
                )
                log_entry += f"Response:\n{json.dumps(response_data, indent=2, default=str, ensure_ascii=False)}\n\n"
                if token_usage:
                    log_entry += f"Token Usage: {json.dumps(token_usage)}\n"
                if error_info:
                    log_entry += f"Error: {error_info}\n"

            # Write to txt file
            # Use "w" mode for final log (with response) to avoid duplicates, "a" for before_call
            write_mode = "w" if not is_before_call else "a"
            with open(final_txt_log_path, write_mode, encoding="utf-8") as f:
                f.write(log_entry + "------------------------------------\n")

            # Write to JSON file if enabled
            if self.log_json and self.json_log_folder and not is_before_call:
                current_json_log_dir = os.path.join(self.json_log_folder, date_folder)
                os.makedirs(current_json_log_dir, exist_ok=True)
                final_json_log_path = json_filepath or os.path.join(current_json_log_dir, f"{base_filename}.json")

                json_data = {
                    "timestamp": now.isoformat(),
                    "model": model,
                    "prompt_messages": prompt,
                    "response": response.model_dump() if isinstance(response, BaseModel) else response,
                    "token_usage": token_usage,
                    "error": error_info,
                    "duration_ms": duration_ms,
                    "search_type": search_type,
                    "request_schema": request_schema,
                }

                with open(final_json_log_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2, default=str, ensure_ascii=False)

            return final_txt_log_path, final_json_log_path

        except Exception as e:
            self.logger.error(f"Failed to write txt/json logs: {e}")
            return None, None

    def _clean_text(self, text: str) -> str:
        return text.replace("\x00", "")

    def _handle_google_rate_limit_retry(self, func, max_retries: int = 3):
        """Handle Google API rate limiting with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Resource has been exhausted" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** (attempt + 1)
                        self.logger.warning(
                            f"Google API rate limit hit, retrying in {sleep_time} seconds "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(sleep_time)
                        continue
                raise

    def is_vision_capable(self, model: str) -> bool:
        """Check if a model supports vision inputs"""
        vision_models = {
            "openai": [
                "gpt-4-vision-preview", "gpt-4o", "gpt-4o-mini",
                "gpt-4-turbo", "gpt-4-turbo-2024-04-09"
            ],
            "anthropic": [
                "claude-3-opus-20240229", "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307", "claude-3-5-sonnet-20241022",
                "claude-3-5-sonnet-20240620", "claude-3-5-haiku-20241022"
            ],
            "google": [
                "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-pro-latest",
                "gemini-1.5-flash-latest", "gemini-pro-vision", "gemini-2.5-pro-preview-05-06",
                "gemini-2.5-flash-preview-05-20"
            ],
            "ollama": [
                "llava", "llava:7b", "llava:13b", "llava:34b",
                "bakllava", "moondream", "minicpm-v"
            ]
        }

        # Try to determine provider, but handle validation errors gracefully
        try:
            provider, model_name = self.determine_provider(model)
            # Check exact match first
            if model_name in vision_models.get(provider, []):
                return True
            # For Google models, also check pattern matching for -latest variants
            if provider == "google":
                model_lower = model_name.lower()
                if any(pattern in model_lower for pattern in ["gemini-1.5", "gemini-pro-vision", "gemini-2.5"]):
                    return True
            return False
        except ValueError:
            # If model validation fails, check by pattern matching
            model_lower = model.lower()

            # Check for vision patterns
            if any(pattern in model_lower for pattern in ["gpt-4o", "gpt-4-vision", "gpt-4-turbo"]):
                return True
            elif any(pattern in model_lower for pattern in ["claude-3", "claude-3-5"]):
                return True
            elif any(pattern in model_lower for pattern in ["gemini-1.5", "gemini-pro-vision", "gemini-2.5"]):
                return True
            elif any(pattern in model_lower for pattern in ["llava", "bakllava", "moondream", "minicpm-v"]):
                return True

            return False

    def generate_structured(
        self,
        prompt: str,
        output_model: Type[T],
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_retries: int = 1,
        enable_web_search: bool = False,
        anthropic_web_search: bool = False,
        duckduckgo_search: bool = False,
        fallback_models: Optional[List[str]] = None,
        images: Optional[List[ImageInput]] = None,
    ) -> T:
        """
        Generate structured output with optional search capabilities, vision support, and fallback models.

        Args:
            prompt: The input prompt
            output_model: Pydantic model class for structured output
            model: Model to use (defaults to DEFAULT_MODEL)
            temperature: Sampling temperature
            max_retries: Maximum number of retries
            enable_web_search: Enable web search (automatically chooses best method for model)
            anthropic_web_search: [DEPRECATED] Enable Anthropic web search (Anthropic models only)
            duckduckgo_search: [DEPRECATED] Enable DuckDuckGo search with 3-step processing
            fallback_models: Optional list of fallback models to try if primary model fails
            images: Optional list of ImageInput objects for vision-capable models

        Returns:
            Structured output of type output_model
        """
        cleaned_prompt = self._clean_text(prompt)
        primary_model = model or self.bootstrap.get("default_model")

        # Handle enable_web_search flag - automatically determine search type
        if enable_web_search and not anthropic_web_search and not duckduckgo_search:
            # Auto-determine search type based on model
            if primary_model and (
                primary_model.startswith("claude") or primary_model.startswith("anthropic")
            ):
                anthropic_web_search = True
            else:
                duckduckgo_search = True

        # Build list of models to try
        models_to_try = [primary_model]
        if fallback_models:
            models_to_try.extend(fallback_models)

        # Try each model in order
        last_exception = None
        for i, current_model in enumerate(models_to_try):
            try:
                if i > 0:  # Only log for fallback attempts
                    self.logger.info(f"Attempting fallback with model: {current_model}")

                # Validate search parameters for current model
                self._validate_search_parameters(anthropic_web_search, duckduckgo_search, current_model)

                # Handle vision inputs if provided
                if images:
                    if not self.is_vision_capable(current_model):
                        if i == len(models_to_try) - 1:  # Last model
                            raise ValueError(f"Model {current_model} does not support vision inputs")
                        else:
                            self.logger.warning(f"Model {current_model} does not support vision, trying next model")
                            continue

                    # Use vision-enabled generation
                    return self._generate_with_vision(
                        cleaned_prompt, images, output_model, current_model, temperature, max_retries
                    )

                # Handle DuckDuckGo search (works with any model)
                if duckduckgo_search:
                    search_handler = self._get_duckduckgo_search()
                    return search_handler.search_and_generate(
                        cleaned_prompt, output_model, current_model, temperature, max_retries
                    )

                # Handle Anthropic web search - Direct integration without separate class
                if anthropic_web_search:
                    if not current_model.startswith(("claude", "anthropic")):
                        raise ValueError("Anthropic web search is only available for Anthropic models")
                    # Extract schema from output_model for logging
                    try:
                        schema_json = json.dumps(output_model.model_json_schema(), default=str)
                    except Exception:
                        schema_json = None
                    return self._generate_anthropic_with_search(
                        cleaned_prompt,
                        output_model,
                        current_model,
                        temperature,
                        max_retries,
                        schema=schema_json,
                    )

                # Standard generation (existing functionality)
                # Extract schema from output_model for logging
                try:
                    schema_json = json.dumps(output_model.model_json_schema(), default=str)
                except Exception:
                    schema_json = None

                return self._generate_standard(
                    cleaned_prompt, output_model, current_model, temperature, max_retries, schema=schema_json
                )

            except Exception as e:
                last_exception = e
                if i < len(models_to_try) - 1:  # Not the last model
                    self.logger.warning(
                        f"Model {current_model} failed: {type(e).__name__} - {str(e)}. Trying next model."
                    )
                else:
                    # Last model failed
                    if len(models_to_try) > 1:
                        self.logger.error(f"All models failed. Last error: {last_exception}")
                    raise last_exception

        # This should never be reached, but just in case
        raise last_exception

    def _generate_with_vision(
        self,
        prompt: str,
        images: List[ImageInput],
        output_model: Type[T],
        model: str,
        temperature: float,
        max_retries: int
    ) -> T:
        """Core vision generation method for different providers"""
        provider, model_name = self.determine_provider(model)
        client = self._get_client_for_model(model)

        # Build multimodal messages based on provider
        if provider == "openai":
            messages = self._build_openai_vision_messages(prompt, images)
        elif provider == "anthropic":
            messages = self._build_anthropic_vision_messages(prompt, images)
        elif provider == "google":
            return self._generate_google_vision(
                prompt, images, output_model, model_name, temperature, max_retries
            )
        elif provider == "ollama":
            messages = self._build_ollama_vision_messages(prompt, images)
        else:
            raise ValueError(f"Unsupported provider for vision: {provider}")

        # Generate with provider-specific client (with logging)
        start_time = time.time()
        response_obj = None
        error_info_str = None
        token_details = None

        # Extract schema for logging
        try:
            schema = json.dumps(output_model.model_json_schema(), default=str)
        except Exception:
            schema = None

        # Log before call
        txt_log_path, json_log_path = self._log_interaction(
            model=model_name,
            prompt=prompt,
            request_schema=schema,
            is_before_call=True,
        )

        try:
            kwargs = {
                "messages": messages,
                "response_model": output_model,
                "max_retries": max_retries
            }

            if provider != "google":
                kwargs["model"] = model_name
                kwargs["temperature"] = temperature
                if provider == "anthropic":
                    kwargs["max_tokens"] = 4000

            response_obj = client.chat.completions.create(**kwargs)
            return response_obj

        except Exception as e:
            error_info_str = f"Vision generation failed with {model}: {e}"
            self.logger.error(error_info_str)
            raise
        finally:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log the interaction (final logging with response)
            self._log_interaction(
                model=model_name,
                prompt=prompt,
                response=response_obj,
                token_usage=token_details,
                error_info=error_info_str,
                duration_ms=duration_ms,
                request_schema=schema,
                is_before_call=False,
                txt_filepath=txt_log_path,
                json_filepath=json_log_path,
            )

    def _build_openai_vision_messages(self, prompt: str, images: List[ImageInput]) -> List[Dict]:
        """Build OpenAI-format multimodal messages"""
        content = [{"type": "text", "text": prompt}]
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img.mime_type};base64,{img.base64_data}",
                    "detail": "high"
                }
            })
        return [{"role": "user", "content": content}]

    def _build_anthropic_vision_messages(self, prompt: str, images: List[ImageInput]) -> List[Dict]:
        """Build Anthropic-format multimodal messages"""
        content = [{"type": "text", "text": prompt}]
        for img in images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img.mime_type,
                    "data": img.base64_data
                }
            })
        return [{"role": "user", "content": content}]

    def _build_ollama_vision_messages(self, prompt: str, images: List[ImageInput]) -> List[Dict]:
        """Build Ollama-format multimodal messages"""
        content = [{"type": "text", "text": prompt}]
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img.mime_type};base64,{img.base64_data}"
                }
            })
        return [{"role": "user", "content": content}]

    def _generate_google_vision(
        self,
        prompt: str,
        images: List[ImageInput],
        output_model: Type[T],
        model_name: str,
        temperature: float,
        max_retries: int
    ) -> T:
        """Handle Google Gemini vision generation"""
        start_time = time.time()
        response_obj = None
        error_info_str = None
        token_details = None

        # Extract schema for logging
        try:
            schema = json.dumps(output_model.model_json_schema(), default=str)
        except Exception:
            schema = None

        # Log before call
        txt_log_path, json_log_path = self._log_interaction(
            model=model_name,
            prompt=prompt,
            request_schema=schema,
            is_before_call=True,
        )

        try:
            import google.generativeai as genai
            import instructor

            api_key = self.config.get("google_api_key")
            if not api_key:
                raise ValueError("Google API key not configured")

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=model_name)
            client = instructor.from_gemini(client=model, mode=instructor.Mode.GEMINI_JSON)

            content_parts = [{"text": prompt}]
            for img in images:
                content_parts.append({
                    "inline_data": {
                        "mime_type": img.mime_type,
                        "data": img.base64_data
                    }
                })

            kwargs = {
                "messages": [{"role": "user", "content": content_parts}],
                "response_model": output_model,
                "max_retries": max_retries
            }

            if temperature != 0.0:
                kwargs["generation_config"] = {"temperature": temperature}

            response_obj = self._handle_google_rate_limit_retry(
                lambda: client.chat.completions.create(**kwargs),
                max_retries=max(max_retries, 3)
            )

            return response_obj

        except ImportError:
            error_info_str = "Google GenAI lib not found. pip install google-generativeai"
            self.logger.error(error_info_str)
            raise
        except Exception as e:
            error_info_str = f"Google vision generation failed: {e}"
            self.logger.error(error_info_str)
            raise
        finally:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log the interaction (final logging with response)
            self._log_interaction(
                model=model_name,
                prompt=prompt,
                response=response_obj,
                token_usage=token_details,
                error_info=error_info_str,
                duration_ms=duration_ms,
                request_schema=schema,
                is_before_call=False,
                txt_filepath=txt_log_path,
                json_filepath=json_log_path,
            )

    def generate_dict(
        self,
        prompt: str,
        schema: str,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_retries: int = 1,
        enable_web_search: bool = False,
        anthropic_web_search: bool = False,
        duckduckgo_search: bool = False,
        fallback_models: Optional[List[str]] = None,
        images: Optional[List[ImageInput]] = None,
    ) -> dict:
        """
        Generate structured output as a plain Python dictionary using string schema.

        NEW: Supports JSON-consistent curly brace syntax!

        Args:
            prompt: The input prompt
            schema: String schema definition (supports both legacy and new curly brace syntax)
                   Examples:
                   - "{name, age:int, email?}" - Single object
                   - "[{name, email}]" - Array of objects
                   - "{team, members:[{name, role}]}" - Nested structures
                   - "name, age:int" - Legacy format (still works)
            model: Model to use (defaults to DEFAULT_MODEL)
            temperature: Sampling temperature
            max_retries: Maximum number of retries
            enable_web_search: Enable web search (automatically chooses best method for model)
            anthropic_web_search: [DEPRECATED] Enable Anthropic web search (Anthropic models only)
            duckduckgo_search: [DEPRECATED] Enable DuckDuckGo search with 3-step processing
            fallback_models: Optional list of fallback models to try if primary model fails
            images: Optional list of ImageInput objects for vision-capable models

        Returns:
            Plain Python dictionary (not a Pydantic model)

        Examples:
            # NEW: JSON-consistent syntax
            result = client.generate_dict("Create a user profile", "{name, age:int, email?}")
            # Returns: {"name": "John Doe", "age": 30, "email": "john@example.com"}

            # NEW: Array of objects
            result = client.generate_dict("List team members", "[{name, role}]")
            # Returns: [{"name": "Alice", "role": "Developer"}, {"name": "Bob", "role": "Designer"}]

            # NEW: Nested structures
            result = client.generate_dict("Create team data", "{team, members:[{name, role}]}")
            # Returns: {"team": "Engineering", "members": [{"name": "Alice", "role": "Developer"}]}
        """
        import string_schema

        # Validate schema first and get detailed information
        validation = string_schema.validate_string_schema(schema)
        if not validation["valid"]:
            raise ValueError(f"Invalid schema: {', '.join(validation['errors'])}")

        # Log schema features for debugging
        if validation.get("warnings"):
            self.logger.warning(f"Schema warnings: {validation['warnings']}")
        self.logger.info(f"Schema features used: {validation.get('features_used', [])}")

        # Handle array schemas by wrapping them in an object for instructor compatibility
        # Array schemas like [{name, age}] need to be wrapped as {items:[{name, age}]}
        # so that instructor can handle them properly
        working_schema = schema
        is_array_schema = schema.strip().startswith("[") and schema.strip().endswith("]")
        if is_array_schema:
            working_schema = f"{{items:{schema}}}"

        # Convert string schema to Pydantic model (supports new curly brace syntax)
        output_model = string_schema.string_to_model(working_schema, "DictGenerationModel")

        # Generate structured output using existing infrastructure
        pydantic_result = self.generate_structured(
            prompt=prompt,
            output_model=output_model,
            model=model,
            temperature=temperature,
            max_retries=max_retries,
            enable_web_search=enable_web_search,
            anthropic_web_search=anthropic_web_search,
            duckduckgo_search=duckduckgo_search,
            fallback_models=fallback_models,
            images=images,
        )

        # Convert Pydantic model to plain dictionary
        result_dict = pydantic_result.model_dump()

        # If we wrapped an array schema, unwrap the result
        if is_array_schema and "items" in result_dict:
            result_dict = result_dict["items"]

        # Use string_schema's validation for additional safety
        try:
            validated_result = string_schema.validate_to_dict(result_dict, schema)
            return validated_result
        except Exception as e:
            self.logger.warning(f"Schema validation warning: {e}")
            # Return original result if validation fails
            return result_dict

    def _generate_standard(
        self,
        prompt: str,
        output_model: Type[T],
        model: str,
        temperature: float,
        max_retries: int,
        schema: str = None,
    ) -> T:
        """Standard generation without search (preserves original functionality)"""
        response_obj = None
        token_details = None
        error_info_str = None

        client = self._get_client_for_model(model, enable_anthropic_search=False)
        provider, model_name = self.determine_provider(model)

        # Log "before call" for txt file logging
        txt_log_path, json_log_path = self._log_interaction(
            model, prompt, request_schema=schema, is_before_call=True
        )

        # Track timing for database logging
        start_time = time.time()

        messages = [{"role": "user", "content": prompt}]
        try:
            self.logger.info(f"Generating with {model} ({provider}). Prompt: '{prompt[:100]}...'")
            kwargs = {"messages": messages, "response_model": output_model, "max_retries": max_retries}

            if provider != "google":
                kwargs["model"] = model_name
                kwargs["temperature"] = temperature

                if provider == "anthropic":
                    kwargs["max_tokens"] = 1024
            else:
                if temperature != 0.0:
                    kwargs["generation_config"] = {"temperature": temperature}

            if provider == "google":
                response_obj = self._handle_google_rate_limit_retry(
                    lambda: client.chat.completions.create(**kwargs), max_retries=max(max_retries, 3)
                )
            else:
                response_obj = client.chat.completions.create(**kwargs)

            if (
                hasattr(response_obj, "_raw_response")
                and hasattr(response_obj._raw_response, "usage")
                and response_obj._raw_response.usage
            ):
                raw_usage = response_obj._raw_response.usage
                if hasattr(raw_usage, "input_tokens"):
                    token_details = {
                        "prompt_tokens": raw_usage.input_tokens,
                        "completion_tokens": raw_usage.output_tokens,
                        "total_tokens": raw_usage.input_tokens + raw_usage.output_tokens,
                    }
                else:
                    token_details = {
                        "prompt_tokens": raw_usage.prompt_tokens,
                        "completion_tokens": raw_usage.completion_tokens,
                        "total_tokens": raw_usage.total_tokens,
                    }
            elif hasattr(response_obj, "usage") and response_obj.usage:
                raw_usage = response_obj.usage
                if hasattr(raw_usage, "input_tokens"):
                    token_details = {
                        "prompt_tokens": raw_usage.input_tokens,
                        "completion_tokens": raw_usage.output_tokens,
                        "total_tokens": raw_usage.input_tokens + raw_usage.output_tokens,
                    }
                else:
                    token_details = {
                        "prompt_tokens": raw_usage.prompt_tokens,
                        "completion_tokens": raw_usage.completion_tokens,
                        "total_tokens": raw_usage.total_tokens,
                    }
            self.logger.info(f"Successfully generated structured output with {model}.")
            return response_obj
        except Exception as e:
            error_info_str = (
                f"Error with {model}: {type(e).__name__} - {str(e)}. "
                f"Traceback: {traceback.format_exc()}"
            )
            self.logger.error(error_info_str)
            raise
        finally:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log the interaction (final logging with response)
            self._log_interaction(
                model=model,
                prompt=prompt,
                response=response_obj,
                token_usage=token_details,
                error_info=error_info_str,
                duration_ms=duration_ms,
                request_schema=schema,
                is_before_call=False,
                txt_filepath=txt_log_path,
                json_filepath=json_log_path,
            )

    def get_model_info(self, model: str) -> Dict[str, Any]:
        try:
            provider, model_name = self.determine_provider(model)
            info = {"model_name": model_name, "provider": provider, "configured": True}

            # Add search capability info
            if provider == "anthropic":
                info["supports_anthropic_web_search"] = True
            info["supports_duckduckgo_search"] = True

            return info
        except ValueError as e:
            return {"model_name": model, "provider": "Unknown", "configured": False, "error": str(e)}

    def get_ollama_models(self) -> List[str]:
        """Query Ollama server for available models"""
        if not self.model_manager.has_provider("ollama"):
            return []

        # Use the ModelManager's simple method to get Ollama models
        ollama_base_url = self.bootstrap.get("ollama_base_url", "http://localhost:11434")
        return self.model_manager.get_ollama_models(ollama_base_url)

    def get_available_models(self) -> List[str]:
        """Get available models using bootstrap configuration"""
        available = []

        # Add models from each provider if configured
        if self.model_manager.has_provider("openai"):
            available.extend(self.bootstrap.get("openai_models", []))

        if self.model_manager.has_provider("anthropic"):
            available.extend(self.bootstrap.get("anthropic_models", []))

        if self.model_manager.has_provider("google"):
            available.extend(self.bootstrap.get("google_models", []))

        if self.model_manager.has_provider("ollama"):
            # Get actual Ollama models instead of placeholder
            ollama_models = self.get_ollama_models()
            if ollama_models:
                available.extend(ollama_models)
            else:
                # Fallback to placeholder if query fails
                available.append("ollama (dynamic models)")

        return sorted(list(set(available)))

    def get_models_grouped_by_provider(self) -> Dict[str, List[str]]:
        """Get models grouped by provider with alphabetical sorting within each group"""
        grouped_models = {"anthropic": [], "google": [], "openai": [], "ollama": []}

        # Add models from each provider if configured
        if self.model_manager.has_provider("anthropic"):
            models = self.bootstrap.get("anthropic_models", [])
            grouped_models["anthropic"] = sorted(models)

        if self.model_manager.has_provider("google"):
            models = self.bootstrap.get("google_models", [])
            grouped_models["google"] = sorted(models)

        if self.model_manager.has_provider("openai"):
            models = self.bootstrap.get("openai_models", [])
            grouped_models["openai"] = sorted(models)

        if self.model_manager.has_provider("ollama"):
            ollama_models = self.get_ollama_models()
            if ollama_models:
                grouped_models["ollama"] = sorted(ollama_models)

        # Remove empty groups
        return {provider: models for provider, models in grouped_models.items() if models}

    def _generate_anthropic_with_search(
        self,
        prompt: str,
        output_model: Type[T],
        model: str,
        temperature: float,
        max_retries: int,
        schema: str = None,
    ) -> T:
        """Direct Anthropic web search integration without separate class"""
        response_obj = None
        token_details = None
        error_info_str = None

        # Get Instructor-wrapped Anthropic client with search enabled
        client = self._get_anthropic_client(with_search=True)
        _, model_name = self.determine_provider(model)

        # Log "before call" for txt file logging
        txt_log_path, json_log_path = self._log_interaction(
            model, prompt, request_schema=schema, is_before_call=True, search_type="anthropic_web_search"
        )

        # Track timing for database logging
        start_time = time.time()

        try:
            self.logger.info(
                f"Generating with Anthropic web search using {model}. Prompt: '{prompt[:100]}...'"
            )

            # Direct call with web search tools - no prompt wrapping needed!
            response_obj = client.messages.create(
                model=model_name,
                max_tokens=4000,
                temperature=temperature,
                response_model=output_model,
                max_retries=max_retries,
                tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract token usage if available
            if hasattr(response_obj, "_raw_response") and hasattr(response_obj._raw_response, "usage"):
                raw_usage = response_obj._raw_response.usage
                token_details = {
                    "prompt_tokens": raw_usage.input_tokens,
                    "completion_tokens": raw_usage.output_tokens,
                    "total_tokens": raw_usage.input_tokens + raw_usage.output_tokens,
                }

            self.logger.info(
                f"Successfully generated structured output with Anthropic web search using {model}."
            )
            return response_obj

        except Exception as e:
            error_info_str = (
                f"Error with Anthropic web search using {model}: {type(e).__name__} - {str(e)}. "
                f"Traceback: {traceback.format_exc()}"
            )
            self.logger.error(error_info_str)
            raise
        finally:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log the interaction (final logging with response)
            self._log_interaction(
                model=model,
                prompt=prompt,
                response=response_obj,
                token_usage=token_details,
                error_info=error_info_str,
                duration_ms=duration_ms,
                search_type="anthropic_web_search",
                request_schema=schema,
                is_before_call=False,
                txt_filepath=txt_log_path,
                json_filepath=json_log_path,
            )

    def upload_to_cloudinary(
        self,
        image_data: Union[bytes, str, Path],
        filename: Optional[str] = None,
        folder: str = "united_llm_uploads",
        cloudinary_config: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload an image to Cloudinary for public access.

        This is a standalone function for uploading images to Cloudinary without
        any AI transformation. Useful when you just need a public URL for an image.

        Args:
            image_data: Image as bytes, file path, or base64 string
            filename: Optional filename (without extension)
            folder: Cloudinary folder to upload to
            cloudinary_config: Optional dict with 'cloud_name', 'api_key', 'api_secret'
                              If not provided, will try to use CLOUDINARY_URL env var

        Returns:
            Dict containing:
            - success: bool
            - cloudinary_url: str (public URL of uploaded image)
            - public_id: str (Cloudinary public ID for management)
            - message: str
            - error: str (if failed)

        Raises:
            ValueError: If Cloudinary is not configured
            Exception: If upload fails
        """
        start_time = time.time()

        try:
            # Import and configure Cloudinary
            try:
                import cloudinary
                import cloudinary.uploader
            except ImportError as e:
                raise ValueError(f"Cloudinary not available: {e}")

            # Configure Cloudinary
            if cloudinary_config:
                cloudinary.config(**cloudinary_config, secure=True)
            else:
                # Try to get from environment
                cloudinary_url = os.environ.get("CLOUDINARY_URL")
                if not cloudinary_url:
                    raise ValueError(
                        "Cloudinary not configured. Please provide cloudinary_config parameter "
                        "or set CLOUDINARY_URL environment variable"
                    )

                # Parse CLOUDINARY_URL manually
                if not cloudinary_url.startswith("cloudinary://"):
                    raise ValueError("Invalid CLOUDINARY_URL format")

                # Remove cloudinary:// prefix and parse
                url_part = cloudinary_url[13:]
                if "@" not in url_part:
                    raise ValueError("Invalid CLOUDINARY_URL format")

                credentials, cloud_name = url_part.rsplit("@", 1)
                if ":" not in credentials:
                    raise ValueError("Invalid CLOUDINARY_URL format")

                api_key, api_secret = credentials.split(":", 1)
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    secure=True
                )

            # Process image data
            if isinstance(image_data, (str, Path)):
                if str(image_data).startswith(('http://', 'https://')):
                    # Download from URL
                    response = requests.get(str(image_data), timeout=30)
                    response.raise_for_status()
                    image_bytes = response.content
                elif str(image_data).startswith('data:image'):
                    # Base64 data URL
                    import base64
                    _, data = str(image_data).split(',', 1)
                    image_bytes = base64.b64decode(data)
                else:
                    # File path
                    with open(image_data, 'rb') as f:
                        image_bytes = f.read()
            else:
                # Already bytes
                image_bytes = image_data

            # Generate filename if not provided
            if not filename:
                import hashlib
                content_hash = hashlib.md5(image_bytes).hexdigest()[:8]
                filename = f"upload_{int(time.time())}_{content_hash}"

            # Upload to Cloudinary
            self.logger.info(f"Uploading image to Cloudinary folder: {folder}")

            cloudinary_result = cloudinary.uploader.upload(
                image_bytes,
                public_id=f"{folder}/{filename}",
                folder=folder,
                resource_type="image",
                format="jpg",
                quality="auto:good"
            )

            cloudinary_url = cloudinary_result["secure_url"]
            public_id = cloudinary_result["public_id"]

            self.logger.info(f"Image uploaded to Cloudinary: {cloudinary_url}")

            # Log the interaction
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_interaction(
                model="cloudinary-upload",
                prompt=f"Upload to folder: {folder}",
                response={"cloudinary_url": cloudinary_url, "public_id": public_id},
                duration_ms=duration_ms,
                is_before_call=False
            )

            return {
                "success": True,
                "cloudinary_url": cloudinary_url,
                "public_id": public_id,
                "message": "Image uploaded to Cloudinary successfully"
            }

        except Exception as e:
            error_msg = f"Cloudinary upload failed: {str(e)}"
            self.logger.error(error_msg)

            return {
                "success": False,
                "error": error_msg
            }

    def delete_from_cloudinary(
        self,
        public_id: str,
        cloudinary_config: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Delete an image from Cloudinary.

        Args:
            public_id: The public ID of the image to delete
            cloudinary_config: Optional Cloudinary configuration

        Returns:
            True if successful, False otherwise
        """
        try:
            # Import and configure Cloudinary
            import cloudinary
            import cloudinary.uploader

            # Configure Cloudinary
            if cloudinary_config:
                cloudinary.config(**cloudinary_config, secure=True)
            else:
                # Try to get from environment
                cloudinary_url = os.environ.get("CLOUDINARY_URL")
                if not cloudinary_url:
                    self.logger.warning("Cloudinary not configured for deletion")
                    return False

                # Parse CLOUDINARY_URL manually
                if not cloudinary_url.startswith("cloudinary://"):
                    return False

                url_part = cloudinary_url[13:]
                if "@" not in url_part:
                    return False

                credentials, cloud_name = url_part.rsplit("@", 1)
                if ":" not in credentials:
                    return False

                api_key, api_secret = credentials.split(":", 1)
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    secure=True
                )

            result = cloudinary.uploader.destroy(public_id)
            success = result.get("result") == "ok"

            if success:
                self.logger.info(f"Deleted image from Cloudinary: {public_id}")
            else:
                self.logger.warning(f"Failed to delete image from Cloudinary: {public_id}")

            return success

        except Exception as e:
            self.logger.error(f"Error deleting image from Cloudinary: {e}")
            return False

    def transform_image_with_cloudinary(
        self,
        image_data: Union[bytes, str, Path],
        prompt: str = "Keep the man's face, body shape the same",
        model: str = "black-forest-labs/FLUX.1-kontext-pro",
        width: int = 320,
        height: int = 320,
        steps: int = 4,
        cloudinary_folder: str = "united_llm_transforms",
        cleanup_cloudinary: bool = True,
        cloudinary_config: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Transform an image using Cloudinary upload + Together AI transformation.

        This function:
        1. Uploads the image to Cloudinary for public access
        2. Uses Together AI to transform the image using the Cloudinary URL
        3. Optionally cleans up the uploaded image from Cloudinary

        Args:
            image_data: Image as bytes, file path, or base64 string
            prompt: Transformation prompt for Together AI
            model: Together AI model to use (default: FLUX.1 Kontext Pro)
            width: Output image width
            height: Output image height
            steps: Number of transformation steps
            cloudinary_folder: Cloudinary folder to upload to
            cleanup_cloudinary: Whether to delete the uploaded image after transformation
            cloudinary_config: Optional dict with 'cloud_name', 'api_key', 'api_secret'
                              If not provided, will try to use CLOUDINARY_URL env var

        Returns:
            Dict containing:
            - success: bool
            - cloudinary_url: str (URL of uploaded image)
            - transformed_url: str (URL of generated image)
            - cloudinary_public_id: str (for cleanup)
            - message: str
            - error: str (if failed)

        Raises:
            ValueError: If Cloudinary or Together AI is not configured
            Exception: If upload or transformation fails
        """
        start_time = time.time()
        cloudinary_public_id = None

        try:
            # Upload image to Cloudinary using the dedicated function
            upload_result = self.upload_to_cloudinary(
                image_data=image_data,
                filename=f"transform_{int(time.time())}",
                folder=cloudinary_folder,
                cloudinary_config=cloudinary_config
            )

            if not upload_result["success"]:
                raise Exception(upload_result.get("error", "Cloudinary upload failed"))

            cloudinary_url = upload_result["cloudinary_url"]
            cloudinary_public_id = upload_result["public_id"]

            self.logger.info(f"Image uploaded to Cloudinary: {cloudinary_url}")

            # Transform with Together AI
            self.logger.info(f"Transforming image with Together AI model: {model}")

            try:
                from together import Together
                together_client = Together()

                generation = together_client.images.generate(
                    model=model,
                    prompt=prompt,
                    image_url=cloudinary_url,
                    width=width,
                    height=height,
                    steps=steps,
                )

                transformed_url = generation.data[0].url
                self.logger.info(f"Image transformed successfully: {transformed_url}")

                # Log the interaction
                duration_ms = int((time.time() - start_time) * 1000)
                self._log_interaction(
                    model=model,
                    prompt=f"Image transformation: {prompt}",
                    response={"transformed_url": transformed_url, "cloudinary_url": cloudinary_url},
                    duration_ms=duration_ms,
                    is_before_call=False
                )

                result = {
                    "success": True,
                    "cloudinary_url": cloudinary_url,
                    "transformed_url": transformed_url,
                    "cloudinary_public_id": cloudinary_public_id,
                    "message": "Image transformation completed successfully"
                }

                # Cleanup Cloudinary if requested
                if cleanup_cloudinary and cloudinary_public_id:
                    success = self.delete_from_cloudinary(cloudinary_public_id, cloudinary_config)
                    result["cloudinary_cleaned"] = success

                return result

            except Exception as together_error:
                error_msg = f"Together AI transformation failed: {together_error}"
                self.logger.error(error_msg)

                # Cleanup on failure
                if cleanup_cloudinary and cloudinary_public_id:
                    self.delete_from_cloudinary(cloudinary_public_id, cloudinary_config)

                return {
                    "success": False,
                    "error": error_msg,
                    "cloudinary_url": cloudinary_url,
                    "cloudinary_public_id": cloudinary_public_id
                }

        except Exception as e:
            error_msg = f"Image transformation failed: {str(e)}"
            self.logger.error(error_msg)

            # Cleanup on failure
            if cleanup_cloudinary and cloudinary_public_id:
                self.delete_from_cloudinary(cloudinary_public_id, cloudinary_config)

            return {
                "success": False,
                "error": error_msg,
                "cloudinary_public_id": cloudinary_public_id
            }
