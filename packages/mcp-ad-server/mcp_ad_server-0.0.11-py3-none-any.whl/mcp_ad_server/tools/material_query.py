"""
素材查询工具

从main.py提取的query_material_data工具实现。
"""

import logging
from typing import Any

from ..models import ErrorCodes, ErrorMessages, ToolResponse

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
                start_date: 查询范围开始时间，格式YYYY-MM-DD
                end_date: 查询范围结束时间，格式YYYY-MM-DD
                indicators: 指标列表（⚠️ 建议先调用 get_available_indicators 确认游戏支持的指标）
                app: 游戏应用，默认正统三国，可选值：正统三国、银河战舰、开心十三张、哈局成语大师、我的仙门、一起斗消乐、大头大菠萝、大头十三水、大头斗地主
                group_key: 分组维度，默认空字符串（不分组），可选值：广告ID、项目ID、创意ID、投手、self_cid、媒体
                is_low_quality: AD优/低质素材筛选，默认-1(全选)，可选值：-1(全选)、1(低质)、2(优质)
                is_inefficient: 低效素材筛选，默认-1(全选)，可选值：-1(全选)、1(是)、2(否)
                is_deep: 是否获取下探UI数据，默认False
                is_old_table: 是否使用旧报表，默认False，当media包含广点通时可选
                media: 媒体渠道筛选，可选值：全选、广点通、今日头条、百度、百度搜索、B站、知乎、UC、抖小广告量、视频号达人、星图、谷歌、自然量
                media_buyers: 投手筛选，可选值：李霖林、戴呈翔、尹欣然、施逸风、郭耀月、张鹏、宗梦男、fx2.0
                producers: 制作人筛选，可选值：蔡睿韬、王子鹏、颜隆隆、郑显洋、李霖林、张鹏、谢雨、占雪涵、方晓聪、刘伍攀、张航、刘锦、翁国峻、刘婷婷、张泽祖、AI、戴呈翔、其他
                creative_users: 创意人筛选，可选值：蔡睿韬、陈朝晖、王子鹏、颜隆隆、郑显洋、李霖林、张鹏、谢雨、周义骅、占雪涵、方晓聪、陈朝辉、刘伍攀、张航、郭耀月、宗梦男、刘锦、翁国峻、刘婷婷、秦翎丰、张泽祖、戴呈翔、AI、其他
                cids: 广告账户CID列表筛选
                originality_ids: 素材ID列表筛选
                originality_names: 素材名称列表筛选
                originality_types: 素材类型筛选，可选值：图片、视频
                adgroup_ids: 广告组ID列表筛选
                creative_ids: 创意ID列表筛选
                component_ids: 组件ID列表筛选

            Returns:
                查询结果按素材价值分类返回，每个分类包含columns（列名）、rows（数据行）、total（数量）：
                - success: 查询是否成功
                - data.historical: 历史素材（无消耗但有转化）
                - data.active: 活跃素材（有消耗且有转化）
                - data.no_conversion: 暂无转化素材（有消耗但暂无转化）
                - data.users_only: 仅用户素材（无消耗仅活跃用户，返回[素材id, 活跃用户数]）
                - data.summary: 汇总数据（若后端提供）
                - metadata: 查询元数据（时间、记录数、接口等）

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

            # 素材数据智能分类
            if result.data and result.data.items:
                classification_result = self._classify_material_data(result.data)

                # 构建简化的分类数据字典
                classified_data = {}

                # 历史素材
                if classification_result["historical"]:
                    columns, rows = self._extract_columns_and_rows(
                        classification_result["historical"]
                    )
                    classified_data["historical"] = {
                        "columns": columns,
                        "rows": rows,
                        "total": len(classification_result["historical"]),
                    }

                # 活跃素材
                if classification_result["active"]:
                    columns, rows = self._extract_columns_and_rows(
                        classification_result["active"]
                    )
                    classified_data["active"] = {
                        "columns": columns,
                        "rows": rows,
                        "total": len(classification_result["active"]),
                    }

                # 暂无转化素材
                if classification_result["no_conversion"]:
                    columns, rows = self._extract_columns_and_rows(
                        classification_result["no_conversion"]
                    )
                    classified_data["no_conversion"] = {
                        "columns": columns,
                        "rows": rows,
                        "total": len(classification_result["no_conversion"]),
                    }

                # 仅用户素材
                if classification_result["users_only"]:
                    users_only_columns = ["素材id", "活跃用户"]
                    users_only_rows = [
                        [item["material_id"], item["active_users"]]
                        for item in classification_result["users_only"]
                    ]
                    classified_data["users_only"] = {
                        "columns": users_only_columns,
                        "rows": users_only_rows,
                        "total": len(classification_result["users_only"]),
                    }

                # 添加汇总数据
                if classification_result["summary"]:
                    classified_data["summary"] = classification_result["summary"]

                total_records = len(result.data.items)
                return ToolResponse.success_response(
                    data=classified_data,
                    record_count=total_records,
                    api_endpoint="/ad/GetMaterialCountList",
                    date_range=f"{start_date} 至 {end_date}",
                    indicators_count=len(result.data.items[0].keys())
                    if result.data.items
                    else 0,
                ).to_dict()

            else:
                # 没有数据时返回空的分类格式
                empty_data = {
                    "historical": None,
                    "active": None,
                    "no_conversion": None,
                    "users_only": None,
                    "summary": None,
                }

                return ToolResponse.success_response(
                    data=empty_data,
                    record_count=0,
                    api_endpoint="/ad/GetMaterialCountList",
                    date_range=f"{start_date} 至 {end_date}",
                    indicators_count=0,
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

    def _classify_material_data(self, response_data):
        """对素材数据进行智能分类和重组

        基于稀疏处理思想，按素材价值分类重新组织数据。
        注意：后端已过滤掉完全无用户行为的素材，返回的数据都至少有某种用户活动。

        分类标准：
        - historical: 历史素材（无消耗+有转化）
        - active: 活跃素材（有消耗+有转化）
        - no_conversion: 暂无转化素材（有消耗+暂无转化）
        - users_only: 仅用户素材（无消耗+仅有活跃用户）

        Args:
            response_data: API响应的data部分

        Returns:
            dict: 包含分类结果的字典，格式为:
            {
                'historical': [...],    # 历史素材列表
                'active': [...],       # 活跃素材列表
                'no_conversion': [...],   # 暂无转化素材列表
                'users_only': [...],   # 仅用户素材列表
                'summary': {...}       # 汇总数据
            }
        """
        if not response_data.items:
            return {
                "historical": [],
                "active": [],
                "no_conversion": [],
                "users_only": [],
            }

        # 核心转化指标（所有有价值的转化行为，使用中文字段名）
        conversion_indicators = [
            # 新增转化指标
            "新增注册",  # regUserCount
            "新增创角",  # regRoleCount
            "新增付费人数",  # newPayUser
            "新增付费金额",  # newPayMoney
            # 付费转化指标
            "当日充值人数",  # payUser
            "当日充值",  # payMoney
            "当日付费次数",  # payCount
            "首充付费人数",  # accumulatedPayUser
            "首充付费金额",  # accumulatedPayMoney
            "首充付费次数",  # accumulatedPayCount
            # 广告变现指标（小游戏相关）
            "广告变现人数",  # adBuyUsers
            "小游戏注册首日广告变现金额",  # income_val_24hs
            "小游戏广告变现金额（平台上报）",  # adBuyMoney2
            "广告变现成本",  # adBuyCost
        ]

        # 按分类组织数据
        classified_items = {
            "historical": [],  # 历史素材（无消耗+有转化）
            "active": [],  # 活跃素材（有消耗+有转化）
            "no_conversion": [],  # 暂无转化素材（有消耗+暂无转化）
        }

        # 仅用户素材列表（素材ID和活跃人数）
        users_only_materials = []

        for item in response_data.items:
            # 获取消耗值（使用中文字段名）
            cost = float(item.get("消耗", 0) or 0)

            # 检查是否有转化
            has_conversion = any(
                float(item.get(field, 0) or 0) > 0 for field in conversion_indicators
            )

            # 分类并组织数据
            if cost == 0:
                if has_conversion:
                    # 无消耗但有转化 = 历史效应素材
                    classified_items["historical"].append(item)
                else:
                    # 无消耗且仅有活跃 = 保留素材ID和活跃人数
                    material_id = item.get("素材id")
                    active_users = item.get("活跃用户", 0)
                    if material_id and active_users:
                        users_only_materials.append(
                            {"material_id": material_id, "active_users": active_users}
                        )

            elif cost > 0 and has_conversion:
                # 有消耗且有转化 = 活跃投放素材
                classified_items["active"].append(item)

            else:
                # 有消耗但暂无转化 = 暂无转化素材
                classified_items["no_conversion"].append(item)

        # 返回分类结果
        result = {
            "historical": classified_items["historical"],
            "active": classified_items["active"],
            "no_conversion": classified_items["no_conversion"],
            "users_only": users_only_materials,
            "summary": response_data.summary,  # 保留汇总数据
        }

        logger.info(
            f"素材数据重组完成: 历史效应{len(classified_items['historical'])}条, "
            f"活跃投放{len(classified_items['active'])}条, "
            f"暂无转化{len(classified_items['no_conversion'])}条, "
            f"仅活跃{len(users_only_materials)}条"
        )

        return result
