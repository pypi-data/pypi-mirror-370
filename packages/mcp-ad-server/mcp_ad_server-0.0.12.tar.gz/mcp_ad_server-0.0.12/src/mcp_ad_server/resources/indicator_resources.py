"""
指标相关资源
"""

import logging

logger = logging.getLogger(__name__)

from typing import Any

from ..models import ToolResponse


class IndicatorResources:
    """指标相关资源处理类"""

    def __init__(self, indicator_manager, config):
        self.indicator_manager = indicator_manager
        self.config = config

    def register(self, mcp):
        """注册资源到MCP服务器"""

        @mcp.resource("mcp://indicators/{indicator_name}")
        async def get_indicator_definition(indicator_name: str) -> dict[str, Any]:
            """获取指标定义和业务含义"""
            return await self._get_indicator_definition(indicator_name)

        @mcp.resource("mcp://groups/{group_id}")
        async def get_indicator_group(group_id: str) -> dict[str, Any]:
            """获取指标组定义和包含的指标列表"""
            return await self._get_indicator_group(group_id)

        @mcp.resource("mcp://config/groups")
        async def list_indicator_groups() -> dict[str, Any]:
            """获取所有指标组概览"""
            return await self._list_indicator_groups()

    async def _get_indicator_definition(self, indicator_name: str) -> dict[str, Any]:
        """获取指标定义和支持的游戏类型"""
        # 使用indicator_manager的公共方法获取支持的上下文
        supported_contexts = self.indicator_manager.get_indicator_contexts(
            indicator_name
        )

        if not supported_contexts:
            return ToolResponse.error_response(
                code="NOT_FOUND",
                message=f"指标 '{indicator_name}' 未找到",
            ).to_dict()

        return ToolResponse.success_response(
            data={
                "name": indicator_name,
                "supported_contexts": supported_contexts,
                "total_contexts": len(supported_contexts),
                "description": (
                    f"指标 '{indicator_name}' 在 "
                    f"{len(supported_contexts)} 个查询上下文中可用"
                ),
            }
        ).to_dict()

    async def _get_indicator_group(self, group_id: str) -> dict[str, Any]:
        """获取指标组信息"""
        group = self.indicator_manager.get_group(group_id)
        if not group:
            return ToolResponse.error_response(
                code="NOT_FOUND",
                message=f"指标分组 '{group_id}' 未找到",
            ).to_dict()
        indicators = group.get("indicators", [])
        return ToolResponse.success_response(
            data={
                "group_id": group_id,
                "name": group.get("name", ""),
                "purpose": group.get("purpose", ""),
                "description": group.get("description", ""),
                "indicators": indicators,
                "indicator_count": len(indicators),
            },
            record_count=len(indicators),
        ).to_dict()

    async def _list_indicator_groups(self) -> dict[str, Any]:
        """获取所有指标组概览"""
        groups = self.indicator_manager.get_all_groups()
        items: list[dict[str, Any]] = []
        for gid, g in groups.items():
            items.append(
                {
                    "group_id": gid,
                    "name": g.get("name", ""),
                    "indicator_count": len(g.get("indicators", [])),
                }
            )

        scenario_mapping = self.config.SCENARIO_MAPPING
        return ToolResponse.success_response(
            data={
                "groups": items,
                "total_groups": len(items),
                "scenario_mapping": scenario_mapping,
            },
            record_count=len(items),
        ).to_dict()
