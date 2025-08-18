# 📚 API接口文档自动生成指南

本项目提供了基于Pydantic模型和类型注解的API接口文档自动生成功能。

## 说明

### 🔧 API客户端文档 (client.md)
- BiApiClient类的所有公开方法
- 方法签名、参数说明、返回值类型
- 基于方法docstring的详细说明

### 📊 数据模型文档 (models/)
- **请求模型**: API请求的Pydantic模型和字段说明
- **响应模型**: API响应的结构和方法说明
- **记录模型**: 业务数据记录的字段分类和使用示例

### ⚙️ 配置文档 (config.md)
- 所有配置常量和支持的选项
- 支持的游戏、媒体、投手、状态等枚举值

目前项目暂未包含自动生成 API 文档的脚本与入口（历史文档提及的 `scripts/generate_api_docs.py` 与 `generate-api-docs` 已移除）。如需生成文档，请使用手工维护的 `docs/api/` 目录。

## 🎯 进阶使用

### 自定义文档生成

可以继承`APIDocGenerator`类来自定义文档生成逻辑：

```python
from scripts.generate_api_docs import APIDocGenerator

class CustomDocGenerator(APIDocGenerator):
    def _generate_custom_section(self):
        # 添加自定义文档部分
        pass
```

若未来需要恢复自动化方案，可新增文档生成脚本后再补充本页内容。

（MkDocs 相关示例暂不适用）

## TODO（如恢复自动化后再启用）
- [ ] 支持生成 OpenAPI 规范文档
- [ ] 集成 Swagger UI / MkDocs
