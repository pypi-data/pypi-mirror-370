## 接口地址

```uri
https://bi.dartou.com/testapi/ad/GetAdCountList
```
## 请求方式
<span style="font-size:1.3rem">`POST`</span>

## 请求头参数（Headers）
| 参数名 | 类型     | 必填 | 说明      |
| --- | ------ | -- | ------- |
| X-Token   | string | 是  | 请求token |
| X-Ver   | string | 是  | 系统版本，当前版本为`0.2.07` |

## 请求体（Body）
请求体需为 <span style="color:red">application/json</span> 格式，并包含以下参数：
| 参数名 | 类型 | 必填 | 说明       |
| --- | ------ | --- | -------- |
| appid   | string | 是 | 游戏id，正统三国ID为:`59` |
| start_time   | string | 是  | 查询范围开始时间，格式：`YYYY-MM-DD` |
| end_time   | string | 是  | 查询范围结束时间，格式：`YYYY-MM-DD` |
| zhibiao_list   | Array\<String\> | 是  | 指标列表，**必须包含"日期"指标**，其他可选值见补充 |
| media   | Array\<String\> | 否  | 媒体，查询广点通媒体：["gdt"] |
| group_key   | string | 否  | 分组，按广告id分组："vp_campaign_id" |
| hours_24 | bool | 否 | 是否返回 24 小时的数据。启用时start_time和end_time必须为同一天，日期字段将显示为01,02,03...24表示小时 |

### 示例请求体
```json
{
    "appid": "59",
    "end_time": "2025-06-24",
    "start_time": "2025-06-24",
    "media":["gdt"],
    "group_key":"vp_campaign_id",
    "zhibiao_list": [
      ...
    ]
}
```

### API行为说明

#### 成功响应（code: 0）
- 当zhibiao_list包含"日期"指标且其他指标有效时，返回正常数据
- 注意：原始 BI API 会忽略无效指标；但在本项目的 MCP 服务中，工具层会预先校验指标，若包含无效指标将直接返回错误（INVALID_INDICATORS），以避免误用。

#### 错误响应（code: 500）
1. **空指标列表错误**：
   - zhibiao_list为空数组`[]`、`null`或缺失
   - 返回消息：`"请先选择指标"`

2. **缺少日期指标错误**：
   - zhibiao_list不包含"日期"指标
   - 返回消息包含SQL错误：`"Missing columns: 'Date' while processing query"`
   - 同时返回完整的SQL查询语句和调用栈信息

### 响应示例

#### 成功响应
```json
{
    "code": 0,
    "data": {
        "groupKeyAlias": "groupKey",
        "group_key": "vp_campaign_id",
        "list": [
            {
                "Date": "2025-08-07~2025-08-07",
                "cost": 2033.51,
                "regUserCount": 410,
                "groupKey": "50799923701"
            }
        ],
        "propMap": {
            "日期": "Date",
            "消耗": "cost",
            "新增注册": "regUserCount"
        },
        "uiCols": ["Date", "cost", "regUserCount"],
        "zhibiao_list": ["日期", "消耗", "新增注册"]
    },
    "msg": "查询成功",
    "token": "",
    "unix_time": 1754621152
}
```

#### 错误响应（空指标）
```json
{
    "code": 500,
    "msg": "请先选择指标",
    "data": [
        "请先选择指标",
        "manager/pkg/service/account_data_report_table.(*AccountDataReportTable).GetAdCountListFxV2",
        "调用栈信息..."
    ],
    "token": "",
    "unix_time": 1754621152
}
```



+ 参数<span style="color:red">media</span>可选值有
    + `全选`(全选)
    + `sphdr`(视频号达人)
    + `bd`(百度)
    + `xt`(星图)
    + `bdss`(百度搜索)
    + `gdt`(广点通)
    + `bz`(b站)
    + `zh`(知乎)
    + `dx`(抖小广告量)
    + `tt`(今日头条)
    + `uc`(uc)
    + `gg`(谷歌)
    + `nature`(自然量)
+ 参数<span style="color:red">group_key</span>可选值有
    + `vp_advert_pitcher_id`(投手)
    + `dt_vp_fx_cid`(self_cid)
    + `vp_adgroup_id`(项目id)
    + `vp_advert_channame`(媒体)
    + `vp_campaign_id`(广告id)
    + `vp_originality_id`(创意id)

## 后端实现架构

### SQL查询结构分析

通过捕获API错误返回的完整SQL查询，我们可以了解后端的实际数据处理逻辑：

#### 主查询结构
```sql
SELECT [聚合指标字段列表]
FROM (复杂的多表UNION查询)
GROUP BY Date WITH ROLLUP
```

**关键点**：
- 查询必须以`GROUP BY Date`结束，这就是为什么"日期"指标是必需的
- 使用`WITH ROLLUP`进行汇总统计

#### 数据源组成（UNION结构）

**1. 用户事件数据** (`local_dt_event59_view`)
```sql
-- 充值成功事件
WHERE dt_part_event IN ('充值成功')

-- 用户注册事件
WHERE dt_part_event IN ('用户注册')

-- 用户创角事件（通过JOIN获取）
INNER JOIN ... WHERE dt_part_event = '用户创角'
```

**2. 用户基础信息** (`local_dt_user59`)

> 59对应于游戏正统三国，如果查询无权限的游戏数据会返回：
>
> httpx - INFO - HTTP Request: POST https://bi.dartou.com/testapi/ad/GetAdCountList "HTTP/1.1 202 Accepted"
> 状态码: 202
> 返回码: 500
> 消息: 您不属于该游戏成员

```sql
-- 提供用户注册时间、渠道等基础信息
-- 关联广告归因数据：fx_cid, campaign_id, originality_id等
```

**3. 平台广告数据** (`platform_data_59`)

```sql
-- 广告投放成本、展示、点击等平台数据
-- 提供cost, show_cnt, click_num等关键指标
```

#### 核心指标计算逻辑

**付费相关指标**：
```sql
-- 累计首充金额
sum(if((dt_part_event = '充值成功') AND (is_first_pay2 = 1), money, 0)) AS accumulatedFirstPayMoney

-- 新增付费用户数
uniqExact(if((dt_part_event = '充值成功') AND (is_first_pay = 1) AND (is_first_reg = 1), dt_distinct_id, NULL)) AS newPayUser

-- 平台分成计算
sum(...) * 0.8 AS newIosPayMoney    -- iOS 80%分成
sum(...) * 0.4 AS newAndroidPayMoney -- Android 40%分成
```

**用户行为指标**：
```sql
-- 新增注册用户数（去重）
uniqExact(if(dt_part_event = '用户注册', dt_distinct_id, NULL)) AS regUserCount

-- 新增创角用户数（去重）
uniqExact(if(dt_part_event = '用户创角', dt_distinct_id, NULL)) AS regRoleCount
```

**广告效果指标**：
```sql
-- 投放成本
round(sum(cost), 2) AS cost

-- 展示次数
sum(show_cnt) AS view_count

-- 小游戏广告变现 24h
sum(income_val_24h) AS income_val_24hs
```

### 为什么"日期"指标是必需的

1. **SQL结构依赖**：主查询使用`GROUP BY Date WITH ROLLUP`，必须存在Date字段
2. **指标映射**：前端"日期"指标映射为SQL中的`Date`字段
3. **数据聚合**：所有业务指标都需要按日期维度进行分组统计

### 业务逻辑链路

```
用户获取: 展示 -> 点击 -> 注册 -> 创角 -> 活跃
收入转化: 活跃用户 -> 付费用户 -> 首充/复充 -> 平台分成
数据聚合: 按日期分组 -> 计算各项指标 -> 返回统计结果
```

### 渠道分类说明

**重要澄清**：从SQL查询分析，`channel IN (100004)`的含义：

- **channel = 100004**：买量渠道（付费广告获取的用户）
- **channel ≠ 100004 或 fx_cid IS NULL**：自然量用户

SQL中的条件 `(fx_cid IS NOT NULL) AND (channel IN (100004))` 明确表示：
- 必须有广告归因ID (`fx_cid IS NOT NULL`)
- 且渠道为100004 (`channel IN (100004)`)
- 这个组合条件用于筛选**买量用户**，而非自然量用户

### 数据表关联关系

```
local_dt_event59_view (用户行为事件)
├── dt_distinct_id: 用户唯一标识
├── dt_part_event: 事件类型（注册/创角/充值等）
└── date: 事件发生日期

local_dt_user59 (用户基础信息)
├── dt_distinct_id: 关联用户标识
├── fx_cid: 广告归因ID
└── campaign_id: 广告计划ID

platform_data_59 (平台广告数据)
├── fx_cid: 关联广告归因
├── cost: 广告消耗
└── show_cnt: 展示次数
```

### POSTMAN示例
![alt text](image.png)
