# Tools Directory - Tools List

This document provides a comprehensive list of all tools available in the `/tools/` directory. This list is maintained for AI agents to quickly understand and query available functionality.

## Core CoinGecko API Tools

### 1. coingecko.py
**Purpose**: Core CoinGecko API wrapper with comprehensive functionality
**Main Function**: `get_coingecko_data()`
**Description**: Provides access to CoinGecko Pro API with support for multiple endpoints including ping, coins list, market data, and more
**Usage**: `from tools.coingecko import get_coingecko_data`

### 2. top_coins.py
**Purpose**: Get top N cryptocurrency symbols by market cap
**Main Function**: `get_top_coins_symbols(n=100)`
**Description**: Fetches the top N cryptocurrencies by market capitalization and returns their symbols
**Usage**: `from tools.top_coins import get_top_coins_symbols`

### 3. volume_data.py
**Purpose**: Get trading volume data for specified cryptocurrencies
**Main Function**: `get_volume_data(symbols)`
**Description**: Fetches trading volume data for a list of cryptocurrency symbols
**Usage**: `from tools.volume_data import get_volume_data`

## Coin Data Tools

### 4. coin_data_by_id.py
**Purpose**: Get detailed data for a specific coin by ID
**Main Function**: `get_coin_data_by_id(coin_id)`
**Description**: Fetches comprehensive data for a specific cryptocurrency including market data, community data, and developer data
**Usage**: `from tools.coin_data_by_id import get_coin_data_by_id`

### 5. coin_tickers_by_id.py
**Purpose**: Get ticker data for a specific coin by ID
**Main Function**: `get_coin_tickers_by_id(coin_id)`
**Description**: Fetches ticker information for a specific cryptocurrency from various exchanges
**Usage**: `from tools.coin_tickers_by_id import get_coin_tickers_by_id`

## Historical Data Tools

### 6. coin_historical_data_by_id.py
**Purpose**: Get historical data for a specific coin by ID and date
**Main Function**: `get_coin_historical_data_by_id(coin_id, date)`
**Description**: Fetches historical data for a specific cryptocurrency on a given date
**Usage**: `from tools.coin_historical_data_by_id import get_coin_historical_data_by_id`

### 7. coin_historical_chart_by_id.py
**Purpose**: Get historical chart data for a specific coin by ID
**Main Function**: `get_coin_historical_chart_by_id(coin_id, vs_currency, days)`
**Description**: Fetches historical price chart data for a specific cryptocurrency over a specified time period
**Usage**: `from tools.coin_historical_chart_by_id import get_coin_historical_chart_by_id`

### 8. coin_historical_chart_range_by_id.py
**Purpose**: Get historical chart data within a specific time range
**Main Function**: `get_coin_historical_chart_range_by_id(coin_id, vs_currency, from_timestamp, to_timestamp)`
**Description**: Fetches historical price chart data for a specific cryptocurrency within a custom time range
**Usage**: `from tools.coin_historical_chart_range_by_id import get_coin_historical_chart_range_by_id`

## OHLC Data Tools

### 9. coin_ohlc_by_id.py
**Purpose**: Get OHLC (Open, High, Low, Close) data for a specific coin by ID
**Main Function**: `get_coin_ohlc_by_id(coin_id, vs_currency, days)`
**Description**: Fetches OHLC chart data for a specific cryptocurrency over a specified time period
**Usage**: `from tools.coin_ohlc_by_id import get_coin_ohlc_by_id`

### 10. coin_ohlc_range_by_id.py
**Purpose**: Get OHLC data within a specific time range
**Main Function**: `get_coin_ohlc_range_by_id(coin_id, vs_currency, from_timestamp, to_timestamp)`
**Description**: Fetches OHLC chart data for a specific cryptocurrency within a custom time range
**Usage**: `from tools.coin_ohlc_range_by_id import get_coin_ohlc_range_by_id`

## Market Data Tools

### 11. coins_list.py
**Purpose**: Get the complete list of supported coins
**Main Function**: `get_coins_list(include_inactive=False)`
**Description**: Fetches the full list of all cryptocurrencies supported by CoinGecko
**Usage**: `from tools.coins_list import get_coins_list`

### 12. coins_list_market_data.py
**Purpose**: Get market data for a list of coins
**Main Function**: `get_coins_list_market_data(ids, vs_currency, order, per_page, page, sparkline, price_change_percentage)`
**Description**: Fetches market data for multiple cryptocurrencies with various filtering and sorting options
**Usage**: `from tools.coins_list_market_data import get_coins_list_market_data`

### 13. coins_gainers_losers.py
**Purpose**: Get top gainers and losers in the market
**Main Function**: `get_top_gainers_losers(vs_currency='usd')`
**Description**: Fetches the top performing and worst performing cryptocurrencies in the market
**Usage**: `from tools.coins_gainers_losers import get_top_gainers_losers`

## Tool Categories Summary

### Data Fetching
- `coingecko.py` - Core API wrapper
- `coins_list.py` - Complete coin list
- `coin_data_by_id.py` - Individual coin details

### Market Analysis
- `top_coins.py` - Top cryptocurrencies by market cap
- `volume_data.py` - Trading volume data
- `coins_gainers_losers.py` - Market performance leaders/laggards
- `coins_list_market_data.py` - Bulk market data

### Historical Analysis
- `coin_historical_data_by_id.py` - Historical data by date
- `coin_historical_chart_by_id.py` - Historical price charts
- `coin_historical_chart_range_by_id.py` - Custom time range charts

### Technical Analysis
- `coin_ohlc_by_id.py` - OHLC data for technical analysis
- `coin_ohlc_range_by_id.py` - Custom time range OHLC data

### Exchange Data
- `coin_tickers_by_id.py` - Exchange ticker information

## Environment Variables Required

**Important**: All tools automatically load API keys from the project root directory's `.env` file. 
The tools are configured to look for the `.env` file in the project root, regardless of where they are called from.

### Required Environment Variables:
- `COINGECKO_API_KEY`: Your CoinGecko Pro API key (required for all CoinGecko API tools)

### .env File Location:
```
claude-code-agent/
├── .env                    # ← API keys are loaded from here
├── tools/
│   ├── coingecko.py
│   └── ...
└── ...
```

### Example .env File Content:
```env
# CoinGecko API Configuration
COINGECKO_API_KEY=your_coingecko_api_key_here
```

**Note**: All tools use `load_dotenv()` with the project root path, ensuring consistent API key loading regardless of the current working directory.

## Usage Patterns

### Basic Data Fetching
```python
from tools.coin_data_by_id import get_coin_data_by_id
data = get_coin_data_by_id('bitcoin')
```

### Market Analysis
```python
from tools.top_coins import get_top_coins_symbols
from tools.volume_data import get_volume_data

# Get top 100 coins
top_symbols = get_top_coins_symbols(100)

# Get volume data for top coins
volume_data = get_volume_data(top_symbols)
```

### Historical Analysis
```python
from tools.coin_historical_chart_by_id import get_coin_historical_chart_by_id
chart_data = get_coin_historical_chart_by_id('bitcoin', 'usd', 30)
```

## Error Handling

All tools include:
- Retry logic (3 attempts by default)
- Comprehensive error handling
- Connection timeout protection (15 seconds)
- Clear error messages

## Performance Notes

- All tools implement efficient API usage
- Rate limiting is handled automatically
- Data is returned in optimized formats (DataFrame where appropriate)
- Error handling includes retry mechanisms

## Testing

All tools include comprehensive test suites located in `/tools/test/`:
- Unit tests for individual functions
- Integration tests for API interactions
- Error handling tests
- Performance tests

## Maintenance

This tools list is automatically maintained. When adding new tools:
1. Add the tool to the appropriate category
2. Update the tool categories summary
3. Add usage examples if needed
4. Update environment variables if required
5. Add corresponding test files

## Quick Reference

### Most Commonly Used Tools:
- `top_coins.py` - Get top cryptocurrencies
- `coin_data_by_id.py` - Get detailed coin information
- `coin_ohlc_by_id.py` - Get OHLC data for technical analysis
- `volume_data.py` - Get trading volume data

### For Technical Analysis:
- `coin_ohlc_by_id.py` - OHLC data
- `coin_historical_chart_by_id.py` - Historical price charts
- `coin_historical_chart_range_by_id.py` - Custom time ranges

### For Market Analysis:
- `top_coins.py` - Market cap rankings
- `coins_gainers_losers.py` - Market performance
- `volume_data.py` - Trading volume analysis
- `coins_list_market_data.py` - Bulk market data 