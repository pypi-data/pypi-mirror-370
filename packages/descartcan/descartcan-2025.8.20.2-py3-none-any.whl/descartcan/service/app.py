# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/21 20:02
# Author     ：Maxwell
# Description：
"""
import uvloop
import platform
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from descartcan.service.core import events
from descartcan.config import config
from descartcan.utils.log import logger
from descartcan.service.exception import handler, exception
from descartcan.service.middleware.logging import LoggingMiddleware
from descartcan.service.middleware.request_id import RequestIDMiddleware
from descartcan.service.api import api_router

from tortoise.exceptions import (
    OperationalError,
    DoesNotExist,
    IntegrityError,
    ValidationError,
)

if platform.system() != "Windows":
    import uvloop
    uvloop.install()
    logger.info("uvloop installed")
else:
    logger.info("Running on Windows, uvloop not available")


application = FastAPI(
    debug=config.APP_DEBUG,
    title=config.APP_NAME,
    docs_url=config.APP_DOCS,
    redoc_url=config.APP_RE_DOCS,
    description=config.APP_DESCRIPTION,
)

application.add_event_handler("startup", events.startup(application))
application.add_event_handler("shutdown", events.stopping(application))

application.add_exception_handler(exception.AppException, handler.handle_app_exception)
application.add_exception_handler(ValidationError, handler.pydantic_validation_handler)
application.add_exception_handler(HTTPException, handler.http_exception_handler)
application.add_exception_handler(
    RequestValidationError, handler.validation_exception_handler
)
application.add_exception_handler(DoesNotExist, handler.mysql_does_not_exist_handler)
application.add_exception_handler(IntegrityError, handler.mysql_integrity_error_handler)
application.add_exception_handler(
    ValidationError, handler.mysql_validation_error_handler
)
application.add_exception_handler(
    OperationalError, handler.mysql_operational_error_handler
)
application.add_exception_handler(ValidationError, handler.pydantic_validation_handler)

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)
application.add_middleware(GZipMiddleware, minimum_size=1000)
application.add_middleware(LoggingMiddleware)
application.add_middleware(RequestIDMiddleware)
# application.add_middleware(HTTPSRedirectMiddleware)
# application.add_middleware(TrustedHostMiddleware)
application.include_router(api_router, include_in_schema=False)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(application, host=config.APP_HOST, port=int(config.APP_PORT))
