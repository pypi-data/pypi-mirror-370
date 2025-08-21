"""
MockFlow Mathematical Models

This module contains mathematical models for generating realistic market patterns:
- Market trend generation (bull/bear/sideways)
- Volatility clustering models (GARCH-like behavior)
- Volume correlation models
"""


import numpy as np


def generate_market_trend(scenario: str, periods: int) -> np.ndarray:
    """Generate market trend multipliers based on scenario"""
    trend = np.zeros(periods)

    if scenario == "bull":
        # Upward trend with occasional pullbacks
        for i in range(periods):
            progress = i / periods
            base_growth = progress * 0.8  # 80% total growth over period
            noise = (np.random.random() - 0.5) * 0.1  # ±5% random variation
            cyclical_pullback = (
                np.sin(progress * np.pi * 8) * 0.05
            )  # Small cyclical movements
            trend[i] = base_growth + noise + cyclical_pullback

    elif scenario == "bear":
        # Downward trend with occasional rallies
        for i in range(periods):
            progress = i / periods
            base_decline = -progress * 0.6  # -60% total decline over period
            noise = (np.random.random() - 0.5) * 0.1  # ±5% random variation
            cyclical_rally = (
                np.sin(progress * np.pi * 6) * 0.08
            )  # Occasional rallies
            trend[i] = base_decline + noise + cyclical_rally

    elif scenario == "sideways":
        # Range-bound movement with cycles
        for i in range(periods):
            progress = i / periods
            cyclical_movement = (
                np.sin(progress * np.pi * 12) * 0.15
            )  # Range-bound cycles
            noise = (np.random.random() - 0.5) * 0.08  # ±4% random variation
            minor_trend = (
                np.sin(progress * np.pi * 3) * 0.05
            )  # Minor trend changes
            trend[i] = cyclical_movement + noise + minor_trend

    return trend


def generate_volatility_cycles(periods: int, timeframe: str) -> np.ndarray:
    """Generate volatility cycles with clustering effects"""
    # Base volatility map for different timeframes
    base_volatility_map = {
        "15m": 0.008,
        "30m": 0.012,
        "1h": 0.015,
        "2h": 0.020,
        "4h": 0.025,
        "12h": 0.035,
        "1d": 0.045,
        "3d": 0.065,
        "1w": 0.085,
    }
    base_volatility = base_volatility_map.get(timeframe, 0.02)

    volatility = np.zeros(periods)

    # Generate volatility clustering using GARCH-like behavior
    current_vol = base_volatility
    alpha = 0.1  # Volatility persistence
    beta = 0.8  # Mean reversion

    for i in range(periods):
        # Random shock
        shock = np.random.normal(0, 0.3)

        # Update volatility with clustering
        current_vol = (
            base_volatility
            + alpha * (shock**2)
            + beta * (current_vol - base_volatility)
        )
        current_vol = max(current_vol, base_volatility * 0.3)  # Floor
        current_vol = min(current_vol, base_volatility * 3.0)  # Ceiling

        # Add cyclical volatility patterns
        progress = i / periods
        cyclical_vol = 1 + 0.3 * np.sin(
            progress * np.pi * 15
        )  # Volatility cycles

        volatility[i] = current_vol * cyclical_vol

    return volatility


def calculate_price_series(
    base_price: float,
    trend_multipliers: np.ndarray,
    volatility_cycles: np.ndarray,
    periods: int,
) -> np.ndarray:
    """Calculate realistic price series with trend and volatility"""
    prices = np.zeros(periods)
    current_price = base_price

    for i in range(periods):
        # Apply trend
        trend_multiplier = 1 + trend_multipliers[i]
        target_price = base_price * trend_multiplier

        # Apply volatility
        volatility = volatility_cycles[i]
        price_shock = np.random.normal(0, volatility)

        # Gradual price movement towards target with shock
        price_change = (
            target_price - current_price
        ) * 0.1 + current_price * price_shock
        current_price += price_change

        prices[i] = current_price

    return prices


def generate_realistic_volume(
    periods: int, prices: np.ndarray, volatility_cycles: np.ndarray
) -> np.ndarray:
    """Generate realistic volume patterns correlated with price movements"""
    base_volume = 1000000
    volumes = np.zeros(periods)

    for i in range(periods):
        # Volume correlates with volatility
        volatility_factor = (
            1 + volatility_cycles[i] * 5
        )  # Higher volume during high volatility

        # Volume correlates with price changes
        if i > 0:
            price_change_factor = (
                1 + abs(prices[i] - prices[i - 1]) / prices[i - 1] * 10
            )
        else:
            price_change_factor = 1

        # Random volume variation
        random_factor = 0.5 + np.random.random() * 1.5  # 0.5x to 2x variation

        # Cyclical volume patterns
        progress = i / periods
        cyclical_factor = 1 + 0.3 * np.sin(progress * np.pi * 15)

        volumes[i] = (
            base_volume
            * volatility_factor
            * price_change_factor
            * random_factor
            * cyclical_factor
        )

    return volumes.astype(int)
