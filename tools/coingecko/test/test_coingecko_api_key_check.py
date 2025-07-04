import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('COINGECKO_API_KEY')
print('COINGECKO_API_KEY:', api_key)

url = 'https://pro-api.coingecko.com/api/v3/ping'
headers = {'x-cg-pro-api-key': api_key}
try:
    resp = requests.get(url, headers=headers, timeout=10)
    print('Status code:', resp.status_code)
    print('Response:', resp.text)
except Exception as e:
    print('Request failed:', e) 