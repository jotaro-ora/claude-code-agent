# BTC MACD 策略回测分析

## 项目概述

本项目对比特币过去3年进行MACD金叉死叉策略回测分析，评估该策略的收益率和风险表现。

## 策略说明

### 交易规则
- **买入信号**: MACD线从下方穿越信号线（金叉）
- **卖出信号**: MACD线从上方穿越信号线（死叉）
- **仓位管理**: 全仓买入/卖出

### MACD参数
- 快线EMA周期: 12天
- 慢线EMA周期: 26天  
- 信号线EMA周期: 9天

## 回测结果

### 核心指标 (2022-06-26 至 2025-06-24)

| 指标 | 数值 |
|-----|------|
| **策略总收益率** | +104.26% |
| **买入持有收益率** | +392.15% |
| **Alpha (超额收益)** | -287.88% |
| **年化收益率** | +26.93% |
| **最大回撤** | -31.28% |
| **夏普比率** | 0.83 |
| **胜率** | 34.9% |
| **总交易次数** | 86次 |

### 资金变化
- **初始资金**: $10,000
- **最终价值**: $20,426.47
- **绝对盈亏**: +$10,426.47

### 信号统计
- **金叉信号**: 43次
- **死叉信号**: 43次
- **分析周期**: 1,094天 (约3年)

## 策略评价

### ❌ 主要劣势
1. **严重跑输买入持有**: 策略收益率(104.26%)远低于简单买入持有(392.15%)，落后287.88%
2. **胜率偏低**: 仅34.9%的交易盈利，说明大部分交易都是亏损的
3. **交易频繁**: 86次交易产生大量手续费成本（未计入回测）
4. **错失主要涨幅**: 在比特币大涨期间可能处于空仓状态

### ⚠️ 风险特征
1. **最大回撤适中**: -31.28%的回撤在可接受范围内
2. **夏普比率一般**: 0.83表示风险调整后收益一般
3. **波动较大**: 频繁交易增加了组合波动性

## 结论

**MACD金叉死叉策略在比特币市场表现不佳**:

1. **收益率**: 虽然实现了104.26%的正收益，但远低于买入持有策略
2. **效率**: 频繁交易(86次)并未带来超额收益
3. **适用性**: 该策略可能更适合震荡市，而非单边上涨行情

## 投资启示

1. **简单有效**: 在比特币这样的高成长资产中，简单的买入持有往往优于复杂的技术分析策略
2. **交易成本**: 频繁交易的成本（手续费、滑点）会进一步降低策略收益
3. **市场特性**: 比特币具有强趋势性，技术指标的滞后性导致错失大部分涨幅
4. **策略局限**: MACD适合震荡行情，不适合单边趋势市场

## 文件结构

```
btc-macd-backtest/
├── README.md                    # 项目说明文档
└── src/
    └── macd_backtest.py        # 主回测程序
```

## 使用方法

### 基本运行 (使用默认参数)
```bash
cd btc-macd-backtest
source ../venv/bin/activate
python src/macd_backtest.py
```

### 命令行参数配置
```bash
# 查看所有可用参数
python src/macd_backtest.py --help

# 自定义参数运行示例
python src/macd_backtest.py --days 730 --capital 20000 --fast-period 10 --slow-period 30

# 分析其他币种 (以太坊为例)
python src/macd_backtest.py --coin ethereum --days 1095 --capital 10000

# 快速测试 (1年数据)
python src/macd_backtest.py --days 365 --capital 5000
```

### 可配置参数
| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `--days` | int | 1095 | 回测天数 (约3年) |
| `--fast-period` | int | 12 | MACD快线EMA周期 |
| `--slow-period` | int | 26 | MACD慢线EMA周期 |
| `--signal-period` | int | 9 | MACD信号线EMA周期 |
| `--capital` | float | 10000.0 | 初始资金 (USD) |
| `--coin` | str | bitcoin | 币种ID (bitcoin, ethereum, cardano等) |

### 参数使用示例

**1. 测试不同MACD参数**
```bash
# 保守参数 (慢速交易)
python src/macd_backtest.py --fast-period 8 --slow-period 35 --signal-period 12

# 激进参数 (快速交易)
python src/macd_backtest.py --fast-period 15 --slow-period 20 --signal-period 5
```

**2. 测试不同时间周期**
```bash
# 1年回测
python src/macd_backtest.py --days 365

# 2年回测
python src/macd_backtest.py --days 730

# 5年回测
python src/macd_backtest.py --days 1825
```

**3. 测试不同币种**
```bash
# 以太坊
python src/macd_backtest.py --coin ethereum

# 卡尔达诺
python src/macd_backtest.py --coin cardano

# 索拉纳
python src/macd_backtest.py --coin solana
```

**4. 组合参数测试**
```bash
# 以太坊2年回测，5万美金初始资金
python src/macd_backtest.py --coin ethereum --days 730 --capital 50000 --fast-period 10 --slow-period 30
```

## 依赖项

- pandas: 数据处理
- numpy: 数值计算
- CoinGecko API: 历史价格数据

## 风险提示

⚠️ **重要声明**:
- 本回测结果仅供学习研究，不构成投资建议
- 历史表现不代表未来收益
- 加密货币投资存在极高风险，可能导致本金全部损失
- 实际交易还需考虑手续费、滑点、流动性等因素
- 投资前请咨询专业财务顾问

## 潜在改进方向

1. **止损机制**: 增加止损条件减少大幅亏损
2. **仓位管理**: 采用分批建仓而非全仓操作
3. **多指标确认**: 结合其他技术指标过滤信号
4. **市场环境识别**: 在不同市场状态使用不同策略
5. **动态参数**: 根据市场波动性调整MACD参数