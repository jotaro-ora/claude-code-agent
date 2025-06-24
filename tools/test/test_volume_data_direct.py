import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('COINGECKO_API_KEY')
print('COINGECKO_API_KEY:', api_key)

# 使用和工具完全一样的参数
symbols = ['BTC_USD', 'ETH_USD']
token_symbols = [symbol.replace('_USD', '').lower() for symbol in symbols]

url = 'https://pro-api.coingecko.com/api/v3/coins/markets'
params = {
    "vs_currency": "USD",
    "symbols": ','.join(token_symbols),  # 尝试逗号分隔的字符串
    "order": "market_cap_desc",
    "per_page": "250",
    "page": "1",
    "sparkline": "false",
    "price_change_percentage": "24h"
}
headers = {'x-cg-pro-api-key': api_key}

print('URL:', url)
print('Params:', params)
print('Headers:', headers)

try:
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    print('Status code:', resp.status_code)
    print('Response headers:', dict(resp.headers))
    print('Response text length:', len(resp.text))
    
    if resp.status_code == 200:
        data = resp.json()
        print('Response data type:', type(data))
        print('Data length:', len(data))
        
        # 检查返回的币种
        returned_symbols = [item.get('symbol', '').lower() for item in data]
        print('Requested symbols:', token_symbols)
        print('Returned symbols:', returned_symbols)
        
        # 检查是否有我们请求的币种
        for requested in token_symbols:
            if requested in returned_symbols:
                print(f'✓ Found {requested}')
            else:
                print(f'❌ Missing {requested}')
        
        if len(data) > 0:
            print('First item keys:', list(data[0].keys()))
            print('First item:', data[0])
    else:
        print('Request failed with status code:', resp.status_code)
        
except Exception as e:
    print('Request failed with exception:', e)
    print('Exception type:', type(e)) 