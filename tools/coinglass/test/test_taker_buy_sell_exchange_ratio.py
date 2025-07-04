#!/usr/bin/env python3
"""
Test module for CoinGlass taker_buy_sell_exchange_ratio tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from coinglass.taker_buy_sell_exchange_ratio import get_taker_buy_sell_exchange_ratio
import unittest

class TestTakerBuySellExchangeRatio(unittest.TestCase):
    
    def test_get_taker_buy_sell_exchange_ratio(self):
        """Test getting taker buy/sell exchange ratio data"""
        try:
            result = get_taker_buy_sell_exchange_ratio("BTC", "4h")
            self.assertIsInstance(result, dict)
            if result:
                # Check for expected keys in the main result
                possible_keys = ['symbol', 'buy_ratio', 'sell_ratio', 'exchange_list']
                has_expected_keys = any(key in result for key in possible_keys)
                self.assertTrue(has_expected_keys, "Result should contain expected keys")
                # Check if exchange_list has data
                if 'exchange_list' in result and result['exchange_list']:
                    exchange_keys = ['exchange', 'buy_ratio', 'sell_ratio']
                    has_exchange_keys = any(key in result['exchange_list'][0] for key in exchange_keys)
                    self.assertTrue(has_exchange_keys, "Exchange data should contain expected keys")
        except ConnectionError as e:
            if "Upgrade plan" in str(e):
                self.skipTest("API endpoint requires upgraded plan")
            else:
                raise
            
    def test_get_taker_buy_sell_exchange_ratio_api_key_validation(self):
        """Test API key validation"""
        original_key = os.getenv("COINGLASS_API_KEY")
        if original_key:
            os.environ.pop("COINGLASS_API_KEY", None)
            with self.assertRaises(EnvironmentError):
                get_taker_buy_sell_exchange_ratio()
            os.environ["COINGLASS_API_KEY"] = original_key

if __name__ == '__main__':
    unittest.main()