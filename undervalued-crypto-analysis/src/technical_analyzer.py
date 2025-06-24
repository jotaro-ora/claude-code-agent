#!/usr/bin/env python3
"""
技术分析模块 - 识别最被低估的加密货币

此模块通过多种技术指标分析排名前10的加密货币，识别价值最被低估的代币。
分析指标包括RSI、价格相对ATH位置、成交量分析、支撑阻力位等。

外部可配置参数:
- coin_list: 要分析的代币列表
- analysis_days: 分析的历史天数
- rsi_oversold_threshold: RSI超卖阈值
- ath_discount_threshold: 相对ATH的折扣阈值
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any, Tuple

# 添加项目路径以导入工具
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from tools.top_coins import get_top_coins
from tools.coin_historical_chart_by_id import get_coin_historical_chart_by_id
from tools.coin_data_by_id import get_coin_data_by_id


def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """
    计算相对强弱指数 (RSI)
    
    Args:
        prices: 价格列表
        period: RSI周期，默认14天
        
    Returns:
        RSI值列表
    """
    if len(prices) < period + 1:
        return [50.0] * len(prices)  # 数据不足时返回中性值
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Wilder's smoothing method
    avg_gains = []
    avg_losses = []
    
    # 初始平均值
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    avg_gains.append(avg_gain)
    avg_losses.append(avg_loss)
    
    # 后续使用Wilder's方法
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        avg_gains.append(avg_gain)
        avg_losses.append(avg_loss)
    
    # 计算RSI
    rsi_values = []
    for avg_gain, avg_loss in zip(avg_gains, avg_losses):
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)
    
    # 为前面的数据填充中性值
    return [50.0] * period + rsi_values


def calculate_support_resistance(prices: List[float], window: int = 20) -> Tuple[float, float]:
    """
    计算支撑和阻力位
    
    Args:
        prices: 价格列表
        window: 窗口大小
        
    Returns:
        (支撑位, 阻力位)
    """
    if len(prices) < window:
        return min(prices), max(prices)
    
    recent_prices = prices[-window:]
    support = min(recent_prices)
    resistance = max(recent_prices)
    
    return support, resistance


def analyze_volume_trend(volumes: List[float], prices: List[float], window: int = 7) -> Dict[str, float]:
    """
    分析成交量趋势
    
    Args:
        volumes: 成交量列表
        prices: 价格列表
        window: 分析窗口
        
    Returns:
        成交量分析结果
    """
    if len(volumes) < window or len(prices) < window:
        return {
            'volume_trend': 0.0,
            'volume_price_correlation': 0.0,
            'avg_volume': np.mean(volumes) if volumes else 0.0
        }
    
    recent_volumes = volumes[-window:]
    recent_prices = prices[-window:]
    
    # 成交量趋势 (最近vs前期)
    if len(volumes) >= window * 2:
        prev_volumes = volumes[-window*2:-window]
        volume_trend = (np.mean(recent_volumes) / np.mean(prev_volumes) - 1) * 100
    else:
        volume_trend = 0.0
    
    # 成交量与价格相关性
    if len(recent_volumes) > 1 and len(recent_prices) > 1:
        correlation = np.corrcoef(recent_volumes, recent_prices)[0, 1]
        if np.isnan(correlation):
            correlation = 0.0
    else:
        correlation = 0.0
    
    return {
        'volume_trend': volume_trend,
        'volume_price_correlation': correlation,
        'avg_volume': np.mean(recent_volumes)
    }


def get_coin_technical_data(coin_id: str, days: int = 30) -> Dict[str, Any]:
    """
    获取单个代币的技术分析数据
    
    Args:
        coin_id: 代币ID
        days: 分析天数
        
    Returns:
        技术分析数据字典
    """
    try:
        print(f"正在分析 {coin_id.upper()}...")
        
        # 获取基本信息
        coin_info = get_coin_data_by_id(coin_id)
        if not coin_info or 'market_data' not in coin_info:
            print(f"  ❌ 无法获取 {coin_id} 的基本信息")
            return None
        
        market_data = coin_info['market_data']
        current_price = market_data.get('current_price', {}).get('usd', 0)
        ath_price = market_data.get('ath', {}).get('usd', current_price)
        market_cap = market_data.get('market_cap', {}).get('usd', 0)
        
        # 获取历史价格数据
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        historical_data = get_coin_historical_chart_by_id(coin_id, start_date, end_date)
        if not historical_data or len(historical_data) < 10:
            print(f"  ❌ 无法获取 {coin_id} 的历史数据")
            return None
        
        # 提取价格和成交量数据
        prices = [float(row[1]) for row in historical_data]
        volumes = [float(row[2]) for row in historical_data if len(row) > 2]
        
        if not prices:
            print(f"  ❌ {coin_id} 价格数据为空")
            return None
        
        # 计算技术指标
        rsi_values = calculate_rsi(prices)
        current_rsi = rsi_values[-1] if rsi_values else 50.0
        
        support, resistance = calculate_support_resistance(prices)
        volume_analysis = analyze_volume_trend(volumes, prices)
        
        # 计算ATH折扣
        ath_discount = ((ath_price - current_price) / ath_price) * 100 if ath_price > 0 else 0
        
        # 计算价格变化
        price_change_7d = ((prices[-1] - prices[-7]) / prices[-7]) * 100 if len(prices) >= 7 else 0
        price_change_30d = ((prices[-1] - prices[0]) / prices[0]) * 100 if len(prices) > 1 else 0
        
        # 计算波动性 (标准差)
        volatility = np.std(prices[-14:]) / np.mean(prices[-14:]) * 100 if len(prices) >= 14 else 0
        
        result = {
            'coin_id': coin_id,
            'symbol': coin_id.upper(),
            'current_price': current_price,
            'market_cap': market_cap,
            'ath_price': ath_price,
            'ath_discount_pct': ath_discount,
            'current_rsi': current_rsi,
            'support_level': support,
            'resistance_level': resistance,
            'price_change_7d_pct': price_change_7d,
            'price_change_30d_pct': price_change_30d,
            'volatility_pct': volatility,
            'volume_trend_pct': volume_analysis['volume_trend'],
            'volume_price_correlation': volume_analysis['volume_price_correlation'],
            'avg_volume': volume_analysis['avg_volume'],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        print(f"  ✅ {coin_id.upper()} 分析完成")
        return result
        
    except Exception as e:
        print(f"  ❌ 分析 {coin_id} 时出错: {str(e)}")
        return None


def calculate_undervalued_score(data: Dict[str, Any], 
                               rsi_oversold_threshold: float = 35,
                               ath_discount_threshold: float = 50) -> float:
    """
    计算低估分数
    
    分数计算基于多个因素:
    1. RSI超卖程度 (权重: 25%)
    2. 相对ATH的折扣 (权重: 30%)
    3. 成交量趋势 (权重: 15%)
    4. 波动性 (权重: 15%)
    5. 价格动量 (权重: 15%)
    
    Args:
        data: 技术分析数据
        rsi_oversold_threshold: RSI超卖阈值
        ath_discount_threshold: ATH折扣阈值
        
    Returns:
        0-100的低估分数，分数越高越被低估
    """
    score = 0.0
    
    # 1. RSI超卖分数 (25%)
    rsi = data.get('current_rsi', 50)
    if rsi <= rsi_oversold_threshold:
        rsi_score = (rsi_oversold_threshold - rsi) / rsi_oversold_threshold * 100
    else:
        rsi_score = max(0, (50 - rsi) / 15 * 50)  # 中性到轻微超卖
    score += rsi_score * 0.25
    
    # 2. ATH折扣分数 (30%)
    ath_discount = data.get('ath_discount_pct', 0)
    ath_score = min(100, (ath_discount / ath_discount_threshold) * 100)
    score += ath_score * 0.30
    
    # 3. 成交量趋势分数 (15%)
    volume_trend = data.get('volume_trend_pct', 0)
    # 成交量增加是好信号，但不能过热
    if volume_trend > 50:
        volume_score = max(0, 100 - (volume_trend - 50) * 2)  # 过热惩罚
    else:
        volume_score = max(0, 50 + volume_trend)
    score += volume_score * 0.15
    
    # 4. 波动性分数 (15%)
    # 适度波动是好的，过高或过低都不好
    volatility = data.get('volatility_pct', 0)
    if 5 <= volatility <= 20:
        volatility_score = 100
    elif volatility < 5:
        volatility_score = volatility * 20  # 太稳定可能缺乏机会
    else:
        volatility_score = max(0, 100 - (volatility - 20) * 5)  # 太波动风险高
    score += volatility_score * 0.15
    
    # 5. 价格动量分数 (15%)
    # 轻微下跌或盘整比大幅上涨更有价值
    price_change_7d = data.get('price_change_7d_pct', 0)
    if -10 <= price_change_7d <= 5:
        momentum_score = 100
    elif price_change_7d < -10:
        momentum_score = max(0, 100 + price_change_7d * 5)  # 跌太多可能有问题
    else:
        momentum_score = max(0, 100 - price_change_7d * 10)  # 涨太多可能超买
    score += momentum_score * 0.15
    
    return min(100, max(0, score))


def analyze_top_cryptocurrencies(coin_list: List[str] = None,
                                analysis_days: int = 30,
                                rsi_oversold_threshold: float = 35,
                                ath_discount_threshold: float = 50) -> pd.DataFrame:
    """
    分析顶级加密货币并找出最被低估的
    
    Args:
        coin_list: 要分析的代币列表，None时使用前10大代币
        analysis_days: 分析的历史天数
        rsi_oversold_threshold: RSI超卖阈值
        ath_discount_threshold: ATH折扣阈值
        
    Returns:
        按低估分数排序的DataFrame
    """
    print("🔍 开始加密货币技术分析...")
    print("=" * 60)
    
    # 如果没有提供代币列表，获取前10大非稳定币
    if coin_list is None:
        print("获取前10大非稳定币...")
        coins_data = get_top_coins(n=15, include_extra_data=True)
        stablecoins = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'FDUSD', 'PYUSD', 'USDD']
        filtered_coins = coins_data[~coins_data['symbol'].str.upper().isin(stablecoins)].head(10)
        coin_list = filtered_coins['symbol'].tolist()
    
    print(f"分析代币列表: {coin_list}")
    print(f"分析参数: 历史天数={analysis_days}, RSI阈值={rsi_oversold_threshold}, ATH折扣阈值={ath_discount_threshold}%")
    print()
    
    # 分析每个代币
    analysis_results = []
    for coin_id in coin_list:
        result = get_coin_technical_data(coin_id, analysis_days)
        if result:
            # 计算低估分数
            undervalued_score = calculate_undervalued_score(
                result, rsi_oversold_threshold, ath_discount_threshold
            )
            result['undervalued_score'] = undervalued_score
            analysis_results.append(result)
    
    if not analysis_results:
        print("❌ 没有成功分析的代币")
        return pd.DataFrame()
    
    # 转换为DataFrame并排序
    df = pd.DataFrame(analysis_results)
    df = df.sort_values('undervalued_score', ascending=False)
    
    print(f"\n✅ 成功分析 {len(df)} 个代币")
    return df


def generate_analysis_report(df: pd.DataFrame) -> str:
    """
    生成分析报告
    
    Args:
        df: 分析结果DataFrame
        
    Returns:
        格式化的报告字符串
    """
    if df.empty:
        return "没有可用的分析数据"
    
    report = []
    report.append("📊 加密货币技术分析报告")
    report.append("=" * 50)
    report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"分析代币数量: {len(df)}")
    report.append()
    
    # 最被低估的前3名
    report.append("🏆 最被低估的加密货币 (前3名):")
    report.append("-" * 30)
    
    for i, (_, row) in enumerate(df.head(3).iterrows(), 1):
        report.append(f"{i}. {row['symbol']} - 低估分数: {row['undervalued_score']:.1f}")
        report.append(f"   当前价格: ${row['current_price']:.4f}")
        report.append(f"   RSI: {row['current_rsi']:.1f}")
        report.append(f"   相对ATH折扣: {row['ath_discount_pct']:.1f}%")
        report.append(f"   7天价格变化: {row['price_change_7d_pct']:.1f}%")
        report.append()
    
    # 详细分析表格
    report.append("📋 详细技术指标:")
    report.append("-" * 30)
    
    # 选择关键列显示
    display_cols = ['symbol', 'undervalued_score', 'current_rsi', 'ath_discount_pct', 
                   'price_change_7d_pct', 'volatility_pct']
    display_df = df[display_cols].copy()
    display_df.columns = ['代币', '低估分数', 'RSI', 'ATH折扣%', '7日变化%', '波动性%']
    
    # 格式化数值
    for col in display_df.columns[1:]:
        if col != '代币':
            display_df[col] = display_df[col].round(1)
    
    report.append(display_df.to_string(index=False))
    report.append()
    
    # 分析总结
    most_undervalued = df.iloc[0]
    report.append("💡 分析总结:")
    report.append("-" * 30)
    report.append(f"最被低估代币: {most_undervalued['symbol']}")
    report.append(f"主要原因:")
    
    if most_undervalued['current_rsi'] < 40:
        report.append(f"  • RSI({most_undervalued['current_rsi']:.1f})显示超卖状态")
    
    if most_undervalued['ath_discount_pct'] > 30:
        report.append(f"  • 相对ATH有{most_undervalued['ath_discount_pct']:.1f}%的折扣")
    
    if most_undervalued['price_change_7d_pct'] < 0:
        report.append(f"  • 7天内价格下跌{abs(most_undervalued['price_change_7d_pct']):.1f}%，可能存在反弹机会")
    
    report.append()
    report.append("⚠️  投资风险提示:")
    report.append("此分析仅基于技术指标，不构成投资建议。")
    report.append("加密货币投资存在高风险，请谨慎决策。")
    
    return "\n".join(report)


def main():
    """
    主函数 - 执行完整的技术分析
    """
    try:
        # 可配置参数
        ANALYSIS_DAYS = 30
        RSI_OVERSOLD_THRESHOLD = 35
        ATH_DISCOUNT_THRESHOLD = 50
        
        # 执行分析
        df = analyze_top_cryptocurrencies(
            analysis_days=ANALYSIS_DAYS,
            rsi_oversold_threshold=RSI_OVERSOLD_THRESHOLD,
            ath_discount_threshold=ATH_DISCOUNT_THRESHOLD
        )
        
        if df.empty:
            print("❌ 分析失败，没有可用数据")
            return
        
        # 生成报告
        report = generate_analysis_report(df)
        print("\n" + report)
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_dir = os.path.join(os.path.dirname(__file__), '../data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 保存详细数据
        csv_file = os.path.join(data_dir, f'undervalued_analysis_{timestamp}.csv')
        df.to_csv(csv_file, index=False)
        
        # 保存JSON格式
        json_file = os.path.join(data_dir, f'undervalued_analysis_{timestamp}.json')
        df.to_json(json_file, orient='records', indent=2)
        
        # 保存报告
        report_file = os.path.join(data_dir, f'undervalued_report_{timestamp}.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 结果已保存:")
        print(f"  CSV: {csv_file}")
        print(f"  JSON: {json_file}")
        print(f"  报告: {report_file}")
        
    except Exception as e:
        print(f"❌ 分析过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()