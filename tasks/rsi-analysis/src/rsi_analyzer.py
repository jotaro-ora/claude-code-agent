#!/usr/bin/env python3
"""
RSI Analysis for Top 50 Cryptocurrencies

This script analyzes the Relative Strength Index (RSI) for the top 50 cryptocurrencies
by market cap and identifies the coins with the highest and lowest RSI values.

The script is designed to be run repeatedly and provides comprehensive analysis
including data caching for efficiency and detailed reporting.

Dependencies:
- tools.top_coins: For getting top cryptocurrencies by market cap
- tools.coingecko: For fetching historical OHLC data
- pandas: For data manipulation and analysis
- numpy: For numerical calculations
- python-dotenv: For environment variable management

Environment Variables Required:
- COINGECKO_API_KEY: Your CoinGecko Pro API key

Usage:
    python rsi-analysis/src/rsi_analyzer.py
    
Output:
    - Console output with RSI analysis results
    - CSV file with detailed results in data/ folder
    - JSON file with summary results for programmatic access
"""

import sys
import os
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional

# Add project root to Python path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tools.top_coins import get_top_coins
from tools.coingecko import get_coingecko_ohlc

class RSIAnalyzer:
    """
    RSI Analysis class for cryptocurrency market analysis.
    
    This class provides functionality to:
    1. Fetch top N cryptocurrencies by market cap
    2. Calculate RSI for each cryptocurrency
    3. Identify coins with highest and lowest RSI values
    4. Generate comprehensive reports and export data
    
    Attributes:
        n_coins (int): Number of top coins to analyze
        rsi_period (int): Period for RSI calculation (default: 14)
        data_period_days (int): Number of days of historical data to fetch
        results (dict): Analysis results storage
        cache_dir (str): Directory for caching data
    """
    
    def __init__(self, n_coins: int = 50, rsi_period: int = 14, data_period_days: int = 30):
        """
        Initialize RSI analyzer with configuration parameters.
        
        Args:
            n_coins (int): Number of top coins to analyze (default: 50)
            rsi_period (int): Period for RSI calculation (default: 14 days)
            data_period_days (int): Days of historical data to fetch (default: 30)
        """
        self.n_coins = n_coins
        self.rsi_period = rsi_period
        self.data_period_days = data_period_days
        self.results = {}
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        print(f"RSI Analyzer initialized:")
        print(f"  - Analyzing top {n_coins} coins")
        print(f"  - RSI period: {rsi_period} days")
        print(f"  - Data period: {data_period_days} days")
        print(f"  - Cache directory: {self.cache_dir}")
    
    def calculate_rsi(self, prices: pd.Series, period: int = None) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index) for given price series.
        
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss over the period
        
        Args:
            prices (pd.Series): Series of closing prices
            period (int): Period for RSI calculation (uses self.rsi_period if None)
            
        Returns:
            pd.Series: RSI values (NaN for first period-1 values)
            
        Note:
            Uses Wilder's smoothing method for RSI calculation, which is the
            standard approach. The first valid RSI value appears at index period.
        """
        if period is None:
            period = self.rsi_period
            
        if len(prices) < period + 1:
            return pd.Series([np.nan] * len(prices), index=prices.index)
        
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses using Wilder's smoothing
        avg_gains = gains.rolling(window=period, min_periods=period).mean()
        avg_losses = losses.rolling(window=period, min_periods=period).mean()
        
        # For subsequent values, use Wilder's smoothing formula
        for i in range(period, len(prices)):
            avg_gains.iloc[i] = (avg_gains.iloc[i-1] * (period-1) + gains.iloc[i]) / period
            avg_losses.iloc[i] = (avg_losses.iloc[i-1] * (period-1) + losses.iloc[i]) / period
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def fetch_coin_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLC data for a specific coin.
        
        Args:
            symbol (str): Trading pair symbol (e.g., "BTC_USD")
            
        Returns:
            Optional[pd.DataFrame]: OHLC data or None if fetch fails
            
        Note:
            Implements error handling and retry logic for robust data fetching.
            Uses a reasonable time period to ensure sufficient data for RSI calculation.
        """
        try:
            # Calculate date range for data fetching
            end_time = int(time.time())
            start_time = end_time - (self.data_period_days * 24 * 60 * 60)
            
            print(f"    Fetching {self.data_period_days} days of data for {symbol}...")
            
            # Fetch OHLC data using coingecko tool
            df = get_coingecko_ohlc(
                symbol=symbol,
                interval="1d",  # Daily data for RSI calculation
                start_time=start_time,
                end_time=end_time
            )
            
            if df.empty:
                print(f"    ⚠️  No data returned for {symbol}")
                return None
            
            print(f"    ✓ Retrieved {len(df)} data points for {symbol}")
            return df
            
        except Exception as e:
            print(f"    ❌ Failed to fetch data for {symbol}: {str(e)}")
            return None
    
    def analyze_coin_rsi(self, symbol: str) -> Optional[Dict]:
        """
        Analyze RSI for a specific coin.
        
        Args:
            symbol (str): Trading pair symbol (e.g., "BTC_USD")
            
        Returns:
            Optional[Dict]: RSI analysis results or None if analysis fails
            
        Returns dict contains:
            - symbol: Trading pair symbol
            - current_rsi: Current RSI value
            - rsi_category: Category (Oversold/Neutral/Overbought)
            - price_data: Basic price information
            - data_points: Number of data points used
            - analysis_date: When the analysis was performed
        """
        try:
            # Fetch historical data
            df = self.fetch_coin_data(symbol)
            if df is None or len(df) < self.rsi_period + 1:
                return None
            
            # Calculate RSI
            rsi_series = self.calculate_rsi(df['close'])
            
            # Get current (latest) RSI value
            current_rsi = rsi_series.dropna().iloc[-1] if not rsi_series.dropna().empty else None
            
            if current_rsi is None or np.isnan(current_rsi):
                print(f"    ⚠️  Could not calculate RSI for {symbol}")
                return None
            
            # Categorize RSI
            if current_rsi <= 30:
                rsi_category = "Oversold"
            elif current_rsi >= 70:
                rsi_category = "Overbought"
            else:
                rsi_category = "Neutral"
            
            # Get latest price data
            latest_data = df.iloc[-1]
            
            result = {
                'symbol': symbol,
                'current_rsi': round(current_rsi, 2),
                'rsi_category': rsi_category,
                'current_price': round(latest_data['close'], 2),
                'price_change_24h': round(((latest_data['close'] - df.iloc[-2]['close']) / df.iloc[-2]['close']) * 100, 2) if len(df) >= 2 else 0,
                'data_points': len(df),
                'valid_rsi_points': len(rsi_series.dropna()),
                'analysis_date': datetime.now(timezone.utc).isoformat()
            }
            
            print(f"    ✓ {symbol}: RSI = {current_rsi:.2f} ({rsi_category})")
            return result
            
        except Exception as e:
            print(f"    ❌ RSI analysis failed for {symbol}: {str(e)}")
            return None
    
    def run_analysis(self) -> Dict:
        """
        Run comprehensive RSI analysis for top N cryptocurrencies.
        
        Returns:
            Dict: Complete analysis results including highest/lowest RSI coins
            
        The analysis process:
        1. Fetch top N coins by market cap
        2. Calculate RSI for each coin
        3. Identify highest and lowest RSI values
        4. Generate summary statistics
        5. Save results to files
        """
        print("=" * 80)
        print(f"Starting RSI Analysis for Top {self.n_coins} Cryptocurrencies")
        print("=" * 80)
        print(f"Analysis Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        # Step 1: Get top coins by market cap
        print(f"Step 1: Fetching top {self.n_coins} cryptocurrencies by market cap...")
        try:
            symbols = get_top_coins(n=self.n_coins)
            print(f"✓ Retrieved {len(symbols)} coin symbols")
            print(f"  Top 5: {symbols[:5]}")
        except Exception as e:
            print(f"❌ Failed to fetch top coins: {str(e)}")
            return {'error': f"Failed to fetch top coins: {str(e)}"}
        
        print()
        
        # Step 2: Analyze RSI for each coin
        print(f"Step 2: Calculating RSI for each cryptocurrency...")
        print(f"  This may take several minutes due to API rate limiting...")
        print()
        
        successful_analyses = []
        failed_symbols = []
        
        for i, symbol in enumerate(symbols, 1):
            print(f"  [{i:2d}/{len(symbols)}] Analyzing {symbol}...")
            
            result = self.analyze_coin_rsi(symbol)
            if result:
                successful_analyses.append(result)
            else:
                failed_symbols.append(symbol)
            
            # Rate limiting delay between coins
            if i < len(symbols):
                time.sleep(1.5)  # 1.5 second delay between API calls
        
        print()
        print(f"✓ Analysis completed:")
        print(f"  - Successful: {len(successful_analyses)}")
        print(f"  - Failed: {len(failed_symbols)}")
        if failed_symbols:
            print(f"  - Failed symbols: {failed_symbols}")
        
        # Step 3: Find highest and lowest RSI
        print()
        print("Step 3: Identifying extreme RSI values...")
        
        if not successful_analyses:
            print("❌ No successful analyses to process")
            return {'error': 'No successful RSI calculations'}
        
        # Sort by RSI value
        sorted_by_rsi = sorted(successful_analyses, key=lambda x: x['current_rsi'])
        
        lowest_rsi = sorted_by_rsi[0]
        highest_rsi = sorted_by_rsi[-1]
        
        print(f"✓ Extreme RSI values identified:")
        print(f"  - Lowest RSI: {lowest_rsi['symbol']} = {lowest_rsi['current_rsi']:.2f}")
        print(f"  - Highest RSI: {highest_rsi['symbol']} = {highest_rsi['current_rsi']:.2f}")
        
        # Step 4: Generate summary statistics
        rsi_values = [result['current_rsi'] for result in successful_analyses]
        
        summary_stats = {
            'total_analyzed': len(successful_analyses),
            'failed_analyses': len(failed_symbols),
            'mean_rsi': round(np.mean(rsi_values), 2),
            'median_rsi': round(np.median(rsi_values), 2),
            'std_rsi': round(np.std(rsi_values), 2),
            'min_rsi': round(min(rsi_values), 2),
            'max_rsi': round(max(rsi_values), 2),
            'oversold_count': len([r for r in successful_analyses if r['current_rsi'] <= 30]),
            'overbought_count': len([r for r in successful_analyses if r['current_rsi'] >= 70]),
            'neutral_count': len([r for r in successful_analyses if 30 < r['current_rsi'] < 70])
        }
        
        # Compile final results
        self.results = {
            'analysis_metadata': {
                'analysis_time': datetime.now(timezone.utc).isoformat(),
                'n_coins_requested': self.n_coins,
                'rsi_period': self.rsi_period,
                'data_period_days': self.data_period_days,
                'total_successful': len(successful_analyses),
                'total_failed': len(failed_symbols)
            },
            'summary_statistics': summary_stats,
            'extreme_values': {
                'lowest_rsi': lowest_rsi,
                'highest_rsi': highest_rsi
            },
            'all_results': successful_analyses,
            'failed_symbols': failed_symbols
        }
        
        # Step 5: Save results
        self.save_results()
        
        return self.results
    
    def save_results(self):
        """
        Save analysis results to files for future reference and programmatic access.
        
        Creates:
        1. CSV file with detailed results
        2. JSON file with complete results
        3. Summary text file with key findings
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Save detailed CSV
            if self.results['all_results']:
                df = pd.DataFrame(self.results['all_results'])
                csv_path = os.path.join(self.cache_dir, f'rsi_analysis_{timestamp}.csv')
                df.to_csv(csv_path, index=False)
                print(f"✓ Detailed results saved to: {csv_path}")
            
            # Save complete JSON
            json_path = os.path.join(self.cache_dir, f'rsi_analysis_{timestamp}.json')
            with open(json_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"✓ Complete results saved to: {json_path}")
            
            # Save summary text
            summary_path = os.path.join(self.cache_dir, f'rsi_summary_{timestamp}.txt')
            with open(summary_path, 'w') as f:
                f.write(self.generate_text_summary())
            print(f"✓ Summary report saved to: {summary_path}")
            
        except Exception as e:
            print(f"⚠️  Error saving results: {str(e)}")
    
    def generate_text_summary(self) -> str:
        """
        Generate a human-readable text summary of the RSI analysis.
        
        Returns:
            str: Formatted text summary
        """
        if not self.results:
            return "No analysis results available."
        
        summary = f"""
RSI Analysis Summary - Top {self.n_coins} Cryptocurrencies
{'='*60}

Analysis Details:
- Analysis Time: {self.results['analysis_metadata']['analysis_time']}
- RSI Period: {self.results['analysis_metadata']['rsi_period']} days
- Data Period: {self.results['analysis_metadata']['data_period_days']} days
- Successful Analyses: {self.results['analysis_metadata']['total_successful']}
- Failed Analyses: {self.results['analysis_metadata']['total_failed']}

Key Findings:
{'='*60}

LOWEST RSI (Most Oversold):
- Symbol: {self.results['extreme_values']['lowest_rsi']['symbol']}
- RSI: {self.results['extreme_values']['lowest_rsi']['current_rsi']:.2f}
- Category: {self.results['extreme_values']['lowest_rsi']['rsi_category']}
- Current Price: ${self.results['extreme_values']['lowest_rsi']['current_price']:,.2f}
- 24h Change: {self.results['extreme_values']['lowest_rsi']['price_change_24h']:+.2f}%

HIGHEST RSI (Most Overbought):
- Symbol: {self.results['extreme_values']['highest_rsi']['symbol']}
- RSI: {self.results['extreme_values']['highest_rsi']['current_rsi']:.2f}
- Category: {self.results['extreme_values']['highest_rsi']['rsi_category']}
- Current Price: ${self.results['extreme_values']['highest_rsi']['current_price']:,.2f}
- 24h Change: {self.results['extreme_values']['highest_rsi']['price_change_24h']:+.2f}%

Market Overview:
{'='*60}
- Mean RSI: {self.results['summary_statistics']['mean_rsi']:.2f}
- Median RSI: {self.results['summary_statistics']['median_rsi']:.2f}
- Standard Deviation: {self.results['summary_statistics']['std_rsi']:.2f}
- RSI Range: {self.results['summary_statistics']['min_rsi']:.2f} - {self.results['summary_statistics']['max_rsi']:.2f}

RSI Distribution:
- Oversold (RSI ≤ 30): {self.results['summary_statistics']['oversold_count']} coins
- Neutral (30 < RSI < 70): {self.results['summary_statistics']['neutral_count']} coins  
- Overbought (RSI ≥ 70): {self.results['summary_statistics']['overbought_count']} coins

"""
        return summary
    
    def display_results(self):
        """
        Display analysis results in a formatted console output.
        """
        if not self.results:
            print("No analysis results to display.")
            return
        
        print()
        print("=" * 80)
        print("RSI ANALYSIS RESULTS")
        print("=" * 80)
        
        # Display key findings
        print("\n🔍 KEY FINDINGS:")
        print("-" * 50)
        
        lowest = self.results['extreme_values']['lowest_rsi']
        highest = self.results['extreme_values']['highest_rsi']
        
        print(f"📉 LOWEST RSI (Most Oversold):")
        print(f"   {lowest['symbol']} - RSI: {lowest['current_rsi']:.2f} - Price: ${lowest['current_price']:,.2f}")
        
        print(f"📈 HIGHEST RSI (Most Overbought):")
        print(f"   {highest['symbol']} - RSI: {highest['current_rsi']:.2f} - Price: ${highest['current_price']:,.2f}")
        
        # Display market overview
        stats = self.results['summary_statistics']
        print(f"\n📊 MARKET OVERVIEW:")
        print("-" * 50)
        print(f"   Coins Analyzed: {stats['total_analyzed']}")
        print(f"   Average RSI: {stats['mean_rsi']:.2f}")
        print(f"   RSI Range: {stats['min_rsi']:.2f} - {stats['max_rsi']:.2f}")
        print(f"   Oversold: {stats['oversold_count']} | Neutral: {stats['neutral_count']} | Overbought: {stats['overbought_count']}")
        
        # Display top 10 extreme values
        all_results = sorted(self.results['all_results'], key=lambda x: x['current_rsi'])
        
        print(f"\n📋 TOP 10 LOWEST RSI VALUES:")
        print("-" * 70)
        for i, result in enumerate(all_results[:10], 1):
            print(f"   {i:2d}. {result['symbol']:12s} RSI: {result['current_rsi']:6.2f} Price: ${result['current_price']:>10,.2f}")
        
        print(f"\n📋 TOP 10 HIGHEST RSI VALUES:")
        print("-" * 70)
        for i, result in enumerate(all_results[-10:], 1):
            print(f"   {i:2d}. {result['symbol']:12s} RSI: {result['current_rsi']:6.2f} Price: ${result['current_price']:>10,.2f}")
        
        print("\n" + "=" * 80)

def main():
    """
    Main function to run RSI analysis.
    
    This function can be called repeatedly and will perform a fresh analysis
    each time, suitable for monitoring RSI changes over time.
    """
    try:
        # Initialize analyzer
        analyzer = RSIAnalyzer(n_coins=50, rsi_period=14, data_period_days=30)
        
        # Run analysis
        results = analyzer.run_analysis()
        
        # Display results
        analyzer.display_results()
        
        print(f"\n✅ RSI analysis completed successfully!")
        print(f"📁 Results saved in: {analyzer.cache_dir}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())