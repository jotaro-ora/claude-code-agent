#!/usr/bin/env python3
"""
简化版技术分析器 - 直接API调用

这个版本直接调用CoinGecko API，避免使用可能有问题的工具函数。
专注于核心功能：基于技术指标识别最被低估的代币。
"""

import requests
import pandas as pd
import numpy as np
import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_api_headers():
    """获取API请求头"""
    return {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}


def get_top_coins_simple(n=15):
    """
    获取前N大代币市场数据
    """
    url = "https://pro-api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": str(n),
        "page": "1",
        "sparkline": "false",
        "price_change_percentage": "24h"
    }
    
    headers = get_api_headers()
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ 获取代币列表失败: {e}")
        return []


def get_coin_details(coin_id: str):
    """
    获取代币详细信息
    """
    url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false"
    }
    
    headers = get_api_headers()
    
    for attempt in range(3):
        try:
            time.sleep(0.5)  # 避免API限流
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == 2:
                print(f"  ❌ 获取 {coin_id} 详细信息失败: {e}")
                return None
            time.sleep(1)
    
    return None


def get_coin_history(coin_id: str, days: int = 30):
    """
    获取代币历史价格数据
    """
    url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": str(days),
        "interval": "daily" if days > 7 else "hourly"
    }
    
    headers = get_api_headers()
    
    for attempt in range(3):
        try:
            time.sleep(0.5)
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == 2:
                print(f"  ❌ 获取 {coin_id} 历史数据失败: {e}")
                return None
            time.sleep(1)
    
    return None


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    计算RSI指标
    """
    if len(prices) < period + 1:
        return 50.0
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Wilder's smoothing
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def analyze_coin_technical(coin_data: dict) -> Dict[str, Any]:
    """
    分析单个代币的技术指标
    """
    coin_id = coin_data.get('id', '')
    symbol = coin_data.get('symbol', '').upper()
    
    print(f"正在分析 {symbol}...")
    
    # 获取详细信息
    details = get_coin_details(coin_id)
    if not details or 'market_data' not in details:
        print(f"  ❌ 无法获取 {symbol} 详细信息")
        return None
    
    market_data = details['market_data']
    current_price = market_data.get('current_price', {}).get('usd', 0)
    ath_price = market_data.get('ath', {}).get('usd', current_price)
    market_cap = market_data.get('market_cap', {}).get('usd', 0)
    
    # 获取历史数据
    history = get_coin_history(coin_id, 30)
    if not history or 'prices' not in history:
        print(f"  ❌ 无法获取 {symbol} 历史数据")
        return None
    
    # 提取价格数据
    prices = [float(price[1]) for price in history['prices']]
    if len(prices) < 10:
        print(f"  ❌ {symbol} 价格数据不足")
        return None
    
    # 计算技术指标
    rsi = calculate_rsi(prices)
    ath_discount = ((ath_price - current_price) / ath_price) * 100 if ath_price > 0 else 0
    
    # 价格变化
    price_7d_ago = prices[-7] if len(prices) >= 7 else prices[0]
    price_change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
    
    price_30d_ago = prices[0] if len(prices) > 0 else current_price
    price_change_30d = ((current_price - price_30d_ago) / price_30d_ago) * 100
    
    # 波动性
    volatility = np.std(prices[-14:]) / np.mean(prices[-14:]) * 100 if len(prices) >= 14 else 0
    
    # 24小时变化
    price_change_24h = coin_data.get('price_change_percentage_24h', 0)
    
    result = {
        'symbol': symbol,
        'coin_id': coin_id,
        'current_price': current_price,
        'market_cap': market_cap,
        'ath_price': ath_price,
        'ath_discount_pct': ath_discount,
        'rsi': rsi,
        'price_change_7d_pct': price_change_7d,
        'price_change_30d_pct': price_change_30d,
        'price_change_24h_pct': price_change_24h,
        'volatility_pct': volatility,
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    print(f"  ✅ {symbol} 分析完成 (RSI: {rsi:.1f}, ATH折扣: {ath_discount:.1f}%)")
    return result


def calculate_undervalued_score(data: Dict[str, Any]) -> float:
    """
    计算低估分数
    """
    score = 0.0
    
    # 1. RSI分数 (40%)
    rsi = data.get('rsi', 50)
    if rsi <= 30:
        rsi_score = 100
    elif rsi <= 35:
        rsi_score = 90
    elif rsi <= 40:
        rsi_score = 75
    elif rsi <= 50:
        rsi_score = 50
    else:
        rsi_score = max(0, 100 - (rsi - 50) * 2)
    
    score += rsi_score * 0.4
    
    # 2. ATH折扣分数 (30%)
    ath_discount = data.get('ath_discount_pct', 0)
    ath_score = min(100, ath_discount * 2)  # 50%折扣=100分
    score += ath_score * 0.3
    
    # 3. 价格动量分数 (20%)
    price_24h = data.get('price_change_24h_pct', 0)
    price_7d = data.get('price_change_7d_pct', 0)
    
    # 结合短期和中期动量
    if rsi <= 40 and price_24h > 5:
        momentum_score = 90  # 低RSI但上涨
    elif rsi <= 40 and -5 <= price_24h <= 5:
        momentum_score = 80  # 低RSI稳定
    elif price_7d < -20:
        momentum_score = 60  # 大幅下跌可能超跌
    elif -10 <= price_7d <= 10:
        momentum_score = 70  # 温和变化
    else:
        momentum_score = 50
    
    score += momentum_score * 0.2
    
    # 4. 波动性分数 (10%)
    volatility = data.get('volatility_pct', 0)
    if 5 <= volatility <= 15:
        vol_score = 100
    elif volatility < 5:
        vol_score = 70
    else:
        vol_score = max(20, 100 - (volatility - 15) * 3)
    
    score += vol_score * 0.1
    
    return min(100, max(0, score))


def main():
    """
    主分析函数
    """
    print("🔍 简化版加密货币技术分析...")
    print("=" * 60)
    
    # 获取前15大代币
    print("获取前15大代币数据...")
    top_coins = get_top_coins_simple(15)
    if not top_coins:
        print("❌ 无法获取代币数据")
        return
    
    # 过滤稳定币
    stablecoins = ['usdt', 'usdc', 'busd', 'dai', 'tusd', 'fdusd', 'pyusd', 'usdd']
    non_stablecoins = [coin for coin in top_coins if coin.get('id', '').lower() not in stablecoins][:8]
    
    print(f"将分析 {len(non_stablecoins)} 个非稳定币代币")
    print()
    
    # 分析每个代币
    analysis_results = []
    for i, coin in enumerate(non_stablecoins):
        print(f"进度: {i+1}/{len(non_stablecoins)}")
        
        result = analyze_coin_technical(coin)
        if result:
            # 计算低估分数
            score = calculate_undervalued_score(result)
            result['undervalued_score'] = score
            analysis_results.append(result)
        
        # API限流控制
        if i < len(non_stablecoins) - 1:
            time.sleep(2)
        
        print()
    
    if not analysis_results:
        print("❌ 没有成功分析的代币")
        return
    
    # 生成结果
    df = pd.DataFrame(analysis_results)
    df = df.sort_values('undervalued_score', ascending=False)
    
    print("📊 分析结果:")
    print("=" * 60)
    print(f"成功分析 {len(df)} 个代币")
    print()
    
    # 显示前5名
    print("🏆 最被低估的代币 (前5名):")
    print("-" * 40)
    
    for i, (_, row) in enumerate(df.head(5).iterrows(), 1):
        print(f"{i}. {row['symbol']} - 低估分数: {row['undervalued_score']:.1f}/100")
        print(f"   当前价格: ${row['current_price']:,.4f}")
        print(f"   RSI: {row['rsi']:.1f}")
        print(f"   ATH折扣: {row['ath_discount_pct']:.1f}%")
        print(f"   24h变化: {row['price_change_24h_pct']:+.1f}%")
        print()
    
    # 详细表格
    print("📋 完整排名:")
    print("-" * 60)
    display_df = df[['symbol', 'undervalued_score', 'rsi', 'ath_discount_pct', 
                    'price_change_24h_pct', 'current_price']].copy()
    display_df.columns = ['代币', '低估分数', 'RSI', 'ATH折扣%', '24h变化%', '当前价格']
    display_df = display_df.round(1)
    print(display_df.to_string(index=False))
    
    print()
    
    # 最终结论
    most_undervalued = df.iloc[0]
    print("🎯 分析结论:")
    print("-" * 30)
    print(f"最被低估的代币: {most_undervalued['symbol']}")
    print(f"低估分数: {most_undervalued['undervalued_score']:.1f}/100")
    print(f"主要理由:")
    
    if most_undervalued['rsi'] <= 35:
        print(f"  • RSI({most_undervalued['rsi']:.1f}) 显示超卖状态")
    if most_undervalued['ath_discount_pct'] > 30:
        print(f"  • 相对ATH有 {most_undervalued['ath_discount_pct']:.1f}% 的折扣")
    if most_undervalued['price_change_24h_pct'] > 5 and most_undervalued['rsi'] <= 40:
        print(f"  • 低RSI配合上涨，可能是反弹信号")
    
    print()
    print("⚠️ 风险提示: 本分析仅基于技术指标，不构成投资建议")
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    os.makedirs(data_dir, exist_ok=True)
    
    csv_file = os.path.join(data_dir, f'simple_analysis_{timestamp}.csv')
    df.to_csv(csv_file, index=False)
    
    json_file = os.path.join(data_dir, f'simple_analysis_{timestamp}.json')
    df.to_json(json_file, orient='records', indent=2)
    
    print(f"\n💾 结果已保存: {csv_file}")


if __name__ == "__main__":
    main()