# API接口与后端代码映射文档

本文档记录了前端API接口与后端实际代码实现的映射关系，便于开发者快速定位相关业务逻辑。

## 文档说明

- **接口端点**：前端调用的API路径
- **路由配置**：路由定义在代码中的位置
- **控制器函数**：处理请求的控制器方法
- **核心业务逻辑**：实际执行业务逻辑的服务层代码
- **关键文件**：涉及的主要代码文件

---

## 广告数据相关接口

### GetMaterialCountList - 素材数据查询

#### 1. 普通接口
- **接口端点**: `/api/ad/GetMaterialCountList`
- **路由配置**: `pkg/web_server/ad.go:104`
- **控制器函数**: `AdDataController.GetMaterialCountList`
- **文件位置**: `pkg/controller/ad_data_controller.go:2925`

#### 2. Token接口
- **接口端点**: `/testapi/ad/GetMaterialCountListByToken`
- **路由配置**: `pkg/web_server/web_server.go:151`
- **控制器函数**: `AdDataController.GetMaterialCountListByToken`
- **文件位置**: `pkg/controller/ad_data_controller.go:1825`

#### 业务逻辑路由
**路由判断逻辑** (`ad_data_controller.go:1847-1850`):
```go
if util.InstrArr(config.FxApps, reqData.Appid) {
    return this.GetMaterialCountListFx(ctx, reqData)  // FX系路由
}
return this.GetMaterialCountListBI(ctx, reqData)     // BI系路由
```

**FX系再次路由** (`ad_data_controller.go:7234-7236`):
```go
if util.InstrArr(reqData.Media, "gdt") || util.InstrArr(reqData.Media, "bd") {
    return this.GetMaterialCountListFxGdt(ctx, reqData)  // GDT路由
}
// 继续TT路由
```

#### 核心实现函数
1. **GetMaterialCountListBI** - BI系素材查询
   - 位置: `pkg/controller/ad_data_controller.go:5872`
   - 用途: 处理非FX系应用的素材数据查询

2. **GetMaterialCountListFxGdt** - FX系GDT/BD路由
   - 位置: `pkg/controller/ad_data_controller.go:6835`
   - 用途: 处理FX系应用中GDT和BD媒体的素材数据

3. **GetMaterialCountListFx** - FX系TT路由
   - 位置: `pkg/controller/ad_data_controller.go:7212`
   - 用途: 处理FX系应用中TT媒体的素材数据

---

### GetAdCountList - 广告数据查询

#### 1. 普通接口
- **接口端点**: `/api/ad/GetAdCountList`
- **路由配置**: `pkg/web_server/ad.go:102`
- **控制器函数**: `AdDataController.GetAdCountList`
- **文件位置**: `pkg/controller/ad_data_controller.go:1330`

#### 2. Token接口
- **接口端点**: `/testapi/ad/GetAdCountListByToken`
- **路由配置**: `pkg/web_server/web_server.go:150`
- **控制器函数**: `AdDataController.GetAdCountListByToken`
- **文件位置**: `pkg/controller/ad_data_controller.go:1785`

#### 核心业务逻辑
**业务逻辑服务** (两个接口最终调用相同服务):
- **FX系**: `this.accountDataReportTable.GetAdCountListFxV2(reqData, this.olap)`
- **BI系**: `this.accountDataReportTable.GetAdCountListBI(reqData, this.olap)`

**路由判断代码位置**:
- 普通接口: `ad_data_controller.go:1448-1457`
- Token接口: `ad_data_controller.go:1812-1821`

---

### GetOrderList - 订单详情查询

#### 1. 普通接口
- **接口端点**: `/api/ad/GetOrderList`
- **路由配置**: `pkg/web_server/ad.go:94`
- **控制器函数**: `AdDataController.GetOrderList`
- **文件位置**: `pkg/controller/ad_data_controller.go:2945`

#### 2. Token接口
- **接口端点**: `/testapi/ad/GetOrderListByToken`
- **路由配置**: `pkg/web_server/web_server.go:152`
- **控制器函数**: `AdDataController.GetOrderListByToken`
- **文件位置**: `pkg/controller/ad_data_controller.go:1853`

#### 业务逻辑路由
**路由判断逻辑** (`ad_data_controller.go:2959`):
```go
if util.InstrArr(config.FxApps, reqData.Appid) {
    return this.GetOrderListByFxV2(ctx, reqData)  // FX系路由
}
return this.GetOrderListByBI(ctx, reqData)       // BI系路由
```

#### 核心实现函数
1. **GetOrderListByFxV2** - FX系订单查询
   - 位置: `pkg/controller/ad_data_controller.go:2962`
   - 用途: 处理FX系应用的订单数据查询

2. **GetOrderListByBI** - BI系订单查询
   - 位置: `pkg/controller/ad_data_controller.go:4146`
   - 用途: 处理BI系应用的订单数据查询

3. **GetOrderListByBIV2** - BI系订单查询V2版本
   - 位置: `pkg/controller/ad_data_controller.go:4561`
   - 用途: BI系订单查询的升级版本

---

### DownloadAdCountList - 广告数据报表下载
- **接口端点**: `/api/ad/DownloadAdCountList`
- **路由配置**: `pkg/web_server/ad.go:103`
- **控制器函数**: `AdDataController.DownloadAdCountList`
- **文件位置**: `pkg/controller/ad_data_controller.go:1460`
- **用途**: 导出Excel格式的广告数据报表

---

## FX系统专用接口

### GetOverData - 综合数据概览
- **接口端点**: `/testapi/ad/GetOverData`
- **路由配置**: `pkg/web_server/web_server.go:154`
- **控制器函数**: `FxController.GetOverData`
- **文件位置**: `pkg/controller/fx_controller.go:445`
- **用途**: 获取FX系统的综合数据概览

### GetSortMoneyApps - 应用收入排序
- **接口端点**: `/testapi/ad/GetSortMoneyApps`
- **路由配置**: `pkg/web_server/web_server.go:155`
- **控制器函数**: `FxController.GetSortMoneyApps`
- **文件位置**: `pkg/controller/fx_controller.go:504`
- **用途**: 获取应用按收入排序的数据

---

## 广告账户管理接口

### GetAdIdGdt - 获取广点通账户ID
- **接口端点**: `/api/ad/GetAdIdGdt`
- **路由配置**: `pkg/web_server/ad.go:98`
- **控制器函数**: `AdDataController.GetAdIdGdt`
- **文件位置**: `pkg/controller/ad_data_controller.go:8133`
- **用途**: 获取广点通平台的账户ID信息

### GetAdIdTT - 获取头条账户ID
- **接口端点**: `/api/ad/GetAdIdTT`
- **路由配置**: `pkg/web_server/ad.go:99`
- **控制器函数**: `AdDataController.GetAdIdTT`
- **文件位置**: `pkg/controller/ad_data_controller.go:8150`
- **用途**: 获取头条平台的账户ID信息

---

## 关键词管理接口

### GetKeywordRecommend - 获取推荐关键词
- **接口端点**: `/api/ad/GetKeywordRecommend`
- **路由配置**: `pkg/web_server/ad.go:95`
- **控制器函数**: `controll.GetKeywordRecommend`
- **用途**: 获取推荐的广告关键词

### GetKeywordBusinessPoint - 获取关键词行业类目
- **接口端点**: `/api/ad/GetKeywordBusinessPoint`
- **路由配置**: `pkg/web_server/ad.go:96`
- **控制器函数**: `controll.GetKeywordBusinessPoint`
- **用途**: 获取关键词相关的行业分类信息

---

## 广告操作接口

### OpenChanAd - 开启或关闭项目
- **接口端点**: `/api/ad/OpenChanAd`
- **路由配置**: `pkg/web_server/ad.go:90`
- **控制器函数**: `controll.OpenChanAd`
- **用途**: 控制广告项目的开启或关闭状态

### EditCost - 编辑广告账户消耗
- **接口端点**: `/api/ad/EditCost`
- **路由配置**: `pkg/web_server/ad.go:92`
- **控制器函数**: `controll.EditCost`
- **用途**: 修改广告账户的消耗数据

---

## 其他工具接口

### router/getList - 路由列表
- **接口端点**: `/testapi/ad/router/getList`
- **路由配置**: `pkg/web_server/web_server.go:157`
- **控制器函数**: `ManagerUserController.RouterGetList`
- **用途**: 获取系统路由配置信息

### deepseek/generate - AI生成
- **接口端点**: `/testapi/ad/deepseek/generate`
- **路由配置**: `pkg/web_server/web_server.go:158`
- **控制器函数**: `RankController.GetGenerate`
- **用途**: AI内容生成相关功能

---

## 配置与工具接口

### ZhibiaoSelectConfig - 指标选择配置
- **接口端点**: 通过MountApi挂载
- **控制器函数**: `AdDataController.ZhibiaoSelectConfig`
- **文件位置**: `pkg/controller/ad_data_controller.go:626`
- **用途**: 返回前端指标选择器的配置数据

### GetSumAdCountOverview - 广告汇总概览
- **控制器函数**: `AdDataController.GetSumAdCountOverview`
- **文件位置**: `pkg/controller/ad_data_controller.go:1874`
- **特殊说明**: 此接口支持"付费"前缀的ROI指标

---

## 权限与用户管理

### 用户角色权限控制
**实现位置**: `pkg/controller/ad_data_controller.go:1350-1440`

**主要角色处理**:
- **Admin用户**: 无额外限制
- **测试用户**: 调用 `GetTestAdCountList`
- **腾讯用户**: 自动设置特定CID过滤
- **B站用户**: 自动设置媒体为"bz"
- **UC用户**: 自动设置投手过滤
- **荣耀用户**: 自动设置媒体为"ryphone"
- **支付宝用户**: 根据用户ID设置投手过滤
- **美术用户**: 限制查询最近180天数据

---

## 数据源配置

### 应用分类配置
- **FxApps配置**: `config.FxApps` 决定应用使用FX系还是BI系路由
- **配置文件**: 具体配置位置需查看config包

### 数据库连接
- **OLAP数据库**: `this.olap` - 主要数据查询
- **MySQL数据库**: `this.biMysql` - 配置和用户信息
- **缓存**: `this.olapLimiter` - 查询前清理缓存

---

## 关键业务服务

### accountDataReportTable服务
- **作用**: 核心数据报表查询服务
- **主要方法**:
  - `GetAdCountListFxV2` - FX系广告数据查询
  - `GetAdCountListBI` - BI系广告数据查询
  - `GetTestAdCountList` - 测试环境数据查询

### 权限服务 (gmRoleService)
- **作用**: 用户角色和权限管理
- **主要方法**:
  - `IsAdminUser` - 判断是否为管理员
  - `IsTencentUser` - 判断是否为腾讯用户
  - `IsBiliBiliUser` - 判断是否为B站用户
  - 其他角色判断方法...

---

## 文件结构总结

```
pkg/
├── controller/
│   ├── ad_data_controller.go      # 广告数据主控制器
│   └── openapi_controller.go      # 开放API控制器
├── web_server/
│   ├── ad.go                      # 广告相关路由配置
│   └── web_server.go              # 主路由配置
├── request/
│   └── Model.go                   # 请求数据模型定义
└── services/
    └── account_data_report_table/ # 核心业务逻辑服务
```

---

## 接口分类统计

### 核心数据查询接口 (3个)
- GetAdCountList - 广告数据查询
- GetMaterialCountList - 素材数据查询
- GetOrderList - 订单详情查询

### FX系统专用接口 (2个)
- GetOverData - 综合数据概览
- GetSortMoneyApps - 应用收入排序

### 广告账户管理接口 (2个)
- GetAdIdGdt - 获取广点通账户ID
- GetAdIdTT - 获取头条账户ID

### 关键词管理接口 (2个)
- GetKeywordRecommend - 获取推荐关键词
- GetKeywordBusinessPoint - 获取关键词行业类目

### 广告操作接口 (2个)
- OpenChanAd - 开启或关闭项目
- EditCost - 编辑广告账户消耗

### 配置与工具接口 (5个)
- ZhibiaoSelectConfig - 指标选择配置
- GetSumAdCountOverview - 广告汇总概览
- DownloadAdCountList - 广告数据报表下载
- router/getList - 路由列表
- deepseek/generate - AI生成

### Token接口统计
所有核心数据查询接口都提供Token版本：
- `/testapi/ad/GetAdCountListByToken`
- `/testapi/ad/GetMaterialCountListByToken`
- `/testapi/ad/GetOrderListByToken`

---

## 快速代码定位索引

### 主要控制器文件
- `pkg/controller/ad_data_controller.go` - 广告数据主控制器 (8000+ 行)
- `pkg/controller/fx_controller.go` - FX系统控制器
- `pkg/controller/openapi_controller.go` - 开放API控制器

### 路由配置文件
- `pkg/web_server/ad.go` - 广告相关路由配置
- `pkg/web_server/web_server.go` - Token接口路由配置
- `pkg/web_server/realdata.go` - 实时数据路由配置

### 核心业务服务
- `accountDataReportTable` - 核心数据报表查询服务
- `gmRoleService` - 用户角色和权限管理服务
- `this.olap` - OLAP数据库查询
- `this.biMysql` - MySQL数据库查询

### 权限控制关键点
- `ad_data_controller.go:1350-1440` - 用户角色权限控制逻辑
- `config.FxApps` - FX系与BI系应用分类配置
- `X-Token` 验证 - Token接口的安全验证

---

## 重要技术说明

### 应用分类体系
- **FX系应用**: 使用FxV2版本的数据查询逻辑
- **BI系应用**: 使用BI版本的数据查询逻辑
- 判断依据: `util.InstrArr(config.FxApps, reqData.Appid)`

### 媒体平台路由
- **GDT/BD媒体**: 使用GDT专用查询逻辑
- **TT媒体**: 使用TT专用查询逻辑
- **其他媒体**: 使用通用查询逻辑

### 数据库架构
- **ClickHouse (OLAP)**: 主要数据存储和查询
- **MySQL (biMysql)**: 配置信息和用户管理
- **缓存管理**: 查询前自动清理Mark Cache和Uncompressed Cache

---

## 开发规范建议

1. **新增接口时**: 优先考虑是否需要Token版本
2. **权限控制**: 新接口应在控制器层添加适当的角色权限检查
3. **路由判断**: 遵循FX系/BI系的分类规范
4. **数据查询**: 大数据量查询优先使用OLAP，配置查询使用MySQL
5. **错误处理**: 统一使用`this.Error(ctx, err)`格式
6. **成功响应**: 统一使用`this.Success(ctx, response.SearchSuccess, data)`格式

---

## 更新说明

本文档基于代码分析创建，如有代码变更请及时更新此文档。

**创建时间**: 2025-08-20
**分析范围**: BI_manager项目主要API接口
**文档版本**: v1.0
