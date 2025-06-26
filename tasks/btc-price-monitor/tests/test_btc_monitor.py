#!/usr/bin/env python3
"""
Test suite for BTC price monitoring functionality.
"""

import unittest
import json
import time
import os
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from btc_monitor import BTCPriceMonitor, calculate_percentage_change


class TestBTCPriceMonitor(unittest.TestCase):
    """Test cases for BTCPriceMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, 'test_state.json')
        self.monitor = BTCPriceMonitor(
            threshold_percent=0.1,
            window_minutes=15,
            cooldown_minutes=60,
            state_file=self.state_file
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        os.rmdir(self.temp_dir)
    
    def test_calculate_percentage_change(self):
        """Test percentage change calculation."""
        # Test positive change
        self.assertAlmostEqual(calculate_percentage_change(100, 105), 5.0)
        
        # Test negative change
        self.assertAlmostEqual(calculate_percentage_change(100, 95), -5.0)
        
        # Test zero change
        self.assertAlmostEqual(calculate_percentage_change(100, 100), 0.0)
        
        # Test with zero old price (should handle gracefully)
        self.assertAlmostEqual(calculate_percentage_change(0, 100), 0.0)
    
    def test_load_save_state(self):
        """Test state persistence functionality."""
        # Initial state should be empty
        state = self.monitor.load_state()
        self.assertEqual(state, {})
        
        # Save some state
        test_state = {
            'last_notification': datetime.now().isoformat(),
            'price_history': [{'price': 50000, 'timestamp': datetime.now().isoformat()}]
        }
        self.monitor.save_state(test_state)
        
        # Load and verify state
        loaded_state = self.monitor.load_state()
        self.assertEqual(loaded_state['last_notification'], test_state['last_notification'])
        self.assertEqual(len(loaded_state['price_history']), 1)
    
    def test_should_send_notification_cooldown(self):
        """Test notification cooldown logic."""
        # No previous notification - should send
        self.assertTrue(self.monitor.should_send_notification())
        
        # Recent notification - should not send
        recent_time = datetime.now() - timedelta(minutes=30)
        state = {'last_notification': recent_time.isoformat()}
        self.monitor.save_state(state)
        self.monitor.state = state
        self.assertFalse(self.monitor.should_send_notification())
        
        # Old notification - should send
        old_time = datetime.now() - timedelta(minutes=90)
        state = {'last_notification': old_time.isoformat()}
        self.monitor.save_state(state)
        self.monitor.state = state
        self.assertTrue(self.monitor.should_send_notification())
    
    def test_add_price_to_history(self):
        """Test price history management."""
        now = datetime.now()
        
        # Add first price
        self.monitor.add_price_to_history(50000, now)
        self.assertEqual(len(self.monitor.state['price_history']), 1)
        
        # Add second price
        self.monitor.add_price_to_history(51000, now + timedelta(minutes=5))
        self.assertEqual(len(self.monitor.state['price_history']), 2)
        
        # Add old price (should be filtered out)
        old_time = now - timedelta(minutes=20)
        self.monitor.add_price_to_history(49000, old_time)
        # Should still have 2 recent prices, old one filtered out
        recent_history = [p for p in self.monitor.state['price_history'] 
                         if datetime.fromisoformat(p['timestamp']) > now - timedelta(minutes=15)]
        self.assertEqual(len(recent_history), 2)
    
    def test_check_price_spike(self):
        """Test price spike detection logic."""
        now = datetime.now()
        
        # Add base price
        self.monitor.add_price_to_history(50000, now - timedelta(minutes=10))
        
        # Test no spike (0.05% change)
        self.monitor.add_price_to_history(50025, now)
        spike_detected = self.monitor.check_price_spike(50025)
        self.assertFalse(spike_detected)
        
        # Test spike (0.2% change)
        self.monitor.add_price_to_history(50100, now)
        spike_detected = self.monitor.check_price_spike(50100)
        self.assertTrue(spike_detected)
    
    @patch('btc_monitor.get_coin_data_by_id')
    def test_get_btc_price_success(self, mock_get_coin_data):
        """Test successful BTC price retrieval."""
        mock_get_coin_data.return_value = {
            'market_data': {
                'current_price': {'usd': 50000}
            }
        }
        
        price = self.monitor.get_btc_price()
        self.assertEqual(price, 50000)
        mock_get_coin_data.assert_called_once_with('bitcoin')
    
    @patch('btc_monitor.get_coin_data_by_id')
    def test_get_btc_price_failure(self, mock_get_coin_data):
        """Test BTC price retrieval failure."""
        mock_get_coin_data.side_effect = Exception("API Error")
        
        price = self.monitor.get_btc_price()
        self.assertIsNone(price)
    
    @patch('builtins.print')
    def test_send_notification(self, mock_print):
        """Test notification sending."""
        self.monitor.send_notification(50000, 51000, 2.0)
        
        # Verify notification was "sent" (printed)
        mock_print.assert_called()
        call_args = str(mock_print.call_args)
        self.assertIn('BTC PRICE SPIKE ALERT', call_args)
        self.assertIn('50,000.00', call_args)
        self.assertIn('51,000.00', call_args)
        self.assertIn('2.00%', call_args)
    
    @patch('btc_monitor.get_coin_data_by_id')
    @patch('builtins.print')
    def test_monitor_integration(self, mock_print, mock_get_coin_data):
        """Test full monitoring integration."""
        # Setup mock to return increasing prices
        mock_get_coin_data.side_effect = [
            {'market_data': {'current_price': {'usd': 50000}}},  # First call
            {'market_data': {'current_price': {'usd': 50100}}}   # Second call (0.2% increase)
        ]
        
        # First check - establish baseline
        self.monitor.check_and_notify()
        
        # Second check - should trigger notification
        self.monitor.check_and_notify()
        
        # Verify notification was sent
        mock_print.assert_called()
        call_args = str(mock_print.call_args_list[-1])
        self.assertIn('BTC PRICE SPIKE ALERT', call_args)
    
    def test_price_history_cleanup(self):
        """Test that old price history is cleaned up properly."""
        now = datetime.now()
        
        # Add prices at different times
        self.monitor.add_price_to_history(50000, now - timedelta(minutes=20))  # Old
        self.monitor.add_price_to_history(50050, now - timedelta(minutes=10))  # Recent
        self.monitor.add_price_to_history(50100, now - timedelta(minutes=5))   # Recent
        
        # Cleanup should remove old entries
        self.monitor.cleanup_old_history()
        
        # Should only have recent entries
        recent_count = len([p for p in self.monitor.state['price_history'] 
                          if datetime.fromisoformat(p['timestamp']) > now - timedelta(minutes=15)])
        self.assertEqual(recent_count, 2)


class TestCalculatePercentageChange(unittest.TestCase):
    """Test cases for percentage change calculation function."""
    
    def test_positive_change(self):
        """Test positive percentage change."""
        result = calculate_percentage_change(100, 110)
        self.assertAlmostEqual(result, 10.0, places=2)
    
    def test_negative_change(self):
        """Test negative percentage change."""
        result = calculate_percentage_change(110, 100)
        self.assertAlmostEqual(result, -9.09, places=2)
    
    def test_zero_change(self):
        """Test zero percentage change."""
        result = calculate_percentage_change(100, 100)
        self.assertEqual(result, 0.0)
    
    def test_zero_old_price(self):
        """Test handling of zero old price."""
        result = calculate_percentage_change(0, 100)
        self.assertEqual(result, 0.0)
    
    def test_small_changes(self):
        """Test small percentage changes."""
        result = calculate_percentage_change(50000, 50050)
        self.assertAlmostEqual(result, 0.1, places=2)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)