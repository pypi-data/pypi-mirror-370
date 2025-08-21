# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/7/9 16:10
# Author     ：Maxwell
# Description：
"""
from pydantic import BaseModel
from datetime import datetime


class BaseResp(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    def _format_price(self, value: float) -> str:
        """格式化价格显示（带两位小数）"""
        if value:
            return f"{value:.2f} 元"
        return ""

    def _format_percentage(self, value: float) -> str:
        """格式化百分比显示（带百分号）"""
        if value:
            return f"{value:.2%}"
        return ""

    def _format_volume(self, value: int) -> str:
        """格式化成交量显示（带千位分隔符）"""
        if value:
            return f"{value:,} 股"
        return ""

    def _format_amount(self, value: float) -> str:
        """格式化成交额显示（带千位分隔符）"""
        if value:
            return f"{value:,} 元"
        return ""

    def _format_time(self, timestamp: int) -> str:
        """将时间戳转换为可读时间"""
        if timestamp:
            return datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
        return ""