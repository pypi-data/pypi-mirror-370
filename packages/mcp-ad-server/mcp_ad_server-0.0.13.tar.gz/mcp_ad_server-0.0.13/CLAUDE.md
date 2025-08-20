# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Management
- **Install dependencies**: `uv sync`
- **Run server**: `uv run python run_server.py` or `python run_server.py`
- **Run tests**: `uv run python tests/test_server.py`

### Code Quality Tools
- **Format code**: `uv run black src/ tests/`
- **Sort imports**: `uv run isort src/ tests/`
- **Lint code**: `uv run ruff check src/ tests/`
- **Type checking**: `uv run mypy src/`
- **Run pytest**: `uv run pytest` (with coverage reporting to htmlcov/)

### Environment Variables
- **BI_API_TOKEN**: Required for API access to external BI service
- **LOG_LEVEL**: Optional, defaults to INFO (use DEBUG for detailed logging)

## Architecture Overview

This is an MCP (Model Context Protocol) server that provides advertising analytics data to LLM applications. The architecture follows a layered design:

### Core Components
- **AdMCPServer** (`src/mcp_ad_server/main.py`): Main server class that coordinates all components
- **Data Model Layer** (`src/mcp_ad_server/models/`): Pydantic-based data validation and type safety
  - `api_models.py`: API request/response models with comprehensive validation
  - `response.py`: MCP tool unified response models with error handling
  - Automatic parameter validation, type conversion, and data cleaning
- **Manager Layer** (`src/mcp_ad_server/managers/`): Data management with Manager base class pattern
  - `IndicatorManager`: Manages 89 business metrics definitions and recommendations
  - `PropmapManager`: Handles API field mapping between display names and API fields
- **Service Layer** (`src/mcp_ad_server/services/`): External API integration
  - `APIClient`: HTTP client with Chinese-to-English parameter mapping, alias support, version management, and automatic summary processing
- **MCP Tools** (`src/mcp_ad_server/tools/`): Business logic exposed as MCP tools
  - `query_ad_data`: Ad performance data queries (18 parameters, TaskGroup concurrent 24-hour queries)
  - `query_material_data`: Creative material analysis (22 parameters, quality filtering)
  - `recommend_indicators`: Smart metric recommendations based on business scenarios
- **MCP Resources** (`src/mcp_ad_server/resources/`): Configuration and metadata access
  - URI pattern: `mcp://indicators/{name}`, `mcp://groups/{id}`, `mcp://config/{type}`

### Data Architecture
- **JSON-based configuration**: All business metrics, groupings, and mappings stored in `data/` directory
- **89 Business Metrics**: Comprehensive advertising KPIs covering spend, conversion, retention, finance
- **7 Business Scenarios**: Metric groupings for different use cases (launch, monitoring, evaluation, etc.)
- **API Field Mapping**: Bidirectional mapping between Chinese display names and API field names

### Business Logic
The system supports 7 key business scenarios with smart metric recommendations:
1. **投放启动** (Launch Decision): Metrics for deciding whether to start new campaigns
2. **效果监控** (Performance Monitoring): Real-time campaign performance tracking
3. **短期评估** (Short-term Evaluation): 1-7 day value assessment
4. **深度分析** (Deep Analysis): Long-term value and retention analysis
5. **数据对账** (Data Reconciliation): Platform data verification
6. **风险预警** (Risk Alerts): Campaign termination decision support
7. **财务核算** (Financial Settlement): Finance-related metrics

### Key Patterns
- **Manager Base Class**: All data managers inherit from `managers.base.Manager` with standardized `load_data()` method
- **Pydantic Data Validation**: Complete type safety with automatic parameter validation and conversion
- **Chinese Parameter Support**: MCP tools accept Chinese parameters (e.g., `app="正统三国"` instead of `app_id="59"`)
- **Parameter Alias Support**: Backward compatibility for legacy parameter names (e.g., `appid` ↔ `app_id`)
- **Intelligent Parameter Mapping**: Automatic conversion from Chinese display values to API-required English codes
- **Accurate Summary Calculation**: Multi-day 24-hour queries use additional API requests for precise aggregated data
- **LLM-Optimized Interface**: Chinese parameters and Chinese-mapped data optimized for LLM consumption
- **Version Management**: API client versioning with compatibility checking
- **Dependency Injection**: Components are initialized with required dependencies in main server
- **Async-first**: All operations use async/await for performance
- **Error Handling**: Comprehensive error responses with success/error status

## File Organization

### Source Code Structure
```
src/mcp_ad_server/
├── main.py              # AdMCPServer main entry point
├── config.py            # Configuration management with validation constants
├── models/              # Pydantic data models and validation
│   ├── __init__.py         # Model exports
│   ├── api_models.py       # API request/response models with validation
│   └── response.py         # MCP tool response models and error handling
├── managers/            # Data management layer
│   ├── base.py         # Manager base class
│   ├── indicator_manager.py
│   └── propmap_manager.py
├── services/           # External service integration
│   └── api_client.py      # HTTP client with alias support and data processing
├── tools/              # MCP tool implementations
│   ├── ad_query.py         # Ad data queries (18 parameters)
│   ├── material_query.py   # Material data queries (22 parameters)
│   └── indicator_query.py # Game indicator tools
├── resources/          # MCP resource implementations
│   ├── indicator_resources.py
│   ├── mapping_resources.py
│   └── config_resources.py
└── prompts/            # MCP prompt implementations (planned)
```

### Data Configuration
```
data/
├── indicators/         # 89 individual metric definitions (JSON)
├── groups/            # 7 business scenario groupings
└── propmap/           # API field mapping files
```

## Testing Strategy

- **Integration Tests**: `tests/test_server.py` - Full server functionality
- **Unit Tests**: `tests/test_config.py`, `tests/test_dotenv.py` - Component testing
- **Coverage Target**: 80% minimum (configured in pyproject.toml)
- **Test Execution**: Use `uv run pytest` for full test suite with coverage

## Common Workflows

### Adding New Metrics
1. Create JSON definition in `data/indicators/{metric_name}.json`
2. Add to appropriate business scenario group in `data/groups/`
3. Update API field mapping in `data/propmap/` if needed
4. Test with `uv run python tests/test_server.py`

### Adding New Business Scenarios
1. Create new group file in `data/groups/`
2. Update IndicatorManager recommendation logic in `indicator_manager.py:104-120`
3. Add corresponding tests

### Extending MCP Tools
1. Create new tool class in `src/mcp_ad_server/tools/`
2. Follow existing pattern with `__init__(dependencies)` and `register(mcp)` methods
3. Register in `AdMCPServer._init_tools()` method in `main.py:70-80`

## API Integration

- **Base URL**: Configured via environment and config system
- **Authentication**: Requires BI_API_TOKEN environment variable
- **Endpoints**: GetAdCountList, GetMaterialCountList (see docs/api/ for details)
- **Field Mapping**: Chinese display names and parameter values automatically mapped to API field names and codes via PropmapManager

## Important Notes

- **Python Version**: Requires Python 3.11+
- **Async Architecture**: All components use async/await patterns
- **MCP Protocol**: Strictly follows MCP standard for tools, resources, and prompts
- **Chinese Language**: Business metrics, scenarios, and tool parameters use Chinese names (this is intentional for the target business users and LLM accessibility)
- **Environment Setup**: Claude Desktop integration requires full Python path in configuration due to PATH differences
