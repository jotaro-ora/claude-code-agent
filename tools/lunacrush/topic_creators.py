"""
LunarCrush Topic Creators Module

This module provides functionality to fetch top creators/influencers
for a specific topic from the LunarCrush API.

Dependencies:
- requests: For HTTP API calls  
- python-dotenv: For environment variable management (optional)
- os: For accessing environment variables

Environment Variables Required:
- LUNA_CRUSH_API_KEY: Your LunarCrush API key (required for API access)

Usage Example:
    from tools.lunacrush.topic_creators import get_topic_creators
    
    # Get top influencers talking about Bitcoin
    bitcoin_influencers = get_topic_creators("bitcoin", limit=15)
"""

import os
try:
    from dotenv import load_dotenv
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    load_dotenv(os.path.join(project_root, '.env'))
except ImportError:
    pass

from lunacrush import make_lunacrush_request

def get_topic_creators(topic, limit=10, time_frame="24h", sort_by="influence"):
    """
    Get top creators/influencers for a specific topic.
    
    Args:
        topic (str): Topic to get creators for
        limit (int): Maximum number of creators to return
        time_frame (str): Time frame for analysis ("1h", "6h", "24h", "7d")
        sort_by (str): Sort criterion ("influence", "engagement", "followers")
        
    Returns:
        dict: API response with creator/influencer data
    """
    
    if not topic or not topic.strip():
        raise ValueError("topic cannot be empty")
    
    topic_cleaned = topic.strip().lower()
    params = {
        "limit": limit,
        "time_frame": time_frame,
        "sort_by": sort_by
    }
    
    try:
        endpoint = f"/topics/{topic_cleaned}/creators"
        response = make_lunacrush_request(endpoint, params)
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to fetch topic creators for '{topic}': {str(e)}")


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches topic creators from LunarCrush API.
    # Example usage:
    #   python topic_creators.py --topic bitcoin
    #   python topic_creators.py --topic defi --limit 20 --time_frame 7d --sort_by engagement --output_format csv
    import argparse
    import json
    import csv
    import io
    
    parser = argparse.ArgumentParser(description="Fetch topic creators from LunarCrush API")
    parser.add_argument('--topic', required=True, help='Topic to get creators for')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of creators to return (default: 10)')
    parser.add_argument('--time_frame', default='24h', choices=['1h', '6h', '24h', '7d'], 
                        help='Time frame for analysis (default: 24h)')
    parser.add_argument('--sort_by', default='influence', choices=['influence', 'engagement', 'followers'], 
                        help='Sort criterion (default: influence)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Call the main function to fetch data
        data = get_topic_creators(args.topic, args.limit, args.time_frame, args.sort_by)
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:  # csv
            # Handle nested dict structure for CSV output
            if data and 'data' in data:
                creators_data = data['data']
                if isinstance(creators_data, list) and creators_data:
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=creators_data[0].keys())
                    writer.writeheader()
                    writer.writerows(creators_data)
                    print(output.getvalue())
                elif isinstance(creators_data, dict):
                    # Convert single dict to list for CSV output
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=creators_data.keys())
                    writer.writeheader()
                    writer.writerow(creators_data)
                    print(output.getvalue())
                else:
                    print("No data available")
            else:
                print("No data available")
                
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch data: {e}")