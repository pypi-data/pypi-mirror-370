#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置模块

加载并管理应用程序配置，支持多环境配置(.env文件)。
配置项按功能分组，便于维护和扩展。

# Time       : 2024/1/17 11:38
# Author     : Maxwell
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from dotenv import load_dotenv

from descartcan.service.mq.kafka.producer import KafkaProducer

# =================================================================
# 环境配置加载
# =================================================================

load_dotenv()
env = os.getenv("ENV", "dev").lower()

env_file = Path(f"./config/.env.{env}")
if env_file.exists():
    load_dotenv(env_file, override=True)
else:
    print(f"警告: 环境配置文件 {env_file} 不存在，使用默认配置", file=sys.stderr)

# =================================================================
# 应用基础配置
# =================================================================

APP_NAME = os.getenv("APP_NAME", "DescartCan")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "DescartCan Base Service")
APP_DEBUG = env != "pro"

# API文档配置 (仅在非生产环境启用)
APP_DOCS: Optional[str] = "/doc" if APP_DEBUG else None
APP_RE_DOCS: Optional[str] = "/redoc" if APP_DEBUG else None

# 应用服务配置
APP_BASE_URI = os.getenv("APP_BASE_URI", "")
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8008"))


# =================================================================
# 认证与安全配置
# =================================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-jwt")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

OAUTH2_REDIRECT_URL = os.getenv("OAUTH2_REDIRECT_URL", "/auth/callback")


# =================================================================
# MySQL
# =================================================================

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB = os.getenv("MYSQL_DB", "")
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

MYSQL_TABLE_MODELS_PATH = os.getenv("MYSQL_TABLE_MODELS_PATH", "app.models")
MYSQL_TABLE_MODELS_CONFIG = os.getenv("MYSQL_TABLE_MODELS", "")

MYSQL_TABLE_MODELS = []
if len(MYSQL_TABLE_MODELS_CONFIG) > 0:
    path = MYSQL_TABLE_MODELS_PATH
    MYSQL_TABLE_MODELS = [f"{path}.{m}" for m in MYSQL_TABLE_MODELS_CONFIG.split(",")]

# =================================================================
# Redis
# =================================================================
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")


# =================================================================
# Milvus
# =================================================================
MILVUS_PREFIX = os.getenv("MILVUS_PREFIX", "http")
MILVUS_HOST = os.getenv("MILVUS_HOST", "")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", 19530))
MILVUS_USER = os.getenv("MILVUS_USER", "")
MILVUS_PASSWD = os.getenv("MILVUS_PASSWD", "")
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN", "")
MILVUS_DB_NAME = os.getenv("MILVUS_DB_NAME", "default")

MILVUS_MAX_IDLE_TIME = int(os.getenv("MILVUS_MAX_IDLE_TIME", 300))
MILVUS_CONNECTION_TTL = int(os.getenv("MILVUS_CONNECTION_TTL", 3600))
MILVUS_MAX_CONNECTIONS = int(os.getenv("MILVUS_MAX_CONNECTIONS", 10))
MILVUS_MIN_CONNECTIONS = int(os.getenv("MILVUS_MIN_CONNECTIONS", 300))
MILVUS_CONNECTION_TIMEOUT = int(os.getenv("MILVUS_CONNECTION_TIMEOUT", 30))
MILVUS_HEALTH_CHECK_INTERVAL = int(os.getenv("MILVUS_HEALTH_CHECK_INTERVAL", 60))

# =================================================================
# Qdrant
# =================================================================
QDRANT_HOST = os.getenv("QDRANT_HOST", None)
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
QDRANT_HTTP_PORT = int(os.getenv("QDRANT_HTTP_PORT", "6333"))
QDRANT_GRPC_PORT = int(os.getenv("QDRANT_GRPC_PORT", "6334"))
QDRANT_PREFER_GRPC = os.getenv("QDRANT_PREFER_GRPC", "true").lower() == "true"


# =================================================================
# 国际化配置
# =================================================================

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "EN")
DEFAULT_LANGUAGE_IS_EN = DEFAULT_LANGUAGE == "EN"
SUPPORTED_LANGUAGES = ["EN", "ZH"]


# =================================================================
# MQ配置
# =================================================================

KAFKA_SERVER = os.getenv("KAFKA_SERVER", None)

NATS_NAME = os.getenv("NATS_NAME", None)
NATS_SERVER = os.getenv("NATS_SERVER", None)
NATS_SERVER_LIST = []
if NATS_SERVER:
    NATS_SERVER_LIST = [m for m in NATS_SERVER.split(",")]

# =================================================================
# 日志配置
# =================================================================

# 日志基础配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "./logs")
LOG_RETENTION = os.getenv("LOG_RETENTION", "7 days")
LOG_ROTATION = os.getenv("LOG_ROTATION", "100 MB")

# 日志格式与功能配置
LOG_FORMAT = os.getenv("LOG_FORMAT", "simple")  # simple/detailed/debug/pro/json
LOG_ENABLE_CONTEXT = os.getenv("LOG_ENABLE_CONTEXT", "true").lower() == "true"
LOG_ENABLE_JSON_LOGS = os.getenv("LOG_ENABLE_JSON_LOGS", "false").lower() == "true"
LOG_RECORD_CALLER_INFO = os.getenv("LOG_RECORD_CALLER_INFO", "true").lower() == "true"
LOG_ENABLE_CONSOLE_COLOR = os.getenv("LOG_ENABLE_CONSOLE_COLOR", "true").lower() == "true"
LOG_ENABLE_ASYNC_LOGGING = os.getenv("LOG_ENABLE_ASYNC_LOGGING", "true").lower() == "true"


if env == "dev":
    LOG_ENABLE_CONSOLE_COLOR = True
    LOG_FORMAT = "detailed"

elif env == "test":
    LOG_ENABLE_CONSOLE_COLOR = True
    LOG_FORMAT = "detailed"

elif env == "pro":
    LOG_ENABLE_CONSOLE_COLOR = False
    LOG_FORMAT = "pro"
