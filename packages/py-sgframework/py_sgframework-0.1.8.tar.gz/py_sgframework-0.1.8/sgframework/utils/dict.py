#!/usr/bin/python
# Created on 2025. 08. 21
# @Author  : 강성훈(ssogaree@gmail.com)
# @File    : sgframework/utils/dict.py
# @version : 1.00.00
# Copyright (c) 1999-2025 KSFAMS Co., Ltd. All Rights Reserved.


def remove_ascii(text):
    """
    문자열에서 ASCII 문자를 제거합니다.
    """
    return ''.join(i for i in text if ord(i) < 128)


def remove_ascii_from_dict(data):
    """
    딕셔너리에서 ASCII 문자를 제거합니다.
    """
    new_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            new_data[key] = remove_ascii(value)
        else:
            new_data[key] = value
    return new_data
