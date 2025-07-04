"""
LunarCrush Topic Details Module

This module provides functionality to fetch 24-hour aggregate metrics
for a specific topic from the LunarCrush API.

Dependencies:
- requests: For HTTP API calls  
- python-dotenv: For environment variable management (optional)
- os: For accessing environment variables

Environment Variables Required:
- LUNA_CRUSH_API_KEY: Your LunarCrush API key (required for API access)

Usage Example:
    from tools.lunacrush.topic_details import get_topic_details
    
    # Get 24h metrics for Bitcoin topic
    bitcoin_details = get_topic_details("bitcoin")
    
    # Get DeFi topic metrics
    defi_details = get_topic_details("defi")
"""

import os
try:
    from dotenv import load_dotenv
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    load_dotenv(os.path.join(project_root, '.env'))
except ImportError:
    pass

from lunacrush import make_lunacrush_request

def get_topic_details(topic, time_frame="24h"):
    """
    Get 24-hour aggregate metrics for a specific topic.
    
    Args:
        topic (str): Topic to analyze (e.g., "bitcoin", "defi", "nft")
        time_frame (str): Time frame for metrics (default: "24h")
        
    Returns:
        dict: API response with topic metrics and details
        
    Raises:
        ConnectionError: If API requests fail after retries
        EnvironmentError: If LUNA_CRUSH_API_KEY environment variable is not set
        ValueError: If topic is empty
    """
    
    if not topic or not topic.strip():
        raise ValueError("topic cannot be empty")
    
    topic_cleaned = topic.strip().lower()
    params = {"time_frame": time_frame}
    
    try:
        endpoint = f"/topics/{topic_cleaned}/details"
        response = make_lunacrush_request(endpoint, params)
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to fetch topic details for '{topic}': {str(e)}")

def get_topic_metrics_summary(topic):
    """Get summarized metrics for a topic."""
    try:
        response = get_topic_details(topic)
        return response
    except Exception:
        return {}


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line.
    # It fetches topic details from LunarCrush API.
    # Example usage:
    #   python topic_details.py --topic bitcoin
    #   python topic_details.py --topic defi --time_frame 7d --output_format csv
    import argparse
    import json
    import csv
    import io
    
    parser = argparse.ArgumentParser(description="Fetch topic details from LunarCrush API")
    parser.add_argument('--topic', required=True, help='Topic to analyze (e.g., bitcoin, defi, nft)')
    parser.add_argument('--time_frame', default='24h', help='Time frame for metrics (default: 24h)')
    parser.add_argument('--output_format', choices=['json', 'csv'], default='json', help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Call the main function to fetch data
        data = get_topic_details(args.topic, args.time_frame)
        
        # Output in the specified format
        if args.output_format == 'json':
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:  # csv
            # Handle nested dict structure for CSV output
            if data and 'data' in data:
                topic_data = data['data']
                if isinstance(topic_data, dict):
                    # Convert single dict to list for CSV output
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=topic_data.keys())
                    writer.writeheader()
                    writer.writerow(topic_data)
                    print(output.getvalue())
                elif isinstance(topic_data, list):
                    # Handle list of dicts
                    if topic_data:
                        output = io.StringIO()
                        writer = csv.DictWriter(output, fieldnames=topic_data[0].keys())
                        writer.writeheader()
                        writer.writerows(topic_data)
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