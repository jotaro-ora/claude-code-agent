# Tools Directory - Tools List

This document provides a comprehensive list of all tools available in the `/tools/` directory. This list is maintained for AI agents to quickly understand and query available functionality.

**🖥️ CLI Support**: All tools that connect to external APIs support command-line interface (CLI) usage for direct testing and integration.

## Core CoinGecko API Tools

### 1. coingecko.py
**Purpose**: Core CoinGecko API wrapper with comprehensive functionality
**Main Function**: `get_coingecko_ohlc(symbol, interval, start_time, end_time)`
**Description**: Provides access to CoinGecko Pro API with support for historical OHLC data retrieval
**Usage**: `from tools.coingecko import get_coingecko_ohlc`
**CLI Usage**:
```bash
python tools/coingecko.py --symbol BTC_USD --interval 1d --start_time 2023-01-01 --end_time 2023-01-31
python tools/coingecko.py --symbol ETH_USD --interval 1h --start_time 2023-12-01 --end_time 2023-12-07 --output_format csv
```

### 2. top_coins.py
**Purpose**: Get top N cryptocurrency symbols by market cap
**Main Function**: `get_top_coins(n=10, include_extra_data=False)`
**Description**: Fetches the top N cryptocurrencies by market capitalization and returns their symbols or detailed data
**Usage**: `from tools.top_coins import get_top_coins`
**CLI Usage**:
```bash
python tools/top_coins.py --n 10
python tools/top_coins.py --n 50 --include_extra_data --output_format json
```

### 3. volume_data.py
**Purpose**: Get trading volume data for specified cryptocurrencies
**Main Function**: `get_volume_data(symbols)`
**Description**: Fetches trading volume data for a list of cryptocurrency symbols
**Usage**: `from tools.volume_data import get_volume_data`

## Coin Data Tools

### 4. coin_data_by_id.py
**Purpose**: Get detailed data for a specific coin by ID
**Main Function**: `get_coin_data_by_id(coin_id, localization='false', tickers='true', market_data='true', community_data='true', developer_data='true', sparkline='false')`
**Description**: Fetches comprehensive data for a specific cryptocurrency including market data, community data, and developer data
**Usage**: `from tools.coin_data_by_id import get_coin_data_by_id`
**CLI Usage**:
```bash
python tools/coin_data_by_id.py --coin_id bitcoin
python tools/coin_data_by_id.py --coin_id ethereum --market_data false --sparkline true
```

### 5. coin_tickers_by_id.py
**Purpose**: Get ticker data for a specific coin by ID
**Main Function**: `get_coin_tickers_by_id(coin_id, exchange_ids=None, include_exchange_logo=False, page=1, order=None, depth=False)`
**Description**: Fetches ticker information for a specific cryptocurrency from various exchanges
**Usage**: `from tools.coin_tickers_by_id import get_coin_tickers_by_id`
**CLI Usage**:
```bash
python tools/coin_tickers_by_id.py --coin_id bitcoin
python tools/coin_tickers_by_id.py --coin_id ethereum --include_exchange_logo --output_format csv
```

## Historical Data Tools

### 6. coin_historical_data_by_id.py
**Purpose**: Get historical data for a specific coin by ID and date
**Main Function**: `get_coin_historical_data_by_id(coin_id, date, localization='false')`
**Description**: Fetches historical data for a specific cryptocurrency on a given date
**Usage**: `from tools.coin_historical_data_by_id import get_coin_historical_data_by_id`
**CLI Usage**:
```bash
python tools/coin_historical_data_by_id.py --coin_id bitcoin --date 30-12-2017
python tools/coin_historical_data_by_id.py --coin_id ethereum --date 01-01-2020 --localization true
```

### 7. coin_historical_chart_by_id.py
**Purpose**: Get historical chart data for a specific coin by ID
**Main Function**: `get_coin_historical_chart_by_id(coin_id, vs_currency='usd', days=30, interval=None)`
**Description**: Fetches historical price chart data for a specific cryptocurrency over a specified time period
**Usage**: `from tools.coin_historical_chart_by_id import get_coin_historical_chart_by_id`
**CLI Usage**:
```bash
python tools/coin_historical_chart_by_id.py --coin_id bitcoin --days 30
python tools/coin_historical_chart_by_id.py --coin_id ethereum --vs_currency usd --days 7 --interval daily
```

### 8. coin_historical_chart_range_by_id.py
**Purpose**: Get historical chart data within a specific time range
**Main Function**: `get_coin_historical_chart_range_by_id(coin_id, vs_currency='usd', from_timestamp=None, to_timestamp=None)`
**Description**: Fetches historical price chart data for a specific cryptocurrency within a custom time range
**Usage**: `from tools.coin_historical_chart_range_by_id import get_coin_historical_chart_range_by_id`
**CLI Usage**:
```bash
python tools/coin_historical_chart_range_by_id.py --coin_id bitcoin --from_timestamp 1609459200 --to_timestamp 1640995200
python tools/coin_historical_chart_range_by_id.py --coin_id ethereum --vs_currency usd --from_timestamp 1609459200 --to_timestamp 1640995200
```

## OHLC Data Tools

### 9. coin_ohlc_by_id.py
**Purpose**: Get OHLC (Open, High, Low, Close) data for a specific coin by ID
**Main Function**: `get_coin_ohlc_by_id(coin_id, vs_currency='usd', days=30)`
**Description**: Fetches OHLC chart data for a specific cryptocurrency over a specified time period
**Usage**: `from tools.coin_ohlc_by_id import get_coin_ohlc_by_id`
**CLI Usage**:
```bash
python tools/coin_ohlc_by_id.py --coin_id bitcoin --days 30
python tools/coin_ohlc_by_id.py --coin_id ethereum --vs_currency usd --days 7
```

### 10. coin_ohlc_range_by_id.py
**Purpose**: Get OHLC data within a specific time range
**Main Function**: `get_coin_ohlc_range_by_id(coin_id, vs_currency='usd', from_timestamp=None, to_timestamp=None, interval=None)`
**Description**: Fetches OHLC chart data for a specific cryptocurrency within a custom time range
**Usage**: `from tools.coin_ohlc_range_by_id import get_coin_ohlc_range_by_id`
**CLI Usage**:
```bash
python tools/coin_ohlc_range_by_id.py --coin_id bitcoin --from_timestamp 1609459200 --to_timestamp 1640995200
python tools/coin_ohlc_range_by_id.py --coin_id ethereum --vs_currency usd --from_timestamp 1609459200 --to_timestamp 1640995200 --interval daily
```

## Market Data Tools

### 11. coins_list.py
**Purpose**: Get the complete list of supported coins
**Main Function**: `get_coins_list(include_inactive=False)`
**Description**: Fetches the full list of all cryptocurrencies supported by CoinGecko
**Usage**: `from tools.coins_list import get_coins_list`
**CLI Usage**:
```bash
python tools/coins_list.py
python tools/coins_list.py --include_inactive --output_format json --limit 100
```

### 12. coins_list_market_data.py
**Purpose**: Get market data for a list of coins
**Main Function**: `get_coins_list_market_data(vs_currency='usd', order='market_cap_desc', per_page=100, page=1, sparkline=False, price_change_percentage=None)`
**Description**: Fetches market data for multiple cryptocurrencies with various filtering and sorting options
**Usage**: `from tools.coins_list_market_data import get_coins_list_market_data`
**CLI Usage**:
```bash
python tools/coins_list_market_data.py --vs_currency usd --per_page 10
python tools/coins_list_market_data.py --vs_currency usd --order market_cap_desc --per_page 50 --output_format csv
```

### 13. coins_gainers_losers.py
**Purpose**: Get top gainers and losers in the market
**Main Function**: `get_top_gainers_losers(vs_currency='usd')`
**Description**: Fetches the top performing and worst performing cryptocurrencies in the market
**Usage**: `from tools.coins_gainers_losers import get_top_gainers_losers`
**CLI Usage**:
```bash
python tools/coins_gainers_losers.py
python tools/coins_gainers_losers.py --vs_currency eur --output_format json
```

## Tool Categories Summary

### Data Fetching
- `coingecko.py` - Core API wrapper with OHLC data
- `coins_list.py` - Complete coin list
- `coin_data_by_id.py` - Individual coin details

### Market Analysis
- `top_coins.py` - Top cryptocurrencies by market cap
- `coins_gainers_losers.py` - Market performance leaders/laggards
- `coins_list_market_data.py` - Bulk market data

### DEX Volume Analysis
- `dex_volume_ranking.py` - DEX trading volume rankings from DeFiLlama

### Historical Analysis
- `coin_historical_data_by_id.py` - Historical data by date
- `coin_historical_chart_by_id.py` - Historical price charts
- `coin_historical_chart_range_by_id.py` - Custom time range charts

### Technical Analysis
- `coin_ohlc_by_id.py` - OHLC data for technical analysis
- `coin_ohlc_range_by_id.py` - Custom time range OHLC data

### Exchange Data
- `coin_tickers_by_id.py` - Exchange ticker information

### Tool Selection and Discovery
- `tool_selector.py` - AI-powered tool filtering and recommendation

## DEX Volume Analysis Tools

### 14. dex_volume_ranking.py
**Purpose**: Get DEX (Decentralized Exchange) trading volume rankings from DeFiLlama
**Main Function**: `get_dex_volume_ranking(n)`
**Description**: Fetches the top N DEXes by trading volume with their 24-hour and 30-day volume data from DeFiLlama API
**Usage**: `from tools.dex_volume_ranking import get_dex_volume_ranking`
**CLI Usage**:
```bash
python tools/dex_volume_ranking.py 10
python tools/dex_volume_ranking.py 20 --format json
python tools/dex_volume_ranking.py 5 --format csv
```

## AI-Powered Tool Selection

### 15. tool_selector.py
**Purpose**: AI-powered tool filtering and recommendation system for efficient tool discovery
**Main Function**: `search_tools(query, max_results=5)` and `get_tool_details(tool_name)`
**Description**: Uses Claude AI to intelligently filter and recommend tools based on natural language queries. Designed to be fast, cost-effective, and scalable for hundreds of tools. Includes fallback search mechanism for when API is not available.
**Usage**: `from tools.tool_selector import ToolSelector`
**CLI Usage**:
```bash
python tools/tool_selector.py "get bitcoin price data"
python tools/tool_selector.py "DEX trading volume" --max-results 3
python tools/tool_selector.py "top cryptocurrencies by market cap" --format json
python tools/tool_selector.py "historical OHLC data" --details
```

## Environment Variables Required

**Important**: All tools automatically load API keys from the project root directory's `.env` file. 
The tools are configured to look for the `.env` file in the project root, regardless of where they are called from.

### Required Environment Variables:
- `COINGECKO_API_KEY`: Your CoinGecko Pro API key (required for all CoinGecko API tools)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (required for AI-powered tool selection)

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

# Anthropic API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
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
from tools.top_coins import get_top_coins
from tools.coins_gainers_losers import get_top_gainers_losers

# Get top 100 coins
top_coins = get_top_coins(n=100, include_extra_data=True)

# Get market performance
performance = get_top_gainers_losers()
```

### Historical Analysis
```python
from tools.coin_historical_chart_by_id import get_coin_historical_chart_by_id
chart_data = get_coin_historical_chart_by_id('bitcoin', 'usd', 30)
```

### Technical Analysis
```python
from tools.coin_ohlc_by_id import get_coin_ohlc_by_id
ohlc_data = get_coin_ohlc_by_id('bitcoin', 'usd', 30)
```

## Error Handling

All tools include:
- Retry logic (3 attempts by default)
- Comprehensive error handling
- Connection timeout protection (15 seconds)
- Clear error messages
- CLI error output with descriptive messages

## Performance Notes

- All tools implement efficient API usage
- Rate limiting is handled automatically
- Data is returned in optimized formats (DataFrame where appropriate)
- Error handling includes retry mechanisms
- CLI tools support both JSON and CSV output for flexibility

## Testing

All tools include comprehensive test suites located in `/tools/test/`:
- Unit tests for individual functions
- Integration tests for API interactions
- Error handling tests
- Performance tests
- CLI functionality tests

## Maintenance

This tools list is automatically maintained. When adding new tools:
1. Add the tool to the appropriate category
2. Update the tool categories summary
3. Add usage examples if needed
4. Update environment variables if required
5. Add corresponding test files
6. Include CLI interface with proper help text
7. Support both JSON and CSV output formats

## Quick Reference

### Most Commonly Used Tools:
- `top_coins.py` - Get top cryptocurrencies
- `coin_data_by_id.py` - Get detailed coin information
- `coin_ohlc_by_id.py` - Get OHLC data for technical analysis
- `coins_gainers_losers.py` - Get market performance

### For Technical Analysis:
- `coin_ohlc_by_id.py` - OHLC data
- `coin_historical_chart_by_id.py` - Historical price charts
- `coin_historical_chart_range_by_id.py` - Custom time ranges
- `coingecko.py` - Advanced OHLC data with pagination

### For Market Analysis:
- `top_coins.py` - Market cap rankings
- `coins_gainers_losers.py` - Market performance
- `coins_list_market_data.py` - Bulk market data
- `dex_volume_ranking.py` - DEX volume analysis

### CLI Quick Commands:
```bash
# Get top 10 coins
python tools/top_coins.py --n 10

# Get Bitcoin data
python tools/coin_data_by_id.py --coin_id bitcoin

# Get OHLC data
python tools/coin_ohlc_by_id.py --coin_id bitcoin --days 30

# Get market performance
python tools/coins_gainers_losers.py

# Get DEX rankings
python tools/dex_volume_ranking.py 10 