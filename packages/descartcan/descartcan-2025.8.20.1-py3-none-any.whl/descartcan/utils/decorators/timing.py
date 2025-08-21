# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/22 12:08
# Author     ：Maxwell
# Description：
"""
import time
import functools
from contextlib import contextmanager
from typing import Callable, TypeVar, Any, Optional, Union, Dict, List, Tuple
from descartcan.utils.log import logger
from inspect import iscoroutinefunction

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


@contextmanager
def timing_context(mark):
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        logger.info(f"{mark}: {elapsed:.4f}s")

def timing(
    label: str = "执行时间",
    threshold_ms: Optional[float] = None,
    log_level: str = "info",
) -> Callable[[F], F]:
    """
    计时装饰器 - 测量函数执行时间并记录日志

    参数:
        label: 日志标签
        threshold_ms: 时间阈值(毫秒)，超过此值才记录日志
        log_level: 日志级别 (debug, info, warning, error, critical)

    示例:
        @timing("数据处理")
        def process_data():
            # 处理数据的代码

        @timing(threshold_ms=100)  # 只记录执行时间超过100ms的调用
        async def fetch_data():
            # 获取数据的异步代码
    """

    def get_logger_method(level_name: str) -> Callable:
        """获取对应日志级别的方法"""
        level_map = {
            "debug": logger.debug,
            "info": logger.info,
            "warning": logger.warning,
            "error": logger.error,
        }
        return level_map.get(level_name.lower(), logger.info)

    log_method = get_logger_method(log_level)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            elapsed_ms = elapsed_time * 1000

            if threshold_ms is None or elapsed_ms > threshold_ms:
                log_method(
                    f"{label}: {func.__name__}, {elapsed_time:.4f}s ({elapsed_ms:.2f}ms)"
                )

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            elapsed_ms = elapsed_time * 1000

            if threshold_ms is None or elapsed_ms > threshold_ms:
                log_method(
                    f"{label}: {func.__name__}, {elapsed_time:.4f}s ({elapsed_ms:.2f}ms)"
                )

            return result

        if iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
