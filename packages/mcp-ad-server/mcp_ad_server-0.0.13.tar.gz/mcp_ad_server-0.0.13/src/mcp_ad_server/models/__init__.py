"""数据模型

包含Pydantic数据模型、MCP协议模型、API请求响应模型等。
"""

from .api_models import (
    AdDataRecord,
    DataConverter,
    GetAdCountListRequest,
    GetAdCountListResponse,
    GetMaterialCountListRequest,
    GetMaterialCountListResponse,
    MaterialDataRecord,
)
from .response import (
    ErrorCodes,
    ErrorInfo,
    ErrorMessages,
    ResponseMetadata,
    ToolPayload,
    ToolResponse,
)

__all__ = [
    # MCP响应模型
    "ErrorInfo",
    "ResponseMetadata",
    "ErrorCodes",
    "ErrorMessages",
    "ToolPayload",
    "ToolResponse",
    # API模型
    "GetAdCountListRequest",
    "GetAdCountListResponse",
    "GetMaterialCountListRequest",
    "GetMaterialCountListResponse",
    "AdDataRecord",
    "MaterialDataRecord",
    "DataConverter",
]
