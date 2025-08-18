"""
United LLM Client Package

A lightweight client library for interacting with the United LLM API service.
This package provides a simple interface for text generation and structured output
without requiring the full United LLM server dependencies.
"""

from .client import UnitedLLMClient

__version__ = "0.1.2"
__author__ = "United LLM Team"
__email__ = "contact@united-llm.com"

__all__ = ["UnitedLLMClient"]
