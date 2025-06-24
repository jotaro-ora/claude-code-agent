#!/usr/bin/env python3
"""
Test module for coin_ohlc_range_by_id tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coin_ohlc_range_by_id import get_coin_ohlc_range_by_id
import unittest

class TestCoinOhlcRangeById(unittest.TestCase):
    
    def test_get_coin_ohlc_range_bitcoin_1_day(self):
        """Test getting Bitcoin OHLC range for 1 day"""
        result = get_coin_ohlc_range_by_id('bitcoin')
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Check first item structure
        first_item = result[0]
        self.assertIsInstance(first_item, list)
        self.assertEqual(len(first_item), 5)  # [timestamp, open, high, low, close]

    def test_get_coin_ohlc_range_ethereum_7_days(self):
        """Test getting Ethereum OHLC range for 7 days"""
        result = get_coin_ohlc_range_by_id('ethereum')
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_get_coin_ohlc_range_with_eur_currency(self):
        """Test with EUR currency"""
        result = get_coin_ohlc_range_by_id('bitcoin', vs_currency='eur')
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_get_coin_ohlc_range_30_days(self):
        """Test with 30 days range"""
        result = get_coin_ohlc_range_by_id('bitcoin', from_timestamp=1672531200, to_timestamp=1673135999)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_get_coin_ohlc_range_90_days(self):
        """Test with 90 days range"""
        result = get_coin_ohlc_range_by_id('bitcoin', from_timestamp=1672531200, to_timestamp=1675123199)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_get_coin_ohlc_range_180_days(self):
        """Test with 180 days range"""
        result = get_coin_ohlc_range_by_id('bitcoin', from_timestamp=1672531200, to_timestamp=1677830399)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_get_coin_ohlc_range_365_days(self):
        """Test with 365 days range"""
        result = get_coin_ohlc_range_by_id('bitcoin', from_timestamp=1672531200, to_timestamp=1679875199)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

if __name__ == '__main__':
    unittest.main() 