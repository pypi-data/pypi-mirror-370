#!/usr/bin/python
# Created on 2025. 08. 19
# @Author  : 강성훈(ssogaree@gmail.com)
# @File    : /setup.py
# @version : 1.00.00
# Copyright (c) 1999-2025 KSFAMS Co., Ltd. All Rights Reserved.

from setuptools import setup, find_packages

setup(
    name="langchain-sgframework",
    version="0.1.1",
    description="LangChain Helper Library",
    author="ssogaree",
    author_email="ssogaree@gmail.com",
    url="",
    install_requires=[
        "langchain",
        "langchain-mcp-adapter"
    ],
    packages=find_packages(exclude=[]),
    keywords=[
        "sgframework",
    ],
    python_requires=">=3.13",
    package_data={},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
