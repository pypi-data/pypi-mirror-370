# 广告投放数据平台 MCP 服务

## 项目概述

这是一个基于 Model Context Protocol (MCP) 的广告投放数据服务器，为 LLM 应用提供智能的广告数据查询和分析能力。通过标准化的MCP协议，LLM可以直接调用广告投放相关的数据查询工具，获取业务洞察和决策支持。

## ✨ 核心特性

- **🔧 MCP工具集成**：提供广告查询、素材分析、指标推荐等MCP工具
- **📊 指标工具**：提供获取与验证指标的工具（推荐功能暂未启用）
- **🎯 多维数据查询**：支持按时间、媒体、分组等维度查询数据
- **🔗 标准协议支持**：完全遵循MCP协议，支持Claude Desktop等客户端
- **⚡ 异步高性能**：基于异步架构，支持并发数据查询

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone <repository-url> && cd mcp

# 2. 设置API Token
export BI_API_TOKEN="your_token_here"

# 3. 安装并运行测试
uv sync && uv run python tests/test_server.py
```

### 运行服务器

#### 方式一：标准stdio模式（Claude Desktop集成）
```bash
# 直接运行
python run_server.py

# 或使用uv
uv run python run_server.py
```

#### 方式二：StreamableHTTP模式（HTTP API服务）
```bash
# 使用命令行参数
python run_server.py --transport streamable-http

# 使用uv
uv run python run_server.py --transport streamable-http
```

StreamableHTTP模式支持以下环境变量配置：
- `HTTP_HOST`: 服务器地址（默认：127.0.0.1）
- `HTTP_PORT`: 服务器端口（默认：8000）
- `STREAMABLE_HTTP_PATH`: 服务路径（默认：/mcp）
- `STATELESS_HTTP`: 无状态模式（默认：False）
- `JSON_RESPONSE`: 使用JSON响应而非SSE（默认：False）

> 💡 StreamableHTTP模式将MCP服务器运行为HTTP API，支持通过HTTP请求调用MCP工具，适用于Web应用、API集成等场景。

### Claude Desktop集成
```json
{
    "mcpServers": {
        "mcp-ad-server": {
            "command": "uvx",
            "args": ["mcp_ad_server"],
            "env": {"BI_API_TOKEN": "your_token"}
        }
    },
    "mcp-ad-server-http": {
      "command": "uvx",
      "args": [
        "mcp-ad-server",
        "--transport",
        "streamable-http"
      ],
      "env": {
        "BI_API_TOKEN": "your_token",
        "HTTP_HOST": "127.0.0.1",
        "HTTP_PORT": "8000"
      }
    }
}
```

> **⚠️ 重要提示**：如果遇到 `spawn python ENOENT` 错误，请使用完整的 Python 路径（用 `which python3` 查找）而非 `python` 命令。Claude Desktop 的 PATH 环境变量与终端不同。


## 📁 项目结构

```
mcp/
├── 📄 README.md                    # 项目说明（本文档）
├── 📄 USER_GUIDE.md               # 用户使用手册
├── 📄 DEVELOPMENT.md             # 开发者指南
├── 📄 ARCHITECTURE.md            # 系统架构设计
├── 🚀 run_server.py               # 服务启动脚本
├── 🧪 tests/                      # 自动化单元测试
│   ├── test_config.py                # 配置测试
│   ├── test_dotenv.py                # 环境变量测试
│   ├── test_api_models.py            # API模型验证测试
│   ├── test_manager_base.py          # Manager基类测试
│   └── test_response_models.py       # 响应模型测试
├── 🔧 scripts/                     # 开发调试工具
│   ├── debug_api_server.py           # API调试服务器
│   └── compare_api_responses.py      # API响应对比工具
├── ✅ manual_tests/                 # 手动验证脚本
│   ├── verify_http_server.py         # HTTP服务器验证
│   ├── verify_ad_query.py            # 广告查询验证
│   ├── verify_mcp_server.py          # MCP服务器验证
│   ├── verify_mcp_components.py      # MCP组件验证
│   └── verify_api_client.py          # API客户端验证
│
├── 💻 src/mcp_ad_server/          # 主要源码
│   ├── main.py                       # 服务器主入口
│   ├── config.py                     # 配置管理
│   ├── services/                     # 业务服务层
│   │   └── api_client.py                # BI API客户端
│   ├── managers/                     # 数据管理层
│   │   ├── base.py                      # Manager基础类
│   │   ├── indicator_manager.py         # 指标管理器
│   │   └── propmap_manager.py           # 字段映射管理器
│   ├── tools/                        # MCP工具实现
│   │   ├── ad_query.py                  # 广告查询工具
│   │   ├── material_query.py            # 素材查询工具
│   │   └── indicator_query.py           # 游戏指标查询工具
│   ├── resources/                    # MCP资源实现
│   │   ├── indicator_resources.py       # 指标资源
│   │   ├── mapping_resources.py         # 映射资源
│   │   └── config_resources.py          # 配置资源
│   └── prompts/                      # MCP提示实现（计划中）
│
├── 📊 src/mcp_ad_server/data/    # 内置数据文件（运行时默认读取）
│   ├── indicators/               # 89个指标定义文件
│   ├── groups/                   # 7个指标分组文件
│   └── propmap/                  # API字段映射文件
│
└── 📚 docs/                       # 原始API文档
    └── api/                          # API接口文档
        ├── GetAdCountList/              # 广告数据统计接口
        └── GetMaterialCountList/        # 素材数据统计接口

```

## 🛠️ MCP 工具功能

### 1. query_ad_data - 广告数据查询
查询广告投放效果数据，支持多维度筛选和分组统计。

**参数**：
- `start_date/end_date`: 查询时间范围 (YYYY-MM-DD)
- `indicators`: 查询指标列表（中文名称）
- `media`: 媒体渠道筛选（支持中文名称：广点通、今日头条、百度等）
- `group_key`: 分组维度（广告ID、项目ID等）
- `hours_24`: 24小时维度查询，支持单天和多天并发查询

**返回结构**：
- `data.columns`: 列名列表（已做中文映射）
- `data.rows`: 二维数组格式的数据行，对应columns顺序
- `data.total`: 当前返回的数据条数
- `data.summary`: 汇总数据（如果存在）

### 2. query_material_data - 素材数据查询
查询广告素材效果和质量数据，支持素材质量筛选。

**参数**：
- `start_date/end_date`: 查询时间范围
- `indicators`: 查询指标列表
- `creative_users`: 创意人筛选
- `producers`: 制作人筛选
- `is_low_quality`: AD优/低质素材筛选
- `is_inefficient`: 低效素材筛选

**返回结构**：同广告数据查询

### 3. 游戏指标工具 - 指标验证与查询
基于游戏兼容性的指标验证和查询工具。

**可用工具**：
- `get_available_indicators` - 获取指定游戏的可用指标
- `validate_indicators` - 验证指标在指定游戏中是否可用

<!-- 场景推荐功能暂时注释，等待业务场景映射完善
- `recommend_indicators` - 基于场景智能推荐指标（开发中）
-->

## ✨ 系统特性

### 🔧 数据处理特性
- **自动总计项处理**: 智能识别和分离后端返回的总计数据
- **LLM优化数据结构**: 提供中文映射的数据格式，便于LLM理解和分析
- **参数别名兼容**: 支持历史参数名向下兼容（如 `appid` ↔ `app_id`）
- **Pydantic类型安全**: 完整的参数验证和数据类型转换

### 📊 数据返回格式
```json
{
  "success": true,
  "data": {
    "columns": ["日期", "消耗", "新增注册", "新增付费"],
    "rows": [
      ["2024-01-01", 100.5, 50, 5],
      ["2024-01-02", 120.0, 60, 8],
      ["2024-01-03", 80.0, 40, 3]
    ],
    "total": 3,            // 当前返回的数据条数
    "summary": {...}       // 汇总数据（如果后端提供）
  },
  "metadata": {...}        // 查询元数据
}
```

### 🔄 版本管理
- **API客户端版本**: v0.0.10
- **BI API版本**: v0.2.07
- **语义化版本控制**: 主版本兼容性保证

## 📋 MCP 资源访问

### 指标相关资源
- `mcp://indicators/{指标名称}` - 获取单个指标详细定义
- `mcp://groups/{组ID}` - 获取指标组信息
- `mcp://config/groups` - 获取所有指标组概览

### 配置相关资源
- `mcp://propmap/{API名称}` - 获取API字段映射关系
- `mcp://config/media` - 获取支持的媒体渠道
- `mcp://config/group_keys` - 获取支持的分组维度

## 📊 指标体系架构

### 目前的业务场景指标组

| 指标组 | 核心用途 | 主要指标示例 |
|--------|----------|-------------|
| **投放启动决策** | 判断是否开始投放新广告 | 激活率、注册成本、创角成本、3秒播放率 |
| **投放效果监控** | 监控投放中广告实时效果 | 消耗、点击率、新增注册、新增付费 |
| **短期价值评估** | 评估首日到7日用户价值 | 首日ROI、7日ROI、新增付费率、新增ARPPU |
| **深度价值分析** | 评估用户长期价值 | 累计ROI、留存率、生命周期价值 |
| **平台数据对账** | 核对各平台上报数据 | 平台充值、平台付费人数、数据差异 |
| **终止决策预警** | 判断是否需要停止投放 | 成本预警、ROI预警、质量预警 |
| **财务核算结算** | 财务结算相关 | 分成后ROI、实际消耗、结算金额 |

## 🔌 客户端集成示例

### Claude Desktop 使用
配置完成后，可直接在Claude Desktop中进行对话查询：

```
请帮我分析一下2025年1月1-7日腾讯广点通渠道的广告投放效果，
重点关注ROI表现和用户转化情况。
```

### 程序化调用
```python
# 使用MCP Python SDK
from mcp import ClientSession

async with ClientSession("stdio", ["python", "run_server.py"]) as session:
    # 查询广告数据
    result = await session.call_tool("query_ad_data", {
        "start_date": "2025-01-01",
        "end_date": "2025-01-07",
        "indicators": ["消耗", "新增注册", "首日ROI"],
        "app": "正统三国",
        "media": ["广点通", "今日头条"]
    })

    # 获取游戏可用指标
    available_indicators = await session.call_tool("get_available_indicators", {
        "app": "正统三国",
        "query_type": "ad_query"
    })

    # 验证指标兼容性
    validation = await session.call_tool("validate_indicators", {
        "indicators": ["消耗", "展现", "点击"],
        "app": "正统三国"
    })
```

## 🌐 支持的媒体渠道

**MCP工具直接使用中文名称，系统会自动转换为对应的API代码：**

| 中文名称 | API代码 | 中文名称 | API代码 |
|---------|---------|---------|---------|
| 广点通 | `gdt` | 今日头条 | `tt` |
| 百度 | `bd` | 百度搜索 | `bdss` |
| B站 | `bz` | 知乎 | `zh` |
| UC | `uc` | 抖小广告量 | `dx` |
| 视频号达人 | `sphdr` | 星图 | `xt` |
| 谷歌 | `gg` | 自然量 | `nature` |

## 📚 文档指南

本项目提供完整的文档体系，请根据您的角色选择合适的文档：

| 角色 | 推荐文档 | 用途 |
|------|----------|------|
| **最终用户/运营** | [USER_GUIDE.md](USER_GUIDE.md) | 安装使用、功能操作、业务应用 |
| **开发者/贡献者** | [DEVELOPMENT.md](DEVELOPMENT.md) | 开发环境、编码规范、扩展开发 |
| **架构师/技术负责人** | [ARCHITECTURE.md](ARCHITECTURE.md) | 系统设计、组件架构、技术决策 |

### 🚀 阅读建议

1. **想要快速使用服务**：直接阅读 [USER_GUIDE.md](USER_GUIDE.md) 的"快速开始"部分
2. **想要贡献代码**：先阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解设计，再看 [DEVELOPMENT.md](DEVELOPMENT.md) 学习开发规范
3. **想要了解技术架构**：重点阅读 [ARCHITECTURE.md](ARCHITECTURE.md)

## 🔧 技术特点

- **现代Python架构**：基于Python 3.11+
- **模块化设计**：清晰的层次分离，Manager模式管理数据
- **标准协议支持**：遵循MCP协议规范
- **高性能异步**：使用Python 3.11+ TaskGroup实现多天24小时数据并发查询，查询性能提升10-20倍
- **模块化扩展**：清晰的组件注册机制，便于添加新工具和资源
- **完整测试覆盖**：包含单元测试和集成测试

## 📈 更新日志

- v0.0.12 (2025-08-19)
  - **MCP工具参数描述优化**：
    - 使用`Annotated`和`Field`为所有MCP工具参数添加描述，使参数在list_tools时正确显示
    - 优化docstring结构，去除冗余部分
  - **硬编码清理**：
    - 更新测试脚本使用uv run本地运行方式，去除硬编码路径
- v0.0.11 (2025-08-19)
  - **素材查询分类架构优化**：重构素材查询工具，自动分类返回
    - 暂定四种素材分类模式：historical（历史素材）、active（活跃素材）、no_conversion（暂无转化）、users_only（仅用户素材）
  - **测试体系重组**：
    - 重新组织测试目录结构：`tests/`（单元测试）、`scripts/`（调试工具）、`manual_tests/`（手动验证脚本）
  - **简化API文档叙述**
- v0.0.10 (2025-08-18)
  - **StreamableHTTP传输模式支持**：新增HTTP API服务器模式，支持 `--transport` 命令行参数选择传输协议（stdio/streamable-http），支持通过HTTP请求调用MCP工具
  - **环境变量配置**：完善HTTP模式的配置选项（host、port、path等）
- v0.0.9 (2025-08-15)
  - **MCP工具参数类型优化**：支持字符串和列表参数混合使用
    - 修复工具签名中 `media` 等参数从 `list[str]` 改为 `str | list[str]`，暂时解决模型调用工具时不 Follow 类型约束的行为
- v0.0.8 (2025-08-15)
  - **日期字段自动添加**：指标查询时自动添加「日期」字段，无需手动指定
    - 改进用户体验，避免因缺少日期字段而产生的错误提示，简化LLM调用工具流程
  - **API模型参数处理优化**：增强GetAdCountListRequest和GetMaterialCountListRequest的参数处理能力
    - 新增 `@field_validator(mode="before")` 预处理验证器
    - 支持空/单字符串参数自动转换为列表，提升API使用体验
  - **API文档完善**：素材查询接口的文档更新（`docs/api/GetMaterialCountList/`）
- v0.0.7 (2025-08-15)
  - **文档参数更新**：统一所有文档中的参数格式，采用中文参数示例
  - **GroupKey指标验证优化**：修复分组字段本身的指标验证问题
    - 当使用 `group_key` 分组时，对应的分组字段（如"广告ID"、"项目ID"）现在被正确识别为有效指标
    - 增强 `validate_indicators` 方法，支持 `group_key` 参数进行更精确的指标验证
  - **API文档完善**：新增素材查询接口的今日头条响应示例文件
- v0.0.6 (2025-08-14)
  - **参数中文化改造**：MCP工具接口全面支持中文参数，提升LLM使用体验
    - 游戏参数从数字ID改为中文名称（如 `app_id="59"` → `app="正统三国"`）
    - 支持中文媒体渠道、投手姓名、广告状态等参数值
    - 新增游戏支持：我的仙门、一起斗消乐、大头系列游戏等
  - **多天24小时查询优化**：改进summary数据准确性
    - 废弃手动合并summary逻辑（存在百分比/比率指标计算不准确问题）
    - 通过额外API请求（`hours_24=False`）获取后端计算的准确汇总数据
    - 添加注释记录未来可返回`daily_summaries`列表的改进思路
- v0.0.5 (2025-08-14)
  - 指标验证系统重构和 PropMap 架构优化
  - 指标体系从全局改为游戏类型分组（棋牌/非棋牌）
  - PropMap 文件反向重构，管理器重写，提升可维护性
  - API 客户端验证逻辑优化：支持动态条件性指标注入，基于 `group_key` 智能添加指标，与前端表现一致
- v0.0.4 (2025-08-13)
  - 数据处理层重构与版本管理优化；素材数据完善；上传后端接口参考代码；基于代码更新 `docs/`
  - 对指标错误提供更规范的错误提示
  - 查询结果改为按日期倒序返回，且只输出筛选后的指标
    - 使用 `group_key` 分组时，会在返回中追加并映射对应的 `group_key`
- v0.0.3 (2025-08-12)
  - 清理推荐逻辑冗余代码，统一文件和函数命名规范
  - 迁移数据目录到 `src/mcp_ad_server/data` 以支持打包分发
  - 实现客户端层数据排序（普通数据按日期倒序，24 小时数据按小时正序）
  - 使用 Python 3.11+ `asyncio.TaskGroup` 优化多天 24 小时查询并发处理，暂时增加间隔避免瞬间打满后端，后续或可优化。
  - 通过 `uvx mcp_ad_server` 可在任意机器快速接入 MCP
- v0.0.2 (2025-08-11)
  - 完善 API 客户端功能：参数别名兼容、自动总计项处理、Pydantic 数据验证
- v0.0.1 (2025-08-07)
  - 重构文档体系，实现完整 MCP 服务架构
  - 初始化项目结构，整理指标体系
  - 添加 API 响应示例文件（原始提交于 2025-08-05）


## 🤝 技术支持

如有问题或建议，请联系：
- **技术问题**：钉钉 AI 开发团队
- **业务咨询**：广告投放团队
- **功能建议**：通过内部反馈渠道提交

## 📋 TODO (低优先级)

- **指标配置优化**：当前card_games/non_card_games结构中可能存在指标重复，可考虑抽取为分层指标集(base + extensions)以简化配置和维护

---

> **注意**：本项目中的指标分组和推荐算法为测试版本，实际使用时需要与投放团队对接校准业务逻辑。
