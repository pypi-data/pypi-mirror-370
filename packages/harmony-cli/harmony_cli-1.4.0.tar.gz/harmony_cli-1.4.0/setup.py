#!/usr/bin/env python3
"""
Setup script for Harmony CLI
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="harmony-cli",
    version="1.4.5",
    author="Mergen AI",
    author_email="info@mergen.az",
    description="Beautiful CLI for Harmony AI with Beta Mode - Advanced AI Assistant with Web Search by Mergen AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mergen-ai/harmony-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
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
    install_requires=[
        "rich>=12.0.0",
        "httpx>=0.24.0",
        "colorama>=0.4.4",
        "asyncio-compat>=0.1.2",
    ],
    entry_points={
        "console_scripts": [
            "harmony=harmony_cli.main:main",
            "harmony-cli=harmony_cli.main:main",
        ],
    },
    keywords="ai, cli, harmony, mergen, assistant, chat, artificial-intelligence",
    project_urls={
        "Bug Reports": "https://github.com/mergen-ai/harmony-cli/issues",
        "Source": "https://github.com/mergen-ai/harmony-cli",
        "Documentation": "https://docs.mergen.az/harmony-cli",
        "Homepage": "https://hal-x.ai",
    },
)
