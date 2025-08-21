# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/22 12:10
# Author     ：Maxwell
# Description：
"""
import time
import asyncio
import functools
from typing import Callable, TypeVar, Any, Optional, Union, Dict, List, Tuple
from descartcan.utils.log import logger
from inspect import iscoroutinefunction

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Exception, ...] = (Exception,),
    logger_name: Optional[str] = None,
) -> Callable[[F], F]:
    """
    重试装饰器 - 在发生特定异常时自动重试函数

    参数:
        max_attempts: 最大尝试次数
        delay_seconds: 初始延迟时间(秒)
        backoff_factor: 退避因子(每次重试后延迟时间的乘数)
        exceptions: 触发重试的异常类型
        logger_name: 自定义日志记录器名称

    示例:
        @retry(max_attempts=5, exceptions=(ConnectionError, TimeoutError))
        async def connect_to_service():
            # 连接服务的代码
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay_seconds

            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts. "
                            f"Last error: {str(e)}"
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} for {func.__name__} failed: {str(e)}. "
                        f"Retrying in {current_delay:.2f}s"
                    )

                    await asyncio.sleep(current_delay)
                    attempt += 1
                    current_delay *= backoff_factor

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay_seconds

            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts. "
                            f"Last error: {str(e)}"
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} for {func.__name__} failed: {str(e)}. "
                        f"Retrying in {current_delay:.2f}s"
                    )

                    time.sleep(current_delay)
                    attempt += 1
                    current_delay *= backoff_factor

        if iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
