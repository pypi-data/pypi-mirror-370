#!/usr/bin/python
# Created on 2025. 08. 20
# @Author  : 강성훈(ssogaree@gmail.com)
# @File    : sgframework/langchain/logging.py
# @version : 1.00.00
# Copyright (c) 1999-2025 KSFAMS Co., Ltd. All Rights Reserved.

import os


def langsmith(project_name: str = None, is_enable: bool = True):
    """
    Langsmith 추적 로깅을 처리한다.
    :param project_name:
    :param is_enable: Langsmith 추적 사용 여부 설정.
    :return:
    """
    if is_enable:
        api_key = os.environ.get('LANGSMITH_API_KEY', '')
        if api_key.strip() == '':
            print('LangSmith API Key가 설정되지 않았습니다.\n참고: https://smith.langchain.com')

        # LangSmith API 엔드포인트
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = project_name
        print('LangSmith 추적을 시작합니다.')
        print(f"[프로젝트명]\n{project_name}")
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        print('LangSmith 추적을 하지 않습니다.')


def env_variable(key: str, value: str):
    """
    env [key], [value] 임시 등록
    :param key:
    :param value:
    :return:
    """
    os.environ[key] = value
