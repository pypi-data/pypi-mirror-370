#!/usr/bin/python
# Created on 2025. 08. 20
# @Author  : 강성훈(ssogaree@gmail.com)
# @File    : sgframework/mcp/load_config.py
# @version : 1.00.00
# Copyright (c) 1999-2025 KSFAMS Co., Ltd. All Rights Reserved.

import json
from functools import lru_cache


def _load_mpc_config():
    """
    './.mcp_config.json' 경로의 MCP 서버 설정 파일을 로드 한다.
    :return:
    """
    try:
        with open('./.mcp_config.json', 'r') as config_file:
            print(f'config_file: {config_file}')
            return json.load(config_file)
    except Exception as e:
        print(f'설정 파일 로딩 오류: {e.__cause__}')
        return None


@lru_cache()
def get_config():
    config_file = _load_mpc_config()
    server_config = {}

    if config_file and "mcpServers" in config_file:
        for server_name, server_config_data in config_file["mcpServers"].items():
            # command가 있으면 stdio 방식
            if "command" in server_config_data:
                server_config[server_name] = {
                    "command": server_config_data.get("command"),
                    "args": server_config_data.get("args", []),
                    "transport": "stdio",
                }
            # url이 있으면 sse 방식
            elif "url" in server_config_data:
                server_config[server_name] = {
                    "url": server_config_data.get("url"),
                    "transport": "sse",
                }
    else:
        print('mcpServers 로 설정된 정보가 없습니다.')

    return server_config


mcp_config = get_config()
