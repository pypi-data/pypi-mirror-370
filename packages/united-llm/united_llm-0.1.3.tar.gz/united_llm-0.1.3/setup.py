#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read client-only requirements
def read_client_requirements():
    try:
        with open("united_llm_client/requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        # Fallback to minimal client requirements if file not found
        return ["requests>=2.31.0", "typing-extensions>=4.0.0"]

# Get version from the package
def get_version():
    version_file = os.path.join("united_llm", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="united-llm",
    version=get_version(),
    author="United LLM Team",
    author_email="contact@united-llm.com",
    description="United LLM client with search capabilities and FastAPI server",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/xychenmsn/united-llm",
    project_urls={
        "Bug Reports": "https://github.com/xychenmsn/united-llm/issues",
        "Source": "https://github.com/xychenmsn/united-llm",
        "Documentation": "https://github.com/xychenmsn/united-llm#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "client": read_client_requirements(),
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings[python]>=0.22.0",
        ],
        "all": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings[python]>=0.22.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "united-llm=united_llm.cli:main",
            "united-llm-server=united_llm.api.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "united_llm": ["py.typed"],
    },
    keywords=[
        "llm", "openai", "anthropic", "google", "ollama", 
        "fastapi", "search", "structured-output", "ai"
    ],
    zip_safe=False,
) 