#!/usr/bin/env python3
"""Setup script for askp - Perplexity CLI tool."""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "A command-line interface for Perplexity AI"

# Read requirements from requirements.txt
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "requests>=2.31.0",
            "colorama>=0.4.6", 
            "prompt_toolkit>=3.0.47",
            "pypdf>=4.2.0",
            "Pillow>=10.0.0",
            "pytesseract>=0.3.10",
            "python-docx>=0.8.11",
            "beautifulsoup4>=4.12.0",
            "pyperclip>=1.8.2"
        ]

setup(
    name="askp-cli",
    version="1.0.8",
    author="LienS",
    author_email="simen@cvcv.no",
    description="A command-line interface for Perplexity AI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/liensimen/askp",
    packages=find_packages(),
    py_modules=["askp"], 
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "askp=askp:main",
        ],
    },
    keywords="perplexity ai cli command-line chat assistant",
    project_urls={
        "Bug Reports": "https://github.com/liensimen/askp/issues",  # Update this
        "Source": "https://github.com/liensimen/askp",  # Update this
    },
)