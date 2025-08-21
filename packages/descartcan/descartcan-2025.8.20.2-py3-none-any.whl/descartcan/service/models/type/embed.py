# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/21 14:08
# Author     ：Maxwell
# Description：
"""

from enum import Enum


class EmbedModelProperty(object):
    def __init__(self, model_name, dem: int, max_length: int):
        self.model_name = model_name
        self.dem = dem
        self.max_length = max_length


class EmbedModel(Enum):
    M3E = EmbedModelProperty("m3e", dem=768, max_length=512)
    BGE_M3 = EmbedModelProperty("bge_m3", dem=1024, max_length=8192)

    @classmethod
    def get_by_name(cls, name):
        if cls.M3E.value.model_name == name:
            return cls.M3E
        return cls.BGE_M3


class EmbedDataType(Enum):
    CONVERSION = "C"
    KNOWLEDGE = "K"
    DIARY = "D"
    FILE = "F"


class EmbedDataProperty(object):
    def __init__(self, collection_name_prefix: str, filed_id_name: str, data_type: EmbedDataType):
        self.collection_name_prefix = collection_name_prefix
        self.filed_id_name = filed_id_name
        self.data_type = data_type


class EmbedCollectionConfig(Enum):
    CONVERSION = EmbedDataProperty("user_conversion", "conversion_id", EmbedDataType.CONVERSION)
    KNOWLEDGE = EmbedDataProperty("user_knowledge", "knowledge_id", EmbedDataType.KNOWLEDGE)
    DIARY = EmbedDataProperty("user_diary", "diary_id", EmbedDataType.DIARY)
    FILE = EmbedDataProperty("user_file", "file_id", EmbedDataType.FILE)

    @classmethod
    def get_by_data_type(cls, data_type: EmbedDataType):
        for one in EmbedCollectionConfig:
            if data_type.name == one.name:
                return one.value
        return None


class EmbedCollection(object):

    @classmethod
    def collection_name(cls, data_type: EmbedDataType, llm: EmbedModel) -> str:
        data_property = EmbedCollectionConfig.get_by_data_type(data_type)
        return f"{data_property.collection_name_prefix}_{llm.value.model_name}"
