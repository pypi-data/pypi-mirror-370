# -*- coding:utf-8 -*-
"""
# Time       ：2023/12/8 18:23
# Author     ：Maxwell
# version    ：python 3.9
# Description：
"""
from descartcan.service.exception.exception import AppError
from descartcan.config.config import DEFAULT_LANGUAGE_IS_EN


def response(code, msg, data=None):
    result = {"code": code, "message": msg, "data": data}
    return result


def success(data=None, msg=""):
    return response(200, msg, data)


def failed(error: AppError):
    msg = error.message_en
    if not DEFAULT_LANGUAGE_IS_EN:
        msg = error.message
    return response(code=error.code, msg=msg)
