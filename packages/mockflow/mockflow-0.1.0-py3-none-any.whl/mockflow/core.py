"""
MockFlow Core Generation Engine

This module contains the main data generation functions and orchestrates
the overall mock data creation process.
"""

from datetime import datetime, timedelta
from typing import Literal, Optional, cast

import numpy as np
import pandas as pd

from .models import (
    calculate_price_series,
    generate_market_trend,
    generate_realistic_volume,
    generate_volatility_cycles,
)
from .utils import (
    apply_performance_caps,
    calculate_periods_from_date_range,
    calculate_periods_from_days,
    generate_ohlc_data,
    generate_timestamps,
    get_timeframe_minutes,
    validate_and_clip_prices,
)

# Type definitions
MarketScenario = Literal["bull", "bear", "sideways", "auto"]


def generate_mock_data(
    symbol: str,
    timeframe: str = "1h",
    limit: Optional[int] = None,
    days: int = 30,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    scenario: MarketScenario = "auto",
) -> pd.DataFrame:
    """
    Generate mock price data for development and testing with realistic
    patterns

    Args:
        symbol: Trading symbol (e.g., BTCUSDT)
        timeframe: Timeframe for candles (15m, 30m, 1h, 2h, 4h, 12h, 1d,
            3d, 1w)
        limit: Number of candles to generate
               (None for auto based on days/date range)
        days: Number of days of historical data to generate (default: 30,
            max: 365, ignored if start_date/end_date provided)
        start_date: Absolute start date for data range (optional)
        end_date: Absolute end date for data range (optional)
        scenario: Market scenario - "bull", "bear", "sideways", or "auto" for
            random selection

    Returns:
        DataFrame with OHLCV data and timestamp index
    """
    # Get timeframe in minutes
    timeframe_mins = get_timeframe_minutes(timeframe)

    # Determine time range and periods calculation
    if start_date and end_date:
        # Absolute time range mode
        if start_date >= end_date:
            raise ValueError("start_date must be before end_date")

        # Calculate number of periods from date range
        periods = calculate_periods_from_date_range(start_date, end_date, timeframe_mins)
        actual_start_date = start_date

    else:
        # Relative time range mode (existing logic)
        # Validate days parameter
        if days <= 0:
            raise ValueError("Days parameter must be positive")
        if days > 365:
            raise ValueError(
                "Days parameter cannot exceed 365 for performance reasons"
            )

        # Calculate periods from days
        periods = calculate_periods_from_days(days, timeframe_mins)

        # Use fixed reference date for consistency
        reference_date = datetime(2024, 1, 1)
        actual_start_date = reference_date - timedelta(days=days)

    # Apply performance caps and handle limit
    periods = apply_performance_caps(periods, timeframe_mins, limit)

    # Use different seeds for different timeframes to create distinct patterns
    np.random.seed(42 + hash(timeframe) % 1000)
    base_price = 50000

    # Select scenario automatically if "auto"
    if scenario == "auto":
        # Use deterministic choice based on symbol for consistency
        scenario_seed = hash(symbol + timeframe) % 3
        scenario = cast(MarketScenario, ["bull", "bear", "sideways"][scenario_seed])

    # Generate realistic market trend based on scenario
    trend_multipliers = generate_market_trend(scenario, periods)

    # Generate volatility cycles with clustering
    volatility_cycles = generate_volatility_cycles(periods, timeframe)

    # Calculate prices with trend and volatility
    prices = calculate_price_series(
        base_price, trend_multipliers, volatility_cycles, periods
    )

    # Ensure prices stay within reasonable bounds
    prices = validate_and_clip_prices(prices)

    # Generate realistic volume patterns
    volumes = generate_realistic_volume(periods, prices, volatility_cycles)

    # Generate realistic OHLC data with intrabar movement
    data = generate_ohlc_data(prices, volatility_cycles, volumes, periods)

    # Create datetime index using the calculated start date
    timestamps = generate_timestamps(periods, timeframe_mins, actual_start_date)

    return pd.DataFrame(
        data,
        index=timestamps,
        columns=["open", "high", "low", "close", "volume"],
    )
