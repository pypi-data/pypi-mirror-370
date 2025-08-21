# MockFlow

Professional-grade Python package for generating realistic financial time series data for backtesting, simulation, and development purposes.

## Features

- **Realistic Market Patterns**: Generate bull, bear, and sideways market scenarios
- **Advanced Volatility Modeling**: GARCH-like volatility clustering with regime switching
- **Volume Correlation**: Realistic volume patterns correlated with price movements
- **Seed-based Reproducibility**: Deterministic generation for consistent testing
- **Multiple Timeframes**: Support for 15m to 1w timeframes
- **OHLCV Data**: Complete OHLC + Volume data generation

## Installation

```bash
pip install mockflow
```

For development:
```bash
pip install mockflow[dev]
```

## Quick Start

```python
from mockflow import generate_mock_data

# Generate 30 days of hourly mock data
data = generate_mock_data(
    symbol="BTCUSDT",
    timeframe="1h", 
    days=30,
    scenario="auto"  # auto-select bull/bear/sideways
)

print(data.head())
```

## API Reference

### Main Function: `generate_mock_data()`

```python
def generate_mock_data(
    symbol: str,
    timeframe: str,
    days: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: Optional[int] = None,
    scenario: str = "auto"
) -> pd.DataFrame
```

**Parameters:**

- **`symbol`** (str): Trading pair symbol (e.g., "BTCUSDT", "ETHUSD")
- **`timeframe`** (str): Candle timeframe. Supported values:
  - `"15m"`, `"30m"`, `"1h"`, `"2h"`, `"4h"`, `"6h"`, `"8h"`, `"12h"`, `"1d"`, `"3d"`, `"1w"`
- **`days`** (int, optional): Number of days to generate. Alternative to date range.
- **`start_date`** (datetime, optional): Start date for generation. Used with `end_date`.
- **`end_date`** (datetime, optional): End date for generation. Used with `start_date`.
- **`limit`** (int, optional): Exact number of candles to generate.
- **`scenario`** (str): Market scenario. Options:
  - `"auto"`: Automatically select scenario based on symbol/timeframe
  - `"bull"`: Sustained upward trend with pullbacks
  - `"bear"`: Sustained downward trend with rallies
  - `"sideways"`: Range-bound movement with cyclical patterns

**Returns:**
- `pd.DataFrame`: OHLCV data with datetime index

**Raises:**
- `ValueError`: Invalid parameters or unsupported timeframe
- `TypeError`: Incorrect parameter types

## Usage Examples

### Basic Generation

```python
import mockflow

# Generate data with specific scenario
data = mockflow.generate_mock_data(
    symbol="ETHUSD",
    timeframe="4h",
    days=90,
    scenario="bull"  # "bull", "bear", "sideways", "auto"
)
```

### Date Range Generation

```python
from datetime import datetime

data = mockflow.generate_mock_data(
    symbol="BTCUSDT",
    timeframe="1d",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 3, 31)
)
```

### With Custom Limit

```python
data = mockflow.generate_mock_data(
    symbol="SOLUSD",
    timeframe="15m",
    limit=1000  # Generate exactly 1000 candles
)
```

### Seed-based Reproducibility

```python
import numpy as np

# Set seed for reproducible data
np.random.seed(42)
data1 = mockflow.generate_mock_data("BTCUSDT", "1h", days=7)

np.random.seed(42)  
data2 = mockflow.generate_mock_data("BTCUSDT", "1h", days=7)

# data1 and data2 are identical
assert data1.equals(data2)
```

## Output Format

Returns a pandas DataFrame with:
- **Index**: Datetime timestamps
- **Columns**: `open`, `high`, `low`, `close`, `volume`
- **Data Types**: Float64 for OHLC, Int64 for volume

## Market Scenarios

- **Bull Market**: Sustained upward trend with occasional pullbacks
- **Bear Market**: Sustained downward trend with occasional rallies  
- **Sideways Market**: Range-bound movement with cyclical patterns
- **Auto**: Automatically selects scenario based on symbol/timeframe

## Advanced Features

### Volatility Clustering

The package implements GARCH-like volatility clustering where:
- High volatility periods tend to be followed by high volatility
- Low volatility periods tend to be followed by low volatility
- Realistic intrabar movement with proper OHLC relationships

### Volume Patterns

Volume generation includes:
- Correlation with price volatility (higher volume during volatile periods)
- Correlation with price changes (higher volume on large moves)
- Cyclical volume patterns
- Random variation within realistic bounds

## Use Cases

### Backtesting Strategy Development

```python
import mockflow
import pandas as pd

# Generate test data for strategy backtesting
def create_backtest_dataset():
    # Multiple market conditions for robust testing
    bull_data = mockflow.generate_mock_data("BTCUSDT", "4h", days=180, scenario="bull")
    bear_data = mockflow.generate_mock_data("BTCUSDT", "4h", days=180, scenario="bear")
    sideways_data = mockflow.generate_mock_data("BTCUSDT", "4h", days=180, scenario="sideways")
    
    # Combine for comprehensive testing
    full_dataset = pd.concat([bull_data, bear_data, sideways_data], ignore_index=True)
    return full_dataset

# Test your strategy
data = create_backtest_dataset()
print(f"Generated {len(data)} candles for backtesting")
```

### Multi-Asset Portfolio Testing

```python
# Create correlated assets for portfolio testing
symbols = ["BTCUSDT", "ETHUSD", "ADAUSDT", "DOTUSD"]
portfolio_data = {}

for symbol in symbols:
    portfolio_data[symbol] = mockflow.generate_mock_data(
        symbol=symbol,
        timeframe="1d",
        days=365,
        scenario="auto"
    )

print("Portfolio datasets ready for analysis")
```

### Data Validation

```python
# Validate generated data quality
def validate_ohlcv_data(data):
    """Validate OHLCV data structure and relationships"""
    assert all(data['high'] >= data['low']), "High must be >= Low"
    assert all(data['high'] >= data['open']), "High must be >= Open"
    assert all(data['high'] >= data['close']), "High must be >= Close"
    assert all(data['low'] <= data['open']), "Low must be <= Open"
    assert all(data['low'] <= data['close']), "Low must be <= Close"
    assert all(data['volume'] > 0), "Volume must be positive"
    print("Data validation passed")

# Test data quality
test_data = mockflow.generate_mock_data("BTCUSDT", "1h", limit=100)
validate_ohlcv_data(test_data)
```

### Performance Benchmarking

```python
import time

# Benchmark generation performance
def benchmark_generation():
    start_time = time.time()
    
    large_dataset = mockflow.generate_mock_data(
        symbol="BTCUSDT",
        timeframe="1h",
        limit=10000  # 10k candles
    )
    
    end_time = time.time()
    generation_time = end_time - start_time
    
    print(f"Generated {len(large_dataset)} candles in {generation_time:.2f}s")
    print(f"Rate: {len(large_dataset)/generation_time:.0f} candles/second")

benchmark_generation()
```

## Requirements

- Python 3.8+
- numpy >= 1.20.0
- pandas >= 1.3.0

## Development

### Installation

```bash
git clone <repository-url>
cd mockflow
pip install -e .[dev]
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=mockflow --cov-report=html

# Run specific test categories
pytest -m contract        # API contract tests
pytest -m integration     # Integration tests
```

### Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy .

# Code formatting
black .
```

### Package Building

```bash
# Build distribution packages
python -m build

# Check package metadata
twine check dist/*
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Ensure tests pass: `pytest`
5. Check code quality: `ruff check . && mypy .`
6. Submit pull request

## Support

For issues and questions, please use the GitHub issue tracker.