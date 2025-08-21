# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/21 21:51
# Author     ：Maxwell
# Description：
"""
from descartcan.service.exception.error import AppError
from descartcan.config.config import DEFAULT_LANGUAGE_IS_EN


class AppException(Exception):

    def __init__(self, error: AppError):
        self.error_code = error.code
        self.message = error.message_en
        if not DEFAULT_LANGUAGE_IS_EN:
            self.message = error.message
        super().__init__(error.message)

    def with_content(self, place_holder, content):
        if self.message:
            self.message = self.message.replace(place_holder, content)
        return self
