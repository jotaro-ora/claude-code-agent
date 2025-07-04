"""
LunarCrush Coins List Module

This module provides functionality to fetch a list of all supported coins
from the LunarCrush API with their basic metrics and information.

Dependencies:
- requests: For HTTP API calls  
- python-dotenv: For environment variable management
- os: For accessing environment variables

Environment Variables Required:
- LUNA_CRUSH_API_KEY: Your LunarCrush API key (required for API access)

Usage Example:
    from tools.lunacrush.coins_list import get_coins_list
    
    # Get list of all coins with default parameters
    coins = get_coins_list()
    
    # Get top 100 coins sorted by galaxy score
    top_coins = get_coins_list(limit=100, sort="gs")
"""

import os
try:
    from dotenv import load_dotenv
    # Load environment variables from project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    load_dotenv(os.path.join(project_root, '.env'))
except ImportError:
    # Handle case where python-dotenv is not available
    pass

from lunacrush import make_lunacrush_request

def get_coins_list(limit=50, sort="gs", desc=True):
    """
    Fetch a list of coins with their basic metrics from LunarCrush.
    
    This function retrieves a current snapshot of LunarCrush metrics on 
    tracked coin assets, including basic pricing data, Galaxy Score™, 
    AltRank™, average sentiment, and Social Dominance.
    
    Args:
        limit (int): Maximum number of coins to return (default: 50, max: 1000)
        sort (str): Field to sort by. Options include:
                   - "gs": Galaxy Score (default)
                   - "alt_rank": AltRank
                   - "mc": Market Cap
                   - "price": Current Price
                   - "price_score": Price Score
                   - "social_score": Social Score
                   - "sentiment": Average Sentiment
        desc (bool): Sort in descending order (default: True)
        
    Returns:
        dict: API response containing:
            - config: Request configuration
            - data: List of coin objects with metrics
            
    Raises:
        ConnectionError: If API requests fail after retries
        EnvironmentError: If LUNA_CRUSH_API_KEY environment variable is not set
        ValueError: If limit exceeds maximum allowed value
        
    Response Structure:
        Each coin object in the data array contains:
        - id: Coin identifier
        - symbol: Coin symbol (e.g., "BTC")
        - name: Coin name (e.g., "Bitcoin")
        - price: Current price in USD
        - market_cap: Market capitalization
        - galaxy_score: Galaxy Score™ (0-100)
        - alt_rank: AltRank™ position
        - sentiment: Average sentiment score
        - social_dominance: Social dominance percentage
        - price_score: Price performance score
        - social_score: Social engagement score
        
    Example Usage:
        # Get top 20 coins by Galaxy Score
        top_coins = get_coins_list(limit=20, sort="gs")
        
        # Get coins sorted by market cap
        by_mcap = get_coins_list(limit=100, sort="mc")
        
        # Get coins with lowest AltRank (best performing)
        best_performers = get_coins_list(limit=25, sort="alt_rank", desc=False)
    """
    
    # Validate parameters
    if limit > 1000:
        raise ValueError("Limit cannot exceed 1000")
    
    if limit < 1:
        raise ValueError("Limit must be at least 1")
    
    valid_sorts = ["gs", "alt_rank", "mc", "price", "price_score", "social_score", "sentiment"]
    if sort not in valid_sorts:
        raise ValueError(f"Invalid sort field: {sort}. Must be one of: {valid_sorts}")
    
    # Prepare API parameters
    params = {
        "limit": limit,
        "sort": sort,
        "desc": "true" if desc else "false"
    }
    
    # Make API request
    try:
        response = make_lunacrush_request("/coins", params)
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to fetch coins list: {str(e)}")

def get_coin_symbols():
    """
    Get a simple list of all supported coin symbols.
    
    Returns:
        list: List of coin symbols (e.g., ["BTC", "ETH", "ADA"])
        
    Note:
        This is a convenience function that extracts just the symbols
        from the full coins list for quick reference.
    """
    try:
        response = get_coins_list(limit=1000)
        if "data" in response:
            return [coin.get("symbol", "") for coin in response["data"]]
        return []
    except Exception:
        return []

def search_coins(query, limit=10):
    """
    Search for coins by name or symbol.
    
    Args:
        query (str): Search term (coin name or symbol)
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of matching coin objects
        
    Note:
        This function performs a client-side search on the coins list.
        For server-side search, use the specific coin endpoints.
    """
    try:
        response = get_coins_list(limit=1000)
        if "data" not in response:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for coin in response["data"]:
            name = coin.get("name", "").lower()
            symbol = coin.get("symbol", "").lower()
            
            if query_lower in name or query_lower in symbol:
                matches.append(coin)
                
            if len(matches) >= limit:
                break
                
        return matches
    except Exception:
        return []


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches coins list from LunarCrush API.
    # Example usage:
    #   python coins_list.py
    #   python coins_list.py --limit 100 --sort mc --desc false --output_format csv
    import argparse
    import json
    import csv
    import io
    
    parser = argparse.ArgumentParser(description="Fetch coins list from LunarCrush API")
    parser.add_argument('--limit', type=int, default=50, help='Maximum number of coins to return (default: 50)')
    parser.add_argument('--sort', default='gs', choices=['gs', 'alt_rank', 'mc', 'price', 'price_score', 'social_score', 'sentiment'], 
                        help='Field to sort by (default: gs)')
    parser.add_argument('--desc', type=str, default='true', choices=['true', 'false'], 
                        help='Sort in descending order (default: true)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Convert desc string to boolean
        desc_bool = args.desc.lower() == 'true'
        
        # Call the main function to fetch data
        data = get_coins_list(args.limit, args.sort, desc_bool)
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:  # csv
            # Handle nested dict structure for CSV output
            if data and 'data' in data:
                coins_data = data['data']
                if isinstance(coins_data, list) and coins_data:
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=coins_data[0].keys())
                    writer.writeheader()
                    writer.writerows(coins_data)
                    print(output.getvalue())
                else:
                    print("No data available")
            else:
                print("No data available")
                
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch data: {e}")