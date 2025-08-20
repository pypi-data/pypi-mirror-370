# statflow

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/statflow.svg)](https://pypi.org/project/statflow/)

**statflow** is a comprehensive Python toolkit for statistical analysis, time series processing, and climatological data analysis. Built with modern scientific computing standards, it provides robust tools for statistical operations, signal processing, and specialised climatology workflows. The package emphasises professional-grade statistical computing with comprehensive type annotations, efficient algorithms, and extensive climatological indicators.

## Features

- **Core Statistical Analysis**:
  - Advanced time series analysis with periodic statistics and trend detection
  - Statistical hypothesis testing (Z-tests, Chi-squared tests)
  - Moving operations (moving averages, window sums) for multi-dimensional data
  - Comprehensive interpolation methods (polynomial, spline, linear) for NumPy, pandas, and xarray
  - Signal processing with filtering (low-pass, high-pass, band-pass) and whitening techniques
  - Regression analysis tools and approximation techniques

- **Climatological Analysis**:
  - Climate indicator calculations (WSDI, SU, CSU, FD, TN, RR, CWD, HWD)
  - Periodic climatological statistics with multi-frequency support (hourly, daily, monthly, seasonal, yearly)
  - Representative series generation including Hourly Design Year (HDY) following ISO 15927-4:2005
  - Simple bias correction techniques with absolute and relative delta methods
  - Comprehensive meteorological variable calculations (heat index, wind chill, dew point, specific humidity)
  - Bioclimatic variable computation (19 standard bioclimatic indicators)

- **Advanced Data Processing**:
  - Multi-format data support (pandas DataFrames, xarray Datasets/DataArrays, NumPy arrays)
  - Cumulative data decomposition and time series transformation
  - Consecutive occurrence analysis for extreme event detection
  - Autocorrelation analysis with optimised algorithms for large datasets
  - Professional error handling with comprehensive input validation

- **Signal Processing & Filtering**:
  - Signal whitening techniques (classic, sklearn PCA, ZCA whitening)
  - Multiple filtering approaches with frequency domain processing
  - Fourier transform-based band-pass filtering methods
  - Noise handling and signal enhancement tools

## Installation

### Prerequisites

- **Python 3.10+**: Required for modern type annotations and features
- **Core Dependencies**: NumPy, pandas, scipy, xarray for scientific computing
- **Additional Dependencies**: filewise, pygenutils (project packages)

### For Regular Users

**For regular users** who want to use the package in their projects:

```bash
pip install statflow
```

This automatically installs `statflow` and all its dependencies from PyPI and GitHub repositories.

### Package Updates

To stay up-to-date with the latest version of this package, simply run:

```bash
pip install --upgrade statflow
```

## Development Setup

### For Contributors and Developers

If you're planning to contribute to the project or work with the source code, follow these setup instructions:

#### Quick Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/EusDancerDev/statflow.git
cd statflow

# Install in editable mode with all dependencies
pip install -e .
```

**Note**: The `-e` flag installs the package in "editable" mode, meaning changes to the source code are immediately reflected without reinstalling.

This will automatically install all dependencies with version constraints.

#### Alternative Setup (Explicit Git Dependencies)

If you prefer to use the explicit development requirements file:

```bash
# Clone the repository
git clone https://github.com/EusDancerDev/statflow.git
cd statflow

# Install development dependencies from requirements-dev.txt
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .
```

This approach gives you the latest development versions of all interdependent packages for testing and development.

If you encounter import errors after cloning:

1. **For regular users**: Run `pip install statflow` (all dependencies included)
2. **For developers**: Run `pip install -e .[dev]` to include development dependencies
3. **Verify Python environment**: Make sure you're using a compatible Python version (3.10+)
4. **Check scientific computing libraries**: Ensure scipy, xarray, and other scientific packages are available

### Verify Installation

To verify that your installation is working correctly, you can run this quick test:

```python
# Test script to verify installation
try:
    import statflow
    from filewise.general.introspection_utils import get_type_str
    from pygenutils.arrays_and_lists.data_manipulation import flatten_list
    from statflow.core.time_series import periodic_statistics
    
    print("✅ All imports successful!")
    print(f"✅ statflow version: {statflow.__version__}")
    print("✅ Installation is working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 For regular users: pip install statflow")
    print("💡 For developers: pip install -e .[dev]")
```

### Implementation Notes

This project implements a **dual-approach dependency management** system:

- **Production Dependencies**: Version-constrained dependencies for PyPI compatibility
- **Development Dependencies**: Git-based dependencies for latest development versions
- **Installation Methods**:
  - **Regular users**: Simple `pip install statflow` with all dependencies included
  - **Developers**: `pip install -e .[dev]` for latest Git versions and development tools
- **PyPI Compatibility**: All packages can be published without Git dependency issues
- **Development Flexibility**: Contributors get access to latest versions for testing and development

## Usage

### Core Statistical Analysis

```python
from statflow.core.time_series import periodic_statistics, autocorrelate
from statflow.core.statistical_tests import z_test_two_means, chi_squared_test
import pandas as pd
import numpy as np

# Load your time series data
df = pd.read_csv("your_data.csv", parse_dates=['date'])

# Calculate periodic statistics
monthly_means = periodic_statistics(
    df, 
    statistic="mean", 
    freq="M",  # Monthly frequency
    drop_date_idx_col=False
)

# Perform hypothesis testing
sample1 = np.random.normal(10, 2, 100)
sample2 = np.random.normal(12, 2, 100)
z_stat, p_value, result = z_test_two_means(sample1, sample2)
print(f"Z-test result: {result}")

# Autocorrelation analysis
autocorr = autocorrelate(df['temperature'].values, twosided=False)
```

### Signal Processing

```python
from statflow.core.signal_processing import low_pass_filter, band_pass1, signal_whitening
from statflow.core.moving_operations import moving_average, window_sum

# Apply signal filtering
filtered_signal = low_pass_filter(noisy_data, window_size=5)

# Band-pass filtering in frequency domain
band_filtered = band_pass1(
    original_signal, 
    timestep=0.1, 
    low_freq=0.1, 
    high_freq=2.0
)

# Signal whitening for decorrelation
whitened_data = signal_whitening(signal_data, method="classic")

# Moving operations for time series
moving_avg = moving_average(time_series, N=7)  # 7-day moving average
cumulative_sum = window_sum(data_array, N=30)  # 30-point window sum
```

### Interpolation Methods

```python
from statflow.core.interpolation_methods import interp_np, interp_pd, interp_xr, polynomial_fitting

# NumPy array interpolation
interpolated_np = interp_np(
    data_with_gaps, 
    method='spline', 
    order=3
)

# Pandas DataFrame interpolation
interpolated_pd = interp_pd(
    df_with_missing, 
    method='polynomial', 
    order=2
)

# Polynomial fitting with edge preservation
fitted_data = polynomial_fitting(
    y_values, 
    poly_ord=3, 
    fix_edges=True
)
```

### Climatological Analysis

```python
from statflow.fields.climatology.indicators import calculate_WSDI, calculate_SU, calculate_hwd
from statflow.fields.climatology.periodic_climat_stats import climat_periodic_statistics
from statflow.fields.climatology.variables import calculate_heat_index, biovars

# Climate indicators
# Warm Spell Duration Index
wsdi = calculate_WSDI(
    daily_tmax_data, 
    tmax_threshold=30.0, 
    min_consec_days=6
)

# Summer Days count
summer_days = calculate_SU(daily_tmax_data, tmax_threshold=25.0)

# Heat wave analysis
hwd_events, total_hwd = calculate_hwd(
    tmax_data, tmin_data, 
    max_thresh=35.0, min_thresh=20.0, 
    dates=date_index, min_days=3
)

# Climatological statistics
monthly_climat = climat_periodic_statistics(
    climate_data,
    statistic="mean",
    time_freq="monthly",
    keep_std_dates=True
)

# Meteorological calculations
heat_idx = calculate_heat_index(temperature, humidity, unit="celsius")
dew_point = calculate_dew_point(temperature, humidity)

# Bioclimatic variables (19 standard indicators)
bioclim_vars = biovars(
    tmax_monthly_climat, 
    tmin_monthly_climat, 
    precip_monthly_climat
)
```

### Bias Correction

```python
from statflow.fields.climatology.simple_bias_correction import calculate_and_apply_deltas

# Simple bias correction between observed and reanalysis data
corrected_data = calculate_and_apply_deltas(
    observed_series=obs_data,
    reanalysis_series=reanalysis_data,
    time_freq="monthly",
    delta_type="absolute",  # or "relative"
    statistic="mean",
    preference="observed",  # treat observations as truth
    season_months=[12, 1, 2]  # for seasonal analysis
)
```

### Representative Series (HDY)

```python
from statflow.fields.climatology.representative_series import calculate_HDY, hdy_interpolation

# Calculate Hourly Design Year following ISO 15927-4:2005
hdy_dataframe, selected_years = calculate_HDY(
    hourly_climate_df,
    varlist=['date', 'temperature', 'humidity', 'wind_speed'],
    varlist_primary=['date', 'temperature', 'humidity'],
    drop_new_idx_col=True
)

# Interpolate between months to smooth transitions
hdy_smooth, wind_dir_smooth = hdy_interpolation(
    hdy_dataframe,
    selected_years,
    previous_month_last_time_range="20:23",
    next_month_first_time_range="0:3",
    varlist_to_interpolate=['temperature', 'humidity'],
    polynomial_order=3
)
```

## Project Structure

The package is organised as a comprehensive statistical analysis toolkit:

```text
statflow/
├── core/                          # Core statistical functionality
│   ├── approximation_techniques.py    # Curve fitting and approximation methods
│   ├── interpolation_methods.py       # Multi-format interpolation tools
│   ├── moving_operations.py           # Moving averages and window operations
│   ├── regressions.py                 # Regression analysis tools
│   ├── signal_processing.py           # Signal filtering and processing
│   ├── statistical_tests.py           # Hypothesis testing functions
│   └── time_series.py                 # Time series analysis and statistics
├── fields/                        # Domain-specific analysis modules
│   └── climatology/                   # Climate data analysis tools
│       ├── indicators.py                  # Climate indicators (WSDI, SU, etc.)
│       ├── periodic_climat_stats.py       # Climatological statistics
│       ├── representative_series.py       # HDY and representative data
│       ├── simple_bias_correction.py      # Bias correction methods
│       └── variables.py                   # Meteorological calculations
├── distributions/                 # Statistical distributions (future expansion)
├── utils/                         # Utility functions and helpers
│   └── helpers.py                     # Support functions for analysis
├── CHANGELOG.md                   # Detailed version history
├── VERSIONING.md                  # Version management documentation
└── README.md                      # Package documentation
```

## Key Capabilities

### 1. Time Series Analysis

- **Periodic Statistics**: Calculate statistics across multiple time frequencies with robust datetime handling
- **Cumulative Data Processing**: Decompose cumulative time series into individual values
- **Consecutive Analysis**: Detect and count consecutive occurrences of extreme events
- **Autocorrelation**: Optimised autocorrelation analysis for pattern detection

### 2. Statistical Testing

- **Hypothesis Tests**: Z-tests for mean comparison, Chi-squared tests for independence
- **Robust Validation**: Comprehensive input validation and error handling
- **Multiple Data Types**: Support for NumPy arrays, pandas Series, and more

### 3. Signal Processing

- **Filtering Suite**: Low-pass, high-pass, and band-pass filters with multiple implementation methods
- **Signal Enhancement**: Whitening techniques for decorrelation and noise reduction
- **Frequency Domain**: Fourier transform-based processing for advanced filtering

### 4. Climatological Indicators

- **Standard Indices**: WSDI, SU, CSU, FD, TN, RR, CWD following international standards
- **Heat Wave Analysis**: Comprehensive heat wave detection with intensity metrics
- **Bioclimatic Variables**: Complete set of 19 bioclimatic indicators for ecological studies

### 5. Meteorological Calculations

- **Atmospheric Variables**: Heat index, wind chill, dew point, specific humidity
- **Magnus Formula**: Accurate saturation vapor pressure calculations
- **Multi-Unit Support**: Celsius/Fahrenheit and metric/imperial unit systems

### 6. Data Processing Excellence

- **Multi-Format Support**: Seamless handling of pandas, xarray, and NumPy data structures
- **Type Safety**: Modern PEP-604 type annotations throughout the codebase
- **Error Handling**: Comprehensive validation with descriptive error messages

## Advanced Features

### Professional Climatology Workflows

```python
# Complete climatological analysis workflow
from statflow.fields.climatology import *

# 1. Calculate basic climate indicators
indicators = {
    'summer_days': calculate_SU(daily_tmax, 25.0),
    'frost_days': calculate_FD(daily_tmin, 0.0),
    'tropical_nights': calculate_TN(daily_tmin, 20.0),
    'wet_days': calculate_RR(daily_precip, 1.0)
}

# 2. Generate climatological statistics
climat_stats = climat_periodic_statistics(
    climate_dataframe,
    statistic="mean",
    time_freq="seasonal",
    season_months=[6, 7, 8]  # Summer season
)

# 3. Apply bias correction
corrected_projections = calculate_and_apply_deltas(
    observed_data, model_data,
    time_freq="monthly",
    delta_type="relative",
    preference="observed"
)

# 4. Calculate meteorological variables
heat_stress = calculate_heat_index(temperature, humidity)
comfort_metrics = calculate_wind_chill(temperature, wind_speed)
```

### High-Performance Time Series Processing

```python
# Optimised for large datasets
from statflow.core.time_series import periodic_statistics, consec_occurrences_maxdata

# Process multi-dimensional climate data
large_dataset = xr.open_dataset("large_climate_file.nc")

# Efficient periodic statistics with proper memory management
monthly_stats = periodic_statistics(
    large_dataset,
    statistic="mean",
    freq="M",
    groupby_dates=True
)

# Vectorised extreme event analysis
extreme_events = consec_occurrences_maxdata(
    temperature_array,
    max_threshold=35.0,
    min_consec=3,
    calc_max_consec=True
)
```

## Dependencies

### Core Dependencies

- **numpy**: Numerical computing and array operations
- **pandas**: Data manipulation and time series handling
- **scipy**: Statistical functions and signal processing
- **xarray**: Multi-dimensional data handling for climate data

### Project Dependencies

- **filewise**: File operations and introspection utilities
- **pygenutils**: General-purpose utilities for arrays, strings, and time handling
- **paramlib**: Parameter management and global constants

### Optional Dependencies

- **scikit-learn**: For advanced whitening techniques in signal processing
- **matplotlib**: For plotting and visualisation (user's choice)

## Integration Examples

### Climate Data Analysis Pipeline

```python
import statflow as sf
import xarray as xr
import pandas as pd

# Load climate model data
climate_data = xr.open_dataset("climate_model_output.nc")

# 1. Time series analysis
trend_analysis = sf.core.time_series.periodic_statistics(
    climate_data.temperature,
    statistic="mean",
    freq="Y"  # Annual trends
)

# 2. Calculate climate indicators
heat_waves = sf.fields.climatology.indicators.calculate_hwd(
    climate_data.tasmax.values,
    climate_data.tasmin.values,
    max_thresh=35.0,
    min_thresh=20.0,
    dates=climate_data.time,
    min_days=3
)

# 3. Signal processing for trend detection
filtered_temp = sf.core.signal_processing.low_pass_filter(
    climate_data.temperature.values,
    window_size=10
)

# 4. Statistical validation
temp_stats = sf.core.statistical_tests.z_test_two_means(
    historical_period,
    future_period
)
```

### Multi-Scale Statistical Analysis

```python
# Analyse data across multiple temporal scales
scales = ['hourly', 'daily', 'monthly', 'seasonal']
results = {}

for scale in scales:
    results[scale] = sf.fields.climatology.climat_periodic_statistics(
        meteorological_data,
        statistic="mean",
        time_freq=scale,
        keep_std_dates=True
    )

# Cross-scale correlation analysis
correlations = {}
for i, scale1 in enumerate(scales):
    for scale2 in scales[i+1:]:
        corr_data = sf.core.time_series.autocorrelate(
            results[scale1].values.flatten()
        )
        correlations[f"{scale1}_{scale2}"] = corr_data
```

## Best Practices

### Data Preparation

- Ensure consistent datetime indexing for time series analysis
- Validate data quality and handle missing values appropriately
- Use appropriate data structures (pandas for tabular, xarray for multi-dimensional)
- Consider memory usage for large climate datasets

### Statistical Analysis

- Choose appropriate statistical tests based on data distribution and assumptions
- Use robust error handling and validate input parameters
- Consider multiple time scales for comprehensive climate analysis
- Apply proper bias correction techniques for model-observation comparisons

### Performance Optimisation

- Leverage vectorised operations for large datasets
- Use appropriate interpolation methods based on data characteristics
- Consider parallel processing for independent calculations
- Monitor memory usage with large climate model outputs

### Climatological Standards

- Follow international standards for climate indicator calculations
- Use appropriate thresholds for regional climate conditions
- Document methodology and parameter choices
- Validate results against established climatological references

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request for:

- New statistical methods or climate indicators
- Performance improvements and optimisations
- Enhanced documentation and examples
- Bug fixes and error handling improvements

### Development Guidelines

1. **Follow Type Annotations**: Use modern PEP-604 syntax for type hints
2. **Maintain Documentation**: Comprehensive docstrings with examples
3. **Add Tests**: Unit tests for new functionality
4. **Performance Considerations**: Optimise for large scientific datasets
5. **Compatibility**: Ensure compatibility with multiple data formats

```bash
git clone https://github.com/EusDancerDev/statflow.git
cd statflow
pip install -e ".[dev]"
pytest  # Run test suite
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Scientific Python Community** for foundational libraries (NumPy, pandas, scipy, xarray)
- **Climate Research Community** for standard definitions of climate indicators
- **International Standards** (ISO 15927-4:2005) for representative weather data methodologies
- **Open Source Contributors** for continuous improvement and feedback

## Citation

If you use statflow in your research, please cite:

```bibtex
@software{statflow2024,
  title={statflow: Statistical Analysis and Climatology Toolkit},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/statflow},
  version={3.5.0}
}
```

## Contact

For questions, suggestions, or collaboration opportunities:

- **Issues**: Open an issue on GitHub for bug reports or feature requests
- **Discussions**: Use GitHub Discussions for general questions and ideas
- **Email**: Contact the maintainers for collaboration inquiries

## Related Projects

- **climalab**: Climate data analysis and processing tools
- **filewise**: File operations and data manipulation utilities  
- **pygenutils**: General-purpose Python utilities
- **paramlib**: Parameter management and configuration constants

## Troubleshooting

### Common Issues

1. **Memory Errors with Large Datasets**:

   ```python
   # Use chunking for large xarray datasets
   large_data = xr.open_dataset("huge_file.nc", chunks={'time': 1000})
   ```

2. **Type Compatibility**:

   ```python
   # Ensure consistent data types
   data = data.astype(np.float64)  # Convert to consistent numeric type
   ```

3. **Missing Dependencies**:

   ```bash
   pip install scipy xarray  # Install missing scientific computing libraries
   ```

4. **Performance Issues**:

   ```python
   # Use appropriate methods for data size
   if len(data) > 50000:
       autocorr = sf.core.time_series.autocorrelate(data, twosided=False)
   ```

### Getting Help

- Check the [CHANGELOG.md](CHANGELOG.md) for recent updates and breaking changes
- Review function docstrings for parameter details and examples
- Consult the [VERSIONING.md](VERSIONING.md) for version compatibility information
- Open an issue on GitHub with a minimal reproducible example

---

**statflow** - Professional statistical analysis and climatology toolkit for Python 🌡️📊
