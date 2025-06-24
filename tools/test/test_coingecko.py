#!/usr/bin/env python3
"""
Test module for coingecko tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coingecko import get_coingecko_ohlc
import unittest

class TestCoingecko(unittest.TestCase):
    
    def test_get_coingecko_ohlc_bitcoin_daily(self):
        """Test getting Bitcoin daily OHLC data"""
        result = get_coingecko_ohlc('BTC_USD', '1d', '2023-01-01', '2023-01-31')
        self.assertIsInstance(result, object)  # pandas DataFrame
        self.assertGreater(len(result), 0)
        
        # Check DataFrame structure
        self.assertIn('datetime', result.columns)
        self.assertIn('open', result.columns)
        self.assertIn('high', result.columns)
        self.assertIn('low', result.columns)
        self.assertIn('close', result.columns)
        
    def test_get_coingecko_ohlc_ethereum_hourly(self):
        """Test getting Ethereum hourly OHLC data"""
        result = get_coingecko_ohlc('ETH_USD', '1h', '2023-01-01', '2023-01-07')
        self.assertIsInstance(result, object)  # pandas DataFrame
        self.assertGreater(len(result), 0)
        
    def test_get_coingecko_ohlc_with_timestamps(self):
        """Test with timestamp inputs"""
        import time
        end_time = int(time.time())
        start_time = end_time - (7 * 24 * 3600)  # 7 days ago
        
        result = get_coingecko_ohlc('BTC_USD', '1d', start_time, end_time)
        self.assertIsInstance(result, object)  # pandas DataFrame
        self.assertGreater(len(result), 0)
        
    def test_get_coingecko_ohlc_invalid_interval(self):
        """Test with invalid interval"""
        with self.assertRaises(ValueError):
            get_coingecko_ohlc('BTC_USD', '1w', '2023-01-01', '2023-01-31')
            
    def test_get_coingecko_ohlc_invalid_date_range(self):
        """Test with invalid date range"""
        with self.assertRaises(ValueError):
            get_coingecko_ohlc('BTC_USD', '1d', '2023-01-31', '2023-01-01')

if __name__ == '__main__':
    unittest.main() 