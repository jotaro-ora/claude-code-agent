#!/usr/bin/env python3
"""
Test module for coins_list tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coins_list import get_coins_list
import unittest
import pandas as pd

class TestCoinsList(unittest.TestCase):
    
    def test_get_coins_list_basic(self):
        """Test basic coins list retrieval"""
        result = get_coins_list()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        
        # Check DataFrame structure
        self.assertIn('id', result.columns)
        self.assertIn('symbol', result.columns)
        self.assertIn('name', result.columns)
        
    def test_get_coins_list_with_include_inactive(self):
        """Test coins list with include_inactive parameter"""
        result = get_coins_list(include_inactive=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        
        # Check DataFrame structure
        self.assertIn('id', result.columns)
        self.assertIn('symbol', result.columns)
        self.assertIn('name', result.columns)
        
    def test_get_coins_list_with_include_inactive_false(self):
        """Test coins list with include_inactive=False"""
        result = get_coins_list(include_inactive=False)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        
        # Check DataFrame structure
        self.assertIn('id', result.columns)
        self.assertIn('symbol', result.columns)
        self.assertIn('name', result.columns)

if __name__ == '__main__':
    unittest.main() 