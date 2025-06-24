#!/usr/bin/env python3
"""
Test module for volume_data tool
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from volume_data import get_volume_data
import unittest

class TestVolumeData(unittest.TestCase):
    
    def test_get_volume_data_single_symbol(self):
        """Test getting volume data for single symbol"""
        result = get_volume_data(['BTC_USD'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('symbol', result.columns)
        self.assertIn('total_volume', result.columns)
        
    def test_get_volume_data_multiple_symbols(self):
        """Test getting volume data for multiple symbols"""
        result = get_volume_data(['BTC_USD', 'ETH_USD'])
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn('symbol', result.columns)
        
    def test_get_volume_data_with_invalid_symbol(self):
        """Test with invalid symbol"""
        with self.assertRaises(ValueError):
            get_volume_data(['INVALID_SYMBOL'])
        
    def test_get_volume_data_mixed_valid_invalid(self):
        """Test with mix of valid and invalid symbols"""
        with self.assertRaises(ValueError):
            get_volume_data(['BTC_USD', 'INVALID_SYMBOL', 'ETH_USD'])

if __name__ == '__main__':
    unittest.main() 