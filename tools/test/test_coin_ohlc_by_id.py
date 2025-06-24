#!/usr/bin/env python3
"""
Test module for coin_ohlc_by_id tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coin_ohlc_by_id import get_coin_ohlc_by_id
import unittest

class TestCoinOhlcById(unittest.TestCase):
    
    def test_get_coin_ohlc_bitcoin_1_day(self):
        """Test getting Bitcoin OHLC for 1 day"""
        result = get_coin_ohlc_by_id('bitcoin')
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Check first item structure
        first_item = result[0]
        self.assertIsInstance(first_item, list)
        self.assertEqual(len(first_item), 5)  # [timestamp, open, high, low, close]
        
    def test_get_coin_ohlc_ethereum_7_days(self):
        """Test getting Ethereum OHLC for 7 days"""
        result = get_coin_ohlc_by_id('ethereum')
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
    def test_get_coin_ohlc_with_eur_currency(self):
        """Test with EUR currency"""
        result = get_coin_ohlc_by_id('bitcoin', vs_currency='eur')
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
    def test_get_coin_ohlc_14_days(self):
        """Test with 14 days"""
        result = get_coin_ohlc_by_id('bitcoin', days=14)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
    def test_get_coin_ohlc_30_days(self):
        """Test with 30 days"""
        result = get_coin_ohlc_by_id('bitcoin', days=30)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
    def test_get_coin_ohlc_90_days(self):
        """Test with 90 days"""
        result = get_coin_ohlc_by_id('bitcoin', days=90)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
    def test_get_coin_ohlc_180_days(self):
        """Test with 180 days"""
        result = get_coin_ohlc_by_id('bitcoin', days=180)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
    def test_get_coin_ohlc_365_days(self):
        """Test with 365 days"""
        result = get_coin_ohlc_by_id('bitcoin', days=365)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

if __name__ == '__main__':
    unittest.main() 