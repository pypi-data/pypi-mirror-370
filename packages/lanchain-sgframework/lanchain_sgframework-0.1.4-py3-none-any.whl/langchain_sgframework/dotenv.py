#!/usr/bin/python
# Created on 2025. 08. 20
# @Author  : 강성훈(ssogaree@gmail.com)
# @File    : langchain_sgframework/dotenv.py
# @version : 1.00.00
# Copyright (c) 1999-2025 KSFAMS Co., Ltd. All Rights Reserved.

import os

from functools import lru_cache
from dotenv import load_dotenv


@lru_cache()
def get_config(key: str, env_file='.env') -> str:
    load_dotenv(env_file, encoding='utf-8')
    return os.environ.get(key)
