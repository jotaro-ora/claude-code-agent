#!/usr/bin/env python3
"""
Test module for CoinGlass spot_supported_exchange_pairs tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from coinglass.spot_supported_exchange_pairs import get_spot_supported_exchange_pairs
import unittest

class TestSpotSupportedExchangePairs(unittest.TestCase):
    
    def test_get_spot_supported_exchange_pairs(self):
        """Test getting supported spot exchange pairs data"""
        try:
            result = get_spot_supported_exchange_pairs()
            self.assertIsInstance(result, dict)
            if result:
                # Check if any exchange has trading pairs
                has_exchange_data = any(isinstance(pairs, list) for pairs in result.values())
                self.assertTrue(has_exchange_data, "Should contain exchange data with trading pairs")
        except ConnectionError as e:
            if "Upgrade plan" in str(e):
                self.skipTest("API endpoint requires upgraded plan")
            else:
                raise
            
    def test_get_spot_supported_exchange_pairs_api_key_validation(self):
        """Test API key validation"""
        original_key = os.getenv("COINGLASS_API_KEY")
        if original_key:
            os.environ.pop("COINGLASS_API_KEY", None)
            with self.assertRaises(EnvironmentError):
                get_spot_supported_exchange_pairs()
            os.environ["COINGLASS_API_KEY"] = original_key

if __name__ == '__main__':
    unittest.main()