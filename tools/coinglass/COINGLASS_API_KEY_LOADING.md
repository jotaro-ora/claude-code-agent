# CoinGlass API Key Loading Configuration

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

#### CoinGlass API Key
- **Environment Variable**: `COINGLASS_API_KEY`
- **Required For**: All CoinGlass API tools
- **Usage**: `os.getenv("COINGLASS_API_KEY")`
- **Header Format**: `{"CG-API-KEY": os.getenv("COINGLASS_API_KEY")}`

**Tools using CoinGlass API (45 endpoints):**
- `futures_supported_coins.py` – Futures: Supported Coins
- `futures_supported_exchange_pairs.py` – Futures: Supported Exchanges & Pairs
- `futures_coins_markets.py` – Futures Coin Markets
- `futures_pairs_markets.py` – Futures Pair Markets
- `futures_price_change_list.py` – Futures Price Change List
- `futures_price_ohlc_history.py` – Futures Price OHLC History
- `open_interest_ohlc_history.py` – Open‑Interest OHLC History
- `open_interest_aggregated_ohlc_history.py` – Aggregated OI OHLC History
- `open_interest_aggregated_stablecoin_ohlc_history.py` – Aggregated Stable‑Coin OI OHLC
- `open_interest_aggregated_coin_margin_ohlc_history.py` – Aggregated Coin‑Margin OI OHLC
- `open_interest_exchange_list.py` – OI by Exchange List
- `open_interest_exchange_history_chart.py` – OI Chart by Exchange
- `funding_rate_ohlc_history.py` – Funding‑Rate OHLC History
- `funding_rate_oi_weight_ohlc_history.py` – OI‑Weighted Funding‑Rate OHLC
- `funding_rate_vol_weight_ohlc_history.py` – Volume‑Weighted Funding‑Rate OHLC
- `funding_rate_exchange_list.py` – Funding‑Rate by Exchange List
- `funding_rate_cumulative_exchange_list.py` – Cumulative Funding‑Rate List
- `funding_rate_arbitrage.py` – Funding Arbitrage Opportunities
- `long_short_global_account_ratio_history.py` – Global Long/Short Account Ratio
- `long_short_top_account_ratio_history.py` – Top‑Trader Long/Short Account Ratio
- `long_short_top_position_ratio_history.py` – Top‑Trader Position Ratio
- `taker_buy_sell_exchange_ratio.py` – Exchange Taker Buy/Sell Ratio
- `liquidation_pair_history.py` – Pair Liquidation History
- `liquidation_coin_history.py` – Coin Liquidation History
- `liquidation_coin_list.py` – Liquidation Coin List
- `liquidation_exchange_list.py` – Liquidation Exchange List
- `liquidation_order.py` – Liquidation Order Detail
- `liquidation_pair_heatmap_model1.py` – Pair Liquidation Heatmap (Model 1)
- `liquidation_pair_heatmap_model2.py` – Pair Liquidation Heatmap (Model 2)
- `liquidation_pair_heatmap_model3.py` – Pair Liquidation Heatmap (Model 3)
- `liquidation_coin_heatmap_model1.py` – Coin Liquidation Heatmap (Model 1)
- `liquidation_coin_heatmap_model2.py` – Coin Liquidation Heatmap (Model 2)
- `liquidation_coin_heatmap_model3.py` – Coin Liquidation Heatmap (Model 3)
- `liquidation_pair_map.py` – Pair Liquidation Map
- `liquidation_coin_map.py` – Coin Liquidation Map
- `orderbook_pair_ask_bids_history.py` – Pair Order‑Book Bid/Ask
- `orderbook_coin_ask_bids_history.py` – Coin Aggregated Order‑Book Bid/Ask
- `orderbook_heatmap_history.py` – Order‑Book Heatmap
- `orderbook_large_limit_order.py` – Large Order‑Book Snapshot
- `orderbook_large_limit_order_history.py` – Large Order‑Book History
- `whale_hyperliquid_alert.py` – Hyperliquid Whale Alert
- `whale_hyperliquid_position.py` – Hyperliquid Whale Position
- `pair_taker_buy_sell_volume_history.py` – Pair Taker Buy/Sell History
- `coin_taker_buy_sell_volume_history.py` – Coin Taker Buy/Sell History
- `spot_supported_coins.py` – Spot: Supported Coins
- `spot_supported_exchange_pairs.py` – Spot: Supported Exchanges & Pairs
- `index_fear_greed_history.py` – Crypto Fear & Greed Index

## .env File Structure

The `.env` file should be located in the project root directory with the following structure:

```env
# CoinGlass API Configuration
COINGLASS_API_KEY=your_coinglass_api_key_here

# Other API keys can be added here as needed
```

## Directory Structure

```
OMNIAPI/
├── .env                         # ← API keys are loaded from here
├── tools/
│   ├── coinglass/               # CoinGlass integrations
│   │   ├── futures_supported_coins.py
│   │   ├── futures_supported_exchange_pairs.py
│   │   ├── futures_coins_markets.py
│   │   ├── futures_pairs_markets.py
│   │   ├── futures_price_change_list.py
│   │   ├── futures_price_ohlc_history.py
│   │   ├── open_interest_ohlc_history.py
│   │   ├── open_interest_aggregated_ohlc_history.py
│   │   ├── open_interest_aggregated_stablecoin_ohlc_history.py
│   │   ├── open_interest_aggregated_coin_margin_ohlc_history.py
│   │   ├── open_interest_exchange_list.py
│   │   ├── open_interest_exchange_history_chart.py
│   │   ├── funding_rate_ohlc_history.py
│   │   ├── funding_rate_oi_weight_ohlc_history.py
│   │   ├── funding_rate_vol_weight_ohlc_history.py
│   │   ├── funding_rate_exchange_list.py
│   │   ├── funding_rate_cumulative_exchange_list.py
│   │   ├── funding_rate_arbitrage.py
│   │   ├── long_short_global_account_ratio_history.py
│   │   ├── long_short_top_account_ratio_history.py
│   │   ├── long_short_top_position_ratio_history.py
│   │   ├── taker_buy_sell_exchange_ratio.py
│   │   ├── liquidation_pair_history.py
│   │   ├── liquidation_coin_history.py
│   │   ├── liquidation_coin_list.py
│   │   ├── liquidation_exchange_list.py
│   │   ├── liquidation_order.py
│   │   ├── liquidation_pair_map.py
│   │   ├── liquidation_coin_map.py
│   │   ├── orderbook_pair_ask_bids_history.py
│   │   ├── orderbook_coin_ask_bids_history.py
│   │   ├── orderbook_heatmap_history.py
│   │   ├── orderbook_large_limit_order.py
│   │   ├── orderbook_large_limit_order_history.py
│   │   ├── whale_hyperliquid_alert.py
│   │   ├── whale_hyperliquid_position.py
│   │   ├── pair_taker_buy_sell_volume_history.py
│   │   ├── coin_taker_buy_sell_volume_history.py
│   │   ├── spot_supported_coins.py
│   │   ├── spot_supported_exchange_pairs.py
│   │   └── index_fear_greed_history.py
│   └── ...
└── ...
```

## Usage Examples

### Basic Usage
```python
# Import any tool – API keys are automatically loaded
from tools.coinglass.futures_supported_coins import get_futures_supported_coins

# Tools will automatically use the API keys from .env
coins = get_futures_supported_coins()
```

### Verification
```python
import os
from dotenv import load_dotenv

# Load environment variables
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

# Check if API keys are loaded
print('COINGLASS_API_KEY:', 'Loaded' if os.getenv('COINGLASS_API_KEY') else 'Not found')
```

## Error Handling

All tools include proper error handling for missing API keys:

### CoinGlass Tools
```python
headers = {"CG-API-KEY": os.getenv("COINGLASS_API_KEY")}
if headers["CG-API-KEY"] is None:
    raise EnvironmentError(
        "COINGLASS_API_KEY not found. "
        "Please add it to your .env file in the project root."
    )
```

## Best Practices

1. **Never commit API keys**: Ensure `.env` is in `.gitignore`
2. **Use environment variables**: Always use `os.getenv()` instead of hard‑coding
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
- Use environment variables instead of hard‑coded values
- Regularly rotate API keys for security
- Monitor API usage for unusual activity
