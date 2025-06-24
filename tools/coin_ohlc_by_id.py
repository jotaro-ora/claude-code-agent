"""
CoinGecko Coin OHLC Chart by ID Tool

This tool provides access to the CoinGecko Pro API /coins/{id}/ohlc endpoint,
which returns OHLC chart data for a specific coin by its id.

API Reference: https://docs.coingecko.com/reference/coins-id-ohlc

Usage Example:
    from tools.coin_ohlc_by_id import get_coin_ohlc_by_id
    data = get_coin_ohlc_by_id('bitcoin', vs_currency='usd', days=30)
    print(data)

Returns:
    list of [timestamp, open, high, low, close]
"""

import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

def get_coin_ohlc_by_id(coin_id, vs_currency='usd', days=30):
    """
    Fetch OHLC chart data for a specific coin by its id from CoinGecko.
    
    Args:
        coin_id (str): The coin id (e.g., 'bitcoin')
        vs_currency (str): The target currency (e.g., 'usd')
        days (int or str): Data up to number of days ago (e.g., 1, 14, 30, 'max')
    
    Returns:
        list: List of [timestamp, open, high, low, close]
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {
        'vs_currency': vs_currency,
        'days': days
    }
    headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
    for _ in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            time.sleep(1)
    raise ConnectionError("API request failed after retries") 