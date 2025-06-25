"""
Test suite for the price monitoring system.
"""

import unittest
import asyncio
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import sys

# Add project root to path for imports - supports execution from project root
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from tasks.crypto_price_monitor.src.price_monitor import CryptoPriceMonitor, TokenConfig, MonitorState


class TestTokenConfig(unittest.TestCase):
    """Test cases for TokenConfig dataclass."""
    
    def test_token_config_creation(self):
        """Test TokenConfig creation."""
        config = TokenConfig(symbol="BTC", coin_id="bitcoin")
        
        self.assertEqual(config.symbol, "BTC")
        self.assertEqual(config.coin_id, "bitcoin")
        self.assertEqual(config.support_level, 0.0)
        self.assertEqual(config.resistance_level, 0.0)
        self.assertIsNone(config.last_alert_time)
        self.assertEqual(config.price_history, [])
    
    def test_token_config_with_values(self):
        """Test TokenConfig with initial values."""
        now = datetime.now()
        history = [{'timestamp': 1000, 'price': 100}]
        
        config = TokenConfig(
            symbol="ETH",
            coin_id="ethereum",
            support_level=1500.0,
            resistance_level=1600.0,
            last_alert_time=now,
            price_history=history
        )
        
        self.assertEqual(config.symbol, "ETH")
        self.assertEqual(config.coin_id, "ethereum")
        self.assertEqual(config.support_level, 1500.0)
        self.assertEqual(config.resistance_level, 1600.0)
        self.assertEqual(config.last_alert_time, now)
        self.assertEqual(config.price_history, history)


class TestMonitorState(unittest.TestCase):
    """Test cases for MonitorState dataclass."""
    
    def test_monitor_state_creation(self):
        """Test MonitorState creation."""
        tokens = {
            'BTC': TokenConfig(symbol="BTC", coin_id="bitcoin"),
            'ETH': TokenConfig(symbol="ETH", coin_id="ethereum")
        }
        
        now = datetime.now()
        state = MonitorState(
            tokens=tokens,
            start_time=now,
            last_update=now,
            alerts_sent=5
        )
        
        self.assertEqual(len(state.tokens), 2)
        self.assertEqual(state.start_time, now)
        self.assertEqual(state.last_update, now)
        self.assertEqual(state.alerts_sent, 5)
    
    def test_monitor_state_serialization(self):
        """Test MonitorState to_dict and from_dict."""
        now = datetime.now()
        tokens = {
            'BTC': TokenConfig(
                symbol="BTC",
                coin_id="bitcoin",
                support_level=45000.0,
                resistance_level=47000.0,
                last_alert_time=now
            )
        }
        
        state = MonitorState(
            tokens=tokens,
            start_time=now,
            last_update=now,
            alerts_sent=3
        )
        
        # Test serialization
        state_dict = state.to_dict()
        
        self.assertIn('tokens', state_dict)
        self.assertIn('start_time', state_dict)
        self.assertIn('last_update', state_dict)
        self.assertIn('alerts_sent', state_dict)
        
        # Test deserialization
        restored_state = MonitorState.from_dict(state_dict)
        
        self.assertEqual(len(restored_state.tokens), 1)
        self.assertEqual(restored_state.tokens['BTC'].symbol, "BTC")
        self.assertEqual(restored_state.tokens['BTC'].support_level, 45000.0)
        self.assertEqual(restored_state.alerts_sent, 3)
        
        # Check datetime restoration
        self.assertIsInstance(restored_state.start_time, datetime)
        self.assertIsInstance(restored_state.last_update, datetime)
        self.assertIsInstance(restored_state.tokens['BTC'].last_alert_time, datetime)


class TestCryptoPriceMonitor(unittest.TestCase):
    """Test cases for CryptoPriceMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.symbols = ['BTC', 'ETH']
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        
        self.monitor = CryptoPriceMonitor(
            symbols=self.symbols,
            state_file=self.temp_file.name,
            alert_cooldown_minutes=30,
            tolerance_percent=0.5
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        self.assertEqual(self.monitor.symbols, ['BTC', 'ETH'])
        self.assertEqual(self.monitor.tolerance_percent, 0.5)
        self.assertEqual(self.monitor.alert_cooldown, timedelta(minutes=30))
        self.assertIsNotNone(self.monitor.sr_calculator)
        self.assertFalse(self.monitor.running)
    
    def test_monitor_empty_symbols(self):
        """Test monitor with empty symbols list."""
        with self.assertRaises(ValueError):
            CryptoPriceMonitor(symbols=[])
    
    def test_symbol_to_id_mapping(self):
        """Test symbol to CoinGecko ID mapping."""
        expected_mappings = {
            'PEPE': 'pepe',
            'VIRTUAL': 'virtuals-protocol',
            'AAVE': 'aave',
            'MKR': 'maker',
            'HYPE': 'hype-coin',
            'SPX': 'spx-6900',
            'ENA': 'ethena',
            'SEI': 'sei-network'
        }
        
        for symbol, coin_id in expected_mappings.items():
            self.assertEqual(
                CryptoPriceMonitor.SYMBOL_TO_ID[symbol],
                coin_id
            )
    
    def test_create_new_state(self):
        """Test creating new monitoring state."""
        # Use symbols that exist in SYMBOL_TO_ID
        monitor = CryptoPriceMonitor(['PEPE', 'AAVE'])
        monitor._create_new_state()
        
        self.assertIsNotNone(monitor.state)
        self.assertEqual(len(monitor.state.tokens), 2)
        self.assertIn('PEPE', monitor.state.tokens)
        self.assertIn('AAVE', monitor.state.tokens)
        self.assertEqual(monitor.state.tokens['PEPE'].coin_id, 'pepe')
        self.assertEqual(monitor.state.tokens['AAVE'].coin_id, 'aave')
    
    def test_create_new_state_unknown_symbols(self):
        """Test creating state with unknown symbols."""
        monitor = CryptoPriceMonitor(['UNKNOWN1', 'UNKNOWN2'])
        
        with patch.object(monitor, 'logger'):
            monitor._create_new_state()
        
        self.assertIsNotNone(monitor.state)
        self.assertEqual(len(monitor.state.tokens), 0)
    
    async def test_save_and_load_state(self):
        """Test state persistence."""
        # Create state with known symbols
        monitor = CryptoPriceMonitor(['PEPE'], state_file=self.temp_file.name)
        monitor._create_new_state()
        
        # Modify state
        monitor.state.tokens['PEPE'].support_level = 0.000001
        monitor.state.tokens['PEPE'].resistance_level = 0.000002
        monitor.state.alerts_sent = 5
        
        # Save state
        await monitor._save_state()
        
        # Create new monitor and load state
        new_monitor = CryptoPriceMonitor(['PEPE'], state_file=self.temp_file.name)
        await new_monitor._load_state()
        
        self.assertIsNotNone(new_monitor.state)
        self.assertEqual(len(new_monitor.state.tokens), 1)
        self.assertEqual(new_monitor.state.tokens['PEPE'].support_level, 0.000001)
        self.assertEqual(new_monitor.state.tokens['PEPE'].resistance_level, 0.000002)
        self.assertEqual(new_monitor.state.alerts_sent, 5)
    
    async def test_load_state_file_not_exists(self):
        """Test loading state when file doesn't exist."""
        non_existent_file = "/tmp/non_existent_file.json"
        monitor = CryptoPriceMonitor(['PEPE'], state_file=non_existent_file)
        
        await monitor._load_state()
        
        self.assertIsNotNone(monitor.state)
        self.assertEqual(len(monitor.state.tokens), 1)
    
    async def test_load_state_invalid_json(self):
        """Test loading state with invalid JSON."""
        # Write invalid JSON to file
        with open(self.temp_file.name, 'w') as f:
            f.write("invalid json content")
        
        monitor = CryptoPriceMonitor(['PEPE'], state_file=self.temp_file.name)
        
        with patch.object(monitor, 'logger'):
            await monitor._load_state()
        
        # Should create new state when loading fails
        self.assertIsNotNone(monitor.state)
        self.assertEqual(len(monitor.state.tokens), 1)
    
    @patch('tasks.crypto_price_monitor.src.price_monitor.get_coin_historical_chart_by_id')
    async def test_update_support_resistance_levels(self, mock_get_chart):
        """Test updating support/resistance levels."""
        # Mock historical data
        mock_chart_data = {
            'prices': [
                [1640000000000, 45000],
                [1640003600000, 45500],
                [1640007200000, 44800],
                [1640010800000, 45200],
                [1640014400000, 45800]
            ]
        }
        mock_get_chart.return_value = mock_chart_data
        
        monitor = CryptoPriceMonitor(['PEPE'])
        monitor._create_new_state()
        
        await monitor._update_support_resistance_levels()
        
        # Check that levels were calculated
        pepe_config = monitor.state.tokens['PEPE']
        self.assertGreater(pepe_config.support_level, 0)
        self.assertGreater(pepe_config.resistance_level, 0)
        self.assertGreater(pepe_config.resistance_level, pepe_config.support_level)
        self.assertEqual(len(pepe_config.price_history), 5)
    
    @patch('tasks.crypto_price_monitor.src.price_monitor.get_coin_historical_chart_by_id')
    async def test_update_levels_no_data(self, mock_get_chart):
        """Test updating levels when no data is available."""
        mock_get_chart.return_value = None
        
        monitor = CryptoPriceMonitor(['PEPE'])
        monitor._create_new_state()
        
        with patch.object(monitor, 'logger'):
            await monitor._update_support_resistance_levels()
        
        # Levels should remain at default values
        pepe_config = monitor.state.tokens['PEPE']
        self.assertEqual(pepe_config.support_level, 0.0)
        self.assertEqual(pepe_config.resistance_level, 0.0)
    
    async def test_check_price_alerts_support(self):
        """Test price alert checking for support level."""
        monitor = CryptoPriceMonitor(['PEPE'])
        monitor._create_new_state()
        
        # Set up token config
        config = monitor.state.tokens['PEPE']
        config.support_level = 0.000001
        config.resistance_level = 0.000002
        
        # Mock the SR calculator
        monitor.sr_calculator.is_price_at_level = Mock(return_value=True)
        
        with patch.object(monitor, '_send_alert') as mock_send_alert:
            await monitor._check_price_alerts('PEPE', 0.000001)
        
        mock_send_alert.assert_called_once()
        call_args = mock_send_alert.call_args[0]
        self.assertEqual(call_args[0], 'PEPE')  # symbol
        self.assertEqual(call_args[1], 0.000001)  # price
        self.assertEqual(call_args[2], 'SUPPORT')  # alert_type
        self.assertEqual(call_args[3], 0.000001)  # level
    
    async def test_check_price_alerts_resistance(self):
        """Test price alert checking for resistance level."""
        monitor = CryptoPriceMonitor(['PEPE'])
        monitor._create_new_state()
        
        # Set up token config
        config = monitor.state.tokens['PEPE']
        config.support_level = 0.000001
        config.resistance_level = 0.000002
        
        # Mock the SR calculator to return False for support, True for resistance
        def mock_is_price_at_level(price, level, tolerance):
            return level == 0.000002  # Only return True for resistance level
        
        monitor.sr_calculator.is_price_at_level = Mock(side_effect=mock_is_price_at_level)
        
        with patch.object(monitor, '_send_alert') as mock_send_alert:
            await monitor._check_price_alerts('PEPE', 0.000002)
        
        mock_send_alert.assert_called_once()
        call_args = mock_send_alert.call_args[0]
        self.assertEqual(call_args[2], 'RESISTANCE')  # alert_type
    
    async def test_check_price_alerts_cooldown(self):
        """Test alert cooldown functionality."""
        monitor = CryptoPriceMonitor(['PEPE'], alert_cooldown_minutes=60)
        monitor._create_new_state()
        
        # Set up token config with recent alert
        config = monitor.state.tokens['PEPE']
        config.support_level = 0.000001
        config.last_alert_time = datetime.now() - timedelta(minutes=30)  # 30 min ago
        
        monitor.sr_calculator.is_price_at_level = Mock(return_value=True)
        
        with patch.object(monitor, '_send_alert') as mock_send_alert:
            await monitor._check_price_alerts('PEPE', 0.000001)
        
        # Should not send alert due to cooldown
        mock_send_alert.assert_not_called()
    
    async def test_check_price_alerts_cooldown_expired(self):
        """Test alert when cooldown has expired."""
        monitor = CryptoPriceMonitor(['PEPE'], alert_cooldown_minutes=60)
        monitor._create_new_state()
        
        # Set up token config with old alert
        config = monitor.state.tokens['PEPE']
        config.support_level = 0.000001
        config.last_alert_time = datetime.now() - timedelta(minutes=90)  # 90 min ago
        
        monitor.sr_calculator.is_price_at_level = Mock(return_value=True)
        
        with patch.object(monitor, '_send_alert') as mock_send_alert:
            await monitor._check_price_alerts('PEPE', 0.000001)
        
        # Should send alert since cooldown expired
        mock_send_alert.assert_called_once()
    
    async def test_price_callback(self):
        """Test real-time price callback."""
        monitor = CryptoPriceMonitor(['PEPE'])
        monitor._create_new_state()
        
        price_data = {'price': 0.000001}
        
        with patch.object(monitor, '_check_price_alerts') as mock_check_alerts:
            await monitor._price_callback('PEPE', price_data)
        
        # Check that price was added to history
        config = monitor.state.tokens['PEPE']
        self.assertEqual(len(config.price_history), 1)
        self.assertEqual(config.price_history[0]['price'], 0.000001)
        
        # Check that alerts were checked
        mock_check_alerts.assert_called_once_with('PEPE', 0.000001)
    
    async def test_price_callback_unknown_symbol(self):
        """Test price callback for unknown symbol."""
        monitor = CryptoPriceMonitor(['PEPE'])
        monitor._create_new_state()
        
        price_data = {'price': 100}
        
        # Should not raise exception for unknown symbol
        await monitor._price_callback('UNKNOWN', price_data)
        
        # PEPE history should remain empty
        config = monitor.state.tokens['PEPE']
        self.assertEqual(len(config.price_history), 0)
    
    async def test_send_alert_formatting(self):
        """Test alert message formatting."""
        monitor = CryptoPriceMonitor(['PEPE'])
        
        with patch('builtins.print') as mock_print:
            with patch.object(monitor, 'logger'):
                await monitor._send_alert('PEPE', 0.000001, 'SUPPORT', 0.0000009)
        
        # Check that print was called (console output)
        self.assertTrue(mock_print.called)
        
        # Check alert message content
        printed_args = mock_print.call_args_list
        alert_content = ''.join(str(call[0][0]) for call in printed_args)
        
        self.assertIn('CRYPTO ALERT', alert_content)
        self.assertIn('PEPE', alert_content)
        self.assertIn('SUPPORT', alert_content)
        self.assertIn('0.000001', alert_content)


class TestAsyncMethods(unittest.IsolatedAsyncioTestCase):
    """Test cases that require async test framework."""
    
    async def test_monitoring_loop_basic(self):
        """Test basic monitoring loop functionality."""
        monitor = CryptoPriceMonitor(['PEPE'])
        monitor._create_new_state()
        monitor.running = True
        
        # Mock the update method to stop after one iteration
        update_call_count = 0
        original_update = monitor._update_support_resistance_levels
        
        async def mock_update():
            nonlocal update_call_count
            update_call_count += 1
            if update_call_count >= 1:
                monitor.running = False
            await original_update()
        
        monitor._update_support_resistance_levels = mock_update
        
        # Mock save state
        monitor._save_state = AsyncMock()
        
        # Run monitoring loop (should exit after one iteration)
        await monitor._monitoring_loop()
        
        self.assertEqual(update_call_count, 1)
        self.assertTrue(monitor._save_state.called)
    
    async def test_cleanup(self):
        """Test cleanup functionality."""
        monitor = CryptoPriceMonitor(['PEPE'])
        monitor._create_new_state()
        
        # Mock websocket client
        monitor.websocket_client = AsyncMock()
        monitor._save_state = AsyncMock()
        
        await monitor._cleanup()
        
        monitor.websocket_client.disconnect.assert_called_once()
        monitor._save_state.assert_called_once()


if __name__ == '__main__':
    unittest.main()