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
import argparse
import json

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

if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It parses command-line arguments and calls get_coin_tickers_by_id with those arguments.
    # Example usage:
    #   python coin_tickers_by_id.py --coin_id bitcoin
    #   python coin_tickers_by_id.py --coin_id ethereum --include_exchange_logo --output_format json
    parser = argparse.ArgumentParser(description="Fetch tickers for a specific coin from CoinGecko API.")
    parser.add_argument('--coin_id', type=str, required=True, help='Coin id, e.g., bitcoin')
    parser.add_argument('--exchange_ids', type=str, help='Comma-separated list of exchange ids')
    parser.add_argument('--include_exchange_logo', action='store_true', help='Include exchange logos')
    parser.add_argument('--page', type=int, default=1, help='Page number (default: 1)')
    parser.add_argument('--order', type=str, help='Order results by')
    parser.add_argument('--depth', action='store_true', help='Include order book depth data')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')

    args = parser.parse_args()

    try:
        # Call the main function to fetch coin tickers using the provided arguments
        data = get_coin_tickers_by_id(
            coin_id=args.coin_id,
            exchange_ids=args.exchange_ids,
            include_exchange_logo=args.include_exchange_logo,
            page=args.page,
            order=args.order,
            depth=args.depth
        )
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data.to_dict('records'), ensure_ascii=False, indent=2))
        else:  # csv
            print(data.to_csv(index=False))
            
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch coin tickers: {e}") 