#!/usr/bin/env python3
"""
Test suite for Weekend Volume Monitor functionality.
"""

import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from weekend_volume_monitor import WeekendVolumeMonitor, is_weekend, get_weekend_dates, calculate_total_volume


class TestWeekendVolumeMonitor(unittest.TestCase):
    """Test cases for WeekendVolumeMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, 'test_state.json')
        self.monitor = WeekendVolumeMonitor(
            historical_weeks=4,
            top_n_coins=100,
            state_file=self.state_file
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        os.rmdir(self.temp_dir)
    
    def test_is_weekend(self):
        """Test weekend detection function."""
        # Test Saturday (weekday = 5)
        saturday = datetime(2024, 1, 6)  # Known Saturday
        self.assertTrue(is_weekend(saturday))
        
        # Test Sunday (weekday = 6)
        sunday = datetime(2024, 1, 7)  # Known Sunday
        self.assertTrue(is_weekend(sunday))
        
        # Test Monday (weekday = 0)
        monday = datetime(2024, 1, 8)  # Known Monday
        self.assertFalse(is_weekend(monday))
        
        # Test Wednesday (weekday = 2)
        wednesday = datetime(2024, 1, 10)  # Known Wednesday
        self.assertFalse(is_weekend(wednesday))
    
    def test_get_weekend_dates(self):
        """Test weekend date calculation."""
        # Test for a known Saturday
        saturday = datetime(2024, 1, 6)
        start, end = get_weekend_dates(saturday)
        self.assertEqual(start.weekday(), 5)  # Saturday
        self.assertEqual(end.weekday(), 6)    # Sunday
        self.assertEqual(start.date(), saturday.date())
        
        # Test for a known Sunday
        sunday = datetime(2024, 1, 7)
        start, end = get_weekend_dates(sunday)
        self.assertEqual(start.weekday(), 5)  # Saturday
        self.assertEqual(end.weekday(), 6)    # Sunday
        self.assertEqual(end.date(), sunday.date())
        
        # Test for a weekday (should get previous weekend)
        tuesday = datetime(2024, 1, 9)
        start, end = get_weekend_dates(tuesday)
        self.assertEqual(start.weekday(), 5)  # Saturday
        self.assertEqual(end.weekday(), 6)    # Sunday
        self.assertTrue(start < tuesday)
        self.assertTrue(end < tuesday)
    
    def test_calculate_total_volume(self):
        """Test total volume calculation."""
        if HAS_PANDAS:
            # Test with pandas DataFrame
            test_data = pd.DataFrame({
                'symbol': ['btc', 'eth', 'bnb'],
                'total_volume': [1000000, 500000, 250000]
            })
            
            total = calculate_total_volume(test_data)
            self.assertEqual(total, 1750000)
            
            # Test with empty DataFrame
            empty_df = pd.DataFrame()
            total = calculate_total_volume(empty_df)
            self.assertEqual(total, 0)
            
            # Test with None values
            test_data_with_none = pd.DataFrame({
                'symbol': ['btc', 'eth', 'bnb'],
                'total_volume': [1000000, None, 250000]
            })
            total = calculate_total_volume(test_data_with_none)
            self.assertEqual(total, 1250000)
        
        # Test with list of dictionaries (fallback mode)
        test_data_list = [
            {'symbol': 'btc', 'total_volume': 1000000},
            {'symbol': 'eth', 'total_volume': 500000},
            {'symbol': 'bnb', 'total_volume': 250000}
        ]
        
        total = calculate_total_volume(test_data_list)
        self.assertEqual(total, 1750000)
        
        # Test with empty list
        empty_list = []
        total = calculate_total_volume(empty_list)
        self.assertEqual(total, 0)
        
        # Test with None values in list
        test_data_with_none_list = [
            {'symbol': 'btc', 'total_volume': 1000000},
            {'symbol': 'eth', 'total_volume': None},
            {'symbol': 'bnb', 'total_volume': 250000}
        ]
        total = calculate_total_volume(test_data_with_none_list)
        self.assertEqual(total, 1250000)
    
    def test_load_save_state(self):
        """Test state persistence functionality."""
        # Initial state should be empty
        state = self.monitor.load_state()
        self.assertEqual(state, {})
        
        # Save test state
        test_state = {
            'weekend_volumes': [
                {'date': '2024-01-06', 'volume': 1000000},
                {'date': '2024-01-13', 'volume': 1200000}
            ],
            'last_check': datetime.now().isoformat()
        }
        self.monitor.save_state(test_state)
        
        # Load and verify state
        loaded_state = self.monitor.load_state()
        self.assertEqual(len(loaded_state['weekend_volumes']), 2)
        self.assertEqual(loaded_state['weekend_volumes'][0]['volume'], 1000000)
    
    def test_add_weekend_volume(self):
        """Test adding weekend volume to history."""
        weekend_date = datetime(2024, 1, 6)  # Saturday
        volume = 1500000
        
        self.monitor.add_weekend_volume(weekend_date, volume)
        
        # Check that volume was added to state
        self.assertEqual(len(self.monitor.state['weekend_volumes']), 1)
        self.assertEqual(self.monitor.state['weekend_volumes'][0]['volume'], volume)
        self.assertEqual(self.monitor.state['weekend_volumes'][0]['date'], '2024-01-06')
    
    def test_get_historical_average(self):
        """Test historical average calculation."""
        # Add test data
        test_volumes = [
            {'date': '2024-01-06', 'volume': 1000000},
            {'date': '2024-01-13', 'volume': 1200000},
            {'date': '2024-01-20', 'volume': 800000},
            {'date': '2024-01-27', 'volume': 1100000}
        ]
        self.monitor.state['weekend_volumes'] = test_volumes
        
        # Calculate average
        avg = self.monitor.get_historical_average()
        expected_avg = (1000000 + 1200000 + 800000 + 1100000) / 4
        self.assertEqual(avg, expected_avg)
        
        # Test with insufficient data
        self.monitor.state['weekend_volumes'] = [
            {'date': '2024-01-06', 'volume': 1000000}
        ]
        avg = self.monitor.get_historical_average()
        self.assertIsNone(avg)
    
    def test_should_alert(self):
        """Test alert threshold logic."""
        # Set up historical data
        test_volumes = [
            {'date': '2024-01-06', 'volume': 1000000},
            {'date': '2024-01-13', 'volume': 1000000},
            {'date': '2024-01-20', 'volume': 1000000}
        ]
        self.monitor.state['weekend_volumes'] = test_volumes
        
        current_volume = 1200000  # 20% higher than average
        self.assertTrue(self.monitor.should_alert(current_volume))
        
        current_volume = 900000   # 10% lower than average
        self.assertFalse(self.monitor.should_alert(current_volume))
        
        current_volume = 1050000  # 5% higher than average
        self.assertFalse(self.monitor.should_alert(current_volume))
    
    def test_cleanup_old_data(self):
        """Test cleanup of old weekend volume data."""
        # Add test data spanning more than the historical period
        test_volumes = []
        base_date = datetime(2024, 1, 6)  # Start with a Saturday
        
        # Add 10 weeks of data (more than the 4-week historical period)
        for i in range(10):
            weekend_date = base_date + timedelta(weeks=i)
            test_volumes.append({
                'date': weekend_date.strftime('%Y-%m-%d'),
                'volume': 1000000 + (i * 10000)
            })
        
        self.monitor.state['weekend_volumes'] = test_volumes
        
        # Cleanup should keep only the most recent historical_weeks
        self.monitor.cleanup_old_data()
        
        # Should have at most historical_weeks entries
        self.assertLessEqual(len(self.monitor.state['weekend_volumes']), self.monitor.historical_weeks)
        
        # Should keep the most recent entries
        if self.monitor.state['weekend_volumes']:
            latest_date = max(vol['date'] for vol in self.monitor.state['weekend_volumes'])
            expected_latest = test_volumes[-1]['date']
            self.assertEqual(latest_date, expected_latest)
    
    @patch('weekend_volume_monitor.coins_list_market_data.get_coins_list_market_data')
    def test_get_current_volume_success(self, mock_get_market_data):
        """Test successful current volume retrieval."""
        if HAS_PANDAS:
            # Mock API response as DataFrame
            mock_df = pd.DataFrame({
                'symbol': ['btc', 'eth', 'bnb'],
                'total_volume': [1000000, 500000, 250000]
            })
            mock_get_market_data.return_value = mock_df
        else:
            # Mock API response as list of dictionaries
            mock_data = [
                {'symbol': 'btc', 'total_volume': 1000000},
                {'symbol': 'eth', 'total_volume': 500000},
                {'symbol': 'bnb', 'total_volume': 250000}
            ]
            mock_get_market_data.return_value = mock_data
        
        volume = self.monitor.get_current_volume()
        self.assertEqual(volume, 1750000)
        
        # Verify API was called with correct parameters
        mock_get_market_data.assert_called_once_with(
            vs_currency='usd',
            per_page=100,
            order='market_cap_desc'
        )
    
    @patch('weekend_volume_monitor.coins_list_market_data.get_coins_list_market_data')
    def test_get_current_volume_failure(self, mock_get_market_data):
        """Test current volume retrieval failure."""
        mock_get_market_data.side_effect = Exception("API Error")
        
        volume = self.monitor.get_current_volume()
        self.assertIsNone(volume)
    
    @patch('builtins.print')
    def test_send_alert(self, mock_print):
        """Test alert sending."""
        current_volume = 1500000
        average_volume = 1000000
        percentage_increase = 50.0
        
        self.monitor.send_alert(current_volume, average_volume, percentage_increase)
        
        # Verify alert was "sent" (printed)
        mock_print.assert_called()
        call_args = str(mock_print.call_args)
        self.assertIn('WEEKEND VOLUME ALERT', call_args)
        self.assertIn('1,500,000', call_args)
        self.assertIn('1,000,000', call_args)
        self.assertIn('50.0%', call_args)
    
    @patch('weekend_volume_monitor.coins_list_market_data.get_coins_list_market_data')
    @patch('builtins.print')
    def test_check_and_alert_integration(self, mock_print, mock_get_market_data):
        """Test full monitoring integration."""
        # Set up historical data
        test_volumes = [
            {'date': '2024-01-06', 'volume': 1000000},
            {'date': '2024-01-13', 'volume': 1000000},
            {'date': '2024-01-20', 'volume': 1000000}
        ]
        self.monitor.state['weekend_volumes'] = test_volumes
        
        if HAS_PANDAS:
            # Mock current high volume as DataFrame
            mock_df = pd.DataFrame({
                'symbol': ['btc', 'eth'],
                'total_volume': [1200000, 600000]  # Total: 1,800,000 (80% increase)
            })
            mock_get_market_data.return_value = mock_df
        else:
            # Mock current high volume as list
            mock_data = [
                {'symbol': 'btc', 'total_volume': 1200000},
                {'symbol': 'eth', 'total_volume': 600000}  # Total: 1,800,000 (80% increase)
            ]
            mock_get_market_data.return_value = mock_data
        
        # Should trigger alert on weekend
        with patch('weekend_volume_monitor.is_weekend', return_value=True):
            self.monitor.check_and_alert()
        
        # Verify alert was sent
        mock_print.assert_called()
        call_args = str(mock_print.call_args_list[-1])
        self.assertIn('WEEKEND VOLUME ALERT', call_args)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_is_weekend_edge_cases(self):
        """Test weekend detection with edge cases."""
        # Test with different times on weekend days
        saturday_morning = datetime(2024, 1, 6, 8, 0, 0)
        saturday_night = datetime(2024, 1, 6, 23, 59, 59)
        sunday_morning = datetime(2024, 1, 7, 0, 0, 1)
        
        self.assertTrue(is_weekend(saturday_morning))
        self.assertTrue(is_weekend(saturday_night))
        self.assertTrue(is_weekend(sunday_morning))
    
    def test_get_weekend_dates_edge_cases(self):
        """Test weekend date calculation edge cases."""
        # Test early Monday morning (should get previous weekend)
        monday_early = datetime(2024, 1, 8, 0, 0, 1)
        start, end = get_weekend_dates(monday_early)
        
        # Should be previous weekend
        self.assertEqual(start.date(), datetime(2024, 1, 6).date())  # Previous Saturday
        self.assertEqual(end.date(), datetime(2024, 1, 7).date())    # Previous Sunday
    
    def test_calculate_total_volume_edge_cases(self):
        """Test total volume calculation edge cases."""
        if HAS_PANDAS:
            # Test with missing total_volume column
            df_no_volume = pd.DataFrame({
                'symbol': ['btc', 'eth'],
                'price': [50000, 3000]
            })
            
            total = calculate_total_volume(df_no_volume)
            self.assertEqual(total, 0)
            
            # Test with all None values
            df_all_none = pd.DataFrame({
                'symbol': ['btc', 'eth'],
                'total_volume': [None, None]
            })
            
            total = calculate_total_volume(df_all_none)
            self.assertEqual(total, 0)
        
        # Test with missing total_volume key in list
        list_no_volume = [
            {'symbol': 'btc', 'price': 50000},
            {'symbol': 'eth', 'price': 3000}
        ]
        
        total = calculate_total_volume(list_no_volume)
        self.assertEqual(total, 0)
        
        # Test with all None values in list
        list_all_none = [
            {'symbol': 'btc', 'total_volume': None},
            {'symbol': 'eth', 'total_volume': None}
        ]
        
        total = calculate_total_volume(list_all_none)
        self.assertEqual(total, 0)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)