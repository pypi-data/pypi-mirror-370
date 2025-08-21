# !/usr/bin/env python
# -*-coding:utf-8 -*-
"""
# Time       ：2023/12/8 18:23
# Author     ：Maxwell
# Description：基础模型
"""

from tortoise import fields
from tortoise.models import Model


class TimestampMixin(Model):

    class Meta:
        abstract = True

    id = fields.IntField(pk=True, null=False)
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
