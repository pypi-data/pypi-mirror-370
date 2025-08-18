#!/usr/bin/env python3
"""
United LLM Command Line Interface

Provides command-line access to United LLM functionality.
"""

import argparse
import sys
from typing import Optional

from . import __version__, print_version
from .client import LLMClient
from .config import setup_united_llm_environment, get_config


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="united-llm",
        description="United LLM - Unified interface for multiple LLM providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"united-llm {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show system information")
    info_parser.add_argument(
        "--config", 
        action="store_true", 
        help="Show configuration details"
    )
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test LLM connectivity")
    test_parser.add_argument(
        "--model", 
        type=str, 
        help="Specific model to test (default: test all available)"
    )
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate text using LLM")
    generate_parser.add_argument(
        "prompt", 
        type=str, 
        help="The prompt to send to the LLM"
    )
    generate_parser.add_argument(
        "--model", 
        type=str, 
        help="Model to use (default: configured default model)"
    )
    generate_parser.add_argument(
        "--temperature", 
        type=float, 
        default=0.7, 
        help="Temperature for generation (default: 0.7)"
    )
    
    return parser


def cmd_info(args) -> int:
    """Handle the info command."""
    print_version()
    print()
    
    try:
        setup_united_llm_environment()
        config = get_config()
        client = LLMClient()
        
        print("📊 System Information:")
        print(f"  Available models: {len(client.get_available_models())}")
        print(f"  OpenAI configured: {client.has_openai}")
        print(f"  Anthropic configured: {client.has_anthropic}")
        print(f"  Google configured: {client.has_google}")
        print(f"  Ollama configured: {client.has_ollama}")
        
        if args.config:
            print("\n⚙️  Configuration:")
            print(f"  Default model: {config.get('default_model')}")
            print(f"  Temperature: {config.get('temperature')}")
            print(f"  Max tokens: {config.get('max_tokens')}")
            print(f"  Database logging: {config.get('log_to_db')}")
            print(f"  API host: {config.get('api_host')}")
            print(f"  API port: {config.get('api_port')}")
        
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def cmd_test(args) -> int:
    """Handle the test command."""
    try:
        setup_united_llm_environment()
        client = LLMClient()
        
        if args.model:
            models_to_test = [args.model]
        else:
            models_to_test = client.get_available_models()[:3]  # Test first 3 models
        
        print("🧪 Testing LLM connectivity...")
        
        for model in models_to_test:
            try:
                print(f"  Testing {model}...", end=" ")
                response = client.generate_text(
                    prompt="Say 'Hello from United LLM!'",
                    model=model,
                    max_tokens=50
                )
                print("✅ OK")
            except Exception as e:
                print(f"❌ Failed: {str(e)[:50]}...")
        
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def cmd_generate(args) -> int:
    """Handle the generate command."""
    try:
        setup_united_llm_environment()
        client = LLMClient()
        
        print(f"🤖 Generating response using {args.model or 'default model'}...")
        print()
        
        response = client.generate_text(
            prompt=args.prompt,
            model=args.model,
            temperature=args.temperature
        )
        
        print("📝 Response:")
        print(response)
        
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == "info":
        return cmd_info(args)
    elif args.command == "test":
        return cmd_test(args)
    elif args.command == "generate":
        return cmd_generate(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
