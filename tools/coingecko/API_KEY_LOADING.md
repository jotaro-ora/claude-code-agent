# API Key Loading Configuration

## Overview

All tools in the `/tools/` directory are configured to automatically load API keys from the project root directory's `.env` file. This ensures consistent API key management regardless of where the tools are called from.

## Configuration Details

### Environment Variable Loading

Each tool uses the following pattern to load environment variables:

```python
import os
from dotenv import load_dotenv

# Load environment variables from project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))
```

This ensures that:
- Tools always look for `.env` in the project root directory
- API keys are loaded regardless of the current working directory
- Consistent behavior across all tools

### Required API Keys

#### CoinGecko API Key
- **Environment Variable**: `COINGECKO_API_KEY`
- **Required For**: All CoinGecko API tools
- **Usage**: `os.getenv("COINGECKO_API_KEY")`
- **Header Format**: `{"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}`

**Tools using CoinGecko API:**
- `coingecko.py` - Core API wrapper
- `top_coins.py` - Top cryptocurrencies by market cap
- `volume_data.py` - Trading volume data
- `coin_data_by_id.py` - Individual coin details
- `coin_tickers_by_id.py` - Exchange ticker information
- `coin_historical_data_by_id.py` - Historical data by date
- `coin_historical_chart_by_id.py` - Historical price charts
- `coin_historical_chart_range_by_id.py` - Custom time range charts
- `coin_ohlc_by_id.py` - OHLC data for technical analysis
- `coin_ohlc_range_by_id.py` - Custom time range OHLC data
- `coins_list.py` - Complete coin list
- `coins_list_market_data.py` - Bulk market data
- `coins_gainers_losers.py` - Market performance leaders/laggards

## .env File Structure

The `.env` file should be located in the project root directory with the following structure:

```env
# CoinGecko API Configuration
COINGECKO_API_KEY=your_coingecko_pro_api_key_here

# Other API keys can be added here as needed
```

## Directory Structure

```
claude-code-agent/
├── .env                    # ← API keys are loaded from here
├── tools/
│   ├── coingecko.py
│   ├── top_coins.py
│   ├── volume_data.py
│   ├── coin_data_by_id.py
│   ├── coin_tickers_by_id.py
│   ├── coin_historical_data_by_id.py
│   ├── coin_historical_chart_by_id.py
│   ├── coin_historical_chart_range_by_id.py
│   ├── coin_ohlc_by_id.py
│   ├── coin_ohlc_range_by_id.py
│   ├── coins_list.py
│   ├── coins_list_market_data.py
│   ├── coins_gainers_losers.py
│   └── ...
└── ...
```

## Usage Examples

### Basic Usage
```python
# Import any tool - API keys are automatically loaded
from tools.coin_data_by_id import get_coin_data_by_id

# Tools will automatically use the API keys from .env
data = get_coin_data_by_id('bitcoin')
```

### Verification
```python
import os
from dotenv import load_dotenv

# Load environment variables
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

# Check if API keys are loaded
print('COINGECKO_API_KEY:', 'Loaded' if os.getenv('COINGECKO_API_KEY') else 'Not found')
```

## Error Handling

All tools include proper error handling for missing API keys:

### CoinGecko Tools
```python
headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
# If API key is missing, requests will fail with 401 Unauthorized
```

## Best Practices

1. **Never commit API keys**: Ensure `.env` is in `.gitignore`
2. **Use environment variables**: Always use `os.getenv()` instead of hardcoding
3. **Validate API keys**: Tools should validate API keys on initialization
4. **Provide clear error messages**: When API keys are missing, provide helpful error messages
5. **Document requirements**: Always document which API keys are required

## Troubleshooting

### Common Issues

1. **API key not found**: Ensure `.env` file exists in project root
2. **Wrong API key format**: Verify API key format matches service requirements
3. **Permission denied**: Check API key permissions and rate limits
4. **Network issues**: Verify internet connection and service availability

### Debug Steps

1. Check if `.env` file exists in project root
2. Verify API key format and validity
3. Test API key with service provider
4. Check tool logs for specific error messages
5. Verify network connectivity

## Security Notes

- API keys are sensitive credentials and should be kept secure
- Never log or print API keys in production
- Use environment variables instead of hardcoded values
- Regularly rotate API keys for security
- Monitor API usage for unusual activity 