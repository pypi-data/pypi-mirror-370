# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/18 14:45
# Author     ：Maxwell
# Description：
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import PlainTextResponse


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, whitelist):
        super().__init__(app)
        self.whitelist = whitelist

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        if client_ip not in self.whitelist:
            return PlainTextResponse(status_code=403, content="IP not allowed")
        return await call_next(request)
