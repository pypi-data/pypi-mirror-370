# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/1/12 10:27
# Author     ：Maxwell
# Description：
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import traceback
from descartcan.utils.log import logger
from descartcan.utils.http.info import ClientInfoExtractor


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.monotonic()
        client_ip: Optional[str] = None
        path: Optional[str] = None

        try:
            client_ip = ClientInfoExtractor.client_ip(request=request)
            path = request.url.path[:200]
            response = await call_next(request)
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            logger.info(f"Req: ip={client_ip}, elapsed_ms={elapsed_ms}, {path}, {response.status_code}")
            return response
        except Exception as e:
            logger.error(
                f"Global error: ip={client_ip}, path={path}, traceback={traceback.format_exc()}"
            )
            return Response(content="Server error.", status_code=500)
