#!/usr/bin/env python3
"""
BTC Price Monitor - Monitors BTC price for significant spikes and sends notifications.

This module monitors Bitcoin (BTC) price changes and sends notifications when the price
increases by more than a configurable threshold within a specified time window.
It includes duplicate notification prevention via cooldown periods.
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Add project root to path for tool imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from tools.coin_data_by_id import get_coin_data_by_id


def calculate_percentage_change(old_price: float, new_price: float) -> float:
    """
    Calculate percentage change between two prices.
    
    Args:
        old_price (float): The original price
        new_price (float): The new price
        
    Returns:
        float: Percentage change (positive for increase, negative for decrease)
    """
    if old_price == 0:
        return 0.0
    return ((new_price - old_price) / old_price) * 100


class BTCPriceMonitor:
    """
    Bitcoin price monitoring class that tracks price changes and sends notifications
    for significant price spikes while preventing duplicate notifications.
    """
    
    def __init__(self, threshold_percent: float = 0.1, window_minutes: int = 15, 
                 cooldown_minutes: int = 60, state_file: str = None):
        """
        Initialize the BTC price monitor.
        
        Args:
            threshold_percent (float): Minimum percentage increase to trigger notification
            window_minutes (int): Time window in minutes to check for price changes
            cooldown_minutes (int): Cooldown period in minutes between notifications
            state_file (str): Path to state persistence file
        """
        self.threshold_percent = threshold_percent
        self.window_minutes = window_minutes
        self.cooldown_minutes = cooldown_minutes
        
        # Default state file location
        if state_file is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            state_file = os.path.join(data_dir, 'btc_monitor_state.json')
        
        self.state_file = state_file
        self.state = self.load_state()
        
        # Initialize price history if not exists
        if 'price_history' not in self.state:
            self.state['price_history'] = []
    
    def load_state(self) -> Dict[str, Any]:
        """
        Load monitoring state from file.
        
        Returns:
            Dict[str, Any]: State dictionary containing price history and last notification time
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
    
    def should_send_notification(self) -> bool:
        """
        Check if enough time has passed since the last notification.
        
        Returns:
            bool: True if notification should be sent, False otherwise
        """
        if 'last_notification' not in self.state:
            return True
        
        try:
            last_notification = datetime.fromisoformat(self.state['last_notification'])
            cooldown_end = last_notification + timedelta(minutes=self.cooldown_minutes)
            return datetime.now() > cooldown_end
        except (ValueError, TypeError):
            # Invalid timestamp, allow notification
            return True
    
    def add_price_to_history(self, price: float, timestamp: datetime = None) -> None:
        """
        Add a price point to the history and clean up old entries.
        
        Args:
            price (float): Current BTC price
            timestamp (datetime): Timestamp for the price point (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        price_point = {
            'price': price,
            'timestamp': timestamp.isoformat()
        }
        
        self.state['price_history'].append(price_point)
        self.cleanup_old_history()
    
    def cleanup_old_history(self) -> None:
        """Remove price history entries older than the monitoring window."""
        cutoff_time = datetime.now() - timedelta(minutes=self.window_minutes)
        
        self.state['price_history'] = [
            point for point in self.state['price_history']
            if datetime.fromisoformat(point['timestamp']) > cutoff_time
        ]
    
    def check_price_spike(self, current_price: float) -> bool:
        """
        Check if the current price represents a significant spike.
        
        Args:
            current_price (float): Current BTC price
            
        Returns:
            bool: True if price spike detected, False otherwise
        """
        if not self.state['price_history']:
            return False
        
        # Find the lowest price in the window
        min_price = min(point['price'] for point in self.state['price_history'])
        
        # Calculate percentage change from minimum
        percentage_change = calculate_percentage_change(min_price, current_price)
        
        return percentage_change >= self.threshold_percent
    
    def get_btc_price(self) -> Optional[float]:
        """
        Fetch current BTC price using CoinGecko API.
        
        Returns:
            Optional[float]: Current BTC price in USD, or None if fetch failed
        """
        try:
            data = get_coin_data_by_id('bitcoin')
            return data['market_data']['current_price']['usd']
        except Exception as e:
            print(f"Error fetching BTC price: {e}")
            return None
    
    def send_notification(self, old_price: float, new_price: float, percentage_change: float) -> None:
        """
        Send notification about price spike.
        
        Args:
            old_price (float): Previous minimum price in window
            new_price (float): Current price
            percentage_change (float): Percentage increase
        """
        message = f"""
🚨 BTC PRICE SPIKE ALERT 🚨
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
From: ${old_price:,.2f}
To: ${new_price:,.2f}
Change: +{percentage_change:.2f}%
Threshold: {self.threshold_percent}%
Window: {self.window_minutes} minutes
        """.strip()
        
        print(message)
        
        # Update last notification time
        self.state['last_notification'] = datetime.now().isoformat()
        self.save_state(self.state)
    
    def check_and_notify(self) -> None:
        """
        Perform a single check cycle: fetch price, check for spike, and notify if needed.
        """
        current_price = self.get_btc_price()
        
        if current_price is None:
            print("Failed to fetch BTC price, skipping check")
            return
        
        print(f"Current BTC price: ${current_price:,.2f}")
        
        # Add current price to history
        self.add_price_to_history(current_price)
        
        # Check for price spike
        if self.check_price_spike(current_price):
            if self.should_send_notification():
                # Find minimum price in window for notification
                min_price = min(point['price'] for point in self.state['price_history'])
                percentage_change = calculate_percentage_change(min_price, current_price)
                
                self.send_notification(min_price, current_price, percentage_change)
            else:
                print(f"Price spike detected (+{calculate_percentage_change(min(p['price'] for p in self.state['price_history']), current_price):.2f}%) but notification is in cooldown")
        
        # Save state after each check
        self.save_state(self.state)
    
    def run_continuous(self, check_interval_seconds: int = 60) -> None:
        """
        Run continuous monitoring with specified check interval.
        
        Args:
            check_interval_seconds (int): Seconds between price checks
        """
        print(f"Starting BTC price monitoring...")
        print(f"Threshold: {self.threshold_percent}% increase")
        print(f"Window: {self.window_minutes} minutes")
        print(f"Cooldown: {self.cooldown_minutes} minutes")
        print(f"Check interval: {check_interval_seconds} seconds")
        print(f"State file: {self.state_file}")
        print("-" * 50)
        
        try:
            while True:
                self.check_and_notify()
                time.sleep(check_interval_seconds)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Monitoring error: {e}")
            raise


def main():
    """Main function with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Monitor BTC price for significant spikes and send notifications'
    )
    
    parser.add_argument(
        '--threshold', 
        type=float, 
        default=0.1,
        help='Percentage threshold for price spike notification (default: 0.1)'
    )
    
    parser.add_argument(
        '--window', 
        type=int, 
        default=15,
        help='Time window in minutes to monitor for price changes (default: 15)'
    )
    
    parser.add_argument(
        '--cooldown', 
        type=int, 
        default=60,
        help='Cooldown period in minutes between notifications (default: 60)'
    )
    
    parser.add_argument(
        '--interval', 
        type=int, 
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--state-file', 
        type=str,
        help='Path to state persistence file (default: ../data/btc_monitor_state.json)'
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
    
    # Create monitor instance
    monitor = BTCPriceMonitor(
        threshold_percent=args.threshold,
        window_minutes=args.window,
        cooldown_minutes=args.cooldown,
        state_file=args.state_file
    )
    
    if args.single_check:
        # Perform single check
        monitor.check_and_notify()
    else:
        # Run continuous monitoring
        monitor.run_continuous(args.interval)


if __name__ == '__main__':
    main()