#!/usr/bin/env python3
"""
Test module for CoinGlass whale_hyperliquid_position tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from coinglass.whale_hyperliquid_position import get_whale_hyperliquid_position
import unittest

class TestWhaleHyperliquidPosition(unittest.TestCase):
    
    def test_get_whale_hyperliquid_position(self):
        """Test getting whale Hyperliquid position data"""
        try:
            result = get_whale_hyperliquid_position("BTC", 10)
            self.assertIsInstance(result, (list, object))
            if len(result) > 0:
                if isinstance(result, list):
                    if result[0] and isinstance(result[0], dict):
                        possible_keys = ['user', 'symbol', 'position', 'size', 'unrealizedPnl', 'marginRatio']
                        has_expected_keys = any(key in result[0] for key in possible_keys)
                        self.assertTrue(has_expected_keys, "First item should contain expected keys")
                else:
                    possible_columns = ['user', 'symbol', 'position', 'size', 'unrealizedPnl', 'marginRatio']
                    has_expected_columns = any(col in result.columns for col in possible_columns)
                    self.assertTrue(has_expected_columns, "DataFrame should contain expected columns")
        except ConnectionError as e:
            if "Upgrade plan" in str(e):
                self.skipTest("API endpoint requires upgraded plan")
            else:
                raise
            
    def test_get_whale_hyperliquid_position_api_key_validation(self):
        """Test API key validation"""
        original_key = os.getenv("COINGLASS_API_KEY")
        if original_key:
            os.environ.pop("COINGLASS_API_KEY", None)
            with self.assertRaises(EnvironmentError):
                get_whale_hyperliquid_position()
            os.environ["COINGLASS_API_KEY"] = original_key

if __name__ == '__main__':
    unittest.main()