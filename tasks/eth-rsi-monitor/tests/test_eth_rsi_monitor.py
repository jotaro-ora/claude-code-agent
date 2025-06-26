#!/usr/bin/env python3
"""
Test suite for ETH RSI Monitor functionality.
"""

import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from eth_rsi_monitor import ETHRSIMonitor, calculate_rsi, get_timeframe_data


class TestETHRSIMonitor(unittest.TestCase):
    """Test cases for ETHRSIMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, 'test_state.json')
        self.monitor = ETHRSIMonitor(
            rsi_period=14,
            overbought_threshold=70,
            oversold_threshold=30,
            cooldown_minutes=60,
            state_file=self.state_file
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        os.rmdir(self.temp_dir)
    
    def test_calculate_rsi(self):
        """Test RSI calculation with known values."""
        # Test data: prices that should result in known RSI values
        # Using simple test case where all gains/losses are equal
        prices = [
            100, 102, 101, 103, 102, 104, 103, 105, 104, 106,  # Initial 10 values
            105, 107, 106, 108, 107, 109, 108, 110, 109, 111   # Next 10 values for RSI calculation
        ]
        
        rsi = calculate_rsi(prices, period=14)
        
        # RSI should be between 0 and 100
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
        
        # With generally increasing prices, RSI should be > 50
        self.assertGreater(rsi, 50)
    
    def test_calculate_rsi_all_gains(self):
        """Test RSI calculation with all price gains."""
        # Prices that only go up
        prices = [100 + i for i in range(20)]
        
        rsi = calculate_rsi(prices, period=14)
        
        # With all gains, RSI should approach 100
        self.assertGreater(rsi, 90)
    
    def test_calculate_rsi_all_losses(self):
        """Test RSI calculation with all price losses."""
        # Prices that only go down
        prices = [100 - i for i in range(20)]
        
        rsi = calculate_rsi(prices, period=14)
        
        # With all losses, RSI should approach 0
        self.assertLess(rsi, 10)
    
    def test_calculate_rsi_insufficient_data(self):
        """Test RSI calculation with insufficient data."""
        # Not enough data points
        prices = [100, 101, 102]
        
        rsi = calculate_rsi(prices, period=14)
        
        # Should return None for insufficient data
        self.assertIsNone(rsi)
    
    def test_get_timeframe_data(self):
        """Test timeframe to days mapping."""
        # Test valid timeframes
        self.assertEqual(get_timeframe_data('1h'), (1, 'hourly'))
        self.assertEqual(get_timeframe_data('4h'), (1, 'hourly'))
        self.assertEqual(get_timeframe_data('1d'), (30, 'daily'))
        
        # Test invalid timeframe
        with self.assertRaises(ValueError):
            get_timeframe_data('invalid')
    
    def test_load_save_state(self):
        """Test state persistence functionality."""
        # Initial state should be empty
        state = self.monitor.load_state()
        self.assertEqual(state, {})
        
        # Save test state
        test_state = {
            'last_notifications': {
                '1h': {'condition': 'overbought', 'timestamp': datetime.now().isoformat()},
                '4h': {'condition': 'oversold', 'timestamp': datetime.now().isoformat()}
            }
        }
        self.monitor.save_state(test_state)
        
        # Load and verify state
        loaded_state = self.monitor.load_state()
        self.assertIn('last_notifications', loaded_state)
        self.assertEqual(len(loaded_state['last_notifications']), 2)
    
    def test_should_send_notification_no_previous(self):
        """Test notification logic with no previous notifications."""
        # No previous notification - should send
        self.assertTrue(self.monitor.should_send_notification('1h', 'overbought'))
        self.assertTrue(self.monitor.should_send_notification('4h', 'oversold'))
    
    def test_should_send_notification_recent(self):
        """Test notification logic with recent notifications."""
        # Add recent notification
        recent_time = datetime.now() - timedelta(minutes=30)
        self.monitor.state['last_notifications'] = {
            '1h': {
                'condition': 'overbought',
                'timestamp': recent_time.isoformat()
            }
        }
        
        # Recent notification for same condition - should not send
        self.assertFalse(self.monitor.should_send_notification('1h', 'overbought'))
        
        # Different condition - should send
        self.assertTrue(self.monitor.should_send_notification('1h', 'oversold'))
        
        # Different timeframe - should send
        self.assertTrue(self.monitor.should_send_notification('4h', 'overbought'))
    
    def test_should_send_notification_old(self):
        """Test notification logic with old notifications."""
        # Add old notification
        old_time = datetime.now() - timedelta(minutes=90)
        self.monitor.state['last_notifications'] = {
            '1h': {
                'condition': 'overbought',
                'timestamp': old_time.isoformat()
            }
        }
        
        # Old notification - should send
        self.assertTrue(self.monitor.should_send_notification('1h', 'overbought'))
    
    def test_record_notification(self):
        """Test notification recording."""
        self.monitor.record_notification('1h', 'overbought')
        
        # Check that notification was recorded
        self.assertIn('last_notifications', self.monitor.state)
        self.assertIn('1h', self.monitor.state['last_notifications'])
        self.assertEqual(self.monitor.state['last_notifications']['1h']['condition'], 'overbought')
    
    @patch('eth_rsi_monitor.coin_ohlc_by_id.get_coin_ohlc_by_id')
    def test_get_ohlc_data_success(self, mock_get_ohlc):
        """Test successful OHLC data retrieval."""
        # Mock OHLC response
        mock_ohlc_data = [
            [1640995200000, 4000.0, 4100.0, 3950.0, 4050.0],  # [timestamp, open, high, low, close]
            [1641081600000, 4050.0, 4150.0, 4000.0, 4100.0],
            [1641168000000, 4100.0, 4200.0, 4050.0, 4150.0]
        ]
        mock_get_ohlc.return_value = mock_ohlc_data
        
        data = self.monitor.get_ohlc_data('1d')
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0][4], 4050.0)  # First close price
        
        # Verify API was called correctly
        mock_get_ohlc.assert_called_once_with('ethereum', vs_currency='usd', days=30)
    
    @patch('eth_rsi_monitor.coin_ohlc_by_id.get_coin_ohlc_by_id')
    def test_get_ohlc_data_failure(self, mock_get_ohlc):
        """Test OHLC data retrieval failure."""
        mock_get_ohlc.side_effect = Exception("API Error")
        
        data = self.monitor.get_ohlc_data('1h')
        self.assertIsNone(data)
    
    @patch('builtins.print')
    def test_send_notification(self, mock_print):
        """Test notification sending."""
        rsi_value = 75.5
        timeframe = '1h'
        condition = 'overbought'
        
        self.monitor.send_notification(timeframe, condition, rsi_value)
        
        # Verify notification was "sent" (printed)
        mock_print.assert_called()
        call_args = str(mock_print.call_args)
        self.assertIn('ETH RSI ALERT', call_args)
        self.assertIn('1h', call_args)
        self.assertIn('overbought', call_args)
        self.assertIn('75.5', call_args)
    
    @patch('eth_rsi_monitor.coin_ohlc_by_id.get_coin_ohlc_by_id')
    @patch('builtins.print')
    def test_check_timeframe_integration(self, mock_print, mock_get_ohlc):
        """Test timeframe checking integration."""
        # Mock OHLC data that should result in high RSI
        high_rsi_data = []
        base_price = 4000
        for i in range(20):
            # Steadily increasing prices to generate high RSI
            price = base_price + (i * 50)
            timestamp = 1640995200000 + (i * 3600000)  # Hourly intervals
            high_rsi_data.append([timestamp, price, price + 20, price - 10, price + 10])
        
        mock_get_ohlc.return_value = high_rsi_data
        
        # Should trigger overbought alert
        self.monitor.check_timeframe('1h')
        
        # Verify notification was sent
        mock_print.assert_called()
        call_args = str(mock_print.call_args_list[-1])
        self.assertIn('ETH RSI ALERT', call_args)
        self.assertIn('overbought', call_args)
    
    @patch('eth_rsi_monitor.coin_ohlc_by_id.get_coin_ohlc_by_id')
    def test_check_timeframe_no_alert(self, mock_get_ohlc):
        """Test timeframe checking with no alert condition."""
        # Mock OHLC data that should result in neutral RSI
        neutral_rsi_data = []
        base_price = 4000
        for i in range(20):
            # Alternating prices to generate neutral RSI
            price = base_price + (10 if i % 2 == 0 else -10)
            timestamp = 1640995200000 + (i * 3600000)
            neutral_rsi_data.append([timestamp, price, price + 5, price - 5, price])
        
        mock_get_ohlc.return_value = neutral_rsi_data
        
        # Should not trigger any alert
        result = self.monitor.check_timeframe('1h')
        self.assertIsNone(result)  # No alert condition


class TestRSICalculation(unittest.TestCase):
    """Test cases for RSI calculation function."""
    
    def test_rsi_boundary_conditions(self):
        """Test RSI calculation boundary conditions."""
        # Test with exactly minimum required data points
        prices = list(range(100, 115))  # 15 prices for 14-period RSI
        rsi = calculate_rsi(prices, period=14)
        self.assertIsNotNone(rsi)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
    
    def test_rsi_with_no_change(self):
        """Test RSI calculation with no price changes."""
        # All prices the same
        prices = [100] * 20
        rsi = calculate_rsi(prices, period=14)
        
        # With no changes, RSI should be 50 (neutral)
        self.assertAlmostEqual(rsi, 50.0, places=1)
    
    def test_rsi_period_validation(self):
        """Test RSI calculation with invalid periods."""
        prices = list(range(100, 120))
        
        # Test with period larger than data
        rsi = calculate_rsi(prices, period=25)
        self.assertIsNone(rsi)
        
        # Test with zero period
        with self.assertRaises(ValueError):
            calculate_rsi(prices, period=0)
        
        # Test with negative period
        with self.assertRaises(ValueError):
            calculate_rsi(prices, period=-1)


class TestTimeframeMapping(unittest.TestCase):
    """Test cases for timeframe data mapping."""
    
    def test_all_supported_timeframes(self):
        """Test all supported timeframe mappings."""
        # Test 1 hour
        days, interval = get_timeframe_data('1h')
        self.assertEqual(days, 1)
        self.assertEqual(interval, 'hourly')
        
        # Test 4 hour
        days, interval = get_timeframe_data('4h')
        self.assertEqual(days, 1)
        self.assertEqual(interval, 'hourly')
        
        # Test 1 day
        days, interval = get_timeframe_data('1d')
        self.assertEqual(days, 30)
        self.assertEqual(interval, 'daily')
    
    def test_unsupported_timeframes(self):
        """Test unsupported timeframe handling."""
        unsupported_timeframes = ['5m', '15m', '30m', '2h', '12h', '1w', '1M']
        
        for timeframe in unsupported_timeframes:
            with self.assertRaises(ValueError):
                get_timeframe_data(timeframe)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)