#!/usr/bin/env python3
"""
Setup script for PyTTD - Python OpenTTD Client Library
"""

import os
import sys
from setuptools import setup, find_packages

# Ensure we're running on Python 3.11+
if sys.version_info < (3, 11):
    sys.exit("PyTTD requires Python 3.11 or higher")


# Read the long description from README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "A Python client library for OpenTTD"


# Read version from package
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "pyttd", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip("\"'")
    return "1.3.0"


setup(
    name="pyttd",
    version=get_version(),
    author="mssc89",
    author_email="pyttd@example.com",
    description="Python OpenTTD Client Library",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/mssc89/pyttd",
    project_urls={
        "Bug Tracker": "https://github.com/mssc89/pyttd/issues",
        "Documentation": "https://github.com/mssc89/pyttd#readme",
        "Source Code": "https://github.com/mssc89/pyttd",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Networking",
    ],
    keywords=[
        "openttd",
        "transport",
        "tycoon",
        "simulation",
        "game",
        "ai",
        "bot",
        "client",
        "network",
        "protocol",
        "multiplayer",
        "automation",
    ],
    python_requires=">=3.11",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
        "examples": [
            "colorama>=0.4.4",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyttd-example=pyttd.examples.data_display:main",
        ],
    },
    package_data={
        "pyttd": ["py.typed"],
    },
    include_package_data=True,
    zip_safe=False,
)
