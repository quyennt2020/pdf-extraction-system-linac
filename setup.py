"""
Setup script for PDF Knowledge Graph Extraction System
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pdf-knowledge-graph-extractor",
    version="1.0.0",
    author="TPump",
    author_email="tpump@example.com",
    description="A comprehensive tool for extracting knowledge graphs from PDF documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tpump/pdf-knowledge-graph-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "viz": [
            "graphviz>=0.20.0",
            "pygraphviz>=1.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kg-extractor=backend.api.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.json", "*.yaml"],
    },
)
