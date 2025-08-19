"""
API数据模型 - 使用Pydantic定义API请求和响应模型
"""

import logging
import re
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..config import Config

logger = logging.getLogger(__name__)


class APIBaseModel(BaseModel):
    """API模型基类"""

    model_config = ConfigDict(
        # 允许额外字段，用于未来扩展
        extra="allow",
        # 使用枚举值而不是枚举名称
        use_enum_values=True,
        # 验证赋值
        validate_assignment=True,
        # 允许用别名/字段名互相赋值和导出
        populate_by_name=True,
        from_attributes=True,
    )

    # 预先获取支持的API参数值（避免在验证器中重复计算）
    VALID_APP_IDS: ClassVar[list[str]] = list(Config.APP_MAPPING.values())
    VALID_GROUP_KEYS: ClassVar[list[str]] = list(Config.GROUP_KEY_MAPPING.values())
    VALID_MEDIA: ClassVar[list[str]] = list(Config.MEDIA_MAPPING.values())
    VALID_MEDIA_BUYERS: ClassVar[list[str]] = list(Config.MEDIA_BUYERS_MAPPING.values())
    VALID_AD_STATUSES: ClassVar[list[str]] = list(Config.AD_STATUSES_MAPPING.values())

    @staticmethod
    def validate_date_format(value: str) -> str:
        """验证日期格式YYYY-MM-DD"""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise ValueError("日期格式必须为YYYY-MM-DD")
        return value


# ==================== 请求模型 ====================


class GetAdCountListRequest(APIBaseModel):
    """广告数据查询请求模型"""

    # 基础参数
    appid: str = Field(
        default=Config.APP_MAPPING[Config.DEFAULT_APP], description="游戏ID"
    )
    start_time: str = Field(default="", description="开始时间，格式：YYYY-MM-DD")
    end_time: str = Field(default="", description="结束时间，格式：YYYY-MM-DD")
    zhibiao_list: list[str] = Field(..., description="查询指标列表")
    group_key: str = Field(default="", description="分组维度")
    is_deep: bool = False
    hours_24: bool = False
    is_test: bool = True

    # 广告计划相关参数
    ji_hua_name: str = ""
    ji_hua_id: list[str] = Field(default_factory=list)

    # 媒体和投手参数
    media: list[str] = Field(default_factory=list, description="媒体渠道列表")
    toushou: list[str] = Field(default_factory=list, description="投手列表")

    # 账户和状态参数
    self_cid: list[str] = Field(default_factory=list)
    ad_status: list[str] = Field(default_factory=list, description="广告状态列表")

    # 创意和广告组参数
    creative_id: list[str] = Field(default_factory=list)
    vp_adgroup_id: list[str] = Field(default_factory=list)

    # 系统参数
    deep_bid_type: list[str] = Field(default_factory=list)

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        if v:  # 只在非空时才验证
            return cls.validate_date_format(v)
        return v

    @field_validator("appid")
    @classmethod
    def validate_appid(cls, v: str) -> str:
        if v not in cls.VALID_APP_IDS:
            raise ValueError(f"不支持的游戏ID: {v}，支持的ID: {cls.VALID_APP_IDS}")
        return v

    @field_validator("media")
    @classmethod
    def validate_media(cls, v: list[str]) -> list[str]:
        if v:
            invalid_media = [m for m in v if m not in cls.VALID_MEDIA]
            if invalid_media:
                raise ValueError(
                    f"不支持的媒体渠道: {invalid_media}，" f"支持的渠道: {cls.VALID_MEDIA}"
                )
        return v

    @field_validator("group_key")
    @classmethod
    def validate_group_key(cls, v: str) -> str:
        if v and v not in cls.VALID_GROUP_KEYS:
            raise ValueError(f"不支持的分组维度: {v}，" f"支持的维度: {cls.VALID_GROUP_KEYS}")
        return v

    @field_validator("ad_status")
    @classmethod
    def validate_ad_status(cls, v: list[str]) -> list[str]:
        if v:
            invalid_status = [s for s in v if s not in cls.VALID_AD_STATUSES]
            if invalid_status:
                raise ValueError(
                    f"不支持的广告状态: {invalid_status}，" f"支持的状态: {cls.VALID_AD_STATUSES}"
                )
        return v

    @field_validator("toushou")
    @classmethod
    def validate_toushou(cls, v: list[str]) -> list[str]:
        if v:
            invalid_toushou = [t for t in v if t not in cls.VALID_MEDIA_BUYERS]
            if invalid_toushou:
                raise ValueError(
                    f"不支持的投手: {invalid_toushou}，" f"支持的投手: {cls.VALID_MEDIA_BUYERS}"
                )
        return v


class GetMaterialCountListRequest(APIBaseModel):
    """素材数据查询请求模型"""

    # 基础参数
    appid: str = Field(
        default=Config.APP_MAPPING[Config.DEFAULT_APP], description="游戏ID"
    )
    start_time: str = Field(default="", description="开始时间，格式：YYYY-MM-DD")
    end_time: str = Field(default="", description="结束时间，格式：YYYY-MM-DD")
    zhibiao_list: list[str] = Field(..., description="查询指标列表")
    group_key: str = Field(default="", description="分组维度")
    is_inefficient_material: Literal[-1, 1, 2] = Field(
        default=-1, description="低效素材筛选：-1全选、1是、2否"
    )
    is_ad_low_quality_material: Literal[-1, 1, 2] = Field(
        default=-1, description="AD优/低质筛选：-1全选、1低质、2优质"
    )
    is_deep: bool = False
    is_old_table: bool = False

    # 媒体和投手参数
    media: list[str] = Field(default_factory=list, description="媒体渠道列表")
    toushou: list[str] = Field(default_factory=list, description="投手列表")

    # 制作和创意人员参数
    producer: list[str] = Field(default_factory=list, description="制作人列表")
    creative_user: list[str] = Field(default_factory=list, description="创意人列表")

    # 账户参数
    self_cid: list[str] = Field(default_factory=list)

    # 素材相关参数 (originality_xxx)
    vp_originality_id: list[str] = Field(default_factory=list)
    vp_originality_name: list[str] = Field(default_factory=list)
    vp_originality_type: list[str] = Field(default_factory=list, description="素材类型列表")

    # 广告组和创意参数
    vp_adgroup_id: list[str] = Field(default_factory=list)
    creative_id: list[str] = Field(default_factory=list)
    component_id: list[str] = Field(default_factory=list)

    # 系统参数
    deep_bid_type: list[str] = Field(default_factory=list)

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        if v:  # 只在非空时才验证
            return cls.validate_date_format(v)
        return v

    @field_validator("appid")
    @classmethod
    def validate_appid(cls, v: str) -> str:
        if v not in cls.VALID_APP_IDS:
            raise ValueError(f"不支持的游戏ID: {v}，支持的ID: {cls.VALID_APP_IDS}")
        return v

    @field_validator("media")
    @classmethod
    def validate_media(cls, v: list[str]) -> list[str]:
        if v:
            invalid_media = [m for m in v if m not in cls.VALID_MEDIA]
            if invalid_media:
                raise ValueError(
                    f"不支持的媒体渠道: {invalid_media}，" f"支持的渠道: {cls.VALID_MEDIA}"
                )
        return v

    @field_validator("group_key")
    @classmethod
    def validate_group_key(cls, v: str) -> str:
        if v and v not in cls.VALID_GROUP_KEYS:
            raise ValueError(f"不支持的分组维度: {v}，" f"支持的维度: {cls.VALID_GROUP_KEYS}")
        return v

    @field_validator("toushou")
    @classmethod
    def validate_toushou(cls, v: list[str]) -> list[str]:
        if v:
            invalid_toushou = [t for t in v if t not in cls.VALID_MEDIA_BUYERS]
            if invalid_toushou:
                raise ValueError(
                    f"不支持的投手: {invalid_toushou}，" f"支持的投手: {cls.VALID_MEDIA_BUYERS}"
                )
        return v

    @field_validator("producer")
    @classmethod
    def validate_producer(cls, v: list[str]) -> list[str]:
        if v:
            invalid_producers = [p for p in v if p not in Config.SUPPORTED_PRODUCERS]
            if invalid_producers:
                raise ValueError(
                    f"不支持的制作人: {invalid_producers}，"
                    f"支持的制作人: {Config.SUPPORTED_PRODUCERS}"
                )
        return v

    @field_validator("creative_user")
    @classmethod
    def validate_creative_user(cls, v: list[str]) -> list[str]:
        if v:
            invalid_users = [u for u in v if u not in Config.SUPPORTED_CREATIVE_USERS]
            if invalid_users:
                raise ValueError(
                    f"不支持的创意人: {invalid_users}，"
                    f"支持的创意人: {Config.SUPPORTED_CREATIVE_USERS}"
                )
        return v

    @field_validator("vp_originality_type")
    @classmethod
    def validate_originality_type(cls, v: list[str]) -> list[str]:
        if v:
            invalid_types = [t for t in v if t not in Config.SUPPORTED_MATERIAL_TYPES]
            if invalid_types:
                raise ValueError(
                    f"不支持的素材类型: {invalid_types}，"
                    f"支持的类型: {Config.SUPPORTED_MATERIAL_TYPES}"
                )
        return v


# ==================== 响应数据模型 ====================


class AdDataRecord(APIBaseModel):
    """广告数据记录模型"""

    # 基础维度字段
    日期: str | None = None
    广告计划名称: str | None = None
    创意名称: str | None = None
    项目名称: str | None = None
    广告状态: str | None = None

    # 指标字段 - 使用Union[str, int, float]因为API可能返回不同类型
    消耗: str | int | float | None = None
    新增注册: str | int | None = None
    新增创角: str | int | None = None
    创角率: str | float | None = None
    点击率: str | float | None = None
    激活率: str | float | None = None
    点击成本: str | float | None = None
    活跃用户: str | int | None = None
    曝光次数: str | int | None = None
    千次展现均价: str | float | None = None
    点击数: str | int | None = None
    当日充值: str | float | None = None
    当日付费次数: str | int | None = None
    当日充值人数: str | int | None = None
    新增付费人数: str | int | None = None
    首充付费人数: str | int | None = None
    首充付费次数: str | int | None = None
    老用户付费人数: str | int | None = None
    新增付费金额: str | float | None = None
    首充付费金额: str | float | None = None
    老用户付费金额: str | float | None = None
    新增付费率: str | float | None = None
    活跃付费率: str | float | None = None
    活跃arppu: str | float | None = None
    新增arppu: str | float | None = None
    小游戏注册首日广告变现金额: str | float | None = None
    小游戏注册首日广告变现ROI: str | float | None = None
    当月注册用户充值金额: str | float | None = None
    注册成本: str | float | None = None
    创角成本: str | float | None = None
    首日ROI: str | float | None = None
    累计ROI: str | float | None = None
    分成后首日ROI: str | float | None = None
    分成后累计ROI: str | float | None = None
    付费成本: str | float | None = None
    新增付费成本: str | float | None = None


class MaterialDataRecord(APIBaseModel):
    """素材数据记录模型"""

    # 基础维度字段
    日期: str | None = None
    素材id: str | None = None
    素材名称: str | None = None
    素材类型: str | None = None
    素材封面uri: str | None = None
    制作人: str | None = None
    创意人: str | None = None
    素材创造时间: str | None = None

    # 素材特有指标
    三秒播放率: str | float | None = Field(None, alias="3秒播放率")
    完播率: str | float | None = None
    是否低效素材: str | int | None = None
    是否AD低质素材: str | int | None = None
    是否AD优质素材: str | int | None = None
    低质原因: str | None = None

    # 通用指标
    新增注册: str | int | None = None
    新增创角: str | int | None = None
    创角率: str | float | None = None
    点击率: str | float | None = None
    激活率: str | float | None = None
    点击成本: str | float | None = None
    活跃用户: str | int | None = None
    当日充值: str | float | None = None
    当日付费次数: str | int | None = None
    当日充值人数: str | int | None = None
    新增付费人数: str | int | None = None
    首充付费人数: str | int | None = None
    新增付费金额: str | float | None = None
    首充付费金额: str | float | None = None
    新增付费率: str | float | None = None
    活跃付费率: str | float | None = None
    活跃arppu: str | float | None = None
    新增arppu: str | float | None = None
    小游戏注册首日广告变现金额: str | float | None = None
    小游戏注册首日广告变现ROI: str | float | None = None
    消耗: str | float | None = None
    新增付费成本: str | float | None = None
    付费成本: str | float | None = None
    注册成本: str | float | None = None
    创角成本: str | float | None = None
    首日ROI: str | float | None = None
    累计ROI: str | float | None = None
    分成后首日ROI: str | float | None = None
    分成后累计ROI: str | float | None = None


class APIResponseData(APIBaseModel):
    """API响应数据部分
    包含完整的API响应字段
    """

    # 数据列表
    items: list[dict[str, Any]] = Field(
        default_factory=list, alias="list", description="数据列表"
    )

    # 字段映射：中文名 -> API字段名
    prop_map: dict[str, str] = Field(
        default_factory=dict, alias="propMap", description="字段映射"
    )

    # UI列字段列表
    ui_cols: list[str] = Field(
        default_factory=list, alias="uiCols", description="UI列字段"
    )

    # 指标列表
    indicator_list: list[str] = Field(
        default_factory=list, alias="zhibiao_list", description="指标列表"
    )

    # 总数量（可选）
    total: int | None = Field(None, description="总记录数")

    # 总计数据（从数据列表中提取的总计项）
    summary: dict[str, Any] | None = Field(None, description="总计数据行")

    # 分组别名（素材API特有）
    group_key_alias: str | None = Field(None, alias="groupKeyAlias", description="分组别名")

    @field_validator("items", mode="before")
    @classmethod
    def validate_items_list(cls, v):
        """处理API返回None时的情况"""
        if v is None:
            return []
        return v

    def model_post_init(self, __context) -> None:
        """模型初始化后处理：提取总计项并清理数据列表"""
        self._extract_and_clean_summary()

    def _extract_and_clean_summary(self):
        """提取总计项并清理数据列表

        后端API在data.list的最后一项返回总计数据：
        - GetAdCountList: date字段为"总计"、空字符串或null
        - GetMaterialCountList: groupKey字段为"总计"
        这个方法会识别并提取总计项到summary字段，同时从items中移除。
        """
        if not self.items:
            return

        # 检查最后一项是否为总计项
        last_item = self.items[-1]

        is_summary_item = False
        summary_identifier_key = None

        # 方法1：检查date字段是否为"总计"、空字符串或null (GetAdCountList)
        for key, value in last_item.items():
            if key in ["日期", "date", "dt"] or "date" in key.lower():
                if value == "总计" or value == "" or value is None:
                    is_summary_item = True
                    summary_identifier_key = key
                break

        # 方法2：检查groupKey字段是否为"总计" (GetMaterialCountList)
        if not is_summary_item:
            for key, value in last_item.items():
                if "group" in key.lower() and "key" in key.lower():
                    if value == "总计":
                        is_summary_item = True
                        summary_identifier_key = key
                    break

        # 如果识别为总计项，则提取并清理
        if is_summary_item:
            self.summary = last_item.copy()
            # 移除标识字段，因为总计数据不应该有维度标识
            if summary_identifier_key and summary_identifier_key in self.summary:
                del self.summary[summary_identifier_key]
            self.items = self.items[:-1]  # 移除最后一项

    page: int | None = Field(None, description="当前页")
    page_size: int | None = Field(None, alias="pageSize", description="每页大小")


class BaseAPIResponse(APIBaseModel):
    """API基础响应模型"""

    code: int = Field(..., description="响应代码")
    msg: str = Field(..., description="响应消息")
    data: APIResponseData | None = None

    @property
    def is_success(self) -> bool:
        """判断请求是否成功"""
        return self.code == 0


class GetAdCountListResponse(BaseAPIResponse):
    """广告数据查询响应模型"""

    def get_records(self) -> list[AdDataRecord]:
        """获取解析后的广告数据记录列表"""
        if not self.data or not self.data.items:
            return []

        records = []
        for item in self.data.items:
            try:
                cleaned = DataConverter.clean_data_record(item)
                records.append(AdDataRecord(**cleaned))
            except Exception as e:
                # 记录解析失败的数据，但不中断处理
                logger.warning("Failed to parse ad record: %s", e)
                continue
        return records


class GetMaterialCountListResponse(BaseAPIResponse):
    """素材数据查询响应模型"""

    def get_records(self) -> list[MaterialDataRecord]:
        """获取解析后的素材数据记录列表"""
        if not self.data or not self.data.items:
            return []

        records = []
        for item in self.data.items:
            try:
                cleaned = DataConverter.clean_data_record(item)
                records.append(MaterialDataRecord(**cleaned))
            except Exception as e:
                # 记录解析失败的数据，但不中断处理
                logger.warning("Failed to parse material record: %s", e)
                continue
        return records


# ==================== 数据转换辅助类 ====================


class DataConverter:
    """数据转换工具类"""

    @staticmethod
    def safe_float(value: str | int | float | None) -> float | None:
        """安全转换为浮点数"""
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def safe_int(value: str | int | float | None) -> int | None:
        """安全转换为整数"""
        if value is None or value == "":
            return None
        try:
            if isinstance(value, float):
                return int(value)
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def clean_data_record(record: dict[str, Any]) -> dict[str, Any]:
        """清理数据记录，处理空字符串和类型转换"""
        cleaned = {}
        for key, value in record.items():
            if value == "" or value == "null":
                cleaned[key] = None
            else:
                cleaned[key] = value
        return cleaned
