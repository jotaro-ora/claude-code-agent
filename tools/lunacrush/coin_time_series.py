"""
LunarCrush Coin Time Series Module

This module provides functionality to fetch historical social and market metrics
for a specific cryptocurrency over time from the LunarCrush API.

Dependencies:
- requests: For HTTP API calls  
- python-dotenv: For environment variable management (optional)
- os: For accessing environment variables

Environment Variables Required:
- LUNA_CRUSH_API_KEY: Your LunarCrush API key (required for API access)

Usage Example:
    from tools.lunacrush.coin_time_series import get_coin_time_series
    
    # Get Bitcoin time series data for last 30 days
    btc_timeseries = get_coin_time_series("bitcoin", interval="1d", data_points=30)
    
    # Get Ethereum hourly data for last 24 hours
    eth_timeseries = get_coin_time_series("ETH", interval="1h", data_points=24)
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

def get_coin_time_series(coin_identifier, interval="1d", data_points=30, metrics=None):
    """
    Fetch historical social and market metrics for a specific cryptocurrency.
    
    This function retrieves time-series data for a coin including price movements,
    social media metrics, sentiment analysis, and other LunarCrush metrics
    over a specified time period.
    
    Args:
        coin_identifier (str): Coin identifier. Can be:
                              - Coin symbol (e.g., "BTC", "ETH")
                              - Coin name (e.g., "bitcoin", "ethereum")
                              - LunarCrush coin ID
        interval (str): Time interval for data points. Options:
                       - "1h": Hourly data
                       - "1d": Daily data (default)
                       - "1w": Weekly data
        data_points (int): Number of time-series data points to return
                          (default: 30, max: varies by subscription)
        metrics (list, optional): Specific metrics to include. If None, returns all available.
                                 Options: ["price", "volume", "market_cap", "social_volume", 
                                          "sentiment", "galaxy_score", "alt_rank", etc.]
        
    Returns:
        dict: API response containing:
            - config: Request configuration
            - data: Time series data array with timestamps and metrics
            
    Raises:
        ConnectionError: If API requests fail after retries
        EnvironmentError: If LUNA_CRUSH_API_KEY environment variable is not set
        ValueError: If coin_identifier is empty or invalid parameters
        
    Response Structure:
        The response contains time-series data with each data point including:
        
        Timestamp:
        - time: Unix timestamp
        - timeSeries: Array of historical data points
        
        Price/Market Data:
        - price: Price in USD at timestamp
        - price_btc: Price in BTC at timestamp
        - volume: Trading volume at timestamp
        - market_cap: Market capitalization at timestamp
        - percent_change_24h: 24-hour price change
        
        Social Metrics:
        - social_volume: Social media mentions count
        - social_dominance: Social dominance percentage
        - sentiment: Average sentiment score
        - sentiment_absolute: Absolute sentiment count
        - tweets: Number of tweets
        - tweet_spam: Spam tweet count
        - news: Number of news articles
        - reddit_posts: Reddit post count
        - youtube: YouTube mention count
        
        LunarCrush Metrics:
        - galaxy_score: Galaxy Score™ at timestamp
        - alt_rank: AltRank™ position at timestamp
        - price_score: Price performance score
        - social_score: Social engagement score
        - correlation_rank: Social-price correlation rank
        - volatility: Price volatility measure
        
        Technical Indicators:
        - close: Close price for the period
        - high: High price for the period  
        - low: Low price for the period
        - open: Open price for the period
        
    Example Usage:
        # Get Bitcoin daily data for last month
        btc_data = get_coin_time_series("bitcoin", "1d", 30)
        
        # Get Ethereum hourly data for last day
        eth_data = get_coin_time_series("ETH", "1h", 24)
        
        # Get specific metrics only
        price_data = get_coin_time_series("bitcoin", "1d", 7, 
                                         metrics=["price", "volume", "market_cap"])
        
        # Process time series data
        if btc_data.get("data") and btc_data["data"].get("timeSeries"):
            for point in btc_data["data"]["timeSeries"]:
                timestamp = point.get("time")
                price = point.get("price")
                social_vol = point.get("social_volume")
                print(f"Time: {timestamp}, Price: ${price}, Social Volume: {social_vol}")
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
    
    # Add metrics filter if specified
    if metrics:
        if isinstance(metrics, list):
            params["metrics"] = ",".join(metrics)
        else:
            params["metrics"] = str(metrics)
    
    # Make API request
    try:
        endpoint = f"/coins/{coin_id}/time-series"
        response = make_lunacrush_request(endpoint, params)
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to fetch time series data for '{coin_identifier}': {str(e)}")

def get_coin_price_history(coin_identifier, days=30):
    """
    Get simplified price history for a coin.
    
    Args:
        coin_identifier (str): Coin identifier (symbol, name, or ID)
        days (int): Number of days of price history (default: 30)
        
    Returns:
        dict: Time series data focused on price metrics
        
    Note:
        This is a convenience function that focuses on price-related metrics
        for simpler price analysis and charting.
    """
    try:
        metrics = ["price", "volume", "market_cap", "high", "low", "open", "close"]
        response = get_coin_time_series(coin_identifier, "1d", days, metrics)
        return response
    except Exception:
        return {}

def get_coin_social_history(coin_identifier, days=7):
    """
    Get social media metrics history for a coin.
    
    Args:
        coin_identifier (str): Coin identifier (symbol, name, or ID)
        days (int): Number of days of social history (default: 7)
        
    Returns:
        dict: Time series data focused on social metrics
        
    Note:
        This function optimizes for social media analytics by requesting
        only social-related metrics over the specified time period.
    """
    try:
        social_metrics = [
            "social_volume", "social_dominance", "sentiment", "tweets", 
            "news", "reddit_posts", "youtube", "social_score"
        ]
        response = get_coin_time_series(coin_identifier, "1d", days, social_metrics)
        return response
    except Exception:
        return {}

def get_coin_galaxy_score_history(coin_identifier, days=30):
    """
    Get Galaxy Score™ history for a coin.
    
    Args:
        coin_identifier (str): Coin identifier (symbol, name, or ID)
        days (int): Number of days of Galaxy Score history (default: 30)
        
    Returns:
        dict: Time series data focused on Galaxy Score and related metrics
        
    Note:
        This function focuses on LunarCrush's proprietary Galaxy Score™
        and related performance metrics over time.
    """
    try:
        galaxy_metrics = [
            "galaxy_score", "alt_rank", "price_score", "social_score", 
            "correlation_rank", "volatility"
        ]
        response = get_coin_time_series(coin_identifier, "1d", days, galaxy_metrics)
        return response
    except Exception:
        return {}


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches coin time series from LunarCrush API.
    # Example usage:
    #   python coin_time_series.py --coin_identifier bitcoin
    #   python coin_time_series.py --coin_identifier BTC --interval 1h --data_points 24 --output_format csv
    import argparse
    import json
    import csv
    import io
    
    parser = argparse.ArgumentParser(description="Fetch coin time series from LunarCrush API")
    parser.add_argument('--coin_identifier', required=True, help='Coin identifier (symbol, name, or ID)')
    parser.add_argument('--interval', default='1d', choices=['1h', '1d', '1w'], help='Time interval (default: 1d)')
    parser.add_argument('--data_points', type=int, default=30, help='Number of data points to return (default: 30)')
    parser.add_argument('--metrics', help='Comma-separated list of metrics to include (optional)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Parse metrics if provided
        metrics = None
        if args.metrics:
            metrics = [m.strip() for m in args.metrics.split(',')]
        
        # Call the main function to fetch data
        data = get_coin_time_series(args.coin_identifier, args.interval, args.data_points, metrics)
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:  # csv
            # Handle nested dict structure for CSV output
            if data and 'data' in data:
                coin_data = data['data']
                if isinstance(coin_data, dict):
                    # Check if there's a timeSeries array
                    if 'timeSeries' in coin_data and isinstance(coin_data['timeSeries'], list):
                        if coin_data['timeSeries']:
                            output = io.StringIO()
                            writer = csv.DictWriter(output, fieldnames=coin_data['timeSeries'][0].keys())
                            writer.writeheader()
                            writer.writerows(coin_data['timeSeries'])
                            print(output.getvalue())
                        else:
                            print("No time series data available")
                    else:
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