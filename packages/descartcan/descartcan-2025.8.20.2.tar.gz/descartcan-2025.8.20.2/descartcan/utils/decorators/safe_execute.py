# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/22 12:07
# Author     ：Maxwell
# Description：
"""
import time
import functools
from typing import Callable, TypeVar, Any, Optional, Union, Dict, List, Tuple
from inspect import iscoroutinefunction
from descartcan.utils.log import logger


T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


def safe_execute(
    func: F, default_return: Any = None, log_error: bool = True, reraise: bool = False
) -> F:
    """
    安全执行装饰器 - 捕获函数执行过程中的异常，防止程序崩溃

    参数:
        default_return: 发生异常时的默认返回值
        log_error: 是否记录错误日志
        reraise: 是否重新抛出异常

    示例:
        @safe_execute
        def my_function():
            # 可能抛出异常的代码

        @safe_execute(default_return=[], log_error=True)
        async def my_async_function():
            # 可能抛出异常的异步代码
    """
    # 处理直接使用不带参数的装饰器情况
    if callable(func) and not isinstance(func, type):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                if reraise:
                    raise
                return default_return

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                if reraise:
                    raise
                return default_return

        if iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    # 处理带参数的装饰器情况
    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {fn.__name__}: {e}", exc_info=True)
                if reraise:
                    raise
                return default_return

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {fn.__name__}: {e}", exc_info=True)
                if reraise:
                    raise
                return default_return

        if iscoroutinefunction(fn):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
