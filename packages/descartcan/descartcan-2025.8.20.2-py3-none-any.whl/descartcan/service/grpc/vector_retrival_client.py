# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/28 23:32
# Author     ：Maxwell
# Description：
"""
import grpc
from dataclasses import dataclass

from descartcan.service.generated import vector_retrival_pb2 as pb2
from descartcan.service.generated import vector_generation_pb2_grpc as pb2_grpc


@dataclass
class VectorRetrivalData:
    key: str
    data_type: str
    content: list[str]


@dataclass
class VectorRetrivalResp:
    embeddings: list[VectorRetrivalData]


class TextRetGrpcClient:

    def __init__(self, host="localhost:50051"):
        self.host = host
        self.channel = None
        self.stub = None

    async def connect(self):
        if not self.channel:
            self.channel = grpc.aio.insecure_channel(self.host)
            self.stub = pb2_grpc.VectorGenerationServiceStub(self.channel)

    async def close(self):
        if self.channel:
            await self.channel.close()
            self.channel = None
            self.stub = None

    async def vector_generation(self, model_name: str, texts: list[str]) -> VectorRetrivalResp | None:
        """获取用户信息"""
        await self.connect()
        try:
            request = pb2.VectorRetrievalRequest(model=model_name, texts=texts)
            response = await self.stub.VectorGeneration(request)

            if response.id:
                return VectorRetrivalResp(
                    embeddings=response.data
                )
            return None
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            return None