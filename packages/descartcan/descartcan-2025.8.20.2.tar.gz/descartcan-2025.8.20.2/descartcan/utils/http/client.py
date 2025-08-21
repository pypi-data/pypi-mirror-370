# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/7/29 14:25
# Author     ：Maxwell
# Description：
"""
import aiohttp
from descartcan.utils.http.result import HttpResult


class HttpAsyncClient:

    @staticmethod
    async def post(url, headers=None, data=None, json=None, files=None) -> HttpResult:
        if data:
            form_data = aiohttp.FormData()
            for key, value in data.items():
                form_data.add_field(key, value)

            if files:
                for key, file in files.items():
                    form_data.add_field(
                        key,
                        file,
                        filename="file",
                        content_type="application/octet-stream",
                    )

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, headers=headers, data=form_data
                ) as response:
                    succeed = response.status == 200
                    content = await response.read()
                    text = await response.text()
                    message = f"{response.status}:{response.reason}"
                    return HttpResult(
                        succeed=succeed, content=content, text=text, message=message
                    )

        if json:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=json) as response:
                    succeed = response.status == 200
                    content = await response.read()
                    text = await response.text()
                    message = f"{response.status}:{response.reason}"
                    return HttpResult(
                        succeed=succeed, content=content, text=text, message=message
                    )

    @staticmethod
    async def get_content(url) -> HttpResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                succeed = response.status == 200
                content = await response.read()
                message = f"{response.status}:{response.reason}"
                return HttpResult(succeed=succeed, content=content, message=message)
