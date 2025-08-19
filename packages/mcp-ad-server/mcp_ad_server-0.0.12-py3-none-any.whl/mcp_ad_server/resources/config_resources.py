"""
配置资源
"""

import logging

logger = logging.getLogger(__name__)

from typing import Any

from ..models import ToolResponse


class ConfigResources:
    """配置资源处理类"""

    def __init__(self, config):
        self.config = config

    def register(self, mcp):
        """注册资源到MCP服务器"""

        @mcp.resource("mcp://config/media")
        async def get_media() -> dict[str, Any]:
            """获取支持的媒体渠道列表"""
            return await self._get_media()

        @mcp.resource("mcp://config/group_keys")
        async def get_group_keys() -> dict[str, Any]:
            """获取支持的分组维度"""
            return await self._get_group_keys()

        @mcp.resource("mcp://config/media_buyers")
        async def get_media_buyers() -> dict[str, Any]:
            """获取支持的投手列表"""
            return await self._get_media_buyers()

        @mcp.resource("mcp://config/ad_statuses")
        async def get_ad_statuses() -> dict[str, Any]:
            """获取支持的广告状态列表"""
            return await self._get_ad_statuses()

    async def _get_media(self) -> dict[str, Any]:
        """获取媒体渠道列表"""
        # 现在SUPPORTED_MEDIA已经是中文值，直接使用
        supported_media = list(self.config.SUPPORTED_MEDIA)

        # 提供中文名称和对应的API代码
        data = {
            "media": [
                {
                    "display_name": media_name,  # 用户应该使用的中文名称
                    "api_code": self.config.MEDIA_MAPPING.get(
                        media_name, media_name
                    ),  # 对应的API代码
                    "description": f"查询时使用参数值: '{media_name}'",
                }
                for media_name in supported_media
            ]
        }

        return ToolResponse.success_response(
            data=data,
            record_count=len(supported_media),
            api_endpoint="mcp://config/media",
        ).to_dict()

    async def _get_group_keys(self) -> dict[str, Any]:
        """获取分组维度"""
        supported_group_keys = self.config.SUPPORTED_GROUP_KEYS
        items = [
            {"key": key, "name": desc} for key, desc in supported_group_keys.items()
        ]

        return ToolResponse.success_response(
            data={"group_keys": items},
            record_count=len(items),
        ).to_dict()
