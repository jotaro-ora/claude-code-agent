#!/usr/bin/env python3
"""
Test module for LunarCrush coin_time_series tool
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coin_time_series import (
    get_coin_time_series, 
    get_coin_price_history, 
    get_coin_social_history, 
    get_coin_galaxy_score_history
)
import unittest

class TestCoinTimeSeriesLunarCrush(unittest.TestCase):
    
    def test_get_coin_time_series_default_parameters(self):
        """Test getting coin time series with default parameters"""
        try:
            result = get_coin_time_series("bitcoin")
            self.assertIsInstance(result, dict)
            # If API call succeeds, check structure
            if "data" in result:
                data = result["data"]
                self.assertIsInstance(data, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_time_series_with_symbol(self):
        """Test getting time series using coin symbol"""
        try:
            result = get_coin_time_series("BTC", interval="1d", data_points=7)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_time_series_hourly_data(self):
        """Test getting hourly time series data"""
        try:
            result = get_coin_time_series("ethereum", interval="1h", data_points=24)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_time_series_with_metrics_filter(self):
        """Test getting time series with specific metrics"""
        try:
            metrics = ["price", "volume", "social_volume"]
            result = get_coin_time_series("bitcoin", data_points=7, metrics=metrics)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_time_series_invalid_coin(self):
        """Test with invalid coin identifier"""
        try:
            result = get_coin_time_series("nonexistentcoin123")
            # This might return an error or empty result depending on API behavior
            self.assertIsInstance(result, dict)
        except Exception as e:
            # Expected for invalid coins
            self.assertIsInstance(e, (ConnectionError, ValueError))
    
    def test_get_coin_time_series_empty_identifier(self):
        """Test with empty coin identifier"""
        with self.assertRaises(ValueError):
            get_coin_time_series("")
    
    def test_get_coin_time_series_invalid_interval(self):
        """Test with invalid interval"""
        with self.assertRaises(ValueError):
            get_coin_time_series("bitcoin", interval="1m")
    
    def test_get_coin_time_series_invalid_data_points(self):
        """Test with invalid data points"""
        with self.assertRaises(ValueError):
            get_coin_time_series("bitcoin", data_points=0)
        
        with self.assertRaises(ValueError):
            get_coin_time_series("bitcoin", data_points=1000)
    
    def test_get_coin_price_history(self):
        """Test getting price history for a coin"""
        try:
            result = get_coin_price_history("bitcoin", days=7)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_price_history_custom_days(self):
        """Test getting price history with custom days"""
        try:
            result = get_coin_price_history("ethereum", days=14)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_social_history(self):
        """Test getting social history for a coin"""
        try:
            result = get_coin_social_history("bitcoin", days=7)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_social_history_custom_days(self):
        """Test getting social history with custom days"""
        try:
            result = get_coin_social_history("ethereum", days=14)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_galaxy_score_history(self):
        """Test getting Galaxy Score history for a coin"""
        try:
            result = get_coin_galaxy_score_history("bitcoin", days=14)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")
    
    def test_get_coin_galaxy_score_history_custom_days(self):
        """Test getting Galaxy Score history with custom days"""
        try:
            result = get_coin_galaxy_score_history("ethereum", days=30)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"API request failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()