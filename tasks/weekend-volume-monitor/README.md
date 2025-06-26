# Weekend Volume Monitor

## Purpose
Monitors total cryptocurrency market trading volume every weekend and alerts if weekend volume exceeds the historical average. Compares current weekend's total trading volume to the average weekend volume over a configurable historical period.

## Features
- **Weekend-only monitoring** with intelligent scheduling
- **Historical volume comparison** over configurable time periods
- **Top N coin monitoring** by market cap for comprehensive coverage
- **Configurable alert thresholds** for volume spike detection
- **State persistence** to maintain historical data across restarts
- **Flexible scheduling** with multiple daily checks on weekends
- **CLI configuration** for all parameters
- **Comprehensive test coverage**

## Usage

### Basic Usage
```bash
# Run scheduled weekend monitoring (default: 4 weeks history, 10% threshold)
python3 src/weekend_volume_monitor.py

# Perform single weekend check
python3 src/weekend_volume_monitor.py --single-check
```

### Advanced Configuration
```bash
# Custom historical period and alert threshold
python3 src/weekend_volume_monitor.py --historical-weeks 8 --threshold 15.0

# Monitor more coins with custom check times
python3 src/weekend_volume_monitor.py --top-coins 200 --check-times 10:00 16:00 22:00

# Custom state file location
python3 src/weekend_volume_monitor.py --state-file /path/to/custom/state.json
```

### CLI Parameters
- `--historical-weeks N`: Number of weeks of historical data to maintain (default: 4)
- `--top-coins N`: Number of top coins by market cap to monitor (default: 100)
- `--threshold PERCENT`: Percentage threshold above average to trigger alert (default: 10.0)
- `--check-times TIME [TIME...]`: Times to check volume on weekends (format: HH:MM, default: 09:00 15:00 21:00)
- `--state-file PATH`: Path to state persistence file (default: ../data/weekend_volume_state.json)
- `--single-check`: Perform single check instead of scheduled monitoring

## Dependencies

### Required Packages
- `python-dotenv`: Environment variable management
- `pandas`: Data manipulation
- `requests`: HTTP requests (via CoinGecko tools)
- `schedule`: Task scheduling (optional, falls back to simple mode if not available)

Install scheduling dependency:
```bash
pip install schedule
```

### Environment Variables
Required in root `.env` file:
```bash
COINGECKO_API_KEY=your_coingecko_api_key_here
```

### External Tools
- Uses `/tools/coins_list_market_data.py` for market data retrieval

## How It Works

### Weekend Detection
- **Saturday/Sunday identification** using Python's `datetime.weekday()`
- **Weekend period calculation** from Saturday 00:00:00 to Sunday 23:59:59
- **Automatic scheduling** only runs checks on weekends

### Volume Analysis Process
1. **Data Collection**: Fetches top N coins by market cap via CoinGecko API
2. **Volume Aggregation**: Sums total trading volume across all monitored coins
3. **Historical Comparison**: Compares current volume to rolling average of previous weekends
4. **Alert Decision**: Triggers alert if volume exceeds threshold percentage above average
5. **State Management**: Persists historical data and maintains rolling window

### Alert Logic
- Requires minimum 2 weekends of historical data before alerting
- Calculates percentage increase: `((current - average) / average) * 100`
- Sends alert if increase ≥ configured threshold percentage
- Automatically manages historical data cleanup

## Example Output

### Normal Weekend Check
```
Weekend volume check - Saturday, 2024-01-13 15:00:23
Current total market volume: $45,234,567,890
Historical average (4 weeks): $42,100,000,000
Volume change: +7.4%
Volume within normal range (threshold: +10.0%)
```

### High Volume Alert
```
🔥 WEEKEND VOLUME ALERT 🔥
Time: 2024-01-13 15:00:23
Weekend: 2024-01-13 to 2024-01-14

Current Volume: $52,500,000,000
Historical Avg: $42,100,000,000
Increase: +24.7%

Alert Threshold: 10.0%
Historical Period: 4 weeks
Top Coins Monitored: 100
```

### Weekday Operation
```
Not weekend - skipping check (today is Tuesday)
```

## Testing

### Run All Tests
```bash
python3 tests/test_weekend_volume_monitor.py
```

### Test Coverage
- Weekend detection logic
- Historical average calculations
- Volume aggregation from market data
- Alert threshold determination
- State persistence functionality
- API integration with mocking
- Date calculation utilities
- Error handling scenarios

## File Structure
```
weekend-volume-monitor/
├── README.md                           # This file
├── src/
│   └── weekend_volume_monitor.py       # Main monitoring implementation
├── tests/
│   └── test_weekend_volume_monitor.py  # Comprehensive test suite
└── data/                               # State persistence (auto-created)
    └── weekend_volume_state.json       # Historical volume data
```

## Configuration Examples

### Conservative Long-Term Monitoring
```bash
# 8 weeks history, 20% threshold, fewer checks
python3 src/weekend_volume_monitor.py --historical-weeks 8 --threshold 20.0 --check-times 12:00
```

### Aggressive Day-Trading Style
```bash
# 2 weeks history, 5% threshold, frequent checks, more coins
python3 src/weekend_volume_monitor.py --historical-weeks 2 --threshold 5.0 --top-coins 250 --check-times 08:00 12:00 16:00 20:00
```

### Institutional Monitoring
```bash
# Comprehensive monitoring with extended history
python3 src/weekend_volume_monitor.py --historical-weeks 12 --threshold 15.0 --top-coins 500
```

## State File Format

The monitor maintains historical data in JSON format:
```json
{
  "weekend_volumes": [
    {
      "date": "2024-01-06",
      "volume": 45234567890,
      "timestamp": "2024-01-06T15:00:23.123456"
    }
  ],
  "last_alert": "2024-01-13T15:00:23.123456"
}
```

## Scheduling Details

### Default Schedule
- **Saturday**: 09:00, 15:00, 21:00
- **Sunday**: 09:00, 15:00, 21:00
- **Weekdays**: No checks performed

### Fallback Mode
If the `schedule` package is unavailable:
- Checks every hour
- Only processes data on weekends (weekdays are skipped)
- Less precise timing but maintains functionality

## Performance Considerations
- **API Rate Limiting**: Respects CoinGecko API limits with retry logic
- **Memory Efficiency**: Maintains only necessary historical data
- **Storage Optimization**: Automatic cleanup of old weekend data
- **Execution Time**: Single check completes within 30 seconds typically

## Error Handling
- **API Failures**: Graceful handling with retry logic and informative messages
- **Missing Dependencies**: Fallback modes for optional packages
- **State File Issues**: Recovery from corrupted or missing state files
- **Network Issues**: Timeout protection and connection error handling
- **Invalid Configuration**: Input validation with clear error messages