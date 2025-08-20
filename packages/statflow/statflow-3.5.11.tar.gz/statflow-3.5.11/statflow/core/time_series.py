#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module for time series operations in statistical analysis.
"""

#----------------#
# Import modules #
#----------------#

import numpy as np
import pandas as pd

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_caller_args, get_type_str
from pygenutils.arrays_and_lists.patterns import count_consecutive
from pygenutils.strings.string_handler import find_substring_index
from pygenutils.strings.text_formatters import format_string
from pygenutils.time_handling.date_and_time_utils import find_dt_key
from pygenutils.time_handling.time_formatters import parse_dt_string

#------------------#
# Define functions #
#------------------#

# Statistical Processing #
#------------------------#

def periodic_statistics(obj,
                        statistic: str,
                        freq: str,
                        groupby_dates: bool = False,
                        drop_date_idx_col: bool = False,
                        season_months: list[int] | None = None,
                        dayfirst: bool = False,
                        yearfirst: bool = False):
    """
    Calculates basic statistics (not climatologies) for the given data 
    object over a specified time frequency.

    This function supports data analysis on Pandas DataFrames and 
    xarray objects, allowing for grouping by different time frequencies 
    such as yearly, quarterly, monthly, etc.

    Parameters
    ----------
    obj : pandas.DataFrame | xarray.Dataset | xarray.DataArray
        The data object for which statistics are to be calculated.
    
    statistic : {"max", "min", "mean", "std", "sum"}
        The statistical measure to compute.
    
    freq : str
        The frequency for resampling or grouping the data.
        For example, "D" for daily, "M" for monthly, etc.
        Refer to the Pandas documentation for more details 
        on time frequency aliases.
    
    groupby_dates : bool, optional
        Only applicable for xarray.Dataset or xarray.DataArray.
        If True, the function will group the dates according to 
        the specified frequency.
    
    drop_date_idx_col : bool, optional
        Whether to drop the date index column from the results. 
        Default is False, retaining the dates in the output.
    
    season_months : list[int] | None, optional
        A list of three integers representing the months of a season,
        used if 'freq' is "SEAS". Must contain exactly three months.
    
    dayfirst : bool, default False
        Specify a date parse order if datetime strings are ambiguous.
        If True, parses dates with the day first, e.g. "10/11/12" is parsed as 2012-11-10.
        When converting date columns to datetime format.
    
    yearfirst : bool, default False
        Specify a date parse order if datetime strings are ambiguous.
        If True parses dates with the year first, e.g. "10/11/12" is parsed as 2010-11-12.
        If both dayfirst and yearfirst are True, yearfirst is preceded (same as dateutil).
        When converting date columns to datetime format.

    Returns
    -------
    pandas.DataFrame | xarray object
        The computed statistics as a DataFrame or xarray object,
        depending on the type of input data.

    Raises
    ------
    ValueError
        If the specified statistic is unsupported, the frequency is 
        invalid, or if the season_months list does not contain exactly 
        three integers.
    """
    
    # Input validation block #
    #-#-#-#-#-#-#-#-#-#-#-#-#-
    
    param_keys = get_caller_args()
    seas_months_arg_pos = find_substring_index(param_keys, "season_months")
    
    obj_type = get_type_str(obj, lowercase=True)
    seas_mon_arg_type = get_type_str(season_months)
    
    if statistic not in STATISTICS:
        format_args_stat = ("statistic", statistic, STATISTICS)
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_stat))
        
    
    if obj_type not in ["dataframe", "dataset", "dataarray"]:
        format_args_obj_type = ("data type",
                                obj_type, 
                                "{pandas.DataFrame, xarray.Dataset, xarray.DataArray}")
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_obj_type))

    if freq not in FREQ_MAPPING:
        format_args_freq = ("frequency", freq, list(FREQ_MAPPING.keys()))
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_freq))
    
    # Only validate season_months if it's provided (not None)
    if season_months is not None:
        if seas_mon_arg_type != "list":
            raise TypeError("Expected a list for parameter 'season_months' "
                            f"(number {seas_months_arg_pos}) got '{seas_mon_arg_type}'.")
        
        if len(season_months) != 3:
            raise ValueError(SEASON_MONTH_FMT_ERROR_TEMPLATE)
    elif freq == "SEAS":  # Only require season_months when freq is "SEAS"
        raise ValueError("Seasonal frequency requires parameter 'season_months'.")

    # Program progression #
    #-#-#-#-#-#-#-#-#-#-#-#

    # Get the date/time column or dimension
    date_key = find_dt_key(obj)

    # Different handling based on object type
    if obj_type in ["dataset", "dataarray"]:
        # Handle xarray objects
        if groupby_dates:
            if freq == "SEAS":
                # Custom handling for seasons
                # This would require more complex logic to define seasons
                raise NotImplementedError("Season grouping for xarray not yet implemented")
            else:
                # Use proper xarray datetime accessor
                groupby_key = f"{date_key}.{FREQ_MAPPING[freq]}"
                result = getattr(obj.groupby(groupby_key), statistic)()
        else:
            # Without groupby_dates, return the full object
            result = getattr(obj, statistic)()
    else:
        # Handle pandas DataFrame
        # Use pandas Grouper properly
        if freq == "SEAS":
            # Special handling for seasonal grouping
            # This would require custom season definition
            raise NotImplementedError("Season grouping for pandas not yet implemented")
        else:
            # Make a copy to avoid modifying the original DataFrame
            df_copy = obj.copy()
            
            # Ensure the date column is in datetime format
            # and handle NaT values by dropping them
            if pd.api.types.is_datetime64_any_dtype(df_copy[date_key]):
                # Already datetime, just drop NaT values
                df_copy = df_copy.dropna(subset=[date_key])
            else:
                # Try to convert to datetime
                try:
                    df_copy[date_key] = parse_dt_string(df_copy[date_key],
                                                        module="pandas",
                                                        dayfirst=dayfirst,
                                                        yearfirst=yearfirst)
                    df_copy = df_copy.dropna(subset=[date_key])
                except Exception as e:
                    raise ValueError(f"Could not convert column '{date_key}' to datetime: {str(e)}")
            
            # Proceed only if we have valid data after cleaning
            if len(df_copy) == 0:
                return pd.DataFrame()  # Return empty DataFrame if no valid data
                
            # Group by frequency and apply statistic
            grouped = df_copy.groupby(pd.Grouper(key=date_key, freq=freq))
            
            # Call the statistic method with explicit numeric_only parameter
            # This prevents FutureWarning about numeric_only default changing
            if statistic in ["mean", "std", "sum", "min", "max"]:
                result = getattr(grouped, statistic)(numeric_only=True)
            else:
                result = getattr(grouped, statistic)()
            
            if drop_date_idx_col:
                result = result.reset_index(drop=True)
            else:
                result = result.reset_index()
    
    return result


def decompose_cumulative_data(cumulative_array: np.ndarray, 
                              fill_value: float | None = None, 
                              zeros_dtype: str = 'd') -> np.ndarray:    
    """
    Convert cumulative values into individual values by subtracting consecutive elements,
    with an option to handle negative differences.

    This function takes an array of cumulative values and returns the individual values
    that make up the cumulative sum. Negative differences can either be preserved or replaced 
    with a specified fill value.
    
    Parameters
    ----------
    cumulative_array : numpy.ndarray
        A multi-dimensional array representing cumulative values over time or other axes.
    fill_value : float | None, optional
        Value to replace negative differences. If None (default), negative differences are preserved.
    zeros_dtype : str
        Data type for the array of zeros if `fill_value` is used. Default is 'd' (float).
    
    Returns
    -------
    individual_values_array : numpy.ndarray
        A multi-dimensional array with individual values extracted from the cumulative array.
    
    Examples
    --------
    Example 1: Basic cumulative data decomposition
    >>> cumulative_array = np.array([6, 7, 13, 13, 20, 22, 30, 31, 38, 43, 52, 55])
    >>> decompose_cumulative_data(cumulative_array)
    array([ 6.,  1.,  6.,  0.,  7.,  2.,  8.,  1.,  7.,  5.,  9.,  3.])

    Example 2: Preserving negative differences
    >>> cumulative_array = np.array([6, 7, 13, 12, 20, 22])
    >>> decompose_cumulative_data(cumulative_array)
    array([ 6.,  1.,  6., -1.,  8.,  2.])

    Example 3: Replacing negative differences with zeros
    >>> decompose_cumulative_data(cumulative_array, fill_value=0)
    array([ 6.,  1.,  6.,  0.,  8.,  2.])
    """
    
    records = len(cumulative_array)
    
    # Define the behaviour for negative differences
    def handle_negative_difference(diff):
        if fill_value is None:
            return diff
        return np.full_like(diff, fill_value, dtype=zeros_dtype) if np.any(diff < 0) else diff
    
    # Calculate the individual values, applying the fill_value if necessary
    individual_values_array = \
        np.array([handle_negative_difference(cumulative_array[t+1] - cumulative_array[t])
                  for t in range(records-1)])
    
    # Add the average of the last two differences to match the shape of the original array
    individual_values_array = np.append(individual_values_array,
                                        np.mean(individual_values_array[-2:], axis=0)[np.newaxis,:],
                                        axis=0)
    
    return individual_values_array


def hourly_ts_cumul(array: np.ndarray, zero_threshold: float, zeros_dtype: str = 'd') -> np.ndarray:    
    """
    Obtain the 1-hour time step cumulative data by subtracting the 
    previous cumulative value from the next.

    Parameters
    ----------
    array : numpy.ndarray
        Time-series array (first index corresponds to time).
    zero_threshold : float
        Values below this threshold are considered unrealistic and set to zero.
    zeros_dtype : str | numpy type, optional
        Data type of the resulting zero array, by default 'd' (double-precision float).

    Returns
    -------
    hour_ts_cumul : numpy.ndarray
        Array of 1-hour time step cumulative data with unrealistic edges set to zero.
    """
    
    hour_ts_data = decompose_cumulative_data(array)  # Apply your decomposition logic
    unmet_case_values = np.zeros_like(array, dtype=zeros_dtype)

    hour_ts_cumul = np.where(np.all(hour_ts_data >= zero_threshold, axis=1),
                                 hour_ts_data, unmet_case_values)
    
    return hour_ts_cumul


def consec_occurrences_maxdata(array: np.ndarray | pd.Series,
                               max_threshold: float,
                               min_consec: int | None = None,
                               calc_max_consec: bool = False) -> int:
    
    """
    Count the occurrences where values exceed a threshold,
    with an option to calculate the longest consecutive occurrences.

    Parameters
    ----------
    array : numpy.ndarray | pandas.Series
        Input array with maximum value data.
    max_threshold : float
        Threshold for counting occurrences.
    min_consec : int | None, optional
        Minimum number of consecutive occurrences.
    calc_max_consec : bool, optional
        If True, returns the maximum length of consecutive occurrences.
        Defaults to False.

    Returns
    -------
    int
        Number of occurrences or max length of consecutive occurrences 
        based on input parameters.
    """
    
    above_idx = array > max_threshold
    
    if min_consec is None:
        if calc_max_consec:
            return count_consecutive(above_idx, True) or 0
        return np.count_nonzero(above_idx)

    # Handle cases with a minimum number of consecutive occurrences
    block_idx = \
    np.flatnonzero(np.convolve(above_idx, np.ones(min_consec, dtype=int), mode='valid') >= min_consec)
    consec_nums = count_consecutive(block_idx)

    if consec_nums:
        return len(consec_nums) * min_consec + sum(consec_nums)
    return 0
    
    
def consec_occurrences_mindata(array: np.ndarray | pd.Series, 
                               min_thres: float, 
                               threshold_mode: str = "below", 
                               min_consec: int | None = None, 
                               calc_min_consec: bool = False) -> int:
    """
    Count the occurrences where values are below or above a threshold,
    with an option to calculate the longest consecutive occurrences.

    Parameters
    ----------
    array : numpy.ndarray | pandas.Series
        Input array with minimum value data.
    min_thres : float
        Threshold for counting occurrences.
    threshold_mode : {"below", "above"}, optional
        Whether to count values below or above the threshold. Defaults to "below".
    min_consec : int | None, optional
        Minimum number of consecutive occurrences.
    calc_min_consec : bool, optional
        If True, returns the maximum length of consecutive occurrences.
        Defaults to False.

    Returns
    -------
    int
        Number of occurrences or max length of consecutive occurrences based on input parameters.
    """
    
    if threshold_mode not in {"below", "above"}:
        raise ValueError("Invalid threshold mode. Choose one from {'below', 'above'}.")

    above_idx = array < min_thres if threshold_mode == "below" else array > min_thres

    if min_consec is None:
        if calc_min_consec:
            return count_consecutive(above_idx, True) or 0
        return np.count_nonzero(above_idx)

    block_idx = \
    np.flatnonzero(np.convolve(above_idx, np.ones(min_consec, dtype=int), mode='valid') >= min_consec)
    consec_nums = count_consecutive(block_idx)

    if consec_nums:
        return len(consec_nums) * min_consec + sum(consec_nums)
    return 0


# Correlations #
#--------------#

def autocorrelate(x: list | np.ndarray, twosided: bool = False) -> np.ndarray:
    """
    Computes the autocorrelation of a time series.

    Autocorrelation measures the similarity between a time series and a 
    lagged version of itself. This is useful for identifying repeating 
    patterns or trends in data, such as the likelihood of future values 
    based on current trends.

    Parameters
    ----------
    x : list | numpy.ndarray
        The time series data to autocorrelate.
    twosided : bool, optional, default: False
        If True, returns autocorrelation for both positive and negative 
        lags (two-sided). If False, returns only non-negative lags 
        (one-sided).

    Returns
    -------
    numpy.ndarray
        The normalised autocorrelation values. If `twosided` is False, 
        returns only the non-negative lags.

    Notes
    -----
    - This function uses `numpy.correlate` for smaller datasets and 
      `scipy.signal.correlate` for larger ones.
    - Be aware that NaN values in the input data must be removed before 
      computing autocorrelation.
    - For large arrays (> ~75000 elements), `scipy.signal.correlate` is 
      recommended due to better performance with Fourier transforms.
    """
    from scipy.signal import correlate

    # Remove NaN values and demean the data
    x_nonan = x[~np.isnan(x)]
    x_demean = x_nonan - np.mean(x_nonan)
    
    if len(x_demean) <= int(5e4):
        x_autocorr = np.correlate(x_demean, x_demean, mode="full")
    else:
        x_autocorr = correlate(x_demean, x_demean)
    
    # Normalise the autocorrelation values
    x_autocorr /= np.max(x_autocorr)
    
    # Return two-sided or one-sided autocorrelation
    return x_autocorr if twosided else x_autocorr[len(x_autocorr) // 2:]


#--------------------------#
# Parameters and constants #
#--------------------------#

# Statistics #
STATISTICS = ["max", "min", "sum", "mean", "std"]

# Time frequency mapping #
FREQ_MAPPING = {
    "Y": "year",
    "SEAS": "season",
    "M": "month",
    "W": "week",
    "D": "day",
    "H": "hour",
    "min": "minute",
    "S": "second"
}

# Template strings #
#------------------#

UNSUPPORTED_OPTION_ERROR_TEMPLATE = "Unsupported {} '{}'. Options are {}."
SEASON_MONTH_FMT_ERROR_TEMPLATE = """Parameter 'season_months' must contain exactly \
3 integers representing months. For example: [12, 1, 2]."""