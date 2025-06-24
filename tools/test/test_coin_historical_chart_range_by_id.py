#!/usr/bin/env python3
"""
Test module for coin_historical_chart_range_by_id tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coin_historical_chart_range_by_id import get_coin_historical_chart_range_by_id
import unittest
import time

class TestCoinHistoricalChartRangeById(unittest.TestCase):
    
    def test_get_coin_market_chart_range_bitcoin_1_day(self):
        """Test getting Bitcoin market chart range for 1 day"""
        now = int(time.time())
        one_day_ago = now - 86400
        result = get_coin_historical_chart_range_by_id('bitcoin', from_timestamp=one_day_ago, to_timestamp=now)
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        self.assertIn('market_caps', result)
        self.assertIn('total_volumes', result)
        self.assertGreater(len(result['prices']), 0)
        
    def test_get_coin_market_chart_range_ethereum_7_days(self):
        """Test getting Ethereum market chart range for 7 days"""
        now = int(time.time())
        seven_days_ago = now - 86400 * 7
        result = get_coin_historical_chart_range_by_id('ethereum', from_timestamp=seven_days_ago, to_timestamp=now)
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        self.assertIn('market_caps', result)
        self.assertIn('total_volumes', result)
        self.assertGreater(len(result['prices']), 0)
        
    def test_get_coin_market_chart_range_with_eur_currency(self):
        """Test with EUR currency"""
        result = get_coin_historical_chart_range_by_id('bitcoin', vs_currency='eur', from_timestamp=1672531200, to_timestamp=1673135999)
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        self.assertIn('market_caps', result)
        self.assertIn('total_volumes', result)
        self.assertGreater(len(result['prices']), 0)
        
    def test_get_coin_market_chart_range_30_days(self):
        """Test with 30 days range"""
        result = get_coin_historical_chart_range_by_id('bitcoin', from_timestamp=1672531200, to_timestamp=1673135999)
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        self.assertIn('market_caps', result)
        self.assertIn('total_volumes', result)
        self.assertGreater(len(result['prices']), 0)
        
    def test_get_coin_market_chart_range_90_days(self):
        """Test with 90 days range"""
        result = get_coin_historical_chart_range_by_id('bitcoin', from_timestamp=1672531200, to_timestamp=1673135999)
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        self.assertIn('market_caps', result)
        self.assertIn('total_volumes', result)
        self.assertGreater(len(result['prices']), 0)
        
    def test_get_coin_market_chart_range_365_days(self):
        """Test with 365 days range"""
        result = get_coin_historical_chart_range_by_id('bitcoin', from_timestamp=1672531200, to_timestamp=1673135999)
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        self.assertIn('market_caps', result)
        self.assertIn('total_volumes', result)
        self.assertGreater(len(result['prices']), 0)

if __name__ == '__main__':
    unittest.main() 