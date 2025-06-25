"""
CoinGecko Coin Historical Chart Data by ID Tool

This tool provides access to the CoinGecko Pro API /coins/{id}/market_chart endpoint,
which returns historical chart data for a specific coin by its id.

API Reference: https://docs.coingecko.com/reference/coins-id-market_chart

Usage Example:
    from tools.coin_historical_chart_by_id import get_coin_historical_chart_by_id
    data = get_coin_historical_chart_by_id('bitcoin', vs_currency='usd', days=30)
    print(data)

Returns:
    dict with keys: 'prices', 'market_caps', 'total_volumes'
"""

import requests
import os
from dotenv import load_dotenv
import time

# Load environment variables from project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

def get_coin_historical_chart_by_id(coin_id, vs_currency='usd', days=30, interval=None):
    """
    Fetch historical chart data for a specific coin by its id from CoinGecko.
    
    Args:
        coin_id (str): The coin id (e.g., 'bitcoin')
        vs_currency (str): The target currency (e.g., 'usd')
        days (int or str): Data up to number of days ago (e.g., 1, 14, 30, 'max')
        interval (str or None): Data interval (e.g., 'daily')
    
    Returns:
        dict: Historical chart data with keys: 'prices', 'market_caps', 'total_volumes'
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': vs_currency,
        'days': days
    }
    if interval:
        params['interval'] = interval
    headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
    for _ in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            time.sleep(1)
    raise ConnectionError("API request failed after retries") 