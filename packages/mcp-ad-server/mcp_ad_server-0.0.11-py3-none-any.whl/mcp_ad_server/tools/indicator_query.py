"""
游戏指标查询工具
"""

import logging

from ..models import ErrorCodes, ToolResponse

logger = logging.getLogger(__name__)


class GameIndicatorQueryTool:
    """游戏指标查询工具类"""

    def __init__(self, indicator_manager, config):
        """初始化游戏指标查询工具"""
        self.indicator_manager = indicator_manager
        self.config = config
        self.logger = logger

    def register(self, mcp_server):
        """注册MCP工具"""

        @mcp_server.tool("get_available_indicators")
        async def get_available_indicators(app: str, query_type: str = "ad_query"):
            """
            获取指定游戏的可用指标列表

            Args:
                app: 游戏名称，可选值：正统三国、银河战舰、开心十三张、哈局成语大师、我的仙门、一起斗消乐、大头大菠萝、大头十三水、大头斗地主
                query_type: 查询类型，可选值：ad_query(广告数据查询)、material_query(素材数据查询)，默认ad_query

            Returns:
                指定游戏和查询类型的可用指标列表
            """
            try:
                # 验证app（支持中文游戏名和数字ID）
                supported_apps = list(self.config.APP_MAPPING.keys())
                supported_ids = list(self.config.APP_MAPPING.values())
                if app not in supported_apps and app not in supported_ids:
                    return ToolResponse.error_response(
                        code=ErrorCodes.INVALID_PARAMETER,
                        message=f"不支持的游戏: {app}，支持的游戏: {supported_apps}",
                    )

                # 验证query_type
                if query_type not in ["ad_query", "material_query"]:
                    return ToolResponse.error_response(
                        code=ErrorCodes.INVALID_PARAMETER,
                        message=f"不支持的查询类型: {query_type}，支持的类型: ['ad_query', 'material_query']",
                    )

                # 获取可用指标（包含基于app的条件性指标）
                available_indicators = self.indicator_manager.get_available_indicators(
                    app, query_type
                )

                # 获取游戏对应的ID和类型
                app_id = self.config.APP_MAPPING.get(app) or (
                    app if app in self.config.APP_MAPPING.values() else None
                )
                app_type = self.config.get_type_by_app(app)

                return ToolResponse.success_response(
                    data={
                        "app": app,
                        "app_id": app_id,
                        "app_type": app_type,
                        "query_type": query_type,
                        "available_indicators": available_indicators,
                        "indicator_count": len(available_indicators),
                    },
                    record_count=len(available_indicators),
                )

            except Exception as e:
                self.logger.error(f"获取游戏可用指标失败: {e}")
                return ToolResponse.error_response(
                    code=ErrorCodes.INTERNAL_ERROR,
                    message=f"获取游戏可用指标失败: {str(e)}",
                )

        @mcp_server.tool("validate_indicators")
        async def validate_indicators(
            indicators: list[str], app: str, query_type: str = "ad_query"
        ):
            """
            验证指定游戏的指标列表

            Args:
                indicators: 要验证的指标列表
                app: 游戏名称，可选值：正统三国、银河战舰、开心十三张、哈局成语大师、我的仙门、一起斗消乐、大头大菠萝、大头十三水、大头斗地主
                query_type: 查询类型，可选值：ad_query(广告数据查询)、material_query(素材数据查询)，默认ad_query

            Returns:
                验证结果，包含有效指标和无效指标列表
            """
            try:
                # 验证app（支持中文游戏名和数字ID）
                supported_apps = list(self.config.APP_MAPPING.keys())
                supported_ids = list(self.config.APP_MAPPING.values())
                if app not in supported_apps and app not in supported_ids:
                    return ToolResponse.error_response(
                        code=ErrorCodes.INVALID_PARAMETER,
                        message=f"不支持的游戏: {app}，支持的游戏: {supported_apps}",
                    )

                # 验证query_type
                if query_type not in ["ad_query", "material_query"]:
                    return ToolResponse.error_response(
                        code=ErrorCodes.INVALID_PARAMETER,
                        message=f"不支持的查询类型: {query_type}，支持的类型: ['ad_query', 'material_query']",
                    )

                # 使用统一的验证方法
                (
                    valid_indicators,
                    invalid_indicators,
                ) = self.indicator_manager.validate_indicators(
                    indicators, app, query_type
                )

                # 获取游戏对应的ID和类型
                app_id = self.config.APP_MAPPING.get(app) or (
                    app if app in self.config.APP_MAPPING.values() else None
                )
                app_type = self.config.get_type_by_app(app)

                return ToolResponse.success_response(
                    data={
                        "app": app,
                        "app_id": app_id,
                        "app_type": app_type,
                        "query_type": query_type,
                        "valid_indicators": valid_indicators,
                        "invalid_indicators": invalid_indicators,
                        "total_indicators": len(indicators),
                        "valid_count": len(valid_indicators),
                        "invalid_count": len(invalid_indicators),
                    },
                    record_count=len(indicators),
                )

            except Exception as e:
                self.logger.error(f"验证游戏指标失败: {e}")
                return ToolResponse.error_response(
                    code=ErrorCodes.INTERNAL_ERROR,
                    message=f"验证游戏指标失败: {str(e)}",
                )

        # TODO: 场景推荐功能暂时注释，等待业务场景映射完善
        # @mcp_server.tool("recommend_indicators")
        # async def recommend_indicators(
        #     scenario: str, app: str, query_type: str = "ad_query"
        # ):
        #     """
        #     基于游戏和业务场景推荐指标
        #
        #     Args:
        #         scenario: 业务场景，可选值：投放启动、效果监控、短期评估、深度分析、数据对账、风险预警、财务核算
        #         app: 游戏名称，可选值：正统三国、银河战舰、开心十三张、哈局成语大师、我的仙门、一起斗消乐、大头大菠萝、大头十三水、大头斗地主
        #         query_type: 查询类型，可选值：ad_query(广告数据查询)、material_query(素材数据查询)，默认ad_query
        #
        #     Returns:
        #         基于游戏和场景的推荐指标列表
        #     """
