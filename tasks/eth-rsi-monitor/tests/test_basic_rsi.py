#!/usr/bin/env python3
"""
Basic RSI functionality tests (dependency-free version).
"""

import unittest
import os
import sys
import tempfile

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from eth_rsi_monitor import calculate_rsi, get_timeframe_data, ETHRSIMonitor


class TestBasicRSI(unittest.TestCase):
    """Test basic RSI functionality without external dependencies."""
    
    def test_rsi_calculation_trending_up(self):
        """Test RSI with upward trending prices."""
        # Steadily increasing prices
        prices = [100 + i * 2 for i in range(20)]
        rsi = calculate_rsi(prices, period=14)
        
        # Should be high RSI (overbought territory)
        self.assertIsNotNone(rsi)
        self.assertGreater(rsi, 70)
        self.assertLessEqual(rsi, 100)
    
    def test_rsi_calculation_trending_down(self):
        """Test RSI with downward trending prices."""
        # Steadily decreasing prices
        prices = [100 - i * 2 for i in range(20)]
        rsi = calculate_rsi(prices, period=14)
        
        # Should be low RSI (oversold territory)
        self.assertIsNotNone(rsi)
        self.assertLess(rsi, 30)
        self.assertGreaterEqual(rsi, 0)
    
    def test_rsi_calculation_sideways(self):
        """Test RSI with sideways price movement."""
        # Alternating up/down prices
        prices = [100 + (5 if i % 2 == 0 else -5) for i in range(20)]
        rsi = calculate_rsi(prices, period=14)
        
        # Should be neutral RSI
        self.assertIsNotNone(rsi)
        self.assertGreater(rsi, 30)
        self.assertLess(rsi, 70)
    
    def test_rsi_insufficient_data(self):
        """Test RSI with insufficient data."""
        prices = [100, 101, 102]  # Only 3 prices
        rsi = calculate_rsi(prices, period=14)
        
        self.assertIsNone(rsi)
    
    def test_rsi_edge_cases(self):
        """Test RSI edge cases."""
        # All same prices (no change)
        same_prices = [100] * 20
        rsi = calculate_rsi(same_prices, period=14)
        self.assertAlmostEqual(rsi, 50.0, places=1)
        
        # Invalid period
        with self.assertRaises(ValueError):
            calculate_rsi([100, 101, 102], period=0)
    
    def test_timeframe_mapping(self):
        """Test timeframe to API parameter mapping."""
        # Valid timeframes
        self.assertEqual(get_timeframe_data('1h'), 1)
        self.assertEqual(get_timeframe_data('4h'), 1)
        self.assertEqual(get_timeframe_data('1d'), 30)
        
        # Invalid timeframe
        with self.assertRaises(ValueError):
            get_timeframe_data('invalid')
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        temp_dir = tempfile.mkdtemp()
        state_file = os.path.join(temp_dir, 'test_state.json')
        
        monitor = ETHRSIMonitor(
            rsi_period=21,
            overbought_threshold=75,
            oversold_threshold=25,
            cooldown_minutes=30,
            timeframes=['1h', '4h'],
            state_file=state_file
        )
        
        self.assertEqual(monitor.rsi_period, 21)
        self.assertEqual(monitor.overbought_threshold, 75)
        self.assertEqual(monitor.oversold_threshold, 25)
        self.assertEqual(monitor.cooldown_minutes, 30)
        self.assertEqual(monitor.timeframes, ['1h', '4h'])
        
        # Cleanup
        if os.path.exists(state_file):
            os.remove(state_file)
        os.rmdir(temp_dir)
    
    def test_notification_logic(self):
        """Test notification cooldown logic."""
        temp_dir = tempfile.mkdtemp()
        state_file = os.path.join(temp_dir, 'test_state.json')
        
        monitor = ETHRSIMonitor(cooldown_minutes=60, state_file=state_file)
        
        # No previous notification - should send
        self.assertTrue(monitor.should_send_notification('1h', 'overbought'))
        
        # Record a notification
        monitor.record_notification('1h', 'overbought')
        
        # Same condition - should not send (in cooldown)
        self.assertFalse(monitor.should_send_notification('1h', 'overbought'))
        
        # Different condition - should send
        self.assertTrue(monitor.should_send_notification('1h', 'oversold'))
        
        # Different timeframe - should send
        self.assertTrue(monitor.should_send_notification('4h', 'overbought'))
        
        # Cleanup
        if os.path.exists(state_file):
            os.remove(state_file)
        os.rmdir(temp_dir)


if __name__ == '__main__':
    unittest.main(verbosity=2)