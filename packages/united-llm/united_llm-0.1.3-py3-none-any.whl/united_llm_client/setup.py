#!/usr/bin/env python3
"""
Setup script for United LLM Client (client-only package)
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    with open(readme_path, "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_path, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version from the package
def get_version():
    init_file = os.path.join(os.path.dirname(__file__), "__init__.py")
    with open(init_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="united-llm-client",
    version=get_version(),
    author="United LLM Team",
    author_email="contact@united-llm.com",
    description="Lightweight client for United LLM API service",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/xychenmsn/united-llm",
    project_urls={
        "Bug Reports": "https://github.com/xychenmsn/united-llm/issues",
        "Source": "https://github.com/xychenmsn/united-llm",
        "Documentation": "https://github.com/xychenmsn/united-llm#readme",
        "Full Package": "https://pypi.org/project/united-llm/",
    },
    py_modules=["client"],
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
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    keywords=[
        "llm", "api-client", "openai", "anthropic", "google", "ollama", 
        "ai", "client", "lightweight"
    ],
    zip_safe=False,
)
