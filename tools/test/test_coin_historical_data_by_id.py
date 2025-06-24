#!/usr/bin/env python3
"""
Test module for coin_historical_data_by_id tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coin_historical_data_by_id import get_coin_historical_data_by_id
import unittest

class TestCoinHistoricalDataById(unittest.TestCase):
    
    def test_get_coin_historical_data_bitcoin(self):
        """Test getting Bitcoin historical data"""
        result = get_coin_historical_data_by_id('bitcoin', '01-01-2023')
        self.assertIsInstance(result, dict)
        self.assertIn('id', result)
        
    def test_get_coin_historical_data_ethereum(self):
        """Test getting Ethereum historical data"""
        result = get_coin_historical_data_by_id('ethereum', '01-01-2023')
        self.assertIsInstance(result, dict)
        self.assertIn('id', result)
        
    def test_get_coin_historical_data_with_localization(self):
        """Test with localization disabled"""
        result = get_coin_historical_data_by_id('bitcoin', '01-01-2023', localization='false')
        self.assertIsInstance(result, dict)
        self.assertIn('id', result)

if __name__ == '__main__':
    unittest.main() 