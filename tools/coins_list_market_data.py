"""
CoinGecko Coins List with Market Data Tool

This tool provides access to the CoinGecko Pro API /coins/markets endpoint,
which returns a list of coins with market data.

API Reference: https://docs.coingecko.com/reference/coins-markets

Usage Example:
    from tools.coins_list_market_data import get_coins_list_market_data
    df = get_coins_list_market_data(vs_currency='usd', per_page=10)
    print(df.head())

Returns:
    pandas.DataFrame with market data for coins
"""

import requests
import pandas as pd
import os
from dotenv import load_dotenv
import time

# Load environment variables from project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

def get_coins_list_market_data(vs_currency='usd', order='market_cap_desc', per_page=100, page=1, sparkline=False, price_change_percentage=None):
    """
    Fetch a list of coins with market data from CoinGecko.
    
    Args:
        vs_currency (str): The target currency of market data (e.g., 'usd')
        order (str): Order results by (default: 'market_cap_desc')
        per_page (int): Number of results per page (max 250)
        page (int): Page number
        sparkline (bool): Include sparkline data
        price_change_percentage (str or None): Include price change percentage (e.g., '24h,7d')
    
    Returns:
        pandas.DataFrame: DataFrame with market data for coins
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = "https://pro-api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': vs_currency,
        'order': order,
        'per_page': per_page,
        'page': page,
        'sparkline': str(sparkline).lower()
    }
    if price_change_percentage:
        params['price_change_percentage'] = price_change_percentage
    headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
    for _ in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return pd.DataFrame(data)
        except Exception:
            time.sleep(1)
    raise ConnectionError("API request failed after retries") 