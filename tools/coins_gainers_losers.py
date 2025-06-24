"""
CoinGecko Top Gainers & Losers Tool

This tool provides access to the CoinGecko Pro API /coins/top_gainers_losers endpoint,
which returns the top gainers and losers in the market.

API Reference: https://docs.coingecko.com/reference/coins-top_gainers_losers

Usage Example:
    from tools.coins_gainers_losers import get_top_gainers_losers
    result = get_top_gainers_losers()
    print(result)

Returns:
    dict with keys: 'gainers' and 'losers', each is a pandas.DataFrame
"""

import requests
import pandas as pd
import os
from dotenv import load_dotenv
import time

load_dotenv()

def get_top_gainers_losers(vs_currency='usd'):
    """
    Fetch the top gainers and losers from CoinGecko.
    
    Args:
        vs_currency (str): The target currency (e.g., 'usd', 'eur')
    
    Returns:
        dict: {'gainers': DataFrame, 'losers': DataFrame}
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = "https://pro-api.coingecko.com/api/v3/coins/top_gainers_losers"
    headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
    params = {"vs_currency": vs_currency}
    for _ in range(3):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            gainers = pd.DataFrame(data.get('top_gainers', []))
            losers = pd.DataFrame(data.get('top_losers', []))
            return {'gainers': gainers, 'losers': losers}
        except Exception:
            time.sleep(1)
    raise ConnectionError("API request failed after retries") 