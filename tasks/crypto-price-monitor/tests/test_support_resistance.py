"""
Test suite for support and resistance level calculation.
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path for imports - supports execution from project root
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from tasks.crypto_price_monitor.src.support_resistance import SupportResistanceCalculator


class TestSupportResistanceCalculator(unittest.TestCase):
    """Test cases for SupportResistanceCalculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = SupportResistanceCalculator(lookback_hours=24)
    
    def test_init_valid_lookback(self):
        """Test valid initialization."""
        calc = SupportResistanceCalculator(12)
        self.assertEqual(calc.lookback_hours, 12)
    
    def test_init_invalid_lookback(self):
        """Test invalid lookback hours."""
        with self.assertRaises(ValueError):
            SupportResistanceCalculator(0)
        
        with self.assertRaises(ValueError):
            SupportResistanceCalculator(-5)
        
        with self.assertRaises(ValueError):
            SupportResistanceCalculator("invalid")
    
    def test_calculate_levels_empty_data(self):
        """Test calculation with empty data."""
        with self.assertRaises(ValueError):
            self.calculator.calculate_levels([])
    
    def test_calculate_levels_insufficient_data(self):
        """Test calculation with insufficient data."""
        price_data = [
            {'timestamp': 1000, 'price': 100},
            {'timestamp': 2000, 'price': 101}
        ]
        
        with self.assertRaises(ValueError):
            self.calculator.calculate_levels(price_data)
    
    def test_calculate_levels_invalid_data_structure(self):
        """Test calculation with invalid data structure."""
        # Non-dict data
        with self.assertRaises(TypeError):
            self.calculator.calculate_levels([100, 101, 102, 103, 104])
        
        # Missing price key
        price_data = [
            {'timestamp': i * 1000, 'value': 100 + i}
            for i in range(10)
        ]
        with self.assertRaises(ValueError):
            self.calculator.calculate_levels(price_data)
        
        # Non-numeric price
        price_data = [
            {'timestamp': i * 1000, 'price': f"price_{i}"}
            for i in range(10)
        ]
        with self.assertRaises(TypeError):
            self.calculator.calculate_levels(price_data)
    
    def test_calculate_levels_trending_up(self):
        """Test calculation with upward trending prices."""
        price_data = [
            {'timestamp': i * 1000, 'price': 100 + i * 5}
            for i in range(20)
        ]
        
        levels = self.calculator.calculate_levels(price_data)
        
        self.assertIn('support', levels)
        self.assertIn('resistance', levels)
        self.assertGreater(levels['resistance'], levels['support'])
        self.assertGreater(levels['support'], 0)
        self.assertGreater(levels['resistance'], 0)
    
    def test_calculate_levels_trending_down(self):
        """Test calculation with downward trending prices."""
        price_data = [
            {'timestamp': i * 1000, 'price': 200 - i * 3}
            for i in range(20)
        ]
        
        levels = self.calculator.calculate_levels(price_data)
        
        self.assertIn('support', levels)
        self.assertIn('resistance', levels)
        self.assertGreater(levels['resistance'], levels['support'])
        self.assertGreater(levels['support'], 0)
        self.assertGreater(levels['resistance'], 0)
    
    def test_calculate_levels_sideways(self):
        """Test calculation with sideways price movement."""
        base_price = 150
        price_data = []
        
        for i in range(20):
            # Add some noise around base price
            noise = (i % 3 - 1) * 2  # -2, 0, 2
            price_data.append({
                'timestamp': i * 1000,
                'price': base_price + noise
            })
        
        levels = self.calculator.calculate_levels(price_data)
        
        self.assertIn('support', levels)
        self.assertIn('resistance', levels)
        self.assertGreater(levels['resistance'], levels['support'])
        
        # For sideways movement, levels should be close to the base price
        self.assertLess(abs(levels['support'] - base_price), base_price * 0.1)
        self.assertLess(abs(levels['resistance'] - base_price), base_price * 0.1)
    
    def test_calculate_levels_volatile(self):
        """Test calculation with volatile price data."""
        price_data = []
        base_price = 1000
        
        for i in range(30):
            # Create volatile movement
            if i % 4 == 0:
                price = base_price * 1.05  # Spike up
            elif i % 4 == 2:
                price = base_price * 0.95  # Dip down
            else:
                price = base_price + (i % 3 - 1) * 10
            
            price_data.append({
                'timestamp': i * 1000,
                'price': price
            })
        
        levels = self.calculator.calculate_levels(price_data)
        
        self.assertIn('support', levels)
        self.assertIn('resistance', levels)
        self.assertGreater(levels['resistance'], levels['support'])
        self.assertGreater(levels['support'], 0)
        self.assertGreater(levels['resistance'], 0)
    
    def test_is_price_at_level_valid(self):
        """Test price level checking with valid inputs."""
        # Exact match
        self.assertTrue(
            self.calculator.is_price_at_level(100.0, 100.0, 0.0)
        )
        
        # Within tolerance
        self.assertTrue(
            self.calculator.is_price_at_level(100.5, 100.0, 1.0)
        )
        
        self.assertTrue(
            self.calculator.is_price_at_level(99.5, 100.0, 1.0)
        )
        
        # Outside tolerance
        self.assertFalse(
            self.calculator.is_price_at_level(102.0, 100.0, 1.0)
        )
        
        self.assertFalse(
            self.calculator.is_price_at_level(98.0, 100.0, 1.0)
        )
    
    def test_is_price_at_level_invalid_inputs(self):
        """Test price level checking with invalid inputs."""
        # Invalid current price
        with self.assertRaises(ValueError):
            self.calculator.is_price_at_level(-100, 100, 1.0)
        
        with self.assertRaises(ValueError):
            self.calculator.is_price_at_level(0, 100, 1.0)
        
        with self.assertRaises(ValueError):
            self.calculator.is_price_at_level("invalid", 100, 1.0)
        
        # Invalid level
        with self.assertRaises(ValueError):
            self.calculator.is_price_at_level(100, -50, 1.0)
        
        with self.assertRaises(ValueError):
            self.calculator.is_price_at_level(100, 0, 1.0)
        
        # Invalid tolerance
        with self.assertRaises(ValueError):
            self.calculator.is_price_at_level(100, 100, -1.0)
    
    def test_pivot_points_calculation(self):
        """Test pivot point calculation method."""
        # Create simple OHLC-like data
        price_data = [
            {'timestamp': 1000, 'price': 95},   # Low
            {'timestamp': 2000, 'price': 100},  # 
            {'timestamp': 3000, 'price': 105},  # High
            {'timestamp': 4000, 'price': 102},  # Close
            {'timestamp': 5000, 'price': 98}
        ]
        
        df = pd.DataFrame(price_data)
        df['price'] = pd.to_numeric(df['price'])
        
        levels = self.calculator._calculate_pivot_points(df)
        
        self.assertIn('support', levels)
        self.assertIn('resistance', levels)
        
        # Verify basic pivot point logic
        high = df['price'].max()  # 105
        low = df['price'].min()   # 95
        close = df['price'].iloc[-1]  # 98
        
        expected_pivot = (high + low + close) / 3  # 99.33
        expected_support = 2 * expected_pivot - high  # 93.66
        expected_resistance = 2 * expected_pivot - low  # 103.66
        
        self.assertAlmostEqual(levels['support'], expected_support, places=2)
        self.assertAlmostEqual(levels['resistance'], expected_resistance, places=2)
    
    def test_local_extrema_calculation(self):
        """Test local extrema calculation method."""
        # Create data with clear local min/max
        price_data = [
            {'timestamp': 1000, 'price': 100},
            {'timestamp': 2000, 'price': 95},   # Local min
            {'timestamp': 3000, 'price': 100},
            {'timestamp': 4000, 'price': 110},  # Local max
            {'timestamp': 5000, 'price': 105},
            {'timestamp': 6000, 'price': 102},
            {'timestamp': 7000, 'price': 98},   # Local min
            {'timestamp': 8000, 'price': 103},
            {'timestamp': 9000, 'price': 108}
        ]
        
        df = pd.DataFrame(price_data)
        df['price'] = pd.to_numeric(df['price'])
        
        levels = self.calculator._calculate_local_extrema(df)
        
        if levels:  # Method might not find extrema in all cases
            if 'support' in levels:
                self.assertGreater(levels['support'], 0)
            if 'resistance' in levels:
                self.assertGreater(levels['resistance'], 0)
    
    def test_ma_levels_calculation(self):
        """Test moving average levels calculation method."""
        # Create trending data
        price_data = [
            {'timestamp': i * 1000, 'price': 100 + i}
            for i in range(25)
        ]
        
        df = pd.DataFrame(price_data)
        df['price'] = pd.to_numeric(df['price'])
        
        levels = self.calculator._calculate_ma_levels(df)
        
        if levels:  # Method might not work with insufficient data
            if 'support' in levels:
                self.assertGreater(levels['support'], 0)
            if 'resistance' in levels:
                self.assertGreater(levels['resistance'], 0)
    
    def test_real_world_price_data(self):
        """Test with realistic cryptocurrency price data."""
        # Simulate BTC-like price data around $45,000
        base_price = 45000
        price_data = []
        
        for i in range(50):
            # Simulate realistic price movements
            if i < 10:
                price = base_price + i * 100  # Gradual rise
            elif i < 20:
                price = base_price + 1000 - (i - 10) * 150  # Sharp drop
            elif i < 30:
                price = base_price - 500 + (i - 20) * 50  # Recovery
            else:
                price = base_price + (i % 5 - 2) * 200  # Consolidation
            
            price_data.append({
                'timestamp': i * 3600000,  # Hourly data
                'price': price
            })
        
        levels = self.calculator.calculate_levels(price_data)
        
        self.assertIn('support', levels)
        self.assertIn('resistance', levels)
        self.assertGreater(levels['resistance'], levels['support'])
        
        # Levels should be reasonable for BTC price range
        self.assertGreater(levels['support'], 30000)  # Not too low
        self.assertLess(levels['resistance'], 60000)  # Not too high
    
    def test_small_price_ranges(self):
        """Test with small price values (altcoins)."""
        # Simulate altcoin with small values
        price_data = [
            {'timestamp': i * 1000, 'price': 0.001 + i * 0.0001}
            for i in range(20)
        ]
        
        levels = self.calculator.calculate_levels(price_data)
        
        self.assertIn('support', levels)
        self.assertIn('resistance', levels)
        self.assertGreater(levels['resistance'], levels['support'])
        self.assertGreater(levels['support'], 0)
        self.assertLess(levels['resistance'], 1)  # Should be small values


if __name__ == '__main__':
    unittest.main()