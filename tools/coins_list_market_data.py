"""
CoinGecko Coins List with Market Data Tool

This tool provides access to the CoinGecko Pro API /coins/markets endpoint,
which returns a list of coins with market data.

API Reference: https://docs.coingecko.com/reference/coins-markets

Usage Example:
    from tools.coins_list_market_data import get_coins_list_market_data
    df = get_coins_list_market_data(vs_currency='usd', per_page=10)
    print(df.head())

Returns:
    pandas.DataFrame with market data for coins
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

def get_coins_list_market_data(vs_currency='usd', order='market_cap_desc', per_page=100, page=1, sparkline=False, price_change_percentage=None):
    """
    Fetch a list of coins with market data from CoinGecko.
    
    Args:
        vs_currency (str): The target currency of market data (e.g., 'usd')
        order (str): Order results by (default: 'market_cap_desc')
        per_page (int): Number of results per page (max 250)
        page (int): Page number
        sparkline (bool): Include sparkline data
        price_change_percentage (str or None): Include price change percentage (e.g., '24h,7d')
    
    Returns:
        pandas.DataFrame: DataFrame with market data for coins
    
    Raises:
        ConnectionError: If API request fails after retries
    """
    url = "https://pro-api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': vs_currency,
        'order': order,
        'per_page': per_page,
        'page': page,
        'sparkline': str(sparkline).lower()
    }
    if price_change_percentage:
        params['price_change_percentage'] = price_change_percentage
    headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
    for _ in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return pd.DataFrame(data)
        except Exception:
            time.sleep(1)
    raise ConnectionError("API request failed after retries")

if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It parses command-line arguments and calls get_coins_list_market_data with those arguments.
    # Example usage:
    #   python coins_list_market_data.py --vs_currency usd --per_page 10
    #   python coins_list_market_data.py --vs_currency usd --order market_cap_desc --per_page 50 --output_format json
    parser = argparse.ArgumentParser(description="Fetch a list of coins with market data from CoinGecko API.")
    parser.add_argument('--vs_currency', type=str, default='usd', help='Target currency (default: usd)')
    parser.add_argument('--order', type=str, default='market_cap_desc', help='Order results by (default: market_cap_desc)')
    parser.add_argument('--per_page', type=int, default=100, help='Number of results per page (max 250, default: 100)')
    parser.add_argument('--page', type=int, default=1, help='Page number (default: 1)')
    parser.add_argument('--sparkline', action='store_true', help='Include sparkline data')
    parser.add_argument('--price_change_percentage', type=str, help='Include price change percentage (e.g., 24h,7d)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')

    args = parser.parse_args()

    try:
        # Call the main function to fetch market data using the provided arguments
        data = get_coins_list_market_data(
            vs_currency=args.vs_currency,
            order=args.order,
            per_page=args.per_page,
            page=args.page,
            sparkline=args.sparkline,
            price_change_percentage=args.price_change_percentage
        )
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data.to_dict('records'), ensure_ascii=False, indent=2))
        else:  # csv
            print(data.to_csv(index=False))
            
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch market data: {e}") 