#!/usr/bin/env python3
"""
Quick test of momentum monitor v2 with volume_data tool.
"""

import sys
import os

# Add project root to Python path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from momentum_monitor import MomentumMonitor

def main():
    """
    Quick test of enhanced momentum monitor v2.
    """
    try:
        print("Momentum Monitor v2 Quick Test")
        print("=" * 40)
        
        # Test with smaller number of coins
        monitor = MomentumMonitor(n_coins=3)
        
        # Test getting filtered coins
        print("\nTesting coin filtering...")
        symbols = monitor.get_filtered_coins()
        print(f"✓ Got {len(symbols)} filtered symbols: {symbols}")
        
        # Test volume data fetching with new tool
        print("\nTesting enhanced volume data fetching...")
        volume_data = monitor.fetch_volume_analysis_data(symbols)
        
        if volume_data:
            print(f"✓ Volume data fetched for {len(volume_data)} coins")
            for symbol, data in volume_data.items():
                vol_ratio = data.get('volume_spike_ratio', 0)
                current_vol = data.get('current_volume', 0)
                print(f"  {symbol}: Volume {current_vol:,.0f}, Ratio: {vol_ratio:.2f}x")
        else:
            print("❌ No volume data fetched")
            return 1
        
        # Test price data fetching for one coin
        print(f"\nTesting price data fetch for {symbols[0]}...")
        price_data = monitor.fetch_price_ema_data(symbols[0])
        
        if price_data:
            print(f"✓ Price data fetched:")
            for timeframe, df in price_data.items():
                print(f"  {timeframe}: {len(df)} data points")
        
        print("\n✅ v2 Quick test completed successfully!")
        print("✅ Enhanced with volume_data tool integration!")
        return 0
        
    except Exception as e:
        print(f"\n❌ v2 Quick test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())