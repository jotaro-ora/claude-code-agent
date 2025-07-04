#!/usr/bin/env python3
"""
Test module for coin_data_by_id tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coin_data_by_id import get_coin_data_by_id
import unittest

class TestCoinDataById(unittest.TestCase):
    
    def test_get_coin_data_bitcoin(self):
        """Test getting Bitcoin data"""
        result = get_coin_data_by_id('bitcoin')
        self.assertIsInstance(result, dict)
        self.assertIn('id', result)
        self.assertIn('symbol', result)
        self.assertIn('name', result)
        self.assertEqual(result['id'], 'bitcoin')
        
    def test_get_coin_data_ethereum(self):
        """Test getting Ethereum data"""
        result = get_coin_data_by_id('ethereum')
        self.assertIsInstance(result, dict)
        self.assertIn('id', result)
        self.assertIn('symbol', result)
        self.assertIn('name', result)
        self.assertEqual(result['id'], 'ethereum')
        
    def test_get_coin_data_with_localization(self):
        """Test with localization disabled"""
        result = get_coin_data_by_id('bitcoin', localization='false')
        self.assertIsInstance(result, dict)
        self.assertIn('id', result)
        
    def test_get_coin_data_with_tickers(self):
        """Test with tickers enabled"""
        result = get_coin_data_by_id('bitcoin', tickers='true')
        self.assertIsInstance(result, dict)
        self.assertIn('tickers', result)
        
    def test_get_coin_data_with_market_data(self):
        """Test with market data enabled"""
        result = get_coin_data_by_id('bitcoin', market_data='true')
        self.assertIsInstance(result, dict)
        self.assertIn('market_data', result)
        
    def test_get_coin_data_with_community_data(self):
        """Test with community data enabled"""
        result = get_coin_data_by_id('bitcoin', community_data='true')
        self.assertIsInstance(result, dict)
        self.assertIn('community_data', result)
        
    def test_get_coin_data_with_developer_data(self):
        """Test with developer data enabled"""
        result = get_coin_data_by_id('bitcoin', developer_data='true')
        self.assertIsInstance(result, dict)
        self.assertIn('developer_data', result)
        
    def test_get_coin_data_with_sparkline(self):
        """Test with sparkline data enabled"""
        result = get_coin_data_by_id('bitcoin', sparkline='true')
        self.assertIsInstance(result, dict)
        self.assertIn('market_data', result)
        self.assertIn('sparkline_7d', result['market_data'])

if __name__ == '__main__':
    unittest.main() 