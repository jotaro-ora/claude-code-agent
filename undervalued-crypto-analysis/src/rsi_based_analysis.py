#!/usr/bin/env python3
"""
基于现有RSI数据的低估代币分析

使用已有的RSI分析数据，结合价格表现和技术指标，
识别排名前10的非稳定币中最被低估的代币。

可配置参数:
- rsi_weight: RSI在评分中的权重
- price_performance_weight: 价格表现的权重  
- oversold_threshold: 超卖阈值
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))


def load_rsi_data(file_path: str) -> dict:
    """
    加载RSI分析数据
    
    Args:
        file_path: RSI数据文件路径
        
    Returns:
        RSI数据字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法加载RSI数据: {str(e)}")
        return {}


def filter_top_10_non_stablecoins(rsi_data: dict) -> list:
    """
    从RSI数据中筛选出前10大非稳定币
    
    Args:
        rsi_data: RSI分析数据
        
    Returns:
        前10大非稳定币的数据列表
    """
    if 'all_results' not in rsi_data:
        return []
    
    # 定义稳定币列表
    stablecoins = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'FDUSD', 'PYUSD', 'USDD', 
                   'USDS', 'USDE', 'BSC-USD', 'SUSDS', 'SUSDE', 'BUIDL']
    
    # 筛选非稳定币
    non_stablecoins = []
    for coin in rsi_data['all_results']:
        symbol = coin['symbol'].replace('_USD', '').upper()
        if symbol not in stablecoins:
            non_stablecoins.append(coin)
    
    # 返回前10个（按市值排名）
    return non_stablecoins[:10]


def calculate_undervalued_score_rsi(coin_data: dict,
                                   rsi_weight: float = 0.4,
                                   price_performance_weight: float = 0.3,
                                   oversold_threshold: float = 35) -> float:
    """
    基于RSI和价格表现计算低估分数
    
    评分因子:
    1. RSI超卖程度 (权重: 40%)
    2. 24小时价格表现 (权重: 30%) 
    3. 价格相对地位 (权重: 30%)
    
    Args:
        coin_data: 代币数据
        rsi_weight: RSI权重
        price_performance_weight: 价格表现权重
        oversold_threshold: 超卖阈值
        
    Returns:
        0-100的低估分数
    """
    score = 0.0
    
    # 1. RSI超卖分数 (40%)
    rsi = coin_data.get('current_rsi', 50)
    if rsi <= oversold_threshold:
        # 越超卖分数越高
        rsi_score = (oversold_threshold - rsi) / oversold_threshold * 100
        rsi_score = min(100, rsi_score * 2)  # 放大超卖信号
    elif rsi <= 45:
        # 接近超卖区域
        rsi_score = (45 - rsi) / 10 * 60
    else:
        # 中性或超买
        rsi_score = max(0, (50 - rsi) * 2)
    
    score += rsi_score * rsi_weight
    
    # 2. 价格表现分数 (30%)
    # 24小时上涨但RSI仍低可能表示强势反弹开始
    price_change_24h = coin_data.get('price_change_24h', 0)
    
    if rsi <= 40 and price_change_24h > 5:
        # RSI低位但价格上涨 - 可能是反弹信号
        price_score = 90
    elif rsi <= 40 and 0 <= price_change_24h <= 5:
        # RSI低位价格稳定 - 筑底信号
        price_score = 80
    elif rsi <= 40 and price_change_24h < 0:
        # RSI低位继续下跌 - 可能超卖但有风险
        price_score = 70
    elif 40 < rsi <= 50 and price_change_24h > 8:
        # 中性RSI但大涨 - 可能动能过强
        price_score = 40
    elif 40 < rsi <= 50 and 3 <= price_change_24h <= 8:
        # 中性RSI适度上涨 - 健康上涨
        price_score = 75
    else:
        # 其他情况
        price_score = 50
    
    score += price_score * price_performance_weight
    
    # 3. 相对价格地位分数 (30%)
    # 基于当前价格的绝对值判断是否在历史低位
    current_price = coin_data.get('current_price', 0)
    
    # 根据不同价格区间判断相对位置（简化方法）
    if current_price < 0.1:
        # 小价格代币，可能被低估
        position_score = 85
    elif 0.1 <= current_price < 1:
        position_score = 75
    elif 1 <= current_price < 10:
        position_score = 65
    elif 10 <= current_price < 100:
        position_score = 55
    else:
        position_score = 45
    
    # 结合RSI调整分数
    if rsi <= 35:
        position_score += 15
    elif rsi <= 40:
        position_score += 10
    
    score += position_score * (1 - rsi_weight - price_performance_weight)
    
    return min(100, max(0, score))


def analyze_undervalued_cryptos(rsi_file_path: str,
                               rsi_weight: float = 0.4,
                               price_performance_weight: float = 0.3,
                               oversold_threshold: float = 35) -> pd.DataFrame:
    """
    分析最被低估的加密货币
    
    Args:
        rsi_file_path: RSI数据文件路径
        rsi_weight: RSI权重
        price_performance_weight: 价格表现权重
        oversold_threshold: 超卖阈值
        
    Returns:
        分析结果DataFrame
    """
    print("🔍 基于RSI数据分析最被低估的加密货币...")
    print("=" * 60)
    
    # 加载RSI数据
    rsi_data = load_rsi_data(rsi_file_path)
    if not rsi_data:
        print("❌ 无法加载RSI数据")
        return pd.DataFrame()
    
    # 筛选前10大非稳定币
    top_10_coins = filter_top_10_non_stablecoins(rsi_data)
    if not top_10_coins:
        print("❌ 无法找到前10大非稳定币数据")
        return pd.DataFrame()
    
    print(f"📊 分析{len(top_10_coins)}个前10大非稳定币...")
    print(f"参数设置: RSI权重={rsi_weight}, 价格表现权重={price_performance_weight}, 超卖阈值={oversold_threshold}")
    print()
    
    # 计算每个代币的低估分数
    analysis_results = []
    for coin in top_10_coins:
        undervalued_score = calculate_undervalued_score_rsi(
            coin, rsi_weight, price_performance_weight, oversold_threshold
        )
        
        result = {
            'symbol': coin['symbol'].replace('_USD', ''),
            'coin_id': coin['coin_id'],
            'current_rsi': coin['current_rsi'],
            'current_price': coin['current_price'],
            'price_change_24h': coin['price_change_24h'],
            'undervalued_score': undervalued_score,
            'rsi_category': coin['rsi_category'],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        analysis_results.append(result)
        
        print(f"✅ {result['symbol']}: 低估分数 {undervalued_score:.1f}, RSI {coin['current_rsi']:.1f}, 24h变化 {coin['price_change_24h']:.1f}%")
    
    # 转换为DataFrame并排序
    df = pd.DataFrame(analysis_results)
    df = df.sort_values('undervalued_score', ascending=False)
    
    print(f"\n📈 分析完成！最被低估的代币: {df.iloc[0]['symbol']}")
    return df


def generate_undervalued_report(df: pd.DataFrame) -> str:
    """
    生成低估分析报告
    
    Args:
        df: 分析结果DataFrame
        
    Returns:
        格式化的报告字符串
    """
    if df.empty:
        return "没有可用的分析数据"
    
    report = []
    report.append("📊 前10大加密货币低估分析报告")
    report.append("=" * 60)
    report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"分析范围: 排名前10的非稳定币")
    report.append(f"数据来源: RSI技术分析")
    report.append("")
    
    # 最被低估的前3名
    report.append("🏆 最被低估的加密货币 (前3名):")
    report.append("-" * 40)
    
    for i, (_, row) in enumerate(df.head(3).iterrows(), 1):
        report.append(f"{i}. {row['symbol']} - 低估分数: {row['undervalued_score']:.1f}/100")
        report.append(f"   当前价格: ${row['current_price']:,.4f}")
        report.append(f"   RSI指标: {row['current_rsi']:.1f} ({row['rsi_category']})")
        report.append(f"   24小时变化: {row['price_change_24h']:+.1f}%")
        
        # 分析原因
        if row['current_rsi'] <= 35:
            report.append(f"   💡 RSI显示深度超卖，技术面支持反弹")
        elif row['current_rsi'] <= 40:
            report.append(f"   💡 RSI接近超卖区域，存在反弹机会")
        
        if row['current_rsi'] <= 40 and row['price_change_24h'] > 5:
            report.append(f"   💡 低RSI但价格上涨，可能开始反弹")
        elif row['current_rsi'] <= 40 and row['price_change_24h'] < 0:
            report.append(f"   ⚠️  价格仍在下跌，需要观察支撑位")
        
        report.append("")
    
    # 排名表格
    report.append("📋 完整排名 (按低估分数排序):")
    report.append("-" * 40)
    
    # 格式化表格
    table_data = []
    for _, row in df.iterrows():
        table_data.append([
            row['symbol'],
            f"{row['undervalued_score']:.1f}",
            f"{row['current_rsi']:.1f}",
            f"${row['current_price']:,.4f}",
            f"{row['price_change_24h']:+.1f}%"
        ])
    
    # 表头
    headers = ["代币", "低估分数", "RSI", "当前价格", "24h变化"]
    report.append(f"{'代币':<8} {'低估分数':<8} {'RSI':<6} {'当前价格':<12} {'24h变化':<8}")
    report.append("-" * 50)
    
    for data in table_data:
        report.append(f"{data[0]:<8} {data[1]:<8} {data[2]:<6} {data[3]:<12} {data[4]:<8}")
    
    report.append("")
    
    # 详细分析
    most_undervalued = df.iloc[0]
    report.append("💡 最被低估代币详细分析:")
    report.append("-" * 40)
    report.append(f"代币: {most_undervalued['symbol']}")
    report.append(f"低估分数: {most_undervalued['undervalued_score']:.1f}/100")
    report.append("")
    
    report.append("技术面分析:")
    if most_undervalued['current_rsi'] <= 30:
        report.append("• RSI极度超卖 (<30)，强烈反弹信号")
    elif most_undervalued['current_rsi'] <= 35:
        report.append("• RSI深度超卖 (≤35)，技术性反弹概率高")
    elif most_undervalued['current_rsi'] <= 40:
        report.append("• RSI接近超卖区域，存在反弹机会")
    else:
        report.append("• RSI相对健康，但可能存在其他低估因素")
    
    # 价格分析
    if most_undervalued['current_rsi'] <= 40 and most_undervalued['price_change_24h'] > 5:
        report.append("• 低RSI配合价格上涨，可能是反弹启动信号")
    elif most_undervalued['price_change_24h'] < -5:
        report.append("• 近期价格大幅下跌，可能已接近底部区域")
    elif 0 <= most_undervalued['price_change_24h'] <= 5:
        report.append("• 价格表现相对稳定，适合逢低买入")
    
    report.append("")
    
    # 投资建议
    report.append("📈 投资策略建议:")
    report.append("-" * 40)
    
    if most_undervalued['current_rsi'] <= 35:
        report.append("• 分批建仓策略: RSI极低，适合分批逢低买入")
        report.append("• 止损设置: 建议设置技术止损位")
        report.append("• 持有周期: 中短期持有，等待技术性反弹")
    else:
        report.append("• 观察策略: 等待进一步确认信号")
        report.append("• 风险管理: 注意仓位控制")
    
    report.append("")
    
    # 风险提示
    report.append("⚠️  风险提示:")
    report.append("-" * 40)
    report.append("• 本分析基于技术指标，不构成投资建议")
    report.append("• 加密货币市场波动极大，存在重大投资风险")
    report.append("• RSI超卖不等于价格不会继续下跌")
    report.append("• 建议结合基本面分析和市场环境综合判断")
    report.append("• 投资前请咨询专业财务顾问")
    
    return "\n".join(report)


def main():
    """
    主函数 - 执行基于RSI的低估分析
    """
    try:
        # 可配置参数
        RSI_WEIGHT = 0.4
        PRICE_PERFORMANCE_WEIGHT = 0.3
        OVERSOLD_THRESHOLD = 35
        
        # RSI数据文件路径
        rsi_file_path = os.path.join(
            os.path.dirname(__file__), 
            '../../rsi-analysis/data/rsi_analysis_fixed_20250623_230331.json'
        )
        
        # 执行分析
        df = analyze_undervalued_cryptos(
            rsi_file_path=rsi_file_path,
            rsi_weight=RSI_WEIGHT,
            price_performance_weight=PRICE_PERFORMANCE_WEIGHT,
            oversold_threshold=OVERSOLD_THRESHOLD
        )
        
        if df.empty:
            print("❌ 分析失败，没有可用数据")
            return
        
        # 生成报告
        report = generate_undervalued_report(df)
        print("\n" + report)
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_dir = os.path.join(os.path.dirname(__file__), '../data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 保存详细数据
        csv_file = os.path.join(data_dir, f'undervalued_top10_analysis_{timestamp}.csv')
        df.to_csv(csv_file, index=False)
        
        # 保存JSON格式
        json_file = os.path.join(data_dir, f'undervalued_top10_analysis_{timestamp}.json')
        df.to_json(json_file, orient='records', indent=2)
        
        # 保存报告
        report_file = os.path.join(data_dir, f'undervalued_top10_report_{timestamp}.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 结果已保存:")
        print(f"  CSV: {csv_file}")
        print(f"  JSON: {json_file}")
        print(f"  报告: {report_file}")
        
        # 返回最被低估的代币
        most_undervalued = df.iloc[0]
        print(f"\n🎯 最终结论: {most_undervalued['symbol']} 是前10大代币中最被低估的")
        print(f"   低估分数: {most_undervalued['undervalued_score']:.1f}/100")
        print(f"   RSI: {most_undervalued['current_rsi']:.1f}")
        print(f"   当前价格: ${most_undervalued['current_price']:,.4f}")
        
    except Exception as e:
        print(f"❌ 分析过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()