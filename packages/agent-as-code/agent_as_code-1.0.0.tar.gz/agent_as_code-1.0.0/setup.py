#!/usr/bin/env python3
"""
Setup script for Agent as Code (AaC) Python package.

This package provides a Python wrapper around the Go-based Agent as Code CLI,
enabling seamless integration with Python development workflows.
"""

import os
import platform
from pathlib import Path
from setuptools import setup, find_packages

# Read README for long description
def read_readme():
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return "Agent as Code - Docker-like CLI for AI agents"

# Get version from package
def get_version():
    version_file = Path(__file__).parent / "agent_as_code" / "__init__.py"
    if version_file.exists():
        content = version_file.read_text()
        for line in content.split('\n'):
            if line.startswith('__version__'):
                return line.split('"')[1]
    return "1.0.0"

# Platform-specific binary inclusion
def get_package_data():
    """Get package data including platform-specific binaries."""
    package_data = {
        'agent_as_code': [
            'bin/agent-linux-amd64',
            'bin/agent-linux-arm64',
            'bin/agent-darwin-amd64', 
            'bin/agent-darwin-arm64',
            'bin/agent-windows-amd64.exe',
            'bin/agent-windows-arm64.exe',
        ]
    }
    
    return package_data

setup(
    name="agent-as-code",
    version=get_version(),
    description="Docker-like CLI for AI agents",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Partha Sarathi Kundu",
    author_email="inboxpartha@outlook.com",
    url="https://agent-as-code.myagentregistry.com",
    project_urls={
        "Homepage": "https://agent-as-code.myagentregistry.com",
        "Documentation": "https://agent-as-code.myagentregistry.com/documentation",
        "Source": "https://github.com/pxkundu/agent-as-code",
    },
    packages=find_packages(),
    package_data=get_package_data(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",

        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - the Go binary is self-contained
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agent=agent_as_code.cli:main",
        ],
    },
    keywords=[
        "ai", "agents", "cli", "docker", "containers", "llm", "machine-learning",
        "artificial-intelligence", "automation", "microservices", "devops"
    ],
    zip_safe=False,  # Required for binary files
    
    # Additional metadata
    license="MIT",
    platforms=["any"],
    
    # Custom commands for development
    cmdclass={},
)