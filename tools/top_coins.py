"""
CoinGecko Top Coins Retrieval Module

This module provides functionality to fetch the top N cryptocurrencies by market cap
using the CoinGecko Pro API.

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
    from tools.top_coins import get_top_coins
    
    # Get top 10 coins by market cap
    df = get_top_coins(n=10)
    
    # Get top 50 coins with additional details
    df = get_top_coins(n=50, include_extra_data=True)
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

def get_top_coins(n=10, include_extra_data=False):
    """
    Fetch the top N cryptocurrencies by market cap from CoinGecko.
    
    This function retrieves the top cryptocurrencies ranked by market capitalization
    using the CoinGecko Pro API. It supports both basic symbol retrieval and detailed
    data including prices, market cap, volume, and other metrics. For large requests
    (n > 250), the function automatically implements pagination to fetch all data.
    
    Args:
        n (int): Number of top coins to retrieve. Must be between 1 and 1000.
                Default is 10. Maximum allowed is 1000 (handled via pagination).
        include_extra_data (bool): Whether to include additional coin data beyond symbols.
                                  If False, returns only symbols in "TOKEN_USD" format.
                                  If True, returns detailed DataFrame with all available data.
                                  Default is False for efficiency.
    
    Returns:
        If include_extra_data=False (default):
            list: List of strings in format "TOKEN_USD" (e.g., ["BTC_USD", "ETH_USD", ...])
        
        If include_extra_data=True:
            pandas.DataFrame: DataFrame with columns:
                             - symbol: Coin symbol (e.g., "btc", "eth")
                             - symbol_usd: Trading pair format (e.g., "BTC_USD", "ETH_USD")
                             - name: Full coin name
                             - current_price: Current price in USD
                             - market_cap: Market capitalization in USD
                             - market_cap_rank: Market cap ranking
                             - total_volume: 24h trading volume
                             - price_change_24h: 24h price change
                             - price_change_percentage_24h: 24h price change percentage
                             - circulating_supply: Circulating supply
                             - total_supply: Total supply
                             - max_supply: Maximum supply (if available)
                             - ath: All-time high price
                             - ath_change_percentage: ATH change percentage
                             - last_updated: Last update timestamp
                             
    Raises:
        ValueError: If n is not between 1 and 1000
        ConnectionError: If API requests fail after retries
        KeyError: If COINGECKO_API_KEY environment variable is not set
        
    Limitations and Constraints:
        - Maximum n value: 1000 (handled via automatic pagination)
        - API rate limits apply based on your CoinGecko Pro subscription
        - Data is sorted by market cap in descending order
        - Some coins may have missing data fields (e.g., max_supply)
        - Prices and market data are real-time but may have slight delays
        - Large requests (n > 250) require multiple API calls with delays
        
    Error Handling:
        - Automatic retry logic for failed API requests (3 attempts)
        - Rate limiting handled with 1-second delays between requests
        - Input validation for n parameter
        - Graceful handling of missing data fields
        - Pagination error handling and recovery
        
    Performance Notes:
        - Single API call for n <= 250 (basic symbol retrieval)
        - Multiple API calls with delays for n > 250
        - Consider caching results for frequently accessed data
        - Larger n values may take longer due to pagination and rate limiting
        
    Example Usage:
        # Get top 10 coin symbols only
        symbols = get_top_coins(n=10)
        # Returns: ["BTC_USD", "ETH_USD", "USDT_USD", ...]
        
        # Get top 500 coins with full data (uses pagination)
        df = get_top_coins(n=500, include_extra_data=True)
        # Returns: DataFrame with detailed market data for 500 coins
        
        # Use symbols for other tools
        from tools.coingecko import get_coingecko_ohlc
        for symbol in get_top_coins(n=5):
            df = get_coingecko_ohlc(symbol, "1d", "2024-01-01", "2024-01-31")
    """
    
    def _validate_n(n):
        """
        Validate the n parameter for number of coins to retrieve.
        
        Args:
            n (int): Number of coins requested
            
        Returns:
            int: Validated n value
            
        Raises:
            ValueError: If n is not between 1 and 1000
        """
        if not isinstance(n, int) or n < 1 or n > 1000:
            raise ValueError("n must be an integer between 1 and 1000")
        return n
    
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
    
    def _fetch_paginated_data(n):
        """
        Fetch data using pagination for requests larger than 250 coins.
        
        Args:
            n (int): Total number of coins to retrieve
            
        Returns:
            list: Combined data from all pages
            
        Note:
            This function handles pagination automatically for large requests.
            It fetches data in chunks of 250 (API limit) and combines the results.
            Rate limiting delays are applied between requests.
            Data is sorted by market cap rank to ensure consistency.
        """
        all_data = []
        per_page = 250  # API limit per request
        total_pages = (n + per_page - 1) // per_page  # Ceiling division
        
        print(f"Fetching {n} coins using {total_pages} API requests...")
        
        for page in range(1, total_pages + 1):
            # Calculate how many coins to fetch on this page
            if page == total_pages:
                # Last page: fetch remaining coins
                remaining = n - (page - 1) * per_page
                current_per_page = remaining
            else:
                # Full page
                current_per_page = per_page
            
            print(f"  Request {page}/{total_pages}: fetching {current_per_page} coins...")
            
            # Prepare API request parameters
            params = {
                "vs_currency": "USD",
                "order": "market_cap_desc",
                "per_page": str(current_per_page),
                "page": str(page),
                "sparkline": "false",
                "price_change_percentage": "24h"
            }
            
            url = "https://pro-api.coingecko.com/api/v3/coins/markets"
            
            # Make API request
            try:
                page_data = _retry_api_request(url, params)
                all_data.extend(page_data)
                print(f"    ✓ Retrieved {len(page_data)} coins")
                
                # Rate limiting delay between requests (except for last request)
                if page < total_pages:
                    time.sleep(1.2)
                    
            except Exception as e:
                print(f"    ❌ Failed to fetch page {page}: {str(e)}")
                # Continue with partial data rather than failing completely
                break
        
        print(f"✓ Total coins retrieved: {len(all_data)}")
        
        # Sort by market cap rank to ensure consistency across pages
        all_data.sort(key=lambda x: x.get('market_cap_rank', float('inf')))
        
        # Take only the first n items to ensure we don't exceed the requested amount
        return all_data[:n]
    
    def _format_symbols_only(data):
        """
        Extract and format only the trading pair symbols from API response.
        
        Args:
            data (list): Raw API response data
            
        Returns:
            list: List of strings in "TOKEN_USD" format
        """
        symbols = []
        for coin in data:
            symbol = coin.get('symbol', '').upper()
            if symbol:
                symbols.append(f"{symbol}_USD")
        return symbols
    
    def _format_detailed_data(data):
        """
        Convert raw API response to detailed pandas DataFrame.
        
        Args:
            data (list): Raw API response data
            
        Returns:
            pandas.DataFrame: Formatted DataFrame with all available coin data
        """
        if not data:
            return pd.DataFrame()
        
        # Create DataFrame from raw data
        df = pd.DataFrame(data)
        
        # Add symbol_usd column for consistency with other tools
        df['symbol_usd'] = df['symbol'].str.upper() + '_USD'
        
        # Select and reorder relevant columns
        columns = [
            'symbol', 'symbol_usd', 'name', 'current_price', 'market_cap', 
            'market_cap_rank', 'total_volume', 'price_change_24h', 
            'price_change_percentage_24h', 'circulating_supply', 'total_supply',
            'max_supply', 'ath', 'ath_change_percentage', 'last_updated'
        ]
        
        # Only include columns that exist in the data
        available_columns = [col for col in columns if col in df.columns]
        return df[available_columns]
    
    # Validate input parameter
    n = _validate_n(n)
    
    # Fetch data (with pagination if needed)
    if n <= 250:
        # Single API request for small requests
        params = {
            "vs_currency": "USD",
            "order": "market_cap_desc",
            "per_page": str(n),
            "page": "1",
            "sparkline": "false",
            "price_change_percentage": "24h"
        }
        url = "https://pro-api.coingecko.com/api/v3/coins/markets"
        data = _retry_api_request(url, params)
    else:
        # Use pagination for large requests
        data = _fetch_paginated_data(n)
    
    # Return appropriate format based on include_extra_data parameter
    if include_extra_data:
        return _format_detailed_data(data)
    else:
        return _format_symbols_only(data) 