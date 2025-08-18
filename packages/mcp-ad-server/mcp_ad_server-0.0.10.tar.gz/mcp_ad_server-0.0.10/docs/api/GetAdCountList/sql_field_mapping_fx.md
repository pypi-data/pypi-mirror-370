# GetAdCountList SQL字段映射分析（FX系统-非棋牌游戏）

## 概述
基于后端Go代码实际实现，详细分析FX系统（非棋牌游戏）的API指标与SQL字段映射关系及业务规则。

**适用范围**: 非棋牌游戏（游戏ID: 59, 61, 65, 67, 68, 69, 72, 73, 74, 75, 78, 80, 81, 82等）
**数据系统**: FX系统（local_dt_event, local_dt_user, platform_data等表）

## 核心指标SQL映射

### 基础用户行为指标
| API指标名称 | SQL字段名 | 计算逻辑 | 说明 |
|-------------|-----------|----------|------|
| 新增注册 | regUserCount | `uniqExact(if(dt_part_event = '用户注册', dt_distinct_id, NULL))` | 新注册用户去重数量 |
| 新增创角 | regRoleCount | `uniqExact(if(dt_part_event = '用户创角', dt_distinct_id, NULL))` | 新创角用户去重数量 |
| 消耗 | cost | `round(sum(cost), 2)` | 广告投放总成本 |
| 曝光次数 | view_count | `sum(show_cnt)` | 广告曝光次数 |

### 付费相关基础指标
| API指标名称 | SQL字段名 | 计算逻辑 | 说明 |
|-------------|-----------|----------|------|
| 付费金额 | payMoney | `round(sum(if(dt_part_event = '充值成功', money, 0)), 2)` | 总付费金额 |
| 付费次数 | payCount | `sum(if(dt_part_event = '充值成功', 1, 0))` | 总付费次数 |
| 付费人数 | payUser | `uniqExact(if(dt_part_event = '充值成功', dt_distinct_id, NULL))` | 付费用户去重数量 |
| 新增付费人数 | newPayUser | `uniqExact(if((dt_part_event = '充值成功') AND (is_first_pay = 1) AND (is_first_reg = 1), dt_distinct_id, NULL))` | 新注册且首次付费用户 |
| 新增付费金额 | newPayMoney | `sum(if((dt_part_event = '充值成功') AND (is_first_reg = 1) AND (is_first_pay2 = 1), money, 0))` | 新注册用户的付费金额 |
| 首充付费金额 | accumulatedFirstPayMoney | `sum(if((dt_part_event = '充值成功') AND (is_first_pay2 = 1), money, 0))` | 用户首次付费金额汇总 |

### 广告变现指标
| API指标名称 | SQL字段名 | 计算逻辑 | 数据来源 |
|-------------|-----------|----------|----------|
| 小游戏广告变现金额 | adBuyMoney | `round(sum(if(income_val_24h != 0, income_val_24h, 0)), 2)` | platform_data_{appid}表 |
| 广告变现人数 | adBuyUsers | `sum(if(mini_game_ad_monetization_users != 0, mini_game_ad_monetization_users, 0))` | 参与广告变现用户数 |

## 平台分成计算规则

### 支付系统编码标准
| 平台 | 标准编码 | 游戏73特殊编码 | 说明 |
|------|----------|----------------|------|
| Android | pay_system = 1 | pay_system = 11 | 安卓平台 |
| iOS | pay_system = 2 | pay_system = 19 | 苹果平台 |
| 支付宝 | pay_system = 12 | pay_system = 12 | 支付宝直接支付 |

### 游戏分成比例矩阵

#### 固定分成游戏
| 游戏ID | Android分成比例 | iOS分成比例 | 特殊说明 |
|--------|----------------|-------------|----------|
| 59 | 40% | 80% | 标准比例 |
| 73 | 75% | 84% | 使用特殊pay_system编码 |
| 65 | 60% | 99% | 高iOS分成 |
| 78 | 45% | 84% | 标准偏高比例 |

#### 动态分成游戏（基于月充值金额）

**游戏61/67/82系列**：
```sql
-- 月充值判断逻辑
SELECT sum(money) FROM local_dt_event{appid}_view
WHERE dt_part_event = '充值成功' AND toYYYYMM(dt_part_date) = {当前月份}

-- 分成规则
IF 月充值 < 100万元:
  Android: 40%, iOS: 79%
ELSE IF 月充值 >= 100万元:
  Android: 45%, iOS: 85%
```

**游戏68**：
```sql
-- 分成规则
IF 月充值 < 600万元:
  Android: 45%, iOS: 84%
ELSE IF 月充值 >= 600万元:
  Android: 46%, iOS: 85%
```

**游戏74（零件游戏）**：
```sql
-- 根据LingJianCpxMoneyFlag标志位控制
IF flag = false:
  Android: 48%, iOS: 87%
ELSE IF flag = true:
  Android: 50%, iOS: 89%
```

### 支付宝分成特殊计算

对于支付宝支付（pay_system = 12），采用特殊手续费扣除逻辑：
```sql
-- 支付宝分成后金额计算
newZfbPayMoney = if(money_zfb == 0,
                   money_zfb,
                   money_zfb - (money_zfb / 0.95 * 0.15))

-- 说明：扣除支付宝手续费约15.79%（先除以0.95再乘以0.15）
```

### 分成后收入组合计算

根据游戏类型采用不同的组合公式：

**标准游戏（59, 65, 74, 78等）**：
```sql
newDividePayMoney = newIosPayMoney + newAndroidPayMoney
```

**支持支付宝的游戏（61, 73等）**：
```sql
newDividePayMoney = newIosPayMoney + newAndroidPayMoney + newZfbPayMoney
```

**游戏73特殊处理**：
```sql
-- 额外的大象渠道分成
money_dx_android = sum(if(pay_system = 19, money, 0)) * 0.75
money_dx_ios = sum(if(pay_system = 11, money, 0)) * 0.84

newDividePayMoney = newIosPayMoney + newAndroidPayMoney + newZfbPayMoney +
                   money_dx_android + money_dx_ios
```

## 数据源架构（FX系统）

### 核心数据表结构
```sql
-- 用户事件表
local_dt_event{appid}_view:
  - dt_distinct_id: 用户唯一标识
  - dt_part_event: 事件类型（'用户注册'/'用户创角'/'充值成功'等）
  - dt_part_date: 事件时间
  - money: 充值金额
  - pay_system: 支付系统编码（1=Android, 2=iOS, 12=支付宝, 游戏73特殊：11=Android, 19=iOS）
  - is_first_pay: 用户维度首付标识
  - is_first_pay2: 订单维度首付标识
  - is_first_reg: 当日注册标识

-- 用户基础信息表
local_dt_user{appid}:
  - dt_distinct_id: 用户标识
  - fx_cid: 投放标识符
  - campaign_id: 广告计划ID
  - originality_id: 创意ID
  - dt_register_time: 注册时间
  - channel: 游戏特定渠道编码（见FxGameAttrMap配置）

-- 平台广告数据表
platform_data_{appid}:
  - fx_cid: 投放标识符
  - cost: 广告消耗
  - show_cnt: 曝光次数
  - click_num: 点击次数
  - income_val_24h: 24小时广告收入
  - mini_game_ad_monetization_users: 广告变现用户数
  - mini_game_ad_monetization_amount: 广告变现金额

-- 按小时统计表（24小时模式）
platform_data_hour_{appid}:
  - 与platform_data_{appid}结构相同
  - 按小时粒度统计数据
```

### 游戏配置映射
```go
// FxGameAttrMap - 非棋牌游戏配置
var FxGameAttrMap = map[string]FxGameAttr{
    "59": {Channel: 100004},   // 游戏59特定渠道
    "61": {Channel: 100014},   // 游戏61特定渠道
    "65": {Channel: 100144},   // 游戏65特定渠道
    "73": {Channel: 100304},   // 游戏73特定渠道
    // ... 其他非棋牌游戏
}
```

## 关键业务逻辑

### 目标用户识别
```sql
WHERE (fx_cid IS NOT NULL) AND (channel IN (100004))
```
- **channel = 100004**: 游戏59的特定渠道编码（不同游戏有不同channel值）
- **fx_cid IS NOT NULL**: 有投放标识符的用户

### 新老用户判断
```sql
-- 新用户（当日注册）
is_first_reg = (toYYYYMMDD(dt_register_time) = date)

-- 老用户（历史注册）
is_old_user = (toYYYYMMDD(dt_register_time) < date)
```

### 首付标识说明
- **is_first_pay**: 用户维度，该用户是否首次付费
- **is_first_pay2**: 订单维度，该笔订单是否为首付订单

### ROI计算公式
```sql
-- 首日ROI
firstDayROI = concat(cast(round(newPayMoney * 100 / cost, 2), 'String'), '%')

-- 分成后首日ROI
dividefirstDayROI = concat(cast(round(newDividePayMoney * 100 / cost, 2), 'String'), '%')

-- 累计ROI
accumulativeROI = concat(cast(round(accumulatedPayMoney * 100 / cost, 2), 'String'), '%')
```

## 时间处理

### 事件时间筛选
```sql
WHERE (dt_part_date >= '{startTime} 00:00:00')
  AND (dt_part_date <= '{endTime} 23:59:59')
```

### 数据聚合策略
```sql
GROUP BY Date WITH ROLLUP
```
- **Date**: 按日期分组
- **WITH ROLLUP**: 自动生成汇总行

## 系统特性说明

### FX系统特点
| 特性 | 说明 | 备注 |
|------|------|------|
| 适用游戏 | 非棋牌游戏 | 游戏ID: 59, 61, 65, 67, 68, 69, 72, 73, 74, 75, 78, 80, 81, 82 |
| 数据表命名 | local_dt_前缀 | local_dt_event{appid}_view, local_dt_user{appid} |
| 字段命名 | 原生字段名 | money, pay_system, fx_cid等 |
| 分成计算 | 实时动态计算 | 基于游戏ID和月充值金额的复杂分成规则 |
| 渠道管理 | Channel字段 | 每个游戏有特定的channel编码 |

这个映射文档基于后端实际代码逻辑，准确反映了各游戏的分成规则、支付系统编码、以及特殊业务逻辑的实现方式。
