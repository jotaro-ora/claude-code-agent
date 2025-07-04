"""
LunarCrush Category Details Module

This module provides functionality to fetch snapshot metrics
for a social category from the LunarCrush API.

Dependencies:
- requests: For HTTP API calls  
- python-dotenv: For environment variable management (optional)
- os: For accessing environment variables

Environment Variables Required:
- LUNA_CRUSH_API_KEY: Your LunarCrush API key (required for API access)

Usage Example:
    from tools.lunacrush.category_details import get_category_details
    
    # Get metrics for DeFi category
    defi_category = get_category_details("defi")
"""

import os
try:
    from dotenv import load_dotenv
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    load_dotenv(os.path.join(project_root, '.env'))
except ImportError:
    pass

from lunacrush import make_lunacrush_request

def get_category_details(category, time_frame="24h"):
    """
    Get snapshot metrics for a social category.
    
    Args:
        category (str): Category to analyze (e.g., "defi", "nft", "gaming")
        time_frame (str): Time frame for metrics (default: "24h")
        
    Returns:
        dict: API response with category metrics
    """
    
    if not category or not category.strip():
        raise ValueError("category cannot be empty")
    
    category_cleaned = category.strip().lower()
    params = {"time_frame": time_frame}
    
    try:
        endpoint = f"/categories/{category_cleaned}/details"
        response = make_lunacrush_request(endpoint, params)
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to fetch category details for '{category}': {str(e)}")


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches category details from LunarCrush API.
    # Example usage:
    #   python category_details.py --category defi
    #   python category_details.py --category nft --time_frame 7d --output_format csv
    import argparse
    import json
    import csv
    import io
    
    parser = argparse.ArgumentParser(description="Fetch category details from LunarCrush API")
    parser.add_argument('--category', required=True, help='Category to analyze (e.g., defi, nft, gaming)')
    parser.add_argument('--time_frame', default='24h', help='Time frame for metrics (default: 24h)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Call the main function to fetch data
        data = get_category_details(args.category, args.time_frame)
        
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