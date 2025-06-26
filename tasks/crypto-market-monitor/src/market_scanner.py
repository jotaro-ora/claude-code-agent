#!/usr/bin/env python3
"""Cryptocurrency market scanner for bullish signals."""

import sys
import os
import argparse
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add tools to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tools'))

from coins_list_market_data import get_coins_list_market_data
from coin_ohlc_range_by_id import get_coin_ohlc_range_by_id
import requests

def get_market_overview():
    """Get market overview with price changes and volume data."""
    try:
        # Get top 1000 coins with market data including 24h/7d changes
        # Try multiple API calls to get more comprehensive data
        all_data = []
        
        # Get top coins by market cap
        data1 = get_coins_list_market_data(
            vs_currency='usd',
            order='market_cap_desc',
            per_page=250,
            price_change_percentage='24h,7d'
        )
        if data1 is not None and not data1.empty:
            all_data.append(data1)
        
        # Get top 24h gainers
        data2 = get_coins_list_market_data(
            vs_currency='usd',
            order='price_change_percentage_24h_desc',
            per_page=250,
            price_change_percentage='24h,7d'
        )
        if data2 is not None and not data2.empty:
            all_data.append(data2)
        
        # Get top volume coins
        data3 = get_coins_list_market_data(
            vs_currency='usd',
            order='volume_desc',
            per_page=250,
            price_change_percentage='24h,7d'
        )
        if data3 is not None and not data3.empty:
            all_data.append(data3)
        
        if all_data:
            import pandas as pd
            combined_data = pd.concat(all_data, ignore_index=True)
            # Remove duplicates based on coin id
            combined_data = combined_data.drop_duplicates(subset=['id'], keep='first')
            return combined_data
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None

def filter_price_volume_criteria(market_data):
    """Filter tokens meeting price and volume criteria."""
    candidates = []
    
    # Convert DataFrame to dict records for iteration
    if hasattr(market_data, 'to_dict'):
        coins = market_data.to_dict('records')
    else:
        coins = market_data
    
    for coin in coins:
        try:
            price_24h = coin.get('price_change_percentage_24h', 0) or 0
            price_7d = coin.get('price_change_percentage_7d_in_currency', 0) or 0
            volume_24h = coin.get('total_volume', 0) or 0
            
            # Criteria 1 & 2: 24h and 7d price change > 5% (adjusted for realistic market conditions)
            if price_24h > 5 and price_7d > 5:
                # Basic volume check (we'll enhance this later)
                if volume_24h > 1000000:  # Minimum $1M volume
                    candidates.append({
                        'id': coin['id'],
                        'symbol': coin['symbol'].upper(),
                        'name': coin['name'],
                        'price': coin['current_price'],
                        'price_24h': price_24h,
                        'price_7d': price_7d,
                        'volume_24h': volume_24h,
                        'market_cap': coin.get('market_cap', 0)
                    })
        except (KeyError, TypeError):
            continue
    
    return candidates

def get_trending_coins():
    """Get trending coins from CoinGecko."""
    try:
        api_key = os.getenv('COINGECKO_API_KEY')
        if not api_key:
            print("Warning: COINGECKO_API_KEY not found")
            return []
        
        url = "https://pro-api.coingecko.com/api/v3/search/trending"
        headers = {'x-cg-pro-api-key': api_key}
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data and 'coins' in data:
            trending = []
            for item in data['coins']:
                coin = item.get('item', {})
                trending.append({
                    'id': coin.get('id'),
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name'),
                    'market_cap_rank': coin.get('market_cap_rank'),
                    'score': coin.get('score', 0)
                })
            return trending
    except Exception as e:
        print(f"Error fetching trending coins: {e}")
    return []

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average."""
    if len(prices) < period:
        return None
    
    multiplier = 2 / (period + 1)
    ema = prices[0]
    
    for price in prices[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema

def calculate_sma(prices, period):
    """Calculate Simple Moving Average."""
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period

def analyze_technical_indicators(coin_id):
    """Analyze technical indicators for a coin."""
    try:
        # Get 4-hour OHLC data for last 30 days
        now = int(time.time())
        thirty_days_ago = now - (30 * 24 * 60 * 60)
        
        ohlc_data = get_coin_ohlc_range_by_id(
            coin_id, 'usd', thirty_days_ago, now, 'hourly'
        )
        
        if not ohlc_data or len(ohlc_data) < 50:
            return None
        
        # Extract close prices
        closes = [float(candle[4]) for candle in ohlc_data]  # Close is index 4
        current_price = closes[-1]
        
        # Calculate EMAs and SMAs
        ema_20 = calculate_ema(closes, 20)
        ema_50 = calculate_ema(closes, 50)
        sma_20 = calculate_sma(closes, 20)
        sma_50 = calculate_sma(closes, 50)
        
        # Check if price is above moving averages
        above_ema_20 = current_price > ema_20 if ema_20 else False
        above_ema_50 = current_price > ema_50 if ema_50 else False
        above_sma_20 = current_price > sma_20 if sma_20 else False
        above_sma_50 = current_price > sma_50 if sma_50 else False
        
        return {
            'current_price': current_price,
            'ema_20': ema_20,
            'ema_50': ema_50,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'above_ema_20': above_ema_20,
            'above_ema_50': above_ema_50,
            'above_sma_20': above_sma_20,
            'above_sma_50': above_sma_50,
            'ma_score': sum([above_ema_20, above_ema_50, above_sma_20, above_sma_50])
        }
    except Exception as e:
        print(f"Error analyzing {coin_id}: {e}")
        return None

def score_candidate(candidate, trending_coins, technical_data):
    """Score a candidate based on all criteria."""
    score = 0
    details = {}
    
    # Criteria 1: 24h price change > 5%
    if candidate['price_24h'] > 5:
        score += 20
        details['price_24h'] = f"✓ {candidate['price_24h']:.1f}%"
    else:
        details['price_24h'] = f"✗ {candidate['price_24h']:.1f}%"
    
    # Criteria 2: 7d price change > 5%
    if candidate['price_7d'] > 5:
        score += 20
        details['price_7d'] = f"✓ {candidate['price_7d']:.1f}%"
    else:
        details['price_7d'] = f"✗ {candidate['price_7d']:.1f}%"
    
    # Criteria 3: High volume (basic check)
    if candidate['volume_24h'] > 10000000:  # $10M+
        score += 15
        details['volume'] = f"✓ ${candidate['volume_24h']:,.0f}"
    elif candidate['volume_24h'] > 1000000:  # $1M+
        score += 10
        details['volume'] = f"~ ${candidate['volume_24h']:,.0f}"
    else:
        details['volume'] = f"✗ ${candidate['volume_24h']:,.0f}"
    
    # Criteria 4: Trending status
    is_trending = any(t['id'] == candidate['id'] for t in trending_coins)
    if is_trending:
        score += 15
        details['trending'] = "✓ Trending"
    else:
        details['trending'] = "✗ Not trending"
    
    # Criteria 5 & 6: Technical indicators
    if technical_data:
        ma_score = technical_data['ma_score']
        if ma_score >= 3:
            score += 20
            details['technical'] = f"✓ {ma_score}/4 MAs"
        elif ma_score >= 2:
            score += 10
            details['technical'] = f"~ {ma_score}/4 MAs"
        else:
            details['technical'] = f"✗ {ma_score}/4 MAs"
    else:
        details['technical'] = "✗ No data"
    
    return score, details

def main():
    """Main scanner function."""
    parser = argparse.ArgumentParser(description='Crypto Market Bullish Scanner')
    parser.add_argument('--min-score', type=int, default=60, 
                       help='Minimum score threshold (default: 60)')
    parser.add_argument('--max-results', type=int, default=20,
                       help='Maximum results to show (default: 20)')
    args = parser.parse_args()
    
    print("🔍 Crypto Market Bullish Scanner")
    print("=" * 50)
    
    # Get market overview
    print("📊 Fetching market data...")
    market_data = get_market_overview()
    if market_data is None or market_data.empty:
        print("❌ Failed to fetch market data")
        return
    
    # Filter initial candidates
    print("🔍 Filtering price/volume criteria...")
    candidates = filter_price_volume_criteria(market_data)
    print(f"Found {len(candidates)} initial candidates")
    
    # Get trending coins
    print("📈 Fetching trending coins...")
    trending_coins = get_trending_coins()
    print(f"Found {len(trending_coins)} trending coins")
    
    # Analyze each candidate
    print("🔬 Analyzing technical indicators...")
    scored_candidates = []
    
    for i, candidate in enumerate(candidates[:50]):  # Limit to top 50 for speed
        print(f"Analyzing {i+1}/50: {candidate['symbol']}", end='\r')
        
        technical_data = analyze_technical_indicators(candidate['id'])
        score, details = score_candidate(candidate, trending_coins, technical_data)
        
        if score >= args.min_score:
            scored_candidates.append({
                'candidate': candidate,
                'score': score,
                'details': details,
                'technical': technical_data
            })
    
    print("\n")
    
    # Sort by score and display results
    scored_candidates.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"🎯 Top Bullish Candidates (Score ≥ {args.min_score})")
    print("=" * 80)
    
    for i, item in enumerate(scored_candidates[:args.max_results]):
        candidate = item['candidate']
        score = item['score']
        details = item['details']
        
        print(f"\n{i+1}. {candidate['symbol']} ({candidate['name']}) - Score: {score}/100")
        print(f"   Price: ${candidate['price']:.6f} | MCap: ${candidate['market_cap']:,.0f}")
        print(f"   24h: {details['price_24h']} | 7d: {details['price_7d']}")
        print(f"   Volume: {details['volume']} | Trending: {details['trending']}")
        print(f"   Technical: {details['technical']}")
    
    if not scored_candidates:
        print("No candidates found meeting the criteria.")
    
    print(f"\n📊 Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    load_dotenv()
    main()