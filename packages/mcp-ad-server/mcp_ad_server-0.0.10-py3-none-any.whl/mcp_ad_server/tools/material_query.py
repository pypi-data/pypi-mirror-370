"""
素材查询工具

从main.py提取的query_material_data工具实现。
"""

import logging
from typing import Any

from ..models import ErrorCodes, ErrorMessages, ToolPayload, ToolResponse

logger = logging.getLogger(__name__)


class MaterialQueryTool:
    """素材查询工具类"""

    def __init__(self, api_client, indicator_manager, config):
        self.api_client = api_client
        self.indicator_manager = indicator_manager
        self.config = config

    def register(self, mcp):
        """注册工具到MCP服务器"""

        @mcp.tool()
        async def query_material_data(
            start_date: str,
            end_date: str,
            indicators: list[str],
            app: str = "正统三国",
            group_key: str = "",
            is_low_quality: int = -1,
            is_inefficient: int = -1,
            is_deep: bool = False,
            is_old_table: bool = False,
            # 媒体和投手参数
            media: str | list[str] | None = None,
            media_buyers: str | list[str] | None = None,
            # 制作和创意人员参数
            producers: str | list[str] | None = None,
            creative_users: str | list[str] | None = None,
            # 账户参数
            cids: str | list[str] | None = None,
            # 素材相关参数 (originality_xxx)
            originality_ids: str | list[str] | None = None,
            originality_names: str | list[str] | None = None,
            originality_types: str | list[str] | None = None,
            # 广告组和创意参数
            adgroup_ids: str | list[str] | None = None,
            creative_ids: str | list[str] | None = None,
            component_ids: str | list[str] | None = None,
        ) -> dict[str, Any]:
            """
            查询素材效果数据

            ⚠️  重要提示：不同游戏支持的指标不同，调用前请先使用 get_available_indicators 或 validate_indicators 工具检查指定游戏的可用指标，避免查询失败。

            Args:
                # 基础参数
                start_date: 查询范围开始时间，格式YYYY-MM-DD
                end_date: 查询范围结束时间，格式YYYY-MM-DD
                indicators: 指标列表。
                           ⚠️ 建议先调用 get_available_indicators 确认游戏支持的指标
                app: 游戏应用，默认正统三国，可选值：正统三国、银河战舰、开心十三张、哈局成语大师、我的仙门、一起斗消乐、大头大菠萝、大头十三水、大头斗地主
                group_key: 分组维度，默认空字符串（不分组），可选值：
                          广告ID、项目ID、创意ID、投手、self_cid、媒体
                          ⚠️ 设置后返回数据中会包含groupKey字段，自动映射为对应的中文名称
                is_low_quality: AD优/低质素材筛选，默认-1(全选)，可选值：-1(全选)、1(低质)、2(优质)
                is_inefficient: 低效素材筛选，默认-1(全选)，可选值：-1(全选)、1(是)、2(否)
                is_deep: 是否获取下探UI数据，默认False
                is_old_table: 是否使用旧报表，默认False，当media包含广点通时可选

                # 媒体和投手参数
                media: 媒体渠道筛选，可选值：全选、广点通、今日头条、百度、百度搜索、B站、知乎、UC、抖小广告量、视频号达人、星图、谷歌、自然量
                media_buyers: 投手筛选，可选值：李霖林、戴呈翔、尹欣然、施逸风、郭耀月、张鹏、宗梦男、fx2.0

                # 制作和创意人员参数
                producers: 制作人筛选，可选值：蔡睿韬、王子鹏、颜隆隆、郑显洋、李霖林、张鹏、谢雨、占雪涵、方晓聪、刘伍攀、张航、刘锦、翁国峻、刘婷婷、张泽祖、AI、戴呈翔、其他
                creative_users: 创意人筛选，可选值：蔡睿韬、陈朝晖、王子鹏、颜隆隆、郑显洋、李霖林、张鹏、谢雨、周义骅、占雪涵、方晓聪、陈朝辉、刘伍攀、张航、郭耀月、宗梦男、刘锦、翁国峻、刘婷婷、秦翎丰、张泽祖、戴呈翔、AI、其他

                # 账户参数
                cids: 广告账户CID列表筛选

                # 素材相关参数 (originality_xxx)
                originality_ids: 素材ID列表筛选
                originality_names: 素材名称列表筛选
                originality_types: 素材类型筛选，可选值：图片、视频

                # 广告组和创意参数
                adgroup_ids: 广告组ID列表筛选
                creative_ids: 创意ID列表筛选
                component_ids: 组件ID列表筛选

            Returns:
                查询结果包含数据和元数据：
                - success: 查询是否成功
                - data.columns: 列名（中文映射后）
                - data.rows: 二维数组展示数据
                - data.total: 当前返回条数
                - data.summary: 汇总数据（若后端提供总计行）
                - metadata: 查询元数据（查询时间、记录数、接口、时间范围、指标数等）

            Note:
                - 无效指标会返回错误码 INVALID_INDICATORS
            """
            return await self._query_material_data(
                start_date=start_date,
                end_date=end_date,
                indicators=indicators,
                app=app,
                group_key=group_key,
                is_low_quality=is_low_quality,
                is_inefficient=is_inefficient,
                is_deep=is_deep,
                is_old_table=is_old_table,
                media=media,
                media_buyers=media_buyers,
                producers=producers,
                creative_users=creative_users,
                cids=cids,
                originality_ids=originality_ids,
                originality_names=originality_names,
                originality_types=originality_types,
                adgroup_ids=adgroup_ids,
                creative_ids=creative_ids,
                component_ids=component_ids,
            )

    async def _query_material_data(
        self,
        start_date: str,
        end_date: str,
        indicators: list[str],
        app: str,
        group_key: str = "",
        is_low_quality: int = -1,
        is_inefficient: int = -1,
        is_deep: bool = False,
        is_old_table: bool = False,
        # 媒体和投手参数
        media: str | list[str] | None = None,
        media_buyers: str | list[str] | None = None,
        # 制作和创意人员参数
        producers: str | list[str] | None = None,
        creative_users: str | list[str] | None = None,
        # 账户参数
        cids: str | list[str] | None = None,
        # 素材相关参数 (originality_xxx)
        originality_ids: str | list[str] | None = None,
        originality_names: str | list[str] | None = None,
        originality_types: str | list[str] | None = None,
        # 广告组和创意参数
        adgroup_ids: str | list[str] | None = None,
        creative_ids: str | list[str] | None = None,
        component_ids: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """实际的查询实现"""
        try:
            # 指标验证现在在APIClient层完成

            # 调用API查询数据
            result = await self.api_client.get_material_count_list(
                app=app,
                start_date=start_date,
                end_date=end_date,
                indicators=indicators,
                group_key=group_key,
                is_low_quality=is_low_quality,
                is_inefficient=is_inefficient,
                is_deep=is_deep,
                is_old_table=is_old_table,
                media=media,
                media_buyers=media_buyers,
                producers=producers,
                creative_users=creative_users,
                cids=cids,
                originality_ids=originality_ids,
                originality_names=originality_names,
                originality_types=originality_types,
                adgroup_ids=adgroup_ids,
                creative_ids=creative_ids,
                component_ids=component_ids,
            )

            # 提取列名和行数据
            data_items = result.data.items if result.data else []
            columns, rows = self._extract_columns_and_rows(data_items)

            payload = ToolPayload(
                columns=columns,
                rows=rows,
                total=len(result.data.items) if result.data else 0,
                summary=result.data.summary if result.data else None,
            )

            return ToolResponse.success_response(
                data=payload,
                record_count=len(result.data.items) if result.data else 0,
                api_endpoint="/ad/GetMaterialCountList",
                date_range=f"{start_date} 至 {end_date}",
                indicators_count=len(columns),
            ).to_dict()

        except Exception as e:
            logger.error(f"查询素材数据失败: {e}")
            msg, suggestions = ErrorMessages.api_request_failed(str(e))
            return ToolResponse.error_response(
                code=ErrorCodes.API_REQUEST_FAILED,
                message=msg,
                details=str(e),
                suggestions=suggestions,
                api_endpoint="/ad/GetMaterialCountList",
                date_range=f"{start_date} 至 {end_date}",
                indicators_count=len(indicators),
            ).to_dict()

    def _extract_columns_and_rows(
        self, mapped_rows: list[dict]
    ) -> tuple[list[str], list[list[Any]]]:
        """从字典列表提取列名和行数据

        Args:
            mapped_rows: 已映射的字典格式数据行

        Returns:
            tuple: (columns, rows) - 列名列表和二维数组数据
        """
        if not mapped_rows:
            return [], []

        # 从第一行提取列名，保持字段顺序
        columns = list(mapped_rows[0].keys())

        # 转换为二维数组，按列名顺序提取值
        rows = []
        for row_dict in mapped_rows:
            row_values = [row_dict.get(col) for col in columns]
            rows.append(row_values)

        return columns, rows
