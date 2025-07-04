"""
LunarCrush API Core Module

This module provides core functionality for interacting with the LunarCrush API.
It includes common request handling, authentication, and error management.

Dependencies:
- requests: For HTTP API calls
- python-dotenv: For environment variable management
- os: For accessing environment variables

Environment Variables Required:
- LUNA_CRUSH_API_KEY: Your LunarCrush API key (required for API access)

API Rate Limits:
- LunarCrush API has rate limits that vary by subscription tier
- This module implements retry logic with delays to handle rate limiting

Usage Example:
    from tools.lunacrush.lunacrush import make_lunacrush_request
    
    # Make a request to the coins endpoint
    data = make_lunacrush_request("/coins")
"""

import requests
import time
import os
try:
    from dotenv import load_dotenv
    # Load environment variables from project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    load_dotenv(os.path.join(project_root, '.env'))
except ImportError:
    # Handle case where python-dotenv is not available
    pass

BASE_URL = "https://lunarcrush.com/api3"

def make_lunacrush_request(endpoint, params=None, retries=3):
    """
    Make a request to the LunarCrush API with automatic retry logic.
    
    Args:
        endpoint (str): API endpoint path (e.g., "/coins", "/coins/bitcoin")
        params (dict, optional): Query parameters for the request
        retries (int): Number of retry attempts (default: 3)
        
    Returns:
        dict: JSON response from the API
        
    Raises:
        EnvironmentError: If LUNA_CRUSH_API_KEY is not set
        ConnectionError: If all retry attempts fail
        
    Note:
        This function implements retry logic with delays between attempts
        to handle temporary API issues and rate limiting.
    """
    api_key = os.getenv("LUNA_CRUSH_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing LUNA_CRUSH_API_KEY - set it in your .env file")
    
    if params is None:
        params = {}
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    url = f"{BASE_URL}{endpoint}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            # Handle specific LunarCrush API errors
            if response.status_code == 402:
                error_msg = "LunarCrush API requires a paid subscription with credits. "
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += error_data["error"]
                except:
                    error_msg += "Please check your subscription at lunarcrush.com/pricing"
                raise ConnectionError(error_msg)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1 * (attempt + 1))  # Exponential backoff
                continue
            else:
                raise ConnectionError(f"API request failed after {retries} attempts: {str(e)}")

def validate_api_key():
    """
    Validate that the LunarCrush API key is properly configured.
    
    Returns:
        bool: True if API key is configured, False otherwise
        
    Note:
        This function only checks if the environment variable is set,
        not if the key is valid. Use test_api_connection() for validation.
    """
    return bool(os.getenv("LUNA_CRUSH_API_KEY"))

def test_api_connection():
    """
    Test the API connection by making a simple request.
    
    Returns:
        bool: True if connection is successful, False otherwise
        
    Note:
        This function makes a lightweight request to verify the API key
        is valid and the service is accessible.
    """
    try:
        make_lunacrush_request("/coins", {"limit": 1})
        return True
    except Exception:
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LunarCrush API Core Module - Test API functionality")
    parser.add_argument("--test", action="store_true", 
                       help="Test API connection and key validation")
    parser.add_argument("--validate-key", action="store_true",
                       help="Validate API key configuration")
    parser.add_argument("--output-format", choices=["json", "text"], default="text",
                       help="Output format (default: text)")
    
    args = parser.parse_args()
    
    if args.validate_key:
        if validate_api_key():
            if args.output_format == "json":
                print('{"status": "success", "message": "API key is configured"}')
            else:
                print("✅ API key is configured")
        else:
            if args.output_format == "json":
                print('{"status": "error", "message": "API key not configured"}')
            else:
                print("❌ API key not configured")
    
    if args.test:
        if test_api_connection():
            if args.output_format == "json":
                print('{"status": "success", "message": "API connection successful"}')
            else:
                print("✅ API connection successful")
        else:
            if args.output_format == "json":
                print('{"status": "error", "message": "API connection failed"}')
            else:
                print("❌ API connection failed")
    
    if not args.test and not args.validate_key:
        parser.print_help()