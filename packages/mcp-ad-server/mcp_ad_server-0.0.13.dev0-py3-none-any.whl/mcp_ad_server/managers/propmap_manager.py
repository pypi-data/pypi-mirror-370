"""
字段映射管理器 - 管理API字段的显示名称与字段名映射关系
"""

import json
from typing import Any

import aiofiles

from ..config import Config
from .base import Manager


class PropmapManager(Manager):
    """字段映射管理器类"""

    def __init__(self):
        super().__init__()
        # data现在存储的是 api_name -> { api_field: display_name }
        # 即：API字段名 -> 中文显示名
        self.field_to_display_mappings: dict[str, dict[str, str]] = {}

        # 反向映射：中文显示名 -> API字段名
        self.display_to_field_mappings: dict[str, dict[str, str]] = {}

    async def load_mappings(self):
        """加载所有字段映射文件"""
        propmap_dir = Config.PROPMAP_DIR

        if not propmap_dir.exists():
            self.logger.warning(f"映射目录不存在: {propmap_dir}")
            return

        try:
            mapping_files = list(propmap_dir.glob("*.json"))
            self.logger.info(f"发现{len(mapping_files)}个映射文件")

            for file_path in mapping_files:
                api_name = file_path.stem  # 如 GetAdCountList, GetMaterialCountList

                try:
                    async with aiofiles.open(file_path, encoding="utf-8") as f:
                        content = await f.read()
                        mapping_data = json.loads(content)

                    # 现在propMap直接是：API字段名 -> 中文显示名
                    prop_map = mapping_data.get("propMap", {})
                    self.field_to_display_mappings[api_name] = prop_map.copy()

                    # 创建反向映射：中文显示名 -> API字段名
                    display_to_field_map = {
                        display_name: api_field
                        for api_field, display_name in prop_map.items()
                    }

                    # 处理字段别名：允许多个后端字段名映射到同一显示名
                    field_aliases = mapping_data.get("fieldAliases", {})
                    if field_aliases:
                        for alias_field_name, display_name in field_aliases.items():
                            # 添加别名到字段->显示名映射
                            self.field_to_display_mappings[api_name][
                                alias_field_name
                            ] = display_name
                            # 如果显示名不存在于反向映射中，添加它（优先使用主字段）
                            if display_name not in display_to_field_map:
                                display_to_field_map[display_name] = alias_field_name

                    self.display_to_field_mappings[api_name] = display_to_field_map

                    self.logger.info(f"加载映射文件 {api_name}: {len(prop_map)}个字段")

                except Exception as e:
                    self.logger.error(f"加载映射文件失败 {file_path}: {e}")

            self.logger.info(f"成功加载{len(self.field_to_display_mappings)}个API的字段映射")

        except Exception as e:
            self.logger.error(f"加载映射目录失败: {e}")
            raise

    async def load_data(self) -> None:
        """实现基类的抽象方法加载数据"""
        await self.load_mappings()
        self.loaded = True
        self.logger.info("字段映射管理器数据加载完成")

    async def initialize(self):
        """初始化管理器"""
        if self.is_loaded():
            return
        await self.load_data()
        self.logger.info("字段映射管理器初始化完成")

    def get_field_name(self, display_name: str, api_name: str) -> str | None:
        """获取显示名称对应的字段名"""
        api_mapping = self.display_to_field_mappings.get(api_name, {})
        return api_mapping.get(display_name)

    def get_display_name(self, field_name: str, api_name: str) -> str | None:
        """获取字段名对应的显示名称"""
        api_mapping = self.field_to_display_mappings.get(api_name, {})
        return api_mapping.get(field_name)

    def get_all_mappings(self, api_name: str) -> dict[str, str]:
        """获取指定API的所有字段映射（显示名称 -> 字段名）"""
        return self.display_to_field_mappings.get(api_name, {}).copy()

    def get_field_to_display_mappings(self, api_name: str) -> dict[str, str]:
        """获取指定API的字段到显示名映射（字段名 -> 显示名称）"""
        return self.field_to_display_mappings.get(api_name, {})

    def get_supported_apis(self) -> list[str]:
        """获取支持的API列表"""
        return list(self.field_to_display_mappings.keys())

    def get_display_names(self, api_name: str) -> list[str]:
        """获取指定API支持的所有显示名称"""
        return list(self.display_to_field_mappings.get(api_name, {}).keys())

    def get_field_names(self, api_name: str) -> list[str]:
        """获取指定API支持的所有字段名"""
        return list(self.field_to_display_mappings.get(api_name, {}).keys())

    def map_to_fields(self, display_names: list[str], api_name: str) -> list[str]:
        """将显示名称列表映射为字段名列表"""
        if not display_names:
            return []

        api_mapping = self.display_to_field_mappings.get(api_name, {})
        field_names = []

        for display_name in display_names:
            field_name = api_mapping.get(display_name)
            if field_name:
                field_names.append(field_name)
            else:
                self.logger.warning(f"显示名称'{display_name}'在API '{api_name}'中没有对应的字段名")
                # 如果没有映射，保留原始名称
                field_names.append(display_name)

        return field_names

    def _get_mapping_with_group_key(
        self, api_name: str, group_key: str = ""
    ) -> dict[str, str]:
        """获取包含动态groupKey映射的字段到显示名映射

        Args:
            api_name: API名称
            group_key: 分组维度参数，用于动态映射groupKey字段

        Returns:
            字段名到显示名的映射字典
        """
        base_mapping = self.get_field_to_display_mappings(api_name)

        if not group_key:
            return base_mapping

        # 创建包含动态groupKey的映射（避免修改原始映射）
        enhanced_mapping = base_mapping.copy()

        # 智能处理group_key：支持中文和英文两种格式
        if group_key in Config.GROUP_KEY_MAPPING:
            # group_key是中文值，直接使用
            group_display_name = group_key
        else:
            # group_key是英文API代码，转换为中文显示名称（向后兼容）
            en_to_cn_mapping = {v: k for k, v in Config.GROUP_KEY_MAPPING.items()}
            group_display_name = en_to_cn_mapping.get(group_key, group_key)

        enhanced_mapping["groupKey"] = group_display_name

        return enhanced_mapping

    def map_fields_to_display(
        self, items: list[dict], api_name: str, group_key: str = ""
    ) -> list[dict]:
        """将items列表的字段名映射为显示名称

        Args:
            items: 数据项列表
            api_name: API名称
            group_key: 分组维度参数，用于动态映射groupKey字段

        Returns:
            映射后的数据项列表
        """
        if not items:
            return items

        api_mapping = self._get_mapping_with_group_key(api_name, group_key)

        mapped_list = []
        for item in items:
            mapped_item = {
                api_mapping.get(field_name, field_name): value
                for field_name, value in item.items()
            }
            mapped_list.append(mapped_item)

        return mapped_list

    def map_field_to_display(
        self, item: dict, api_name: str, group_key: str = ""
    ) -> dict:
        """将单个数据项的字段名映射为显示名称

        Args:
            item: 单个数据项
            api_name: API名称
            group_key: 分组维度参数，用于动态映射groupKey字段

        Returns:
            映射后的数据项
        """
        if not item:
            return item

        api_mapping = self._get_mapping_with_group_key(api_name, group_key)

        return {
            api_mapping.get(field_name, field_name): value
            for field_name, value in item.items()
        }

    def validate_names(self, names: list[str], api_name: str) -> list[str]:
        """验证显示名称是否支持指定API，返回不支持的名称列表"""
        if not names:
            return []

        api_mapping = self.display_to_field_mappings.get(api_name, {})
        return [name for name in names if name not in api_mapping]

    def search_fields(
        self, keyword: str, api_name: str | None = None
    ) -> dict[str, list[str]]:
        """搜索包含关键词的字段"""
        if not keyword:
            return {}

        results = {}
        keyword_lower = keyword.lower()

        apis_to_search = (
            [api_name] if api_name else self.field_to_display_mappings.keys()
        )

        for api in apis_to_search:
            api_field_to_display = self.field_to_display_mappings.get(api, {})

            matched_displays = [
                display_name
                for field_name, display_name in api_field_to_display.items()
                if keyword_lower in display_name.lower()
                or keyword_lower in field_name.lower()
            ]

            if matched_displays:
                results[api] = matched_displays

        return results

    def get_mapping_stats(self) -> dict[str, Any]:
        """获取映射统计信息"""
        return {
            "total_apis": len(self.field_to_display_mappings),
            "api_details": [
                {"api_name": api_name, "field_count": len(mappings)}
                for api_name, mappings in self.field_to_display_mappings.items()
            ],
            "total_fields": sum(
                len(mappings) for mappings in self.field_to_display_mappings.values()
            ),
        }

    async def reload(self):
        """重新加载映射数据"""
        self.clear_data()
        self.field_to_display_mappings.clear()
        self.display_to_field_mappings.clear()

        await self.initialize()
        self.logger.info("字段映射管理器数据已重新加载")
