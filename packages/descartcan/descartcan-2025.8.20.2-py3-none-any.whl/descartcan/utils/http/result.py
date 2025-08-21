# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/7/29 14:42
# Author     ：Maxwell
# Description：
"""


class HttpResult(object):

    def __init__(
        self, succeed: bool, content: bytes, text: str = "", message: str = ""
    ):
        self.succeed = succeed
        self.content = content
        self.text = text
        self.message = message
