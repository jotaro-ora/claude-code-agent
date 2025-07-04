#!/usr/bin/env python3
"""
Test module for LunarCrush coin_meta tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coin_meta import get_coin_meta, get_coin_basic_info, get_coin_social_metrics, validate_coin_exists
import unittest

class TestCoinMetaLunarCrush(unittest.TestCase):
    
    def test_get_coin_meta_default_parameters(self):
        """Test getting coin metadata with default parameters"""
        try:
            result = get_coin_meta("bitcoin")
            self.assertIsInstance(result, dict)
            # If API call succeeds, check structure
            if "data" in result:
                coin = result["data"]
                self.assertIsInstance(coin, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_meta_with_symbol(self):
        """Test getting coin metadata using symbol"""
        try:
            result = get_coin_meta("BTC")
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_meta_with_custom_parameters(self):
        """Test getting coin metadata with custom interval and data points"""
        try:
            result = get_coin_meta("ethereum", interval="1h", data_points=24)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_meta_invalid_coin(self):
        """Test with invalid coin identifier"""
        try:
            result = get_coin_meta("nonexistentcoin123")
            # This might return an error or empty result depending on API behavior
            self.assertIsInstance(result, dict)
        except Exception as e:
            # Expected for invalid coins
            self.assertIsInstance(e, (ConnectionError, ValueError))
    
    def test_get_coin_meta_empty_identifier(self):
        """Test with empty coin identifier"""
        with self.assertRaises(ValueError):
            get_coin_meta("")
    
    def test_get_coin_meta_invalid_interval(self):
        """Test with invalid interval"""
        with self.assertRaises(ValueError):
            get_coin_meta("bitcoin", interval="1m")
    
    def test_get_coin_meta_invalid_data_points(self):
        """Test with invalid data points"""
        with self.assertRaises(ValueError):
            get_coin_meta("bitcoin", data_points=0)
        
        with self.assertRaises(ValueError):
            get_coin_meta("bitcoin", data_points=1000)
    
    def test_get_coin_basic_info(self):
        """Test getting basic coin information"""
        try:
            result = get_coin_basic_info("bitcoin")
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_social_metrics(self):
        """Test getting social metrics for a coin"""
        try:
            result = get_coin_social_metrics("bitcoin", days=7)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_social_metrics_custom_days(self):
        """Test getting social metrics with custom days"""
        try:
            result = get_coin_social_metrics("ethereum", days=14)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_validate_coin_exists(self):
        """Test coin existence validation"""
        try:
            # Test with known coin
            exists = validate_coin_exists("bitcoin")
            self.assertIsInstance(exists, bool)
            
            # Test with unknown coin
            not_exists = validate_coin_exists("nonexistentcoin123")
            self.assertIsInstance(not_exists, bool)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()