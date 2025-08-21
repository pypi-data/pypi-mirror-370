# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/9/29 08:01
# Author     ：Maxwell
# Description：
"""
import json
import aiohttp
from descartcan.utils.log import logger


class RobotManager(object):

    @classmethod
    async def publish_message(cls, url, message):
        try:
            headers = {"Content-Type": "application/json"}
            json_data = {"msg_type": "text", "content": {"text": message}}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, headers=headers, data=json.dumps(json_data)
                ) as response:
                    if response.status == 200:
                        logger.info("RobotManager publish_message sent successfully")
                    else:
                        logger.info(
                            f"RobotManager publish_message. Status code: {response.status}"
                        )
                        response_text = await response.text()
                        logger.info(f"RobotManager publish_message: {response_text}")
        except Exception as e:
            logger.info(f"RobotManager error: {e}")
