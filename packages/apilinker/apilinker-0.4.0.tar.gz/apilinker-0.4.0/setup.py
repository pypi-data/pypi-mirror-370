#!/usr/bin/env python
"""Minimal setup script for APILinker."""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

__version__ = "0.4.0"

setup(
    name="apilinker",
    version=__version__,
    description="A universal bridge to connect, map, and automate data transfer between any two REST APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="K. Kartas",
    author_email="kkartas@users.noreply.github.com",
    url="https://github.com/kkartas/APILinker",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.23.0",
        "pyyaml>=6.0",
        "typer>=0.7.0",
        "pydantic>=2.0.0",
        "croniter>=1.3.8",
        "rich>=12.6.0",
        "cryptography>=41.0.0",
        "jsonschema>=4.18.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "types-croniter",
            "types-PyYAML",
            "black>=23.0.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
            "sphinx-autodoc-typehints>=2.0.0",
            "sphinx-autoapi>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "apilinker=apilinker.cli:app",
        ],
    },
)
