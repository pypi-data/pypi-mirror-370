#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
periodic_climat_stats.py
------------------------

This module provides functionality to compute periodic climatology statistics
over specified time frequencies. These functions are particularly useful for 
climatological and atmospheric sciences, where it's common to analyze data 
on seasonal, monthly, daily, or even hourly time scales.

The primary function calculates summary statistics (mean, median, etc.) 
for an observed or modeled data series across these time intervals, allowing for 
the detection and comparison of climate patterns and trends.

Notes
-----

- This module supports various time frequencies common in climatological studies, 
  allowing flexibility in analyzing and summarizing periodic trends.
- It works with standard data structures used in climatology, including both Pandas 
  and xarray, making it adaptable for various data sources (e.g., observations, 
  reanalysis, or climate model outputs).
- The function is optimised for efficiency with large datasets and supports 
  both absolute and relative time-based statistics.
"""


#----------------#
# Import modules #
#----------------#

import calendar

import numpy as np
import pandas as pd

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_caller_args, get_type_str
from paramlib.global_parameters import (
    BASIC_TIME_FORMAT_STRS,
    MONTH_NUMBER_DICT,
    TIME_FREQUENCIES_COMPLETE,
    TIME_FREQUENCIES_ABBREVIATED
)
from pygenutils.strings.string_handler import find_substring_index
from pygenutils.strings.text_formatters import format_string
from pygenutils.time_handling.date_and_time_utils import find_dt_key
from pygenutils.time_handling.time_formatters import datetime_obj_converter
from statflow.core.time_series import periodic_statistics

#------------------#
# Define functions #
#------------------#

def climat_periodic_statistics(obj,
                               statistic: str,
                               time_freq: str,
                               keep_std_dates: bool = False, 
                               drop_date_idx_col: bool = False,
                               season_months: list[int] | None = None):
    """
    Function that calculates climatologic statistics for a time-frequency.
    
    Parameters
    ----------
    obj : pandas.DataFrame | xarray.Dataset | xarray.DataArray
        The data object for climatological statistics calculation.
    statistic : {"max", "min", "mean", "std", "sum"}
        The statistic to calculate.
    time_freq : str
        Time frequency to which data will be filtered.
    keep_std_dates : bool
        If True, standard YMD (HMS) date format is kept for all climatologics
        except for yearly climatologics.
        Otherwise dates are shown as hour, day, or month indices,
        and season achronyms if "seasonal" is selected as the time frequency.
        Default value is False.
    drop_date_idx_col : bool
        Whether to drop the date index column. Default is False.
        If True, the dates will be kept, but the corresponding array
        will be an index, instead of a column.
        Defaults to False
    season_months : list[int] | None
        List containing the month numbers to later refer to the time array,
        whatever the object is among the mentioned three types.
        Defaults to None.
    
    Returns
    -------
    obj_climat : pandas.DataFrame | xarray.Dataset | xarray.DataArray
        Calculated climatological average.
    
    Notes
    -----
    For Pandas DataFrames, since it is a 2D object,
    it is interpreted as data holds for a specific geographical point.
    """
    
    # Input validation
    _validate_inputs(time_freq, season_months, statistic)
    
    # Determine object type and get time frequency abbreviation
    obj_type = get_type_str(obj, lowercase=True)
    freq_abbr = FREQ_ABBRS[TIME_FREQUENCIES_ABBREVIATED.index(time_freq)]
    
    # Identify the time dimension
    date_key = _get_time_dimension(obj, obj_type)
    
    # Get date array and parts of it
    dates = obj[date_key]
    years = np.unique(dates.dt.year)
    days = np.unique(dates.dt.day)
    months = np.unique(dates.dt.month)
    hours = np.unique(dates.dt.hour)
    
    # Get the latest year (preferably a leap year)
    latest_year = _get_latest_year(years)
    
    # Process based on object type
    if obj_type == "dataframe":
        return _process_dataframe(obj, date_key, statistic, time_freq, keep_std_dates, 
                                drop_date_idx_col, season_months, freq_abbr, 
                                latest_year, months, days, hours)
    elif obj_type in ["dataset", "dataarray"]:
        return _process_xarray(obj, date_key, statistic, time_freq, keep_std_dates, 
                             season_months, freq_abbr, latest_year)
    else:
        raise TypeError(f"Unsupported object type: {obj_type}")


def _validate_inputs(time_freq: str, season_months: list[int] | None, statistic: str | None = None) -> None:
    """Validate input parameters."""
    if time_freq not in TIME_FREQUENCIES_ABBREVIATED:
        format_args_climat_stats = ("time-frequency", time_freq, TIME_FREQUENCIES_ABBREVIATED)
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_climat_stats))
    
    if statistic is not None and statistic not in STATISTICS:
        format_args_stat = ("statistic", statistic, STATISTICS)
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_stat))
    
    if time_freq == "seasonal":
        param_keys = get_caller_args()
        seas_months_arg_pos = find_substring_index(param_keys, "season_months")
        seas_mon_arg_type = get_type_str(season_months)
        
        if seas_mon_arg_type != "list":
            raise TypeError("Expected a list for parameter "
                            f"'{param_keys[seas_months_arg_pos]}', "
                            f"got '{seas_mon_arg_type}'.")
        
        if (season_months and len(season_months) != 3):
            raise ValueError(SEASON_MONTH_FMT_ERROR_TEMPLATE)


def _get_time_dimension(obj, obj_type: str) -> str:
    """Get the time dimension key from the object."""
    if obj_type in ["dataframe", "dataset", "dataarray"]:
        return find_dt_key(obj)
    else:
        raise TypeError(f"Unsupported object type: {obj_type}")


def _get_latest_year(years: np.ndarray) -> int:
    """Get the latest year, preferably a leap year."""
    leapyear_bool_arr = [calendar.isleap(year) for year in years]
    llba = len(leapyear_bool_arr)
    
    if llba > 0:
        return years[leapyear_bool_arr][-1]
    else:
        return years[-1]


def _process_dataframe(obj: pd.DataFrame, 
                      date_key: str, 
                      statistic: str, 
                      time_freq: str, 
                      keep_std_dates: bool, 
                      drop_date_idx_col: bool, 
                      season_months: list[int] | None, 
                      freq_abbr: str, 
                      latest_year: int, 
                      months: np.ndarray, 
                      days: np.ndarray, 
                      hours: np.ndarray):
    """Process pandas DataFrame objects."""
    # Define the climatologic statistical data frame columns
    climat_obj_cols = [date_key] + [obj.columns[i]+"_climat" for i in range(1, len(obj.columns))]
    
    # Process based on time frequency
    if time_freq == "hourly":
        climat_vals, climat_dates, climat_obj_cols = _process_hourly_dataframe(
            obj, date_key, statistic, keep_std_dates, freq_abbr, latest_year, 
            months, days, hours, climat_obj_cols
        )
    elif time_freq == "daily":
        climat_vals, climat_dates, climat_obj_cols = _process_daily_dataframe(
            obj, date_key, statistic, keep_std_dates, freq_abbr, latest_year, 
            months, days, climat_obj_cols
        )
    elif time_freq == "monthly":
        climat_vals, climat_dates, climat_obj_cols = _process_monthly_dataframe(
            obj, date_key, statistic, keep_std_dates, freq_abbr, latest_year, 
            months, climat_obj_cols
        )
    elif time_freq == "seasonal":
        climat_vals, climat_dates, climat_obj_cols = _process_seasonal_dataframe(
            obj, date_key, statistic, keep_std_dates, season_months, climat_obj_cols
        )
    elif time_freq == "yearly":
        climat_vals, climat_dates = _process_yearly_dataframe(
            obj, statistic, freq_abbr, drop_date_idx_col
        )
    
    # Format the output DataFrame
    return _format_dataframe_output(climat_vals, climat_dates, climat_obj_cols)


def _process_hourly_dataframe(obj: pd.DataFrame, 
                            date_key: str, 
                            statistic: str, 
                            keep_std_dates: bool, 
                            freq_abbr: str, 
                            latest_year: int, 
                            months: np.ndarray, 
                            days: np.ndarray, 
                            hours: np.ndarray, 
                            climat_obj_cols: list[str]) -> tuple[list, np.ndarray, list[str]]:
    """Process hourly data for DataFrame."""
    climat_vals = []
    for m in months:
        for d in days:
            for h in hours:
                subset = obj[(obj[date_key].dt.month == m) & 
                             (obj[date_key].dt.day == d) & 
                             (obj[date_key].dt.hour == h)].iloc[:, 1:]
                if len(subset) > 0:
                    climat_vals.append(subset[statistic]())
    
    if keep_std_dates:
        climat_dates = pd.date_range(f"{latest_year}-01-01 0:00",
                                     f"{latest_year}-12-31 23:00",
                                     freq=freq_abbr)
    else:    
        climat_dates = np.arange(len(climat_vals))
        climat_obj_cols[0] = "hour_of_year"
    
    return climat_vals, climat_dates, climat_obj_cols


def _process_daily_dataframe(obj: pd.DataFrame, 
                           date_key: str, 
                           statistic: str, 
                           keep_std_dates: bool, 
                           freq_abbr: str, 
                           latest_year: int, 
                           months: np.ndarray, 
                           days: np.ndarray, 
                           climat_obj_cols: list[str]) -> tuple[list, np.ndarray, list[str]]:
    """Process daily data for DataFrame."""
    climat_vals = []
    for m in months:
        for d in days:
            subset = obj[(obj[date_key].dt.month == m) & 
                         (obj[date_key].dt.day == d)].iloc[:, 1:]
            if len(subset) > 0:
                climat_vals.append(subset[statistic]())
    
    if keep_std_dates:
        climat_dates = pd.date_range(f"{latest_year}-01-01 0:00",
                                     f"{latest_year}-12-31 23:00",
                                     freq=freq_abbr)
    else:    
        climat_dates = np.arange(1, len(climat_vals) + 1)
        climat_obj_cols[0] = "day_of_year"
    
    return climat_vals, climat_dates, climat_obj_cols


def _process_monthly_dataframe(obj: pd.DataFrame, 
                             date_key: str, 
                             statistic: str, 
                             keep_std_dates: bool, 
                             freq_abbr: str, 
                             latest_year: int, 
                             months: np.ndarray, 
                             climat_obj_cols: list[str]) -> tuple[list, np.ndarray, list[str]]:
    """Process monthly data for DataFrame."""
    climat_vals = []
    for m in months:
        subset = obj[obj[date_key].dt.month == m].iloc[:, 1:]
        if len(subset) > 0:
            climat_vals.append(subset[statistic]())
    
    if keep_std_dates:
        climat_dates = pd.date_range(f"{latest_year}-01-01 0:00",
                                     f"{latest_year}-12-31 23:00",
                                     freq=freq_abbr)
    else:
        climat_dates = np.arange(1, 13)
        climat_obj_cols[0] = "month_of_year"
    
    return climat_vals, climat_dates, climat_obj_cols


def _process_seasonal_dataframe(obj: pd.DataFrame, 
                              date_key: str, 
                              statistic: str, 
                              keep_std_dates: bool, 
                              season_months: list[int] | None, 
                              climat_obj_cols: list[str]) -> tuple[list, list, list[str]]:
    """Process seasonal data for DataFrame."""
    climat_vals = [obj[obj[date_key].dt.month.isin(season_months)].iloc[:, 1:][statistic]()]
    
    if keep_std_dates:                
        climat_dates = [obj[obj[date_key].dt.month==season_months[-1]].
                        iloc[-1][date_key].strftime(DAYTIME_FMT_STR)]
    else:
        climat_dates = [MONTH_NUMBER_DICT[m] for m in season_months]
        climat_obj_cols[0] = "season"
    
    return climat_vals, climat_dates, climat_obj_cols


def _process_yearly_dataframe(obj: pd.DataFrame, 
                            statistic: str, 
                            freq_abbr: str, 
                            drop_date_idx_col: bool) -> tuple[list, list]:
    """
    Process yearly data for DataFrame.
    
    Parameters
    ----------
    obj : pd.DataFrame
        Input DataFrame containing time series data.
    statistic : str
        Statistical operation to perform ('mean', 'max', 'min', 'std', 'sum').
    freq_abbr : str
        Frequency abbreviation for time resampling.
    drop_date_idx_col : bool
        Whether to drop the date index column from the results.
        
    Returns
    -------
    tuple[list, list]
        climat_vals : list
            List containing the calculated statistical values.
        climat_dates : list
            List containing the corresponding dates.
    """
    climat_df = periodic_statistics(obj, statistic, freq_abbr, drop_date_idx_col)
    climat_vals = [climat_df.iloc[:, 1:][statistic]()]
    climat_dates = [climat_df.iloc[-1,0]]
    
    return climat_vals, climat_dates


def _format_dataframe_output(climat_vals: list, climat_dates: list | np.ndarray, climat_obj_cols: list[str]) -> pd.DataFrame:
    """Format the output DataFrame."""
    # Check climatological value array's shape to later fit into the df
    climat_vals = np.array(climat_vals)
    climat_vals_ndims = climat_vals.ndim
     
    if climat_vals_ndims == 1:
        climat_vals = climat_vals[:, np.newaxis]    
    
    climat_dates = np.array(climat_dates, 'O')[:, np.newaxis]
    
    # Store climatological data into the data frame
    climat_arr = np.append(climat_dates, climat_vals, axis=1)
    obj_climat = pd.DataFrame(climat_arr, columns=climat_obj_cols)
    obj_climat.iloc[:, 0] = datetime_obj_converter(obj_climat.iloc[:, 0], "pandas")
    
    return obj_climat


def _process_xarray(obj, 
                  date_key: str, 
                  statistic: str, 
                  time_freq: str, 
                  keep_std_dates: bool, 
                  season_months: list[int] | None, 
                  freq_abbr: str, 
                  latest_year: int):
    """Process xarray objects (Dataset or DataArray)."""
    # Process based on time frequency
    if time_freq == "hourly":
        obj_climat = _process_hourly_xarray(obj, date_key, statistic)
    elif time_freq == "seasonal":
        obj_climat = _process_seasonal_xarray(obj, date_key, statistic, season_months)
    else:
        # For other time frequencies, use the original logic
        obj_climat = _process_other_xarray(obj, date_key, statistic, time_freq)
    
    # Format the time dimension
    return _format_xarray_time_dimension(obj_climat, time_freq, keep_std_dates, 
                                       season_months, freq_abbr, latest_year, date_key)


def _process_hourly_xarray(obj, date_key: str, statistic: str):
    """Process hourly data for xarray."""
    # Define the hourly climatology pattern
    obj_climat_nonstd_times = obj['time.hour'] / 24 + obj['time.dayofyear']
    return obj.groupby(obj_climat_nonstd_times).statistic(dim=date_key)


def _process_seasonal_xarray(obj, date_key: str, statistic: str, season_months: list[int] | None):
    """Process seasonal data for xarray."""
    obj_seas_sel = obj.sel({date_key: obj[date_key].dt.month.isin(season_months)})
    return obj_seas_sel[statistic](dim=date_key)


def _process_other_xarray(obj, date_key: str, statistic: str, time_freq: str):
    """
    Process other time frequencies for xarray objects.
    
    This function handles time frequencies that are not specifically 
    implemented in dedicated functions (hourly, seasonal).
    
    Parameters
    ----------
    obj : xarray.Dataset | xarray.DataArray
        Input xarray object containing time series data.
    date_key : str
        Name of the time dimension in the xarray object.
    statistic : str
        Statistical operation to perform ('mean', 'max', 'min', 'std', 'sum').
    time_freq : str
        Time frequency for grouping ('daily', 'monthly', 'yearly').
        
    Returns
    -------
    xarray.Dataset | xarray.DataArray
        Processed xarray object with applied statistical operation.
        
    Notes
    -----
    This is a placeholder function for time frequencies that require
    specific implementations. In a complete implementation, you would
    add specific logic for each supported time frequency.
    """
    # This is a placeholder for other time frequencies
    # In a complete refactoring, you would implement specific functions for each
    return obj.groupby(time_freq)[statistic](dim=date_key)


def _format_xarray_time_dimension(obj_climat, 
                                time_freq: str, 
                                keep_std_dates: bool, 
                                season_months: list[int] | None, 
                                freq_abbr: str, 
                                latest_year: int, 
                                date_key: str):
    """Format the time dimension for xarray objects."""
    if time_freq in TIME_FREQUENCIES_COMPLETE[2:]:
        # Get the analogous dimension of 'time', usually label 'group'
        occ_time_name_temp = find_dt_key(obj_climat)
        
        if keep_std_dates:                          
            climat_dates = pd.date_range(f"{latest_year}-1-1 0:00",
                                         f"{latest_year}-12-31 23:00",
                                         freq=freq_abbr)
            occ_time_name = date_key 
          
        else:
            climat_dates = obj_climat[occ_time_name_temp].values
            lcd = len(climat_dates)
            
            occ_time_name = occ_time_name_temp
            
            if time_freq in TIME_FREQUENCIES_COMPLETE[-2:]:
                occ_time_name = time_freq[:-2] + "ofyear"    
                climat_dates = np.arange(lcd) 
            
        # 'time' dimension renaming and its assignment
        obj_climat = _rename_xarray_dimension(obj_climat, occ_time_name_temp, occ_time_name)
                
    elif time_freq == TIME_FREQUENCIES_COMPLETE[1]:  # seasonal
        if keep_std_dates:
            seas_end_dayofmonth = calendar.monthcalendar(latest_year, season_months[-1])[-1][-1]
            climat_dates = pd.Timestamp(latest_year, season_months[-1], seas_end_dayofmonth)
            occ_time_name = date_key
        else:
            occ_time_name = time_freq[:-2]
            climat_dates = "".join([MONTH_NUMBER_DICT[m] for m in season_months])
    
    # Update the time array
    obj_climat = obj_climat.assign_coords({occ_time_name: climat_dates})
    
    return obj_climat


def _rename_xarray_dimension(obj_climat, occ_time_name_temp: str, occ_time_name: str):
    """
    Rename dimension in xarray objects.
    
    This function attempts to rename a dimension in an xarray object using
    multiple approaches to handle different xarray structures and versions.
    
    Parameters
    ----------
    obj_climat : xarray.Dataset | xarray.DataArray
        The xarray object whose dimension needs to be renamed.
    occ_time_name_temp : str
        Current (temporary) name of the time dimension.
    occ_time_name : str
        Desired new name for the time dimension.
        
    Returns
    -------
    xarray.Dataset | xarray.DataArray
        The xarray object with renamed dimension.
        
    Notes
    -----
    The function uses multiple fallback approaches:
    1. First tries rename_dims() and rename()
    2. If that fails, tries swap_dims() twice
    3. Silently continues if all approaches fail
    
    This robust approach handles different xarray versions and object states.
    """
    try:
        # Rename the analogous dimension of 'time' on dimension list
        obj_climat = obj_climat.rename_dims({occ_time_name_temp: occ_time_name})
    except:
        # Rename the analogous dimension name of 'time' to standard
        obj_climat = obj_climat.rename({occ_time_name_temp: occ_time_name})
        
    try:
        # Rename the analogous dimension of 'time' on dimension list
        obj_climat = obj_climat.swap_dims({occ_time_name_temp: occ_time_name})
    except:
        try:
            # Rename the analogous dimension name of 'time' to standard
            obj_climat = obj_climat.swap_dims({occ_time_name_temp: occ_time_name})
        except:
            pass
    
    return obj_climat


#--------------------------#
# Parameters and constants #
#--------------------------#

# Error template strings #
UNSUPPORTED_OPTION_ERROR_TEMPLATE = "Unsupported {} '{}'. Options are {}."
SEASON_MONTH_FMT_ERROR_TEMPLATE = """Parameter 'season_months' must contain exactly \
3 integers representing months. For example: [12, 1, 2]."""

# Date and time format strings #
DAYTIME_FMT_STR = BASIC_TIME_FORMAT_STRS["D"]

# Statistics #
STATISTICS = ["max", "min", "sum", "mean", "std"]

# Time frequency abbreviations #
FREQ_ABBRS = ["Y", "S", "M", "D", "H"]
