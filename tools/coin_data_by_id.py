"""
CoinGecko Coin Data by ID Tool

This tool provides access to the CoinGecko Pro API /coins/{id} endpoint,
which returns detailed data for a specific coin by its id.

API Reference: https://docs.coingecko.com/reference/coins-id

Usage Example:
    from tools.coin_data_by_id import get_coin_data_by_id
    data = get_coin_data_by_id('bitcoin')
    print(data)

Returns:
    dict with detailed coin data
"""

import requests
import os
from dotenv import load_dotenv
import time

# Load environment variables from project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

def get_coin_data_by_id(coin_id, localization='false', tickers='true', market_data='true', community_data='true', developer_data='true', sparkline='false'):
    """
    Fetch detailed data for a specific coin by its id from CoinGecko.
    
    Args:
        coin_id (str): The coin id (e.g., 'bitcoin')
        localization (str): Include all localized languages in response ('true'/'false')
        tickers (str): Include tickers data ('true'/'false')
        market_data (str): Include market data ('true'/'false')
        community_data (str): Include community data ('true'/'false')
        developer_data (str): Include developer data ('true'/'false')
        sparkline (str): Include sparkline data ('true'/'false')
    
    Returns:
        dict: Detailed coin data
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}"
    params = {
        'localization': localization,
        'tickers': tickers,
        'market_data': market_data,
        'community_data': community_data,
        'developer_data': developer_data,
        'sparkline': sparkline
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