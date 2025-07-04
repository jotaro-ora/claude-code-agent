"""
CoinGecko Coin OHLC Chart within Time Range by ID Tool

This tool provides access to the CoinGecko Pro API /coins/{id}/ohlc/range endpoint,
which returns OHLC chart data for a specific coin by its id within a time range.

API Reference: https://docs.coingecko.com/reference/coins-id-ohlc-range

Usage Example:
    from tools.coin_ohlc_range_by_id import get_coin_ohlc_range_by_id
    data = get_coin_ohlc_range_by_id('bitcoin', vs_currency='usd', from_timestamp, to_timestamp, interval='daily')
    print(data)

Returns:
    list of [timestamp, open, high, low, close]
"""

import requests
import os
from dotenv import load_dotenv
import time
import argparse
import json

# Load environment variables from project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

def get_coin_ohlc_range_by_id(coin_id, vs_currency='usd', from_timestamp=None, to_timestamp=None, interval=None):
    """
    Fetch OHLC chart data for a specific coin by its id within a time range from CoinGecko.
    
    Args:
        coin_id (str): The coin id (e.g., 'bitcoin')
        vs_currency (str): The target currency (e.g., 'usd')
        from_timestamp (int): From timestamp (UNIX, in seconds)
        to_timestamp (int): To timestamp (UNIX, in seconds)
        interval (str or None): Data interval (e.g., 'daily', 'hourly')
    
    Returns:
        list: List of [timestamp, open, high, low, close]
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/ohlc/range"
    params = {
        'vs_currency': vs_currency
    }
    if from_timestamp:
        params['from'] = from_timestamp
    if to_timestamp:
        params['to'] = to_timestamp
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch OHLC chart data within a time range for a specific coin from CoinGecko API.")
    parser.add_argument('--coin_id', type=str, required=True, help='Coin id, e.g., bitcoin')
    parser.add_argument('--vs_currency', type=str, default='usd', help='Target currency (default: usd)')
    parser.add_argument('--from_timestamp', type=int, help='From timestamp (UNIX, in seconds)')
    parser.add_argument('--to_timestamp', type=int, help='To timestamp (UNIX, in seconds)')
    parser.add_argument('--interval', type=str, help='Data interval (e.g., daily, hourly)')

    args = parser.parse_args()

    try:
        data = get_coin_ohlc_range_by_id(
            coin_id=args.coin_id,
            vs_currency=args.vs_currency,
            from_timestamp=args.from_timestamp,
            to_timestamp=args.to_timestamp,
            interval=args.interval
        )
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Failed to fetch OHLC range data: {e}") 