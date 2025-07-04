"""
LunarCrush Category Time Series Module

This module provides functionality to fetch historical metrics
for a category over time from the LunarCrush API.

Dependencies:
- requests: For HTTP API calls  
- python-dotenv: For environment variable management (optional)
- os: For accessing environment variables

Environment Variables Required:
- LUNA_CRUSH_API_KEY: Your LunarCrush API key (required for API access)

Usage Example:
    from tools.lunacrush.category_time_series import get_category_time_series
    
    # Get DeFi category historical data
    defi_history = get_category_time_series("defi", data_points=30)
"""

import os
try:
    from dotenv import load_dotenv
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    load_dotenv(os.path.join(project_root, '.env'))
except ImportError:
    pass

from lunacrush import make_lunacrush_request

def get_category_time_series(category, interval="1d", data_points=30):
    """
    Get historical metrics for a category over time.
    
    Args:
        category (str): Category to analyze
        interval (str): Time interval ("1h", "1d", "1w")
        data_points (int): Number of data points to return
        
    Returns:
        dict: API response with historical category metrics
    """
    
    if not category or not category.strip():
        raise ValueError("category cannot be empty")
    
    valid_intervals = ["1h", "1d", "1w"]
    if interval not in valid_intervals:
        raise ValueError(f"Invalid interval: {interval}")
    
    category_cleaned = category.strip().lower()
    params = {
        "interval": interval,
        "data_points": data_points
    }
    
    try:
        endpoint = f"/categories/{category_cleaned}/time-series"
        response = make_lunacrush_request(endpoint, params)
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to fetch category time series for '{category}': {str(e)}")


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches category time series from LunarCrush API.
    # Example usage:
    #   python category_time_series.py --category defi
    #   python category_time_series.py --category nft --interval 1h --data_points 24 --output_format csv
    import argparse
    import json
    import csv
    import io
    
    parser = argparse.ArgumentParser(description="Fetch category time series from LunarCrush API")
    parser.add_argument('--category', required=True, help='Category to analyze (e.g., defi, nft, gaming)')
    parser.add_argument('--interval', default='1d', choices=['1h', '1d', '1w'], help='Time interval (default: 1d)')
    parser.add_argument('--data_points', type=int, default=30, help='Number of data points to return (default: 30)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Call the main function to fetch data
        data = get_category_time_series(args.category, args.interval, args.data_points)
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:  # csv
            # Handle nested dict structure for CSV output
            if data and 'data' in data:
                category_data = data['data']
                if isinstance(category_data, dict):
                    # Convert single dict to list for CSV output
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=category_data.keys())
                    writer.writeheader()
                    writer.writerow(category_data)
                    print(output.getvalue())
                elif isinstance(category_data, list):
                    # Handle list of dicts
                    if category_data:
                        output = io.StringIO()
                        writer = csv.DictWriter(output, fieldnames=category_data[0].keys())
                        writer.writeheader()
                        writer.writerows(category_data)
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