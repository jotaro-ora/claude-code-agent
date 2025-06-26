#!/usr/bin/env python3
"""Tests for crypto market scanner."""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from market_scanner import (
    filter_price_volume_criteria,
    calculate_ema,
    calculate_sma,
    score_candidate
)

class TestMarketScanner(unittest.TestCase):
    """Test cases for market scanner functions."""
    
    def test_filter_price_volume_criteria(self):
        """Test price and volume filtering."""
        mock_data = [
            {
                'id': 'bitcoin',
                'symbol': 'btc',
                'name': 'Bitcoin',
                'current_price': 50000,
                'price_change_percentage_24h': 15,
                'price_change_percentage_7d_in_currency': 12,
                'total_volume': 2000000,
                'market_cap': 1000000000
            },
            {
                'id': 'ethereum',
                'symbol': 'eth',
                'name': 'Ethereum',
                'current_price': 3000,
                'price_change_percentage_24h': 5,  # Below threshold
                'price_change_percentage_7d_in_currency': 15,
                'total_volume': 1500000,
                'market_cap': 500000000
            }
        ]
        
        candidates = filter_price_volume_criteria(mock_data)
        
        # Only Bitcoin should pass (both 24h and 7d > 5%)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]['symbol'], 'BTC')
    
    def test_calculate_ema(self):
        """Test EMA calculation."""
        prices = [10, 12, 11, 13, 14, 15]
        ema = calculate_ema(prices, 3)
        
        # EMA should be a float
        self.assertIsInstance(ema, float)
        self.assertGreater(ema, 10)
        self.assertLess(ema, 20)
        
        # Test with insufficient data
        short_prices = [10, 12]
        ema_short = calculate_ema(short_prices, 5)
        self.assertIsNone(ema_short)
    
    def test_calculate_sma(self):
        """Test SMA calculation."""
        prices = [10, 12, 14, 16, 18]
        sma = calculate_sma(prices, 3)
        
        # Should be average of last 3: (14+16+18)/3 = 16
        self.assertEqual(sma, 16)
        
        # Test with insufficient data
        short_prices = [10, 12]
        sma_short = calculate_sma(short_prices, 5)
        self.assertIsNone(sma_short)
    
    def test_score_candidate(self):
        """Test candidate scoring."""
        candidate = {
            'id': 'test-coin',
            'symbol': 'TEST',
            'price_24h': 15,
            'price_7d': 12,
            'volume_24h': 15000000
        }
        
        trending_coins = [{'id': 'test-coin'}]
        
        technical_data = {
            'ma_score': 3,
            'above_ema_20': True,
            'above_ema_50': True
        }
        
        score, details = score_candidate(candidate, trending_coins, technical_data)
        
        # Should get points for price changes, volume, trending, and technical
        self.assertGreater(score, 60)
        self.assertIn('✓', details['price_24h'])
        self.assertIn('✓', details['trending'])

if __name__ == '__main__':
    unittest.main()