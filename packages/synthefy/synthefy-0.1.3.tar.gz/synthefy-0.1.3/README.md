# Synthefy Python Client

A Python client for the Synthefy API forecasting service. This package provides an easy-to-use interface for making time series forecasting requests.

## Features

- **Simple API Client**: Easy-to-use client for making forecasting requests
- **Pandas Integration**: Built-in support for pandas DataFrames
- **Type Safety**: Full type hints and Pydantic validation
- **Flexible Data Handling**: Support for multiple data sources and metadata columns

## Installation

```bash
pip install synthefy
```

## Quick Start

### Basic Usage

```python
from synthefy import SynthefyAPIClient
import pandas as pd

# Initialize the client
client = SynthefyAPIClient(api_key="your_api_key_here")

# Or use environment variable
# export SYNTHEFY_API_KEY="your_api_key_here"
client = SynthefyAPIClient()
```

### Making a Forecast Request

```python
from synthefy import SynthefyAPIClient
from synthefy.data_models import ForecastV2Request
import pandas as pd

# Create sample data
history_data = {
    'timestamp': ['2024-01-01', '2024-01-02', '2024-01-03'],
    'sales': [100, 120, 110],
    'temperature': [20, 22, 21]
}

target_data = {
    'timestamp': ['2024-01-04', '2024-01-05', '2024-01-06'],
    'sales': [None, None, None],  # Values to forecast
    'temperature': [23, 24, 22]   # Known future values
}

history_df = pd.DataFrame(history_data)
target_df = pd.DataFrame(target_data)

# Create request using the convenience method
response = client.forecast_dfs(
    history_dfs=[history_df],
    target_dfs=[target_df],
    target_col='sales',
    timestamp_col='timestamp',
    metadata_cols=['temperature'],
    leak_cols=[],  # No leak columns in this example
    model='sfm_moe'
)

# response is a list of DataFrames with forecasts
forecast_df = response[0]
print(forecast_df)
```

### Advanced Usage with Multiple Data Sources

```python
# Multiple data sources
history_dfs = [history_df1, history_df2, history_df3]
target_dfs = [target_df1, target_df2, target_df3]

response = client.forecast_dfs(
    history_dfs=history_dfs,
    target_dfs=target_dfs,
    target_col='revenue',
    timestamp_col='date',
    metadata_cols=['marketing_spend', 'competitor_price'],
    leak_cols=['marketing_spend'],  # This column is known in the future
    model='sfm_moe'
)

# Each DataFrame in response corresponds to one data source
for i, forecast_df in enumerate(response):
    print(f"Forecast for data source {i}:")
    print(forecast_df)
```

## API Reference

### SynthefyAPIClient

The main client class for interacting with the Synthefy API.

#### Methods

- `forecast(request: ForecastV2Request) -> ForecastV2Response`: Make a direct forecast request
- `forecast_dfs(...) -> List[pd.DataFrame]`: Convenience method for working with pandas DataFrames

#### Parameters

- `api_key`: Your Synthefy API key (can also be set via `SYNTHEFY_API_KEY` environment variable)
- `timeout`: Request timeout in seconds (default: 120.0)

## Configuration

### Environment Variables

- `SYNTHEFY_API_KEY`: Your Synthefy API key

## Support

For support and questions:
- Email: contact@synthefy.com

## License

MIT License - see LICENSE file for details. 