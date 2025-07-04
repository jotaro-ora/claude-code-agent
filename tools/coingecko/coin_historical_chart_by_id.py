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
import argparse
import json

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

if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It parses command-line arguments and calls get_coin_historical_chart_by_id with those arguments.
    # Example usage:
    #   python coin_historical_chart_by_id.py --coin_id bitcoin --days 30
    #   python coin_historical_chart_by_id.py --coin_id ethereum --vs_currency usd --days 7 --interval daily
    parser = argparse.ArgumentParser(description="Fetch historical chart data for a specific coin from CoinGecko API.")
    parser.add_argument('--coin_id', type=str, required=True, help='Coin id, e.g., bitcoin')
    parser.add_argument('--vs_currency', type=str, default='usd', help='Target currency (default: usd)')
    parser.add_argument('--days', type=str, default='30', help='Data up to number of days ago (e.g., 1, 14, 30, max)')
    parser.add_argument('--interval', type=str, help='Data interval (e.g., daily)')

    args = parser.parse_args()

    try:
        # Call the main function to fetch historical chart data using the provided arguments
        data = get_coin_historical_chart_by_id(
            coin_id=args.coin_id,
            vs_currency=args.vs_currency,
            days=args.days,
            interval=args.interval
        )
        
        # Print the result as pretty-formatted JSON
        print(json.dumps(data, ensure_ascii=False, indent=2))
            
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch historical chart data: {e}") 