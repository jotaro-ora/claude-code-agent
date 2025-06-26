# BTC Price Monitor

## Purpose
Monitors Bitcoin (BTC) price for significant spikes and sends notifications when the price increases by more than a configurable threshold within a specified time window. Includes duplicate notification prevention via cooldown periods.

## Features
- Real-time BTC price monitoring using CoinGecko API
- Configurable percentage threshold for spike detection (default: 0.1%)
- Time window-based price comparison (default: 15 minutes)
- Duplicate notification prevention with cooldown periods (default: 60 minutes)
- State persistence to handle application restarts
- Comprehensive CLI configuration options
- Full test coverage

## Usage

### Basic Usage
```bash
# Run continuous monitoring with default settings
python src/btc_monitor.py

# Perform single price check
python src/btc_monitor.py --single-check
```

### Advanced Configuration
```bash
# Custom threshold and timing parameters
python src/btc_monitor.py --threshold 0.2 --window 10 --cooldown 30 --interval 30

# Specify custom state file location
python src/btc_monitor.py --state-file /path/to/custom/state.json
```

### CLI Parameters
- `--threshold PERCENT`: Percentage threshold for price spike notification (default: 0.1)
- `--window MINUTES`: Time window in minutes to monitor for price changes (default: 15)
- `--cooldown MINUTES`: Cooldown period in minutes between notifications (default: 60)
- `--interval SECONDS`: Check interval in seconds for continuous monitoring (default: 60)
- `--state-file PATH`: Path to state persistence file (default: ../data/btc_monitor_state.json)
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
- Uses `/tools/coin_data_by_id.py` for CoinGecko API integration

## How It Works

1. **Price Fetching**: Retrieves current BTC price from CoinGecko API
2. **History Management**: Maintains a rolling window of price data
3. **Spike Detection**: Compares current price against minimum price in the time window
4. **Notification Logic**: Sends alerts when threshold is exceeded and cooldown has passed
5. **State Persistence**: Saves price history and notification timestamps to prevent duplicates

## Example Output

### Normal Operation
```
Current BTC price: $45,234.56
```

### Price Spike Alert
```
🚨 BTC PRICE SPIKE ALERT 🚨
Time: 2024-01-15 14:30:22
From: $45,000.00
To: $45,234.56
Change: +0.52%
Threshold: 0.1%
Window: 15 minutes
```

## Testing

### Run All Tests
```bash
python tests/test_btc_monitor.py
```

### Test Coverage
- Unit tests for percentage calculations
- State persistence functionality
- Notification cooldown logic
- Price history management
- Spike detection algorithms
- API integration mocking
- Error handling scenarios

## File Structure
```
btc-price-monitor/
├── README.md                    # This file
├── src/
│   └── btc_monitor.py          # Main monitoring implementation
├── tests/
│   └── test_btc_monitor.py     # Comprehensive test suite
└── data/                       # State persistence (auto-created)
    └── btc_monitor_state.json  # Runtime state file
```

## Configuration Examples

### High-Frequency Day Trading
```bash
python src/btc_monitor.py --threshold 0.05 --window 5 --cooldown 15 --interval 30
```

### Conservative Long-Term Monitoring
```bash
python src/btc_monitor.py --threshold 1.0 --window 60 --cooldown 240 --interval 300
```

## Error Handling
- Graceful handling of API failures with retry logic
- State file corruption recovery
- Network timeout protection
- Invalid configuration parameter validation

## Performance
- Efficient rolling window price history management
- Minimal memory footprint through automatic cleanup
- API rate limiting compliance
- Execution time under 10 minutes for continuous operation