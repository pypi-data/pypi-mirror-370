"""
MCP工具响应模型 - 统一的响应格式（Pydantic 版本）
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


class ErrorInfo(BaseModel):
    """错误信息结构"""

    code: str
    message: str
    details: str | None = None
    suggestions: list[str] = Field(default_factory=list)


class ResponseMetadata(BaseModel):
    """响应元数据"""

    query_time: datetime
    record_count: int = 0
    execution_time_ms: float | None = None
    api_endpoint: str | None = None
    date_range: str | None = None
    indicators_count: int | None = None


class ErrorCodes:
    """错误代码常量"""

    # 成功代码
    SUCCESS = "SUCCESS"

    # 参数验证错误 (4xx类)
    INVALID_PARAMETER = "INVALID_PARAMETER"
    MISSING_REQUIRED_PARAMETER = "MISSING_REQUIRED_PARAMETER"
    INVALID_TIME_RANGE = "INVALID_TIME_RANGE"
    INVALID_APPID = "INVALID_APPID"
    INVALID_MEDIA = "INVALID_MEDIA"
    INVALID_INDICATORS = "INVALID_INDICATORS"
    INVALID_GROUP_KEY = "INVALID_GROUP_KEY"

    # API调用错误 (5xx类)
    API_REQUEST_FAILED = "API_REQUEST_FAILED"
    API_TIMEOUT = "API_TIMEOUT"
    API_AUTHENTICATION_FAILED = "API_AUTHENTICATION_FAILED"
    API_RESPONSE_ERROR = "API_RESPONSE_ERROR"

    # 业务逻辑错误
    NO_DATA_FOUND = "NO_DATA_FOUND"
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # 系统错误
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class ErrorMessages:
    """错误消息模板"""

    @staticmethod
    def invalid_parameter(
        param_name: str, value: str, valid_options: list[str] | None = None
    ) -> tuple[str, list[str]]:
        """参数值无效"""
        message = f"参数 '{param_name}' 的值 '{value}' 无效"
        suggestions = [f"请检查参数 '{param_name}' 的值是否正确"]

        if valid_options:
            suggestions.append(f"有效选项包括: {', '.join(map(str, valid_options))}")

        return message, suggestions

    @staticmethod
    def missing_required_parameter(param_name: str) -> tuple[str, list[str]]:
        """缺少必需参数"""
        message = f"缺少必需参数: {param_name}"
        suggestions = [f"请提供参数 '{param_name}'"]
        return message, suggestions

    @staticmethod
    def date_range_error(details: str) -> tuple[str, list[str]]:
        """日期范围错误"""
        message = f"日期范围参数错误: {details}"
        suggestions = [
            "请确保开始时间不大于结束时间",
            "请使用 YYYY-MM-DD 格式",
        ]
        return message, suggestions

    @staticmethod
    def api_request_failed(api_error: str) -> tuple[str, list[str]]:
        """API请求失败"""
        message = "数据查询失败，请稍后重试"
        suggestions = [
            "请检查网络连接",
            "请确认API服务可用",
            "如果问题持续，请联系管理员",
        ]
        return message, suggestions

    @staticmethod
    def no_data_found() -> tuple[str, list[str]]:
        """无数据"""
        message = "查询条件下没有找到相关数据"
        suggestions = [
            "请尝试调整查询条件",
            "请确认选择的时间范围内有数据",
            "请检查筛选条件是否过于严格",
        ]
        return message, suggestions


# ========== 工具层通用响应模型 ==========
T = TypeVar("T")


class ToolPayload(BaseModel):
    """工具层数据载荷

    - columns: 列名列表（已做中文映射）
    - rows: 二维数组格式的数据行，对应columns顺序
    - total: 当前返回的数据条数
    - summary: 汇总数据（从后端总计行提取，已做中文映射）
    """

    columns: list[str] | None = None
    rows: list[list[Any]] | None = None
    total: int | None = None
    summary: dict[str, Any] | None = None


class ToolResponse(BaseModel, Generic[T]):
    """工具层统一响应"""

    success: bool
    data: T | None = None
    error: ErrorInfo | None = None
    metadata: ResponseMetadata | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典"""
        return self.model_dump()

    @classmethod
    def success_response(
        cls,
        data: T,
        record_count: int = 0,
        execution_time_ms: float | None = None,
        api_endpoint: str | None = None,
        date_range: str | None = None,
        indicators_count: int | None = None,
    ) -> "ToolResponse[T]":
        return cls(
            success=True,
            data=data,
            metadata=ResponseMetadata(
                query_time=datetime.now(),
                record_count=record_count,
                execution_time_ms=execution_time_ms,
                api_endpoint=api_endpoint,
                date_range=date_range,
                indicators_count=indicators_count,
            ),
        )

    @classmethod
    def error_response(
        cls,
        code: str,
        message: str,
        details: str | None = None,
        suggestions: list[str] | None = None,
        execution_time_ms: float | None = None,
        api_endpoint: str | None = None,
        record_count: int = 0,
        date_range: str | None = None,
        indicators_count: int | None = None,
    ) -> "ToolResponse[T]":
        return cls(
            success=False,
            error=ErrorInfo(
                code=code,
                message=message,
                details=details,
                suggestions=suggestions or [],
            ),
            metadata=ResponseMetadata(
                query_time=datetime.now(),
                record_count=record_count,
                execution_time_ms=execution_time_ms,
                api_endpoint=api_endpoint,
                date_range=date_range,
                indicators_count=indicators_count,
            ),
        )
