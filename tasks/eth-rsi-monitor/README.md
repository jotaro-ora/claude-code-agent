# ETH RSI Monitor

## Purpose
Monitors ETH RSI on 1H, 4H, 1D timeframes. Alerts when RSI crosses 70 (overbought) or 30 (oversold). Prevents duplicate notifications within 1 hour.

## Features
- **Multi-timeframe RSI monitoring** (1H, 4H, 1D)
- **Configurable RSI thresholds** for overbought/oversold conditions
- **Duplicate notification prevention** with customizable cooldown periods
- **Real-time OHLC data** from CoinGecko API
- **Accurate RSI calculation** using Wilder's smoothing method
- **State persistence** to maintain notification history across restarts
- **Comprehensive CLI configuration** for all parameters
- **Full test coverage** with RSI calculation validation

## Usage

### Basic Usage
```bash
# Run continuous monitoring with default settings (70/30 thresholds, 1h cooldown)
python3 src/eth_rsi_monitor.py

# Perform single RSI check across all timeframes
python3 src/eth_rsi_monitor.py --single-check
```

### Advanced Configuration
```bash
# Custom RSI thresholds and timeframes
python3 src/eth_rsi_monitor.py --overbought 75 --oversold 25 --timeframes 1h 4h

# Custom RSI period and cooldown
python3 src/eth_rsi_monitor.py --rsi-period 21 --cooldown 30

# High-frequency monitoring with custom check interval
python3 src/eth_rsi_monitor.py --interval 120 --cooldown 15
```

### CLI Parameters
- `--rsi-period N`: RSI calculation period (default: 14)
- `--overbought LEVEL`: RSI overbought threshold (default: 70)
- `--oversold LEVEL`: RSI oversold threshold (default: 30)
- `--cooldown MINUTES`: Cooldown period between duplicate notifications (default: 60)
- `--timeframes TF [TF...]`: Timeframes to monitor (default: 1h 4h 1d)
- `--interval SECONDS`: Check interval for continuous monitoring (default: 300)
- `--state-file PATH`: Path to state persistence file (default: ../data/eth_rsi_state.json)
- `--single-check`: Perform single check instead of continuous monitoring

## Dependencies

### Required Packages
- `python-dotenv`: Environment variable management
- `requests`: HTTP requests (via CoinGecko tools)

### Environment Variables
Required in root `.env` file:
```bash
COINGECKO_API_KEY=your_coingecko_api_key_here
```

### External Tools
- Uses `/tools/coin_ohlc_by_id.py` for OHLC data retrieval

## How It Works

### RSI Calculation
- **Formula**: Uses Wilder's smoothing method for accurate RSI calculation
- **Period**: Configurable period (default: 14 candles)
- **Range**: RSI values between 0-100
- **Thresholds**: 
  - Overbought: RSI ≥ 70 (configurable)
  - Oversold: RSI ≤ 30 (configurable)

### Timeframe Processing
1. **1H**: Uses hourly OHLC data directly
2. **4H**: Aggregates hourly data into 4-hour candles
3. **1D**: Uses daily OHLC data directly

### Alert Logic
1. **Data Retrieval**: Fetches OHLC data from CoinGecko API
2. **RSI Calculation**: Computes RSI for each timeframe
3. **Threshold Check**: Compares RSI against overbought/oversold levels
4. **Cooldown Check**: Prevents duplicate notifications within cooldown period
5. **Notification**: Sends alert if conditions are met

### Duplicate Prevention
- **Per-timeframe tracking**: Separate cooldown for each timeframe
- **Condition-specific**: Different cooldowns for overbought vs oversold
- **Time-based**: Configurable cooldown period (default: 1 hour)
- **State persistence**: Maintains notification history across restarts

## Example Output

### Normal RSI Check
```
Checking 1H RSI...
1H RSI: 45.2
Checking 4H RSI...
4H RSI: 52.8
Checking 1D RSI...
1D RSI: 48.1
Next check in 300 seconds...
```

### Overbought Alert
```
🔴 ETH RSI ALERT 🔴
Time: 2024-01-15 14:30:22
Timeframe: 1H
Condition: OVERBOUGHT
RSI: 75.3
Threshold: 70
Period: 14
```

### Oversold Alert
```
🟢 ETH RSI ALERT 🟢
Time: 2024-01-15 14:30:22
Timeframe: 4H
Condition: OVERSOLD
RSI: 28.7
Threshold: 30
Period: 14
```

### Cooldown Prevention
```
1H overbought condition detected but notification is in cooldown
```

## Testing

### Run All Tests
```bash
python3 tests/test_eth_rsi_monitor.py
```

### Test Coverage
- RSI calculation with various market conditions
- Timeframe data processing and aggregation
- Overbought/oversold threshold detection
- Notification cooldown logic
- State persistence functionality
- OHLC data retrieval and processing
- Error handling scenarios
- Edge cases and boundary conditions

## File Structure
```
eth-rsi-monitor/
├── README.md                      # This file
├── src/
│   └── eth_rsi_monitor.py         # Main RSI monitoring implementation
├── tests/
│   └── test_eth_rsi_monitor.py    # Comprehensive test suite
└── data/                          # State persistence (auto-created)
    └── eth_rsi_state.json         # Notification history
```

## Configuration Examples

### Conservative Trading Setup
```bash
# Wider thresholds, longer cooldown
python3 src/eth_rsi_monitor.py --overbought 80 --oversold 20 --cooldown 120
```

### Day Trading Setup
```bash
# Tighter thresholds, shorter cooldown, frequent checks
python3 src/eth_rsi_monitor.py --overbought 65 --oversold 35 --cooldown 15 --interval 60
```

### Swing Trading Setup
```bash
# Focus on higher timeframes only
python3 src/eth_rsi_monitor.py --timeframes 4h 1d --cooldown 240
```

### Custom RSI Period
```bash
# Use 21-period RSI instead of default 14
python3 src/eth_rsi_monitor.py --rsi-period 21
```

## RSI Interpretation

### Overbought Conditions (RSI ≥ 70)
- **Meaning**: ETH may be overvalued in the short term
- **Potential Action**: Consider selling or taking profits
- **Risk**: Price may continue rising in strong trends

### Oversold Conditions (RSI ≤ 30)
- **Meaning**: ETH may be undervalued in the short term  
- **Potential Action**: Consider buying or accumulating
- **Risk**: Price may continue falling in strong downtrends

### Neutral Zone (30 < RSI < 70)
- **Meaning**: ETH price is in normal trading range
- **Action**: No immediate RSI-based signals
- **Strategy**: Wait for clear overbought/oversold conditions

## State File Format

The monitor maintains notification history in JSON format:
```json
{
  "last_notifications": {
    "1h": {
      "condition": "overbought",
      "timestamp": "2024-01-15T14:30:22.123456"
    },
    "4h": {
      "condition": "oversold", 
      "timestamp": "2024-01-15T12:15:30.654321"
    }
  }
}
```

## Performance Considerations
- **API Rate Limiting**: Respects CoinGecko API limits with retry logic
- **Data Efficiency**: Fetches minimal required data for each timeframe
- **Memory Usage**: Lightweight state management
- **Execution Time**: Single check completes within 10-15 seconds typically

## Error Handling
- **API Failures**: Graceful handling with retry logic and informative messages
- **Missing Dependencies**: Clear error messages for missing tools
- **Invalid Configuration**: Input validation with helpful error descriptions
- **Network Issues**: Timeout protection and connection error handling
- **Insufficient Data**: Handles cases where not enough OHLC data is available

## Technical Details

### RSI Calculation Method
- **Initial Period**: Uses simple average for first RSI calculation
- **Smoothing**: Applies Wilder's smoothing for subsequent calculations
- **Formula**: RSI = 100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss
- **Validation**: Handles edge cases like no losses (RSI = 100) or no gains (RSI = 0)

### Timeframe Aggregation
- **4H from 1H**: Groups 4 consecutive hourly candles, uses close of 4th hour
- **Data Alignment**: Ensures proper time alignment for aggregated candles
- **Missing Data**: Handles gaps in hourly data gracefully