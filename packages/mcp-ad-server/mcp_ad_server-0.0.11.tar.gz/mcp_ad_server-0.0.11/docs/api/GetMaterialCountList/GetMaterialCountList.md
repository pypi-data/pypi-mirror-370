## 接口地址

```uri
https://bi.dartou.com/testapi/ad/GetMaterialCountList
```
## 请求方式
<span style="font-size:1.3rem">`POST`</span>

## 请求头参数（Headers）
| 参数名 | 类型     | 必填 | 说明      |
| --- | ------ | -- | ------- |
| X-Token   | String | 是  | 请求token |
| X-Ver   | String | 是  | 系统版本，当前版本为`0.2.07` |

## 请求体（Body）
请求体需为 <span style="color:red">application/json</span> 格式，并包含以下参数：
| 参数名 | 类型 | 必填 | 说明       |
| --- | ------ | --- | -------- |
| appid   | String | 是 | 游戏id，正统三国ID为:`59` |
| start_time   | String | 是  | 查询范围开始时间，格式：`YYYY-MM-DD` |
| end_time   | String | 是  | 查询范围结束时间，格式：`YYYY-MM-DD` |
| zhibiao_list   | Array\<String\> | 是  | 指标,可选值见补充 |
| media   | Array\<String\> | 否  | 媒体，查询广点通媒体：["gdt"] |
| group_key   | String | 否  | 分组（TT 默认 `originality_names`，GDT/BD 默认 `vp_originality_name`） |
| vp_adgroup_id   | Array\<String\> | 否  | 计划id |
| creative_id   | Array\<String\> | 否  | 创意id（GDT专用，可选） |
| component_id   | Array\<String\> | 否  | 组件id（GDT专用，可选） |
| self_cid   | Array\<String\> | 否  | 广告账户cid |
| toushou   | Array\<String\> | 否  | 投手 |
| producer   | Array\<String\> | 否  | 制作人 |
| creative_user | Array\<String\> | 否  | 创意人 |
| vp_originality_id | Array\<String\> | 否  | 素材id |
| vp_originality_name | Array\<String\> | 否  | 素材名 |
| vp_originality_type | Array\<String\> | 否  | 素材类型：TT 路由支持`["视频","图片"]`并做内部映射；GDT/BD 路由需传平台原始类型值 |
| is_inefficient_material | ‌Integer | 否  | 低效素材:取值`-1`(全选)、`1`(是)、`2`(否)（TT 路由支持，GDT 路由忽略） |
| is_ad_low_quality_material | ‌Integer | 否  | AD优/低质:取值`-1`(全选)、`1`(低质)、`2`(优质)（TT 路由支持，GDT 路由忽略） |
| is_old_table | Boolean | 否  | 旧报表：当`media`包含`gdt`或`bd`时可选，启用旧表`platform_data_gdt_` |
| is_deep | Boolean | 否  | 下探：仅 TT 路由有效（决定是否返回 UI 明细列） |
| deep_bid_type | Array\<String\> | 否 | 出价类型（仅 GDT/BD 路由可用） |


### 示例请求体
```json
{
	"appid": "59",
	"zhibiao_list": [
      ...
    ],
	"start_time": "2025-06-25",
	"end_time": "2025-06-25",
	"media": ["gdt"],
	"toushou": ["zp"],
	"group_key": "",
	"self_cid": [],
	"producer": [],
	"creative_user": ["张鹏"],
	"vp_originality_id": [],
	"vp_adgroup_id": [],
	"vp_originality_name": [],
	"vp_originality_type": [],
	"is_inefficient_material": -1,
	"is_ad_low_quality_material": -1,
	"is_deep": false,
	"is_old_table": false,
	"component_id": [],
	"creative_id": []
}
```

### 响应示例
以下示例为 GDT 路由返回；TT 路由在`uiCols`与`midAndScriptMap`上有所不同。TT 路由响应示例见同目录文件：`getmaterial_response_tt_example.json`。
```json
{
    "code": 0,
    "msg": "查询成功",
    "data": {
        "groupKeyAlias": "groupKey",//分组字段别名，详见"GroupKey字段处理机制"章节
        "list": [],//广告素材报表数据列表，使用group_key分组时包含groupKey字段
        "propMap": {//指标字段映射，包含所有可用指标的中英文映射关系
            "素材id": "show_vp_originality_id",
            "素材名称": "show_originality_names",
            "素材类型": "show_originality_type",
            "素材封面uri": "show_img_uris",
            "制作人": "show_producers",
            "创意人": "show_creative_persons",
            "素材创造时间": "show_material_create_times",
            "是否低效素材": "show_is_inefficient_material",
            "是否AD低质素材": "show_is_ad_low_quality_material",
            "低质原因": "show_message_ad_low_quality_material",
            "新增注册": "regUserCount",
            "消耗": "cost",
            "首日ROI": "firstDayRoi"
            //...更多指标映射
        },
        "uiCols": [],//GDT 路由无用户ID明细字段
    },
    "token": "",
    "unix_time": 1750822668
}
```

### API行为说明

- 注意：原始 BI API 可能会忽略无效指标；但在本项目的 MCP 服务中，工具层会预先校验指标，若包含无效指标将直接返回错误（INVALID_INDICATORS），以避免误用。

### 路由判断规则

接口根据`media`参数决定路由选择：
- 当`media`包含`"gdt"`或`"bd"`时 → 使用 GDT 路由（GetMaterialCountListFxGdt）
- 其他情况 → 使用 TT 路由（GetMaterialCountListFx）

### 重要业务逻辑规则

#### 1. 媒体自动设置
- 当未指定媒体(`media`)时，系统会根据内部业务规则自动设置：
  - 公司ID=2，产品ID=33 → 自动设置为["gdt"]
  - 公司ID=6，产品ID=12 → 自动设置为["tt"]
  - 公司ID=11，产品ID=34 → 自动设置为["zh"]

#### 2. 分组键与默认值
- TT 路由：当`group_key`为`"vp_originality_name"`或空时，统一转换为`"originality_names"`进行分组
- GDT/BD 路由：当`group_key`为空时，默认按`"vp_originality_name"`分组，不做上述转换

#### 3. 高级应用特殊处理（仅TT路由）
- 对于APP ID为`61`、`67`、`82`的应用，系统会自动添加质量相关指标：
  - 强制包含"新增付费成本"和"首日ROI"指标
  - **注意**：虽然代码中调用了优质广告判断逻辑（`CheckHighGradeAd`），但该判断依赖的`firstDayAllRoi`字段在GetMaterialCountList中不存在，因此优质广告状态判断功能实际无法正常工作
  - 若需要优质广告状态，建议使用GetAdCountList接口，该接口包含完整的`firstDayAllRoi`字段生成逻辑

#### 4. 收入分成计算
- iOS分成比例：默认79%，月收入≥100万时为85%
- Android分成比例：默认40%，月收入≥100万时为45%
- APP ID=59有特殊分成比例：iOS 80%，Android 40%

#### 5. 必需指标处理
- TT 路由：系统会自动确保"素材id"包含在指标列表中，如果未指定则自动添加到列表开头
- GDT/BD 路由：无此自动添加逻辑

#### 6. 素材返回条件说明

##### 6.1 基础返回条件
素材被返回到结果集中需要同时满足以下条件：

**用户行为关联要求：**
- 在查询时间范围内（`start_time` ~ `end_time`）有用户行为数据
- 用户行为包括：用户登录、用户注册、充值成功、用户创角
- 这些用户必须能通过用户表关联到素材信息

**数据完整性要求：**
- 有有效的用户追踪ID：`dt_vp_fx_cid != ''`
- 有有效的媒体渠道信息：`vp_advert_channame != ''`
- 有有效的素材ID：`vp_originality_id != ''`
- 数据记录有效：`_sign = 1`（未被逻辑删除）

**关键澄清：** 素材返回**主要基于用户行为，而非投放活动**。即使素材在查询时间范围内没有任何投放成本，只要有关联用户产生了行为（包括登录），素材就会出现在结果中。

**重要说明：** 素材返回**不要求任何指标大于0**。这就是为什么经常看到消耗=0但仍被返回的素材。

##### 6.2 数据来源结构
接口使用复杂的UNION ALL结构合并多个数据源：

**用户行为数据：**
- 用户注册、充值、登录事件（这些记录中cost强制设为0）
- 用户创角事件（cost强制设为0）

**投放成本数据：**
- 平台投放数据表（包含真实的cost值）

**聚合逻辑：**
- 最终按素材ID分组聚合所有相关记录
- 消耗 = SUM(所有买量成本事件的cost)
- 其他指标根据对应事件类型计算

##### 6.3 指标为0的典型场景

**场景1：纯用户行为记录**
- 素材关联到用户注册、充值行为
- 但在查询时间范围内没有投放数据
- 结果：消耗=0，但可能有用户转化数据

**场景2：投放无效果**
- 素材有投放成本记录
- 但没有产生任何用户行为（注册、充值等）
- 结果：消耗>0，但转化指标都是0

**场景3：时间范围错位**
- 素材的投放时间和用户行为时间不在同一查询范围内
- 结果：部分指标为0

**场景4：数据关联失败**
- LEFT JOIN可能关联不到完整的用户或素材标签数据
- 结果：部分展示字段为空或0

##### 6.4 自动排除规则
以下素材会被自动排除，不会出现在结果中：

**TT路由排除规则：**
- 素材名称包含"0R,g"的素材
- 素材名称包含"icon"的素材

**GDT路由排除规则：**
- 素材名称包含"副本"的素材
- 素材名称包含"icon"的素材

**数据完整性排除：**
- 素材文件缺失：`video_uris = '' AND img_uris = ''`
- 关键字段为空的记录

##### 6.5 容错机制
所有指标计算都包含防除0和防NaN处理：
```sql
-- 示例：首日ROI计算
if(isInfinite(if(isNaN(round(newPayMoney*100/cost,2)),0,round(newPayMoney*100/cost,2))),0,...)
```
这确保了即使数据异常也不会导致接口报错，异常值会被转换为0。

#### 7. GDT/BD 特殊行为
- 数据源：优先读取`component_data_gdt_{appid}`；当`is_old_table=true`或`media`包含`bd`时读取`platform_data_gdt_{appid}`
- 名称过滤：自动排除包含"副本"或"icon"的素材名
- BD 特判：当`media`包含`bd`时，以下指标固定为0：`首日ROI`、`累计ROI`、`新增付费金额`
- 过滤能力：GDT 支持 `component_id`、`creative_id`、`originality_types` 的精确 IN 过滤；`vp_originality_name` 支持模糊匹配（LIKE）。`is_inefficient_material`、`is_ad_low_quality_material` 等仅在 TT 路由生效

#### 8. 响应差异（TT vs GDT）
- TT 路由：
  - 可能返回`uiCols`（当`is_deep=true`时包含用户ID相关字段）
  - 返回`midAndScriptMap`（素材脚本映射信息）
- GDT/BD 路由：
  - `uiCols`恒为空
  - 不返回`midAndScriptMap`

#### 9. 累计ROI计算
- 仅当`zhibiao_list`包含"累计ROI"时触发计算
- 计算时间范围：从`start_time`到当前日期
- 同时返回`accumulativeROI`（累计ROI）和`divideAccumulativeROI`（分成后累计ROI）

#### 10. 素材类型映射（TT 路由）
- "视频" → 映射为["横版视频", "竖版视频"]
- "图片" → 映射为["大图横图", "大图竖图", "图文"]

#### 10.1 平台原始类型值
- TT 路由使用的平台原始类型值来源于`platform_data_{appid}_material_tag.originality_types`，TT 对外部传入的`["视频","图片"]`做内部映射为以下平台值：
  - 横版视频、竖版视频、大图横图、大图竖图、图文
- GDT/BD 路由直接使用数据表中的原始字段：
  - `component_data_gdt_{appid}.originality_type`（查询时作为`originality_types`使用）
  - 过滤条件为精确 IN 匹配：`originality_types in (...)`

源码依据（TT 路由内部映射）：

```318:backend-reference/GetMaterialCountList/GetMaterialCountListFx.go
        if util.InstrArr(reqData.Vp_originality_type, "视频") {
            tmp = append(tmp, "横版视频")
            tmp = append(tmp, "竖版视频")
        }
        if util.InstrArr(reqData.Vp_originality_type, "图片") {
            tmp = append(tmp, "大图横图")
            tmp = append(tmp, "大图竖图")
            tmp = append(tmp, "图文")
        }
```

源码依据（GDT 路由字段与过滤）：

```395:backend-reference/GetMaterialCountList/GetMaterialCountListFxGdt.go
 ,advert_media_name as vp_advert_channame,originality_type as originality_types,* FROM fx_bi_user_2.` + tableName + ` final
```

```85:backend-reference/GetMaterialCountList/GetMaterialCountListFxGdt.go
 if len(reqData.Vp_originality_type) > 0 {
     where = where + " and originality_types in (" + parseFn(reqData.Vp_originality_type) + ") "
 }
```

#### 11. GroupKey字段处理机制

当使用`group_key`参数分组时，返回结果中的`groupKey`字段会经过以下处理：

##### 11.1 字段别名设置（以源码为准）
- TT 路由：始终返回`groupKeyAlias = "groupKey"`
  - 原因：当`group_key`为空或为`vp_originality_name`，会强制改为`originality_names`，并在SQL中使用`... as groupKey`（源码：`GetMaterialCountListFx.go` 54-58, 564-571）。
- GDT/BD 路由：
  - 当`group_key`为空（默认按`vp_originality_name`分组）时，返回`groupKeyAlias = "vp_originality_name"`（源码：`GetMaterialCountListFxGdt.go` 319-325）。
  - 当传入自定义`group_key`时，统一使用`... as groupKey`并返回`groupKeyAlias = "groupKey"`（源码：`GetMaterialCountListFxGdt.go` 325-333）。

##### 11.2 汇总行处理
- 当分组字段值为空时（SQL `WITH ROLLUP`产生的汇总行）
- 系统自动将该行的`groupKey`字段设置为`"总计"`

##### 11.3 投手ID映射
- **触发条件**：当字段名为`"groupKey"`且按投手分组时
- **映射逻辑**：通过内部配置将投手ID自动转换为投手姓名
- **示例**：`"123"` → `"张三"`

##### 11.4 PropMap动态调整
- **TT 路由**：当`group_key="originality_names"`时，设置`propMap["素材名称"] = "groupKey"`
- **GDT 路由**：当`group_key="vp_originality_name"`时，设置`propMap["素材名称"] = "groupKey"`
- 这样前端可通过propMap找到分组字段对应的中文名称

##### 11.5 实际应用示例

**示例1：按投手分组**
```json
// 请求
{"group_key": "vp_advert_pitcher_id"}

// 返回数据片段
{
  "data": {
    "list": [
      {"groupKey": "张三", "消耗": 1000, ...},
      {"groupKey": "李四", "消耗": 800, ...},
      {"groupKey": "总计", "消耗": 1800, ...}
    ],
    "groupKeyAlias": "groupKey"
  }
}
```

**示例2：按素材名称分组（TT路由）**
```json
// 请求
{"group_key": "originality_names"}

// 返回数据片段
{
  "data": {
    "propMap": {
      "素材名称": "groupKey",
      ...
    },
    "groupKeyAlias": "groupKey"
  }
}
```

### 补充
+ 参数<span style="color:red">zhibiao_list</span>可选值有（按功能分类）：
  + **基础指标**
    + `新增注册`
    + `新增创角`
    + `创角率`
    + `活跃用户`
    + `注册成本`
    + `创角成本`
  + **付费指标**
    + `当日充值`
    + `当日充值人数`
    + `当日付费次数`
    + `新增付费人数`
    + `新增付费金额`
    + `新增付费率`
    + `新增付费成本`
    + `新增arppu`
    + `首充付费人数`
    + `首充付费次数`
    + `首充付费金额`
    + `付费成本`
    + `活跃付费率`
    + `活跃arppu`
  + **ROI指标**
    + `首日ROI`
    + `累计ROI`
    + `分成后首日ROI`
    + `分成后累计ROI`
    + `分成后收入`
  + **广告效果指标**
    + `消耗`
    + `点击率`
    + `激活率`
    + `点击成本`
  + **素材质量指标**
    + `3秒播放率`
    + `完播率`
    + `是否低效素材`（TT 路由专用）
    + `是否AD优质素材`（TT 路由专用）
    + `是否AD低质素材`（TT 路由专用）
    + `低质原因`（TT 路由专用）
  + **素材信息**
    + `素材id`
    + `素材名称`
    + `素材类型`
    + `素材封面uri`
    + `制作人`
    + `创意人`
    + `素材创造时间`
  + **GDT/BD专用指标**
    + `广告变现人数`
    + `小游戏广告变现金额（平台上报）`
    + `当前注册用户24小时广告变现金额`
    + `小游戏注册首日广告变现ROI`
    + `广告变现成本`
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
    + `vp_originality_id`(创意id)
    + `vp_originality_name`(素材名称)
    + `originality_names`(素材名称，TT 默认分组字段)

### POSTMAN示例
![alt text](image.png)
