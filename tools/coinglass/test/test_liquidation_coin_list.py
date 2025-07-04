#!/usr/bin/env python3
"""
Test module for CoinGlass liquidation_coin_list tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from coinglass.liquidation_coin_list import get_liquidation_coin_list
import unittest

class TestLiquidationCoinList(unittest.TestCase):
    
    def test_get_liquidation_coin_list(self):
        """Test getting liquidation coin list data"""
        try:
            result = get_liquidation_coin_list()
            self.assertIsInstance(result, (list, object))  # list or pandas DataFrame
            
            # Check if result is not empty
            if len(result) > 0:
                # Check if it's a list of dictionaries or DataFrame with columns
                if isinstance(result, list):
                    # Check if first item is a dictionary with expected keys
                    if result[0] and isinstance(result[0], dict):
                        possible_keys = ['symbol', 'totalLiquidation', 'longLiquidation', 'shortLiquidation']
                        has_expected_keys = any(key in result[0] for key in possible_keys)
                        self.assertTrue(has_expected_keys, "First item should contain expected keys")
                else:
                    # DataFrame case
                    possible_columns = ['symbol', 'totalLiquidation', 'longLiquidation', 'shortLiquidation']
                    has_expected_columns = any(col in result.columns for col in possible_columns)
                    self.assertTrue(has_expected_columns, "DataFrame should contain expected columns")
        except ConnectionError as e:
            if "Upgrade plan" in str(e):
                self.skipTest("API endpoint requires upgraded plan")
            else:
                raise
            
    def test_get_liquidation_coin_list_api_key_validation(self):
        """Test API key validation"""
        # Temporarily remove API key
        original_key = os.getenv("COINGLASS_API_KEY")
        if original_key:
            os.environ.pop("COINGLASS_API_KEY", None)
            
            with self.assertRaises(EnvironmentError):
                get_liquidation_coin_list()
                
            # Restore API key
            os.environ["COINGLASS_API_KEY"] = original_key

if __name__ == '__main__':
    unittest.main()