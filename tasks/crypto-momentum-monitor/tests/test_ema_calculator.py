#!/usr/bin/env python3
"""
EMA Calculator Test Suite

This module tests the Exponential Moving Average (EMA) calculation functionality
to ensure accurate technical analysis calculations for cryptocurrency momentum monitoring.

Test Objectives:
1. Verify EMA calculation accuracy with known data
2. Test edge cases and error handling  
3. Validate multiple timeframe EMA calculations
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

def create_test_price_data(days=100, start_price=100.0):
    """
    Create synthetic price data for EMA testing.
    
    This function generates realistic price data with known patterns
    to validate EMA calculations against expected results.
    
    Args:
        days (int): Number of days of data to generate
        start_price (float): Starting price
        
    Returns:
        pandas.DataFrame: Test OHLC data with datetime index
    """
    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
    
    # Create price series with trend and volatility
    prices = [start_price]
    np.random.seed(42)  # For reproducible tests
    
    for i in range(1, days):
        # Add trend and random walk
        trend = 0.001  # Slight upward trend
        volatility = 0.02  # 2% daily volatility
        change = trend + np.random.normal(0, volatility)
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, 0.01))  # Ensure positive prices
    
    # Create OHLC data from close prices
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # Generate realistic OHLC from close price
        volatility_factor = 0.005  # 0.5% intraday volatility
        high = close * (1 + np.random.uniform(0, volatility_factor))
        low = close * (1 - np.random.uniform(0, volatility_factor))
        open_price = prices[i-1] if i > 0 else close
        
        data.append({
            'datetime': date,
            'open': round(open_price, 2),
            'high': round(max(high, close, open_price), 2),
            'low': round(min(low, close, open_price), 2),
            'close': round(close, 2),
            'volume': np.random.randint(10000, 100000)
        })
    
    return pd.DataFrame(data)

def calculate_ema(prices, period):
    """
    Calculate Exponential Moving Average (EMA) for given price series.
    
    EMA = (Price * Multiplier) + (Previous EMA * (1 - Multiplier))
    where Multiplier = 2 / (Period + 1)
    
    Args:
        prices (pd.Series): Series of closing prices
        period (int): Period for EMA calculation
        
    Returns:
        pd.Series: EMA values
        
    Note:
        The first EMA value is calculated as Simple Moving Average (SMA).
        Subsequent values use the exponential smoothing formula.
    """
    if len(prices) < period:
        return pd.Series([np.nan] * len(prices), index=prices.index)
    
    multiplier = 2.0 / (period + 1)
    ema_values = pd.Series(index=prices.index, dtype=float)
    
    # First EMA value is SMA
    first_sma = prices.iloc[:period].mean()
    ema_values.iloc[period - 1] = first_sma
    
    # Calculate subsequent EMA values
    for i in range(period, len(prices)):
        current_price = prices.iloc[i]
        previous_ema = ema_values.iloc[i - 1]
        ema_values.iloc[i] = (current_price * multiplier) + (previous_ema * (1 - multiplier))
    
    return ema_values

def test_ema_calculation_accuracy():
    """
    Test EMA calculation accuracy with known data patterns.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    print("=" * 60)
    print("Test 1: EMA Calculation Accuracy")
    print("=" * 60)
    
    try:
        # Create test data
        test_df = create_test_price_data(days=100)
        print(f"Created test data with {len(test_df)} data points")
        
        # Calculate EMAs for different periods
        periods = [20, 50]
        ema_results = {}
        
        for period in periods:
            ema_values = calculate_ema(test_df['close'], period)
            ema_results[period] = ema_values
            
            print(f"\nEMA-{period} Validation:")
            
            # Validate EMA properties
            valid_ema = ema_values.dropna()
            if len(valid_ema) == 0:
                return False, f"No valid EMA values calculated for period {period}"
            
            # Check that first valid EMA is after period-1 index
            first_valid_index = ema_values.first_valid_index()
            expected_first_index = period - 1
            if ema_values.index.get_loc(first_valid_index) != expected_first_index:
                return False, f"First valid EMA index incorrect for period {period}"
            
            print(f"  ✓ First valid EMA at correct index: {expected_first_index}")
            
            # Check that EMA values are positive and reasonable
            if (valid_ema <= 0).any():
                return False, f"Found non-positive EMA values for period {period}"
            print(f"  ✓ All EMA values are positive")
            
            # Check EMA smoothness (EMA should be smoother than prices)
            price_volatility = test_df['close'].pct_change().std()
            ema_volatility = valid_ema.pct_change().std()
            if ema_volatility >= price_volatility:
                return False, f"EMA not smoother than prices for period {period}"
            print(f"  ✓ EMA is smoother than raw prices ({ema_volatility:.4f} vs {price_volatility:.4f})")
            
            # Display sample EMA values
            print(f"  Sample EMA-{period} values:")
            recent_data = pd.DataFrame({
                'Price': test_df['close'].tail(5),
                f'EMA-{period}': valid_ema.tail(5)
            })
            print(f"    {recent_data.to_string(index=False)}")
        
        # Test EMA relationships (EMA-20 should be more responsive than EMA-50)
        print(f"\nEMA Relationship Tests:")
        ema_20 = ema_results[20].dropna()
        ema_50 = ema_results[50].dropna()
        
        # Align series for comparison
        common_index = ema_20.index.intersection(ema_50.index)
        ema_20_aligned = ema_20.loc[common_index]
        ema_50_aligned = ema_50.loc[common_index]
        
        # EMA-20 should be more volatile than EMA-50
        ema_20_vol = ema_20_aligned.pct_change().std()
        ema_50_vol = ema_50_aligned.pct_change().std()
        
        if ema_20_vol <= ema_50_vol:
            return False, "EMA-20 should be more volatile than EMA-50"
        print(f"  ✓ EMA-20 more responsive than EMA-50 ({ema_20_vol:.4f} vs {ema_50_vol:.4f})")
        
        print("\n✅ EMA calculation accuracy test passed!")
        return True, ""
        
    except Exception as e:
        print(f"❌ EMA calculation test failed: {str(e)}")
        return False, str(e)

def test_ema_edge_cases():
    """
    Test EMA calculation with edge cases.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    print("=" * 60)
    print("Test 2: EMA Edge Cases")
    print("=" * 60)
    
    try:
        # Test case 1: Insufficient data
        short_data = pd.Series([100, 101, 102])
        ema_short = calculate_ema(short_data, period=20)
        if not ema_short.isna().all():
            return False, "Should return all NaN for insufficient data"
        print("  ✓ Handles insufficient data correctly")
        
        # Test case 2: Exact period length
        exact_data = pd.Series(range(100, 120))  # 20 values
        ema_exact = calculate_ema(exact_data, period=20)
        valid_count = ema_exact.dropna().shape[0]
        if valid_count != 1:  # Should have exactly 1 valid value
            return False, f"Expected 1 valid EMA value for exact period data, got {valid_count}"
        print(f"  ✓ Handles exact period length correctly ({valid_count} valid value)")
        
        # Test case 3: Constant prices (EMA should equal price)
        constant_prices = pd.Series([100.0] * 50)
        ema_constant = calculate_ema(constant_prices, period=20)
        valid_ema = ema_constant.dropna()
        if not np.allclose(valid_ema, 100.0, rtol=1e-10):
            return False, "EMA of constant prices should equal the constant price"
        print(f"  ✓ Constant prices produce constant EMA")
        
        # Test case 4: Single step change
        step_prices = pd.Series([100.0] * 30 + [200.0] * 30)
        ema_step = calculate_ema(step_prices, period=20)
        
        # EMA should gradually move toward new price level
        ema_before_step = ema_step.iloc[29]  # Last EMA before step
        ema_after_step = ema_step.iloc[35]   # EMA a few periods after step
        
        if not (100 < ema_before_step <= 100.1):  # Should be close to 100
            return False, f"EMA before step unexpected: {ema_before_step}"
        if not (100 < ema_after_step < 200):  # Should be between old and new price
            return False, f"EMA after step should be transitioning: {ema_after_step}"
        
        print(f"  ✓ Step change handled correctly (before: {ema_before_step:.2f}, after: {ema_after_step:.2f})")
        
        print("\n✅ EMA edge cases test passed!")
        return True, ""
        
    except Exception as e:
        print(f"❌ EMA edge cases test failed: {str(e)}")
        return False, str(e)

def test_volume_analysis():
    """
    Test volume analysis functionality.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    print("=" * 60)
    print("Test 3: Volume Analysis")
    print("=" * 60)
    
    try:
        # Create test data with varying volume
        test_df = create_test_price_data(days=10)
        
        # Modify volume to create specific patterns
        volumes = [10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 80000]  # Last day is high volume
        test_df['volume'] = volumes
        
        # Test volume analysis logic
        def analyze_volume_spike(df, lookback_days=3, spike_threshold=1.5):
            """
            Analyze if current volume is significantly higher than recent average.
            
            Args:
                df (pd.DataFrame): OHLC data with volume
                lookback_days (int): Days to look back for average calculation
                spike_threshold (float): Multiplier threshold for volume spike
                
            Returns:
                tuple: (is_spike: bool, current_volume: float, avg_volume: float, ratio: float)
            """
            if len(df) < lookback_days + 1:
                return False, 0, 0, 0
            
            current_volume = df['volume'].iloc[-1]
            recent_volumes = df['volume'].iloc[-(lookback_days+1):-1]  # Exclude current day
            avg_volume = recent_volumes.mean()
            
            ratio = current_volume / avg_volume if avg_volume > 0 else 0
            is_spike = ratio >= spike_threshold
            
            return is_spike, current_volume, avg_volume, ratio
        
        # Test with our data
        is_spike, current_vol, avg_vol, ratio = analyze_volume_spike(test_df, lookback_days=3, spike_threshold=1.5)
        
        print(f"  Volume Analysis Results:")
        print(f"    Current Volume: {current_vol:,}")
        print(f"    Average Volume (3 days): {avg_vol:,.2f}")
        print(f"    Ratio: {ratio:.2f}x")
        print(f"    Is Volume Spike (≥1.5x): {is_spike}")
        
        # Validate results
        expected_avg = (50000 + 45000 + 40000) / 3  # Last 3 days before current
        expected_ratio = 80000 / expected_avg
        
        if abs(avg_vol - expected_avg) > 0.1:
            return False, f"Average volume calculation incorrect: {avg_vol} vs {expected_avg}"
        
        if abs(ratio - expected_ratio) > 0.01:
            return False, f"Volume ratio calculation incorrect: {ratio} vs {expected_ratio}"
        
        if not is_spike:
            return False, "Should detect volume spike with 1.77x ratio"
        
        print(f"  ✓ Volume spike detection working correctly")
        
        # Test edge case: insufficient data
        short_df = test_df.head(2)
        is_spike_short, _, _, _ = analyze_volume_spike(short_df, lookback_days=3, spike_threshold=1.5)
        if is_spike_short:
            return False, "Should not detect spike with insufficient data"
        print(f"  ✓ Handles insufficient data correctly")
        
        print("\n✅ Volume analysis test passed!")
        return True, ""
        
    except Exception as e:
        print(f"❌ Volume analysis test failed: {str(e)}")
        return False, str(e)

def test_momentum_conditions():
    """
    Test the complete momentum detection logic.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    print("=" * 60)
    print("Test 4: Momentum Conditions")
    print("=" * 60)
    
    try:
        # Create test scenario with bullish momentum
        test_df = create_test_price_data(days=100)
        
        # Calculate EMAs
        ema_20 = calculate_ema(test_df['close'], 20)
        ema_50 = calculate_ema(test_df['close'], 50)
        
        # Add EMAs to dataframe
        test_df['ema_20'] = ema_20
        test_df['ema_50'] = ema_50
        
        # Test momentum condition function
        def check_momentum_conditions(df):
            """
            Check if current price meets momentum conditions.
            
            Returns:
                dict: Analysis results
            """
            latest = df.iloc[-1]
            
            # Condition 1: Price above both EMAs
            price_above_ema20 = latest['close'] > latest['ema_20']
            price_above_ema50 = latest['close'] > latest['ema_50']
            price_condition = price_above_ema20 and price_above_ema50
            
            # Condition 2: Volume spike (≥50% higher than 3-day average)
            current_volume = latest['volume']
            recent_volumes = df['volume'].iloc[-4:-1]  # Last 3 days excluding current
            avg_volume = recent_volumes.mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            volume_condition = volume_ratio >= 1.5  # 50% higher
            
            return {
                'price_above_ema20': price_above_ema20,
                'price_above_ema50': price_above_ema50,
                'price_condition': price_condition,
                'volume_ratio': volume_ratio,
                'volume_condition': volume_condition,
                'all_conditions_met': price_condition and volume_condition,
                'current_price': latest['close'],
                'ema_20': latest['ema_20'],
                'ema_50': latest['ema_50'],
                'current_volume': current_volume,
                'avg_volume': avg_volume
            }
        
        # Test with current data
        results = check_momentum_conditions(test_df)
        
        print(f"  Momentum Analysis Results:")
        print(f"    Current Price: ${results['current_price']:.2f}")
        print(f"    EMA-20: ${results['ema_20']:.2f}")
        print(f"    EMA-50: ${results['ema_50']:.2f}")
        print(f"    Price above EMA-20: {results['price_above_ema20']}")
        print(f"    Price above EMA-50: {results['price_above_ema50']}")
        print(f"    Price Condition Met: {results['price_condition']}")
        print(f"    Volume Ratio: {results['volume_ratio']:.2f}x")
        print(f"    Volume Condition Met: {results['volume_condition']}")
        print(f"    ALL CONDITIONS MET: {results['all_conditions_met']}")
        
        # Validate that function returns expected structure
        required_keys = ['price_condition', 'volume_condition', 'all_conditions_met']
        for key in required_keys:
            if key not in results:
                return False, f"Missing required key in results: {key}"
        
        print(f"  ✓ Momentum condition analysis function working correctly")
        
        # Test with modified data to ensure both conditions can be met
        # Create bullish scenario
        bullish_df = test_df.copy()
        # Set last price well above EMAs
        bullish_df.loc[bullish_df.index[-1], 'close'] = max(
            bullish_df.iloc[-1]['ema_20'], 
            bullish_df.iloc[-1]['ema_50']
        ) * 1.1
        # Set high volume
        bullish_df.loc[bullish_df.index[-1], 'volume'] = bullish_df['volume'].iloc[-4:-1].mean() * 2
        
        # Recalculate EMAs with updated data
        bullish_df['ema_20'] = calculate_ema(bullish_df['close'], 20)
        bullish_df['ema_50'] = calculate_ema(bullish_df['close'], 50)
        
        bullish_results = check_momentum_conditions(bullish_df)
        
        if not bullish_results['price_condition']:
            return False, "Bullish scenario should meet price conditions"
        if not bullish_results['volume_condition']:
            return False, "Bullish scenario should meet volume conditions"
        if not bullish_results['all_conditions_met']:
            return False, "Bullish scenario should meet all conditions"
        
        print(f"  ✓ Bullish momentum scenario correctly identified")
        
        print("\n✅ Momentum conditions test passed!")
        return True, ""
        
    except Exception as e:
        print(f"❌ Momentum conditions test failed: {str(e)}")
        return False, str(e)

def main():
    """
    Run all EMA and momentum analysis tests.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("Starting EMA Calculator and Momentum Analysis Test Suite...")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("EMA Calculation Accuracy", test_ema_calculation_accuracy),
        ("EMA Edge Cases", test_ema_edge_cases),
        ("Volume Analysis", test_volume_analysis),
        ("Momentum Conditions", test_momentum_conditions)
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
    print(f"EMA Calculator: {'✅ Ready for Implementation' if all_passed else '❌ Needs Fixes'}")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())