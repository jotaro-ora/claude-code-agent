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
import argparse
import json

# Load environment variables from project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

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

if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It parses command-line arguments and calls get_top_gainers_losers with those arguments.
    # Example usage:
    #   python coins_gainers_losers.py
    #   python coins_gainers_losers.py --vs_currency eur --output_format json
    parser = argparse.ArgumentParser(description="Fetch top gainers and losers from CoinGecko API.")
    parser.add_argument('--vs_currency', type=str, default='usd', help='Target currency (default: usd)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')

    args = parser.parse_args()

    try:
        # Call the main function to fetch gainers and losers using the provided arguments
        result = get_top_gainers_losers(vs_currency=args.vs_currency)
        
        # Output in the specified format
        if args.output_format == 'json':
            output = {
                'gainers': result['gainers'].to_dict('records') if not result['gainers'].empty else [],
                'losers': result['losers'].to_dict('records') if not result['losers'].empty else []
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:  # csv
            print("=== TOP GAINERS ===")
            print(result['gainers'].to_csv(index=False))
            print("\n=== TOP LOSERS ===")
            print(result['losers'].to_csv(index=False))
            
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch gainers and losers: {e}") 