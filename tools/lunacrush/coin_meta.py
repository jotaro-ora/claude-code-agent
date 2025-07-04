"""
LunarCrush Coin Metadata Module

This module provides functionality to fetch detailed metadata and metrics
for a specific cryptocurrency from the LunarCrush API.

Dependencies:
- requests: For HTTP API calls  
- python-dotenv: For environment variable management (optional)
- os: For accessing environment variables

Environment Variables Required:
- LUNA_CRUSH_API_KEY: Your LunarCrush API key (required for API access)

Usage Example:
    from tools.lunacrush.coin_meta import get_coin_meta
    
    # Get detailed Bitcoin metadata
    btc_data = get_coin_meta("bitcoin")
    
    # Get Ethereum metadata by symbol
    eth_data = get_coin_meta("ETH")
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

def get_coin_meta(coin_identifier, interval="1d", data_points=30):
    """
    Fetch detailed metadata and metrics for a specific cryptocurrency.
    
    This function retrieves comprehensive information about a single coin
    including 60+ metrics, social data, market data, and metadata from
    the LunarCrush API.
    
    Args:
        coin_identifier (str): Coin identifier. Can be:
                              - Coin symbol (e.g., "BTC", "ETH")
                              - Coin name (e.g., "bitcoin", "ethereum")
                              - LunarCrush coin ID
        interval (str): Time interval for time-series data. Options:
                       - "1h": Hourly data
                       - "1d": Daily data (default)
                       - "1w": Weekly data
        data_points (int): Number of time-series data points to return
                          (default: 30, max: varies by subscription)
        
    Returns:
        dict: API response containing:
            - config: Request configuration
            - data: Detailed coin object with comprehensive metrics
            
    Raises:
        ConnectionError: If API requests fail after retries
        EnvironmentError: If LUNA_CRUSH_API_KEY environment variable is not set
        ValueError: If coin_identifier is empty or invalid parameters
        
    Response Structure:
        The coin object contains comprehensive data including:
        
        Basic Information:
        - id: LunarCrush coin ID
        - symbol: Coin symbol (e.g., "BTC")
        - name: Full coin name (e.g., "Bitcoin")
        - categories: Array of categories the coin belongs to
        
        Market Data:
        - price: Current price in USD
        - price_btc: Price in BTC
        - market_cap: Market capitalization
        - volume_24h: 24-hour trading volume
        - percent_change_24h: 24-hour price change percentage
        - percent_change_7d: 7-day price change percentage
        - percent_change_30d: 30-day price change percentage
        
        LunarCrush Metrics:
        - galaxy_score: Galaxy Score™ (0-100)
        - alt_rank: AltRank™ position
        - sentiment: Average sentiment score
        - social_dominance: Social dominance percentage
        - price_score: Price performance score (0-100)
        - social_score: Social engagement score (0-100)
        - correlation_rank: Correlation rank
        - volatility: Price volatility measure
        
        Social Metrics:
        - social_volume: Social media mentions volume
        - social_volume_24h_change: 24h change in social volume
        - tweets: Number of tweets
        - tweet_spam: Spam tweet count
        - news: Number of news articles
        - reddit_posts: Reddit post count
        - reddit_posts_score: Reddit engagement score
        - youtube: YouTube video count
        - medium: Medium article count
        
        Technical Analysis:
        - close: Latest close price
        - high_24h: 24-hour high
        - low_24h: 24-hour low
        - open_24h: 24-hour open price
        
        Time Series Data:
        - timeSeries: Array of historical data points with timestamps
                     Contains price, volume, social metrics over time
        
    Example Usage:
        # Get Bitcoin metadata with default settings
        btc = get_coin_meta("bitcoin")
        
        # Get Ethereum metadata with hourly data
        eth = get_coin_meta("ETH", interval="1h", data_points=24)
        
        # Access specific metrics
        if btc.get("data"):
            coin = btc["data"]
            print(f"Galaxy Score: {coin.get('galaxy_score')}")
            print(f"Social Dominance: {coin.get('social_dominance')}%")
            print(f"24h Price Change: {coin.get('percent_change_24h')}%")
    """
    
    # Validate parameters
    if not coin_identifier or not coin_identifier.strip():
        raise ValueError("coin_identifier cannot be empty")
    
    valid_intervals = ["1h", "1d", "1w"]
    if interval not in valid_intervals:
        raise ValueError(f"Invalid interval: {interval}. Must be one of: {valid_intervals}")
    
    if data_points < 1:
        raise ValueError("data_points must be at least 1")
    
    if data_points > 720:  # Reasonable upper limit
        raise ValueError("data_points cannot exceed 720")
    
    # Clean and prepare coin identifier
    coin_id = coin_identifier.strip().lower()
    
    # Prepare API parameters
    params = {
        "interval": interval,
        "data_points": data_points
    }
    
    # Make API request
    try:
        endpoint = f"/coins/{coin_id}"
        response = make_lunacrush_request(endpoint, params)
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to fetch coin metadata for '{coin_identifier}': {str(e)}")

def get_coin_basic_info(coin_identifier):
    """
    Get basic information for a coin without time-series data.
    
    Args:
        coin_identifier (str): Coin identifier (symbol, name, or ID)
        
    Returns:
        dict: Basic coin information without time-series data
        
    Note:
        This is a lightweight version that fetches minimal data points
        for quick access to basic coin information.
    """
    try:
        response = get_coin_meta(coin_identifier, interval="1d", data_points=1)
        return response
    except Exception:
        return {}

def get_coin_social_metrics(coin_identifier, days=7):
    """
    Get focused social media metrics for a coin.
    
    Args:
        coin_identifier (str): Coin identifier (symbol, name, or ID)
        days (int): Number of days of data to retrieve (default: 7)
        
    Returns:
        dict: Coin data focused on social metrics
        
    Note:
        This function optimizes for social media data retrieval
        by requesting daily intervals for the specified time period.
    """
    try:
        response = get_coin_meta(coin_identifier, interval="1d", data_points=days)
        return response
    except Exception:
        return {}

def validate_coin_exists(coin_identifier):
    """
    Check if a coin exists in the LunarCrush database.
    
    Args:
        coin_identifier (str): Coin identifier to validate
        
    Returns:
        bool: True if coin exists, False otherwise
        
    Note:
        This function makes a minimal API call to check coin existence
        without retrieving full metadata.
    """
    try:
        response = get_coin_basic_info(coin_identifier)
        return bool(response.get("data"))
    except Exception:
        return False


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches coin metadata from LunarCrush API.
    # Example usage:
    #   python coin_meta.py --coin_identifier bitcoin
    #   python coin_meta.py --coin_identifier BTC --interval 1h --data_points 24 --output_format csv
    import argparse
    import json
    import csv
    import io
    
    parser = argparse.ArgumentParser(description="Fetch coin metadata from LunarCrush API")
    parser.add_argument('--coin_identifier', required=True, help='Coin identifier (symbol, name, or ID)')
    parser.add_argument('--interval', default='1d', choices=['1h', '1d', '1w'], help='Time interval (default: 1d)')
    parser.add_argument('--data_points', type=int, default=30, help='Number of data points to return (default: 30)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Call the main function to fetch data
        data = get_coin_meta(args.coin_identifier, args.interval, args.data_points)
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:  # csv
            # Handle nested dict structure for CSV output
            if data and 'data' in data:
                coin_data = data['data']
                if isinstance(coin_data, dict):
                    # Convert single dict to list for CSV output
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=coin_data.keys())
                    writer.writeheader()
                    writer.writerow(coin_data)
                    print(output.getvalue())
                elif isinstance(coin_data, list):
                    # Handle list of dicts
                    if coin_data:
                        output = io.StringIO()
                        writer = csv.DictWriter(output, fieldnames=coin_data[0].keys())
                        writer.writeheader()
                        writer.writerows(coin_data)
                        print(output.getvalue())
                    else:
                        print("No data available")
                else:
                    print("No data available")
            else:
                print("No data available")
                
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch data: {e}")