#!/usr/bin/env python3
"""
Test module for coin_historical_chart_by_id tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coin_historical_chart_by_id import get_coin_historical_chart_by_id
import unittest

class TestCoinHistoricalChartById(unittest.TestCase):
    
    def test_get_coin_market_chart_bitcoin_1_day(self):
        """Test getting Bitcoin market chart for 1 day"""
        result = get_coin_historical_chart_by_id('bitcoin')
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        self.assertIn('market_caps', result)
        self.assertIn('total_volumes', result)
        
    def test_get_coin_market_chart_ethereum_7_days(self):
        """Test getting Ethereum market chart for 7 days"""
        result = get_coin_historical_chart_by_id('ethereum')
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        self.assertIn('market_caps', result)
        self.assertIn('total_volumes', result)
        
    def test_get_coin_market_chart_with_eur_currency(self):
        """Test with EUR currency"""
        result = get_coin_historical_chart_by_id('bitcoin', vs_currency='eur')
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        
    def test_get_coin_market_chart_30_days(self):
        """Test with 30 days"""
        result = get_coin_historical_chart_by_id('bitcoin', days=30)
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        
    def test_get_coin_market_chart_90_days(self):
        """Test with 90 days"""
        result = get_coin_historical_chart_by_id('bitcoin', days=90)
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        
    def test_get_coin_market_chart_365_days(self):
        """Test with 365 days"""
        result = get_coin_historical_chart_by_id('bitcoin', days=365)
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)
        
    def test_get_coin_market_chart_max_days(self):
        """Test with maximum days (1825)"""
        result = get_coin_historical_chart_by_id('bitcoin', days=1825)
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)

    def test_get_coin_market_chart_interval(self):
        """Test with daily interval"""
        result = get_coin_historical_chart_by_id('bitcoin', interval='daily')
        self.assertIsInstance(result, dict)
        self.assertIn('prices', result)

if __name__ == '__main__':
    unittest.main() 