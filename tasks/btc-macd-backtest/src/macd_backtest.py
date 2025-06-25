#!/usr/bin/env python3
"""
BTC MACD 回测分析器

对比特币过去3年进行MACD金叉死叉策略回测:
- MACD金叉时买入
- MACD死叉时卖出
- 计算总收益率和策略表现

可配置参数:
- fast_period: MACD快线周期 (默认12)
- slow_period: MACD慢线周期 (默认26) 
- signal_period: 信号线周期 (默认9)
- initial_capital: 初始资金 (默认10000 USD)
"""

import sys
import os
import pandas as pd
import numpy as np
import argparse
from datetime import datetime, timedelta

# 添加项目路径以导入工具
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from tools.coin_historical_chart_by_id import get_coin_historical_chart_by_id


def calculate_macd(prices: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> dict:
    """
    计算MACD指标
    
    Args:
        prices: 价格序列
        fast_period: 快线EMA周期
        slow_period: 慢线EMA周期
        signal_period: 信号线EMA周期
        
    Returns:
        包含MACD线、信号线和柱状图的字典
    """
    # 计算快线和慢线EMA
    ema_fast = prices.ewm(span=fast_period).mean()
    ema_slow = prices.ewm(span=slow_period).mean()
    
    # MACD线 = 快线EMA - 慢线EMA
    macd_line = ema_fast - ema_slow
    
    # 信号线 = MACD线的EMA
    signal_line = macd_line.ewm(span=signal_period).mean()
    
    # MACD柱状图 = MACD线 - 信号线
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram,
        'ema_fast': ema_fast,
        'ema_slow': ema_slow
    }


def detect_macd_signals(macd_data: dict) -> pd.DataFrame:
    """
    检测MACD金叉死叉信号
    
    Args:
        macd_data: MACD计算结果
        
    Returns:
        包含信号的DataFrame
    """
    macd = macd_data['macd']
    signal = macd_data['signal']
    
    # 计算MACD线与信号线的交叉
    macd_above_signal = (macd > signal).astype(bool)
    
    # 检测金叉 (MACD线从下方穿越信号线)
    golden_cross = (macd_above_signal) & (~macd_above_signal.shift(1).fillna(False))
    
    # 检测死叉 (MACD线从上方穿越信号线)  
    death_cross = (~macd_above_signal) & (macd_above_signal.shift(1).fillna(False))
    
    signals = pd.DataFrame({
        'golden_cross': golden_cross,
        'death_cross': death_cross,
        'macd': macd,
        'signal': signal,
        'histogram': macd_data['histogram']
    })
    
    return signals


def run_backtest(prices: pd.Series, signals: pd.DataFrame, initial_capital: float = 10000) -> dict:
    """
    运行回测策略
    
    Args:
        prices: 价格序列
        signals: 交易信号
        initial_capital: 初始资金
        
    Returns:
        回测结果
    """
    # 初始化变量
    capital = initial_capital
    btc_holdings = 0
    cash = initial_capital
    trades = []
    portfolio_values = []
    
    # 遍历每一天
    for i in range(len(prices)):
        current_price = prices.iloc[i]
        current_date = prices.index[i]
        
        # 检查金叉信号 (买入)
        if signals.iloc[i]['golden_cross'] and cash > 0:
            # 全仓买入
            btc_amount = cash / current_price
            btc_holdings += btc_amount
            
            trades.append({
                'date': current_date,
                'action': 'BUY',
                'price': current_price,
                'amount': btc_amount,
                'cash_before': cash,
                'btc_before': btc_holdings - btc_amount
            })
            
            cash = 0  # 全仓买入后现金为0
            
        # 检查死叉信号 (卖出)
        elif signals.iloc[i]['death_cross'] and btc_holdings > 0:
            # 全部卖出
            cash_received = btc_holdings * current_price
            
            trades.append({
                'date': current_date,
                'action': 'SELL',
                'price': current_price,
                'amount': btc_holdings,
                'cash_before': cash,
                'btc_before': btc_holdings
            })
            
            cash += cash_received
            btc_holdings = 0
        
        # 计算当前组合价值
        portfolio_value = cash + (btc_holdings * current_price)
        portfolio_values.append({
            'date': current_date,
            'cash': cash,
            'btc_holdings': btc_holdings,
            'btc_value': btc_holdings * current_price,
            'total_value': portfolio_value,
            'price': current_price
        })
    
    # 最终结算 (如果还持有BTC)
    final_price = prices.iloc[-1]
    final_date = prices.index[-1]
    final_value = cash + (btc_holdings * final_price)
    
    if btc_holdings > 0:
        trades.append({
            'date': final_date,
            'action': 'FINAL_SELL',
            'price': final_price,
            'amount': btc_holdings,
            'cash_before': cash,
            'btc_before': btc_holdings
        })
    
    return {
        'trades': trades,
        'portfolio_values': portfolio_values,
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return': (final_value - initial_capital) / initial_capital * 100,
        'total_trades': len([t for t in trades if t['action'] in ['BUY', 'SELL']])
    }


def calculate_performance_metrics(backtest_result: dict, prices: pd.Series) -> dict:
    """
    计算策略表现指标
    
    Args:
        backtest_result: 回测结果
        prices: 价格序列
        
    Returns:
        表现指标
    """
    portfolio_df = pd.DataFrame(backtest_result['portfolio_values'])
    portfolio_df.set_index('date', inplace=True)
    
    # 计算买入持有策略收益
    buy_hold_return = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100
    
    # 计算最大回撤
    portfolio_values = portfolio_df['total_value']
    peak = portfolio_values.expanding().max()
    drawdown = (portfolio_values - peak) / peak * 100
    max_drawdown = drawdown.min()
    
    # 计算年化收益率
    days = (portfolio_df.index[-1] - portfolio_df.index[0]).days
    years = days / 365.25
    annualized_return = ((backtest_result['final_value'] / backtest_result['initial_capital']) ** (1/years) - 1) * 100
    
    # 计算夏普比率 (简化版，假设无风险利率为2%)
    daily_returns = portfolio_values.pct_change().dropna()
    risk_free_rate = 0.02 / 365  # 日化无风险利率
    excess_returns = daily_returns - risk_free_rate
    sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(365) if excess_returns.std() > 0 else 0
    
    # 计算胜率
    trades = [t for t in backtest_result['trades'] if t['action'] in ['BUY', 'SELL']]
    profitable_trades = 0
    
    for i in range(0, len(trades), 2):
        if i + 1 < len(trades):
            buy_trade = trades[i] if trades[i]['action'] == 'BUY' else trades[i+1]
            sell_trade = trades[i+1] if trades[i+1]['action'] == 'SELL' else trades[i]
            
            if sell_trade['price'] > buy_trade['price']:
                profitable_trades += 1
    
    win_rate = (profitable_trades / (len(trades) // 2)) * 100 if len(trades) >= 2 else 0
    
    return {
        'strategy_return': backtest_result['total_return'],
        'buy_hold_return': buy_hold_return,
        'alpha': backtest_result['total_return'] - buy_hold_return,
        'max_drawdown': max_drawdown,
        'annualized_return': annualized_return,
        'sharpe_ratio': sharpe_ratio,
        'win_rate': win_rate,
        'total_trades': backtest_result['total_trades'],
        'days_analyzed': days
    }


def get_btc_historical_data(days: int = 1095) -> pd.DataFrame:
    """
    获取BTC历史数据 (过去3年 ≈ 1095天)
    
    Args:
        days: 获取天数
        
    Returns:
        包含价格数据的DataFrame
    """
    print(f"获取BTC过去{days}天的历史数据...")
    
    try:
        # 使用工具获取历史数据
        historical_data = get_coin_historical_chart_by_id('bitcoin', 'usd', days)
        
        if not historical_data or 'prices' not in historical_data:
            raise ValueError("无法获取BTC历史数据")
        
        # 转换为DataFrame
        prices_data = historical_data['prices']
        df = pd.DataFrame(prices_data, columns=['timestamp', 'price'])
        
        # 转换时间戳
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('date', inplace=True)
        df.drop('timestamp', axis=1, inplace=True)
        
        print(f"✅ 成功获取 {len(df)} 天的BTC数据")
        print(f"数据范围: {df.index[0].strftime('%Y-%m-%d')} 到 {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"起始价格: ${df['price'].iloc[0]:,.2f}")
        print(f"结束价格: ${df['price'].iloc[-1]:,.2f}")
        
        return df
        
    except Exception as e:
        print(f"❌ 获取BTC历史数据失败: {str(e)}")
        return None


def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description="BTC MACD策略回测分析",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--days', 
        type=int, 
        default=1095,
        help='回测天数 (默认1095天，约3年)'
    )
    
    parser.add_argument(
        '--fast-period', 
        type=int, 
        default=12,
        help='MACD快线EMA周期'
    )
    
    parser.add_argument(
        '--slow-period', 
        type=int, 
        default=26,
        help='MACD慢线EMA周期'
    )
    
    parser.add_argument(
        '--signal-period', 
        type=int, 
        default=9,
        help='MACD信号线EMA周期'
    )
    
    parser.add_argument(
        '--capital', 
        type=float, 
        default=10000.0,
        help='初始资金 (USD)'
    )
    
    parser.add_argument(
        '--coin', 
        type=str, 
        default='bitcoin',
        help='要分析的币种ID (默认bitcoin)'
    )
    
    return parser.parse_args()


def main():
    """
    主函数 - 执行BTC MACD策略回测
    """
    # 解析命令行参数
    args = parse_arguments()
    
    print("🚀 BTC MACD 策略回测分析")
    print("=" * 60)
    
    # 使用命令行参数
    DAYS = args.days
    FAST_PERIOD = args.fast_period
    SLOW_PERIOD = args.slow_period
    SIGNAL_PERIOD = args.signal_period
    INITIAL_CAPITAL = args.capital
    COIN_ID = args.coin
    
    print(f"回测参数:")
    print(f"  币种: {COIN_ID.upper()}")
    print(f"  时间范围: 过去 {DAYS} 天")
    print(f"  MACD参数: 快线={FAST_PERIOD}, 慢线={SLOW_PERIOD}, 信号线={SIGNAL_PERIOD}")
    print(f"  初始资金: ${INITIAL_CAPITAL:,}")
    print()
    
    # 1. 获取历史数据
    historical_data = get_coin_historical_chart_by_id(COIN_ID, 'usd', DAYS)
    if not historical_data or 'prices' not in historical_data:
        print(f"❌ 无法获取 {COIN_ID.upper()} 历史数据")
        return
    
    # 转换为DataFrame
    prices_data = historical_data['prices']
    btc_data = pd.DataFrame(prices_data, columns=['timestamp', 'price'])
    btc_data['date'] = pd.to_datetime(btc_data['timestamp'], unit='ms')
    btc_data.set_index('date', inplace=True)
    btc_data.drop('timestamp', axis=1, inplace=True)
    
    print(f"✅ 成功获取 {len(btc_data)} 天的 {COIN_ID.upper()} 数据")
    print(f"数据范围: {btc_data.index[0].strftime('%Y-%m-%d')} 到 {btc_data.index[-1].strftime('%Y-%m-%d')}")
    print(f"起始价格: ${btc_data['price'].iloc[0]:,.2f}")
    print(f"结束价格: ${btc_data['price'].iloc[-1]:,.2f}")
    if len(btc_data) < 100:
        print("❌ 无法获取足够的历史数据进行回测")
        return
    
    prices = btc_data['price']
    
    # 2. 计算MACD指标
    print("📈 计算MACD指标...")
    macd_data = calculate_macd(prices, FAST_PERIOD, SLOW_PERIOD, SIGNAL_PERIOD)
    
    # 3. 检测交易信号
    print("🔍 检测MACD金叉死叉信号...")
    signals = detect_macd_signals(macd_data)
    
    # 统计信号数量
    golden_crosses = signals['golden_cross'].sum()
    death_crosses = signals['death_cross'].sum()
    print(f"  金叉信号: {golden_crosses} 次")
    print(f"  死叉信号: {death_crosses} 次")
    print()
    
    # 4. 运行回测
    print("⚙️ 运行回测策略...")
    backtest_result = run_backtest(prices, signals, INITIAL_CAPITAL)
    
    # 5. 计算表现指标
    print("📊 计算表现指标...")
    performance = calculate_performance_metrics(backtest_result, prices)
    
    # 6. 输出结果
    print("\n" + "=" * 60)
    print(f"📈 {COIN_ID.upper()} MACD 策略回测结果")
    print("=" * 60)
    
    print(f"🔹 策略总收益率: {performance['strategy_return']:+.2f}%")
    print(f"🔹 买入持有收益率: {performance['buy_hold_return']:+.2f}%")
    print(f"🔹 Alpha (超额收益): {performance['alpha']:+.2f}%")
    print(f"🔹 年化收益率: {performance['annualized_return']:+.2f}%")
    print(f"🔹 最大回撤: {performance['max_drawdown']:.2f}%")
    print(f"🔹 夏普比率: {performance['sharpe_ratio']:.2f}")
    print(f"🔹 胜率: {performance['win_rate']:.1f}%")
    print(f"🔹 总交易次数: {performance['total_trades']} 次")
    print(f"🔹 分析天数: {performance['days_analyzed']} 天")
    print()
    
    print("💰 资金变化:")
    print(f"  初始资金: ${backtest_result['initial_capital']:,.2f}")
    print(f"  最终价值: ${backtest_result['final_value']:,.2f}")
    print(f"  绝对盈亏: ${backtest_result['final_value'] - backtest_result['initial_capital']:+,.2f}")
    print()
    
    # 策略评价
    print("📝 策略评价:")
    if performance['alpha'] > 0:
        print(f"  ✅ 策略跑赢买入持有 {performance['alpha']:.2f}%")
    else:
        print(f"  ❌ 策略跑输买入持有 {abs(performance['alpha']):.2f}%")
    
    if performance['sharpe_ratio'] > 1:
        print(f"  ✅ 夏普比率优秀 ({performance['sharpe_ratio']:.2f} > 1)")
    elif performance['sharpe_ratio'] > 0.5:
        print(f"  ⚠️ 夏普比率一般 ({performance['sharpe_ratio']:.2f})")
    else:
        print(f"  ❌ 夏普比率较差 ({performance['sharpe_ratio']:.2f})")
    
    if performance['win_rate'] > 50:
        print(f"  ✅ 胜率良好 ({performance['win_rate']:.1f}%)")
    else:
        print(f"  ⚠️ 胜率偏低 ({performance['win_rate']:.1f}%)")
    
    print()
    print("📋 交易记录前5笔:")
    print("-" * 50)
    for i, trade in enumerate(backtest_result['trades'][:5]):
        date_str = trade['date'].strftime('%Y-%m-%d')
        print(f"{i+1}. {date_str} | {trade['action']:<4} | ${trade['price']:>8,.2f} | {trade['amount']:>10,.6f} BTC")
    
    if len(backtest_result['trades']) > 5:
        print(f"... 还有 {len(backtest_result['trades']) - 5} 笔交易")
    
    print()
    print("⚠️ 免责声明:")
    print("此回测结果仅供参考，不构成投资建议。")
    print("历史表现不代表未来收益，投资有风险。")
    
    return {
        'performance': performance,
        'backtest_result': backtest_result,
        'strategy_params': {
            'fast_period': FAST_PERIOD,
            'slow_period': SLOW_PERIOD,
            'signal_period': SIGNAL_PERIOD,
            'initial_capital': INITIAL_CAPITAL,
            'days': DAYS
        }
    }


if __name__ == "__main__":
    main()