"""
CoinGlass Futures Supported Exchange Pairs API Tool

This module provides functionality to fetch supported futures exchanges and pairs
from the CoinGlass API.

Dependencies:
- requests: For HTTP API calls
- pandas: For data manipulation and DataFrame operations (optional)

Environment Variables Required:
- COINGLASS_API_KEY: Your CoinGlass API key (required for API access)

Usage Example:
    from tools.coinglass.futures_supported_exchange_pairs import get_futures_supported_exchange_pairs
    
    # Get all supported futures exchange pairs
    df = get_futures_supported_exchange_pairs()
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

def get_futures_supported_exchange_pairs():
    """
    Fetch the list of supported futures exchanges and pairs from CoinGlass API.
    
    Returns:
        dict: Dictionary with exchanges as keys and lists of trading pairs as values
        
    Raises:
        EnvironmentError: If COINGLASS_API_KEY is not found in environment variables
        ConnectionError: If API request fails after retries
        
    Example:
        df = get_futures_supported_exchange_pairs()
        print(df.head())
    """
    # Validate API key
    api_key = os.getenv("COINGLASS_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "COINGLASS_API_KEY not found. "
            "Please add it to your .env file in the project root."
        )
    
    # Prepare API request
    url = "https://open-api-v4.coinglass.com/api/futures/supported-exchange-pairs"
    headers = {"CG-API-KEY": api_key}
    
    # Make API request with retry logic
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if API response is successful
            if (data.get("code") == 0 or data.get("code") == "0") and "data" in data:
                # The data is a dictionary with exchanges as keys and pairs as values
                # Return the raw data structure as it's more useful than a flattened DataFrame
                return data["data"]
            else:
                raise ConnectionError(f"API error: {data.get('msg', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            if attempt == 2:  # Last attempt
                raise ConnectionError(f"Failed to fetch data after 3 attempts: {str(e)}")
            time.sleep(1)  # Wait before retry
    
    return {}  # Return empty dictionary if all attempts fail


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches the list of supported futures exchanges and pairs from CoinGlass API.
    # Example usage:
    #   python futures_supported_exchange_pairs.py
    #   python futures_supported_exchange_pairs.py --output_format json
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Fetch the list of supported futures exchanges and pairs from CoinGlass API")
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Call the main function to fetch data
        data = get_futures_supported_exchange_pairs()
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:  # csv
            # Convert dictionary to CSV format
            if data:
                import csv
                import io
                output = io.StringIO()
                
                # Flatten the dictionary for CSV output
                rows = []
                for exchange, pairs in data.items():
                    for pair in pairs:
                        rows.append({"exchange": exchange, "pair": pair})
                
                if rows:
                    writer = csv.DictWriter(output, fieldnames=["exchange", "pair"])
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