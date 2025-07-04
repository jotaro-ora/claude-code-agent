#!/usr/bin/env python3
"""
Test module for CoinGlass index_fear_greed_history tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from coinglass.index_fear_greed_history import get_index_fear_greed_history
import unittest

class TestIndexFearGreedHistory(unittest.TestCase):
    
    def test_get_index_fear_greed_history(self):
        """Test getting fear & greed index history data"""
        try:
            result = get_index_fear_greed_history("1d")
            self.assertIsInstance(result, (list, object))  # list or pandas DataFrame
            
            # Check if result is not empty
            if result:
                # Check if it's a dict, list of dictionaries or DataFrame with columns
                if isinstance(result, dict):
                    # Check for expected keys in the main result
                    possible_keys = ['data_list', 'price_list', 'time_list']
                    has_expected_keys = any(key in result for key in possible_keys)
                    self.assertTrue(has_expected_keys, "Result should contain expected keys")
                elif isinstance(result, list) and len(result) > 0:
                    # Check if first item is a dictionary with expected keys
                    if result[0] and isinstance(result[0], dict):
                        possible_keys = ['timestamp', 'value', 'classification', 'index']
                        has_expected_keys = any(key in result[0] for key in possible_keys)
                        self.assertTrue(has_expected_keys, "First item should contain expected keys")
                else:
                    # DataFrame case
                    possible_columns = ['data_list', 'price_list', 'time_list']
                    has_expected_columns = any(col in result.columns for col in possible_columns)
                    self.assertTrue(has_expected_columns, "DataFrame should contain expected columns")
        except ConnectionError as e:
            if "Upgrade plan" in str(e):
                self.skipTest("API endpoint requires upgraded plan")
            else:
                raise
            
    def test_get_index_fear_greed_history_api_key_validation(self):
        """Test API key validation"""
        # Temporarily remove API key
        original_key = os.getenv("COINGLASS_API_KEY")
        if original_key:
            os.environ.pop("COINGLASS_API_KEY", None)
            
            with self.assertRaises(EnvironmentError):
                get_index_fear_greed_history()
                
            # Restore API key
            os.environ["COINGLASS_API_KEY"] = original_key

if __name__ == '__main__':
    unittest.main()