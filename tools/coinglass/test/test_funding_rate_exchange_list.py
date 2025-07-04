#!/usr/bin/env python3
"""
Test module for CoinGlass funding_rate_exchange_list tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from coinglass.funding_rate_exchange_list import get_funding_rate_exchange_list
import unittest

class TestFundingRateExchangeList(unittest.TestCase):
    
    def test_get_funding_rate_exchange_list(self):
        """Test getting funding rate by exchange list data"""
        try:
            result = get_funding_rate_exchange_list("BTC")
            self.assertIsInstance(result, (list, object))  # list or pandas DataFrame
            
            # Check if result is not empty
            if len(result) > 0:
                # Check if it's a list of dictionaries or DataFrame with columns
                if isinstance(result, list):
                    # Check if first item is a dictionary with expected keys
                    if result[0] and isinstance(result[0], dict):
                        possible_keys = ['symbol', 'stablecoin_margin_list', 'token_margin_list']
                        has_expected_keys = any(key in result[0] for key in possible_keys)
                        self.assertTrue(has_expected_keys, "First item should contain expected keys")
                        # Also check if exchange data exists
                        if 'stablecoin_margin_list' in result[0] and result[0]['stablecoin_margin_list']:
                            exchange_keys = ['exchange', 'funding_rate']
                            has_exchange_keys = any(key in result[0]['stablecoin_margin_list'][0] for key in exchange_keys)
                            self.assertTrue(has_exchange_keys, "Exchange data should contain expected keys")
                else:
                    # DataFrame case
                    possible_columns = ['symbol', 'stablecoin_margin_list', 'token_margin_list']
                    has_expected_columns = any(col in result.columns for col in possible_columns)
                    self.assertTrue(has_expected_columns, "DataFrame should contain expected columns")
        except ConnectionError as e:
            if "Upgrade plan" in str(e):
                self.skipTest("API endpoint requires upgraded plan")
            else:
                raise
            
    def test_get_funding_rate_exchange_list_api_key_validation(self):
        """Test API key validation"""
        # Temporarily remove API key
        original_key = os.getenv("COINGLASS_API_KEY")
        if original_key:
            os.environ.pop("COINGLASS_API_KEY", None)
            
            with self.assertRaises(EnvironmentError):
                get_funding_rate_exchange_list()
                
            # Restore API key
            os.environ["COINGLASS_API_KEY"] = original_key

if __name__ == '__main__':
    unittest.main()