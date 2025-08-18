"""
Logging Configuration for Unified LLM System
Handles multiple log types:
- App logs (console + file)
- FastAPI server logs
- LLM call request/response logs
"""

import logging
import logging.config
import os
from pathlib import Path
from datetime import datetime


def ensure_log_directories(log_dir: str = "logs"):
    """
    Ensure all necessary log directories exist
    This is called automatically by setup_logging() but can be called independently
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    (log_path / "llm_calls").mkdir(parents=True, exist_ok=True)
    return log_path


def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """
    Setup comprehensive logging for the united LLM system

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
    """

    # Ensure log directories exist - create them automatically
    log_path = ensure_log_directories(log_dir)

    # Log file paths
    app_log_file = log_path / "app.log"
    server_log_file = log_path / "server.log"
    llm_calls_dir = log_path / "llm_calls"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {"format": "%(asctime)s - %(levelname)s - %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"},
            "console": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "datefmt": "%H:%M:%S"},
            "llm_calls": {"format": "%(asctime)s - %(levelname)s - %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "console",
                "stream": "ext://sys.stdout",
            },
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": str(app_log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "server_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": str(server_log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "llm_calls_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "INFO",
                "formatter": "llm_calls",
                "filename": str(llm_calls_dir / "llm_calls.log"),
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,  # Keep 30 days
                "encoding": "utf8",
            },
        },
        "loggers": {
            # Root logger - captures everything and duplicates to app.log
            "": {"level": log_level, "handlers": ["console", "app_file"], "propagate": False},
            # FastAPI/Uvicorn server logs
            "uvicorn": {"level": "INFO", "handlers": ["console", "server_file"], "propagate": False},
            "uvicorn.error": {"level": "INFO", "handlers": ["console", "server_file"], "propagate": False},
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["server_file"],  # Only to file, not console
                "propagate": False,
            },
            "fastapi": {"level": "INFO", "handlers": ["console", "server_file"], "propagate": False},
            # LLM call specific logger
            "united_llm.calls": {"level": "INFO", "handlers": ["llm_calls_file"], "propagate": False},
            # Main application loggers
            "united_llm": {"level": log_level, "handlers": ["console", "app_file"], "propagate": False},
            "united_llm.client": {"level": log_level, "handlers": ["console", "app_file"], "propagate": False},
            "united_llm.search": {"level": log_level, "handlers": ["console", "app_file"], "propagate": False},
            "united_llm.database": {"level": log_level, "handlers": ["console", "app_file"], "propagate": False},
        },
    }

    logging.config.dictConfig(logging_config)

    # Log startup message
    logger = logging.getLogger("united_llm")
    logger.info(f"Logging initialized - Level: {log_level}, Directory: {log_dir}")
    logger.info(f"App logs: {app_log_file}")
    logger.info(f"Server logs: {server_log_file}")
    logger.info(f"LLM call logs: {llm_calls_dir}")


def get_llm_calls_logger():
    """Get the dedicated LLM calls logger"""
    return logging.getLogger("united_llm.calls")


def log_llm_call(
    model: str,
    prompt: str,
    response: str = None,
    error: str = None,
    duration_ms: int = None,
    token_usage: dict = None,
    provider: str = None,
):
    """
    Log an LLM call with structured information

    Args:
        model: Model name used
        prompt: Input prompt
        response: Generated response (if successful)
        error: Error message (if failed)
        duration_ms: Call duration in milliseconds
        token_usage: Token usage statistics
        provider: Provider name (openai, anthropic, google, ollama)
    """
    logger = get_llm_calls_logger()

    # Create structured log entry
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "provider": provider,
        "model": model,
        "prompt_length": len(prompt) if prompt else 0,
        "prompt_preview": prompt[:100] + "..." if prompt and len(prompt) > 100 else prompt,
        "duration_ms": duration_ms,
        "token_usage": token_usage,
        "status": "success" if response else "error",
    }

    if response:
        log_data["response_length"] = len(response)
        log_data["response_preview"] = response[:100] + "..." if len(response) > 100 else response

    if error:
        log_data["error"] = error

    # Log as structured JSON-like string
    import json

    log_message = json.dumps(log_data, ensure_ascii=False, separators=(",", ":"))

    if error:
        logger.error(f"LLM_CALL_FAILED: {log_message}")
    else:
        logger.info(f"LLM_CALL_SUCCESS: {log_message}")


def setup_fastapi_logging():
    """
    Configure FastAPI/Uvicorn specific logging
    Call this when starting the FastAPI server
    """
    # Ensure server logs go to the right place
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access = logging.getLogger("uvicorn.access")

    # Custom access log format for FastAPI
    class AccessLogFilter(logging.Filter):
        def filter(self, record):
            # Add custom formatting for access logs
            return True

    uvicorn_access.addFilter(AccessLogFilter())

    return uvicorn_logger


# Convenience function to get main app logger
def get_logger(name: str = None):
    """Get a logger for the application"""
    if name:
        return logging.getLogger(f"united_llm.{name}")
    return logging.getLogger("united_llm")
