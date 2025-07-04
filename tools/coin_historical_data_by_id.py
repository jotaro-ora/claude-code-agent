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
import argparse
import json

# Load environment variables from project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

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

if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It parses command-line arguments and calls get_coin_historical_data_by_id with those arguments.
    # Example usage:
    #   python coin_historical_data_by_id.py --coin_id bitcoin --date 30-12-2017
    #   python coin_historical_data_by_id.py --coin_id ethereum --date 01-01-2020 --localization true
    parser = argparse.ArgumentParser(description="Fetch historical data for a specific coin from CoinGecko API.")
    parser.add_argument('--coin_id', type=str, required=True, help='Coin id, e.g., bitcoin')
    parser.add_argument('--date', type=str, required=True, help='Date in dd-mm-yyyy format, e.g., 30-12-2017')
    parser.add_argument('--localization', type=str, default='false', help="Include all localized languages ('true' or 'false', default: false)")

    args = parser.parse_args()

    try:
        # Call the main function to fetch historical data using the provided arguments
        data = get_coin_historical_data_by_id(
            coin_id=args.coin_id,
            date=args.date,
            localization=args.localization
        )
        
        # Print the result as pretty-formatted JSON
        print(json.dumps(data, ensure_ascii=False, indent=2))
            
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch historical data: {e}") 