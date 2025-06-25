"""
Support and resistance level calculation module.

This module provides algorithms to dynamically calculate support and resistance levels
based on historical price data for cryptocurrency monitoring.
"""

from typing import List, Dict
import pandas as pd


class SupportResistanceCalculator:
    """
    Calculate dynamic support and resistance levels from price data.
    
    Uses multiple algorithms including:
    - Pivot points
    - Moving average convergence/divergence
    - Volume weighted levels
    - Local extrema detection
    """
    
    def __init__(self, lookback_hours: int = 24):
        """
        Initialize the calculator.
        
        Args:
            lookback_hours: Hours of historical data to analyze
        """
        if not isinstance(lookback_hours, int) or lookback_hours <= 0:
            raise ValueError("lookback_hours must be a positive integer")
        
        self.lookback_hours = lookback_hours
        
    def calculate_levels(self, price_data: List[Dict]) -> Dict[str, float]:
        """
        Calculate support and resistance levels from price data.
        
        Args:
            price_data: List of price data dictionaries with keys:
                       'timestamp', 'price', 'volume' (optional)
        
        Returns:
            Dictionary with 'support' and 'resistance' levels
            
        Raises:
            ValueError: If price_data is invalid or insufficient
        """
        if not price_data:
            raise ValueError("Price data cannot be empty")
        
        if len(price_data) < 5:
            raise ValueError("Insufficient price data (minimum 5 points required)")
        
        # Validate data structure
        for i, data_point in enumerate(price_data):
            if not isinstance(data_point, dict):
                raise TypeError(f"Price data point {i} must be a dictionary")
            
            if 'price' not in data_point:
                raise ValueError(f"Price data point {i} missing 'price' key")
            
            if not isinstance(data_point['price'], (int, float)):
                raise TypeError(f"Price at index {i} must be numeric")
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(price_data)
        df['price'] = pd.to_numeric(df['price'])
        
        # Sort by timestamp if available
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
        
        # Calculate multiple support/resistance levels and take the most reliable
        levels = {}
        
        # Method 1: Pivot points
        pivot_levels = self._calculate_pivot_points(df)
        
        # Method 2: Local extrema
        extrema_levels = self._calculate_local_extrema(df)
        
        # Method 3: Moving average based levels
        ma_levels = self._calculate_ma_levels(df)
        
        # Combine and validate levels
        support_candidates = [
            pivot_levels.get('support', 0),
            extrema_levels.get('support', 0),
            ma_levels.get('support', 0)
        ]
        
        resistance_candidates = [
            pivot_levels.get('resistance', 0),
            extrema_levels.get('resistance', 0),
            ma_levels.get('resistance', 0)
        ]
        
        # Filter out zero values and select most conservative levels
        valid_support = [s for s in support_candidates if s > 0]
        valid_resistance = [r for r in resistance_candidates if r > 0]
        
        if not valid_support:
            # Fallback to recent low
            levels['support'] = float(df['price'].min())
        else:
            # Take the highest support level (most conservative)
            levels['support'] = float(max(valid_support))
        
        if not valid_resistance:
            # Fallback to recent high
            levels['resistance'] = float(df['price'].max())
        else:
            # Take the lowest resistance level (most conservative)
            levels['resistance'] = float(min(valid_resistance))
        
        # Sanity check: support should be less than resistance
        if levels['support'] >= levels['resistance']:
            current_price = float(df['price'].iloc[-1])
            levels['support'] = current_price * 0.95  # 5% below current
            levels['resistance'] = current_price * 1.05  # 5% above current
        
        return levels
    
    def _calculate_pivot_points(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate pivot point based support and resistance."""
        if len(df) < 3:
            return {}
        
        high = df['price'].max()
        low = df['price'].min()
        close = df['price'].iloc[-1]
        
        pivot = (high + low + close) / 3
        support = 2 * pivot - high
        resistance = 2 * pivot - low
        
        return {
            'support': float(support),
            'resistance': float(resistance)
        }
    
    def _calculate_local_extrema(self, df: pd.DataFrame) -> Dict[str, float]:
        """Find local extrema as support/resistance levels."""
        if len(df) < 5:
            return {}
        
        prices = df['price'].values
        
        # Find local minima and maxima
        local_mins = []
        local_maxs = []
        
        for i in range(2, len(prices) - 2):
            # Local minimum
            if (prices[i] < prices[i-1] and prices[i] < prices[i+1] and
                prices[i] < prices[i-2] and prices[i] < prices[i+2]):
                local_mins.append(prices[i])
            
            # Local maximum
            if (prices[i] > prices[i-1] and prices[i] > prices[i+1] and
                prices[i] > prices[i-2] and prices[i] > prices[i+2]):
                local_maxs.append(prices[i])
        
        result = {}
        
        if local_mins:
            # Take the highest local minimum as support
            result['support'] = float(max(local_mins))
        
        if local_maxs:
            # Take the lowest local maximum as resistance
            result['resistance'] = float(min(local_maxs))
        
        return result
    
    def _calculate_ma_levels(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate moving average based support/resistance levels."""
        if len(df) < 10:
            return {}
        
        # Calculate moving averages
        window = min(20, len(df) // 2)
        df['ma'] = df['price'].rolling(window=window).mean()
        
        # Use MA as dynamic support/resistance
        current_price = df['price'].iloc[-1]
        current_ma = df['ma'].iloc[-1]
        
        if pd.isna(current_ma):
            return {}
        
        # Determine if price is above or below MA
        if current_price > current_ma:
            # MA acts as support
            support = float(current_ma)
            # Resistance is recent high above MA
            recent_highs = df[df['price'] > current_ma]['price']
            if len(recent_highs) > 0:
                resistance = float(recent_highs.quantile(0.8))  # 80th percentile
            else:
                resistance = float(current_price * 1.05)
        else:
            # MA acts as resistance
            resistance = float(current_ma)
            # Support is recent low below MA
            recent_lows = df[df['price'] < current_ma]['price']
            if len(recent_lows) > 0:
                support = float(recent_lows.quantile(0.2))  # 20th percentile
            else:
                support = float(current_price * 0.95)
        
        return {
            'support': support,
            'resistance': resistance
        }
    
    def is_price_at_level(self, current_price: float, level: float, 
                         tolerance_percent: float = 1.0) -> bool:
        """
        Check if current price is at a support/resistance level.
        
        Args:
            current_price: Current price to check
            level: Support or resistance level
            tolerance_percent: Tolerance as percentage (default 1%)
        
        Returns:
            True if price is within tolerance of the level
        """
        if not isinstance(current_price, (int, float)) or current_price <= 0:
            raise ValueError("current_price must be a positive number")
        
        if not isinstance(level, (int, float)) or level <= 0:
            raise ValueError("level must be a positive number")
        
        if not isinstance(tolerance_percent, (int, float)) or tolerance_percent < 0:
            raise ValueError("tolerance_percent must be non-negative")
        
        tolerance = level * (tolerance_percent / 100)
        return abs(current_price - level) <= tolerance