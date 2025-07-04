#!/usr/bin/env python3
"""
Test module for coins_gainers_losers tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coins_gainers_losers import get_top_gainers_losers
import unittest
import pandas as pd

class TestCoinsGainersLosers(unittest.TestCase):
    
    def test_get_top_gainers_losers_basic(self):
        """Test basic top gainers and losers retrieval"""
        result = get_top_gainers_losers()
        self.assertIsInstance(result, dict)
        self.assertIn('gainers', result)
        self.assertIn('losers', result)
        
        gainers = result['gainers']
        losers = result['losers']
        self.assertIsInstance(gainers, pd.DataFrame)
        self.assertIsInstance(losers, pd.DataFrame)
        self.assertGreater(len(gainers), 0)
        self.assertGreater(len(losers), 0)
        
        # 检查列结构
        for df in [gainers, losers]:
            self.assertIn('id', df.columns)
            self.assertIn('symbol', df.columns)
            self.assertIn('name', df.columns)
            self.assertIn('usd_24h_change', df.columns)

    def test_get_top_gainers_losers_with_currency(self):
        """Test with different currency"""
        result = get_top_gainers_losers(vs_currency='eur')
        self.assertIsInstance(result, dict)
        self.assertIn('gainers', result)
        self.assertIn('losers', result)
        gainers = result['gainers']
        losers = result['losers']
        self.assertIsInstance(gainers, pd.DataFrame)
        self.assertIsInstance(losers, pd.DataFrame)
        self.assertGreater(len(gainers), 0)
        self.assertGreater(len(losers), 0)

if __name__ == '__main__':
    unittest.main() 