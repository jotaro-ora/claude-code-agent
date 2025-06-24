#!/usr/bin/env python3
"""
Debug script to investigate data fetching issues.
"""

import sys
import os
import pandas as pd

# Add project root to Python path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tools.top_coins import get_top_coins
from tools.coingecko import get_coingecko_ohlc
import time

def debug_data_fetching():
    """Debug data fetching for different coins."""
    
    print("Debug: Investigating data fetching issues")
    print("=" * 50)
    
    # Get top 3 coins
    print("1. Getting top 3 coins...")
    symbols = get_top_coins(n=3)
    print(f"Symbols: {symbols}")
    print()
    
    # Test each coin individually
    end_time = int(time.time())
    start_time = end_time - (21 * 24 * 60 * 60)  # 21 days
    
    for symbol in symbols:
        print(f"2. Testing {symbol}...")
        try:
            df = get_coingecko_ohlc(
                symbol=symbol,
                interval="1d",
                start_time=start_time,
                end_time=end_time
            )
            
            print(f"   Data shape: {df.shape}")
            print(f"   Columns: {df.columns.tolist()}")
            
            if not df.empty:
                print(f"   Date range: {df['datetime'].min()} to {df['datetime'].max()}")
                print(f"   Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
                print(f"   Sample data:")
                print(df[['datetime', 'close']].tail(3).to_string(index=False))
            else:
                print("   DataFrame is empty!")
                
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        print()

if __name__ == "__main__":
    debug_data_fetching()