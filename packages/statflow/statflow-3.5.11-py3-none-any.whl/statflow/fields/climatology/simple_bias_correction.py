#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
simple_bias_correction.py
-------------------------

This module provides a set of functions to perform simple bias correction techniques,
particularly designed for climatology data. These functions focus on calculating and 
applying deltas between observed data series and reanalysis or model output series, 
which are useful for correcting systematic biases in climate simulations or historical 
reanalysis datasets.

The functions in this module support bias correction using both absolute and relative deltas,
across various time frequencies such as seasonal, monthly, daily, or hourly resolutions.
They can handle common data structures used in climatology like Pandas DataFrames or 
xarray Datasets.
"""

#----------------#
# Import modules #
#----------------#

import pandas as pd
import xarray as xr

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_type_str
from pygenutils.strings.text_formatters import format_string, print_format_string
from pygenutils.time_handling.date_and_time_utils import find_dt_key
from statflow.fields.climatology.periodic_climat_stats import climat_periodic_statistics

#------------------#
# Define functions #
#------------------#

# Internal functions #
#--------------------#

def _unique_sorted(items):
    """
    Returns a sorted list of unique items.
    
    Parameters
    ----------
    items : list
        List of items to deduplicate and sort.
        
    Returns
    -------
    list
        Sorted list of unique items.
        
    Examples
    --------
    >>> _unique_sorted([3, 1, 4, 1, 5, 9, 2, 6, 5])
    [1, 2, 3, 4, 5, 6, 9]
    >>> _unique_sorted(['c', 'a', 'b', 'a'])
    ['a', 'b', 'c']
    """
    return sorted(set(items))

def _validate_inputs(delta_type, preference, delta_value, statistic=None):
    """Validate input parameters."""
    if delta_type not in DELTA_TYPES:
        format_args_delta_type = ("delta type", delta_type, DELTA_TYPES)
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_delta_type))
    
    if preference not in SUPPORTED_TIME_SERIES:
        format_args_preference = ("preferent time series name", preference, SUPPORTED_TIME_SERIES)
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_preference))
    
    if statistic is not None and statistic not in STATISTICS:
        format_args_statistic = ("statistic", statistic, STATISTICS)
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_statistic))
    
    # Validate delta_value
    if delta_value != "auto" and (not isinstance(delta_value, int) or delta_value < 0):
        raise ValueError("Argument 'delta_value' must be a positive integer or 'auto'")


def _get_delta_format(delta_value):
    """
    Get the format string for delta values.
    
    Parameters
    ----------
    delta_value : int | str
        If an integer, specifies the number of decimal places to display.
        If "auto", uses scientific notation with 2 significant digits.
        
    Returns
    -------
    str
        Format string for displaying delta values.
        
    Examples
    --------
    >>> _get_delta_format(3)
    '{:.3f}'
    >>> _get_delta_format("auto")
    '{:.2g}'
    """
    if delta_value == "auto":
        return "{:.2g}"
    else:
        return "{:." + str(delta_value) + "f}"


def _align_time_dimensions(observed_series, reanalysis_series, obj_type_observed, obj_type_reanalysis):
    """Align time dimensions between observed and reanalysis series."""
    if (obj_type_observed, obj_type_reanalysis) == ("dataframe", "dataframe"):      
        date_key = find_dt_key(observed_series)
        date_key_rean = find_dt_key(reanalysis_series)

        if date_key != date_key_rean:
            reanalysis_series.columns = [date_key] + reanalysis_series.columns[1:]
        return date_key

    elif ((obj_type_observed, obj_type_reanalysis) == ("dataset", "dataset"))\
        or ((obj_type_observed, obj_type_reanalysis) == ("dataarray", "dataarray")):
        
        date_key = find_dt_key(observed_series)
        date_key_rean = find_dt_key(reanalysis_series)
        
        if date_key != date_key_rean:
            _rename_xarray_dimension(reanalysis_series, date_key_rean, date_key)
        
        return date_key
    else:
        return None


def _rename_xarray_dimension(obj, old_dim, new_dim):
    """
    Rename a dimension in an xarray object.
    
    This function attempts to rename a dimension in an xarray object using
    multiple approaches to handle different xarray structures and versions.
    
    Parameters
    ----------
    obj : xarray.Dataset | xarray.DataArray
        The xarray object whose dimension needs to be renamed.
    old_dim : str
        Current name of the dimension to be renamed.
    new_dim : str
        New name for the dimension.
        
    Notes
    -----
    The function modifies the object in place and uses multiple fallback 
    approaches:
    1. First tries rename_dims() and rename()
    2. If that fails, tries swap_dims() twice
    3. Silently continues if all approaches fail
    
    This robust approach handles different xarray versions and object states.
    
    Examples
    --------
    >>> import xarray as xr
    >>> data = xr.DataArray([1, 2, 3], dims=['old_time'])
    >>> _rename_xarray_dimension(data, 'old_time', 'time')
    # The dimension 'old_time' is now renamed to 'time'
    """
    try:
        # Rename the analogous dimension of 'time' on dimension list
        obj = obj.rename_dims({old_dim: new_dim})
        # Rename the analogous dimension name of 'time' to standard
        obj = obj.rename({old_dim: new_dim})
    except:
        try:
            # Rename the analogous dimension of 'time' on dimension list
            obj = obj.swap_dims({old_dim: new_dim})
            # Rename the analogous dimension name of 'time' to standard
            obj = obj.swap_dims({old_dim: new_dim})
        except:
            pass


def _calculate_deltas(observed_series, reanalysis_series, time_freq, statistic, 
                     keep_std_dates, drop_date_idx_col, season_months, delta_type, 
                     preference, obj_type_observed, obj_type_reanalysis, date_key):
    """Calculate deltas between observed and reanalysis series."""
    # Calculate statistical climatologies
    format_args_delta3 = (
        "Calculating observed climatologies...",
        time_freq,
        "N/P",
        "N/P",
        "N/P"
    )
    print_format_string(DELTA_APPLICATION_INFO_TEMPLATE, format_args_delta3)
    
    obs_climat = climat_periodic_statistics(observed_series, 
                                            statistic, 
                                            time_freq,
                                            keep_std_dates,
                                            drop_date_idx_col,
                                            season_months)
    
    format_args_delta4 = (
        "Calculating reanalysis climatologies...",
        time_freq,
        "N/P",
        "N/P",
        "N/P"
    )
    print_format_string(DELTA_APPLICATION_INFO_TEMPLATE, format_args_delta4)
    
    rean_climat = climat_periodic_statistics(reanalysis_series, 
                                             statistic, 
                                             time_freq,
                                             keep_std_dates,
                                             drop_date_idx_col,
                                             season_months)
    
    # Calculate deltas
    if ((obj_type_observed, obj_type_reanalysis) == ("dataframe", "dataframe")):
        return _calculate_dataframe_deltas(obs_climat, rean_climat, preference, 
                                          delta_type, date_key, observed_series, 
                                          reanalysis_series)
    
    elif ((obj_type_observed, obj_type_reanalysis) == ("dataset", "dataset"))\
        or ((obj_type_observed, obj_type_reanalysis) == ("dataarray", "dataarray")):
        return _calculate_xarray_deltas(obs_climat, rean_climat, preference, 
                                       delta_type), None


def _calculate_dataframe_deltas(obs_climat, rean_climat, preference, delta_type, 
                               date_key, observed_series, reanalysis_series):
    """Calculate deltas for DataFrame objects."""
    if preference == "observed":
        delta_cols = observed_series.columns[1:]
        
        if delta_type == "absolute":
            delta_arr = rean_climat.iloc[:, 1:].values - obs_climat.iloc[:, 1:].values
        else:
            delta_arr = rean_climat.iloc[:, 1:].values / obs_climat.iloc[:, 1:].values
        
    elif preference == "reanalysis":
        delta_cols = reanalysis_series.columns[1:]
        
        if delta_type == "absolute":
            delta_arr = obs_climat.iloc[:, 1:].values - rean_climat.iloc[:, 1:].values
        else:
            delta_arr = obs_climat.iloc[:, 1:].values / rean_climat.iloc[:, 1:].values
        
    delta_obj = pd.concat([obs_climat[date_key],
                           pd.DataFrame(delta_arr, columns=delta_cols)],
                          axis=1)
    
    return delta_obj, delta_cols


def _calculate_xarray_deltas(obs_climat, rean_climat, preference, delta_type):
    """Calculate deltas for xarray objects."""
    if preference == "observed":
        if delta_type == "absolute":
            delta_obj = rean_climat - obs_climat
        else:
            delta_obj = rean_climat / obs_climat
        
    elif preference == "reanalysis":            
        if delta_type == "absolute":
            delta_obj = obs_climat - rean_climat
        else:
            delta_obj = obs_climat / rean_climat
    
    return delta_obj


def _apply_deltas(delta_obj, delta_cols, time_freq, delta_type, preference, 
                 obj_type_observed, obj_type_reanalysis, date_key, delta_format, 
                 season_months, observed_series, reanalysis_series):
    """Apply deltas to the chosen series."""
    # Extract time components
    months_delta = _unique_sorted(delta_obj[date_key].dt.month)
    days_delta = _unique_sorted(delta_obj[date_key].dt.day)
    hours_delta = _unique_sorted(delta_obj[date_key].dt.hour)
    
    # Determine frequency abbreviation
    freq_abbr = _get_frequency_abbreviation(time_freq, delta_obj, date_key, 
                                           obj_type_observed, obj_type_reanalysis)
    
    # Create a copy of the object to be corrected
    obj_aux = reanalysis_series.copy() if preference == "observed" else observed_series.copy()
    
    # Apply deltas based on time frequency
    if time_freq == "seasonal":
        obj_aux = _apply_seasonal_deltas(obj_aux, delta_obj, delta_cols, delta_type, 
                                        obj_type_observed, obj_type_reanalysis, 
                                        date_key, delta_format, season_months)
    
    elif time_freq == "monthly":
        obj_aux = _apply_monthly_deltas(obj_aux, delta_obj, delta_cols, delta_type, 
                                       obj_type_observed, obj_type_reanalysis, 
                                       date_key, delta_format, months_delta)
    
    elif time_freq == "daily":
        obj_aux = _apply_daily_deltas(obj_aux, delta_obj, delta_cols, delta_type, 
                                     obj_type_observed, obj_type_reanalysis, 
                                     date_key, delta_format, months_delta, days_delta)
    
    elif time_freq == "hourly":
        obj_aux = _apply_hourly_deltas(obj_aux, delta_obj, delta_cols, delta_type, 
                                      obj_type_observed, obj_type_reanalysis, 
                                      date_key, delta_format, months_delta, days_delta, 
                                      hours_delta)
    
    return obj_aux.copy()


def _get_frequency_abbreviation(time_freq, delta_obj, date_key, obj_type_observed, obj_type_reanalysis):
    """
    Get the frequency abbreviation for the time frequency.
    
    Parameters
    ----------
    time_freq : str
        Time frequency string ('seasonal', 'monthly', 'daily', 'hourly').
    delta_obj : pandas.DataFrame | xarray.Dataset | xarray.DataArray
        Delta object containing time information.
    date_key : str
        Name of the date/time column or dimension.
    obj_type_observed : str
        Type of the observed series object ('dataframe', 'dataset', 'dataarray').
    obj_type_reanalysis : str
        Type of the reanalysis series object ('dataframe', 'dataset', 'dataarray').
        
    Returns
    -------
    str
        Frequency abbreviation string for pandas/xarray operations.
        
    Notes
    -----
    For seasonal frequency, returns the time_freq string itself.
    For other frequencies, infers the frequency from the time series data.
    """
    if time_freq == "seasonal":
        return time_freq
    else:
        if ((obj_type_observed, obj_type_reanalysis) == ("DataFrame", "DataFrame")): 
            return pd.infer_freq(delta_obj[date_key])
        elif ((obj_type_observed, obj_type_reanalysis) == ("dataset", "dataset"))\
            or ((obj_type_observed, obj_type_reanalysis) == ("dataarray", "dataarray")):
            return xr.infer_freq(delta_obj[date_key])


def _apply_seasonal_deltas(obj_aux, delta_obj, delta_cols, delta_type, 
                          obj_type_observed, obj_type_reanalysis, date_key, 
                          delta_format, season_months):
    """Apply deltas for seasonal time frequency."""
    obj2correct = obj_aux[obj_aux[date_key].dt.month.isin(season_months)]
    
    # Get the actual delta value for display
    if ((obj_type_observed, obj_type_reanalysis) == ("DataFrame", "DataFrame")):
        actual_delta = delta_obj.iloc[0, 1]  # First row, second column (after date)
    else:
        actual_delta = float(delta_obj.values[0])
        
    format_args_delta_seasonal = (
        "delta",
        delta_type,
        f"{delta_type} ({delta_format.format(actual_delta)})"
    )
    print_format_string(DELTA_APPLICATION_INFO_TEMPLATE, format_args_delta_seasonal)
    
    if ((obj_type_observed, obj_type_reanalysis) == ("DataFrame", "DataFrame")):    
        if delta_type == "absolute":    
            obj_aux.loc[obj2correct.index, delta_cols]\
            += delta_obj.loc[:, delta_cols].values
        else:
            obj_aux.loc[obj2correct.index, delta_cols]\
            *= delta_obj.loc[:, delta_cols].values
            
    elif ((obj_type_observed, obj_type_reanalysis) == ("dataset", "dataset"))\
        or ((obj_type_observed, obj_type_reanalysis) == ("dataarray", "dataarray")):
        if delta_type == "absolute":
            obj_aux.loc[obj2correct.time] += delta_obj.values
        else:
            obj_aux.loc[obj2correct.time] *= delta_obj.values
    
    return obj_aux


def _apply_monthly_deltas(obj_aux, delta_obj, delta_cols, delta_type, 
                         obj_type_observed, obj_type_reanalysis, date_key, 
                         delta_format, months_delta):
    """Apply deltas for monthly time frequency."""
    for m in months_delta:            
        obj2correct = obj_aux[obj_aux[date_key].dt.month==m]
        obj_delta = delta_obj[delta_obj[date_key].dt.month==m]
        
        # Get the actual delta value for display
        if ((obj_type_observed, obj_type_reanalysis) == ("DataFrame", "DataFrame")):
            actual_delta = obj_delta.iloc[0, 1]  # First row, second column (after date)
        else:
            actual_delta = float(obj_delta.values[0])
            
        format_args_delta_monthly = (
            "delta",
            delta_type,
            f"{delta_type} ({delta_format.format(actual_delta)})"
        )
        print_format_string(DELTA_APPLICATION_INFO_TEMPLATE, format_args_delta_monthly)
        
        if ((obj_type_observed, obj_type_reanalysis) == ("DataFrame", "DataFrame")):
            if delta_type == "absolute":
                obj_aux.loc[obj2correct.index, delta_cols]\
                += obj_delta.loc[:, delta_cols].values
            else:
                obj_aux.loc[obj2correct.index, delta_cols]\
                *= obj_delta.loc[:, delta_cols].values
                
        elif ((obj_type_observed, obj_type_reanalysis) == ("dataset", "dataset"))\
            or ((obj_type_observed, obj_type_reanalysis) == ("dataarray", "dataarray")):
            if delta_type == "absolute":
                obj_aux.loc[obj2correct.time] += obj_delta.values
            else:
                obj_aux.loc[obj2correct.time] *= obj_delta.values
    
    return obj_aux


def _apply_daily_deltas(obj_aux, delta_obj, delta_cols, delta_type, 
                       obj_type_observed, obj_type_reanalysis, date_key, 
                       delta_format, months_delta, days_delta):
    """Apply deltas for daily time frequency."""
    for m in months_delta: 
        for d in days_delta:
            obj2correct = obj_aux[(obj_aux[date_key].dt.month==m)&
                                  (obj_aux[date_key].dt.day==d)]
            
            obj_delta = delta_obj[(delta_obj[date_key].dt.month==m)&
                                  (delta_obj[date_key].dt.day==d)]
            
            # Delta application
            if len(obj2correct) > 0 and len(obj_delta) > 0:
                # Get the actual delta value for display
                if ((obj_type_observed, obj_type_reanalysis) == ("DataFrame", "DataFrame")):
                    actual_delta = obj_delta.iloc[0, 1]  # First row, second column (after date)
                else:
                    actual_delta = float(obj_delta.values[0])
                    
                format_args_delta_daily = (
                    "delta",
                    delta_type,
                    f"{delta_type} ({delta_format.format(actual_delta)})"
                )
                print_format_string(DELTA_APPLICATION_INFO_TEMPLATE, format_args_delta_daily)
                
                if ((obj_type_observed, obj_type_reanalysis) == ("DataFrame", "DataFrame")):
                    if delta_type == "absolute":
                        obj_aux.loc[obj2correct.index, delta_cols] \
                        += obj_delta.loc[:, delta_cols].values
                    else:
                        obj_aux.loc[obj2correct.index, delta_cols] \
                        *= obj_delta.loc[:, delta_cols].values
                        
                elif ((obj_type_observed, obj_type_reanalysis) == ("dataset", "dataset"))\
                    or ((obj_type_observed, obj_type_reanalysis) == ("dataarray", "dataarray")):
                    if delta_type == "absolute":
                        obj_aux.loc[obj2correct.time] += obj_delta.values
                    else:
                        obj_aux.loc[obj2correct.time] *= obj_delta.values
    
    return obj_aux


def _apply_hourly_deltas(obj_aux, delta_obj, delta_cols, delta_type, 
                        obj_type_observed, obj_type_reanalysis, date_key, 
                        delta_format, months_delta, days_delta, hours_delta):
    """Apply deltas for hourly time frequency."""
    for m in months_delta:
        for d in days_delta:
            for h in hours_delta:
                obj2correct = obj_aux[(obj_aux[date_key].dt.month==m)&
                                      (obj_aux[date_key].dt.day==d)&
                                      (obj_aux[date_key].dt.hour==h)]
                                   
                obj_delta = delta_obj[(delta_obj[date_key].dt.month==m)&
                                      (delta_obj[date_key].dt.day==d)&
                                      (delta_obj[date_key].dt.hour==h)]
               
                # Delta application
                if len(obj2correct) > 0 and len(obj_delta) > 0:
                    # Get the actual delta value for display
                    if ((obj_type_observed, obj_type_reanalysis) == ("DataFrame", "DataFrame")):
                        actual_delta = obj_delta.iloc[0, 1]  # First row, second column (after date)
                    else:
                        actual_delta = float(obj_delta.values[0])
                        
                    format_args_delta_hourly = (
                        "delta",
                        delta_type,
                        f"{delta_type} ({delta_format.format(actual_delta)})"
                    )
                    print_format_string(DELTA_APPLICATION_INFO_TEMPLATE, format_args_delta_hourly)
                    
                    if ((obj_type_observed, obj_type_reanalysis) == ("DataFrame", "DataFrame")):
                        if delta_type == "absolute":
                            obj_aux.loc[obj2correct.index, delta_cols] \
                            += obj_delta.loc[:, delta_cols].values
                        else:
                            obj_aux.loc[obj2correct.index, delta_cols] \
                            *= obj_delta.loc[:, delta_cols].values
                            
                    elif ((obj_type_observed, obj_type_reanalysis) == ("dataset", "dataset"))\
                        or ((obj_type_observed, obj_type_reanalysis) == ("dataarray", "dataarray")):
                        if delta_type == "absolute":
                            obj_aux.loc[obj2correct.time] += obj_delta.values
                        else:
                            obj_aux.loc[obj2correct.time] *= obj_delta.values
    
    return obj_aux


# Public functions #
#------------------#

def calculate_and_apply_deltas(observed_series,
                               reanalysis_series,
                               time_freq,
                               delta_type="absolute",
                               statistic="mean",
                               preference="observed",
                               keep_std_dates=True, 
                               drop_date_idx_col=False,
                               season_months=None,
                               delta_value=2):
    """
    Function that calculates simple deltas between two objects
    and then applies to any of them.
    
    For that, it firstly calculates the given time-frequency climatologies
    for both objects using 'climat_periodic_statistics' function,
    and then performs the delta calculation, 
    depending on the math operator chosen:
      1. Absolute delta: subtraction between both objects
      2. Relative delta: division between both objects
    
    Once calculated, delta values are climatologically applied to the chosen
    object, by addition if the deltas are absolute or multiplication if they
    are relative.
    
    Parameters
    ----------
    observed_series : pandas.DataFrame, xarray.Dataset or xarray.DataArray.
    reanalysis_series : pandas.DataFrame, xarray.Dataset or xarray.DataArray.
        This object can be that extracted from a reanalysis,
        CORDEX projections or similar ones.
    time_freq : str
        Time frequency to which data will be filtered.
    delta_type : {"absolute", "relative"}
    statistic : {"max", "min", "mean", "std", "sum"}
        The statistic to calculate.
        Default is "mean" so that climatologic mean is calculated.
    preference : {"observed", "reanalysis"}
        If "observed", then the observed series will be treated as the 'truth'
        and the reanalysis will be delta-corrected.
        Otherwise, though it is not common, the reanalysis will be treated
        as the truth and observations will be delta-corrected.
        Defaults to give preference over the observed series.
    keep_std_dates : bool
        If True, standard YMD (HMS) date format is kept for all climatologics
        except for yearly climatologics.
        Otherwise dates are shown as hour, day, or month indices,
        and season achronyms if "seasonal" is selected as the time frequency.
        Default value is False.
    drop_date_idx_col : bool
        Affects only if the passed object is a Pandas DataFrame.
        Boolean used to whether drop the date columns in the new data frame.
        If it is False, then the columns of the dates will be kept.
        Otherwise, the dates themselves will be kept, but they will be
        treated as indexers, and not as a column.
        Defaults to True in order to return date-time incorporated series.
    season_months : list of integers
        List containing the month numbers to later refer to the time array,
        whatever the object is among the mentioned three types.
        Defaults to None.
    delta_value : int or "auto", optional
        Controls the formatting of the delta value in output messages.
        If an integer, it specifies the number of decimal places to display.
        If "auto", it uses the best format with 2 significant digits, 
        choosing between scientific notation and floating-point.
        Defaults to 2.
    
    Returns
    -------
    obj_climat : pandas.DataFrame, xarray.Dataset or xarray.DataArray.
        Climatological average of the data.
    
    Notes
    -----
    For Pandas DataFrames, since it is an 2D object,
    it is interpreted that data holds for a specific geographical point.
    """
    
    # Input validations
    _validate_inputs(delta_type, preference, delta_value, statistic)
    
    # Define the format string based on delta_value type
    delta_format = _get_delta_format(delta_value)
    
    # Determine object type
    obj_type_observed = get_type_str(observed_series, lowercase=True)
    obj_type_reanalysis = get_type_str(reanalysis_series, lowercase=True)
    
    # Identify the time dimension and align if needed
    date_key = _align_time_dimensions(observed_series, reanalysis_series, 
                                     obj_type_observed, obj_type_reanalysis)
    
    # Calculate climatologies and deltas
    delta_obj, delta_cols = _calculate_deltas(observed_series, reanalysis_series, 
                                             time_freq, statistic, keep_std_dates, 
                                             drop_date_idx_col, season_months, 
                                             delta_type, preference, obj_type_observed, 
                                             obj_type_reanalysis, date_key)
    
    # Apply deltas to the chosen series
    delta_corrected_obj = _apply_deltas(delta_obj, delta_cols, time_freq, 
                                       delta_type, preference, obj_type_observed, 
                                       obj_type_reanalysis, date_key, 
                                       delta_format, season_months, 
                                       observed_series, reanalysis_series)
    
    return delta_corrected_obj


#--------------------------#
# Parameters and constants #
#--------------------------#

# Delta application function #
DELTA_TYPES = ["absolute", "relative"]
SUPPORTED_TIME_SERIES = ["observed", "reanalysis"]

# Statistics #
STATISTICS = ["max", "min", "sum", "mean", "std"]

# Template strings #
#------------------#

# Error strings #
UNSUPPORTED_OPTION_ERROR_TEMPLATE = "Unsupported {} '{}'. Options are {}."

# Delta application options #
DELTA_APPLICATION_INFO_TEMPLATE = """{}
Time frequency : {}
Month = {}
Day = {}
Hour = {}
"""
