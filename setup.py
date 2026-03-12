#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for multiagent-llm package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="multiagent-llm",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A LangGraph-based multi-agent research workflow system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/MultiagentLLM",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8+",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain==1.2.11",
        "langchain-core==1.2.18",
        "langchain-openai==1.1.11",
        "langchain-community==0.4.1",
        "langgraph==1.1.0",
        "langgraph-prebuilt==1.0.8",
        "python-dotenv==1.2.2",
        "openai==2.26.0",
        "pydantic==2.12.5",
        "requests==2.32.5",
    ],
    entry_points={
        "console_scripts": [
            "multiagent-llm=main:main",
        ],
    },
)
