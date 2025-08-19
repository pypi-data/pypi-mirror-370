"""MCP广告服务器

提供广告投放数据的MCP服务接口。
"""

# 版本定义
__version__ = "0.0.12"
__api_client_version__ = "0.0.12"
__author__ = "AI Ad Team"

from .config import Config
from .main import AdMCPServer, main
from .managers import IndicatorManager, Manager, PropmapManager
from .resources import ConfigResources, IndicatorResources, MappingResources
from .services.api_client import BiApiClient
from .tools import AdQueryTool, MaterialQueryTool

__all__ = [
    "AdMCPServer",
    "main",
    "Config",
    "Manager",
    "IndicatorManager",
    "PropmapManager",
    "BiApiClient",
    "ConfigResources",
    "IndicatorResources",
    "MappingResources",
    "AdQueryTool",
    "MaterialQueryTool",
]
