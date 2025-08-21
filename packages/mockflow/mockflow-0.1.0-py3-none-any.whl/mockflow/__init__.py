"""
MockFlow - Financial Time Series Mock Data Generation Package

A professional-grade Python package for generating realistic financial time series data
for backtesting, simulation, and development purposes.

Main Components:
- Core generation engine with realistic market patterns
- Mathematical models (trend, volatility, volume)
- Market scenarios (bull, bear, sideways markets)
- Utility functions for timestamp generation and validation
"""

__version__ = "0.1.0"
__author__ = "Conflux ML Engine Team"

# Import main public API
# Import key types and enums
from .core import MarketScenario, generate_mock_data

# Package-level exports
__all__ = [
    "generate_mock_data",
    "MarketScenario",
    "__version__"
]
