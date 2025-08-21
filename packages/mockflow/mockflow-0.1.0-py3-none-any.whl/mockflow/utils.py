"""
MockFlow Utility Functions

This module contains utility functions for:
- Timestamp generation and validation
- Data validation and clipping
- Helper functions for OHLC processing
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np


def generate_ohlc_data(
    prices: np.ndarray,
    volatility_cycles: np.ndarray,
    volumes: np.ndarray,
    periods: int,
) -> Dict[str, np.ndarray]:
    """Generate realistic OHLC data with proper intrabar movement"""
    opens = np.zeros(periods)
    highs = np.zeros(periods)
    lows = np.zeros(periods)
    closes = np.zeros(periods)

    for i in range(periods):
        if i == 0:
            open_price = prices[i]
        else:
            # Open is usually close to previous close with small gap
            gap_factor = np.random.normal(0, volatility_cycles[i] * 0.2)
            open_price = closes[i - 1] * (1 + gap_factor)

        close_price = prices[i]

        # Generate realistic intrabar movement based on volatility
        intrabar_volatility = volatility_cycles[i] * 0.5

        # High and low based on open and close with realistic movement
        high_variation = np.abs(np.random.normal(0, intrabar_volatility))
        low_variation = np.abs(np.random.normal(0, intrabar_volatility))

        # Calculate high and low ensuring they encompass open and close
        high_price = max(open_price, close_price) * (1 + high_variation)
        low_price = min(open_price, close_price) * (1 - low_variation)

        # Ensure OHLC consistency
        opens[i] = open_price
        highs[i] = max(open_price, high_price, close_price)
        lows[i] = min(open_price, low_price, close_price)
        closes[i] = close_price

    # Clip all values to prevent JSON serialization errors
    return {
        "open": np.clip(opens, 1, 1_000_000).astype(float),
        "high": np.clip(highs, 1, 1_000_000).astype(float),
        "low": np.clip(lows, 1, 1_000_000).astype(float),
        "close": np.clip(closes, 1, 1_000_000).astype(float),
        "volume": volumes.astype(int),
    }


def generate_timestamps(
    periods: int,
    timeframe_mins: int,
    start_date: datetime
) -> List[datetime]:
    """Generate datetime timestamps for the given parameters"""
    return [
        start_date + timedelta(minutes=timeframe_mins * i)
        for i in range(periods)
    ]


def get_timeframe_minutes(timeframe: str) -> int:
    """Get the number of minutes for a given timeframe string"""
    timeframe_map = {
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "2h": 120,
        "4h": 240,
        "12h": 720,
        "1d": 1440,
        "3d": 4320,
        "1w": 10080,
    }
    return timeframe_map.get(timeframe, 60)  # Default to 1h


def calculate_periods_from_days(days: int, timeframe_mins: int) -> int:
    """Calculate number of periods from days and timeframe"""
    total_minutes = days * 24 * 60
    return int(total_minutes / timeframe_mins)


def calculate_periods_from_date_range(
    start_date: datetime,
    end_date: datetime,
    timeframe_mins: int
) -> int:
    """Calculate number of periods from date range and timeframe"""
    time_diff = end_date - start_date
    total_minutes = int(time_diff.total_seconds() / 60)
    return int(total_minutes / timeframe_mins)


def validate_and_clip_prices(prices: np.ndarray) -> np.ndarray:
    """Validate and clip prices to prevent serialization errors"""
    return np.clip(prices, 1, 1_000_000)


def apply_performance_caps(periods: int, timeframe_mins: int, limit: Optional[int] = None) -> int:
    """Apply performance caps to prevent excessive generation"""
    # Handle limit parameter logic
    if limit is not None and limit > 0 and limit < periods:
        periods = limit

    # For very short timeframes, apply a sensible default cap
    if limit is None and timeframe_mins < 60 and periods > 2000:
        periods = 2000
    elif limit is None and periods > 10000:  # Global safety cap
        periods = 10000

    return periods
