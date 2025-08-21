#!/usr/bin/python
# Created on 2025. 08. 21
# @Author  : 강성훈(ssogaree@gmail.com)
# @File    : sgframework/utils/string.py
# @version : 1.00.00
# Copyright (c) 1999-2025 KSFAMS Co., Ltd. All Rights Reserved.

import re


def check_kor(text):
    """
    [text] 에 한글 존재 여부 확인
    :param text:
    :return:
    """
    p = re.compile('[ㄱ-힣]')
    r = p.search(text)
    if r is None:
        return False
    else:
        return True
