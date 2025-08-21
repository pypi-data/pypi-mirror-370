import re
import time
import asyncio
from enum import Enum
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, List, Optional, Callable, Union
from descartcan.utils.log import logger


class LimitStrategy(str, Enum):
    IP = "ip"
    PATH = "path"
    USER = "user"
    IP_PATH = "ip_path"
    USER_PATH = "user_path"
    GLOBAL = "global"


class RateLimitExceeded(Exception):

    def __init__(self, limit: int, window: int, retry_after: int):
        self.limit = limit
        self.window = window
        self.retry_after = retry_after
        message = f"Rate limit exceeded: {limit} requests per {window} seconds. Try again in {retry_after} seconds."
        super().__init__(message)


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window: int = 60,
        strategy: Union[LimitStrategy, str] = LimitStrategy.IP,
        whitelist: List[str] = None,
        blacklist: List[str] = None,
        user_identifier: Callable[[Request], str] = None,
        custom_response: Callable[[int], JSONResponse] = None,
        path_pattern: Optional[str] = None,
        exclude_paths: List[str] = None,
        clean_interval: int = 60,
        enable_statistics: bool = False,
        redis_url: Optional[str] = None,
    ):
        """
        初始化限流中间件

        Args:
            app: FastAPI应用
            max_requests: 时间窗口内允许的最大请求数
            window: 时间窗口大小(秒)
            strategy: 限流策略，可以是LimitStrategy枚举或字符串
            whitelist: IP白名单列表，这些IP不受限流影响
            blacklist: IP黑名单列表，这些IP总是被拒绝
            user_identifier: 从请求中提取用户标识的函数
            custom_response: 自定义限流响应的函数
            path_pattern: 只对匹配此正则表达式的路径应用限流
            exclude_paths: 不进行限流的路径列表
            clean_interval: 清理过期记录的间隔(秒)
            enable_statistics: 是否启用详细统计
            redis_url: Redis连接URL，如果提供则使用Redis存储请求记录
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.strategy = (
            strategy if isinstance(strategy, LimitStrategy) else LimitStrategy(strategy)
        )
        self.whitelist = set(whitelist or [])
        self.blacklist = set(blacklist or [])
        self.user_identifier = user_identifier
        self.custom_response = custom_response
        self.path_pattern = re.compile(path_pattern) if path_pattern else None
        self.exclude_paths = set(exclude_paths or [])
        self.clean_interval = clean_interval
        self.enable_statistics = enable_statistics
        self.redis_url = redis_url

        self.requests: Dict[str, List[float]] = {}
        self.statistics = {
            "total_requests": 0,
            "limited_requests": 0,
            "last_reset": time.time(),
            "by_ip": {},
            "by_path": {},
        }

        self.redis = None
        if self.redis_url:
            self._setup_redis()
        self._setup_cleanup_task()

    def _setup_redis(self):
        try:
            import redis.asyncio as redis

            self.redis = redis.from_url(self.redis_url)
            logger.info(f"Using Redis for rate limiting: {self.redis_url}")
        except ImportError:
            logger.warning(
                "redis-py package not installed. Falling back to in-memory storage."
            )
            self.redis = None

    def _setup_cleanup_task(self):

        async def cleanup_task():
            while True:
                await asyncio.sleep(self.clean_interval)
                self._cleanup_expired_records()

                if (
                    self.enable_statistics
                    and time.time() - self.statistics["last_reset"] > 3600
                ):
                    self.statistics = {
                        "total_requests": 0,
                        "limited_requests": 0,
                        "last_reset": time.time(),
                        "by_ip": {},
                        "by_path": {},
                    }

        asyncio.create_task(cleanup_task())

    def _cleanup_expired_records(self):
        current_time = time.time()
        expired_keys = []

        for key, timestamps in self.requests.items():
            valid_timestamps = [
                ts for ts in timestamps if ts > current_time - self.window
            ]
            if not valid_timestamps:
                expired_keys.append(key)
            else:
                self.requests[key] = valid_timestamps

        for key in expired_keys:
            del self.requests[key]
        logger.debug(
            f"Cleaned up {len(expired_keys)} expired records. Current records: {len(self.requests)}"
        )

    def _get_request_key(self, request: Request) -> str:
        client_ip = request.client.host
        path = request.url.path

        if self.strategy == LimitStrategy.IP:
            return f"ip:{client_ip}"
        elif self.strategy == LimitStrategy.PATH:
            return f"path:{path}"
        elif self.strategy == LimitStrategy.USER:
            user_id = (
                self.user_identifier(request) if self.user_identifier else "anonymous"
            )
            return f"user:{user_id}"
        elif self.strategy == LimitStrategy.IP_PATH:
            return f"ip:{client_ip}:path:{path}"
        elif self.strategy == LimitStrategy.USER_PATH:
            user_id = (
                self.user_identifier(request) if self.user_identifier else "anonymous"
            )
            return f"user:{user_id}:path:{path}"
        elif self.strategy == LimitStrategy.GLOBAL:
            return "global"
        else:
            return f"ip:{client_ip}"

    async def _get_request_count(self, key: str, current_time: float) -> int:
        if self.redis:
            try:
                timestamps = await self.redis.zrangebyscore(
                    key, current_time - self.window, current_time
                )
                return len(timestamps)
            except Exception as e:
                logger.error(f"Redis error: {e}")
                if key not in self.requests:
                    self.requests[key] = []
                self.requests[key] = [
                    ts for ts in self.requests[key] if ts > current_time - self.window
                ]
                return len(self.requests[key])
        else:
            if key not in self.requests:
                self.requests[key] = []
            self.requests[key] = [
                ts for ts in self.requests[key] if ts > current_time - self.window
            ]
            return len(self.requests[key])

    async def _add_request_record(self, key: str, current_time: float) -> None:
        if self.redis:
            try:
                await self.redis.zadd(key, {str(current_time): current_time})
                await self.redis.expire(key, self.window * 2)
            except Exception as e:
                logger.error(f"Redis error: {e}")
                if key not in self.requests:
                    self.requests[key] = []
                self.requests[key].append(current_time)
        else:
            if key not in self.requests:
                self.requests[key] = []
            self.requests[key].append(current_time)

    def _update_statistics(self, request: Request, limited: bool) -> None:
        if not self.enable_statistics:
            return

        self.statistics["total_requests"] += 1
        if limited:
            self.statistics["limited_requests"] += 1

        client_ip = request.client.host
        if client_ip not in self.statistics["by_ip"]:
            self.statistics["by_ip"][client_ip] = {"total": 0, "limited": 0}
        self.statistics["by_ip"][client_ip]["total"] += 1
        if limited:
            self.statistics["by_ip"][client_ip]["limited"] += 1

        path = request.url.path
        if path not in self.statistics["by_path"]:
            self.statistics["by_path"][path] = {"total": 0, "limited": 0}
        self.statistics["by_path"][path]["total"] += 1
        if limited:
            self.statistics["by_path"][path]["limited"] += 1

    def _create_rate_limit_response(self, retry_after: int) -> JSONResponse:
        if self.custom_response:
            return self.custom_response(retry_after)

        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "detail": f"Rate limit exceeded: {self.max_requests} requests per {self.window} seconds.",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    def _should_limit_path(self, path: str) -> bool:
        if path in self.exclude_paths:
            return False

        if self.path_pattern and not self.path_pattern.match(path):
            return False

        return True

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self._should_limit_path(request.url.path):
            return await call_next(request)

        client_ip = request.client.host
        if client_ip in self.whitelist:
            return await call_next(request)
        if client_ip in self.blacklist:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Forbidden",
                    "detail": "Your IP address is blacklisted.",
                },
            )

        key = self._get_request_key(request)
        current_time = int(time.monotonic() * 1000)
        request_count = await self._get_request_count(key, current_time)

        if request_count >= self.max_requests:
            oldest_timestamp = (
                min(self.requests.get(key, [current_time]))
                if not self.redis
                else current_time - self.window
            )
            retry_after = max(1, int(self.window - (current_time - oldest_timestamp)))
            self._update_statistics(request, limited=True)
            logger.warning(
                f"Rate limit exceeded for {key}. "
                f"Count: {request_count}/{self.max_requests}, "
                f"Window: {self.window}s, "
                f"Retry-After: {retry_after}s"
            )
            return self._create_rate_limit_response(retry_after)

        await self._add_request_record(key, current_time)

        self._update_statistics(request, limited=False)
        response = await call_next(request)
        remaining = self.max_requests - request_count - 1
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window))
        return response
