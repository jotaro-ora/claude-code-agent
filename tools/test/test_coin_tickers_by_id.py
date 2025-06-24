#!/usr/bin/env python3
"""
Test module for coin_tickers_by_id tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coin_tickers_by_id import get_coin_tickers_by_id
import unittest
import pandas as pd

class TestCoinTickersById(unittest.TestCase):
    
    def test_get_coin_tickers_bitcoin(self):
        """Test getting Bitcoin tickers"""
        result = get_coin_tickers_by_id('bitcoin')
        self.assertIsInstance(result, pd.DataFrame)
        for col in ['base', 'target', 'market', 'coin_id']:
            self.assertIn(col, result.columns)
        
    def test_get_coin_tickers_ethereum(self):
        """Test getting Ethereum tickers"""
        result = get_coin_tickers_by_id('ethereum')
        self.assertIsInstance(result, pd.DataFrame)
        for col in ['base', 'target', 'market', 'coin_id']:
            self.assertIn(col, result.columns)
        
    def test_get_coin_tickers_with_exchange_ids(self):
        """Test with specific exchange IDs"""
        result = get_coin_tickers_by_id('bitcoin', exchange_ids=['binance', 'coinbase'])
        self.assertIsInstance(result, pd.DataFrame)
        for col in ['base', 'target', 'market', 'coin_id']:
            self.assertIn(col, result.columns)
        
    def test_get_coin_tickers_with_include_exchange_logo(self):
        """Test with exchange logo included"""
        result = get_coin_tickers_by_id('bitcoin', include_exchange_logo='true')
        self.assertIsInstance(result, pd.DataFrame)
        for col in ['base', 'target', 'market', 'coin_id']:
            self.assertIn(col, result.columns)
        
    def test_get_coin_tickers_with_page(self):
        """Test with page parameter"""
        result = get_coin_tickers_by_id('bitcoin', page=2)
        self.assertIsInstance(result, pd.DataFrame)
        for col in ['base', 'target', 'market', 'coin_id']:
            self.assertIn(col, result.columns)

if __name__ == '__main__':
    unittest.main() 