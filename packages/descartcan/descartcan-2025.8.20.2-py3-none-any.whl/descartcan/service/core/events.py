# -*- coding:utf-8 -*-
"""
# Time       ：2023/12/8 18:23
# Author     ：Maxwell
# version    ：python 3.9
# Description：
"""

from typing import Callable
from fastapi import FastAPI
from descartcan.service.database.mysql import register_mysql
from descartcan.service.database.milvus import AsyncMilvusClient
from descartcan.config import config

import redis
from qdrant_client import AsyncQdrantClient
from descartcan.service.mq.nats.nats_client import NATSClient
from descartcan.service.mq.kafka.producer import KafkaProducer


def startup(app: FastAPI) -> Callable:
    async def app_start() -> None:
        await register_mysql(app)

        if len(config.NATS_SERVER_LIST) > 0:
            app.state.nats_client = NATSClient(config.NATS_SERVER_LIST, config.NATS_NAME)

        if config.KAFKA_SERVER:
            app.state.kafka_producer = KafkaProducer(config.KAFKA_SERVER)

        if config.QDRANT_HOST:
            app.state.qdrant_client = AsyncQdrantClient(
                port=config.QDRANT_HTTP_PORT,
                grpc_port=config.QDRANT_GRPC_PORT,
                api_key=config.QDRANT_API_KEY,
                host=config.QDRANT_HOST
            )

        if config.REDIS_HOST and config.REDIS_PORT:
            sys_cache_pool = redis.asyncio.ConnectionPool.from_url(
                f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}",
                db=config.REDIS_DB,
                encoding="utf-8",
                decode_responses=True,
            )
            app.state.redis_client = redis.asyncio.Redis(connection_pool=sys_cache_pool)

        milvus_client = AsyncMilvusClient.get_milvus_client()
        if milvus_client:
            app.state.milvus_client = milvus_client

    return app_start


def stopping(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        if app.state.redis_client:
            await app.state.redis_client.close()
    return stop_app
