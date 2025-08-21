# Universal Timeseries Transformer

A Python package that provides a universal interface for transforming and manipulating time series data. This package offers flexible and efficient tools for handling various types of time series data transformations.

## Version Updates

### v0.3.9 (2025-01-27)
- Enhanced function stability and error handling in timestamp conversion
- Improved type checking with numpy integer and floating types support
- Added UTC timezone handling for consistent datetime conversion
- Optimized validation by checking only first 5 elements for performance
- Better threshold values for automatic unit detection (seconds, milliseconds, microseconds, nanoseconds)

### v0.3.8 (2025-01-27)
- Enhanced unix timestamp conversion for broader compatibility
- Added automatic unit detection (seconds, milliseconds, nanoseconds) in map_unix_timestamps_to_datetimes
- Improved error handling and validation in timestamp conversion functions
- Added support for pd.Index type in date conversion functions

### v0.3.0 (2025-07-03)
- Standardized timestamp format aliases across the package
- Updated FORMAT_ALIASES to use 'timestamp' instead of 'unix'
- Improved documentation for transform_timeseries_index function
- Completed timestamp conversion functionality with consistent naming

### v0.2.10 (2025-07-03)
- Fixed compatibility issues in PricesMatrix with TimeseriesMatrix changes
- Updated constructor parameter handling for better inheritance

### v0.2.9 (2025-07-03)
- Standardized property names in TimeseriesMatrix class
- Added 'dt' property as an alias for 'datetime'
- Added 'timestamp' property as the standard name for 'unixtime'
- Simplified TimeseriesMatrix by removing reference-based methods
- Improved index naming in transformed dataframes

### v0.2.8 (2025-06-23)
- Implemented cached_property decorator for lazy loading attributes
- Added type hints for better code readability and IDE support
- Improved documentation with class docstrings
- Renamed historical_dates to historical_date_pairs for consistency
- Added MANIFEST.in file for better package distribution

### v0.2.7 (2025-06-17)
- Updated string_date_controller dependency to version 0.2.7
- Modified historical_dates property to use get_all_data_historical_date_pairs function
- Added yearly_date_pairs property to PricesMatrix class

### v0.2.6 (2025-06-15)
- Renamed functions in timeseries_splitter module for better clarity and consistency
- Changed 'split_timeseries_to_two_columned_timeseries' to 'split_timeseries_to_pair_timeseries'
- Updated related partial functions with the new naming convention

### v0.2.5 (2025-06-15)
- Added timeseries_splitter module for splitting timeseries data into two-columned format
- Fixed incomplete function in timeseries_splitter module

### v0.2.4 (2025-06-08)
- Modified return calculation functions to display returns in percentage format (multiplied by 100)
- Updated all return-related functions in timeseries_application.py

### v0.2.3 (2025-06-04)
- Added new properties to PricesMatrix class: ytd_date_pairs, date_inception, date_end
- Updated string_date_controller dependency to version 0.2.3 or higher

### v0.2.2 (2025-06-04)
- Enhanced exception handling in PricesMatrix class
- Added set_date_ref method for better date reference management

### v0.2.1 (2025-06-03)
- Added monthly_date_pairs property to PricesMatrix class for convenient monthly date analysis
- Updated string_date_controller dependency to version 0.2.1 or higher

### v0.2.0 (2025-06-03)
- Major version update as the module reaches maturity
- Added date_ref property to PricesMatrix class for improved date reference handling
- All features from previous versions are now stable and production-ready

### v0.1.10 (2025-06-03)
- Fixed bug in PricesMatrix class to use correct string_date_controller function
- Updated to use get_all_data_historical_dates function from string_date_controller 0.2.0

### v0.1.9 (2025-06-02)
- Fixed bug in PricesMatrix class related to historical dates calculation
- Updated to use correct string_date_controller functions

### v0.1.8 (2025-06-02)
- Added PricesMatrix class extending TimeseriesMatrix for price data handling
- Enhanced matrix representation capabilities with historical dates support

### v0.1.7 (2025-06-02)
- Improved TimeseriesMatrix class with optimized property handling
- Updated string_date_controller dependency to version 0.2.0 or higher
- Removed unused date_calculus module

### v0.1.6 (2025-06-01)
- Added timeseries_slicer module with date-based and index-based slicing functions
- Added timeseries_extender module with enhanced date extension functionality
- Improved .gitignore to exclude Jupyter notebook files

### v0.1.5 (2025-05-30)
- Added TimeseriesMatrix class for matrix representation of time series data
- Enhanced data access with row, column, and component selection methods
- Added format conversion methods (datetime, unixtime, string)

### v0.1.4 (2025-05-28)
- Added verbose option to control log output
- Enhanced timeseries extension functionality
- Improved code readability and documentation

### v0.1.3 (2025-05-19)
- Added new timeseries_application module with financial calculations
- Added functions for returns and cumulative returns calculation

### v0.1.2 (2025-05-19)
- Improved stability and performance optimization
- Enhanced type checking functionality
- Documentation improvements

## Features

- Index Transformer
  - Flexible time index manipulation
  - Date range operations
  - Frequency conversion
- DataFrame Transformer
  - Universal interface for time series operations
  - Data alignment and merging
  - Efficient data transformation
- Timeseries Basis
  - Core functionality for time series manipulation
  - Common time series operations

## Installation

You can install the package using pip:

```bash
pip install universal-timeseries-transformer
```

## Requirements

- Python >= 3.8
- Dependencies:
  - pandas
  - numpy

## Usage Examples

### 1. Basic Time Series Transformation

```python
from universal_timeseries_transformer import IndexTransformer, DataFrameTransformer
import pandas as pd

# Create sample time series data
df = pd.DataFrame({'value': [1, 2, 3, 4]},
                  index=pd.date_range('2025-01-01', periods=4))

# Transform time series index
index_transformer = IndexTransformer(df)
weekly_data = index_transformer.to_weekly()

# Apply data transformations
df_transformer = DataFrameTransformer(weekly_data)
result = df_transformer.rolling_mean(window=2)
```

### 2. Advanced Time Series Operations

```python
from universal_timeseries_transformer import TimeseriesBasis

# Initialize time series basis
ts_basis = TimeseriesBasis(df)

# Perform complex transformations
transformed_data = ts_basis.transform()
```
)

# Find funds with borrowings
funds_with_borrowings = search_funds_having_borrowings(date_ref='2025-02-21')

# Get borrowing details
fund_code = '100075'
borrowing_details = get_borriwings_by_fund(fund_code=fund_code, date_ref='2025-02-21')
```

### 3. Check Repo Agreements

```python
from financial_dataset_preprocessor import (
    search_funds_having_repos,
    get_repos_by_fund
)

# Find funds with repos
funds_with_repos = search_funds_having_repos(date_ref='2025-02-21')

# Get repo details for a specific fund
fund_code = '100075'
repo_details = get_repos_by_fund(fund_code=fund_code, date_ref='2025-02-21')
```

## Development

To set up the development environment:

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## License

This project is licensed under a proprietary license. All rights reserved.

### Terms of Use

- Source code viewing and forking is allowed
- Commercial use is prohibited without explicit permission
- Redistribution or modification of the code is prohibited
- Academic and research use is allowed with proper attribution

## Author

**June Young Park**  
AI Management Development Team Lead & Quant Strategist at LIFE Asset Management

LIFE Asset Management is a hedge fund management firm that integrates value investing and engagement strategies with quantitative approaches and financial technology, headquartered in Seoul, South Korea.

### Contact

- Email: juneyoungpaak@gmail.com
- Location: TWO IFC, Yeouido, Seoul
