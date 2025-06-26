"""
Real-time cryptocurrency price monitoring system.

This module provides continuous monitoring of specified cryptocurrencies,
tracking support/resistance levels and triggering alerts when prices reach these levels.
"""

import asyncio
import json
import logging
import signal
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tools.coin_historical_chart_by_id import get_coin_historical_chart_by_id

# Import support_resistance from relative path
sys.path.append(str(Path(__file__).parent))
from support_resistance import SupportResistanceCalculator


@dataclass
class TokenConfig:
    """Configuration for a monitored token."""
    symbol: str
    coin_id: str
    support_level: float = 0.0
    resistance_level: float = 0.0
    last_alert_time: Optional[datetime] = None
    price_history: List[Dict] = None
    
    def __post_init__(self):
        if self.price_history is None:
            self.price_history = []


@dataclass
class MonitorState:
    """Persistent state for the monitoring system."""
    tokens: Dict[str, TokenConfig]
    start_time: datetime
    last_update: datetime
    alerts_sent: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            'tokens': {},
            'start_time': self.start_time.isoformat(),
            'last_update': self.last_update.isoformat(),
            'alerts_sent': self.alerts_sent
        }
        
        for symbol, config in self.tokens.items():
            token_dict = asdict(config)
            if config.last_alert_time:
                token_dict['last_alert_time'] = config.last_alert_time.isoformat()
            result['tokens'][symbol] = token_dict
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MonitorState':
        """Create from dictionary loaded from JSON."""
        tokens = {}
        for symbol, token_data in data['tokens'].items():
            # Convert last_alert_time back to datetime
            if token_data.get('last_alert_time'):
                token_data['last_alert_time'] = datetime.fromisoformat(
                    token_data['last_alert_time']
                )
            tokens[symbol] = TokenConfig(**token_data)
        
        return cls(
            tokens=tokens,
            start_time=datetime.fromisoformat(data['start_time']),
            last_update=datetime.fromisoformat(data['last_update']),
            alerts_sent=data.get('alerts_sent', 0)
        )


class CryptoPriceMonitor:
    """
    Real-time cryptocurrency price monitoring system with support/resistance alerts.
    """
    
    # Mapping of symbols to CoinGecko IDs
    SYMBOL_TO_ID = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'PEPE': 'pepe',
        'VIRTUAL': 'virtuals-protocol',
        'AAVE': 'aave',
        'MKR': 'maker',
        'HYPE': 'hype-coin',
        'SPX': 'spx-6900',
        'ENA': 'ethena',
        'SEI': 'sei-network'
    }
    
    def __init__(self, symbols: List[str], state_file: str = "monitor_state.json",
                 alert_cooldown_minutes: int = 60, tolerance_percent: float = 1.0):
        """
        Initialize the price monitor.
        
        Args:
            symbols: List of crypto symbols to monitor
            state_file: Path to state persistence file
            alert_cooldown_minutes: Minimum minutes between alerts for same token
            tolerance_percent: Price tolerance for support/resistance levels
        """
        if not symbols:
            raise ValueError("symbols list cannot be empty")
        
        self.symbols = [s.upper() for s in symbols]
        # Make state file path relative to project root if not absolute
        if not Path(state_file).is_absolute():
            self.state_file = project_root / 'tasks' / 'crypto-price-monitor' / state_file
        else:
            self.state_file = Path(state_file)
        self.alert_cooldown = timedelta(minutes=alert_cooldown_minutes)
        self.tolerance_percent = tolerance_percent
        
        # Initialize components
        self.sr_calculator = SupportResistanceCalculator(lookback_hours=24)
        self.state = None
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Set up log file path relative to project root
        log_file = project_root / 'tasks' / 'crypto-price-monitor' / 'crypto_monitor.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def initialize(self):
        """Initialize the monitoring system."""
        self.logger.info("Initializing crypto price monitor...")
        
        # Load or create state
        await self._load_state()
        
        # Fetch initial historical data and calculate levels
        await self._update_support_resistance_levels()
        
        self.logger.info(f"Monitor initialized for symbols: {', '.join(self.symbols)}")
    
    async def _load_state(self):
        """Load monitoring state from file or create new."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                self.state = MonitorState.from_dict(data)
                self.logger.info(f"Loaded existing state with {len(self.state.tokens)} tokens")
            except Exception as e:
                self.logger.warning(f"Failed to load state file: {e}")
                self._create_new_state()
        else:
            self._create_new_state()
    
    def _create_new_state(self):
        """Create new monitoring state."""
        tokens = {}
        for symbol in self.symbols:
            coin_id = self.SYMBOL_TO_ID.get(symbol)
            if not coin_id:
                self.logger.warning(f"Unknown coin ID for symbol {symbol}")
                continue
            tokens[symbol] = TokenConfig(symbol=symbol, coin_id=coin_id)
        
        self.state = MonitorState(
            tokens=tokens,
            start_time=datetime.now(),
            last_update=datetime.now()
        )
        self.logger.info(f"Created new state for {len(tokens)} tokens")
    
    async def _save_state(self):
        """Save current state to file."""
        try:
            self.state.last_update = datetime.now()
            with open(self.state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    async def _update_support_resistance_levels(self):
        """Update support and resistance levels for all tokens."""
        self.logger.info("Updating support/resistance levels...")
        
        for symbol, config in self.state.tokens.items():
            try:
                # Get historical data for the last 24 hours
                historical_data = await get_coin_historical_chart_by_id(
                    config.coin_id, 'usd', 1
                )
                
                if historical_data and 'prices' in historical_data:
                    prices = [price[1] for price in historical_data['prices']]
                    
                    # Calculate support and resistance levels
                    support, resistance = self.sr_calculator.calculate_levels(prices)
                    
                    config.support_level = support
                    config.resistance_level = resistance
                    config.price_history = [
                        {'timestamp': price[0], 'price': price[1]} 
                        for price in historical_data['prices']
                    ]
                    
                    self.logger.info(f"{symbol}: Support=${support:.4f}, Resistance=${resistance:.4f}")
                else:
                    self.logger.warning(f"No historical data available for {symbol}")
                
            except Exception as e:
                self.logger.error(f"Failed to update levels for {symbol}: {e}")
        
        await self._save_state()
    
    async def _price_callback(self, symbol: str, price_data: Dict):
        """Handle price updates from WebSocket."""
        try:
            current_price = float(price_data.get('price', 0))
            if current_price > 0:
                await self._check_price_alerts(symbol, current_price)
                
                # Update price history
                if symbol in self.state.tokens:
        config = self.state.tokens[symbol]
                    config.price_history.append({
            'timestamp': datetime.now().timestamp() * 1000,
            'price': current_price
                    })
        
        # Keep only last 24 hours of data
        cutoff_time = (datetime.now() - timedelta(hours=24)).timestamp() * 1000
        config.price_history = [
                        entry for entry in config.price_history 
                        if entry['timestamp'] > cutoff_time
        ]
        except Exception as e:
            self.logger.error(f"Error in price callback for {symbol}: {e}")
    
    async def _check_price_alerts(self, symbol: str, current_price: float):
        """Check if current price triggers any alerts."""
        if symbol not in self.state.tokens:
            return
        
        config = self.state.tokens[symbol]
        now = datetime.now()
        
        # Check if enough time has passed since last alert
        if (config.last_alert_time and 
            now - config.last_alert_time < self.alert_cooldown):
            return
        
        # Calculate tolerance
        support_tolerance = config.support_level * (self.tolerance_percent / 100)
        resistance_tolerance = config.resistance_level * (self.tolerance_percent / 100)
        
        # Check support level
        if (config.support_level > 0 and 
            current_price <= config.support_level + support_tolerance):
            await self._send_alert(symbol, current_price, "SUPPORT", config.support_level)
            config.last_alert_time = now
            self.state.alerts_sent += 1
        
        # Check resistance level
        elif (config.resistance_level > 0 and 
              current_price >= config.resistance_level - resistance_tolerance):
            await self._send_alert(symbol, current_price, "RESISTANCE", config.resistance_level)
            config.last_alert_time = now
            self.state.alerts_sent += 1
    
    async def _send_alert(self, symbol: str, price: float, alert_type: str, level: float):
        """Send price alert."""
        message = (
            f"🚨 {alert_type} ALERT: {symbol} "
            f"Price: ${price:.4f} | Level: ${level:.4f} | "
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        self.logger.warning(message)
        print(f"\n{message}\n")
        
        await self._save_state()
    
    async def _update_token_levels(self, symbol: str):
        """Update support/resistance levels for a specific token."""
        if symbol not in self.state.tokens:
            return
        
        config = self.state.tokens[symbol]
        try:
            historical_data = await get_coin_historical_chart_by_id(
                config.coin_id, 'usd', 1
            )
            
            if historical_data and 'prices' in historical_data:
                prices = [price[1] for price in historical_data['prices']]
                support, resistance = self.sr_calculator.calculate_levels(prices)
                
                config.support_level = support
                config.resistance_level = resistance
            
                self.logger.info(f"Updated {symbol}: Support=${support:.4f}, Resistance=${resistance:.4f}")
            
        except Exception as e:
            self.logger.error(f"Failed to update levels for {symbol}: {e}")
    
    async def _error_callback(self, error: str):
        """Handle WebSocket errors."""
        self.logger.error(f"WebSocket error: {error}")
    
    async def start_monitoring(self):
        """Start the monitoring system."""
        self.logger.info("Starting crypto price monitor...")
        self.running = True
        
        try:
            # Start monitoring loop
            await self._monitoring_loop()
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
        finally:
            await self._cleanup()
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Update levels every hour
                if (datetime.now() - self.state.last_update).total_seconds() > 3600:
                    await self._update_support_resistance_levels()
                
                # Save state periodically
                await self._save_state()
                
                # Sleep for a short interval
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up...")
        await self._save_state()
        self.logger.info("Cleanup complete")
    
    async def stop(self):
        """Stop the monitoring system."""
        self.logger.info("Stopping monitor...")
        self.running = False
        await self._cleanup()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Crypto Price Monitor")
    parser.add_argument("--symbols", nargs="+", 
                       default=["PEPE", "VIRTUAL", "AAVE", "MKR", "HYPE", "SPX", "ENA", "SEI"],
                       help="Cryptocurrency symbols to monitor")
    parser.add_argument("--state-file", default="monitor_state.json",
                       help="State persistence file path")
    parser.add_argument("--alert-cooldown", type=int, default=60,
                       help="Minutes between alerts for same token")
    parser.add_argument("--tolerance", type=float, default=1.0,
                       help="Price tolerance percentage for support/resistance levels")
    
    args = parser.parse_args()
    
    monitor = CryptoPriceMonitor(
        symbols=args.symbols,
        state_file=args.state_file,
        alert_cooldown_minutes=args.alert_cooldown,
        tolerance_percent=args.tolerance
    )
    
    try:
    await monitor.initialize()
    await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())