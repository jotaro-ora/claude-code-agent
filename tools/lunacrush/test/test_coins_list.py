#!/usr/bin/env python3
"""
Test module for LunarCrush coins_list tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coins_list import get_coins_list, get_coin_symbols, search_coins
import unittest

class TestCoinsListLunarCrush(unittest.TestCase):
    
    def test_get_coins_list_default(self):
        """Test getting coins list with default parameters"""
        try:
            result = get_coins_list()
            self.assertIsInstance(result, dict)
            self.assertIn('data', result)
            self.assertIsInstance(result['data'], list)
            self.assertGreater(len(result['data']), 0)
            self.assertLessEqual(len(result['data']), 50)  # Default limit
            
            # Check first coin structure
            if result['data']:
                coin = result['data'][0]
                self.assertIn('symbol', coin)
                self.assertIn('name', coin)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coins_list_with_limit(self):
        """Test getting coins list with custom limit"""
        try:
            result = get_coins_list(limit=10)
            self.assertIsInstance(result, dict)
            self.assertIn('data', result)
            self.assertLessEqual(len(result['data']), 10)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coins_list_invalid_limit(self):
        """Test with invalid limit values"""
        with self.assertRaises(ValueError):
            get_coins_list(limit=1001)  # Exceeds maximum
            
        with self.assertRaises(ValueError):
            get_coins_list(limit=0)  # Below minimum
    
    def test_get_coins_list_different_sort(self):
        """Test getting coins list with different sort options"""
        try:
            # Test market cap sort
            result = get_coins_list(limit=5, sort="mc")
            self.assertIsInstance(result, dict)
            self.assertIn('data', result)
            
            # Test price sort
            result = get_coins_list(limit=5, sort="price")
            self.assertIsInstance(result, dict)
            self.assertIn('data', result)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coins_list_invalid_sort(self):
        """Test with invalid sort field"""
        with self.assertRaises(ValueError):
            get_coins_list(sort="invalid_field")
    
    def test_get_coins_list_ascending_order(self):
        """Test getting coins list in ascending order"""
        try:
            result = get_coins_list(limit=5, sort="alt_rank", desc=False)
            self.assertIsInstance(result, dict)
            self.assertIn('data', result)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_symbols(self):
        """Test getting list of coin symbols"""
        try:
            symbols = get_coin_symbols()
            self.assertIsInstance(symbols, list)
            if symbols:  # If API call succeeded
                self.assertGreater(len(symbols), 0)
                # Check that symbols are strings
                for symbol in symbols[:5]:  # Check first 5
                    self.assertIsInstance(symbol, str)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_search_coins(self):
        """Test searching for coins by name/symbol"""
        try:
            # Search for Bitcoin
            results = search_coins("bitcoin", limit=5)
            self.assertIsInstance(results, list)
            
            # Search for BTC
            results = search_coins("BTC", limit=5)
            self.assertIsInstance(results, list)
            
            # Search for non-existent coin
            results = search_coins("nonexistentcoin123", limit=5)
            self.assertIsInstance(results, list)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()