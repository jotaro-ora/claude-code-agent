import json

# ================== Begin fetch k-line tool code ==================
import requests
import pandas as pd
import time
from datetime import datetime


def get_coingecko_ohlc(symbol, interval, start_time, end_time):
    """
    Fetch OHLC data from CoinGecko API with flexible intervals and pagination.

    Args:
        symbol: Trading pair symbol(e.g., 'SPOT_BTC_USDT')
        interval: Kline interval('1h' or '1d')
        start_time: Start time(timestamp in ms or datetime string)
        end_time: End time(timestamp in ms or datetime string)

    Returns:
        DataFrame with OHLC data
    """
    cg_interval = _validate_interval(interval)
    coin_id = get_coinid_by_symbol(symbol)

    # Parse string time to timestamp in seconds
    def parse_start_time(tstr):
        try:
            # If it's already a timestamp, convert to seconds
            if isinstance(tstr, (int, float)):
                return int(tstr // 1000) if tstr > 1e11 else int(tstr)

            # Try parsing with seconds format first
            try:
                return int(datetime.strptime(tstr, "%Y-%m-%d %H:%M:%S").timestamp())
            except ValueError:
                # If that fails, try day format - set to beginning of day for start_time
                dt = datetime.strptime(tstr, "%Y-%m-%d")
                dt = dt.replace(hour=0, minute=0, second=0)
                return int(dt.timestamp())
        except Exception:
            raise ValueError("start_time should be timestamp or string 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'")

    def parse_end_time(tstr):
        try:
            # If it's already a timestamp, convert to seconds
            if isinstance(tstr, (int, float)):
                return int(tstr // 1000) if tstr > 1e11 else int(tstr)

            # Try parsing with seconds format first
            try:
                return int(datetime.strptime(tstr, "%Y-%m-%d %H:%M:%S").timestamp())
            except ValueError:
                # If that fails, try day format - set to end of day for end_time
                dt = datetime.strptime(tstr, "%Y-%m-%d")
                dt = dt.replace(hour=23, minute=59, second=59)
                return int(dt.timestamp())
        except Exception:
            raise ValueError("end_time should be timestamp or string 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'")

    start_time = parse_start_time(start_time)
    end_time = parse_end_time(end_time)
    now = int(datetime.utcnow().timestamp())
    if end_time > now:
        end_time = now
    min_time = 1518147224  # Historical limit
    if start_time < min_time:
        start_time = min_time
    if start_time > end_time:
        raise ValueError("start_time after end_time")
    all_data = []
    current_end_sec = end_time

    # ===== Pagination logic =====
    while True:
        # Calculate the chunk size based on interval
        if cg_interval == 'daily':
            chunk_size = 180 * 24 * 60 * 60  # 180 days in seconds (daily interval limit)
        else:
            chunk_size = 31 * 24 * 60 * 60   # 31 days in seconds (hourly interval limit)

        chunk_start = max(start_time, current_end_sec - chunk_size)

        params = {
            "vs_currency": "USD",
            "from": str(chunk_start),
            "to": str(current_end_sec),
            "interval": cg_interval
        }

        url = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/ohlc/range"

        # Send request with retries
        success = False
        for _ in range(3):
            try:
                data = _retry_api_request(url, params)

                if data:
                    # Process and filter the data
                    valid_klines = []
                    min_ts_sec = float('inf')

                    for item in data:
                        ts_ms = item[0]  # CoinGecko returns timestamps in ms
                        ts_sec = ts_ms // 1000

                        if ts_sec * 1000 >= start_time * 1000:  # Compare in ms for consistency
                            valid_klines.append({
                                "timestamp": ts_ms,
                                "open": item[1],
                                "high": item[2],
                                "low": item[3],
                                "close": item[4],
                            })

                            if ts_sec < min_ts_sec:
                                min_ts_sec = ts_sec

                    all_data.extend(valid_klines)

                    # Update pagination cursor
                    if min_ts_sec != float('inf'):
                        current_end_sec = min_ts_sec - 1
                    else:
                        print("No valid data found in current chunk")
                        break

                    # Check if we've covered the entire range
                    if current_end_sec <= start_time:
                        print("Full time range covered")
                        break

                    success = True

                else:
                    print("Empty response from API")
                    break

            except Exception as e:
                print(f"Request failed:{str(e)}")
                time.sleep(1)
                continue

            if success:
                break

        if not success:
            print("Failed to fetch data after retries")
            break

        # Break if we've reached the start time
        if current_end_sec <= start_time:
            break

        # Rate limiting
        time.sleep(1.2)  # CoinGecko Pro has a rate limit of 50 calls per minute

    return _format_dataframe(all_data)


def get_coinid_by_symbol(symbol: str):
    token = symbol.split('_')[1]
    url = "https://pro-api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "USD",
        "symbols": [token],
        "include_tokens": "top",
    }
    data = _retry_api_request(url, params)
    if len(data):
        return data[0].get("id", "")
    else:
        return "bitcoin"


def _validate_interval(interval):
    """
    Validate and map interval to CoinGecko format.

    Args:
        interval: Input interval ('1h' or '1d')

    Returns:
        Mapped interval ('hourly' or 'daily')
    """
    interval_map = {
        '1h': 'hourly',
        '1d': 'daily'
    }
    if interval not in interval_map:
        raise ValueError(f"Unsupported interval: {interval}. Must be one of: {list(interval_map.keys())}")
    return interval_map[interval]


def _retry_api_request(url, params, retries=3):
    for _ in range(retries):
        try:
            headers = {
                "x-cg-pro-api-key": "CG-t4wUUFcF6twecmvceJVeH6bx"
            }
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Request failed: {str(e)}")
            time.sleep(1)
    raise ConnectionError("API request failed after retries")


def _format_dataframe(raw_data):
    if not raw_data:
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Check if volume column exists, if not add it with 0 values
    if 'volume' not in df.columns:
        df['volume'] = 0

    return df.sort_values('datetime')[['datetime', 'open', 'high', 'low', 'close', 'volume']]
# ================== End fetch k-line tool code ==================


def main():
    try:
        df = get_coingecko_ohlc(
            symbol="SPOT_BTC_USDT",
            interval="1d",
            start_time="2024-01-01",
            end_time="2025-01-01"
        )
        if not df.empty:
            result = {"result": "1"}
        else:
            result = {"result": "0"}
    except Exception:
        result = {"result": "0"}
    print(json.dumps(result))


if __name__ == "__main__":
    main()