#!/usr/bin/env python3
"""
Test module for CoinGlass futures_supported_exchange_pairs tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from coinglass.futures_supported_exchange_pairs import get_futures_supported_exchange_pairs
import unittest

class TestFuturesSupportedExchangePairs(unittest.TestCase):
    
    def test_get_futures_supported_exchange_pairs(self):
        """Test getting futures supported exchange pairs data"""
        result = get_futures_supported_exchange_pairs()
        self.assertIsInstance(result, dict)  # Should return a dictionary
        
        # Check if result is not empty (assuming there are supported exchange pairs)
        if len(result) > 0:
            # Check that the keys are exchange names and values are lists
            first_exchange = list(result.keys())[0]
            self.assertIsInstance(result[first_exchange], list, "Exchange data should be a list")
            
            # Check that the list contains trading pair dictionaries
            if len(result[first_exchange]) > 0:
                first_pair = result[first_exchange][0]
                self.assertIsInstance(first_pair, dict, "Trading pair should be a dictionary")
                
                # Check for expected keys in trading pair data
                possible_keys = ['instrument_id', 'base_asset', 'quote_asset', 'onboard_date']
                has_expected_keys = any(key in first_pair for key in possible_keys)
                self.assertTrue(has_expected_keys, "Trading pair should contain expected keys")
            
    def test_get_futures_supported_exchange_pairs_api_key_validation(self):
        """Test API key validation"""
        # Temporarily remove API key
        original_key = os.getenv("COINGLASS_API_KEY")
        if original_key:
            os.environ.pop("COINGLASS_API_KEY", None)
            
            with self.assertRaises(EnvironmentError):
                get_futures_supported_exchange_pairs()
                
            # Restore API key
            os.environ["COINGLASS_API_KEY"] = original_key

if __name__ == '__main__':
    unittest.main()