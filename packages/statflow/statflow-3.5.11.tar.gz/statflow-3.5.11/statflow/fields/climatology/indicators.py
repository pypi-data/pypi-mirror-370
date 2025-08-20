#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.arrays_and_lists.patterns import count_consecutive
from statflow.core.time_series import consec_occurrences_maxdata, consec_occurrences_mindata

#------------------#
# Define functions #
#------------------#

# Climate indicator functions #
#-----------------------------#

def calculate_WSDI(season_daily_tmax: np.ndarray | list, 
                   tmax_threshold: float, 
                   min_consec_days: int) -> int:
    """
    Function that calculates the WSDI (Warm Spell Duration Index).
    
    Parameters
    ----------
    season_daily_tmax : numpy.ndarray | list
        Daily maximum temperature data of the corresponding season in units ºC.
    tmax_threshold : float
        Upper limit of the maximum temperature in units ºC.
    min_consec_days : int
        Minimum number of consecutive days for the warm spell.
    
    Returns
    -------
    int
        Number of days forming warm spells.
    """
    return consec_occurrences_maxdata(season_daily_tmax, 
                                      tmax_threshold, 
                                      min_consec=min_consec_days)


def calculate_SU(season_daily_tmax: np.ndarray | list, 
                 tmax_threshold: float = 25) -> int:
    """
    Function that calculates the SU (Summer Days).
    
    Parameters
    ----------
    season_daily_tmax : numpy.ndarray | list
        Daily maximum temperature data of the corresponding season in units ºC.
    
    tmax_threshold : float, default 25
        Upper limit of the maximum temperature in units ºC. Default is 25ºC.
    
    Returns
    -------
    int
        Number of days in which the
        maximum temperature has risen above the threshold.
    """
    return consec_occurrences_maxdata(season_daily_tmax, tmax_threshold)


def calculate_CSU(season_daily_tmax: np.ndarray | list, 
                  tmax_threshold: float = 25) -> int:
    """
    Function that calculates the CSU (Consecutive Summer Days).
    
    Parameters
    ----------
    season_daily_tmax : numpy.ndarray | list
        Daily maximum temperature data of the season in units ºC.
    
    tmax_threshold : float, default 25
        Upper limit of the maximum temperature in units ºC. Default is 25ºC.
    
    Returns
    -------
    int
        Number of maximum consecutive days in which
        the temperature has risen above the threshold.
    """
    return consec_occurrences_maxdata(season_daily_tmax,
                                      tmax_threshold,
                                      min_consec=None,
                                      calc_max_consec=True)


def calculate_FD(season_daily_tmin: np.ndarray | list, 
                 tmin_threshold: float = 0) -> int:
    """
    Function that calculates the FD (Frost Days).
    
    Parameters
    ----------
    season_daily_tmin : numpy.ndarray | list
        Daily minimum temperature data of the corresponding season in units ºC.
    
    tmin_threshold : float, default 0
        Upper limit of the minimum temperature in units ºC. Defaults to 0ºC.
    
    Returns
    -------
    int
        Number of days in which the
        minimum temperature has fallen below the threshold.
    """
    return consec_occurrences_mindata(season_daily_tmin, tmin_threshold)


def calculate_TN(season_daily_tmin: np.ndarray | list, 
                 tmin_threshold: float = 20) -> int:
    """
    Function that calculates the TN (Tropical Night Days).
    
    Parameters
    ----------
    season_daily_tmin : numpy.ndarray | list
        Daily minimum temperature data of the corresponding season in units ºC.
    
    tmin_threshold : float, default 20
        Lower limit of the minimum temperature in units ºC. Default is 20ºC.
    
    Returns
    -------
    int
        Number of nights in which the
        minimum temperature has risen above the threshold.
    """
    return consec_occurrences_mindata(season_daily_tmin,
                                      tmin_threshold,
                                      threshold_mode="above")


def calculate_RR(season_daily_precip: np.ndarray | list, 
                 precip_threshold: float) -> int:
    """
    Function that calculates the RR parameter (Wet Days).
    It is defined as the number of days in which the precipitation
    amount exceeds 1 mm.
    
    Parameters
    ----------
    season_daily_precip : numpy.ndarray | list
        Daily precipitation data of the corresponding season in units mm.
    
    precip_threshold : float
        Upper limit of the daily precipitation, 1 mm in this case.
    
    Returns
    -------
    int
        Number of days in which the
        precipitation has risen above the threshold.   
    """
    return consec_occurrences_maxdata(season_daily_precip, precip_threshold)


def calculate_CWD(season_daily_precip: np.ndarray | list, 
                  precip_threshold: float) -> int:
    """
    Function that calculates the CWD (Consecutive Wet Days),
    i.e. the number of maximum consecutive days in which
    the precipitation amount exceeds 1 mm.
    
    Parameters
    ----------
    season_daily_precip : numpy.ndarray | list
        Daily precipitation data of the season in units mm.
    
    precip_threshold : float
        Upper limit of the daily precipitation, 1 mm in this case.
    
    Returns
    -------
    int
        Number of maximum consecutive days in which
        the precipitation has risen above the threshold.
    """
    return consec_occurrences_maxdata(season_daily_precip,
                                      precip_threshold,
                                      min_consec=None,
                                      calc_max_consec=True)


def calculate_hwd(tmax: np.ndarray | list, 
                  tmin: np.ndarray | list, 
                  max_thresh: float, 
                  min_thresh: float, 
                  dates: np.ndarray | list, 
                  min_days: int) -> tuple[list[tuple], int]:
    """
    Calculate the total heat wave days (HWD) based on daily data.
    
    A heat wave is defined as a period of at least N consecutive days where
    the maximum temperature exceeds the 95th percentile (max_thresh)
    and the minimum temperature exceeds the 90th percentile (min_thresh).
    
    Parameters
    ----------
    tmax : numpy.ndarray | list
        Array of daily maximum temperatures.
    tmin : numpy.ndarray | list
        Array of daily minimum temperatures.
    max_thresh : float
        Threshold for maximum temperature (95th percentile).
    min_thresh : float
        Threshold for minimum temperature (90th percentile).
    dates : numpy.ndarray | list
        Array of dates corresponding to the temperature data.
    min_days : int
        Minimum number of consecutive days for a heat wave.
    
    Returns
    -------
    tuple[list[tuple], int]
        hwd_events : list of tuples
            Each heat wave event's duration, global intensity, peak intensity, and start date.
        total_hwd : int
            Total number of heat wave days.
    
    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> tmax = np.array([32, 33, 34, 35, 36, 35, 34, 33])
    >>> tmin = np.array([22, 23, 24, 25, 26, 25, 24, 23])
    >>> dates = pd.date_range('2023-07-01', periods=8)
    >>> hwd_events, total_hwd = calculate_hwd(tmax, tmin, 34.5, 24.5, dates, 3)
    >>> print(f"Total heat wave days: {total_hwd}")
    
    Notes
    -----
    - The function uses consecutive occurrence analysis to identify heat wave periods
    - Heat wave intensity is calculated as the average maximum temperature during the event
    - Peak intensity represents the highest maximum temperature within the heat wave
    """
    # Create a boolean array where both thresholds are satisfied
    heatwave_mask = (tmax > max_thresh) & (tmin > min_thresh)
    
    # Find consecutive blocks of heat wave days
    conv_result = np.convolve(heatwave_mask, np.ones(min_days, dtype=int), mode='valid') >= min_days
    consecutive_indices = np.flatnonzero(conv_result)
    
    hwd_events = []
    total_hwd = 0
    
    if consecutive_indices.size > 0:
        consecutive_lengths = count_consecutive(consecutive_indices)
        
        for count in consecutive_lengths:
            hw_event_indices = np.arange(consecutive_indices[0], consecutive_indices[0] + count)
            hw_max_temps = tmax[hw_event_indices]
            
            # Calculate heat wave characteristics
            duration = hw_event_indices.size
            global_intensity = hw_max_temps.sum() / duration
            peak_intensity = hw_max_temps.max()
            start_date = dates[hw_event_indices[0]]
            
            hwd_events.append((duration, global_intensity, peak_intensity, start_date))
            total_hwd += duration
            
            # Remove used indices
            consecutive_indices = consecutive_indices[count:]

    return hwd_events, total_hwd if hwd_events else ([(0, None, None, None)], 0)
