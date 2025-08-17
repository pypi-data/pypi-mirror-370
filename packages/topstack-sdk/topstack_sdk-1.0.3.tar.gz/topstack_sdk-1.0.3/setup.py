#!/usr/bin/env python3
"""
TopStack Python SDK 安装配置
"""

from setuptools import setup, find_packages

setup(
    name="topstack-sdk",
    version="1.0.3",
    description="TopStack Python SDK - 用于与 TopStack 平台交互的 Python 客户端库",
    author="TopStack Team",
    author_email="support@topstack.com",
    url="https://github.com/topstack/topstack-sdk-python",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=1.8.0",
        "python-dateutil>=2.8.0"
    ],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
) 