# GetAdCountList SQL字段映射分析（BI系统-棋牌游戏）

## 概述
基于后端Go代码实际实现，详细分析BI系统（棋牌游戏）的API指标与SQL字段映射关系及业务规则。

**适用范围**: 棋牌游戏（游戏ID: 48, 57, 62等）
**数据系统**: BI系统（使用vp_前缀字段，pfids标识符）
**核心特征**: 通过 `is_wangyou = 1` 标识棋牌游戏数据

## 核心指标SQL映射

### 基础用户行为指标
| API指标名称 | SQL字段名 | 计算逻辑 | 说明 |
|-------------|-----------|----------|------|
| 新增注册 | regUserCount | `uniqExact(if(dt_part_event = '用户注册', dt_distinct_id, NULL))` | 新注册用户去重数量 |
| 新增创角 | regRoleCount | `0 as regRoleCount` | 棋牌游戏无创角概念，固定为0 |
| 消耗 | cost | `round(sum(cost), 2)` | 广告投放总成本 |
| 曝光次数 | view_count | `sum(show_cnt)` | 广告曝光次数 |

### 付费相关基础指标
| API指标名称 | SQL字段名 | 计算逻辑 | 说明 |
|-------------|-----------|----------|------|
| 付费金额 | payMoney | `round(sum(if(is_wangyou = 0, price, 0)), 2)` | 非棋牌游戏付费金额 |
| 平台当日充值 | pf_payMoney | `round(sum(if(is_wangyou = 1, price, 0)), 2)` | 棋牌游戏付费金额 |
| 付费次数 | payCount | `sum(if(dt_part_event = '充值成功' and is_wangyou = 0, 1, 0))` | 非棋牌付费次数 |
| 平台当日付费次数 | pf_payCount | `sum(if(dt_part_event = '充值成功' and is_wangyou = 1, 1, 0))` | 棋牌付费次数 |
| 付费人数 | payUser | `uniqExact(if(dt_part_event = '充值成功' and is_wangyou = 0, dt_distinct_id, NULL))` | 非棋牌付费用户数 |
| 平台当日充值人数 | pf_payUser | `uniqExact(if(dt_part_event = '充值成功' and is_wangyou = 1, dt_distinct_id, NULL))` | 棋牌付费用户数 |
| 新增付费人数 | newPayUser | `uniqExact(if(is_wangyou = 0 and is_first_reg2 = 1 and is_first_pay2 = 1, dt_distinct_id, NULL))` | 新注册非棋牌付费用户 |
| 平台新增付费人数 | pf_newPayUser | `uniqExact(if(is_first_reg2 = 1 and is_first_pay2 = 1, dt_distinct_id, NULL))` | 新注册棋牌付费用户 |
| 新增付费金额 | newPayMoney | `sum(if(is_wangyou = 0 and is_first_reg2 = 1 and is_first_pay2 = 1, price, 0))` | 新注册非棋牌付费金额 |
| 平台新增付费金额 | pf_newPayMoney | `sum(if(is_first_reg2 = 1 and is_first_pay2 = 1, price, 0))` | 新注册棋牌付费金额 |
| 首充付费金额 | accumulatedPayMoney | `sum(if(is_wangyou = 0 and is_first_pay2 = 1, price, 0))` | 首次付费金额汇总 |

### 广告变现指标
| API指标名称 | SQL字段名 | 计算逻辑 | 数据来源 |
|-------------|-----------|----------|----------|
| 小游戏广告变现金额 | adBuyMoney | `round(sum(if(income_val_24h != 0, income_val_24h, 0)), 2)` | platform_data表 |
| 广告变现人数 | adBuyUsers | `sum(if(mini_game_ad_monetization_users != 0, mini_game_ad_monetization_users, 0))` | 参与广告变现用户数 |

## 平台分成计算规则

### 支付系统编码标准
| 平台 | BI系统编码 | 说明 |
|------|------------|------|
| Android | vp_pay_system = '2' | 安卓平台 |
| iOS | vp_pay_system = '1' | 苹果平台 |

### 棋牌游戏固定分成比例
| 游戏类型 | Android分成比例 | iOS分成比例 | 计算方式 |
|----------|----------------|-------------|----------|
| 棋牌游戏 | 60% | 99% | 固定比例，相对简单 |

### 分成后收入计算

**BI系统固定分成公式**：
```sql
-- iOS分成收入
newIosPayMoney = sum(if(is_wangyou = 0 and gameid = {appid} and vp_pay_system = '1' and is_first_reg2 = 1 and is_first_pay2 = 1, price, 0)) * 0.99

-- Android分成收入
newAndroidPayMoney = sum(if(is_wangyou = 0 and gameid = {appid} and vp_pay_system = '2' and is_first_reg2 = 1 and is_first_pay2 = 1, price, 0)) * 0.6

-- 总分成收入
newDividePayMoney = newIosPayMoney + newAndroidPayMoney
```

**平台分成收入（多游戏）**：
```sql
-- 为每个棋牌游戏单独计算分成
sum(if(is_first_reg2 = 1 and gameid = {appid} and vp_pay_system = '1' and is_first_pay2 = 1 and is_wangyou = 1, price, 0)) * {iosDivScale}
sum(if(is_first_reg2 = 1 and gameid = {appid} and vp_pay_system = '2' and is_first_pay2 = 1 and is_wangyou = 1, price, 0)) * {androidDivScale}
```

## 数据源架构（BI系统）

### 核心数据表结构
```sql
-- 用户事件表（使用相同的local_dt_event表，但字段处理不同）
local_dt_event{appid}_view:
  - dt_distinct_id: 用户唯一标识
  - dt_part_event: 事件类型（'用户注册'/'充值成功'等）
  - dt_part_date: 事件时间
  - price: 充值金额（BI系统字段名）
  - pay_system: 支付系统编码（映射为vp_pay_system）
  - is_first_pay2: 首付标识
  - is_first_reg2: 新注册标识
  - is_wangyou: 网游标识（0=非棋牌, 1=棋牌）

-- 用户基础信息表
local_dt_user{appid}:
  - dt_distinct_id: 用户标识
  - fx_cid: 投放标识符（映射为dt_vp_fx_cid）
  - campaign_id: 广告计划ID
  - originality_id: 创意ID
  - register_time: 注册时间
  - pfids: 棋牌游戏特定标识符（见BIGameAttrMap配置）

-- 平台广告数据表
platform_data_表:
  - cost: 广告消耗
  - show_cnt: 曝光次数
  - click_num: 点击次数
  - income_val_24h: 24小时广告收入
  - mini_game_ad_monetization_amount: 广告变现金额
```

### 棋牌游戏配置映射
```go
// BIGameAttrMap - 棋牌游戏配置
var BIGameAttrMap = map[string]BIGameAttr{
    "48": {Pfids: []int{7512, 7511}},   // 棋牌游戏48的pfids
    "57": {Pfids: []int{7342, 7341}},   // 棋牌游戏57的pfids
    "62": {Pfids: []int{7752, 7751}},   // 棋牌游戏62的pfids
}

// Pfids筛选逻辑
func GetPfidsWhere(appid string) string {
    return "(pfids = " + BIGameAttrMap[appid].Pfids[0] + " or pfids = " + BIGameAttrMap[appid].Pfids[1] + ")"
}
```

## 关键业务逻辑

### 用户识别筛选
```sql
-- 棋牌游戏用户筛选
WHERE dt_vp_fx_cid IS NOT NULL OR {GetPfidsWhere(appid)}
```

### 数据类型区分
```sql
-- is_wangyou字段含义
is_wangyou = 0: 非棋牌游戏数据
is_wangyou = 1: 棋牌游戏数据
```

### 字段映射处理
```sql
-- BI系统的字段映射逻辑
vp_pay_system = if(t1.pay_system=='0', t2.pay_system, t1.pay_system)
gameid = {appid}
price (instead of money)
pfids (instead of channel)
```

## ROI计算公式

### 首日ROI
```sql
-- 首日ROI计算
firstDayRoi = concat(toString(if(cost==0, 0, round(newPayMoney*100/cost, 2))), '%')

-- 分成后首日ROI
dividefirstDayRoi = concat(toString(if(cost==0, 0, round(newDividePayMoney*100/cost, 2))), '%')
```

### 累计ROI
```sql
-- 累计ROI
accumulativeROI = concat(cast(if(isInfinite(if(isNaN(round(accumulatedPayMoney*100/cost, 2)), 0, round(accumulatedPayMoney*100/cost, 2))), 0, if(isNaN(round(accumulatedPayMoney*100/cost, 2)), 0, round(accumulatedPayMoney*100/cost, 2))), 'String'), '%')

-- 分成后累计ROI
divideAccumulativeROI = concat(cast(if(isInfinite(if(isNaN(round(divideAccumulatedPayMoney*100/cost, 2)), 0, round(divideAccumulatedPayMoney*100/cost, 2))), 0, if(isNaN(round(divideAccumulatedPayMoney*100/cost, 2)), 0, round(divideAccumulatedPayMoney*100/cost, 2))), 'String'), '%')
```

## 系统特性说明

### BI系统特点
| 特性 | 说明 | 备注 |
|------|------|------|
| 适用游戏 | 棋牌游戏 | 游戏ID: 48, 57, 62等 |
| 数据标识 | is_wangyou字段（应该是网游？） | 1=棋牌, 0=非棋牌 |
| 字段前缀 | vp_前缀 | vp_pay_system, dt_vp_fx_cid等 |
| 分成计算 | 固定比例 | iOS 99%, Android 60% |
| 渠道管理 | Pfids字段 | 每个棋牌游戏有特定的pfids数组 |
| 创角逻辑 | 无创角概念 | regRoleCount固定为0 |

### 与FX系统的主要差异
| 差异项 | BI系统（棋牌） | FX系统（非棋牌） |
|--------|----------------|------------------|
| 游戏类型 | 棋牌游戏 | 非棋牌游戏 |
| 充值字段 | price | money |
| 支付编码 | vp_pay_system | pay_system |
| 渠道标识 | pfids | channel |
| 分成规则 | 固定比例 | 动态分成 |
| 数据标识 | is_wangyou=1 | is_wangyou=0 |

这个映射文档专门针对BI系统（棋牌游戏），与FX系统文档完全分离，避免混淆。
