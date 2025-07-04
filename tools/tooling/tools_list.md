# Tools Directory - Tools List

This document provides a comprehensive list of all tools available in the `/tools/` directory. This list is maintained for AI agents to quickly understand and query available functionality.

**🖥️ CLI Support**: All tools that connect to external APIs support command-line interface (CLI) usage for direct testing and integration.

## Table of Contents

1. [Core CoinGecko API Tools](#core-coingecko-api-tools)
2. [CoinGlass API Tools](#coinglass-api-tools)
3. [LunaCrush API Tools](#lunacrush-api-tools)
4. [Utility Tools](#utility-tools)
5. [Environment Configuration](#environment-configuration)
6. [Tool Categories Summary](#tool-categories-summary)
7. [Usage Patterns](#usage-patterns)
8. [Quick Reference](#quick-reference)
9. [Technical Information](#technical-information)

---

## Core CoinGecko API Tools

### Basic Market Data

#### 1. coingecko.py
**Purpose**: Core CoinGecko API wrapper with comprehensive functionality
**Main Function**: `get_coingecko_ohlc(symbol, interval, start_time, end_time)`
**Description**: Provides access to CoinGecko Pro API with support for historical OHLC data retrieval
**Usage**: `from tools.coingecko import get_coingecko_ohlc`
**CLI Usage**:
```bash
python tools/coingecko.py --symbol BTC_USD --interval 1d --start_time 2023-01-01 --end_time 2023-01-31
python tools/coingecko.py --symbol ETH_USD --interval 1h --start_time 2023-12-01 --end_time 2023-12-07 --output_format csv
```

#### 2. top_coins.py
**Purpose**: Get top N cryptocurrency symbols by market cap
**Main Function**: `get_top_coins(n=10, include_extra_data=False)`
**Description**: Fetches the top N cryptocurrencies by market capitalization and returns their symbols or detailed data
**Usage**: `from tools.top_coins import get_top_coins`
**CLI Usage**:
```bash
python tools/top_coins.py --n 10
python tools/top_coins.py --n 50 --include_extra_data --output_format json
```

#### 3. volume_data.py
**Purpose**: Get trading volume data for specified cryptocurrencies
**Main Function**: `get_volume_data(symbols)`
**Description**: Fetches trading volume data for a list of cryptocurrency symbols
**Usage**: `from tools.volume_data import get_volume_data`

### Coin Information

#### 4. coin_data_by_id.py
**Purpose**: Get detailed data for a specific coin by ID
**Main Function**: `get_coin_data_by_id(coin_id, localization='false', tickers='true', market_data='true', community_data='true', developer_data='true', sparkline='false')`
**Description**: Fetches comprehensive data for a specific cryptocurrency including market data, community data, and developer data
**Usage**: `from tools.coin_data_by_id import get_coin_data_by_id`
**CLI Usage**:
```bash
python tools/coin_data_by_id.py --coin_id bitcoin
python tools/coin_data_by_id.py --coin_id ethereum --market_data false --sparkline true
```

#### 5. coin_tickers_by_id.py
**Purpose**: Get ticker data for a specific coin by ID
**Main Function**: `get_coin_tickers_by_id(coin_id, exchange_ids=None, include_exchange_logo=False, page=1, order=None, depth=False)`
**Description**: Fetches ticker information for a specific cryptocurrency from various exchanges
**Usage**: `from tools.coin_tickers_by_id import get_coin_tickers_by_id`
**CLI Usage**:
```bash
python tools/coin_tickers_by_id.py --coin_id bitcoin
python tools/coin_tickers_by_id.py --coin_id ethereum --include_exchange_logo --output_format csv
```

### Historical Data

#### 6. coin_historical_data_by_id.py
**Purpose**: Get historical data for a specific coin by ID and date
**Main Function**: `get_coin_historical_data_by_id(coin_id, date, localization='false')`
**Description**: Fetches historical data for a specific cryptocurrency on a given date
**Usage**: `from tools.coin_historical_data_by_id import get_coin_historical_data_by_id`
**CLI Usage**:
```bash
python tools/coin_historical_data_by_id.py --coin_id bitcoin --date 30-12-2017
python tools/coin_historical_data_by_id.py --coin_id ethereum --date 01-01-2020 --localization true
```

#### 7. coin_historical_chart_by_id.py
**Purpose**: Get historical chart data for a specific coin by ID
**Main Function**: `get_coin_historical_chart_by_id(coin_id, vs_currency='usd', days=30, interval=None)`
**Description**: Fetches historical price chart data for a specific cryptocurrency over a specified time period
**Usage**: `from tools.coin_historical_chart_by_id import get_coin_historical_chart_by_id`
**CLI Usage**:
```bash
python tools/coin_historical_chart_by_id.py --coin_id bitcoin --days 30
python tools/coin_historical_chart_by_id.py --coin_id ethereum --vs_currency usd --days 7 --interval daily
```

#### 8. coin_historical_chart_range_by_id.py
**Purpose**: Get historical chart data within a specific time range
**Main Function**: `get_coin_historical_chart_range_by_id(coin_id, vs_currency='usd', from_timestamp=None, to_timestamp=None)`
**Description**: Fetches historical price chart data for a specific cryptocurrency within a custom time range
**Usage**: `from tools.coin_historical_chart_range_by_id import get_coin_historical_chart_range_by_id`
**CLI Usage**:
```bash
python tools/coin_historical_chart_range_by_id.py --coin_id bitcoin --from_timestamp 1609459200 --to_timestamp 1640995200
python tools/coin_historical_chart_range_by_id.py --coin_id ethereum --vs_currency usd --from_timestamp 1609459200 --to_timestamp 1640995200
```

### OHLC Data

#### 9. coin_ohlc_by_id.py
**Purpose**: Get OHLC (Open, High, Low, Close) data for a specific coin by ID
**Main Function**: `get_coin_ohlc_by_id(coin_id, vs_currency='usd', days=30)`
**Description**: Fetches OHLC chart data for a specific cryptocurrency over a specified time period
**Usage**: `from tools.coin_ohlc_by_id import get_coin_ohlc_by_id`
**CLI Usage**:
```bash
python tools/coin_ohlc_by_id.py --coin_id bitcoin --days 30
python tools/coin_ohlc_by_id.py --coin_id ethereum --vs_currency usd --days 7
```

#### 10. coin_ohlc_range_by_id.py
**Purpose**: Get OHLC data within a specific time range
**Main Function**: `get_coin_ohlc_range_by_id(coin_id, vs_currency='usd', from_timestamp=None, to_timestamp=None, interval=None)`
**Description**: Fetches OHLC chart data for a specific cryptocurrency within a custom time range
**Usage**: `from tools.coin_ohlc_range_by_id import get_coin_ohlc_range_by_id`
**CLI Usage**:
```bash
python tools/coin_ohlc_range_by_id.py --coin_id bitcoin --from_timestamp 1609459200 --to_timestamp 1640995200
python tools/coin_ohlc_range_by_id.py --coin_id ethereum --vs_currency usd --from_timestamp 1609459200 --to_timestamp 1640995200 --interval daily
```

### Market Data

#### 11. coins_list.py
**Purpose**: Get the complete list of supported coins
**Main Function**: `get_coins_list(include_inactive=False)`
**Description**: Fetches the full list of all cryptocurrencies supported by CoinGecko
**Usage**: `from tools.coins_list import get_coins_list`
**CLI Usage**:
```bash
python tools/coins_list.py
python tools/coins_list.py --include_inactive --output_format json --limit 100
```

#### 12. coins_list_market_data.py
**Purpose**: Get market data for a list of coins
**Main Function**: `get_coins_list_market_data(vs_currency='usd', order='market_cap_desc', per_page=100, page=1, sparkline=False, price_change_percentage=None)`
**Description**: Fetches market data for multiple cryptocurrencies with various filtering and sorting options
**Usage**: `from tools.coins_list_market_data import get_coins_list_market_data`
**CLI Usage**:
```bash
python tools/coins_list_market_data.py --vs_currency usd --per_page 10
python tools/coins_list_market_data.py --vs_currency usd --order market_cap_desc --per_page 50 --output_format csv
```

#### 13. coins_gainers_losers.py
**Purpose**: Get top gainers and losers in the market
**Main Function**: `get_top_gainers_losers(vs_currency='usd')`
**Description**: Fetches the top performing and worst performing cryptocurrencies in the market
**Usage**: `from tools.coins_gainers_losers import get_top_gainers_losers`
**CLI Usage**:
```bash
python tools/coins_gainers_losers.py
python tools/coins_gainers_losers.py --vs_currency eur --output_format json
```

---

## CoinGlass API Tools

### Funding & Derivatives

#### 16. coinglass/funding_rate_arbitrage.py
**Purpose**: Fetch funding rate arbitrage opportunities from CoinGlass API
**Main Function**: `get_funding_rate_arbitrage(symbol="BTC")`
**Description**: Retrieves funding rate differences across exchanges for arbitrage opportunities
**Usage**: `from tools.coinglass.funding_rate_arbitrage import get_funding_rate_arbitrage`
**CLI Usage**:
```bash
python coinglass/funding_rate_arbitrage.py --symbol BTC
python coinglass/funding_rate_arbitrage.py --symbol ETH --output_format csv
```

#### 17. coinglass/funding_rate_exchange_list.py
**Purpose**: Get funding rate exchange list from CoinGlass API
**Main Function**: `get_funding_rate_exchange_list(symbol="BTC")`
**Description**: Retrieves list of exchanges offering funding rates for specific cryptocurrencies
**Usage**: `from tools.coinglass.funding_rate_exchange_list import get_funding_rate_exchange_list`
**CLI Usage**:
```bash
python coinglass/funding_rate_exchange_list.py --symbol BTC
python coinglass/funding_rate_exchange_list.py --symbol ETH --output_format csv
```

#### 18. coinglass/funding_rate_oi_weight_ohlc_history.py
**Purpose**: Fetch OI-weighted funding rate OHLC history from CoinGlass API
**Main Function**: `get_funding_rate_oi_weight_ohlc_history(symbol="BTC", interval="1h", start_time=None, end_time=None)`
**Description**: Retrieves open interest weighted funding rate OHLC historical data for technical analysis
**Usage**: `from tools.coinglass.funding_rate_oi_weight_ohlc_history import get_funding_rate_oi_weight_ohlc_history`
**CLI Usage**:
```bash
python coinglass/funding_rate_oi_weight_ohlc_history.py --symbol BTC --interval 1h
python coinglass/funding_rate_oi_weight_ohlc_history.py --symbol ETH --interval 4h --output_format csv
```

#### 19. coinglass/funding_rate_vol_weight_ohlc_history.py
**Purpose**: Fetch volume-weighted funding rate OHLC history from CoinGlass API
**Main Function**: `get_funding_rate_vol_weight_ohlc_history(symbol="BTC", interval="1h", start_time=None, end_time=None)`
**Description**: Retrieves volume weighted funding rate OHLC historical data for technical analysis
**Usage**: `from tools.coinglass.funding_rate_vol_weight_ohlc_history import get_funding_rate_vol_weight_ohlc_history`
**CLI Usage**:
```bash
python coinglass/funding_rate_vol_weight_ohlc_history.py --symbol BTC --interval 1h
python coinglass/funding_rate_vol_weight_ohlc_history.py --symbol ETH --interval 4h --output_format csv
```

### Futures Market Data

#### 20. coinglass/futures_supported_coins.py
**Purpose**: Get supported futures coins from CoinGlass API
**Main Function**: `get_futures_supported_coins()`
**Description**: Retrieves list of all cryptocurrencies supported for futures trading
**Usage**: `from tools.coinglass.futures_supported_coins import get_futures_supported_coins`
**CLI Usage**:
```bash
python coinglass/futures_supported_coins.py
python coinglass/futures_supported_coins.py --output_format csv
```

#### 21. coinglass/futures_pairs_markets.py
**Purpose**: Get futures pair markets data from CoinGlass API
**Main Function**: `get_futures_pairs_markets(symbol="BTC")`
**Description**: Retrieves futures trading pairs and market information for cryptocurrencies
**Usage**: `from tools.coinglass.futures_pairs_markets import get_futures_pairs_markets`
**CLI Usage**:
```bash
python coinglass/futures_pairs_markets.py --symbol BTC
python coinglass/futures_pairs_markets.py --symbol ETH --output_format csv
```

#### 22. coinglass/futures_supported_exchange_pairs.py
**Purpose**: Get supported futures exchange pairs from CoinGlass API
**Main Function**: `get_futures_supported_exchange_pairs()`
**Description**: Retrieves list of all supported futures exchange pairs and their configurations
**Usage**: `from tools.coinglass.futures_supported_exchange_pairs import get_futures_supported_exchange_pairs`
**CLI Usage**:
```bash
python coinglass/futures_supported_exchange_pairs.py
python coinglass/futures_supported_exchange_pairs.py --output_format csv
```

### Open Interest Analysis

#### 23. coinglass/open_interest_exchange_list.py
**Purpose**: Get open interest exchange list from CoinGlass API
**Main Function**: `get_open_interest_exchange_list(symbol="BTC")`
**Description**: Retrieves list of exchanges with open interest data for cryptocurrencies
**Usage**: `from tools.coinglass.open_interest_exchange_list import get_open_interest_exchange_list`
**CLI Usage**:
```bash
python coinglass/open_interest_exchange_list.py --symbol BTC
python coinglass/open_interest_exchange_list.py --symbol ETH --output_format csv
```

#### 24. coinglass/open_interest_aggregated_ohlc_history.py
**Purpose**: Get aggregated open interest OHLC history from CoinGlass API
**Main Function**: `get_open_interest_aggregated_ohlc_history(symbol="BTC", interval="1h", start_time=None, end_time=None)`
**Description**: Retrieves aggregated open interest OHLC historical data across exchanges
**Usage**: `from tools.coinglass.open_interest_aggregated_ohlc_history import get_open_interest_aggregated_ohlc_history`
**CLI Usage**:
```bash
python coinglass/open_interest_aggregated_ohlc_history.py --symbol BTC --interval 1h
python coinglass/open_interest_aggregated_ohlc_history.py --symbol ETH --interval 4h --output_format csv
```

#### 25. coinglass/open_interest_aggregated_coin_margin_ohlc_history.py
**Purpose**: Get aggregated coin margin open interest OHLC history from CoinGlass API
**Main Function**: `get_open_interest_aggregated_coin_margin_ohlc_history(symbol="BTC", interval="1h", start_time=None, end_time=None)`
**Description**: Retrieves aggregated open interest OHLC data for coin margin trading
**Usage**: `from tools.coinglass.open_interest_aggregated_coin_margin_ohlc_history import get_open_interest_aggregated_coin_margin_ohlc_history`
**CLI Usage**:
```bash
python coinglass/open_interest_aggregated_coin_margin_ohlc_history.py --symbol BTC --interval 1h
python coinglass/open_interest_aggregated_coin_margin_ohlc_history.py --symbol ETH --interval 4h --output_format csv
```

#### 26. coinglass/open_interest_aggregated_stablecoin_ohlc_history.py
**Purpose**: Get aggregated stablecoin open interest OHLC history from CoinGlass API
**Main Function**: `get_open_interest_aggregated_stablecoin_ohlc_history(symbol="BTC", interval="1h", start_time=None, end_time=None)`
**Description**: Retrieves aggregated stablecoin-denominated open interest OHLC data
**Usage**: `from tools.coinglass.open_interest_aggregated_stablecoin_ohlc_history import get_open_interest_aggregated_stablecoin_ohlc_history`
**CLI Usage**:
```bash
python coinglass/open_interest_aggregated_stablecoin_ohlc_history.py --symbol BTC --interval 1h
python coinglass/open_interest_aggregated_stablecoin_ohlc_history.py --symbol ETH --interval 4h --output_format csv
```

### Liquidation Analysis

#### 27. coinglass/liquidation_coin_list.py
**Purpose**: Get liquidation coin list from CoinGlass API
**Main Function**: `get_liquidation_coin_list()`
**Description**: Retrieves list of cryptocurrencies with available liquidation data
**Usage**: `from tools.coinglass.liquidation_coin_list import get_liquidation_coin_list`
**CLI Usage**:
```bash
python coinglass/liquidation_coin_list.py
python coinglass/liquidation_coin_list.py --output_format csv
```

#### 28. coinglass/liquidation_coin_history.py
**Purpose**: Get coin liquidation history from CoinGlass API
**Main Function**: `get_liquidation_coin_history(symbol="BTC", interval="1h")`
**Description**: Retrieves historical liquidation data for specific cryptocurrencies
**Usage**: `from tools.coinglass.liquidation_coin_history import get_liquidation_coin_history`
**CLI Usage**:
```bash
python coinglass/liquidation_coin_history.py --symbol BTC --interval 1h
python coinglass/liquidation_coin_history.py --symbol ETH --interval 4h --output_format csv
```

#### 29. coinglass/liquidation_exchange_list.py
**Purpose**: Get liquidation exchange list from CoinGlass API
**Main Function**: `get_liquidation_exchange_list()`
**Description**: Retrieves list of exchanges with available liquidation data
**Usage**: `from tools.coinglass.liquidation_exchange_list import get_liquidation_exchange_list`
**CLI Usage**:
```bash
python coinglass/liquidation_exchange_list.py
python coinglass/liquidation_exchange_list.py --output_format csv
```

#### 30. coinglass/liquidation_order.py
**Purpose**: Get liquidation order details from CoinGlass API
**Main Function**: `get_liquidation_order(symbol="BTC", limit=100)`
**Description**: Retrieves detailed liquidation order information for specific cryptocurrencies
**Usage**: `from tools.coinglass.liquidation_order import get_liquidation_order`
**CLI Usage**:
```bash
python coinglass/liquidation_order.py --symbol BTC --limit 50
python coinglass/liquidation_order.py --symbol ETH --limit 100 --output_format csv
```

#### 31. coinglass/liquidation_pair_map.py
**Purpose**: Get liquidation pair mapping from CoinGlass API
**Main Function**: `get_liquidation_pair_map()`
**Description**: Retrieves mapping of liquidation pairs and their configurations
**Usage**: `from tools.coinglass.liquidation_pair_map import get_liquidation_pair_map`
**CLI Usage**:
```bash
python coinglass/liquidation_pair_map.py
python coinglass/liquidation_pair_map.py --output_format csv
```

### Volume & Trading Analysis

#### 32. coinglass/coin_taker_buy_sell_volume_history.py
**Purpose**: Fetch coin taker buy/sell volume history from CoinGlass API
**Main Function**: `get_coin_taker_buy_sell_volume_history(symbol="BTC", interval="1h", exchange_list="Binance,OKX,Bybit", start_time=None, end_time=None)`
**Description**: Retrieves historical taker buy/sell volume data for cryptocurrencies across major exchanges
**Usage**: `from tools.coinglass.coin_taker_buy_sell_volume_history import get_coin_taker_buy_sell_volume_history`
**CLI Usage**:
```bash
python coinglass/coin_taker_buy_sell_volume_history.py --symbol BTC
python coinglass/coin_taker_buy_sell_volume_history.py --symbol ETH --interval 4h --output_format csv
```

#### 33. coinglass/taker_buy_sell_exchange_ratio.py
**Purpose**: Get taker buy/sell exchange ratio from CoinGlass API
**Main Function**: `get_taker_buy_sell_exchange_ratio(symbol="BTC")`
**Description**: Retrieves taker buy/sell ratio data across exchanges for market sentiment analysis
**Usage**: `from tools.coinglass.taker_buy_sell_exchange_ratio import get_taker_buy_sell_exchange_ratio`
**CLI Usage**:
```bash
python coinglass/taker_buy_sell_exchange_ratio.py --symbol BTC
python coinglass/taker_buy_sell_exchange_ratio.py --symbol ETH --output_format csv
```

### Spot Market Data

#### 34. coinglass/spot_supported_coins.py
**Purpose**: Get supported spot coins from CoinGlass API
**Main Function**: `get_spot_supported_coins()`
**Description**: Retrieves list of all cryptocurrencies supported for spot trading
**Usage**: `from tools.coinglass.spot_supported_coins import get_spot_supported_coins`
**CLI Usage**:
```bash
python coinglass/spot_supported_coins.py
python coinglass/spot_supported_coins.py --output_format csv
```

#### 35. coinglass/spot_supported_exchange_pairs.py
**Purpose**: Get supported spot exchange pairs from CoinGlass API
**Main Function**: `get_spot_supported_exchange_pairs()`
**Description**: Retrieves list of all supported spot exchange pairs and their configurations
**Usage**: `from tools.coinglass.spot_supported_exchange_pairs import get_spot_supported_exchange_pairs`
**CLI Usage**:
```bash
python coinglass/spot_supported_exchange_pairs.py
python coinglass/spot_supported_exchange_pairs.py --output_format csv
```

### Whale & Large Trader Analysis

#### 36. coinglass/whale_hyperliquid_alert.py
**Purpose**: Get Hyperliquid whale alerts from CoinGlass API
**Main Function**: `get_whale_hyperliquid_alert(limit=100)`
**Description**: Retrieves whale trading alerts from Hyperliquid exchange for large transaction monitoring
**Usage**: `from tools.coinglass.whale_hyperliquid_alert import get_whale_hyperliquid_alert`
**CLI Usage**:
```bash
python coinglass/whale_hyperliquid_alert.py --limit 50
python coinglass/whale_hyperliquid_alert.py --limit 100 --output_format csv
```

#### 37. coinglass/whale_hyperliquid_position.py
**Purpose**: Get Hyperliquid whale positions from CoinGlass API
**Main Function**: `get_whale_hyperliquid_position(limit=100)`
**Description**: Retrieves whale position data from Hyperliquid exchange for large holder analysis
**Usage**: `from tools.coinglass.whale_hyperliquid_position import get_whale_hyperliquid_position`
**CLI Usage**:
```bash
python coinglass/whale_hyperliquid_position.py --limit 50
python coinglass/whale_hyperliquid_position.py --limit 100 --output_format csv
```

### Market Sentiment

#### 38. coinglass/index_fear_greed_history.py
**Purpose**: Get fear & greed index history from CoinGlass API
**Main Function**: `get_index_fear_greed_history(interval="1d")`
**Description**: Retrieves historical fear & greed index data for market sentiment analysis
**Usage**: `from tools.coinglass.index_fear_greed_history import get_index_fear_greed_history`
**CLI Usage**:
```bash
python coinglass/index_fear_greed_history.py --interval 1d
python coinglass/index_fear_greed_history.py --interval 1h --output_format csv
```

---

## LunaCrush API Tools

### Coin Social Analytics

#### 39. lunacrush/coins_list.py
**Purpose**: Get list of all supported coins from LunarCrush API
**Main Function**: `get_coins_list(limit=50, sort="gs", desc=True)`
**Description**: Retrieves comprehensive list of cryptocurrencies with LunarCrush metrics including Galaxy Score and social data
**Usage**: `from tools.lunacrush.coins_list import get_coins_list`
**CLI Usage**:
```bash
python lunacrush/coins_list.py --limit 100 --sort mc
python lunacrush/coins_list.py --limit 50 --sort gs --desc false --output_format csv
```

#### 40. lunacrush/coin_meta.py
**Purpose**: Get detailed coin metadata from LunarCrush API
**Main Function**: `get_coin_meta(coin_identifier, interval="1d", data_points=30)`
**Description**: Retrieves comprehensive 60+ metrics for specific cryptocurrencies including social sentiment and market data
**Usage**: `from tools.lunacrush.coin_meta import get_coin_meta`
**CLI Usage**:
```bash
python lunacrush/coin_meta.py --coin_identifier bitcoin --interval 1d
python lunacrush/coin_meta.py --coin_identifier BTC --interval 1h --data_points 24 --output_format csv
```

#### 41. lunacrush/coin_time_series.py
**Purpose**: Get historical coin data from LunarCrush API
**Main Function**: `get_coin_time_series(coin_identifier, interval="1d", data_points=30, metrics=None)`
**Description**: Retrieves time-series data for cryptocurrencies with social and price metrics
**Usage**: `from tools.lunacrush.coin_time_series import get_coin_time_series`
**CLI Usage**:
```bash
python lunacrush/coin_time_series.py --coin_identifier bitcoin --interval 1d --data_points 30
python lunacrush/coin_time_series.py --coin_identifier ETH --interval 1h --data_points 24 --output_format csv
```

### Category Analytics

#### 42. lunacrush/category_details.py
**Purpose**: Get category snapshot metrics from LunarCrush API
**Main Function**: `get_category_details(category, time_frame="24h")`
**Description**: Retrieves current metrics and analytics for cryptocurrency categories
**Usage**: `from tools.lunacrush.category_details import get_category_details`
**CLI Usage**:
```bash
python lunacrush/category_details.py --category defi --time_frame 24h
python lunacrush/category_details.py --category nft --time_frame 7d --output_format csv
```

#### 43. lunacrush/category_time_series.py
**Purpose**: Get historical category data from LunarCrush API
**Main Function**: `get_category_time_series(category, interval="1d", data_points=30)`
**Description**: Retrieves time-series data for cryptocurrency categories with social and market metrics
**Usage**: `from tools.lunacrush.category_time_series import get_category_time_series`
**CLI Usage**:
```bash
python lunacrush/category_time_series.py --category defi --interval 1d --data_points 30
python lunacrush/category_time_series.py --category nft --interval 1h --data_points 24 --output_format csv
```

### Topic Analytics

#### 44. lunacrush/topic_details.py
**Purpose**: Get topic aggregate metrics from LunarCrush API
**Main Function**: `get_topic_details(topic, time_frame="24h")`
**Description**: Retrieves social media metrics and analytics for specific cryptocurrency topics
**Usage**: `from tools.lunacrush.topic_details import get_topic_details`
**CLI Usage**:
```bash
python lunacrush/topic_details.py --topic bitcoin --time_frame 24h
python lunacrush/topic_details.py --topic defi --time_frame 7d --output_format csv
```

#### 45. lunacrush/topic_time_series.py
**Purpose**: Get historical topic data from LunarCrush API
**Main Function**: `get_topic_time_series(topic, interval="1d", data_points=30)`
**Description**: Retrieves time-series data for cryptocurrency topics with social sentiment metrics
**Usage**: `from tools.lunacrush.topic_time_series import get_topic_time_series`
**CLI Usage**:
```bash
python lunacrush/topic_time_series.py --topic bitcoin --interval 1d --data_points 30
python lunacrush/topic_time_series.py --topic defi --interval 1h --data_points 24 --output_format csv
```

### Social Media Content

#### 46. lunacrush/topic_news.py
**Purpose**: Get news articles for topics from LunarCrush API
**Main Function**: `get_topic_news(topic, limit=20, time_frame="24h", sort_by="time")`
**Description**: Retrieves latest news articles related to specific cryptocurrency topics
**Usage**: `from tools.lunacrush.topic_news import get_topic_news`
**CLI Usage**:
```bash
python lunacrush/topic_news.py --topic bitcoin --limit 10
python lunacrush/topic_news.py --topic defi --limit 20 --time_frame 7d --output_format csv
```

#### 47. lunacrush/topic_creators.py
**Purpose**: Get top creators/influencers for topics from LunarCrush API
**Main Function**: `get_topic_creators(topic, limit=10, time_frame="24h", sort_by="influence")`
**Description**: Retrieves top social media creators and influencers for specific cryptocurrency topics
**Usage**: `from tools.lunacrush.topic_creators import get_topic_creators`
**CLI Usage**:
```bash
python lunacrush/topic_creators.py --topic bitcoin --limit 10
python lunacrush/topic_creators.py --topic defi --limit 20 --time_frame 7d --sort_by engagement --output_format csv
```

#### 48. lunacrush/topic_posts.py
**Purpose**: Get social media posts for topics from LunarCrush API
**Main Function**: `get_topic_posts(topic, limit=20, time_frame="24h", sort_by="engagement")`
**Description**: Retrieves top social media posts for specific cryptocurrency topics
**Usage**: `from tools.lunacrush.topic_posts import get_topic_posts`
**CLI Usage**:
```bash
python lunacrush/topic_posts.py --topic bitcoin --limit 20
python lunacrush/topic_posts.py --topic defi --limit 30 --time_frame 7d --sort_by time --output_format csv
```

---

## Utility Tools

### DEX Volume Analysis

#### 14. dex_volume_ranking.py
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

### AI-Powered Tool Selection

#### 15. tool_selector.py
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

---

## Environment Configuration

**Important**: All tools automatically load API keys from the project root directory's `.env` file. 
The tools are configured to look for the `.env` file in the project root, regardless of where they are called from.

### Required Environment Variables

#### Core APIs
- `COINGECKO_API_KEY`: Your CoinGecko Pro API key (required for all CoinGecko API tools)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (required for AI-powered tool selection)

#### Additional APIs
- `COINGLASS_API_KEY`: Your CoinGlass API key (required for all CoinGlass tools)
- `LUNA_CRUSH_API_KEY`: Your LunarCrush API key (required for all LunaCrush tools)

### .env File Location
```
claude-code-agent/
├── .env                    # ← API keys are loaded from here
├── tools/
│   ├── coingecko.py
│   └── ...
└── ...
```

### Complete .env File Example
```env
# CoinGecko API Configuration
COINGECKO_API_KEY=your_coingecko_api_key_here

# Anthropic API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# CoinGlass API Configuration
COINGLASS_API_KEY=your_coinglass_api_key_here

# LunaCrush API Configuration
LUNA_CRUSH_API_KEY=your_lunacrush_api_key_here
```

**Note**: All tools use `load_dotenv()` with the project root path, ensuring consistent API key loading regardless of the current working directory.

---

## Tool Categories Summary

### Market Data & Analytics
- **CoinGecko**: Basic market data, prices, historical charts
- **CoinGlass**: Futures market data, liquidations, funding rates, sentiment analysis
- **LunaCrush**: Social sentiment, community metrics, news analysis

### Funding & Derivatives Analysis
- `coinglass/funding_rate_arbitrage.py` - Funding rate opportunities
- `coinglass/funding_rate_exchange_list.py` - Exchange funding rates
- `coinglass/funding_rate_oi_weight_ohlc_history.py` - OI-weighted funding rate OHLC
- `coinglass/funding_rate_vol_weight_ohlc_history.py` - Volume-weighted funding rate OHLC
- `coinglass/futures_supported_coins.py` - Futures market coverage
- `coinglass/futures_pairs_markets.py` - Futures pair markets
- `coinglass/futures_supported_exchange_pairs.py` - Supported futures exchange pairs

### Liquidation Analysis
- `coinglass/liquidation_coin_list.py` - Available liquidation data
- `coinglass/liquidation_coin_history.py` - Historical liquidation events
- `coinglass/liquidation_exchange_list.py` - Exchange liquidation data
- `coinglass/liquidation_order.py` - Detailed liquidation orders
- `coinglass/liquidation_pair_map.py` - Liquidation pair mapping

### Open Interest Analysis
- `coinglass/open_interest_exchange_list.py` - Open interest data by exchange
- `coinglass/open_interest_aggregated_ohlc_history.py` - Aggregated OI OHLC
- `coinglass/open_interest_aggregated_coin_margin_ohlc_history.py` - Coin margin OI OHLC
- `coinglass/open_interest_aggregated_stablecoin_ohlc_history.py` - Stablecoin OI OHLC

### Social Sentiment Analysis
- `lunacrush/coins_list.py` - Social metrics for all coins
- `lunacrush/coin_meta.py` - Detailed social analytics
- `lunacrush/coin_time_series.py` - Historical coin social data
- `lunacrush/topic_details.py` - Topic-based sentiment
- `lunacrush/topic_news.py` - News sentiment analysis
- `lunacrush/topic_creators.py` - Top influencers for topics
- `lunacrush/topic_posts.py` - Social media posts for topics
- `lunacrush/topic_time_series.py` - Historical topic sentiment
- `lunacrush/category_details.py` - Category-based analytics
- `lunacrush/category_time_series.py` - Historical category data

### Volume & Trading Analysis
- `coinglass/coin_taker_buy_sell_volume_history.py` - Taker volume analysis
- `coinglass/taker_buy_sell_exchange_ratio.py` - Taker buy/sell ratios
- `dex_volume_ranking.py` - DEX volume rankings

### Spot Market Analysis
- `coinglass/spot_supported_coins.py` - Supported spot coins
- `coinglass/spot_supported_exchange_pairs.py` - Spot exchange pairs

### Whale & Large Trader Analysis
- `coinglass/whale_hyperliquid_alert.py` - Hyperliquid whale alerts
- `coinglass/whale_hyperliquid_position.py` - Hyperliquid whale positions

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

---

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

---

## Quick Reference

### Most Commonly Used Tools
- `top_coins.py` - Get top cryptocurrencies
- `coin_data_by_id.py` - Get detailed coin information
- `coin_ohlc_by_id.py` - Get OHLC data for technical analysis
- `coins_gainers_losers.py` - Get market performance

### For Technical Analysis
- `coin_ohlc_by_id.py` - OHLC data
- `coin_historical_chart_by_id.py` - Historical price charts
- `coin_historical_chart_range_by_id.py` - Custom time ranges
- `coingecko.py` - Advanced OHLC data with pagination

### For Market Analysis
- `top_coins.py` - Market cap rankings
- `coins_gainers_losers.py` - Market performance
- `coins_list_market_data.py` - Bulk market data
- `dex_volume_ranking.py` - DEX volume analysis

### CLI Quick Commands
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

# Find tools using AI
python tools/tool_selector.py "get bitcoin price data"
```

---

## Technical Information

### Error Handling
All tools include:
- Retry logic (3 attempts by default)
- Comprehensive error handling
- Connection timeout protection (15 seconds)
- Clear error messages
- CLI error output with descriptive messages

### Performance Notes
- All tools implement efficient API usage
- Rate limiting is handled automatically
- Data is returned in optimized formats (DataFrame where appropriate)
- Error handling includes retry mechanisms
- CLI tools support both JSON and CSV output for flexibility

### Testing
All tools include comprehensive test suites located in `/tools/test/`:
- Unit tests for individual functions
- Integration tests for API interactions
- Error handling tests
- Performance tests
- CLI functionality tests

### Maintenance
This tools list is automatically maintained. When adding new tools:
1. Add the tool to the appropriate category
2. Update the tool categories summary
3. Add usage examples if needed
4. Update environment variables if required
5. Add corresponding test files
6. Include CLI interface with proper help text
7. Support both JSON and CSV output formats