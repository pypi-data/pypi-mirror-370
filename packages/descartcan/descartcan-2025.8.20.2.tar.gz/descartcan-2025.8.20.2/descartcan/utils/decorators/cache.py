# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/22 12:11
# Author     ：Maxwell
# Description：
"""
import time
import functools
from typing import Callable, TypeVar, Any, Optional, Union, Dict, List, Tuple
from descartcan.utils.log import logger
from inspect import iscoroutinefunction

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


def cache(
    ttl: Optional[int] = 60,  # 缓存生存时间(秒)
    max_size: int = 128,  # 最大缓存条目数
    key_func: Optional[Callable] = None,  # 自定义缓存键生成函数
) -> Callable[[F], F]:
    """
    缓存装饰器 - 缓存函数结果以提高性能

    参数:
        ttl: 缓存生存时间(秒)，None表示永不过期
        max_size: 最大缓存条目数
        key_func: 自定义缓存键生成函数

    示例:
        @cache(ttl=300)  # 缓存5分钟
        def get_user_data(user_id):
            # 获取用户数据的代码
    """
    cache_dict: Dict[str, Tuple[Any, Optional[float]]] = {}

    def make_key(*args, **kwargs) -> str:
        """生成缓存键"""
        if key_func:
            return str(key_func(*args, **kwargs))

        # 默认键生成逻辑
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return ":".join(key_parts)

    def is_expired(timestamp: Optional[float]) -> bool:
        """检查缓存是否过期"""
        if timestamp is None:  # 永不过期
            return False
        return time.time() > timestamp

    def cleanup_cache() -> None:
        """清理过期缓存"""
        if ttl is None:
            return

        expired_keys = [
            k
            for k, (_, exp_time) in cache_dict.items()
            if exp_time is not None and is_expired(exp_time)
        ]

        for k in expired_keys:
            del cache_dict[k]

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 清理过期缓存
            cleanup_cache()

            # 生成缓存键
            key = make_key(*args, **kwargs)

            # 检查缓存
            if key in cache_dict:
                value, exp_time = cache_dict[key]
                if not is_expired(exp_time):
                    return value

            # 缓存未命中，执行函数
            result = await func(*args, **kwargs)

            # 更新缓存
            if len(cache_dict) >= max_size:
                # 简单的LRU策略：删除第一个条目
                if cache_dict:
                    cache_dict.pop(next(iter(cache_dict)))

            expiration = (time.time() + ttl) if ttl is not None else None
            cache_dict[key] = (result, expiration)

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 清理过期缓存
            cleanup_cache()

            # 生成缓存键
            key = make_key(*args, **kwargs)

            # 检查缓存
            if key in cache_dict:
                value, exp_time = cache_dict[key]
                if not is_expired(exp_time):
                    return value

            # 缓存未命中，执行函数
            result = func(*args, **kwargs)

            # 更新缓存
            if len(cache_dict) >= max_size:
                # 简单的LRU策略：删除第一个条目
                if cache_dict:
                    cache_dict.pop(next(iter(cache_dict)))

            expiration = (time.time() + ttl) if ttl is not None else None
            cache_dict[key] = (result, expiration)

            return result

        # 添加清除缓存的辅助方法
        def clear_cache():
            cache_dict.clear()

        if iscoroutinefunction(func):
            async_wrapper.clear_cache = clear_cache
            return async_wrapper
        else:
            sync_wrapper.clear_cache = clear_cache
            return sync_wrapper

    return decorator
