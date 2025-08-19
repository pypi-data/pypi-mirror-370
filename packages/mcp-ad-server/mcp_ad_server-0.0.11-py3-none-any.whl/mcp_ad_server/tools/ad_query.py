"""
广告查询工具

从main.py提取的query_ad_data工具实现。
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from ..models import ErrorCodes, ErrorMessages, ToolPayload, ToolResponse

logger = logging.getLogger(__name__)


class AdQueryTool:
    """广告查询工具类"""

    def __init__(self, api_client, indicator_manager, config):
        self.api_client = api_client
        self.indicator_manager = indicator_manager
        self.config = config

    def register(self, mcp):
        """注册工具到MCP服务器"""

        @mcp.tool()
        async def query_ad_data(
            start_date: str,
            end_date: str,
            indicators: list[str],
            app: str = "正统三国",
            group_key: str = "",
            is_deep: bool = False,
            hours_24: bool = False,
            # 广告计划相关参数
            campaign_name: str | None = None,
            campaign_ids: str | list[str] | None = None,
            # 媒体和投手参数
            media: str | list[str] | None = None,
            media_buyers: str | list[str] | None = None,
            # 账户和状态参数
            cids: str | list[str] | None = None,
            ad_statuses: str | list[str] | None = None,
            # 创意和广告组参数
            creative_ids: str | list[str] | None = None,
            adgroup_ids: str | list[str] | None = None,
        ) -> dict[str, Any]:
            """
            查询广告投放数据

            Args:
                start_date: 查询开始日期（YYYY-MM-DD）
                end_date: 查询结束日期（YYYY-MM-DD）
                indicators: 指标列表（⚠️ 建议先调用 get_available_indicators 确认可用指标）
                app: 游戏应用，默认：正统三国，可选值：正统三国、银河战舰、开心十三张、哈局成语大师、我的仙门、一起斗消乐、大头大菠萝、大头十三水、大头斗地主
                group_key: 分组维度，默认：空字符串（不分组），可选值：广告ID、项目ID、创意ID、投手、self_cid、媒体
                is_deep: 是否获取下探UI数据（默认：False）
                hours_24: 是否返回逐小时数据（True时日期格式变为"YYYY-MM-DD HH"，当天数据仅返回已有小时）
                campaign_name: 广告计划名称筛选
                campaign_ids: 广告计划ID列表
                media: 媒体渠道，可选值：全选、广点通、今日头条、百度、百度搜索、B站、知乎、UC、抖小广告量、视频号达人、星图、谷歌、自然量
                media_buyers: 投手，可选值：李霖林、戴呈翔、尹欣然、施逸风、郭耀月、张鹏、宗梦男、fx2.0
                cids: 广告账户CID列表
                ad_statuses: 广告状态，可选值：已冻结、暂停中、已删除、广告未到投放时间、投放中、账户余额不足、广告达到日预算上限、投放结束
                creative_ids: 创意ID列表
                adgroup_ids: 广告组ID列表

            Returns:
                查询结果：
                - success: 是否成功
                - data.columns: 列名
                - data.rows: 数据行
                - data.total: 记录数
                - data.summary: 汇总行
                - metadata: 元数据（时间、接口等）

            Note:
                - 不同游戏支持的指标不同，建议先验证指标可用性
                - 多天24小时查询会并发请求各天数据并合并
                - 分组查询支持多维度统计分析
                - 参数支持中文值输入，自动映射为API格式
            """
            return await self._query_ad_data(
                start_date=start_date,
                end_date=end_date,
                indicators=indicators,
                app=app,
                group_key=group_key,
                is_deep=is_deep,
                hours_24=hours_24,
                campaign_name=campaign_name,
                campaign_ids=campaign_ids,
                media=media,
                media_buyers=media_buyers,
                cids=cids,
                ad_statuses=ad_statuses,
                creative_ids=creative_ids,
                adgroup_ids=adgroup_ids,
            )

    async def _query_ad_data(
        self,
        start_date: str,
        end_date: str,
        indicators: list[str],
        app: str,
        group_key: str = "",
        is_deep: bool = False,
        hours_24: bool = False,
        # 广告计划相关参数
        campaign_name: str | None = None,
        campaign_ids: str | list[str] | None = None,
        # 媒体和投手参数
        media: str | list[str] | None = None,
        media_buyers: str | list[str] | None = None,
        # 账户和状态参数
        cids: str | list[str] | None = None,
        ad_statuses: str | list[str] | None = None,
        # 创意和广告组参数
        creative_ids: str | list[str] | None = None,
        adgroup_ids: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """实际的查询实现"""
        try:
            # 多天24小时查询处理
            if hours_24 and start_date != end_date:
                return await self._handle_multi_day_24h_query(
                    start_date,
                    end_date,
                    indicators,
                    app,
                    group_key,
                    is_deep,
                    campaign_name,
                    campaign_ids,
                    media,
                    media_buyers,
                    cids,
                    ad_statuses,
                    creative_ids,
                    adgroup_ids,
                )

            # 指标验证现在在APIClient层完成

            # 调用API查询数据
            result = await self.api_client.get_ad_count_list(
                app=app,
                start_date=start_date,
                end_date=end_date,
                indicators=indicators,
                group_key=group_key,
                is_deep=is_deep,
                hours_24=hours_24,
                campaign_name=campaign_name,
                campaign_ids=campaign_ids,
                media=media,
                media_buyers=media_buyers,
                cids=cids,
                ad_statuses=ad_statuses,
                creative_ids=creative_ids,
                adgroup_ids=adgroup_ids,
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
                api_endpoint="/ad/GetAdCountList",
                date_range=(
                    f"{start_date} 24小时维度" if hours_24 else f"{start_date} 至 {end_date}"
                ),
                indicators_count=len(columns),
            ).to_dict()

        except Exception as e:
            logger.error(f"查询广告数据失败: {e}")
            msg, suggestions = ErrorMessages.api_request_failed(str(e))
            return ToolResponse.error_response(
                code=ErrorCodes.API_REQUEST_FAILED,
                message=msg,
                details=str(e),
                suggestions=suggestions,
                api_endpoint="/ad/GetAdCountList",
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

    async def _handle_multi_day_24h_query(
        self,
        start_date: str,
        end_date: str,
        indicators: list[str],
        app: str,
        group_key: str,
        is_deep: bool,
        campaign_name: str,
        campaign_ids: str | list[str] | None,
        media: str | list[str] | None,
        media_buyers: str | list[str] | None,
        cids: str | list[str] | None,
        ad_statuses: str | list[str] | None,
        creative_ids: str | list[str] | None,
        adgroup_ids: str | list[str] | None,
    ) -> dict[str, Any]:
        """处理多天24小时查询：分天调用并合并结果"""
        try:
            # 生成日期范围
            date_range = self._generate_date_range(start_date, end_date)
            logger.info(f"执行多天24小时查询: {len(date_range)}天，从{start_date}到{end_date}")

            # 指标验证现在在APIClient层完成

            # 定义单天查询函数
            async def query_single_day(date: str):
                """查询单天数据，返回(date, result)元组"""
                result = await self.api_client.get_ad_count_list(
                    start_date=date,
                    end_date=date,  # 确保同一天
                    indicators=indicators,
                    app=app,
                    group_key=group_key,
                    is_deep=is_deep,
                    hours_24=True,  # 强制24小时
                    campaign_name=campaign_name,
                    campaign_ids=campaign_ids or [],
                    media=media or [],
                    media_buyers=media_buyers or [],
                    cids=cids or [],
                    ad_statuses=ad_statuses or [],
                    creative_ids=creative_ids or [],
                    adgroup_ids=adgroup_ids or [],
                )
                return (date, result)

            # 使用TaskGroup并发查询所有天
            logger.info(f"开始并发查询{len(date_range)}天的24小时数据")
            daily_results = []
            failed_dates = []

            async with asyncio.TaskGroup() as tg:
                # 创建所有任务，按日期增加错峰启动间隔（在非调试模式下）
                tasks = []
                for index, date in enumerate(date_range):
                    if (
                        not self.config.BI_DEBUG
                        and getattr(self.config, "QUERY_STAGGER_SECONDS", 0) > 0
                    ):
                        # 为每个任务加入基于索引的延迟，避免瞬时同时打满后端
                        async def delayed_task(d: str, delay: float):
                            await asyncio.sleep(delay)
                            return await query_single_day(d)

                        delay_seconds = index * self.config.QUERY_STAGGER_SECONDS
                        task = tg.create_task(delayed_task(date, delay_seconds))
                    else:
                        task = tg.create_task(query_single_day(date))
                    tasks.append((date, task))

            # 收集结果
            for date, task in tasks:
                try:
                    result = task.result()
                    daily_results.append(result)
                except Exception as e:
                    logger.error(f"查询日期{date}时发生错误: {e}")
                    failed_dates.append(date)

            logger.info(f"并发查询完成，成功{len(daily_results)}天，失败{len(failed_dates)}天")

            if not daily_results:
                return ToolResponse.error_response(
                    code=ErrorCodes.API_REQUEST_FAILED,
                    message="所有日期查询均失败",
                    details=f"查询日期范围: {start_date} - {end_date}",
                    suggestions=["请检查日期范围是否正确", "请稍后重试"],
                ).to_dict()

            # 合并查询结果
            merged_result = await self._merge_multi_day_results(
                daily_results=daily_results,
                start_date=start_date,
                end_date=end_date,
                indicators=indicators,
                app=app,
                group_key=group_key,
                is_deep=is_deep,
                campaign_name=campaign_name,
                campaign_ids=campaign_ids,
                media=media,
                media_buyers=media_buyers,
                cids=cids,
                ad_statuses=ad_statuses,
                creative_ids=creative_ids,
                adgroup_ids=adgroup_ids,
            )
            logger.info(f"成功合并{len(daily_results)}天的24小时数据")

            return merged_result

        except Exception as e:
            logger.error(f"多天24小时查询失败: {e}")
            msg, suggestions = ErrorMessages.api_request_failed(str(e))
            return ToolResponse.error_response(
                code=ErrorCodes.API_REQUEST_FAILED,
                message=msg,
                details=str(e),
                suggestions=suggestions,
            ).to_dict()

    def _generate_date_range(self, start_date: str, end_date: str) -> list[str]:
        """生成日期范围列表，按日期倒序排列（最新日期在前）"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        date_list = []
        current = start
        while current <= end:
            date_list.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        # 倒序排列，保持与普通数据查询的一致性（最新日期在前）
        date_list.reverse()
        return date_list

    async def _merge_multi_day_results(
        self,
        daily_results: list[tuple[str, Any]],
        start_date: str,
        end_date: str,
        indicators: list[str],
        app: str,
        group_key: str,
        is_deep: bool,
        campaign_name: str | None,
        campaign_ids: str | list[str] | None,
        media: str | list[str] | None,
        media_buyers: str | list[str] | None,
        cids: str | list[str] | None,
        ad_statuses: str | list[str] | None,
        creative_ids: str | list[str] | None,
        adgroup_ids: str | list[str] | None,
    ) -> dict[str, Any]:
        """合并多天查询结果"""
        if not daily_results:
            return ToolResponse.error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message="没有可合并的查询结果",
            ).to_dict()

        columns = []
        merged_rows = []
        total_records = 0

        # TODO: 未来可考虑返回daily_summaries列表，保留每天的summary细节
        # daily_summaries = []  # 格式: [{"date": "2024-01-01", "summary": {...}}, ...]
        # 这样前端可以展示每日趋势，更好地理解数据变化

        # 处理每一天的数据
        for date, api_result in daily_results:
            try:
                # 提取列名和行数据
                data_items = api_result.data.items if api_result.data else []
                if data_items:
                    if not columns:
                        # 第一天：建立列名标准
                        columns = list(data_items[0].keys())

                    # 转换为二维数组格式并合并
                    for row_dict in data_items:
                        row_values = [row_dict.get(col) for col in columns]
                        merged_rows.append(row_values)

                # 累计记录数
                total_records += len(data_items)

                # 当前方案：暂时忽略每天的summary，后续通过额外请求获取准确总计
                # 未来方案：可收集保留 daily_summaries.append({"date": date, "summary": api_result.data.summary})

            except Exception as e:
                logger.warning(f"处理日期{date}的数据时发生错误: {e}")
                continue

        # 额外请求获取准确的总计数据（非24小时查询）
        # 这样可以获得后端正确计算的百分比、比率等聚合指标
        #
        # 原方案问题：
        # 1. 手动合并summary时，百分比/比率字段简单取第一个值，不能反映整体情况
        # 2. 某些字段不应该简单累加，缺乏业务逻辑
        # 3. 容易产生错误的统计结果（如ROI、点击率等比率指标）
        total_summary = None
        try:
            logger.info(f"请求{start_date}至{end_date}的汇总数据")
            summary_result = await self.api_client.get_ad_count_list(
                start_date=start_date,
                end_date=end_date,
                indicators=indicators,
                app=app,
                group_key=group_key,
                is_deep=is_deep,
                hours_24=False,  # 关键：不要24小时数据，获取日汇总
                campaign_name=campaign_name,
                campaign_ids=campaign_ids,
                media=media,
                media_buyers=media_buyers,
                cids=cids,
                ad_statuses=ad_statuses,
                creative_ids=creative_ids,
                adgroup_ids=adgroup_ids,
            )

            if summary_result.data and summary_result.data.summary:
                total_summary = summary_result.data.summary
                logger.info("成功获取准确的汇总数据")
            else:
                logger.warning("未能获取汇总数据，将不返回summary")

        except Exception as e:
            logger.warning(f"获取汇总数据失败: {e}，将不返回summary")
            # 不影响主数据返回，只是没有summary

        # 构建最终响应
        payload = ToolPayload(
            columns=columns,
            rows=merged_rows,
            total=total_records,
            summary=total_summary,  # 使用后端计算的准确总计
        )

        return ToolResponse.success_response(
            data=payload,
            record_count=total_records,
            api_endpoint="/ad/GetAdCountList",
            date_range=f"{start_date} 至 {end_date} 24小时维度",
            indicators_count=len(columns),
        ).to_dict()
