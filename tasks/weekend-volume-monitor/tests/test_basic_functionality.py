#!/usr/bin/env python3
"""
Basic functionality tests for Weekend Volume Monitor (pandas-free version).
"""

import unittest
import os
import sys
import tempfile
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from weekend_volume_monitor import (
    is_weekend, get_weekend_dates, calculate_total_volume, WeekendVolumeMonitor
)


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality without external dependencies."""
    
    def test_is_weekend(self):
        """Test weekend detection."""
        # Known dates
        saturday = datetime(2024, 1, 6)   # Saturday
        sunday = datetime(2024, 1, 7)     # Sunday  
        monday = datetime(2024, 1, 8)     # Monday
        
        self.assertTrue(is_weekend(saturday))
        self.assertTrue(is_weekend(sunday))
        self.assertFalse(is_weekend(monday))
    
    def test_get_weekend_dates(self):
        """Test weekend date calculation."""
        saturday = datetime(2024, 1, 6)
        start, end = get_weekend_dates(saturday)
        
        self.assertEqual(start.weekday(), 5)  # Saturday
        self.assertEqual(end.weekday(), 6)    # Sunday
        self.assertEqual(start.date(), saturday.date())
    
    def test_calculate_total_volume(self):
        """Test volume calculation with list data."""
        test_data = [
            {'symbol': 'btc', 'total_volume': 1000000},
            {'symbol': 'eth', 'total_volume': 500000},
            {'symbol': 'bnb', 'total_volume': 250000}
        ]
        
        total = calculate_total_volume(test_data)
        self.assertEqual(total, 1750000)
        
        # Test with empty list
        self.assertEqual(calculate_total_volume([]), 0)
        
        # Test with None values
        test_with_none = [
            {'symbol': 'btc', 'total_volume': 1000000},
            {'symbol': 'eth', 'total_volume': None}
        ]
        self.assertEqual(calculate_total_volume(test_with_none), 1000000)
    
    def test_monitor_initialization(self):
        """Test monitor can be initialized."""
        temp_dir = tempfile.mkdtemp()
        state_file = os.path.join(temp_dir, 'test_state.json')
        
        monitor = WeekendVolumeMonitor(
            historical_weeks=4,
            top_n_coins=100,
            state_file=state_file
        )
        
        self.assertEqual(monitor.historical_weeks, 4)
        self.assertEqual(monitor.top_n_coins, 100)
        self.assertEqual(monitor.alert_threshold_percent, 10.0)
        
        # Cleanup
        if os.path.exists(state_file):
            os.remove(state_file)
        os.rmdir(temp_dir)
    
    def test_state_persistence(self):
        """Test state save and load."""
        temp_dir = tempfile.mkdtemp()
        state_file = os.path.join(temp_dir, 'test_state.json')
        
        monitor = WeekendVolumeMonitor(state_file=state_file)
        
        # Add test data
        test_state = {
            'weekend_volumes': [
                {'date': '2024-01-06', 'volume': 1000000}
            ]
        }
        monitor.save_state(test_state)
        
        # Load and verify
        loaded_state = monitor.load_state()
        self.assertEqual(len(loaded_state['weekend_volumes']), 1)
        self.assertEqual(loaded_state['weekend_volumes'][0]['volume'], 1000000)
        
        # Cleanup
        if os.path.exists(state_file):
            os.remove(state_file)
        os.rmdir(temp_dir)
    
    def test_historical_average(self):
        """Test historical average calculation."""
        temp_dir = tempfile.mkdtemp()
        state_file = os.path.join(temp_dir, 'test_state.json')
        
        monitor = WeekendVolumeMonitor(state_file=state_file)
        monitor.state['weekend_volumes'] = [
            {'date': '2024-01-06', 'volume': 1000000},
            {'date': '2024-01-13', 'volume': 1200000},
            {'date': '2024-01-20', 'volume': 800000}
        ]
        
        avg = monitor.get_historical_average()
        expected = (1000000 + 1200000 + 800000) / 3
        self.assertEqual(avg, expected)
        
        # Test insufficient data
        monitor.state['weekend_volumes'] = [{'date': '2024-01-06', 'volume': 1000000}]
        self.assertIsNone(monitor.get_historical_average())
        
        # Cleanup
        if os.path.exists(state_file):
            os.remove(state_file)
        os.rmdir(temp_dir)
    
    def test_should_alert(self):
        """Test alert logic."""
        temp_dir = tempfile.mkdtemp()
        state_file = os.path.join(temp_dir, 'test_state.json')
        
        monitor = WeekendVolumeMonitor(
            alert_threshold_percent=10.0,
            state_file=state_file
        )
        monitor.state['weekend_volumes'] = [
            {'date': '2024-01-06', 'volume': 1000000},
            {'date': '2024-01-13', 'volume': 1000000}
        ]
        
        # Should alert for 15% increase
        self.assertTrue(monitor.should_alert(1150000))
        
        # Should not alert for 5% increase
        self.assertFalse(monitor.should_alert(1050000))
        
        # Cleanup
        if os.path.exists(state_file):
            os.remove(state_file)
        os.rmdir(temp_dir)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)