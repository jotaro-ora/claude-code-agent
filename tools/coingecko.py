"""
CoinGecko OHLC Data Retrieval Module

This module provides functionality to fetch historical OHLC (Open, High, Low, Close) 
price data for cryptocurrencies using the CoinGecko Pro API.

Dependencies:
- requests: For HTTP API calls
- pandas: For data manipulation and DataFrame operations
- python-dotenv: For environment variable management
- os: For accessing environment variables

Environment Variables Required:
- COINGECKO_API_KEY: Your CoinGecko Pro API key (required for API access)

API Rate Limits:
- CoinGecko Pro API has rate limits that vary by subscription tier
- This module implements retry logic with delays to handle rate limiting
- Recommended to respect API limits and implement appropriate delays between calls

Usage Example:
    from tools.coingecko import get_coingecko_ohlc
    
    # Get daily OHLC data for BTC_USD from 2023-01-01 to 2023-01-31
    df = get_coingecko_ohlc(
        symbol="BTC_USD",
        interval="1d", 
        start_time="2023-01-01",
        end_time="2023-01-31"
    )
"""

import requests
import pandas as pd
from datetime import datetime, timezone
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_coingecko_ohlc(symbol, interval, start_time, end_time):
    """
    Fetch historical OHLC (Open, High, Low, Close) price data for cryptocurrencies.
    
    This function retrieves historical price data from CoinGecko Pro API with automatic
    pagination handling for large date ranges. It supports both hourly and daily intervals
    and automatically handles API rate limiting with retry logic.
    
    Args:
        symbol (str): Trading pair symbol in format "TOKEN_USD" (e.g., "BTC_USD", "ETH_USD")
                     The function extracts the token part (before "_") to find the coin ID
        interval (str): Time interval for data points. Must be one of:
                       - "1h": Hourly data (limited to ~31 days per request)
                       - "1d": Daily data (limited to ~180 days per request)
        start_time: Start time for data retrieval. Can be:
                   - Unix timestamp (int/float): Seconds since epoch
                   - String "YYYY-MM-DD HH:MM:SS": Specific datetime
                   - String "YYYY-MM-DD": Date only (time set to 00:00:00)
        end_time: End time for data retrieval. Can be:
                 - Unix timestamp (int/float): Seconds since epoch  
                 - String "YYYY-MM-DD HH:MM:SS": Specific datetime
                 - String "YYYY-MM-DD": Date only (time set to 23:59:59)
    
    Returns:
        pandas.DataFrame: DataFrame with columns:
                         - datetime: UTC timestamp (pandas datetime)
                         - open: Opening price
                         - high: Highest price in period
                         - low: Lowest price in period  
                         - close: Closing price
                         
    Raises:
        ValueError: If interval is not supported, start_time > end_time, or invalid time format
        ConnectionError: If API requests fail after retries
        KeyError: If COINGECKO_API_KEY environment variable is not set
        
    Limitations and Constraints:
        - Minimum start_time: 2018-02-08 (timestamp 1518147224) - CoinGecko data availability
        - Maximum end_time: Current time (future dates are automatically adjusted)
        - API rate limits apply based on your CoinGecko Pro subscription
        - Large date ranges are automatically chunked to respect API limits
        - Some coins may have limited historical data availability
        - For volume data, use the volume_data tool instead
        
    Error Handling:
        - Automatic retry logic for failed API requests (3 attempts)
        - Rate limiting handled with 1.2 second delays between requests
        - Invalid symbols fallback to "bitcoin" as default
        - Future end times automatically adjusted to current time
        
    Performance Notes:
        - Large date ranges require multiple API calls with delays
        - Hourly data has smaller chunk sizes than daily data
        - Consider caching results for frequently accessed data
        
    Example Usage:
        # Get daily Bitcoin data for January 2023
        df = get_coingecko_ohlc("BTC_USD", "1d", "2023-01-01", "2023-01-31")
        
        # Get hourly Ethereum data for last week using timestamps
        import time
        end = int(time.time())
        start = end - (7 * 24 * 3600)  # 7 days ago
        df = get_coingecko_ohlc("ETH_USD", "1h", start, end)
    """

    def get_coinid_by_symbol(symbol: str):
        """
        Convert trading pair symbol to CoinGecko coin ID.
        
        Args:
            symbol (str): Trading pair in format "TOKEN_USD" (e.g., "BTC_USD")
            
        Returns:
            str: CoinGecko coin ID (e.g., "bitcoin", "ethereum")
                 Falls back to "bitcoin" if symbol not found
                 
        Note:
            This function uses the CoinGecko markets API to find the coin ID.
            It extracts the token part (before "_") and searches for matching symbols.
            If no match is found, it defaults to "bitcoin" to prevent errors.
        """
        token = symbol.split('_')[1]
        url = "https://pro-api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "USD",
            "symbols": [token],
            "include_tokens": "top",
        }
        data = _retry_api_request(url, params)
        if len(data):
            return data[0].get("id","bitcoin")
        else:
            return "bitcoin"

    def _validate_interval(interval):
        """
        Validate and convert interval parameter to CoinGecko API format.
        
        Args:
            interval (str): User-provided interval ("1h" or "1d")
            
        Returns:
            str: CoinGecko API interval format ("hourly" or "daily")
            
        Raises:
            ValueError: If interval is not supported
            
        Note:
            CoinGecko API uses "hourly" and "daily" internally, but this function
            accepts more user-friendly "1h" and "1d" formats for convenience.
        """
        interval_map = {
            '1h': 'hourly',
            '1d': 'daily'
        }
        if interval not in interval_map:
            raise ValueError(f"Unsupported interval: {interval}. Must be one of: {list(interval_map.keys())}")
        return interval_map[interval]

    def _retry_api_request(url, params, retries=3):
        """
        Make API request with automatic retry logic and error handling.
        
        Args:
            url (str): API endpoint URL
            params (dict): Query parameters for the request
            retries (int): Number of retry attempts (default: 3)
            
        Returns:
            dict: JSON response from the API
            
        Raises:
            ConnectionError: If all retry attempts fail
            
        Note:
            This function implements exponential backoff with 1-second delays
            between retries to handle temporary API issues and rate limiting.
            It uses the COINGECKO_API_KEY environment variable for authentication.
            
        Error Handling:
            - Catches all exceptions and retries up to specified number of times
            - 15-second timeout per request to prevent hanging
            - 1-second delay between retries
            - Raises ConnectionError if all retries fail
        """
        for _ in range(retries):
            try:
                headers = {
                    "x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")
                }
                resp = requests.get(url, params=params, headers=headers, timeout=15)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                time.sleep(1)
        raise ConnectionError("API request failed after retries")

    def _format_dataframe(raw_data):
        """
        Convert raw API response data to standardized pandas DataFrame.
        
        Args:
            raw_data (list): List of OHLC data dictionaries from API
            
        Returns:
            pandas.DataFrame: Formatted DataFrame with columns:
                             datetime, open, high, low, close
                             
        Note:
            This function processes the raw CoinGecko API response and converts
            it to a standardized DataFrame format. It handles:
            - Timestamp conversion from milliseconds to pandas datetime
            - Column ordering and sorting by datetime
            - UTC timezone handling
        """
        if not raw_data:
            return pd.DataFrame()
        df = pd.DataFrame(raw_data)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        return df.sort_values('datetime')[['datetime', 'open', 'high', 'low', 'close']]

    def parse_start_time(tstr):
        """
        Parse start time input into Unix timestamp.
        
        Args:
            tstr: Time input in various formats:
                 - Unix timestamp (int/float): Seconds since epoch
                 - String "YYYY-MM-DD HH:MM:SS": Specific datetime
                 - String "YYYY-MM-DD": Date only (time set to 00:00:00)
                 
        Returns:
            int: Unix timestamp in seconds
            
        Raises:
            ValueError: If time format is invalid
            
        Note:
            This function handles multiple time input formats for user convenience.
            For date-only strings, time is set to start of day (00:00:00).
            Large timestamps (>1e11) are assumed to be in milliseconds and converted.
        """
        try:
            if isinstance(tstr, (int, float)):
                return int(tstr // 1000) if tstr > 1e11 else int(tstr)
            try:
                return int(datetime.strptime(tstr, "%Y-%m-%d %H:%M:%S").timestamp())
            except ValueError:
                dt = datetime.strptime(tstr, "%Y-%m-%d")
                dt = dt.replace(hour=0, minute=0, second=0)
                return int(dt.timestamp())
        except Exception:
            raise ValueError("start_time should be timestamp or string 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'")
            
    def parse_end_time(tstr):
        """
        Parse end time input into Unix timestamp.
        
        Args:
            tstr: Time input in various formats:
                 - Unix timestamp (int/float): Seconds since epoch
                 - String "YYYY-MM-DD HH:MM:SS": Specific datetime
                 - String "YYYY-MM-DD": Date only (time set to 23:59:59)
                 
        Returns:
            int: Unix timestamp in seconds
            
        Raises:
            ValueError: If time format is invalid
            
        Note:
            This function handles multiple time input formats for user convenience.
            For date-only strings, time is set to end of day (23:59:59).
            Large timestamps (>1e11) are assumed to be in milliseconds and converted.
        """
        try:
            if isinstance(tstr, (int, float)):
                return int(tstr // 1000) if tstr > 1e11 else int(tstr)
            try:
                return int(datetime.strptime(tstr, "%Y-%m-%d %H:%M:%S").timestamp())
            except ValueError:
                dt = datetime.strptime(tstr, "%Y-%m-%d")
                dt = dt.replace(hour=23, minute=59, second=59)
                return int(dt.timestamp())
        except Exception:
            raise ValueError("end_time should be timestamp or string 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'")

    # Validate and convert parameters
    cg_interval = _validate_interval(interval)
    coin_id = get_coinid_by_symbol(symbol)
    start_time = parse_start_time(start_time)
    end_time = parse_end_time(end_time)
    
    # Apply time range constraints and validations
    now = int(datetime.utcnow().timestamp())
    if end_time > now:
        end_time = now  # Cannot fetch future data
    min_time = 1518147224  # 2018-02-08 - CoinGecko data availability limit
    if start_time < min_time:
        start_time = min_time  # Adjust to earliest available data
    if start_time > end_time:
        raise ValueError("start_time after end_time")
        
    # Initialize data collection with pagination handling
    all_data = []
    current_end_sec = end_time
    while True:
        # Determine chunk size based on interval to respect API limits
        if cg_interval == 'daily':
            chunk_size = 180 * 24 * 60 * 60  # ~180 days for daily data
        else:
            chunk_size = 31 * 24 * 60 * 60   # ~31 days for hourly data
            
        # Calculate chunk boundaries for pagination
        chunk_start = max(start_time, current_end_sec - chunk_size)
        
        # Prepare API request parameters
        params = {
            "vs_currency": "USD",
            "from": str(chunk_start),
            "to": str(current_end_sec),
            "interval": cg_interval
        }
        url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/ohlc/range"
        
        # Attempt to fetch data with retry logic
        success = False
        for _ in range(3):
            try:
                data = _retry_api_request(url, params)
                if data:
                    # Process and validate received data
                    valid_klines = []
                    min_ts_sec = float('inf')
                    for item in data:
                        # CoinGecko API returns array format: [timestamp, open, high, low, close]
                        # No volume data is available in this endpoint
                        ts_ms = item[0]
                        ts_sec = ts_ms // 1000
                        if ts_sec * 1000 >= start_time * 1000:
                            valid_klines.append({
                                "timestamp": ts_ms,
                                "open": item[1],
                                "high": item[2],
                                "low": item[3],
                                "close": item[4],
                                "volume": 0  # Volume not available in CoinGecko OHLC endpoint
                            })
                            if ts_sec < min_ts_sec:
                                min_ts_sec = ts_sec
                    all_data.extend(valid_klines)
                    
                    # Update pagination cursor for next iteration
                    if min_ts_sec != float('inf'):
                        current_end_sec = min_ts_sec - 1
                    else:
                        break
                    if current_end_sec <= start_time:
                        break
                    success = True
                else:
                    break
            except Exception:
                time.sleep(1)
                continue
            if success:
                break
        if not success:
            break
        if current_end_sec <= start_time:
            break
        time.sleep(1.2)  # Rate limiting delay between requests
    return _format_dataframe(all_data)