#!/usr/bin/env python3
"""
ETH RSI Monitor - Monitors Ethereum RSI levels across multiple timeframes.

This module monitors Ethereum (ETH) RSI levels on 1H, 4H, and 1D timeframes
and sends alerts when RSI crosses overbought (>70) or oversold (<30) thresholds.
It includes duplicate notification prevention via cooldown periods.
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dotenv import load_dotenv

# Add project root to path for tool imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

try:
    from tools import coin_ohlc_by_id
    HAS_TOOLS = True
except ImportError as e:
    print(f"Warning: Could not import tools: {e}")
    HAS_TOOLS = False
    coin_ohlc_by_id = None


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    Calculate the Relative Strength Index (RSI) for a series of prices.
    
    Args:
        prices (List[float]): List of closing prices (oldest to newest)
        period (int): RSI calculation period (default: 14)
        
    Returns:
        Optional[float]: RSI value between 0-100, or None if insufficient data
        
    Raises:
        ValueError: If period is <= 0
    """
    if period <= 0:
        raise ValueError("RSI period must be positive")
    
    if len(prices) < period + 1:
        return None
    
    # Calculate price changes
    deltas = []
    for i in range(1, len(prices)):
        deltas.append(prices[i] - prices[i-1])
    
    # Separate gains and losses
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    # Calculate initial average gain and loss
    if len(gains) < period:
        return None
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # Calculate RSI using Wilder's smoothing method
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    # Calculate RSI
    if avg_loss == 0 and avg_gain == 0:
        return 50.0  # No price movement, RSI = 50 (neutral)
    elif avg_loss == 0:
        return 100.0  # No losses, RSI = 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def get_timeframe_data(timeframe: str) -> int:
    """Get days parameter for timeframe."""
    timeframe_mapping = {
        '1h': 1,     # 1 day of hourly data (48 points)
        '4h': 1,     # 1 day of hourly data (48 points, take every 4th)
        '1d': 30     # 30 days of daily data
    }
    
    if timeframe not in timeframe_mapping:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    
    return timeframe_mapping[timeframe]


class ETHRSIMonitor:
    """
    Ethereum RSI monitoring class that tracks RSI levels across multiple timeframes
    and sends notifications for overbought/oversold conditions with cooldown prevention.
    """
    
    def __init__(self, rsi_period: int = 14, overbought_threshold: float = 70,
                 oversold_threshold: float = 30, cooldown_minutes: int = 60,
                 timeframes: List[str] = None, state_file: str = None):
        """
        Initialize the ETH RSI monitor.
        
        Args:
            rsi_period (int): RSI calculation period (default: 14)
            overbought_threshold (float): RSI threshold for overbought alerts (default: 70)
            oversold_threshold (float): RSI threshold for oversold alerts (default: 30)
            cooldown_minutes (int): Cooldown period in minutes between duplicate notifications (default: 60)
            timeframes (List[str]): List of timeframes to monitor (default: ['1h', '4h', '1d'])
            state_file (str): Path to state persistence file
        """
        self.rsi_period = rsi_period
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
        self.cooldown_minutes = cooldown_minutes
        self.timeframes = timeframes or ['1h', '4h', '1d']
        
        # Default state file location
        if state_file is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            state_file = os.path.join(data_dir, 'eth_rsi_state.json')
        
        self.state_file = state_file
        self.state = self.load_state()
        
        # Initialize last notifications if not exists
        if 'last_notifications' not in self.state:
            self.state['last_notifications'] = {}
    
    def load_state(self) -> Dict[str, Any]:
        """
        Load monitoring state from file.
        
        Returns:
            Dict[str, Any]: State dictionary containing notification history
        """
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load state file: {e}")
        
        return {}
    
    def save_state(self, state: Dict[str, Any]) -> None:
        """
        Save monitoring state to file.
        
        Args:
            state (Dict[str, Any]): State dictionary to save
        """
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save state file: {e}")
    
    def should_send_notification(self, timeframe: str, condition: str) -> bool:
        """
        Check if enough time has passed since the last notification for this timeframe/condition.
        
        Args:
            timeframe (str): The timeframe being checked ('1h', '4h', '1d')
            condition (str): The condition ('overbought' or 'oversold')
            
        Returns:
            bool: True if notification should be sent, False otherwise
        """
        if timeframe not in self.state['last_notifications']:
            return True
        
        last_notification = self.state['last_notifications'][timeframe]
        
        # Check if same condition
        if last_notification.get('condition') != condition:
            return True
        
        try:
            last_time = datetime.fromisoformat(last_notification['timestamp'])
            cooldown_end = last_time + timedelta(minutes=self.cooldown_minutes)
            return datetime.now() > cooldown_end
        except (ValueError, TypeError, KeyError):
            # Invalid timestamp or missing data, allow notification
            return True
    
    def record_notification(self, timeframe: str, condition: str) -> None:
        """
        Record that a notification was sent for this timeframe/condition.
        
        Args:
            timeframe (str): The timeframe that triggered the notification
            condition (str): The condition that triggered the notification
        """
        self.state['last_notifications'][timeframe] = {
            'condition': condition,
            'timestamp': datetime.now().isoformat()
        }
        self.save_state(self.state)
    
    def get_ohlc_data(self, timeframe: str) -> Optional[List[List[float]]]:
        """
        Fetch OHLC data for ETH using CoinGecko API.
        
        Args:
            timeframe (str): Timeframe to fetch ('1h', '4h', '1d')
            
        Returns:
            Optional[List[List[float]]]: OHLC data as [timestamp, open, high, low, close] lists,
                                       or None if fetch failed
        """
        if not HAS_TOOLS:
            print("Error: CoinGecko tools not available")
            return None
        
        try:
            days = get_timeframe_data(timeframe)
            
            # Get OHLC data from CoinGecko
            ohlc_data = coin_ohlc_by_id.get_coin_ohlc_by_id(
                coin_id='ethereum',
                vs_currency='usd',
                days=days
            )
            
            return ohlc_data
            
        except Exception as e:
            print(f"Error fetching OHLC data for {timeframe}: {e}")
            return None
    
    def process_ohlc_for_timeframe(self, ohlc_data: List[List[float]], timeframe: str) -> List[float]:
        """Process OHLC data for timeframe."""
        closes = [candle[4] for candle in ohlc_data]
        
        if timeframe == '4h':
            # For 4h, use every 4th hour but with shorter RSI period if needed
            return closes[3::4]  
        
        return closes
    
    def send_notification(self, timeframe: str, condition: str, rsi_value: float) -> None:
        """
        Send notification about RSI condition.
        
        Args:
            timeframe (str): Timeframe that triggered the alert
            condition (str): Condition that triggered the alert ('overbought' or 'oversold')
            rsi_value (float): Current RSI value
        """
        emoji = "🔴" if condition == "overbought" else "🟢"
        threshold = self.overbought_threshold if condition == "overbought" else self.oversold_threshold
        
        message = f"""
{emoji} ETH RSI ALERT {emoji}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Timeframe: {timeframe.upper()}
Condition: {condition.upper()}
RSI: {rsi_value:.1f}
Threshold: {threshold}
Period: {self.rsi_period}
        """.strip()
        
        print(message)
        
        # Record the notification
        self.record_notification(timeframe, condition)
    
    def check_timeframe(self, timeframe: str) -> Optional[str]:
        """
        Check RSI for a specific timeframe and send alerts if needed.
        
        Args:
            timeframe (str): Timeframe to check ('1h', '4h', '1d')
            
        Returns:
            Optional[str]: Alert condition if triggered ('overbought', 'oversold'), None otherwise
        """
        print(f"Checking {timeframe.upper()} RSI...")
        
        # Get OHLC data
        ohlc_data = self.get_ohlc_data(timeframe)
        if ohlc_data is None:
            print(f"Failed to fetch OHLC data for {timeframe}")
            return None
        
        # Process data for timeframe
        closes = self.process_ohlc_for_timeframe(ohlc_data, timeframe)
        
        # Adjust RSI period if insufficient data
        rsi_period = self.rsi_period
        if len(closes) < rsi_period + 1:
            rsi_period = min(len(closes) - 1, 9)  # Use minimum 9 period
            if rsi_period < 2:
                print(f"Insufficient data for {timeframe} RSI calculation (got {len(closes)})")
                return None
            print(f"Using shorter RSI period {rsi_period} for {timeframe} (data points: {len(closes)})")
        
        # Calculate RSI
        rsi = calculate_rsi(closes, rsi_period)
        if rsi is None:
            print(f"Failed to calculate RSI for {timeframe}")
            return None
        
        print(f"{timeframe.upper()} RSI: {rsi:.1f}")
        
        # Check for alert conditions
        condition = None
        if rsi >= self.overbought_threshold:
            condition = 'overbought'
        elif rsi <= self.oversold_threshold:
            condition = 'oversold'
        
        if condition:
            if self.should_send_notification(timeframe, condition):
                self.send_notification(timeframe, condition, rsi)
                return condition
            else:
                print(f"{timeframe.upper()} {condition} condition detected but notification is in cooldown")
        
        return condition
    
    def check_all_timeframes(self) -> Dict[str, Optional[str]]:
        """
        Check RSI for all configured timeframes.
        
        Returns:
            Dict[str, Optional[str]]: Dictionary mapping timeframes to alert conditions
        """
        results = {}
        
        for timeframe in self.timeframes:
            try:
                condition = self.check_timeframe(timeframe)
                results[timeframe] = condition
            except Exception as e:
                print(f"Error checking {timeframe}: {e}")
                results[timeframe] = None
        
        return results
    
    def run_continuous(self, check_interval_seconds: int = 300) -> None:
        """
        Run continuous RSI monitoring with specified check interval.
        
        Args:
            check_interval_seconds (int): Seconds between RSI checks (default: 300 = 5 minutes)
        """
        print(f"Starting ETH RSI monitoring...")
        print(f"Timeframes: {', '.join(self.timeframes)}")
        print(f"RSI period: {self.rsi_period}")
        print(f"Overbought threshold: {self.overbought_threshold}")
        print(f"Oversold threshold: {self.oversold_threshold}")
        print(f"Cooldown: {self.cooldown_minutes} minutes")
        print(f"Check interval: {check_interval_seconds} seconds")
        print(f"State file: {self.state_file}")
        print("-" * 50)
        
        try:
            while True:
                self.check_all_timeframes()
                print(f"Next check in {check_interval_seconds} seconds...")
                print("-" * 30)
                time.sleep(check_interval_seconds)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Monitoring error: {e}")
            raise


def main():
    """Main function with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Monitor ETH RSI levels across multiple timeframes and send alerts'
    )
    
    parser.add_argument(
        '--rsi-period', 
        type=int, 
        default=14,
        help='RSI calculation period (default: 14)'
    )
    
    parser.add_argument(
        '--overbought', 
        type=float, 
        default=70,
        help='RSI overbought threshold (default: 70)'
    )
    
    parser.add_argument(
        '--oversold', 
        type=float, 
        default=30,
        help='RSI oversold threshold (default: 30)'
    )
    
    parser.add_argument(
        '--cooldown', 
        type=int, 
        default=60,
        help='Cooldown period in minutes between duplicate notifications (default: 60)'
    )
    
    parser.add_argument(
        '--timeframes', 
        type=str, 
        nargs='+',
        default=['1h', '4h', '1d'],
        help='Timeframes to monitor (default: 1h 4h 1d)'
    )
    
    parser.add_argument(
        '--interval', 
        type=int, 
        default=300,
        help='Check interval in seconds (default: 300)'
    )
    
    parser.add_argument(
        '--state-file', 
        type=str,
        help='Path to state persistence file (default: ../data/eth_rsi_state.json)'
    )
    
    parser.add_argument(
        '--single-check', 
        action='store_true',
        help='Perform single check instead of continuous monitoring'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check for required API key
    if not os.getenv('COINGECKO_API_KEY'):
        print("Error: COINGECKO_API_KEY not found in environment variables")
        print("Please add your CoinGecko API key to the .env file")
        sys.exit(1)
    
    # Check for required tools
    if not HAS_TOOLS:
        print("Error: CoinGecko tools not available")
        print("This may be due to missing dependencies in the tools")
        sys.exit(1)
    
    # Validate thresholds
    if args.overbought <= args.oversold:
        print("Error: Overbought threshold must be greater than oversold threshold")
        sys.exit(1)
    
    # Validate timeframes
    supported_timeframes = ['1h', '4h', '1d']
    for timeframe in args.timeframes:
        if timeframe not in supported_timeframes:
            print(f"Error: Unsupported timeframe '{timeframe}'. Supported: {supported_timeframes}")
            sys.exit(1)
    
    # Create monitor instance
    monitor = ETHRSIMonitor(
        rsi_period=args.rsi_period,
        overbought_threshold=args.overbought,
        oversold_threshold=args.oversold,
        cooldown_minutes=args.cooldown,
        timeframes=args.timeframes,
        state_file=args.state_file
    )
    
    if args.single_check:
        # Perform single check
        results = monitor.check_all_timeframes()
        print(f"\nCheck completed. Results: {results}")
    else:
        # Run continuous monitoring
        monitor.run_continuous(args.interval)


if __name__ == '__main__':
    main()