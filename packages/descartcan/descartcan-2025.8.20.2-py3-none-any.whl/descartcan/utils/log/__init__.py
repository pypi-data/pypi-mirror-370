# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/22 12:05
# Author     ：Maxwell
# Description：
"""
import os
import sys
import socket
import atexit
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable

from loguru import logger
from descartcan.config import config as settings

# =================================================================
# 基础配置
# =================================================================

# 创建日志目录
log_dir = Path(settings.LOG_DIR if hasattr(settings, "LOG_DIR") else "./log/app")
log_dir.mkdir(parents=True, exist_ok=True)

HOSTNAME = socket.gethostname()
APP_NAME = settings.APP_NAME
ENVIRONMENT = settings.env
LOG_LEVEL = settings.LOG_LEVEL
LOG_RETENTION = settings.LOG_RETENTION
LOG_ROTATION = settings.LOG_ROTATION
ENABLE_CONSOLE_COLOR = settings.LOG_ENABLE_CONSOLE_COLOR
RECORD_CALLER_INFO = settings.LOG_RECORD_CALLER_INFO
ENABLE_JSON_LOGS = settings.LOG_ENABLE_JSON_LOGS
ENABLE_ASYNC_LOGGING = settings.LOG_ENABLE_ASYNC_LOGGING
ENABLE_CONTEXT = settings.LOG_ENABLE_CONTEXT

# =================================================================
# 日志格式配置
# =================================================================

JSON_FORMAT_PRESETS = {
    "simple": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    "detailed": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
    "debug": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {process}:{thread} | {level: <8} | {name}:{function}:{line} | {message}",
    "pro": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {extra[hostname]} | {extra[app_name]} | {level: <8} | {name}:{function} | {message}",
}

CONSOLE_FORMAT_PRESETS = {
    "simple": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    "detailed": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    "debug": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <magenta>{process}</magenta>:<magenta>{thread}</magenta> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    "pro": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {extra[hostname]} | {extra[app_name]} | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
}


LOG_FORMAT = CONSOLE_FORMAT_PRESETS.get(settings.LOG_FORMAT)
if settings.LOG_ENABLE_JSON_LOGS:
    LOG_FORMAT = JSON_FORMAT_PRESETS.get(settings.LOG_FORMAT)


# =================================================================
# 日志过滤器
# =================================================================

def log_filter(record):
    """
    日志过滤器，可以根据需要过滤掉某些日志

    例如:
    - 过滤掉特定模块的DEBUG日志
    - 过滤掉某些重复的警告
    """
    if record["name"] == "uvicorn.access" and record["level"].name == "DEBUG":
        return False

    # 示例: 过滤掉特定的重复警告
    if "Connection pool is full" in record["message"] and record["level"].name == "WARNING":
        return False

    return True


# =================================================================
# 日志配置实现
# =================================================================

# 移除默认处理器
logger.remove()

# 添加额外上下文信息
logger = logger.bind(hostname=HOSTNAME, app_name=APP_NAME, environment=ENVIRONMENT)

# 添加控制台处理器 (仅在非生产环境)
if ENVIRONMENT.lower() != "pro":
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        colorize=ENABLE_CONSOLE_COLOR,
        backtrace=True,
        diagnose=True,
        filter=log_filter,
        enqueue=ENABLE_ASYNC_LOGGING
    )


logger.add(
    f"{log_dir}/all.log",
    format=LOG_FORMAT,
    level="DEBUG",
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    compression="zip",
    filter=log_filter,
    backtrace=True,
    diagnose=True,
    enqueue=ENABLE_ASYNC_LOGGING
)

# 添加文件处理器 - 信息日志
logger.add(
    f"{log_dir}/info.log",
    format=LOG_FORMAT,
    level="INFO",
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    compression="zip",
    filter=log_filter,
    enqueue=ENABLE_ASYNC_LOGGING
)

# # 添加文件处理器 - 警告日志
# logger.add(
#     f"{log_dir}/warning.log",
#     format=LOG_FORMAT,
#     level="WARNING",
#     rotation=LOG_ROTATION,
#     retention=LOG_RETENTION,
#     compression="zip",
#     filter=log_filter,
#     enqueue=ENABLE_ASYNC_LOGGING
# )

# 添加文件处理器 - 错误日志
logger.add(
    f"{log_dir}/error.log",
    format=LOG_FORMAT,
    level="ERROR",
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    compression="zip",
    backtrace=True,
    diagnose=True,
    filter=log_filter,
    enqueue=ENABLE_ASYNC_LOGGING
)

# 添加文件处理器 - 调试日志 (仅在开发环境)
if ENVIRONMENT.lower() in ["development", "dev", "local"]:
    logger.add(
        f"{log_dir}/debug.log",
        format=LOG_FORMAT,
        level="DEBUG",
        rotation=LOG_ROTATION,
        retention=LOG_RETENTION,
        compression="zip",
        filter=log_filter,
        enqueue=ENABLE_ASYNC_LOGGING
    )

# =================================================================
# 上下文管理
# =================================================================

if ENABLE_CONTEXT:
    # 请求上下文
    class RequestContext:
        """请求上下文管理器，用于在日志中添加请求ID等信息"""

        _context = {}

        @classmethod
        def set(cls, key: str, value: Any) -> None:
            """设置上下文值"""
            cls._context[key] = value
            # 更新logger上下文
            logger.configure(extra={**logger._core.extra, **cls._context})

        @classmethod
        def get(cls, key: str, default: Any = None) -> Any:
            """获取上下文值"""
            return cls._context.get(key, default)

        @classmethod
        def clear(cls) -> None:
            """清除上下文"""
            cls._context.clear()
            # 重置logger上下文为基本值
            logger.configure(extra={
                "hostname": HOSTNAME,
                "app_name": APP_NAME,
                "environment": ENVIRONMENT
            })


    # 导出上下文管理器
    context = RequestContext()
else:
    # 如果未启用上下文，提供一个空实现
    class DummyContext:
        @staticmethod
        def set(key: str, value: Any) -> None:
            pass

        @staticmethod
        def get(key: str, default: Any = None) -> Any:
            return default

        @staticmethod
        def clear() -> None:
            pass


    context = DummyContext()


# =================================================================
# 辅助函数
# =================================================================

def setup_logger_for_module(module_name: str) -> "logger":
    """
    为特定模块创建一个预配置的logger

    用法:
        logger = setup_logger_for_module(__name__)
    """
    return logger.bind(name=module_name)


def log_function_call(func_name: str, args: tuple, kwargs: dict) -> None:
    """记录函数调用信息"""
    args_str = ", ".join([str(arg) for arg in args])
    kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    params = f"{args_str}{', ' if args_str and kwargs_str else ''}{kwargs_str}"
    logger.debug(f"调用函数: {func_name}({params})")


# =================================================================
# 退出处理
# =================================================================

@atexit.register
def cleanup():
    """应用退出时的清理工作"""
    logger.info("应用程序正在关闭，清理日志资源")


# =================================================================
# 装饰器
# =================================================================

def log_calls(level: str = "DEBUG"):
    """
    记录函数调用的装饰器

    用法:
        @log_calls()
        def my_function(arg1, arg2):
            pass
    """

    def decorator(func):
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            log_message = f"调用: {func_name}"

            # 记录参数 (可选，小心记录敏感信息)
            if level == "DEBUG":
                args_str = ", ".join([repr(arg) for arg in args])
                kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in kwargs.items()])
                params = f"{args_str}{', ' if args_str and kwargs_str else ''}{kwargs_str}"
                log_message = f"{log_message}({params})"

            getattr(logger, level.lower())(log_message)

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"异常: {func_name} - {str(e)}", exc_info=True)
                raise

        return wrapper

    return decorator


# =================================================================
# 使用示例
# =================================================================

if __name__ == "__main__":

    # 基本用法
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志")

    # 带结构化数据的日志
    logger.info("用户登录", extra={"user_id": 123, "ip": "192.168.1.1"})

    # 异常日志
    try:
        1 / 0
    except Exception as e:
        logger.exception("发生除零错误")

    # 使用上下文
    context.set("request_id", "req-123456")
    logger.info("处理请求")  # 将包含request_id
    context.clear()

    # 模块专用logger
    module_logger = setup_logger_for_module("auth.service")
    module_logger.info("验证用户")  # 将显示模块名称

    @log_calls()
    def sample_function(a, b):
        return a + b

    sample_function(1, 2)