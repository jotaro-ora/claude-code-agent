#!/usr/bin/env python3
"""
Simple Crypto Price Monitor

A simplified version that uses periodic polling instead of WebSocket connections.
This version is more reliable for testing and demonstration purposes.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import signal
import sys
from dataclasses import dataclass, asdict

# Add project root to path for tool imports - supports execution from project root
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tools.coin_historical_chart_by_id import get_coin_historical_chart_by_id
from tools.coins_list_market_data import get_coins_list_market_data

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
    last_price: float = 0.0
    
    def __post_init__(self):
        if self.last_alert_time is None:
            self.last_alert_time = datetime.now() - timedelta(hours=2)


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


class SimpleCryptoPriceMonitor:
    """
    Simple cryptocurrency price monitoring system with support/resistance alerts.
    Uses periodic polling instead of WebSocket connections for better reliability.
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
    
    def __init__(self, symbols: List[str], state_file: str = "simple_monitor_state.json",
                 alert_cooldown_minutes: int = 60, tolerance_percent: float = 1.0,
                 check_interval_minutes: int = 5):
        """
        Initialize the simple price monitor.
        
        Args:
            symbols: List of crypto symbols to monitor
            state_file: Path to state persistence file
            alert_cooldown_minutes: Minimum minutes between alerts for same token
            tolerance_percent: Price tolerance for support/resistance levels
            check_interval_minutes: Minutes between price checks
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
        self.check_interval = timedelta(minutes=check_interval_minutes)
        
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
        log_file = project_root / 'tasks' / 'crypto-price-monitor' / 'simple_monitor.log'
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
    
    def initialize(self):
        """Initialize the monitoring system."""
        self.logger.info("Initializing simple crypto price monitor...")
        
        # Load or create state
        self._load_state()
        
        # Fetch initial historical data and calculate levels
        self._update_support_resistance_levels()
        
        self.logger.info(f"Monitor initialized for symbols: {', '.join(self.symbols)}")
    
    def _load_state(self):
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
    
    def _save_state(self):
        """Save current state to file."""
        try:
            self.state.last_update = datetime.now()
            with open(self.state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def _update_support_resistance_levels(self):
        """Update support and resistance levels for all tokens."""
        self.logger.info("Updating support/resistance levels...")
        
        for symbol, config in self.state.tokens.items():
            try:
                # Fetch 24h historical data
                chart_data = get_coin_historical_chart_by_id(
                    config.coin_id, 'usd', 1
                )
                
                if not chart_data or 'prices' not in chart_data:
                    self.logger.warning(f"No price data for {symbol}")
                    continue
                
                # Convert to format expected by calculator
                price_data = []
                for timestamp, price in chart_data['prices']:
                    price_data.append({
                        'timestamp': timestamp,
                        'price': price
                    })
                
                # Calculate levels
                levels = self.sr_calculator.calculate_levels(price_data)
                config.support_level = levels['support']
                config.resistance_level = levels['resistance']
                
                # Update last price
                if price_data:
                    config.last_price = price_data[-1]['price']
                
                self.logger.info(
                    f"{symbol}: Support=${config.support_level:.6f}, "
                    f"Resistance=${config.resistance_level:.6f}, "
                    f"Last Price=${config.last_price:.6f}"
                )
                
            except Exception as e:
                self.logger.error(f"Failed to update levels for {symbol}: {e}")
        
        self._save_state()
    
    def _get_current_prices(self) -> Dict[str, float]:
        """Get current prices for monitored tokens."""
        try:
            # Fetch market data for top coins (this includes most major cryptocurrencies)
            market_data = get_coins_list_market_data(
                vs_currency='usd',
                per_page=250,  # Get top 250 coins to ensure we catch our tokens
                order='market_cap_desc'
            )
            
            if market_data is None or len(market_data) == 0:
                self.logger.warning("No market data received")
                return {}
            
            # Map back to symbols
            prices = {}
            for _, coin in market_data.iterrows():
                coin_id = coin.get('id', '')
                current_price = coin.get('current_price', 0)
                
                # Find symbol for this coin_id
                for symbol, config in self.state.tokens.items():
                    if config.coin_id == coin_id and current_price > 0:
                        prices[symbol] = current_price
                        break
            
            return prices
            
        except Exception as e:
            self.logger.error(f"Failed to get current prices: {e}")
            return {}
    
    def _check_price_alerts(self, symbol: str, current_price: float):
        """Check if price triggers support/resistance alerts."""
        config = self.state.tokens[symbol]
        now = datetime.now()
        
        # Check alert cooldown
        if (config.last_alert_time and 
            now - config.last_alert_time < self.alert_cooldown):
            return
        
        alert_triggered = False
        alert_type = ""
        level_price = 0.0
        
        # Check support level
        if (config.support_level > 0 and 
            self.sr_calculator.is_price_at_level(
                current_price, config.support_level, self.tolerance_percent
            )):
            alert_triggered = True
            alert_type = "SUPPORT"
            level_price = config.support_level
        
        # Check resistance level
        elif (config.resistance_level > 0 and 
              self.sr_calculator.is_price_at_level(
                  current_price, config.resistance_level, self.tolerance_percent
              )):
            alert_triggered = True
            alert_type = "RESISTANCE"
            level_price = config.resistance_level
        
        if alert_triggered:
            self._send_alert(symbol, current_price, alert_type, level_price)
            config.last_alert_time = now
            self.state.alerts_sent += 1
            self._save_state()
    
    def _send_alert(self, symbol: str, price: float, alert_type: str, level: float):
        """Send price alert notification."""
        message = (
            f"🚨 CRYPTO ALERT 🚨\n"
            f"Symbol: {symbol}\n"
            f"Current Price: ${price:.6f}\n"
            f"Alert Type: {alert_type} LEVEL REACHED\n"
            f"Level Price: ${level:.6f}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Print to console (could be extended to send notifications)
        print("\n" + "="*50)
        print(message)
        print("="*50 + "\n")
        
        self.logger.warning(f"🚨 ALERT: {symbol} {alert_type} at ${price:.6f}")
    
    def _monitoring_cycle(self):
        """Run one monitoring cycle."""
        try:
            # Get current prices
            current_prices = self._get_current_prices()
            
            if not current_prices:
                self.logger.warning("No price data available for this cycle")
                return
            
            self.logger.debug(f"Price check: {current_prices}")
            
            # Check each token for alerts
            for symbol, current_price in current_prices.items():
                if symbol in self.state.tokens:
                    # Update last price
                    self.state.tokens[symbol].last_price = current_price
                    
                    # Check for alerts
                    self._check_price_alerts(symbol, current_price)
            
            # Save state
            self._save_state()
            
        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {e}")
    
    def start_monitoring(self):
        """Start the monitoring system with periodic checks."""
        self.running = True
        self.logger.info(f"Starting simple cryptocurrency monitoring...")
        self.logger.info(f"Check interval: {self.check_interval.total_seconds()/60:.1f} minutes")
        self.logger.info(f"Alert cooldown: {self.alert_cooldown.total_seconds()/60:.1f} minutes")
        
        last_level_update = datetime.now()
        level_update_interval = timedelta(hours=1)  # Update levels every hour
        
        try:
            while self.running:
                cycle_start = datetime.now()
                
                # Run monitoring cycle
                self._monitoring_cycle()
                
                # Periodic level updates (every hour)
                if datetime.now() - last_level_update >= level_update_interval:
                    self._update_support_resistance_levels()
                    last_level_update = datetime.now()
                
                # Calculate sleep time
                elapsed = datetime.now() - cycle_start
                sleep_time = max(0, self.check_interval.total_seconds() - elapsed.total_seconds())
                
                if sleep_time > 0:
                    self.logger.debug(f"Sleeping for {sleep_time:.1f} seconds...")
                    for _ in range(int(sleep_time)):
                        if not self.running:
                            break
                        import time
                        time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Monitor stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup resources."""
        self.logger.info("Cleaning up resources...")
        self._save_state()
        self.logger.info("Simple monitor cleanup completed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Simple Cryptocurrency Price Monitor with Support/Resistance Alerts"
    )
    parser.add_argument(
        '--symbols', 
        nargs='+', 
        default=['PEPE', 'VIRTUAL', 'AAVE', 'MKR', 'HYPE', 'SPX', 'ENA', 'SEI'],
        help='Crypto symbols to monitor'
    )
    parser.add_argument(
        '--state-file', 
        default='simple_monitor_state.json',
        help='State persistence file path'
    )
    parser.add_argument(
        '--alert-cooldown', 
        type=int, 
        default=60,
        help='Minutes between alerts for same token'
    )
    parser.add_argument(
        '--tolerance', 
        type=float, 
        default=1.0,
        help='Price tolerance percentage for support/resistance levels'
    )
    parser.add_argument(
        '--check-interval', 
        type=int, 
        default=5,
        help='Minutes between price checks'
    )
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = SimpleCryptoPriceMonitor(
        symbols=args.symbols,
        state_file=args.state_file,
        alert_cooldown_minutes=args.alert_cooldown,
        tolerance_percent=args.tolerance,
        check_interval_minutes=args.check_interval
    )
    
    # Initialize and start monitoring
    monitor.initialize()
    monitor.start_monitoring()


if __name__ == "__main__":
    main()