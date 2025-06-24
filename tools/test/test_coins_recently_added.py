#!/usr/bin/env python3
"""
Test module for coins_recently_added tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coins_recently_added import get_recently_added_coins
import unittest
import pandas as pd

class TestCoinsRecentlyAdded(unittest.TestCase):
    
    def test_get_coins_recently_added(self):
        result = get_recently_added_coins()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)

if __name__ == '__main__':
    unittest.main() 