# GetOrderList API文档

## 接口地址
```uri
https://bi.dartou.com/testapi/ad/GetOrderList
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

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | ------ | --- | --- | -------- |
| appid | String | 是 | - | 游戏ID |
| start_time | String | 是 | - | 查询范围开始时间，格式：`YYYY-MM-DD` 或 8位格式 |
| end_time | String | 是 | - | 查询范围结束时间，格式：`YYYY-MM-DD` |
| page | Integer | 否 | 1 | 页码，0时自动设为1 |
| limit | Integer | 否 | 20 | 每页数量，0时自动设为20 |
| order_by_type | String | 否 | " asc " | 排序方式，空时自动设为" asc " |
| order_by_col | String | 否 | - | 排序字段 |
| type | Integer | 否 | 0 | 查询类型：0=充值订单，1=注册数据，2=创角数据，3=用户信息 |
| open_id | String | 否 | - | 直接指定用户ID |
| ui | String | 否 | - | UI Token，用于获取用户ID列表 |
| is_excel | Boolean | 否 | false | 是否导出Excel |

## 查询类型说明

### Type 0 (默认) - 充值订单数据
查询用户充值成功事件，包含：
- 订单详情（订单ID、商品信息、金额）
- 支付系统信息
- 用户地理位置信息
- 当日总充值金额
- 历史总充值金额

### Type 1 - 注册数据
查询用户注册事件，包含：
- 注册时间和地理位置
- 广告投放相关信息（fx_cid、媒体、投手）

### Type 2 - 创角数据
查询用户创角事件，包含：
- 创角时间和地理位置
- 角色相关信息
- 服务器信息

### Type 3 - 用户信息
直接查询用户基础信息，包含：
- 用户注册信息
- 完整的广告投放链路信息

## 请求示例
```json
{
    "appid": "59",
    "start_time": "2025-01-01",
    "end_time": "2025-01-01",
    "page": 1,
    "limit": 20,
    "order_by_type": " asc ",
    "type": 0,
    "ui": "your_ui_token",
    "is_excel": false
}
```

## 响应格式

### 标准响应
```json
{
    "code": 0,
    "msg": "查询成功",
    "data": {
        "list": [],  // 数据列表
        "count": 100, // 总条数
        "propMap": {} // 字段映射
    },
    "token": "",
    "unix_time": 1750822668
}
```

### Excel导出响应
当`is_excel=true`时，直接返回Excel文件流：
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Content-Disposition: `attachment; filename=用户下探数据.xlsx`

## 字段映射说明

### Type 0 - 充值订单字段映射
```json
{
    "channame": "媒体",
    "device": "机型",
    "dt_distinct_id": "openid",
    "dt_part_date": "时间",
    "dt_province": "省",
    "dt_city": "市",
    "game_version": "游戏版本号",
    "goods_id": "商品id",
    "goods_name": "商品名",
    "money": "充值金额",
    "orderid": "订单id",
    "pay_system": "支付系统",
    "role_id": "角色id",
    "role_level": "角色等级",
    "role_name": "角色名",
    "server_id": "服务器id",
    "server_name": "服务器名",
    "is_first_reg": "是否当天注册",
    "dt_ip": "IP",
    "reg_time": "注册时间",
    "sum_money": "当天总充值金额",
    "sum_money_all": "总生命周期充值金额"
}
```

### Type 1 - 注册数据字段映射
```json
{
    "channame": "媒体",
    "online_time": "在线时间",
    "dt_id": "openid",
    "dt_part_date2": "时间",
    "fx_cid": "fx_cid",
    "advert_media_name2": "平台",
    "advert_pitchers_id2": "投手",
    "dt_province2": "省",
    "dt_city2": "市",
    "dt_ip2": "IP",
    "reg_time": "注册时间"
}
```

### Type 2 - 创角数据字段映射
```json
{
    "channame": "媒体",
    "dt_distinct_id": "openid",
    "dt_part_date": "时间",
    "dt_province": "省",
    "dt_city": "市",
    "game_version": "游戏版本号",
    "role_id": "角色id",
    "role_level": "角色等级",
    "role_name": "角色名",
    "server_id": "服务器id",
    "server_name": "服务器名",
    "dt_ip": "IP",
    "reg_time": "注册时间"
}
```

### Type 3 - 用户信息字段映射
```json
{
    "channame": "媒体",
    "dt_distinct_id": "openid",
    "register_time": "注册时间",
    "fx_cid": "fx_cid",
    "advert_channame": "平台",
    "advert_pitcher_id": "投手",
    "dt_province": "省",
    "dt_city": "市",
    "campaign_id": "广告id",
    "dt_ip": "IP",
    "originality_id": "素材id"
}
```

## 数据处理规则

### 支付系统编码转换
- "1" → "IOS"
- "2" → "安卓"
- 其他值 → "未知"

### 首次注册标识转换
- "1" → "是"
- 其他值 → "否"

### 特殊处理规则

#### 在线时间查询
仅当`appid`为"48"或"62"时，系统会：
1. 调用外部接口获取用户在线时间
2. 将秒数转换为分钟数
3. 添加`online_time`字段到响应中

#### 时间格式处理
- 当`start_time`长度为8位时，会添加"0100:00:00"后缀
- 当`start_time`长度为8位时，`endFilterWhere`设置为"and (1 = 1)"
- 其他情况下，时间范围为"00:00:00"到"23:59:59"

#### 媒体渠道名称映射
系统会通过配置映射表(`k2vMap`)对渠道名称进行转换。

## 性能特性

### 并发处理
- 默认并发协程数：50
- Excel导出时并发数：10
- 使用信号量控制并发数量，防止系统过载

### 分页机制
- 先执行count查询获取总数
- 再执行limit查询获取具体数据
- Excel导出时不使用分页，返回全量数据

## 用户数据获取机制

### 优先级顺序
1. 如果`open_id`不为空，直接使用该用户ID
2. 否则使用`ui` Token从缓存中获取用户ID列表

这种设计保护了用户隐私，避免直接在请求中传递用户ID列表。
