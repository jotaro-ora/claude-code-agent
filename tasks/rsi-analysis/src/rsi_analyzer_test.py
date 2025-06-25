#!/usr/bin/env python3
"""
RSI Analyzer Test Script

This script tests the RSI analyzer with a smaller subset of coins
to verify functionality before running the full analysis.

This version tests with top 5 coins for faster execution and debugging.
"""

import sys
import os

# Add project root to Python path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from rsi_analyzer import RSIAnalyzer

def main():
    """
    Test RSI analyzer with a small subset of coins.
    """
    try:
        print("Testing RSI Analyzer with Top 5 Coins...")
        print("=" * 50)
        
        # Initialize analyzer with smaller parameters for testing
        analyzer = RSIAnalyzer(
            n_coins=5,          # Test with only 5 coins
            rsi_period=14,      # Standard RSI period
            data_period_days=21 # Reduced data period for faster testing
        )
        
        # Run analysis
        results = analyzer.run_analysis()
        
        # Check if analysis was successful
        if 'error' in results:
            print(f"❌ Analysis failed: {results['error']}")
            return 1
        
        # Display results
        analyzer.display_results()
        
        print(f"\n✅ Test completed successfully!")
        print(f"📁 Results saved in: {analyzer.cache_dir}")
        
        # Validate key results
        if results['analysis_metadata']['total_successful'] > 0:
            print(f"✅ Successfully analyzed {results['analysis_metadata']['total_successful']} coins")
            return 0
        else:
            print("❌ No coins were successfully analyzed")
            return 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())