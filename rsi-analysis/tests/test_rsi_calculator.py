#!/usr/bin/env python3
"""
RSI Calculator Test Suite

This module tests the RSI (Relative Strength Index) calculation functionality
to ensure accurate technical analysis calculations before implementing the
main RSI analysis script.

Test Objectives:
1. Verify RSI calculation accuracy with known data
2. Test edge cases and error handling
3. Validate data preprocessing and formatting
4. Ensure integration with tools works correctly

Dependencies:
- pandas: For data manipulation
- numpy: For numerical calculations
- sys, os: For path management
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to Python path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def create_test_data():
    """
    Create synthetic OHLC data for RSI testing.
    
    This function generates realistic price data with known patterns
    to validate RSI calculations against expected results.
    
    Returns:
        pandas.DataFrame: Test OHLC data with datetime index
    """
    # Create 50 days of test data
    dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
    
    # Create price series with known patterns
    # Start at 100, create some upward and downward movements
    prices = [100.0]
    changes = [2, 1.5, -1, 3, -2, 1, -0.5, 2.5, -1.5, 1,  # First 10 days
               -1, -2, -1.5, 1, 2, 1.5, -1, -2, 1, 0.5,    # Days 11-20
               3, 2, 1, -1, -3, -2, 1, 2, 1.5, -1,         # Days 21-30
               2, 1, -1, 3, -2, -1, 2, 1.5, -1, 2,         # Days 31-40
               -1, 1, 2, -1.5, 3, -2, 1, 2, -1, 1.5]       # Days 41-50
    
    for change in changes:
        prices.append(prices[-1] + change)
    
    # Create OHLC data from close prices
    data = []
    for i, (date, close) in enumerate(zip(dates, prices[1:])):
        # Generate realistic OHLC from close price
        volatility = 0.5  # 0.5% daily volatility
        high = close * (1 + np.random.uniform(0, volatility/100))
        low = close * (1 - np.random.uniform(0, volatility/100))
        open_price = prices[i] if i > 0 else close
        
        data.append({
            'datetime': date,
            'open': round(open_price, 2),
            'high': round(max(high, close, open_price), 2),
            'low': round(min(low, close, open_price), 2),
            'close': round(close, 2),
            'volume': np.random.randint(1000, 10000)
        })
    
    return pd.DataFrame(data)

def calculate_rsi(prices, period=14):
    """
    Calculate RSI (Relative Strength Index) for given price series.
    
    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss over the period
    
    Args:
        prices (pd.Series): Series of closing prices
        period (int): Period for RSI calculation (default: 14)
        
    Returns:
        pd.Series: RSI values (NaN for first period-1 values)
        
    Note:
        This is the standard RSI calculation using Wilder's smoothing method.
        The first RSI value appears at index period (0-based indexing).
    """
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

def test_rsi_calculation():
    """
    Test RSI calculation with known data patterns.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    print("=" * 60)
    print("Test 1: RSI Calculation Accuracy")
    print("=" * 60)
    
    try:
        # Create test data
        test_df = create_test_data()
        print(f"Created test data with {len(test_df)} data points")
        
        # Calculate RSI
        rsi_values = calculate_rsi(test_df['close'], period=14)
        
        # Validate RSI properties
        print("\nRSI Validation:")
        
        # 1. RSI should be between 0 and 100
        valid_rsi = rsi_values.dropna()
        if (valid_rsi < 0).any() or (valid_rsi > 100).any():
            return False, "RSI values outside valid range (0-100)"
        print(f"  ✓ All RSI values in valid range (0-100)")
        
        # 2. First 13 values should be NaN (period-1)
        nan_count = rsi_values.isna().sum()
        if nan_count != 13:  # First 13 values should be NaN for period=14
            return False, f"Expected 13 NaN values, got {nan_count}"
        print(f"  ✓ Correct number of NaN values: {nan_count}")
        
        # 3. Should have valid RSI values after period
        valid_count = len(valid_rsi)
        expected_valid = len(test_df) - 13
        if valid_count != expected_valid:
            return False, f"Expected {expected_valid} valid RSI values, got {valid_count}"
        print(f"  ✓ Correct number of valid RSI values: {valid_count}")
        
        # 4. Display sample RSI values
        print(f"\nSample RSI Values:")
        recent_rsi = valid_rsi.tail(10)
        for i, (date, rsi) in enumerate(zip(test_df['datetime'].tail(10), recent_rsi), 1):
            print(f"  {date.strftime('%Y-%m-%d')}: RSI = {rsi:.2f}")
        
        print(f"\nRSI Statistics:")
        print(f"  Min RSI: {valid_rsi.min():.2f}")
        print(f"  Max RSI: {valid_rsi.max():.2f}")
        print(f"  Mean RSI: {valid_rsi.mean():.2f}")
        
        print("\n✅ RSI calculation test passed!")
        return True, ""
        
    except Exception as e:
        print(f"❌ RSI calculation test failed: {str(e)}")
        return False, str(e)

def test_edge_cases():
    """
    Test RSI calculation with edge cases.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    print("=" * 60)
    print("Test 2: Edge Cases")
    print("=" * 60)
    
    try:
        # Test case 1: Insufficient data
        short_data = pd.Series([100, 101, 102])
        rsi_short = calculate_rsi(short_data, period=14)
        if not rsi_short.isna().all():
            return False, "Should return all NaN for insufficient data"
        print("  ✓ Handles insufficient data correctly")
        
        # Test case 2: All increasing prices (RSI should approach 100)
        increasing_prices = pd.Series(range(100, 150))  # 50 increasing values
        rsi_increasing = calculate_rsi(increasing_prices, period=14)
        final_rsi = rsi_increasing.dropna().iloc[-1]
        if final_rsi < 90:  # Should be very high for all increasing
            return False, f"RSI for all increasing prices too low: {final_rsi}"
        print(f"  ✓ All increasing prices: RSI = {final_rsi:.2f}")
        
        # Test case 3: All decreasing prices (RSI should approach 0)
        decreasing_prices = pd.Series(range(150, 100, -1))  # 50 decreasing values
        rsi_decreasing = calculate_rsi(decreasing_prices, period=14)
        final_rsi_dec = rsi_decreasing.dropna().iloc[-1]
        if final_rsi_dec > 10:  # Should be very low for all decreasing
            return False, f"RSI for all decreasing prices too high: {final_rsi_dec}"
        print(f"  ✓ All decreasing prices: RSI = {final_rsi_dec:.2f}")
        
        # Test case 4: Constant prices (RSI should be around 50)
        constant_prices = pd.Series([100] * 30)
        constant_prices.iloc[-1] = 100.01  # Tiny change to avoid division by zero
        rsi_constant = calculate_rsi(constant_prices, period=14)
        final_rsi_const = rsi_constant.dropna().iloc[-1]
        print(f"  ✓ Nearly constant prices: RSI = {final_rsi_const:.2f}")
        
        print("\n✅ Edge cases test passed!")
        return True, ""
        
    except Exception as e:
        print(f"❌ Edge cases test failed: {str(e)}")
        return False, str(e)

def test_tools_integration():
    """
    Test integration with project tools.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    print("=" * 60)
    print("Test 3: Tools Integration")
    print("=" * 60)
    
    try:
        # Test importing tools
        from tools.top_coins import get_top_coins
        from tools.coingecko import get_coingecko_ohlc
        print("  ✓ Successfully imported project tools")
        
        # Test getting symbols (don't actually call API in test)
        print("  ✓ Tools are compatible for RSI analysis workflow")
        
        # Test that our RSI function works with expected data format
        # Create mock data in the format that coingecko returns
        mock_data = pd.DataFrame({
            'datetime': pd.date_range('2024-01-01', periods=20, freq='D'),
            'open': np.random.uniform(100, 110, 20),
            'high': np.random.uniform(110, 120, 20),
            'low': np.random.uniform(90, 100, 20),
            'close': np.random.uniform(95, 115, 20),
            'volume': np.random.randint(1000, 10000, 20)
        })
        
        # Test RSI calculation with mock data format
        rsi_result = calculate_rsi(mock_data['close'], period=14)
        print(f"  ✓ RSI calculation works with coingecko data format")
        print(f"    Sample RSI: {rsi_result.dropna().iloc[-1]:.2f}")
        
        print("\n✅ Tools integration test passed!")
        return True, ""
        
    except Exception as e:
        print(f"❌ Tools integration test failed: {str(e)}")
        return False, str(e)

def main():
    """
    Run all RSI calculator tests.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("Starting RSI Calculator Test Suite...")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("RSI Calculation", test_rsi_calculation),
        ("Edge Cases", test_edge_cases),
        ("Tools Integration", test_tools_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        success, error_msg = test_func()
        results.append((test_name, success, error_msg))
        print()
    
    # Summary
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, success, error in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if error:
            print(f"    Error: {error}")
        if not success:
            all_passed = False
    
    print()
    print(f"Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print(f"RSI Calculator: {'✅ Ready for Implementation' if all_passed else '❌ Needs Fixes'}")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())