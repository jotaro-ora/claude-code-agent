"""
CoinGecko Coins List Tool

This tool provides access to the CoinGecko Pro API /coins/list endpoint,
which returns all supported coins with their id, symbol, and name.

API Reference: https://docs.coingecko.com/reference/coins-list

Usage Example:
    from tools.coins_list import get_coins_list
    coins = get_coins_list()
    print(coins.head())

Returns:
    pandas.DataFrame with columns: id, symbol, name
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

def get_coins_list(include_inactive=False):
    """
    Fetch the full list of coins supported by CoinGecko.
    
    Args:
        include_inactive (bool): If True, include inactive coins (default: False)
    
    Returns:
        pandas.DataFrame: DataFrame with columns: id, symbol, name
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = "https://pro-api.coingecko.com/api/v3/coins/list"
    params = {}
    if include_inactive:
        params['status'] = 'inactive'
    headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
    for _ in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return pd.DataFrame(data)[['id', 'symbol', 'name']]
        except Exception:
            time.sleep(1)
    raise ConnectionError("API request failed after retries")

if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It parses command-line arguments and calls get_coins_list with those arguments.
    # Example usage:
    #   python coins_list.py --include_inactive
    #   python coins_list.py --include_inactive --output_format json
    parser = argparse.ArgumentParser(description="Fetch the full list of coins supported by CoinGecko API.")
    parser.add_argument('--include_inactive', action='store_true', help='Include inactive coins in the results')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    parser.add_argument('--limit', type=int, help='Limit the number of results (optional)')

    args = parser.parse_args()

    try:
        # Call the main function to fetch coins list using the provided arguments
        data = get_coins_list(include_inactive=args.include_inactive)
        
        # Apply limit if specified
        if args.limit:
            data = data.head(args.limit)
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data.to_dict('records'), ensure_ascii=False, indent=2))
        else:  # csv
            print(data.to_csv(index=False))
            
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch coins list: {e}") 