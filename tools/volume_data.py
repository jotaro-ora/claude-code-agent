"""
CoinGecko Volume Data Retrieval Module

This module provides functionality to fetch trading volume data for cryptocurrencies
using the CoinGecko Pro API. It can work with both individual symbols and lists of symbols
from the top_coins tool.

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
    from tools.volume_data import get_volume_data
    from tools.top_coins import get_top_coins
    
    # Get volume data for specific symbols
    volume_df = get_volume_data(["BTC_USD", "ETH_USD"])
    
    # Get volume data for top 10 coins
    top_symbols = get_top_coins(n=10)
    volume_df = get_volume_data(top_symbols)
"""

import requests
import pandas as pd
import os
import time
from datetime import datetime
from typing import List, Optional, Union
from dotenv import load_dotenv

# Load environment variables from project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

def get_volume_data(symbols, include_extra_data=False):
    """
    Fetch trading volume data for cryptocurrencies from CoinGecko.
    
    This function retrieves trading volume data for specified cryptocurrency symbols
    using the CoinGecko Pro API. It supports both single symbol and multiple symbols,
    and can return either basic volume data or detailed market information.
    
    Args:
        symbols: Can be:
                - str: Single symbol in "TOKEN_USD" format (e.g., "BTC_USD")
                - list: List of symbols in "TOKEN_USD" format (e.g., ["BTC_USD", "ETH_USD"])
        include_extra_data (bool): Whether to include additional market data beyond volume.
                                  If False, returns only volume-related data.
                                  If True, returns detailed DataFrame with all available data.
                                  Default is False for efficiency.
    
    Returns:
        pandas.DataFrame: DataFrame with columns:
                         - symbol: Coin symbol (e.g., "btc", "eth")
                         - symbol_usd: Trading pair format (e.g., "BTC_USD", "ETH_USD")
                         - name: Full coin name
                         - total_volume: 24h trading volume in USD
                         - volume_change_24h: 24h volume change
                         - volume_change_percentage_24h: 24h volume change percentage
                         
                         If include_extra_data=True, also includes:
                         - current_price: Current price in USD
                         - market_cap: Market capitalization in USD
                         - market_cap_rank: Market cap ranking
                         - price_change_24h: 24h price change
                         - price_change_percentage_24h: 24h price change percentage
                         - circulating_supply: Circulating supply
                         - total_supply: Total supply
                         - max_supply: Maximum supply (if available)
                         - ath: All-time high price
                         - ath_change_percentage: ATH change percentage
                         - last_updated: Last update timestamp
                         
    Raises:
        ValueError: If symbols format is invalid or empty
        ConnectionError: If API requests fail after retries
        KeyError: If COINGECKO_API_KEY environment variable is not set
        
    Limitations and Constraints:
        - Maximum 250 symbols per API request (handled automatically)
        - API rate limits apply based on your CoinGecko Pro subscription
        - Some coins may have missing volume data
        - Volume data is real-time but may have slight delays
        - Large symbol lists require multiple API calls with delays
        
    Error Handling:
        - Automatic retry logic for failed API requests (3 attempts)
        - Rate limiting handled with 1-second delays between requests
        - Input validation for symbols parameter
        - Graceful handling of missing data fields
        - Batch processing for large symbol lists
        
    Performance Notes:
        - Single API call for small symbol lists
        - Multiple API calls with delays for large symbol lists
        - Consider caching results for frequently accessed data
        - Larger symbol lists may take longer due to rate limiting
        
    Example Usage:
        # Get volume data for specific symbols
        volume_df = get_volume_data(["BTC_USD", "ETH_USD"])
        
        # Get volume data for top 50 coins
        from tools.top_coins import get_top_coins
        top_symbols = get_top_coins(n=50)
        volume_df = get_volume_data(top_symbols)
        
        # Get detailed volume data
        detailed_df = get_volume_data(["BTC_USD"], include_extra_data=True)
        
        # Use with coingecko OHLC tool
        from tools.coingecko import get_coingecko_ohlc
        for symbol in volume_df['symbol_usd']:
            ohlc_df = get_coingecko_ohlc(symbol, "1d", "2024-01-01", "2024-01-31")
    """
    
    def _validate_symbols(symbols):
        """
        Validate and normalize the symbols parameter.
        
        Args:
            symbols: Input symbols (str or list)
            
        Returns:
            list: Normalized list of symbols
            
        Raises:
            ValueError: If symbols format is invalid
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        if not isinstance(symbols, list) or len(symbols) == 0:
            raise ValueError("symbols must be a non-empty string or list of strings")
        
        # Validate symbol format
        for symbol in symbols:
            if not isinstance(symbol, str) or not symbol.endswith('_USD'):
                raise ValueError(f"Invalid symbol format: {symbol}. Must be in 'TOKEN_USD' format")
            
            # Additional validation for common invalid symbols
            token_part = symbol.replace('_USD', '').upper()
            if not token_part or len(token_part) < 1:
                raise ValueError(f"Invalid symbol format: {symbol}. Token part cannot be empty")
        
        return symbols
    
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
            This function implements retry logic with 1-second delays
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
    
    def _fetch_volume_data_batch(symbols_batch):
        """
        Fetch volume data for a batch of symbols.
        
        Args:
            symbols_batch (list): List of symbols to fetch data for
            
        Returns:
            list: Raw API response data for the batch
        """
        # Extract token symbols (remove _USD suffix)
        token_symbols = [symbol.replace('_USD', '').lower() for symbol in symbols_batch]
        
        # Prepare API request parameters
        params = {
            "vs_currency": "USD",
            "symbols": ','.join(token_symbols),
            "order": "market_cap_desc",
            "per_page": "250",  # Use maximum per page to ensure we get all symbols
            "page": "1",
            "sparkline": "false",
            "price_change_percentage": "24h"
        }
        
        url = "https://pro-api.coingecko.com/api/v3/coins/markets"
        
        # Make API request
        data = _retry_api_request(url, params)
        
        # Filter data to only include requested symbols
        filtered_data = []
        requested_symbols_set = set(token_symbols)
        
        for item in data:
            if item.get('symbol', '').lower() in requested_symbols_set:
                filtered_data.append(item)
        
        return filtered_data
    
    def _fetch_volume_data_large_list(symbols):
        """
        Fetch volume data for large symbol lists using batching.
        
        Args:
            symbols (list): List of symbols to fetch data for
            
        Returns:
            list: Combined data from all batches
        """
        all_data = []
        batch_size = 250  # API limit per request
        total_batches = (len(symbols) + batch_size - 1) // batch_size
        
        print(f"Fetching volume data for {len(symbols)} symbols using {total_batches} API requests...")
        
        for i in range(0, len(symbols), batch_size):
            batch_num = (i // batch_size) + 1
            batch_symbols = symbols[i:i + batch_size]
            
            print(f"  Request {batch_num}/{total_batches}: fetching data for {len(batch_symbols)} symbols...")
            
            try:
                batch_data = _fetch_volume_data_batch(batch_symbols)
                all_data.extend(batch_data)
                print(f"    ✓ Retrieved data for {len(batch_data)} symbols")
                
                # Rate limiting delay between requests (except for last request)
                if batch_num < total_batches:
                    time.sleep(1.2)
                    
            except Exception as e:
                print(f"    ❌ Failed to fetch batch {batch_num}: {str(e)}")
                # Continue with partial data rather than failing completely
                continue
        
        print(f"✓ Total symbols processed: {len(all_data)}")
        return all_data
    
    def _format_volume_data(data, include_extra_data=False):
        """
        Convert raw API response to formatted DataFrame.
        
        Args:
            data (list): Raw API response data
            include_extra_data (bool): Whether to include extra market data
            
        Returns:
            pandas.DataFrame: Formatted DataFrame
        """
        if not data:
            return pd.DataFrame()
        
        # Create DataFrame from raw data
        df = pd.DataFrame(data)
        
        # Add symbol_usd column for consistency with other tools
        df['symbol_usd'] = df['symbol'].str.upper() + '_USD'
        
        if include_extra_data:
            # Include all available columns
            columns = [
                'symbol', 'symbol_usd', 'name', 'current_price', 'market_cap', 
                'market_cap_rank', 'total_volume', 'volume_change_24h',
                'volume_change_percentage_24h', 'price_change_24h', 
                'price_change_percentage_24h', 'circulating_supply', 'total_supply',
                'max_supply', 'ath', 'ath_change_percentage', 'last_updated'
            ]
        else:
            # Include only volume-related columns
            columns = [
                'symbol', 'symbol_usd', 'name', 'total_volume', 
                'volume_change_24h', 'volume_change_percentage_24h'
            ]
        
        # Only include columns that exist in the data
        available_columns = [col for col in columns if col in df.columns]
        return df[available_columns]
    
    # Validate and normalize input
    symbols = _validate_symbols(symbols)
    
    # Fetch data (with batching if needed)
    if len(symbols) <= 250:
        # Single API request for small lists
        data = _fetch_volume_data_batch(symbols)
    else:
        # Use batching for large lists
        data = _fetch_volume_data_large_list(symbols)
    
    # Format and return data
    return _format_volume_data(data, include_extra_data) 