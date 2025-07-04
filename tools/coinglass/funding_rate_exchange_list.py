"""
CoinGlass Funding Rate Exchange List API Tool

This module provides functionality to fetch funding rate by exchange list data
from the CoinGlass API.

Dependencies:
- requests: For HTTP API calls

Environment Variables Required:
- COINGLASS_API_KEY: Your CoinGlass API key (required for API access)

Usage Example:
    from tools.coinglass.funding_rate_exchange_list import get_funding_rate_exchange_list
    
    # Get funding rate by exchange list for Bitcoin
    data = get_funding_rate_exchange_list(symbol="BTC")
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

def get_funding_rate_exchange_list(symbol="BTC"):
    """
    Fetch funding rate by exchange list from CoinGlass API.
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., "BTC", "ETH")
    
    Returns:
        list or pandas.DataFrame: List of dictionaries or DataFrame containing funding rate by exchange data
        
    Raises:
        EnvironmentError: If COINGLASS_API_KEY is not found in environment variables
        ConnectionError: If API request fails after retries
        
    Example:
        data = get_funding_rate_exchange_list("BTC")
        print(data[:5])  # Show first 5 exchange funding rate records
    """
    # Validate API key
    api_key = os.getenv("COINGLASS_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "COINGLASS_API_KEY not found. "
            "Please add it to your .env file in the project root."
        )
    
    # Prepare API request
    url = "https://open-api-v4.coinglass.com/api/futures/funding-rate/exchange-list"
    headers = {"CG-API-KEY": api_key}
    
    # Prepare parameters
    params = {
        "symbol": symbol
    }
    
    # Make API request with retry logic
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if API response is successful
            if (data.get("code") == 0 or data.get("code") == "0") and "data" in data:
                # Convert to DataFrame if pandas is available, otherwise return raw data
                if PANDAS_AVAILABLE:
                    df = pd.DataFrame(data["data"])
                    return df
                else:
                    return data["data"]
            else:
                raise ConnectionError(f"API error: {data.get('msg', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            if attempt == 2:  # Last attempt
                raise ConnectionError(f"Failed to fetch data after 3 attempts: {str(e)}")
            time.sleep(1)  # Wait before retry
    
    return [] if not PANDAS_AVAILABLE else pd.DataFrame()  # Return empty list or DataFrame if all attempts fail


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches funding rate by exchange list from CoinGlass API.
    # Example usage:
    #   python funding_rate_exchange_list.py --symbol BTC
    #   python funding_rate_exchange_list.py --symbol ETH --output_format csv
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Fetch funding rate by exchange list from CoinGlass API")
    parser.add_argument('--symbol', type=str, default='BTC', help='Cryptocurrency symbol (default: BTC)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Call the main function to fetch data
        data = get_funding_rate_exchange_list(symbol=args.symbol)
        
        # Output in the specified format
        if args.output_format == 'json':
            if PANDAS_AVAILABLE and hasattr(data, 'to_dict'):
                print(json.dumps(data.to_dict('records'), ensure_ascii=False, indent=2))
            else:
                print(json.dumps(data, ensure_ascii=False, indent=2))
        else:  # csv
            if PANDAS_AVAILABLE and hasattr(data, 'to_csv'):
                print(data.to_csv(index=False))
            else:
                # Convert list of dicts to CSV manually
                if data:
                    import csv
                    import io
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                    print(output.getvalue())
                else:
                    print("No data available")
                    
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch data: {e}")