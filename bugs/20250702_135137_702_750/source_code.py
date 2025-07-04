import requests
import time
import uuid
import json
from urllib.parse import quote
import pandas as pd
import numpy as np
from datetime import datetime, timezone


# =====================  DO NOT MODIFY – BEGIN fetch k-line code  =====================
def get_alltick_data(symbol, interval, start_time, end_time):
    # ===== Parameter conversion =====
    symbol_clean = symbol.split("_")[1] + "USDT"

    interval_map = {"1m": 1, "5m": 2, "15m": 3, "30m": 4, "1h": 5, "2h": 6, "4h": 7, "6h": 11, "12h": 12, "1d": 8, "1w": 9, "1mon": 10}
    kline_type = interval_map.get(interval)
    if not kline_type:
        raise ValueError(f"Invalid interval: {interval}")

    # ===== Time handling =====
    start_ts = int(start_time)  # Input timestamp in milliseconds
    end_ts = int(end_time)
    current_end_sec = end_ts // 1000  # Current end time in seconds
    all_data = []

    # ===== Pagination logic =====
    while True:
        # Calculate request batch size
        req_num = calculate_request_num(start_ts, current_end_sec * 1000, interval)

        # Build request parameters (using second-level timestamp)
        params = {"trace": f"{uuid.uuid4()}-{int(time.time() * 1000)}", "data": {"code": symbol_clean, "kline_type": kline_type, "kline_timestamp_end": current_end_sec, "query_kline_num": min(1000, req_num), "adjust_type": 0}}

        # Encode request
        query_data = json.dumps(params, separators=(",", ":"))
        encoded_query = quote(query_data)
        url = f"https://quote.alltick.io/quote-b-api/kline?token=cf173f1791c7818b666aa95bdebcbdbd-c-app&query={encoded_query}"

        # Send request
        success = False
        for _ in range(3):
            try:
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                data = resp.json()

                if data.get("ret") == 200:
                    klines = data["data"]["kline_list"]
                    if not klines:
                        return process_dataframe(all_data)  # Early return

                    # Convert timestamps and filter
                    valid_klines = []
                    min_ts_sec = float("inf")  # Track minimum second-level timestamp
                    for k in klines:
                        ts_sec = int(k["timestamp"])
                        ts_ms = ts_sec * 1000
                        if ts_ms >= start_ts:
                            valid_klines.append({**k, "timestamp": ts_ms})
                            if ts_sec < min_ts_sec:
                                min_ts_sec = ts_sec

                    all_data.extend(valid_klines)

                    # Critical fix: Update current end time
                    if min_ts_sec != float("inf"):
                        current_end_sec = min_ts_sec - 1  # Decrement second-level timestamp
                    else:
                        return process_dataframe(all_data)

                    # Check if we need to continue
                    if current_end_sec < (start_ts // 1000):
                        return process_dataframe(all_data)

                    success = True
                    break

                else:
                    time.sleep(1)

            except Exception:
                time.sleep(1)

        if not success:
            raise ConnectionError("Request failed after 3 retries")

        # Rate limiting
        time.sleep(0.1)


def calculate_request_num(start_ts_ms, end_ts_ms, interval):
    interval_ms = get_interval_milliseconds(interval)
    if interval_ms == 0 or end_ts_ms <= start_ts_ms:
        return 1

    return (end_ts_ms - start_ts_ms) // interval_ms


def get_interval_milliseconds(interval):
    if interval == "1mon":
        return 30 * 24 * 60 * 60 * 1000  # 30 days approximation

    unit = interval[-1]
    value = int(interval[:-1])

    multipliers = {"m": 60, "h": 60 * 60, "d": 24 * 60 * 60, "w": 7 * 24 * 60 * 60}
    return value * multipliers[unit] * 1000


def process_dataframe(raw_data):
    if not raw_data:
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)

    # Type conversion
    numeric_cols = ["open_price", "close_price", "high_price", "low_price", "volume"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Time handling
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")

    # Column renaming
    df = df.rename(columns={"open_price": "open", "close_price": "close", "high_price": "high", "low_price": "low"})

    # Deduplication and sorting
    df = df.drop_duplicates("timestamp").sort_values("datetime")

    return df[["datetime", "open", "high", "low", "close", "volume"]]


# =====================  DO NOT MODIFY – END fetch k-line code  =====================


def compute_stochastic(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["low14"] = df["low"].rolling(window=14, min_periods=14).min()
    df["high14"] = df["high"].rolling(window=14, min_periods=14).max()

    # Avoid division by zero
    df["raw_k"] = np.where((df["high14"] - df["low14"]) == 0, np.nan, (df["close"] - df["low14"]) / (df["high14"] - df["low14"]) * 100)

    df["%K"] = df["raw_k"].rolling(window=3, min_periods=3).mean()
    df["%D"] = df["%K"].rolling(window=3, min_periods=3).mean()
    return df.dropna(subset=["%K", "%D"])


def detect_events(df: pd.DataFrame, timeframe: str):
    window_map = {"4h": 6, "6h": 4, "12h": 2, "1d": 2}
    window_size = window_map.get(timeframe, 10)
    sub_df = df.tail(max(10, window_size))
    idxs = sub_df.index.tolist()
    crosses = []

    # Detect crossovers in chronological order
    for i in range(1, len(idxs)):
        prev = idxs[i - 1]
        curr = idxs[i]
        prev_k, prev_d = sub_df.loc[prev, "%K"], sub_df.loc[prev, "%D"]
        curr_k, curr_d = sub_df.loc[curr, "%K"], sub_df.loc[curr, "%D"]

        if prev_k < prev_d and curr_k > curr_d:
            crosses.append((curr, "bullish"))
        elif prev_k > prev_d and curr_k < curr_d:
            crosses.append((curr, "bearish"))

    events = []

    # New
    if crosses and crosses[-1][0] == idxs[-1]:
        events.append(("new", crosses[-1][1], sub_df.loc[crosses[-1][0], "datetime"]))

    # Confirmed
    if len(crosses) >= 1 and crosses[-1][0] == idxs[-2]:
        last_dir = crosses[-1][1]
        last_k, last_d = sub_df.loc[idxs[-1], "%K"], sub_df.loc[idxs[-1], "%D"]
        if (last_dir == "bullish" and last_k > last_d) or (last_dir == "bearish" and last_k < last_d):
            events.append(("confirmed", last_dir, sub_df.loc[idxs[-1], "datetime"]))

    # Closed
    if len(crosses) >= 2:
        last_dir = crosses[-2][1]
        if crosses[-1][1] != last_dir:
            events.append(("closed", last_dir, sub_df.loc[crosses[-1][0], "datetime"]))

    formatted_events = []
    for etype, direction, dt in events:
        formatted_events.append({"timeframe": timeframe, "eventTimeUTC": dt.strftime("%Y-%m-%d %H:%M:%S"), "direction": direction, "type": etype})
    return formatted_events


def main():
    timeframes = ["4h", "6h", "12h", "1d"]
    interval_ms_map = {"4h": 4 * 60 * 60 * 1000, "6h": 6 * 60 * 60 * 1000, "12h": 12 * 60 * 60 * 1000, "1d": 24 * 60 * 60 * 1000}

    all_events = []
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    for tf in timeframes:
        interval_ms = interval_ms_map[tf]
        start_ms = now_ms - 200 * interval_ms  # Fetch 200 candles to ensure >=100 available
        df_raw = get_alltick_data("SPOT_BTC_USDT", tf, start_ms, now_ms)
        if df_raw.empty:
            continue
        df_stoch = compute_stochastic(df_raw)
        if df_stoch.empty:
            continue
        events = detect_events(df_stoch, tf)
        all_events.extend(events)

    print(json.dumps(all_events))


if __name__ == "__main__":
    main()
