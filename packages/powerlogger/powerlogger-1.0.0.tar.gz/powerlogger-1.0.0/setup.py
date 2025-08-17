#!/usr/bin/env python3
"""
Setup script for powerlogger package
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "PowerLogger - A high-performance, thread-safe logging library"

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return ["rich>=13.0.0"]

setup(
    name="powerlogger",
    version="1.0.0",
    author="Pandiyaraj Karuppasamy",
    author_email="pandiyarajk@live.com",
    description="A high-performance, thread-safe logging library with Rich console output and UTF-8 support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/kpandiyaraj/powerlogger",
    project_urls={
        "Bug Reports": "https://github.com/kpandiyaraj/powerlogger/issues",
        "Source": "https://github.com/kpandiyaraj/powerlogger",
        "Documentation": "https://github.com/kpandiyaraj/powerlogger#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers, Testers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: Text Processing :: General",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    keywords="logging, rich, console, utf8, unicode, thread-safe, file-rotation, windows",
    license="MIT",
    zip_safe=False,
    include_package_data=True,
    package_data={
        "powerlogger": ["*.ini", "*.txt"],
    },
)
