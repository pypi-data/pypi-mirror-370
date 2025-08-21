from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from http import HTTPStatus


@dataclass
class ErrorProperties:
    code: int
    message: str
    message_en: str
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    details: Optional[Dict[str, Any]] = None


class AppError(Enum):

    @property
    def code(self) -> int:
        return self.value.code

    @property
    def message(self) -> str:
        return self.value.message

    @property
    def message_en(self) -> str:
        return self.value.message_en

    @property
    def status_code(self) -> int:
        return self.value.status_code

    @property
    def details(self) -> Optional[Dict[str, Any]]:
        return self.value.details

    def with_details(self, details: Dict[str, Any]) -> ErrorProperties:
        return ErrorProperties(
            code=self.code,
            message=self.message,
            message_en=self.message_en,
            status_code=self.status_code,
            details=details,
        )


class AppSystemError(AppError):
    UNKNOWN_ERROR = ErrorProperties(
        100000, "系统未知异常", "Unknown system error", HTTPStatus.INTERNAL_SERVER_ERROR
    )

    SYSTEM_ERROR = ErrorProperties(
        100001,
        "系统内部错误",
        "Internal server error",
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    TIMEOUT_ERROR = ErrorProperties(
        100002, "系统处理超时", "System processing timeout", HTTPStatus.GATEWAY_TIMEOUT
    )

    SERVICE_UNAVAILABLE = ErrorProperties(
        100003,
        "服务暂时不可用",
        "Service temporarily unavailable",
        HTTPStatus.SERVICE_UNAVAILABLE,
    )

    RESOURCE_EXHAUSTED = ErrorProperties(
        100004,
        "系统资源不足",
        "System resources exhausted",
        HTTPStatus.TOO_MANY_REQUESTS,
    )

    CONFIGURATION_ERROR = ErrorProperties(
        100005,
        "系统配置错误",
        "System configuration error",
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )


class RequestError(AppError):
    VALIDATION_ERROR = ErrorProperties(
        200000,
        "请求数据验证失败",
        "Request data validation failed",
        HTTPStatus.BAD_REQUEST,
    )

    INVALID_PARAMETER = ErrorProperties(
        200001, "无效的请求参数", "Invalid request parameter", HTTPStatus.BAD_REQUEST
    )

    MISSING_PARAMETER = ErrorProperties(
        200002, "缺少必要参数", "Missing required parameter", HTTPStatus.BAD_REQUEST
    )

    INVALID_FORMAT = ErrorProperties(
        200003, "请求格式错误", "Invalid request format", HTTPStatus.BAD_REQUEST
    )

    REQUEST_TOO_LARGE = ErrorProperties(
        200004,
        "请求体过大",
        "Request body too large",
        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
    )

    RATE_LIMITED = ErrorProperties(
        200005, "请求频率超限", "Request rate limited", HTTPStatus.TOO_MANY_REQUESTS
    )

    UNSUPPORTED_MEDIA_TYPE = ErrorProperties(
        200006,
        "不支持的媒体类型",
        "Unsupported media type",
        HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
    )


class DatabaseError(AppError):
    VALIDATION_ERROR = ErrorProperties(
        300000, "数据验证失败", "Data validation failed", HTTPStatus.BAD_REQUEST
    )

    INTEGRITY_ERROR = ErrorProperties(
        300001,
        "数据完整性约束冲突",
        "Data integrity constraint violation",
        HTTPStatus.CONFLICT,
    )

    RECORD_NOT_FOUND = ErrorProperties(
        300002, "记录不存在", "Record not found", HTTPStatus.NOT_FOUND
    )

    DUPLICATE_ENTRY = ErrorProperties(
        300003, "记录已存在", "Duplicate record", HTTPStatus.CONFLICT
    )

    OPERATIONAL_ERROR = ErrorProperties(
        300004,
        "数据库操作错误",
        "Database operational error",
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    CONNECTION_ERROR = ErrorProperties(
        300005,
        "数据库连接错误",
        "Database connection error",
        HTTPStatus.SERVICE_UNAVAILABLE,
    )

    TRANSACTION_ERROR = ErrorProperties(
        300006,
        "事务处理错误",
        "Transaction processing error",
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    QUERY_TIMEOUT = ErrorProperties(
        300007, "查询超时", "Query timeout", HTTPStatus.GATEWAY_TIMEOUT
    )


class BusinessError(AppError):

    INVALID_OPERATION = ErrorProperties(
        400000, "无效的操作", "Invalid operation", HTTPStatus.BAD_REQUEST
    )

    STATE_CONFLICT = ErrorProperties(
        400001, "状态冲突", "State conflict", HTTPStatus.CONFLICT
    )

    RESOURCE_LOCKED = ErrorProperties(
        400002, "资源已锁定", "Resource locked", HTTPStatus.LOCKED
    )

    QUOTA_EXCEEDED = ErrorProperties(
        400003, "配额超限", "Quota exceeded", HTTPStatus.FORBIDDEN
    )

    PAYMENT_REQUIRED = ErrorProperties(
        400004, "需要付款", "Payment required", HTTPStatus.PAYMENT_REQUIRED
    )

    BUSINESS_RULE_VIOLATION = ErrorProperties(
        400005, "违反业务规则", "Business rule violation", HTTPStatus.BAD_REQUEST
    )


class SecurityError(AppError):
    """
    安全相关错误

    包括认证、授权、访问控制等错误
    错误代码范围：500000-599999
    """

    UNAUTHORIZED = ErrorProperties(
        500000, "未授权访问", "Unauthorized access", HTTPStatus.UNAUTHORIZED
    )

    FORBIDDEN = ErrorProperties(
        500001, "禁止访问", "Access forbidden", HTTPStatus.FORBIDDEN
    )

    INVALID_CREDENTIALS = ErrorProperties(
        500002, "无效的凭证", "Invalid credentials", HTTPStatus.UNAUTHORIZED
    )

    TOKEN_EXPIRED = ErrorProperties(
        500003, "令牌已过期", "Token expired", HTTPStatus.UNAUTHORIZED
    )

    INVALID_TOKEN = ErrorProperties(
        500004, "无效的令牌", "Invalid token", HTTPStatus.UNAUTHORIZED
    )

    PERMISSION_DENIED = ErrorProperties(
        500005, "权限不足", "Permission denied", HTTPStatus.FORBIDDEN
    )

    ACCOUNT_LOCKED = ErrorProperties(
        500006, "账户已锁定", "Account locked", HTTPStatus.FORBIDDEN
    )

    IP_RESTRICTED = ErrorProperties(
        500007, "IP地址受限", "IP address restricted", HTTPStatus.FORBIDDEN
    )


class ExternalServiceError(AppError):
    """
    外部服务错误

    包括第三方API、外部依赖服务等错误
    错误代码范围：600000-699999
    """

    SERVICE_UNAVAILABLE = ErrorProperties(
        600000, "外部服务不可用", "External service unavailable", HTTPStatus.BAD_GATEWAY
    )

    REQUEST_FAILED = ErrorProperties(
        600001,
        "外部服务请求失败",
        "External service request failed",
        HTTPStatus.BAD_GATEWAY,
    )

    RESPONSE_ERROR = ErrorProperties(
        600002,
        "外部服务响应错误",
        "External service response error",
        HTTPStatus.BAD_GATEWAY,
    )

    TIMEOUT = ErrorProperties(
        600003, "外部服务超时", "External service timeout", HTTPStatus.GATEWAY_TIMEOUT
    )

    INVALID_RESPONSE = ErrorProperties(
        600004,
        "外部服务返回无效数据",
        "Invalid data returned from external service",
        HTTPStatus.BAD_GATEWAY,
    )
