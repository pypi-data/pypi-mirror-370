"""
字段映射资源
"""

import logging

logger = logging.getLogger(__name__)

from typing import Any

from ..models import ToolResponse


class MappingResources:
    """字段映射资源处理类"""

    def __init__(self, propmap_manager):
        self.propmap_manager = propmap_manager

    def register(self, mcp):
        """注册资源到MCP服务器"""

        @mcp.resource("mcp://propmap/{api_name}")
        async def get_field_mapping(api_name: str) -> dict[str, Any]:
            """获取API字段的显示名称与字段名映射关系（结构化）"""
            return await self._get_field_mapping(api_name)

    async def _get_field_mapping(self, api_name: str) -> dict[str, Any]:
        """获取字段映射（结构化）"""
        mappings = self.propmap_manager.get_all_mappings(api_name)
        if not mappings:
            return ToolResponse.error_response(
                code="NOT_FOUND",
                message=f"API '{api_name}' 的字段映射未找到",
            ).to_dict()

        items = [{"display": cn, "field": en} for cn, en in mappings.items()]
        return ToolResponse.success_response(
            data={
                "api": api_name,
                "mappings": items,
                "total_fields": len(items),
            },
            record_count=len(items),
        ).to_dict()
