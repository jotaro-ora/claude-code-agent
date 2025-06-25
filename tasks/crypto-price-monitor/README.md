# Crypto Price Monitor

## Purpose

Real-time cryptocurrency price monitoring system with support/resistance level alerts. Continuously monitors specified cryptocurrencies and sends immediate notifications when prices reach calculated support or resistance levels based on the last 24 hours of price data.

## Features

- **Real-time Monitoring**: Uses WebSocket connections for live price updates
- **Dynamic Support/Resistance**: Automatically calculates and updates levels using multiple algorithms:
  - Pivot points analysis
  - Local extrema detection  
  - Moving average convergence/divergence
- **State Persistence**: Maintains monitoring state across restarts
- **Alert Cooldown**: Prevents spam alerts with configurable cooldown periods
- **CLI Configuration**: All parameters configurable via command-line arguments
- **Comprehensive Logging**: Detailed logging with file and console output

## Usage

### Recommended: Simple Monitor (Polling-based)
The simple monitor uses periodic polling and is more reliable:

```bash
# Basic usage
python3 tasks/crypto-price-monitor/run_simple_monitor.py

# Custom configuration
python3 tasks/crypto-price-monitor/run_simple_monitor.py \
    --symbols BTC ETH PEPE AAVE \
    --check-interval 5 \
    --alert-cooldown 30 \
    --tolerance 2.0
```

### Advanced: WebSocket Monitor (Real-time)
The WebSocket monitor provides real-time updates but requires API key configuration:

```bash
# Basic usage
python3 tasks/crypto-price-monitor/run_monitor.py

# Custom configuration
python3 tasks/crypto-price-monitor/run_monitor.py \
    --symbols PEPE VIRTUAL AAVE MKR \
    --alert-cooldown 30 \
    --tolerance 0.5
```

### Alternative: Direct Execution
If you prefer to run the scripts directly:
```bash
# Simple monitor
python3 tasks/crypto-price-monitor/src/simple_monitor.py

# WebSocket monitor  
python3 tasks/crypto-price-monitor/src/price_monitor.py
```
*(Requires dependencies to be installed manually)*

### Command-Line Parameters

**Common Parameters:**
- `--symbols`: List of crypto symbols to monitor (default: PEPE VIRTUAL AAVE MKR HYPE SPX ENA SEI)
- `--state-file`: Path to state persistence file (default: monitor_state.json)
- `--alert-cooldown`: Minutes between alerts for same token (default: 60)
- `--tolerance`: Price tolerance percentage for support/resistance levels (default: 1.0)

**Simple Monitor Only:**
- `--check-interval`: Minutes between price checks (default: 5)

## Monitored Cryptocurrencies

The system supports the following cryptocurrencies by default:
- PEPE (pepe)
- VIRTUAL (virtuals-protocol)
- AAVE (aave)
- MKR (maker)
- HYPE (hype-coin)
- SPX (spx-6900)
- ENA (ethena)
- SEI (sei-network)

## Dependencies

The `run_monitor.py` script automatically handles dependency installation in a virtual environment.

For manual installation (from project root):
```bash
pip install -r tasks/crypto-price-monitor/requirements.txt
```

### Required Environment Variables

Create a `.env` file in the project root with:
```bash
# API Keys
COINGECKO_API_KEY=your_coingecko_api_key_here
```

## Support/Resistance Algorithm

The system uses a multi-algorithm approach to calculate reliable support and resistance levels:

1. **Pivot Points**: Classic technical analysis pivot point calculation
2. **Local Extrema**: Identifies significant price peaks and troughs
3. **Moving Average Levels**: Uses MA as dynamic support/resistance

The most conservative levels are selected to minimize false alerts.

## Alert System

- Alerts trigger when price reaches within tolerance of support/resistance levels
- Default tolerance: 1% of the level price
- Cooldown period prevents duplicate alerts (default: 60 minutes)
- Alerts are displayed in console and logged to file

## State Persistence

The system maintains state across restarts including:
- Current support/resistance levels for each token
- Price history (last 24 hours)
- Last alert timestamps
- Total alerts sent

## Performance

- Designed for continuous operation (up to 1 month)
- Efficient memory usage with rolling price history
- Automatic reconnection for WebSocket failures
- Periodic level recalculation (hourly)

## Testing

Run the test suite (from project root):
```bash
python -m unittest tasks.crypto_price_monitor.tests.test_support_resistance -v
python -m unittest tasks.crypto_price_monitor.tests.test_price_monitor -v
```

Or run all tests:
```bash
python -m unittest discover tasks/crypto-price-monitor/tests/ -v
```

## Graceful Shutdown

The monitor handles shutdown signals gracefully:
- Ctrl+C (SIGINT) for manual stop
- SIGTERM for programmatic shutdown
- Automatically saves state before exit

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure valid API keys in `.env` file
2. **WebSocket Disconnections**: Monitor automatically reconnects
3. **Missing Price Data**: Check CoinGecko API limits and coin IDs
4. **State File Corruption**: Delete state file to reset (will lose history)

### Logging

Logs are written to:
- Console (INFO level and above)
- `crypto_monitor.log` file (all levels)

Increase verbosity by modifying the logging level in `price_monitor.py`.

## Architecture

```
tasks/crypto-price-monitor/
├── src/
│   ├── price_monitor.py        # Main monitoring system
│   └── support_resistance.py   # Level calculation algorithms
├── tests/
│   ├── test_price_monitor.py   # Monitor system tests
│   └── test_support_resistance.py  # Algorithm tests
├── data/                       # State files (created at runtime)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Security

- No API keys are logged or exposed
- State files contain no sensitive information
- All network connections use secure protocols
- Input validation prevents injection attacks