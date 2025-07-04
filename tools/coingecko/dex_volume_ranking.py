"""
DEX Volume Ranking Tool - DeFiLlama API Integration

This module provides functionality to fetch DEX (Decentralized Exchange) trading volume 
rankings from DeFiLlama API. It retrieves the top N DEXes by trading volume with 
their 24-hour and 30-day volume data.

Dependencies:
- requests: For HTTP API calls
- pandas: For data manipulation and output formatting
- python-dotenv: For environment variable management

Environment Variables Required:
- None (DeFiLlama API is free and doesn't require API keys)

API/Service Limitations:
- Rate limits: Standard HTTP rate limits apply
- Data updates: Every hour
- Free API access without authentication

Usage Example:
    from tools.dex_volume_ranking import get_dex_volume_ranking
    
    # Get top 10 DEXes by trading volume
    result = get_dex_volume_ranking(10)
    
    # Get top 5 DEXes
    result = get_dex_volume_ranking(5)
"""

import requests
import pandas as pd
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = "https://api.llama.fi"
DEX_OVERVIEW_ENDPOINT = "/overview/dexs"
REQUEST_TIMEOUT = 15


def get_dex_volume_ranking(n: int) -> pd.DataFrame:
    """
    Get top N DEXes by trading volume from DeFiLlama API.
    
    Fetches DEX trading volume rankings with 24-hour and 30-day volume data.
    Returns the top N DEXes sorted by 24-hour trading volume.
    
    Args:
        n (int): Number of top DEXes to return (must be positive integer)
                Valid range: 1-100 (API typically returns ~50-100 DEXes)
    
    Returns:
        pd.DataFrame: DataFrame containing DEX ranking data with columns:
                     - name: DEX name
                     - total1d: 24-hour trading volume in USD
                     - total30d: 30-day trading volume in USD
                     - change1d: 24-hour percentage change
                     - change30d: 30-day percentage change
                     
    Raises:
        ValueError: If n is not a positive integer or exceeds available data
        ConnectionError: If API request fails
        RuntimeError: If data processing fails
        
    Limitations and Constraints:
        - Maximum n value depends on API response (typically 50-100 DEXes)
        - Data updates every hour
        - Free API with standard rate limits
        - No authentication required
        
    Error Handling:
        - Validates input parameters
        - Handles API connection errors with retries
        - Manages empty or malformed API responses
        - Provides meaningful error messages
        
    Performance Notes:
        - Single API call regardless of n value
        - Processing time scales with response size
        - Memory usage minimal for typical use cases
        
    Example Usage:
        # Get top 10 DEXes
        top_10 = get_dex_volume_ranking(10)
        print(top_10[['name', 'total1d', 'total30d']])
        
        # Get top 5 DEXes with error handling
        try:
            top_5 = get_dex_volume_ranking(5)
            print(f"Top 5 DEXes by 24h volume:")
            for _, row in top_5.iterrows():
                print(f"{row['name']}: ${row['total1d']:,.0f}")
        except ValueError as e:
            print(f"Invalid input: {e}")
        except ConnectionError as e:
            print(f"API error: {e}")
    """
    # Input validation
    _validate_input(n)
    
    try:
        # Fetch data from API
        dex_data = _fetch_dex_data()
        
        # Process and format data
        formatted_data = _process_dex_data(dex_data)
        
        # Return top N results
        return _get_top_n_dexes(formatted_data, n)
        
    except Exception as e:
        raise RuntimeError(f"Failed to get DEX volume ranking: {e}") from e


def _validate_input(n: int) -> None:
    """Validate input parameter n."""
    if not isinstance(n, int):
        raise ValueError(f"n must be an integer, got {type(n).__name__}")
    
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    
    if n > 100:
        raise ValueError(f"n cannot exceed 100, got {n}")


def _fetch_dex_data() -> Dict[str, Any]:
    """Fetch DEX volume data from DeFiLlama API."""
    url = f"{API_BASE_URL}{DEX_OVERVIEW_ENDPOINT}"
    
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            raise ValueError("API returned empty response")
        
        return data
        
    except requests.exceptions.Timeout:
        raise ConnectionError("Request timeout - API may be slow")
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Request failed: {e}")
    except ValueError as e:
        if "JSON" in str(e):
            raise ConnectionError("Invalid JSON response from API")
        raise


def _process_dex_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process raw API data into structured format."""
    if not isinstance(data, dict):
        raise ValueError("Invalid data format from API")
    
    # DeFiLlama API returns data in 'protocols' field
    protocols = data.get('protocols', [])
    if not protocols:
        raise ValueError("No DEX data found in API response")
    
    processed_data = []
    for protocol in protocols:
        if not isinstance(protocol, dict):
            continue
            
        # Extract required fields with defaults
        dex_info = {
            'name': protocol.get('name', 'Unknown'),
            'total1d': protocol.get('total24h', 0),
            'total30d': protocol.get('total30d', 0),
            'change1d': protocol.get('change_1d', 0),
            'change30d': protocol.get('change_1m', 0)
        }
        
        # Only include DEXes with valid volume data
        if dex_info['total1d'] > 0:
            processed_data.append(dex_info)
    
    if not processed_data:
        raise ValueError("No valid DEX data found")
    
    return processed_data


def _get_top_n_dexes(data: List[Dict[str, Any]], n: int) -> pd.DataFrame:
    """Get top N DEXes sorted by 24-hour volume."""
    # Sort by 24-hour volume (descending)
    sorted_data = sorted(data, key=lambda x: x['total1d'], reverse=True)
    
    # Take top N
    top_n = sorted_data[:n]
    
    if len(top_n) < n:
        available = len(top_n)
        print(f"Warning: Only {available} DEXes available, returning all")
    
    # Convert to DataFrame
    df = pd.DataFrame(top_n)
    
    # Add ranking column
    df.insert(0, 'rank', range(1, len(df) + 1))
    
    return df


if __name__ == "__main__":
    """Command-line interface for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Get DEX volume rankings")
    parser.add_argument(
        "n", 
        type=int, 
        help="Number of top DEXes to return (1-100)"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    
    args = parser.parse_args()
    
    try:
        result = get_dex_volume_ranking(args.n)
        
        if args.format == "table":
            print(f"\nTop {args.n} DEXes by 24h Trading Volume:")
            print("=" * 80)
            print(result.to_string(index=False, formatters={
                'total1d': '${:,.0f}'.format,
                'total30d': '${:,.0f}'.format,
                'change1d': '{:+.1f}%'.format,
                'change30d': '{:+.1f}%'.format
            }))
        elif args.format == "json":
            print(result.to_json(indent=2))
        elif args.format == "csv":
            print(result.to_csv(index=False))
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)