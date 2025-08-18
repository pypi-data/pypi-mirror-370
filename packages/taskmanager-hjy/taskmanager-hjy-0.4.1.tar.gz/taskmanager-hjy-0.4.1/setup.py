#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全独立的 taskmanager-hjy 包
基于新包架构，无旧包依赖
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="taskmanager-hjy",
    version="0.4.1",  # 新版本，完全独立
    author="hjy",
    author_email="hjy@example.com",
    description="完全独立的任务管理包 - 基于新包架构，无旧包依赖",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hjy/taskmanager-hjy",
    packages=find_packages(),
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
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "loguru>=0.7.0",
        "redis>=4.5.0",
        "rq>=1.15.0",
        "pyyaml>=6.0",
        "typing-extensions>=4.0.0",
        # 使用新包，不依赖旧包
        "configmanager-hjy>=0.3.0",
        "datamanager-hjy>=0.3.0",
        "aimanager-hjy>=0.3.0",
        "keymanager-hjy>=0.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "isort>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "taskmanager-hjy=taskmanager_hjy.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
