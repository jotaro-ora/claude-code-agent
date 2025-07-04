"""
CoinGlass Taker Buy/Sell Exchange Ratio API Tool

This module provides functionality to fetch exchange taker buy/sell ratio data
from the CoinGlass API.

Dependencies:
- requests: For HTTP API calls

Environment Variables Required:
- COINGLASS_API_KEY: Your CoinGlass API key (required for API access)

Usage Example:
    from tools.coinglass.taker_buy_sell_exchange_ratio import get_taker_buy_sell_exchange_ratio
    
    # Get exchange taker buy/sell ratio for Bitcoin
    data = get_taker_buy_sell_exchange_ratio(symbol="BTC")
"""

import requests
import os
import time
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Load environment variables from project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
env_path = os.path.join(project_root, '.env')

# Load .env file manually if python-dotenv is not available
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

def get_taker_buy_sell_exchange_ratio(symbol="BTC", time_range="4h"):
    """
    Fetch exchange taker buy/sell ratio from CoinGlass API.
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., "BTC", "ETH")
        time_range (str): Time range (e.g., "4h", "24h", "7d")
    
    Returns:
        dict: Dictionary containing aggregated taker buy/sell ratio data and exchange breakdown
        
    Raises:
        EnvironmentError: If COINGLASS_API_KEY is not found in environment variables
        ConnectionError: If API request fails after retries
        
    Example:
        data = get_taker_buy_sell_exchange_ratio("BTC", "4h")
        print(data[:5])  # Show first 5 exchange taker buy/sell ratio records
    """
    # Validate API key
    api_key = os.getenv("COINGLASS_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "COINGLASS_API_KEY not found. "
            "Please add it to your .env file in the project root."
        )
    
    # Prepare API request
    url = "https://open-api-v4.coinglass.com/api/futures/taker-buy-sell-volume/exchange-list"
    headers = {"CG-API-KEY": api_key}
    
    # Prepare parameters
    params = {
        "symbol": symbol,
        "range": time_range
    }
    
    # Make API request with retry logic
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if API response is successful
            if (data.get("code") == 0 or data.get("code") == "0") and "data" in data:
                # Return the data directly as it's already in dict format
                return data["data"]
            else:
                raise ConnectionError(f"API error: {data.get('msg', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            if attempt == 2:  # Last attempt
                raise ConnectionError(f"Failed to fetch data after 3 attempts: {str(e)}")
            time.sleep(1)  # Wait before retry
    
    return {}  # Return empty dict if all attempts fail


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches exchange taker buy/sell ratio from CoinGlass API.
    # Example usage:
    #   python taker_buy_sell_exchange_ratio.py --symbol BTC --time_range 4h
    #   python taker_buy_sell_exchange_ratio.py --symbol ETH --time_range 24h --output_format json
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Fetch exchange taker buy/sell ratio from CoinGlass API")
    parser.add_argument('--symbol', type=str, default='BTC', help='Cryptocurrency symbol (default: BTC)')
    parser.add_argument('--time_range', type=str, default='4h', help='Time range (default: 4h)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Call the main function to fetch data
        data = get_taker_buy_sell_exchange_ratio(symbol=args.symbol, time_range=args.time_range)
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:  # csv
            # Convert dict to CSV format
            if data:
                import csv
                import io
                output = io.StringIO()
                
                # Handle nested structure for CSV output
                rows = []
                if isinstance(data, dict):
                    # Flatten the structure for CSV
                    for key, value in data.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                rows.append({"category": key, "field": sub_key, "value": sub_value})
                        else:
                            rows.append({"category": "main", "field": key, "value": value})
                
                if rows:
                    writer = csv.DictWriter(output, fieldnames=["category", "field", "value"])
                    writer.writeheader()
                    writer.writerows(rows)
                    print(output.getvalue())
                else:
                    print("No data available")
            else:
                print("No data available")
                
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch data: {e}")