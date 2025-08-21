#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EntangleKey - 量子もつれベースの分散セッションキー生成ライブラリ
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="entanglekey",
    version="1.0.0",
    author="tikisan",
    author_email="",
    description="量子もつれベースの分散セッションキー生成ライブラリ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tikipiya/EntangleKey",
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
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=3.4.8",
        "numpy>=1.20.0",
        "asyncio-mqtt>=0.13.0",
        "pynacl>=1.5.0",
        "websockets>=10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "entanglekey=entanglekey.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
