# Crypto Market Monitor

## Purpose
Monitors the cryptocurrency market for tokens meeting comprehensive bullish criteria including price momentum, volume analysis, trending status, and technical indicators.

## Features

### Bullish Framework Criteria
1. **Price Momentum**: 24h and 7d price changes > 5% (adjustable based on market conditions)
2. **Volume Analysis**: 24h trading volume significantly above average
3. **Trending Status**: Token appearing on CoinGecko Most Searched
4. **Technical Analysis**: Price above 20-EMA and 50-SMA on multiple timeframes
5. **Breakout Detection**: Technical breakout above resistance levels
6. **Support Validation**: Pullbacks holding previous resistance as new support

### Scoring System
- **Price Changes (40 points)**: 20 points each for 24h/7d > 5%
- **Volume (15 points)**: Based on volume thresholds
- **Trending (15 points)**: Appears in CoinGecko trending
- **Technical (20 points)**: Moving average position analysis
- **Breakout (10 points)**: Resistance level breaks (future enhancement)

## Usage

### Basic Scan
```bash
cd tasks/crypto-market-monitor
python src/market_scanner.py
```

### Advanced Options
```bash
# Set minimum score threshold
python src/market_scanner.py --min-score 70

# Limit number of results
python src/market_scanner.py --max-results 10

# Combine options
python src/market_scanner.py --min-score 75 --max-results 5
```

## Dependencies

### Required Packages
- requests
- python-dotenv
- pandas (optional, for enhanced data processing)

### Installation
```bash
pip install requests python-dotenv
```

### Environment Variables
Create a `.env` file in the project root:
```bash
COINGECKO_API_KEY=your_coingecko_api_key_here
```

## Output Format

```
🎯 Top Bullish Candidates (Score ≥ 60)
================================================================================

1. EXAMPLE (Example Token) - Score: 85/100
   Price: $1.234567 | MCap: $1,000,000,000
   24h: ✓ 15.2% | 7d: ✓ 18.7%
   Volume: ✓ $25,000,000 | Trending: ✓ Trending
   Technical: ✓ 3/4 MAs
```

## Technical Analysis

### Moving Averages
- **EMA-20**: 20-period Exponential Moving Average
- **EMA-50**: 50-period Exponential Moving Average  
- **SMA-20**: 20-period Simple Moving Average
- **SMA-50**: 50-period Simple Moving Average

### Scoring Logic
- 4/4 MAs above: 20 points
- 3/4 MAs above: 20 points
- 2/4 MAs above: 10 points
- < 2 MAs above: 0 points

## Testing

### Run Tests
```bash
cd tasks/crypto-market-monitor
python -m pytest tests/ -v
```

### Test Coverage
- Unit tests for filtering functions
- Technical indicator calculations
- Scoring system validation
- Mock data testing

## Performance

- **Execution Time**: < 2 minutes for top 50 coins
- **API Calls**: Optimized to minimize rate limiting
- **Memory Usage**: Efficient processing of market data
- **Rate Limiting**: Built-in delays for API compliance

## File Structure

```
crypto-market-monitor/
├── src/
│   └── market_scanner.py     # Main scanner implementation
├── tests/
│   └── test_market_scanner.py # Test suite
├── data/                     # Cache and state files (auto-created)
└── README.md                # This documentation
```

## Limitations

1. **Historical Data**: Limited to recent price history for technical analysis
2. **Volume Average**: Basic volume comparison (enhanced version needed)
3. **Resistance Levels**: Simplified breakout detection
4. **Real-time Data**: Snapshot analysis, not continuous monitoring

## Future Enhancements

1. **Advanced Volume Analysis**: Compare against historical averages
2. **Resistance/Support Detection**: Automated level identification
3. **Real-time Monitoring**: Continuous scanning capabilities
4. **Alert System**: Notifications for high-scoring candidates
5. **Historical Backtesting**: Performance validation
6. **Additional Timeframes**: 1h, 4h, daily analysis

## Error Handling

- API connection failures with retry logic
- Missing data graceful handling
- Rate limiting protection
- Invalid coin ID handling

## Security

- API keys loaded from environment variables
- No credential logging or exposure
- Input validation for all parameters
- Secure API communication