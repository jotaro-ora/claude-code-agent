#!/usr/bin/env python3
"""
Test module for coins_list_market_data tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coins_list_market_data import get_coins_list_market_data
import unittest
import pandas as pd

class TestCoinsListMarketData(unittest.TestCase):
    
    def test_get_coins_market_data_basic(self):
        """Test basic market data retrieval"""
        result = get_coins_list_market_data()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        # 检查主要字段
        for col in ['id', 'symbol', 'name', 'current_price', 'market_cap', 'total_volume']:
            self.assertIn(col, result.columns)
    
    def test_get_coins_market_data_with_limit(self):
        """Test with custom limit"""
        result = get_coins_list_market_data(per_page=5)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertLessEqual(len(result), 5)
    
    def test_get_coins_market_data_with_currency(self):
        """Test with different currency"""
        result = get_coins_list_market_data(vs_currency='EUR')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
    
    def test_get_coins_market_data_with_order(self):
        """Test with different ordering"""
        result = get_coins_list_market_data(order='market_cap_desc')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
    
    def test_get_coins_market_data_with_sparkline(self):
        """Test with sparkline data"""
        result = get_coins_list_market_data(sparkline=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        # 检查 sparkline 字段
        self.assertIn('sparkline_in_7d', result.columns)

if __name__ == '__main__':
    unittest.main() 