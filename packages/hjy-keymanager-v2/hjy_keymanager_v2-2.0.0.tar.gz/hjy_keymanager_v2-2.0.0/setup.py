#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="hjy-keymanager-v2",
    version="2.0.0",
    description="Hjy keymanager package",
    author="Hjy",
    author_email="hjy@example.com",
    packages=find_packages(),
    install_requires=[
        "loguru>=0.7.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
