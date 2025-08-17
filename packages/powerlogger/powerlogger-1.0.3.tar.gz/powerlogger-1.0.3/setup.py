#!/usr/bin/env python3
"""
Setup script for PowerLogger package.
"""

from setuptools import setup, find_packages
import os

def read_readme():
    """Read README.md file."""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "PowerLogger - A high-performance, thread-safe logging library"

def read_requirements():
    """Read requirements.txt file."""
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return ["rich>=13.0.0"]

setup(
    name="powerlogger",
    version="1.0.3",
    author="Pandiyaraj Karuppasamy",
    author_email="pandiyarajk@live.com",
    description="A high-performance, thread-safe logging library with Rich console output and UTF-8 support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Pandiyarajk/powerlogger",
    project_urls={
        "Bug Tracker": "https://github.com/Pandiyarajk/powerlogger/issues",
        "Documentation": "https://github.com/Pandiyarajk/powerlogger#readme",
        "Source Code": "https://github.com/Pandiyarajk/powerlogger",
        "Changelog": "https://github.com/Pandiyarajk/powerlogger/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
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
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
    },
    package_data={
        "powerlogger": ["*.ini", "*.txt"],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="logging, rich, console, utf8, unicode, thread-safe, file-rotation, windows",
)
