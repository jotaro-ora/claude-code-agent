"""
CoinGecko Coins List Tool

This tool provides access to the CoinGecko Pro API /coins/list endpoint,
which returns all supported coins with their id, symbol, and name.

API Reference: https://docs.coingecko.com/reference/coins-list

Usage Example:
    from tools.coins_list import get_coins_list
    coins = get_coins_list()
    print(coins.head())

Returns:
    pandas.DataFrame with columns: id, symbol, name
"""

import requests
import pandas as pd
import os
from dotenv import load_dotenv
import time

load_dotenv()

def get_coins_list(include_inactive=False):
    """
    Fetch the full list of coins supported by CoinGecko.
    
    Args:
        include_inactive (bool): If True, include inactive coins (default: False)
    
    Returns:
        pandas.DataFrame: DataFrame with columns: id, symbol, name
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = "https://pro-api.coingecko.com/api/v3/coins/list"
    params = {}
    if include_inactive:
        params['status'] = 'inactive'
    headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
    for _ in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return pd.DataFrame(data)[['id', 'symbol', 'name']]
        except Exception:
            time.sleep(1)
    raise ConnectionError("API request failed after retries") 