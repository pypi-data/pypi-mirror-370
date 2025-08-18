#!/usr/bin/env python3

from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "AI-Powered Security Vulnerability Scanner with intelligent multi-agent analysis"

requirements = [
    "openai",
    "colorama",
    "rich",
    "python-dotenv",
    "langchain==0.3.23",
    "langchain-core==0.3.62",
    "langchain-anthropic==0.3.14",
    "langchain-community==0.3.21",
    "langchain-openai==0.3.12",
    "langchain-pinecone==0.2.8",
    "langchain-text-splitters==0.3.8",
    "langgraph==0.2.67",
    "langgraph-checkpoint==2.0.10",
    "langgraph-sdk==0.1.51",
    "langsmith==0.2.11",
    "typing-extensions"
]

setup(
    name="antishlopcli",
    version="1.0.5",
    author="itscool2b",
    description="AI-Powered Security Vulnerability Scanner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "antishlop=antishlopcli.antishlop:main",
        ],
    },
)