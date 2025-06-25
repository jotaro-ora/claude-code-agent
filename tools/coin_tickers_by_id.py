"""
CoinGecko Coin Tickers by ID Tool

This tool provides access to the CoinGecko Pro API /coins/{id}/tickers endpoint,
which returns tickers for a specific coin by its id.

API Reference: https://docs.coingecko.com/reference/coins-id-tickers

Usage Example:
    from tools.coin_tickers_by_id import get_coin_tickers_by_id
    df = get_coin_tickers_by_id('bitcoin')
    print(df.head())

Returns:
    pandas.DataFrame with tickers for the coin
"""

import requests
import pandas as pd
import os
from dotenv import load_dotenv
import time

# Load environment variables from project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

def get_coin_tickers_by_id(coin_id, exchange_ids=None, include_exchange_logo=False, page=1, order=None, depth=False):
    """
    Fetch tickers for a specific coin by its id from CoinGecko.
    
    Args:
        coin_id (str): The coin id (e.g., 'bitcoin')
        exchange_ids (str or None): Comma-separated list of exchange ids
        include_exchange_logo (bool): Whether to include exchange logos
        page (int): Page number
        order (str or None): Order results by
        depth (bool): Include order book depth data
    
    Returns:
        pandas.DataFrame: DataFrame with tickers for the coin
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/tickers"
    params = {
        'include_exchange_logo': str(include_exchange_logo).lower(),
        'page': page,
        'depth': str(depth).lower()
    }
    if exchange_ids:
        params['exchange_ids'] = exchange_ids
    if order:
        params['order'] = order
    headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
    for _ in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return pd.DataFrame(data.get('tickers', []))
        except Exception:
            time.sleep(1)
    raise ConnectionError("API request failed after retries") 