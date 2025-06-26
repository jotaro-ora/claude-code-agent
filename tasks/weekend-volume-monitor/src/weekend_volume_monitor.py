#!/usr/bin/env python3
"""
Weekend Volume Monitor - Monitors cryptocurrency market trading volume on weekends.

This module monitors total cryptocurrency market trading volume every weekend
and sends alerts if the weekend volume exceeds the historical average for weekends.
It compares current weekend volume to the average weekend volume over a configurable
historical period.
"""

import json
import os
import sys
import time
import argparse
try:
    import schedule
except ImportError:
    print("Warning: 'schedule' package not found. Install with: pip install schedule")
    schedule = None
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    print("Warning: 'pandas' package not found. Using basic data structures.")
    HAS_PANDAS = False

# Add project root to path for tool imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

try:
    from tools import coins_list_market_data
    HAS_TOOLS = True
except ImportError as e:
    print(f"Warning: Could not import tools: {e}")
    HAS_TOOLS = False
    coins_list_market_data = None


def is_weekend(date: datetime = None) -> bool:
    """
    Check if the given date is a weekend (Saturday or Sunday).
    
    Args:
        date (datetime): Date to check (defaults to current date)
        
    Returns:
        bool: True if date is Saturday or Sunday, False otherwise
    """
    if date is None:
        date = datetime.now()
    return date.weekday() >= 5  # Saturday = 5, Sunday = 6


def get_weekend_dates(reference_date: datetime = None) -> tuple:
    """
    Get the start and end dates for the weekend containing or preceding the reference date.
    
    Args:
        reference_date (datetime): Reference date (defaults to current date)
        
    Returns:
        tuple: (saturday_start, sunday_end) datetime objects
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    # Find the Saturday of the current or previous weekend
    days_since_saturday = (reference_date.weekday() + 2) % 7  # Convert to days since Saturday
    if reference_date.weekday() < 5:  # If it's a weekday, get previous weekend
        days_since_saturday += 7
    
    saturday = reference_date - timedelta(days=days_since_saturday)
    sunday = saturday + timedelta(days=1)
    
    # Set to start/end of day
    saturday_start = saturday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday_end = sunday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return saturday_start, sunday_end


def calculate_total_volume(market_data) -> float:
    """
    Calculate total trading volume from market data.
    
    Args:
        market_data: DataFrame or list of dictionaries containing market data with 'total_volume' field
        
    Returns:
        float: Total trading volume across all coins
    """
    if HAS_PANDAS and hasattr(market_data, 'empty'):
        # pandas DataFrame
        if market_data.empty or 'total_volume' not in market_data.columns:
            return 0.0
        volumes = market_data['total_volume'].fillna(0)
        return float(volumes.sum())
    else:
        # List of dictionaries or other iterable
        if not market_data:
            return 0.0
        
        total = 0.0
        for item in market_data:
            if isinstance(item, dict) and 'total_volume' in item:
                volume = item['total_volume']
                if volume is not None:
                    total += float(volume)
        return total


class WeekendVolumeMonitor:
    """
    Weekend cryptocurrency trading volume monitor that tracks volume patterns
    and sends alerts when weekend volume exceeds historical averages.
    """
    
    def __init__(self, historical_weeks: int = 4, top_n_coins: int = 100, 
                 alert_threshold_percent: float = 10.0, state_file: str = None):
        """
        Initialize the weekend volume monitor.
        
        Args:
            historical_weeks (int): Number of weeks of historical data to maintain
            top_n_coins (int): Number of top coins by market cap to monitor
            alert_threshold_percent (float): Percentage threshold above average to trigger alert
            state_file (str): Path to state persistence file
        """
        self.historical_weeks = historical_weeks
        self.top_n_coins = top_n_coins
        self.alert_threshold_percent = alert_threshold_percent
        
        # Default state file location
        if state_file is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            state_file = os.path.join(data_dir, 'weekend_volume_state.json')
        
        self.state_file = state_file
        self.state = self.load_state()
        
        # Initialize weekend volumes if not exists
        if 'weekend_volumes' not in self.state:
            self.state['weekend_volumes'] = []
    
    def load_state(self) -> Dict[str, Any]:
        """
        Load monitoring state from file.
        
        Returns:
            Dict[str, Any]: State dictionary containing weekend volume history
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
    
    def add_weekend_volume(self, weekend_date: datetime, volume: float) -> None:
        """
        Add a weekend volume measurement to the historical data.
        
        Args:
            weekend_date (datetime): Date of the weekend (Saturday or Sunday)
            volume (float): Total trading volume for the weekend
        """
        # Use Saturday as the canonical weekend date
        saturday, _ = get_weekend_dates(weekend_date)
        
        volume_entry = {
            'date': saturday.strftime('%Y-%m-%d'),
            'volume': volume,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if we already have data for this weekend
        existing_index = None
        for i, entry in enumerate(self.state['weekend_volumes']):
            if entry['date'] == volume_entry['date']:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update existing entry
            self.state['weekend_volumes'][existing_index] = volume_entry
        else:
            # Add new entry
            self.state['weekend_volumes'].append(volume_entry)
        
        # Sort by date and cleanup old data
        self.state['weekend_volumes'].sort(key=lambda x: x['date'])
        self.cleanup_old_data()
    
    def cleanup_old_data(self) -> None:
        """Remove weekend volume data older than the historical period."""
        if len(self.state['weekend_volumes']) > self.historical_weeks:
            # Keep only the most recent historical_weeks entries
            self.state['weekend_volumes'] = self.state['weekend_volumes'][-self.historical_weeks:]
    
    def get_historical_average(self) -> Optional[float]:
        """
        Calculate the historical average weekend volume.
        
        Returns:
            Optional[float]: Average weekend volume, or None if insufficient data
        """
        if len(self.state['weekend_volumes']) < 2:
            return None
        
        total_volume = sum(entry['volume'] for entry in self.state['weekend_volumes'])
        return total_volume / len(self.state['weekend_volumes'])
    
    def should_alert(self, current_volume: float) -> bool:
        """
        Check if current volume warrants an alert.
        
        Args:
            current_volume (float): Current weekend volume
            
        Returns:
            bool: True if alert should be sent, False otherwise
        """
        historical_avg = self.get_historical_average()
        
        if historical_avg is None:
            return False
        
        # Calculate percentage increase
        percentage_increase = ((current_volume - historical_avg) / historical_avg) * 100
        
        return percentage_increase >= self.alert_threshold_percent
    
    def get_current_volume(self) -> Optional[float]:
        """
        Fetch current total market trading volume using CoinGecko API.
        
        Returns:
            Optional[float]: Current total volume, or None if fetch failed
        """
        if not HAS_TOOLS:
            print("Error: CoinGecko tools not available")
            return None
            
        try:
            # Get market data for top N coins
            market_data = coins_list_market_data.get_coins_list_market_data(
                vs_currency='usd',
                per_page=self.top_n_coins,
                order='market_cap_desc'
            )
            
            # Convert DataFrame to list of dictionaries if pandas is available
            if HAS_PANDAS and hasattr(market_data, 'to_dict'):
                market_data = market_data.to_dict('records')
            
            return calculate_total_volume(market_data)
            
        except Exception as e:
            print(f"Error fetching current volume: {e}")
            return None
    
    def send_alert(self, current_volume: float, average_volume: float, percentage_increase: float) -> None:
        """
        Send alert about high weekend volume.
        
        Args:
            current_volume (float): Current weekend volume
            average_volume (float): Historical average volume
            percentage_increase (float): Percentage increase over average
        """
        weekend_start, weekend_end = get_weekend_dates()
        
        message = f"""
🔥 WEEKEND VOLUME ALERT 🔥
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Weekend: {weekend_start.strftime('%Y-%m-%d')} to {weekend_end.strftime('%Y-%m-%d')}

Current Volume: ${current_volume:,.0f}
Historical Avg: ${average_volume:,.0f}
Increase: +{percentage_increase:.1f}%

Alert Threshold: {self.alert_threshold_percent}%
Historical Period: {self.historical_weeks} weeks
Top Coins Monitored: {self.top_n_coins}
        """.strip()
        
        print(message)
        
        # Update last alert time
        self.state['last_alert'] = datetime.now().isoformat()
        self.save_state(self.state)
    
    def check_and_alert(self) -> None:
        """
        Perform weekend volume check and send alert if needed.
        """
        now = datetime.now()
        
        # Only check on weekends
        if not is_weekend(now):
            print(f"Not weekend - skipping check (today is {now.strftime('%A')})")
            return
        
        print(f"Weekend volume check - {now.strftime('%A, %Y-%m-%d %H:%M:%S')}")
        
        # Get current volume
        current_volume = self.get_current_volume()
        
        if current_volume is None:
            print("Failed to fetch current volume, skipping check")
            return
        
        print(f"Current total market volume: ${current_volume:,.0f}")
        
        # Add to historical data
        self.add_weekend_volume(now, current_volume)
        
        # Check if alert needed
        historical_avg = self.get_historical_average()
        
        if historical_avg is None:
            print(f"Insufficient historical data ({len(self.state['weekend_volumes'])} weekends), need at least 2")
            self.save_state(self.state)
            return
        
        print(f"Historical average ({self.historical_weeks} weeks): ${historical_avg:,.0f}")
        
        percentage_increase = ((current_volume - historical_avg) / historical_avg) * 100
        print(f"Volume change: {percentage_increase:+.1f}%")
        
        if self.should_alert(current_volume):
            self.send_alert(current_volume, historical_avg, percentage_increase)
        else:
            print(f"Volume within normal range (threshold: +{self.alert_threshold_percent}%)")
        
        # Save state after check
        self.save_state(self.state)
    
    def run_scheduled(self, check_times: List[str] = None) -> None:
        """
        Run scheduled weekend volume monitoring.
        
        Args:
            check_times (List[str]): List of times to check (format: "HH:MM")
                                   Defaults to ["09:00", "15:00", "21:00"]
        """
        if schedule is None:
            print("Error: 'schedule' package not available. Install with: pip install schedule")
            print("Falling back to simple weekend checking mode...")
            self._run_simple_weekend_check()
            return
            
        if check_times is None:
            check_times = ["09:00", "15:00", "21:00"]
        
        print(f"Starting weekend volume monitoring...")
        print(f"Historical period: {self.historical_weeks} weeks")
        print(f"Alert threshold: +{self.alert_threshold_percent}%")
        print(f"Top coins monitored: {self.top_n_coins}")
        print(f"Check times (weekends only): {', '.join(check_times)}")
        print(f"State file: {self.state_file}")
        print("-" * 50)
        
        # Schedule checks for weekends only
        for check_time in check_times:
            schedule.every().saturday.at(check_time).do(self.check_and_alert)
            schedule.every().sunday.at(check_time).do(self.check_and_alert)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for scheduled tasks
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Monitoring error: {e}")
            raise
    
    def _run_simple_weekend_check(self) -> None:
        """
        Simple weekend checking mode without scheduling (fallback when schedule is unavailable).
        """
        print("Running in simple weekend check mode...")
        print("This will check every hour and only act on weekends.")
        
        try:
            while True:
                self.check_and_alert()
                time.sleep(3600)  # Check every hour
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Monitoring error: {e}")
            raise


def main():
    """Main function with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Monitor weekend cryptocurrency market trading volume and alert on unusual activity'
    )
    
    parser.add_argument(
        '--historical-weeks', 
        type=int, 
        default=4,
        help='Number of weeks of historical data to maintain (default: 4)'
    )
    
    parser.add_argument(
        '--top-coins', 
        type=int, 
        default=100,
        help='Number of top coins by market cap to monitor (default: 100)'
    )
    
    parser.add_argument(
        '--threshold', 
        type=float, 
        default=10.0,
        help='Percentage threshold above average to trigger alert (default: 10.0)'
    )
    
    parser.add_argument(
        '--state-file', 
        type=str,
        help='Path to state persistence file (default: ../data/weekend_volume_state.json)'
    )
    
    parser.add_argument(
        '--check-times', 
        type=str, 
        nargs='+',
        default=["09:00", "15:00", "21:00"],
        help='Times to check volume on weekends (format: HH:MM, default: 09:00 15:00 21:00)'
    )
    
    parser.add_argument(
        '--single-check', 
        action='store_true',
        help='Perform single check instead of scheduled monitoring'
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
        print("This may be due to missing pandas dependency in the tools")
        sys.exit(1)
    
    # Create monitor instance
    monitor = WeekendVolumeMonitor(
        historical_weeks=args.historical_weeks,
        top_n_coins=args.top_coins,
        alert_threshold_percent=args.threshold,
        state_file=args.state_file
    )
    
    if args.single_check:
        # Perform single check
        monitor.check_and_alert()
    else:
        # Run scheduled monitoring
        monitor.run_scheduled(args.check_times)


if __name__ == '__main__':
    main()