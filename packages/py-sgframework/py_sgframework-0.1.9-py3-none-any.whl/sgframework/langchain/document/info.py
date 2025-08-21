#!/usr/bin/python
# Created on 2025. 08. 21
# @Author  : 강성훈(ssogaree@gmail.com)
# @File    : sgframework/langchain/document/info.py
# @version : 1.00.00
# Copyright (c) 1999-2025 KSFAMS Co., Ltd. All Rights Reserved.

from langchain_core.documents import Document

from sgframework.utils.dict import remove_ascii_from_dict


def show_metadata(docs: list[Document]):
    """
    [docs] 의 메타데이터 확인
    :param docs:
    :return:
    """
    if docs:
        print(f"\n[docs length]\n{len(docs)}")

        metadata = remove_ascii_from_dict(docs[0].metadata)
        print("\n[metadata]")
        print(list(metadata.keys()))
        print(f"\n[{metadata['source']}]")
        max_key_length = max(len(k) for k in metadata.keys())
        for k, v in metadata.items():
            print(f"{k:<{max_key_length}} : {v}")
    else:
        print('Document list is empty')
