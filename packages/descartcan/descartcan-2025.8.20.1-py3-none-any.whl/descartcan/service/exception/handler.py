# -*- coding:utf-8 -*-
"""
# Time       ：2023/12/8 18:23
# Author     ：Maxwell
# version    ：python 3.9
# Description：
"""
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from tortoise.exceptions import (
    OperationalError,
    DoesNotExist,
    IntegrityError,
    ValidationError as MysqlValidationError,
)

from descartcan.service.exception.error import DatabaseError, RequestError
from descartcan.service.exception.exception import AppException
from descartcan.utils.log import logger


async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    return JSONResponse(
        status_code=exc.status_code, content=exc.detail, headers=exc.headers
    )


async def handle_app_exception(_: Request, exc: AppException) -> Response:
    return JSONResponse(
        {"code": exc.error_code, "message": exc.message, "data": {}}, status_code=200
    )


async def mysql_validation_error_handler(
    _: Request, exc: MysqlValidationError
) -> Response:
    logger.error(f"mysql_validation_error: {exc}")
    err = DatabaseError.VALIDATION_ERROR
    return JSONResponse(
        {"code": err.code, "message": err.message, "data": {}}, status_code=200
    )


async def mysql_integrity_error_handler(_: Request, exc: IntegrityError) -> Response:
    logger.error(f"mysql_integrity_error: {exc}")
    err = DatabaseError.INTEGRITY_ERROR
    return JSONResponse(
        {"code": err.code, "message": err.message, "data": {}}, status_code=200
    )


async def mysql_does_not_exist_handler(_: Request, exc: DoesNotExist) -> Response:
    logger.error(f"mysql_does_not_exist: {exc}")
    err = DatabaseError.RECORD_NOT_FOUND
    return JSONResponse(
        {"code": err.code, "message": err.message, "data": {}}, status_code=200
    )


async def mysql_operational_error_handler(
    _: Request, exc: OperationalError
) -> Response:
    logger.error(f"mysql_operational_error: {exc}")
    err = DatabaseError.OPERATIONAL_ERROR
    return JSONResponse(
        {"code": err.code, "message": err.message, "data": {}}, status_code=200
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> Response:
    logger.error(f"validation_exception: {exc}")
    error_details = []
    for error in exc.errors():
        error_details.append(
            {
                "loc": " -> ".join([str(loc) for loc in error["loc"]]),
                "msg": error["msg"],
                "type": error["type"],
            }
        )
    err = RequestError.VALIDATION_ERROR
    return JSONResponse(
        {"code": err.code, "message": error_details, "data": {}}, status_code=200
    )


async def pydantic_validation_handler(
    request: Request, exc: ValidationError
) -> Response:
    logger.error(f"pydantic_validation: {exc}")
    error_details = []
    for error in exc.errors():
        error_details.append(
            {
                "loc": " -> ".join([str(loc) for loc in error["loc"]]),
                "msg": error["msg"],
                "type": error["type"],
            }
        )
    err = RequestError.VALIDATION_ERROR
    return JSONResponse(
        {"code": err.code, "message": error_details, "data": {}}, status_code=200
    )
