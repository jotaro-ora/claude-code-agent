"""
CoinGecko Coin Historical Data by ID Tool

This tool provides access to the CoinGecko Pro API /coins/{id}/history endpoint,
which returns historical data for a specific coin by its id and date.

API Reference: https://docs.coingecko.com/reference/coins-id-history

Usage Example:
    from tools.coin_historical_data_by_id import get_coin_historical_data_by_id
    data = get_coin_historical_data_by_id('bitcoin', '30-12-2017')
    print(data)

Returns:
    dict with historical coin data for the given date
"""

import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

def get_coin_historical_data_by_id(coin_id, date, localization='false'): 
    """
    Fetch historical data for a specific coin by its id and date from CoinGecko.
    
    Args:
        coin_id (str): The coin id (e.g., 'bitcoin')
        date (str): The date in dd-mm-yyyy format (e.g., '30-12-2017')
        localization (str): Include all localized languages in response ('true'/'false')
    
    Returns:
        dict: Historical coin data for the given date
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/history"
    params = {
        'date': date,
        'localization': localization
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