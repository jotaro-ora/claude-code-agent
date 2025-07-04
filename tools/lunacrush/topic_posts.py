"""
LunarCrush Topic Posts Module

This module provides functionality to fetch top social posts
for a specific topic from the LunarCrush API.

Dependencies:
- requests: For HTTP API calls  
- python-dotenv: For environment variable management (optional)
- os: For accessing environment variables

Environment Variables Required:
- LUNA_CRUSH_API_KEY: Your LunarCrush API key (required for API access)

Usage Example:
    from tools.lunacrush.topic_posts import get_topic_posts
    
    # Get top posts about Bitcoin
    bitcoin_posts = get_topic_posts("bitcoin", limit=20)
"""

import os
try:
    from dotenv import load_dotenv
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    load_dotenv(os.path.join(project_root, '.env'))
except ImportError:
    pass

from lunacrush import make_lunacrush_request

def get_topic_posts(topic, limit=20, time_frame="24h", sort_by="engagement"):
    """
    Get top social media posts for a specific topic.
    
    Args:
        topic (str): Topic to get posts for
        limit (int): Maximum number of posts to return
        time_frame (str): Time frame for posts ("1h", "6h", "24h", "7d")
        sort_by (str): Sort criterion ("engagement", "time", "influence")
        
    Returns:
        dict: API response with social media posts
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
        endpoint = f"/topics/{topic_cleaned}/posts"
        response = make_lunacrush_request(endpoint, params)
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to fetch topic posts for '{topic}': {str(e)}")


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches topic posts from LunarCrush API.
    # Example usage:
    #   python topic_posts.py --topic bitcoin
    #   python topic_posts.py --topic defi --limit 30 --time_frame 7d --sort_by time --output_format csv
    import argparse
    import json
    import csv
    import io
    
    parser = argparse.ArgumentParser(description="Fetch topic posts from LunarCrush API")
    parser.add_argument('--topic', required=True, help='Topic to get posts for')
    parser.add_argument('--limit', type=int, default=20, help='Maximum number of posts to return (default: 20)')
    parser.add_argument('--time_frame', default='24h', choices=['1h', '6h', '24h', '7d'], 
                        help='Time frame for posts (default: 24h)')
    parser.add_argument('--sort_by', default='engagement', choices=['engagement', 'time', 'influence'], 
                        help='Sort criterion (default: engagement)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Call the main function to fetch data
        data = get_topic_posts(args.topic, args.limit, args.time_frame, args.sort_by)
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:  # csv
            # Handle nested dict structure for CSV output
            if data and 'data' in data:
                posts_data = data['data']
                if isinstance(posts_data, list) and posts_data:
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=posts_data[0].keys())
                    writer.writeheader()
                    writer.writerows(posts_data)
                    print(output.getvalue())
                elif isinstance(posts_data, dict):
                    # Convert single dict to list for CSV output
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=posts_data.keys())
                    writer.writeheader()
                    writer.writerow(posts_data)
                    print(output.getvalue())
                else:
                    print("No data available")
            else:
                print("No data available")
                
    except Exception as e:
        # Print error message if the API call fails
        print(f"Failed to fetch data: {e}")