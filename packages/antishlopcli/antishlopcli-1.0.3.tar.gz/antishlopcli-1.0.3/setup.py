#!/usr/bin/env python3

from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "AI-Powered Security Vulnerability Scanner with intelligent multi-agent analysis"

try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = [
        "openai>=1.0.0",
        "langchain>=0.1.0", 
        "langchain-openai>=0.1.0",
        "langgraph>=0.1.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        "typing-extensions>=4.0.0"
    ]

setup(
    name="antishlopcli",
    version="1.0.3",
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