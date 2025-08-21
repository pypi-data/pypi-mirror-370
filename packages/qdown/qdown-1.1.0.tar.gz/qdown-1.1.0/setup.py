#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# README.mdの内容を読み込む
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qdown",
    version="1.1.0",
    description="Client for QualitegDrive",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Qualiteg Inc.",
    author_email="qualiteger@qualiteg.com",
    url="https://github.com/qualiteg/qdown",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.23.0",
        "tqdm>=4.64.0",
    ],
    entry_points={
        "console_scripts": [
            "qdown=qdown.qdown:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)