#!/usr/bin/env python3
"""
Test module for top_coins tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from top_coins import get_top_coins
import unittest
import pandas as pd

class TestTopCoins(unittest.TestCase):
    
    def test_get_top_coins_basic(self):
        """Test basic top coins retrieval"""
        result = get_top_coins(5)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)
        self.assertIsInstance(result[0], str)
        self.assertIn('_USD', result[0])
        
    def test_get_top_coins_with_extra_data(self):
        """Test with extra data enabled"""
        result = get_top_coins(5, include_extra_data=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 5)
        self.assertIn('symbol', result.columns)
        
    def test_get_top_coins_large_request(self):
        """Test large request (uses pagination)"""
        result = get_top_coins(100)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 100)
        self.assertIsInstance(result[0], str)
        
    def test_get_top_coins_max_request(self):
        """Test maximum request size"""
        result = get_top_coins(1000)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1000)
        
    def test_get_top_coins_invalid_n(self):
        """Test invalid n parameter"""
        with self.assertRaises(ValueError):
            get_top_coins(0)
        with self.assertRaises(ValueError):
            get_top_coins(1001)

if __name__ == '__main__':
    unittest.main() 