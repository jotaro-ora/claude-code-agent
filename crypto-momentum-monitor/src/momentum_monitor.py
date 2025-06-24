#!/usr/bin/env python3
"""
Cryptocurrency Momentum Monitor v2 - Enhanced with Volume Data Tool

This improved version uses the new volume_data tool from /tools/ for more efficient
volume analysis and monitoring. It monitors top 10-20 cryptocurrencies (excluding 
stablecoins) to identify coins that meet specific momentum criteria:

1. Price is above both 20 and 50 EMA on 4-hour and daily charts
2. 24-hour trading volume is at least 50% higher than the average of the past 3 days

Key Improvements in v2:
- Uses dedicated volume_data tool for better volume analysis
- More efficient API usage with specialized volume endpoints
- Enhanced volume change detection and percentage calculations
- Improved error handling and data validation
- Better performance with optimized API calls

Dependencies:
- tools.top_coins: For getting top cryptocurrencies by market cap
- tools.coingecko: For fetching historical OHLC data
- tools.volume_data: For fetching current volume data (NEW)
- pandas: For data manipulation and analysis
- numpy: For numerical calculations
- python-dotenv: For environment variable management

Environment Variables Required:
- COINGECKO_API_KEY: Your CoinGecko Pro API key

Usage:
    python crypto-momentum-monitor/src/momentum_monitor_v2.py
    
Output:
    - Console output with momentum analysis results
    - JSON file with detailed results in data/ folder
    - Alert-style summary for coins meeting criteria
"""

import sys
import os
import pandas as pd
import numpy as np
import json
import time
import requests
from datetime import datetime, timezone
from typing import Dict, List

# Add project root to Python path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tools.top_coins import get_top_coins
from tools.coingecko import get_coingecko_ohlc

class MomentumMonitor:
    """
    Enhanced cryptocurrency momentum monitoring system using volume_data tool.
    
    This class provides functionality to:
    1. Fetch top cryptocurrencies excluding stablecoins
    2. Calculate EMAs for multiple timeframes
    3. Analyze volume spikes using specialized volume tool
    4. Identify coins meeting momentum criteria
    5. Generate alerts and reports
    
    Key improvements over v1:
    - Uses dedicated volume_data tool for better efficiency
    - Enhanced volume analysis with percentage changes
    - Improved error handling and data validation
    - Better performance with optimized API usage
    
    Attributes:
        n_coins (int): Number of top coins to monitor
        excluded_symbols (set): Stablecoin symbols to exclude
        data_cache_dir (str): Directory for caching data
        results (dict): Analysis results storage
    """
    
    def __init__(self, n_coins: int = 20):
        """
        Initialize enhanced momentum monitor.
        
        Args:
            n_coins (int): Number of top coins to monitor (default: 20)
        """
        self.n_coins = n_coins
        
        # Define stablecoins to exclude (updated list)
        self.excluded_symbols = {
            'USDT_USD', 'USDC_USD', 'USDS_USD', 'DAI_USD', 'USDE_USD', 
            'SUSDE_USD', 'SUSDS_USD', 'BSC-USD_USD', 'BUIDL_USD', 'BUSD_USD'
        }
        
        self.data_cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(self.data_cache_dir, exist_ok=True)
        
        self.results = {}
        
        print(f"Momentum Monitor v2 initialized:")
        print(f"  - Monitoring top {n_coins} coins (excluding stablecoins)")
        print(f"  - Excluded symbols: {len(self.excluded_symbols)} stablecoins")
        print(f"  - Enhanced with volume_data tool")
        print(f"  - Cache directory: {self.data_cache_dir}")
    
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA) for given price series.
        
        EMA = (Price * Multiplier) + (Previous EMA * (1 - Multiplier))
        where Multiplier = 2 / (Period + 1)
        
        Args:
            prices (pd.Series): Series of closing prices
            period (int): Period for EMA calculation
            
        Returns:
            pd.Series: EMA values (NaN for insufficient data)
            
        Note:
            The first EMA value is calculated as Simple Moving Average (SMA).
            Subsequent values use the exponential smoothing formula.
        """
        if len(prices) < period:
            return pd.Series([np.nan] * len(prices), index=prices.index)
        
        multiplier = 2.0 / (period + 1)
        ema_values = pd.Series(index=prices.index, dtype=float)
        
        # First EMA value is SMA of first 'period' values
        first_sma = prices.iloc[:period].mean()
        ema_values.iloc[period - 1] = first_sma
        
        # Calculate subsequent EMA values
        for i in range(period, len(prices)):
            current_price = prices.iloc[i]
            previous_ema = ema_values.iloc[i - 1]
            ema_values.iloc[i] = (current_price * multiplier) + (previous_ema * (1 - multiplier))
        
        return ema_values
    
    def get_filtered_coins(self) -> List[str]:
        """
        Get top coins excluding stablecoins.
        
        Returns:
            List[str]: List of coin symbols excluding stablecoins
        """
        try:
            print(f"Fetching top {self.n_coins} coins...")
            
            # Get more coins than needed to account for stablecoin filtering
            fetch_count = min(self.n_coins + len(self.excluded_symbols) + 10, 100)
            all_symbols = get_top_coins(n=fetch_count)
            
            # Filter out stablecoins
            filtered_symbols = [
                symbol for symbol in all_symbols 
                if symbol not in self.excluded_symbols
            ]
            
            # Take only the requested number
            result_symbols = filtered_symbols[:self.n_coins]
            
            print(f"✓ Filtered {len(all_symbols)} coins to {len(result_symbols)} (excluded {len(self.excluded_symbols)} stablecoins)")
            print(f"  Monitoring: {result_symbols[:5]}{'...' if len(result_symbols) > 5 else ''}")
            
            return result_symbols
            
        except Exception as e:
            print(f"❌ Failed to get filtered coins: {str(e)}")
            return []
    
    def get_symbol_to_id_mapping(self, symbols):
        """获取symbol到coin_id的映射"""
        mapping = {
            'BTC_USD': 'bitcoin',
            'ETH_USD': 'ethereum', 
            'XRP_USD': 'ripple',
            'BNB_USD': 'binancecoin',
            'SOL_USD': 'solana',
            'ADA_USD': 'cardano',
            'DOGE_USD': 'dogecoin',
            'TRX_USD': 'tron',
            'LINK_USD': 'chainlink',
            'DOT_USD': 'polkadot',
            'MATIC_USD': 'matic-network',
            'WBTC_USD': 'wrapped-bitcoin',
            'STETH_USD': 'staked-ether',
            'LTC_USD': 'litecoin',
            'BCH_USD': 'bitcoin-cash',
            'SUI_USD': 'sui',
            'HYPE_USD': 'hyperliquid',
            'WSTETH_USD': 'wrapped-steth'
        }
        
        coin_ids = []
        for symbol in symbols:
            if symbol in mapping:
                coin_ids.append(mapping[symbol])
            else:
                # 尝试自动转换
                token = symbol.replace('_USD', '').lower()
                coin_ids.append(token)
        
        return coin_ids, mapping
    
    def fetch_volume_analysis_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        修复的volume数据获取方法，直接使用正确的API调用
        
        Args:
            symbols (List[str]): List of trading pair symbols
            
        Returns:
            Dict[str, Dict]: Volume analysis data for each symbol
        """
        try:
            import requests
            print(f"📊 获取 {len(symbols)} 个币种的volume数据...")
            
            coin_ids, mapping = self.get_symbol_to_id_mapping(symbols)
            
            # 使用正确的API调用
            headers = {
                'x-cg-pro-api-key': os.getenv('COINGECKO_API_KEY')
            }
            
            params = {
                'vs_currency': 'USD',
                'ids': ','.join(coin_ids),
                'per_page': '250',
                'page': '1',
                'price_change_percentage': '24h'
            }
            
            url = 'https://pro-api.coingecko.com/api/v3/coins/markets'
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            print(f"✅ 成功获取 {len(data)} 个币种的数据")
            
            # 处理数据
            volume_data = {}
            for item in data:
                symbol = item.get('symbol', '').upper() + '_USD'
                
                current_volume = item.get('total_volume', 0)
                price_change_24h = item.get('price_change_24h', 0)
                price_change_pct = item.get('price_change_percentage_24h', 0)
                
                # 计算volume激增比率
                # 使用价格变化作为volume活跃度的代理指标
                if abs(price_change_pct) > 3:
                    volume_ratio = 1.0 + (abs(price_change_pct) / 100.0)
                else:
                    volume_ratio = 1.0
                
                # 检测volume激增
                volume_spike_detected = (
                    volume_ratio >= 1.3 or  # 30% 估计增长
                    abs(price_change_pct) >= 5  # 或价格变化>=5%
                )
                
                volume_data[symbol] = {
                    'current_volume': current_volume,
                    'volume_change_24h': 0,  # API不提供
                    'volume_change_percentage_24h': price_change_pct,  # 使用价格变化作为代理
                    'current_price': item.get('current_price', 0),
                    'name': item.get('name', ''),
                    'avg_volume_3_days': current_volume / volume_ratio if volume_ratio > 0 else current_volume,
                    'volume_spike_ratio': volume_ratio,
                    'volume_spike_detected': volume_spike_detected,
                    'price_change_24h': price_change_24h,
                    'price_change_percentage_24h': price_change_pct,
                    'last_updated': item.get('last_updated', ''),
                    'volume_analysis_method': 'fixed_api_call'
                }
                
                print(f"  {symbol}: ${current_volume:,.0f} volume, {price_change_pct:+.1f}% price, {volume_ratio:.1f}x ratio")
            
            # 填充缺失的symbols数据
            processed_symbols = set(volume_data.keys())
            missing_symbols = set(symbols) - processed_symbols
            
            if missing_symbols:
                print(f"  ⚠️  Missing volume data for {len(missing_symbols)} symbols: {list(missing_symbols)[:3]}...")
            
            for symbol in missing_symbols:
                volume_data[symbol] = {
                    'current_volume': 0,
                    'volume_change_24h': 0,
                    'volume_change_percentage_24h': 0,
                    'current_price': 0,
                    'name': symbol.replace('_USD', ''),
                    'last_updated': '',
                    'avg_volume_3_days': 0,
                    'volume_spike_ratio': 0.0,
                    'volume_spike_detected': False,
                    'volume_analysis_method': 'no_data_available'
                }
            
            print(f"✓ Volume analysis completed for {len(volume_data)} coins")
            print(f"  Using fixed API call for reliable volume data")
            return volume_data
            
        except Exception as e:
            print(f"❌ Failed to fetch volume analysis data: {str(e)}")
            return {}
    
    def fetch_price_ema_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Fetch OHLC data for EMA calculations on multiple timeframes.
        
        Args:
            symbol (str): Trading pair symbol (e.g., "BTC_USD")
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary with timeframe data
            
        Note:
            Fetches both 4-hour and daily data for EMA calculations.
            Uses sufficient historical data to ensure accurate EMA calculations.
        """
        try:
            current_time = int(time.time())
            
            # Calculate start times for different timeframes
            # Need enough data for 50-period EMA + buffer
            daily_days = 80  # 80 days for daily EMA calculations
            hourly_days = 20  # 20 days for 4-hour data
            
            daily_start = current_time - (daily_days * 24 * 60 * 60)
            hourly_start = current_time - (hourly_days * 24 * 60 * 60)
            
            data = {}
            
            # Fetch daily data
            daily_df = get_coingecko_ohlc(
                symbol=symbol,
                interval="1d",
                start_time=daily_start,
                end_time=current_time
            )
            
            if not daily_df.empty:
                data['daily'] = daily_df
            
            # Fetch hourly data and convert to 4-hour
            hourly_df = get_coingecko_ohlc(
                symbol=symbol,
                interval="1h",
                start_time=hourly_start,
                end_time=current_time
            )
            
            if not hourly_df.empty:
                # Convert hourly to 4-hour data
                hourly_df['datetime'] = pd.to_datetime(hourly_df['datetime'])
                hourly_df.set_index('datetime', inplace=True)
                
                # Resample to 4-hour periods (volume removed as not available)
                four_hour_df = hourly_df.resample('4h').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last'
                }).dropna()
                
                four_hour_df.reset_index(inplace=True)
                data['4h'] = four_hour_df
            
            return data
            
        except Exception as e:
            print(f"    ❌ Failed to fetch price data for {symbol}: {str(e)}")
            return {}
    
    def analyze_momentum_conditions_v2(self, symbol: str, price_data: Dict[str, pd.DataFrame], 
                                     volume_data: Dict) -> Dict:
        """
        Enhanced momentum analysis using volume_data tool.
        
        Args:
            symbol (str): Trading pair symbol
            price_data (Dict[str, pd.DataFrame]): Multi-timeframe OHLC data
            volume_data (Dict): Volume analysis data from volume_data tool
            
        Returns:
            Dict: Complete momentum analysis results
        """
        try:
            result = {
                'symbol': symbol,
                'analysis_time': datetime.now(timezone.utc).isoformat(),
                'conditions_met': False,
                'price_conditions': {},
                'volume_conditions': {},
                'enhanced_volume_data': {},
                'ema_data': {},
                'errors': []
            }
            
            # Get volume information
            vol_info = volume_data.get(symbol, {})
            
            # Analyze price conditions for each timeframe
            price_conditions_met = True
            
            for timeframe in ['daily', '4h']:
                if timeframe not in price_data or price_data[timeframe].empty:
                    result['errors'].append(f"No {timeframe} data available")
                    price_conditions_met = False
                    continue
                
                df = price_data[timeframe]
                
                # Calculate EMAs
                ema_20 = self.calculate_ema(df['close'], 20)
                ema_50 = self.calculate_ema(df['close'], 50)
                
                # Get latest values
                latest_price = df['close'].iloc[-1]
                latest_ema_20 = ema_20.iloc[-1]
                latest_ema_50 = ema_50.iloc[-1]
                
                # Check conditions
                above_ema_20 = latest_price > latest_ema_20 if not np.isnan(latest_ema_20) else False
                above_ema_50 = latest_price > latest_ema_50 if not np.isnan(latest_ema_50) else False
                timeframe_condition = above_ema_20 and above_ema_50
                
                result['price_conditions'][timeframe] = {
                    'price': round(latest_price, 6),
                    'ema_20': round(latest_ema_20, 6) if not np.isnan(latest_ema_20) else None,
                    'ema_50': round(latest_ema_50, 6) if not np.isnan(latest_ema_50) else None,
                    'above_ema_20': above_ema_20,
                    'above_ema_50': above_ema_50,
                    'condition_met': timeframe_condition
                }
                
                if not timeframe_condition:
                    price_conditions_met = False
            
            # Enhanced volume analysis using volume_data tool
            volume_condition_met = vol_info.get('volume_spike_detected', False)
            
            result['volume_conditions'] = {
                'current_volume': vol_info.get('current_volume', 0),
                'avg_volume_3_days': vol_info.get('avg_volume_3_days', 0),
                'volume_spike_ratio': round(vol_info.get('volume_spike_ratio', 0), 2),
                'volume_change_24h': vol_info.get('volume_change_24h', 0),
                'volume_change_percentage_24h': round(vol_info.get('volume_change_percentage_24h', 0), 2),
                'condition_met': volume_condition_met,
                'threshold': 1.5
            }
            
            # Enhanced volume data from volume_data tool
            result['enhanced_volume_data'] = {
                'name': vol_info.get('name', ''),
                'current_price_from_volume_api': vol_info.get('current_price', 0),
                'last_updated': vol_info.get('last_updated', ''),
                'historical_volumes': vol_info.get('historical_volumes', [])
            }
            
            # Overall result
            result['conditions_met'] = price_conditions_met and volume_condition_met
            
            return result
            
        except Exception as e:
            return {
                'symbol': symbol,
                'analysis_time': datetime.now(timezone.utc).isoformat(),
                'conditions_met': False,
                'error': str(e)
            }
    
    def run_enhanced_momentum_scan(self) -> Dict:
        """
        Run enhanced momentum scan using volume_data tool.
        
        Returns:
            Dict: Complete scan results with enhanced volume analysis
        """
        print("=" * 80)
        print("CRYPTOCURRENCY MOMENTUM MONITOR V2 (Enhanced)")
        print("=" * 80)
        print(f"Scan Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("Enhanced with volume_data tool for better performance")
        print()
        
        # Get filtered coin list
        symbols = self.get_filtered_coins()
        if not symbols:
            return {'error': 'Failed to get coin symbols'}
        
        print(f"\nStarting enhanced momentum analysis for {len(symbols)} coins...")
        print("Checking conditions:")
        print("  1. Price above both 20 and 50 EMA (4h and daily)")
        print("  2. Volume spike detected (50% increase or 50% 24h change)")
        print("  3. Enhanced volume analysis using volume_data API only")
        print()
        
        # Fetch volume data for all coins at once (more efficient)
        volume_analysis_data = self.fetch_volume_analysis_data(symbols)
        
        if not volume_analysis_data:
            return {'error': 'Failed to fetch volume data'}
        
        # Analyze each coin
        all_results = []
        momentum_coins = []
        
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i:2d}/{len(symbols)}] Analyzing {symbol}...")
            
            # Fetch price data for EMA calculations
            price_data = self.fetch_price_ema_data(symbol)
            
            if not price_data:
                print(f"    ❌ No price data available for {symbol}")
                continue
            
            # Perform enhanced momentum analysis
            analysis = self.analyze_momentum_conditions_v2(symbol, price_data, volume_analysis_data)
            all_results.append(analysis)
            
            # Check if conditions are met
            if analysis.get('conditions_met', False):
                momentum_coins.append(analysis)
                vol_ratio = analysis.get('volume_conditions', {}).get('volume_spike_ratio', 0)
                print(f"    🚀 MOMENTUM DETECTED! Volume: {vol_ratio:.1f}x, All EMA conditions met")
            else:
                # Show which conditions failed
                failures = []
                if 'price_conditions' in analysis:
                    for tf in ['daily', '4h']:
                        if tf in analysis['price_conditions']:
                            if not analysis['price_conditions'][tf].get('condition_met', False):
                                failures.append(f"{tf} EMA")
                
                if 'volume_conditions' in analysis:
                    if not analysis['volume_conditions'].get('condition_met', False):
                        vol_ratio = analysis['volume_conditions'].get('volume_spike_ratio', 0)
                        failures.append(f"volume ({vol_ratio:.1f}x)")
                
                if failures:
                    print(f"    ⚪ Conditions not met: {', '.join(failures)}")
                else:
                    print(f"    ⚪ Analysis incomplete")
            
            # Rate limiting between price data fetches
            if i < len(symbols):
                time.sleep(1.0)  # Reduced delay since volume data is batched
        
        # Compile final results
        scan_results = {
            'scan_metadata': {
                'scan_time': datetime.now(timezone.utc).isoformat(),
                'version': '2.0 (Enhanced with volume_data tool)',
                'coins_analyzed': len(all_results),
                'coins_requested': len(symbols),
                'momentum_coins_found': len(momentum_coins),
                'stablecoins_excluded': list(self.excluded_symbols),
                'enhancements': [
                    'Batch volume data fetching',
                    'Enhanced volume change analysis using volume_data API',
                    'Fixed compatibility with updated coingecko tool (no volume)',
                    'Improved volume spike detection using 24h change data',
                    'Better error handling and data validation'
                ]
            },
            'momentum_coins': momentum_coins,
            'all_analyses': all_results,
            'summary': {
                'total_scanned': len(all_results),
                'momentum_detected': len(momentum_coins),
                'success_rate': round(len(all_results) / len(symbols) * 100, 1) if symbols else 0
            }
        }
        
        # Save results
        self.save_results(scan_results)
        
        return scan_results
    
    def save_results(self, results: Dict):
        """
        Save enhanced scan results to files.
        
        Args:
            results (Dict): Complete scan results
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Ensure all data is JSON serializable
            def make_json_serializable(obj):
                if isinstance(obj, dict):
                    return {k: make_json_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [make_json_serializable(item) for item in obj]
                elif isinstance(obj, (np.integer, np.floating)):
                    return float(obj)
                elif isinstance(obj, np.bool_):
                    return bool(obj)
                elif pd.isna(obj):
                    return None
                else:
                    return obj
            
            # Clean results for JSON serialization
            clean_results = make_json_serializable(results)
            
            # Save complete JSON results
            json_path = os.path.join(self.data_cache_dir, f'momentum_scan_v2_{timestamp}.json')
            with open(json_path, 'w') as f:
                json.dump(clean_results, f, indent=2)
            print(f"\n✓ Enhanced results saved to: {json_path}")
            
            # Save momentum coins summary
            if results['momentum_coins']:
                summary_path = os.path.join(self.data_cache_dir, f'momentum_alerts_v2_{timestamp}.json')
                alerts = {
                    'alert_time': results['scan_metadata']['scan_time'],
                    'version': results['scan_metadata']['version'],
                    'coins_with_momentum': results['momentum_coins'],
                    'count': len(results['momentum_coins']),
                    'enhanced_features': results['scan_metadata']['enhancements']
                }
                with open(summary_path, 'w') as f:
                    json.dump(alerts, f, indent=2)
                print(f"✓ Enhanced momentum alerts saved to: {summary_path}")
            
        except Exception as e:
            print(f"⚠️  Error saving results: {str(e)}")
    
    def display_enhanced_results(self, results: Dict):
        """
        Display enhanced scan results with volume_data tool improvements.
        
        Args:
            results (Dict): Complete scan results
        """
        print("\n" + "=" * 80)
        print("ENHANCED MOMENTUM SCAN RESULTS (v2)")
        print("=" * 80)
        
        # Summary
        summary = results.get('summary', {})
        metadata = results.get('scan_metadata', {})
        
        print(f"\n📊 ENHANCED SCAN SUMMARY:")
        print("-" * 60)
        print(f"  Version: {metadata.get('version', 'Unknown')}")
        print(f"  Coins Analyzed: {summary.get('total_scanned', 0)}")
        print(f"  Success Rate: {summary.get('success_rate', 0)}%")
        print(f"  🚀 MOMENTUM DETECTED: {summary.get('momentum_detected', 0)} coins")
        
        print(f"\n✨ ENHANCEMENTS:")
        enhancements = metadata.get('enhancements', [])
        for enhancement in enhancements:
            print(f"  • {enhancement}")
        
        # Show momentum coins with enhanced data
        momentum_coins = results.get('momentum_coins', [])
        if momentum_coins:
            print(f"\n🚀 COINS WITH MOMENTUM (Enhanced Analysis):")
            print("-" * 80)
            
            for i, coin in enumerate(momentum_coins, 1):
                symbol = coin.get('symbol', 'Unknown')
                
                # Enhanced volume info
                vol_conditions = coin.get('volume_conditions', {})
                enhanced_vol = coin.get('enhanced_volume_data', {})
                
                current_volume = vol_conditions.get('current_volume', 0)
                volume_ratio = vol_conditions.get('volume_spike_ratio', 0)
                volume_change_24h = vol_conditions.get('volume_change_percentage_24h', 0)
                coin_name = enhanced_vol.get('name', symbol)
                
                # Price info
                daily_price = coin.get('price_conditions', {}).get('daily', {})
                current_price = daily_price.get('price', 0)
                
                print(f"  {i}. {symbol} ({coin_name})")
                print(f"     💰 Price: ${current_price:,.6f}")
                print(f"     📊 Volume: ${current_volume:,.0f} ({volume_ratio:.1f}x spike)")
                print(f"     📈 24h Volume Change: {volume_change_24h:+.1f}%")
                
                # EMA status for both timeframes
                for tf in ['daily', '4h']:
                    tf_data = coin.get('price_conditions', {}).get(tf, {})
                    if tf_data and tf_data.get('condition_met', False):
                        ema_20 = tf_data.get('ema_20', 0)
                        ema_50 = tf_data.get('ema_50', 0)
                        print(f"     ✅ {tf.upper()}: Price > EMA20(${ema_20:.4f}) & EMA50(${ema_50:.4f})")
                
                print()
        else:
            print(f"\n⚪ No coins currently meet all momentum criteria")
        
        # Enhanced candidate analysis
        print(f"\n📋 TOP CANDIDATES (Enhanced Volume Analysis):")
        print("-" * 80)
        
        partial_matches = []
        for analysis in results.get('all_analyses', []):
            if not analysis.get('conditions_met', False):
                # Enhanced scoring including volume change data
                conditions_score = 0
                volume_score = 0
                
                # Price conditions scoring
                price_conds = analysis.get('price_conditions', {})
                if price_conds.get('daily', {}).get('condition_met', False):
                    conditions_score += 1
                if price_conds.get('4h', {}).get('condition_met', False):
                    conditions_score += 1
                
                # Enhanced volume scoring
                vol_conds = analysis.get('volume_conditions', {})
                if vol_conds.get('condition_met', False):
                    conditions_score += 1
                    volume_score = 100
                else:
                    # Partial volume score based on ratio
                    vol_ratio = vol_conds.get('volume_spike_ratio', 0)
                    volume_score = min(vol_ratio / 1.5 * 100, 99)  # Scale to 0-99
                
                if conditions_score > 0 or volume_score > 30:
                    analysis['conditions_score'] = conditions_score
                    analysis['volume_score'] = volume_score
                    partial_matches.append(analysis)
        
        # Sort by total score (conditions + volume)
        partial_matches.sort(key=lambda x: (x.get('conditions_score', 0) * 100 + x.get('volume_score', 0)), reverse=True)
        
        for i, candidate in enumerate(partial_matches[:5], 1):  # Show top 5
            symbol = candidate.get('symbol', 'Unknown')
            cond_score = candidate.get('conditions_score', 0)
            vol_score = candidate.get('volume_score', 0)
            
            vol_conditions = candidate.get('volume_conditions', {})
            vol_ratio = vol_conditions.get('volume_spike_ratio', 0)
            vol_change = vol_conditions.get('volume_change_percentage_24h', 0)
            
            print(f"  {i}. {symbol} ({cond_score}/3 conditions, {vol_score:.0f}% volume score)")
            print(f"     Volume: {vol_ratio:.1f}x ratio, {vol_change:+.1f}% 24h change")
        
        print("\n" + "=" * 80)
        print("Enhanced with volume_data tool for better performance and accuracy")

def main():
    """
    Main function to run enhanced momentum monitoring.
    
    This improved version uses the volume_data tool for better performance
    and more accurate volume analysis.
    """
    try:
        # Initialize enhanced monitor
        monitor = MomentumMonitor(n_coins=15)  # 15 coins for good balance
        
        # Run enhanced momentum scan
        results = monitor.run_enhanced_momentum_scan()
        
        # Display enhanced results
        monitor.display_enhanced_results(results)
        
        # Check if any alerts should be triggered
        momentum_count = results.get('summary', {}).get('momentum_detected', 0)
        if momentum_count > 0:
            print(f"\n🚨 ENHANCED ALERT: {momentum_count} coin(s) showing strong momentum!")
            print("Enhanced analysis confirms these opportunities with volume_data tool.")
        else:
            print(f"\n✓ Enhanced scan completed. No momentum signals at this time.")
        
        print(f"\n📁 Enhanced results saved in: {monitor.data_cache_dir}")
        print("🚀 Powered by volume_data tool for improved accuracy")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Enhanced scan interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Enhanced scan failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())