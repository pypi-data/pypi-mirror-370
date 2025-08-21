# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/4/11 18:51
# Author     ：Maxwell
# Description：
"""


class ClientInfoExtractor:

    @staticmethod
    def client_ip(request) -> str:
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.headers.get("X-Real-IP", request.client.host)
        return client_ip or "unknown"

    @staticmethod
    def user_agent(request) -> str:
        return request.headers.get("User-Agent", "Unknown")

    @staticmethod
    def time_zone(request) -> str:
        return request.headers.get("TimeZone", "")

    @staticmethod
    def info(request) -> dict:
        return {
            "ip": ClientInfoExtractor.client_ip(request),
            "timezone": ClientInfoExtractor.time_zone(request),
            "useragent": ClientInfoExtractor.user_agent(request),
        }
