"""
CoinGecko Coin Historical Chart Data within Time Range by ID Tool

This tool provides access to the CoinGecko Pro API /coins/{id}/market_chart/range endpoint,
which returns historical chart data for a specific coin by its id within a time range.

API Reference: https://docs.coingecko.com/reference/coins-id-market_chart-range

Usage Example:
    from tools.coin_historical_chart_range_by_id import get_coin_historical_chart_range_by_id
    data = get_coin_historical_chart_range_by_id('bitcoin', vs_currency='usd', from_timestamp, to_timestamp)
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

def get_coin_historical_chart_range_by_id(coin_id, vs_currency='usd', from_timestamp=None, to_timestamp=None):
    """
    Fetch historical chart data for a specific coin by its id within a time range from CoinGecko.
    
    Args:
        coin_id (str): The coin id (e.g., 'bitcoin')
        vs_currency (str): The target currency (e.g., 'usd')
        from_timestamp (int): From timestamp (UNIX, in seconds)
        to_timestamp (int): To timestamp (UNIX, in seconds)
    
    Returns:
        dict: Historical chart data with keys: 'prices', 'market_caps', 'total_volumes'
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    params = {
        'vs_currency': vs_currency
    }
    if from_timestamp:
        params['from'] = from_timestamp
    if to_timestamp:
        params['to'] = to_timestamp
    headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
    for _ in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            time.sleep(1)
    raise ConnectionError("API request failed after retries") 