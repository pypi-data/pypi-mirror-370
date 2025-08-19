#!/usr/bin/env python3
"""
Setup script for rag-mcp-server-lizhibing
"""
from setuptools import setup, find_packages

setup(
    name="rag-mcp-server-lizhibing",
    version="0.1.2",
    description="RAG MCP Server for document search and retrieval",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/rag-mcp-server",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "httpx>=0.28.1",
        "mcp[cli]>=1.13.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=["mcp", "rag", "document-search", "ai"],
) 