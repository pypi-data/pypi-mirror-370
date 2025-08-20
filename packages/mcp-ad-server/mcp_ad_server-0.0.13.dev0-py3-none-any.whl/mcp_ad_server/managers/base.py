"""
数据管理器基础类
"""

import logging
from abc import ABC, abstractmethod
from typing import Any


class Manager(ABC):
    """数据管理器基础类"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.loaded = False
        self.data: dict[str, Any] = {}

    @abstractmethod
    async def load_data(self) -> None:
        """加载数据 - 子类必须实现"""
        pass

    def get_data(self, key: str) -> Any | None:
        """获取数据"""
        return self.data.get(key)

    def get_all_data(self) -> dict[str, Any]:
        """获取所有数据"""
        return self.data.copy()

    def is_loaded(self) -> bool:
        """检查是否已加载数据"""
        return self.loaded

    def clear_data(self) -> None:
        """清空数据"""
        self.data.clear()
        self.loaded = False
        self.logger.info("数据已清空")

    def get_data_count(self) -> int:
        """获取数据项数量"""
        return len(self.data)
