#!/usr/bin/python
# Created on 2025. 08. 21
# @Author  : 강성훈(ssogaree@gmail.com)
# @File    : sgframework/langchain/document/info.py
# @version : 1.00.00
# Copyright (c) 1999-2025 KSFAMS Co., Ltd. All Rights Reserved.

from langchain_core.documents import Document


def show_metadata(docs: list[Document]):
    """
    [docs] 의 메타데이터 확인
    :param docs:
    :return:
    """
    if docs:
        print("[metadata]")
        print(list(docs[0].metadata.keys()))
        print(f"\n[{docs[0].metadata['source']}]")
        max_key_length = max(len(k) for k in docs[0].metadata.keys())
        for k, v in docs[0].metadata.items():
            print(f"{k:<{max_key_length}} : {v}")
    else:
        print('Document list is empty')
