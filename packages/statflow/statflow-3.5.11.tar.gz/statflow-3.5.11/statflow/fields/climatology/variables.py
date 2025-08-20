#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np
import scipy.stats as ss

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.arrays_and_lists.maths import window_sum

#-------------------------#
# Define custom functions #
#-------------------------#

# Atmospheric variables #
#-----------------------#

# Biovariables: set of atmospheric variables #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

def biovars(tmax_monthly_climat, tmin_monthly_climat, prec_monthly_climat):
    """
    Function that calculates 19 bioclimatic variables
    based on monthly climatologic data, for every horizontal grid point.
    
    Parameters
    ----------
    tmax_monthly_climat : numpy.ndarray
          Array containing the monthly climatologic maximum temperature data.
    tmin_monthly_climat : numpy.ndarray
          Array containing the monthly climatologic minimum temperature data.
    precip_dataset : numpy.ndarray
          Array containing the monthly climatologic precipitation data.
    
    Returns
    -------
    p : numpy.ndarray
          Array containing the bioclimatic data for the considered period.
          structured as (biovariable, lat, lon).
    """

    dimensions = tmax_monthly_climat.shape
    bioclim_var_array = np.zeros((19, dimensions[1], dimensions[2]))
     
    # tavg = (tmin_monthly_climat + tmax_monthly_climat) / 2
    tavg = np.mean((tmax_monthly_climat, tmin_monthly_climat), axis=0)
    range_temp = tmax_monthly_climat - tmin_monthly_climat
      
    # P1. Annual Mean Temperature
    bioclim_var_array[0] = np.mean(tavg, axis=0)
      
    # P2. Mean Diurnal Range(Mean(period max-min))
    bioclim_var_array[1] = np.mean(range_temp, axis=0)
      
    # P4. Temperature Seasonality (standard deviation)
    bioclim_var_array[3] = np.std(tavg, axis=0) # * 100
      
    # P5. Max Temperature of Warmest Period 
    bioclim_var_array[4] = np.max(tmax_monthly_climat, axis=0)
     
    # P6. Min Temperature of Coldest Period
    bioclim_var_array[5] = np.min(tmin_monthly_climat, axis=0)
      
    # P7. Temperature Annual Range (P5 - P6)
    bioclim_var_array[6] = bioclim_var_array[4] - bioclim_var_array[5]
      
    # P3. Isothermality ((P2 / P7) * 100)
    bioclim_var_array[2] = bioclim_var_array[1] / bioclim_var_array[6] * 100
      
    # P12. Annual Precipitation
    bioclim_var_array[11] = np.sum(prec_monthly_climat, axis=0)
      
    # P13. Precipitation of Wettest Period
    bioclim_var_array[12] = np.max(prec_monthly_climat, axis=0)
      
    # P14. Precipitation of Driest Period
    bioclim_var_array[13] = np.min(prec_monthly_climat, axis=0)
    
    # P15. Precipitation Seasonality(Coefficient of Variation) 
    # the "+1" is to avoid strange CVs for areas where the mean rainfall is < 1 mm)
    bioclim_var_array[14] = ss.variation(prec_monthly_climat+1, axis=0) * 100
    
    # precipitation by quarters (window of 3 months)
    wet = window_sum(prec_monthly_climat, N=3)
    # P16. Precipitation of Wettest Quarter
    bioclim_var_array[15] = np.max(wet, axis=0)
      
    # P17. Precipitation of Driest Quarter 
    bioclim_var_array[16] = np.min(wet, axis=0)
      
    # temperature by quarters (window of 3 months)
    tmp_qrt = window_sum(tavg, N=3) / 3
      
    # P8. Mean Temperature of Wettest Quarter
    wet_qrt = np.argmax(wet, axis=0)
    for i in range(dimensions[1]):
        for j in range(dimensions[2]):
            bioclim_var_array[7,i,j] = tmp_qrt[wet_qrt[i,j],i,j]
      
    # P9. Mean Temperature of Driest Quarter
    dry_qrt = np.argmin(wet, axis=0)
    for i in range(dimensions[1]):
        for j in range(dimensions[2]):
            bioclim_var_array[8,i,j] = tmp_qrt[dry_qrt[i,j],i,j]
    
    # P10 Mean Temperature of Warmest Quarter 
    bioclim_var_array[9] = np.max(tmp_qrt, axis=0)
      
    # P11 Mean Temperature of Coldest Quarter
    bioclim_var_array[10] = np.min(tmp_qrt, axis=0)
          
    # P18. Precipitation of Warmest Quarter 
    hot_qrt = np.argmax(tmp_qrt, axis=0)
    for i in range(dimensions[1]):
        for j in range(dimensions[2]):
            bioclim_var_array[17,i,j] = wet[hot_qrt[i,j],i,j]
     
    # P19. Precipitation of Coldest Quarter 
    cold_qrt = np.argmin(tmp_qrt, axis=0)
    for i in range(dimensions[1]):
        for j in range(dimensions[2]):
            bioclim_var_array[18,i,j] = wet[cold_qrt[i,j],i,j]
    
    print("Biovariables have been successfully computed.")
    return bioclim_var_array

# Meteorological variables #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-

def calculate_saturation_vapor_pressure(temperature):
    """
    Calculate saturation vapor pressure using the Magnus formula.
    
    This function computes the saturation vapor pressure over water
    using the Magnus-Tetens approximation, which is accurate for
    temperatures between -40°C and +50°C.
    
    Parameters
    ----------
    temperature : numpy.ndarray | pandas.Series | float
        Temperature in degrees Celsius.
    
    Returns
    -------
    numpy.ndarray | pandas.Series | float
        Saturation vapor pressure in hPa (hectopascals).
    
    Notes
    -----
    The Magnus formula used is:
    e_s = 6.112 * exp(17.67 * T / (T + 243.5))
    
    Where:
    - e_s is saturation vapor pressure in hPa
    - T is temperature in °C
    
    References
    ----------
    Magnus, G. (1844). Versuche über die Spannkräfte des Wasserdampfs.
    Annalen der Physik und Chemie, 61(2), 225-247.
    """
    return 6.112 * np.exp(17.67 * temperature / (temperature + 243.5))


def calculate_actual_vapor_pressure(temperature, relative_humidity):
    """
    Calculate actual vapor pressure from temperature and relative humidity.
    
    Parameters
    ----------
    temperature : numpy.ndarray | pandas.Series | float
        Temperature in degrees Celsius.
    relative_humidity : numpy.ndarray | pandas.Series | float
        Relative humidity as a percentage (0-100).
    
    Returns
    -------
    numpy.ndarray | pandas.Series | float
        Actual vapor pressure in hPa (hectopascals).
    
    Notes
    -----
    The actual vapor pressure is calculated as:
    e_a = (RH / 100) * e_s
    
    Where:
    - e_a is actual vapor pressure in hPa
    - RH is relative humidity in %
    - e_s is saturation vapor pressure in hPa
    """
    e_s = calculate_saturation_vapor_pressure(temperature)
    return (relative_humidity / 100.0) * e_s


def calculate_dew_point(temperature, relative_humidity):
    """
    Calculate dew point temperature from temperature and relative humidity.
    
    Parameters
    ----------
    temperature : numpy.ndarray | pandas.Series | float
        Temperature in degrees Celsius.
    relative_humidity : numpy.ndarray | pandas.Series | float
        Relative humidity as a percentage (0-100).
    
    Returns
    -------
    numpy.ndarray | pandas.Series | float
        Dew point temperature in degrees Celsius.
    
    Notes
    -----
    The dew point is calculated using the Magnus formula inversion:
    T_d = 243.5 * ln(e_a / 6.112) / (17.67 - ln(e_a / 6.112))
    
    Where:
    - T_d is dew point temperature in °C
    - e_a is actual vapor pressure in hPa
    """
    e_a = calculate_actual_vapor_pressure(temperature, relative_humidity)
    ln_ratio = np.log(e_a / 6.112)
    return 243.5 * ln_ratio / (17.67 - ln_ratio)


def calculate_heat_index(temperature, relative_humidity, unit="celsius"):
    """
    Calculate heat index (apparent temperature) from temperature and relative humidity.
    
    The heat index is a measure of how hot it feels when relative humidity
    is factored in with the actual air temperature.
    
    Parameters
    ----------
    temperature : numpy.ndarray | pandas.Series | float
        Temperature in degrees Celsius or Fahrenheit (depending on unit parameter).
    relative_humidity : numpy.ndarray | pandas.Series | float
        Relative humidity as a percentage (0-100).
    unit : {"celsius", "fahrenheit"}, default "celsius"
        Temperature unit for input and output.
    
    Returns
    -------
    numpy.ndarray | pandas.Series | float
        Heat index in the same temperature unit as input.
    
    Notes
    -----
    This function uses the Rothfusz regression equation, which is most
    accurate for temperatures above 26.7°C (80°F) and relative humidity above 40%.
    
    For temperatures below this range, the simple average of temperature
    and relative humidity effects is used.
    """
    
    # Convert to Fahrenheit if needed for calculation
    if unit == "celsius":
        temp_f = temperature * 9/5 + 32
    else:
        temp_f = temperature
    
    # Heat index calculation (Rothfusz regression)
    # Valid for temp >= 80°F and RH >= 40%
    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -6.83783e-3
    c6 = -5.481717e-2
    c7 = 1.22874e-3
    c8 = 8.5282e-4
    c9 = -1.99e-6
    
    # Calculate heat index in Fahrenheit
    hi_f = (c1 + c2 * temp_f + c3 * relative_humidity + 
            c4 * temp_f * relative_humidity + 
            c5 * temp_f**2 + c6 * relative_humidity**2 + 
            c7 * temp_f**2 * relative_humidity + 
            c8 * temp_f * relative_humidity**2 + 
            c9 * temp_f**2 * relative_humidity**2)
    
    # For conditions where the simple formula is more accurate
    simple_hi_f = 0.5 * (temp_f + 61.0 + ((temp_f - 68.0) * 1.2) + (relative_humidity * 0.094))
    
    # Use simple formula for lower temperatures/humidity
    mask = (temp_f < 80) | (relative_humidity < 40)
    if np.isscalar(temp_f):
        hi_f = simple_hi_f if mask else hi_f
    else:
        hi_f = np.where(mask, simple_hi_f, hi_f)
    
    # Convert back to Celsius if needed
    if unit == "celsius":
        return (hi_f - 32) * 5/9
    else:
        return hi_f


def calculate_wind_chill(temperature, wind_speed, unit="celsius"):
    """
    Calculate wind chill temperature from temperature and wind speed.
    
    Wind chill is the perceived decrease in air temperature felt by the body
    on exposed skin due to the flow of air.
    
    Parameters
    ----------
    temperature : numpy.ndarray | pandas.Series | float
        Temperature in degrees Celsius or Fahrenheit (depending on unit parameter).
    wind_speed : numpy.ndarray | pandas.Series | float
        Wind speed in km/h or mph (depending on unit parameter).
    unit : {"celsius", "fahrenheit"}, default "celsius"
        Unit system for temperature and wind speed.
        - "celsius": Temperature in °C, wind speed in km/h
        - "fahrenheit": Temperature in °F, wind speed in mph
    
    Returns
    -------
    numpy.ndarray | pandas.Series | float
        Wind chill temperature in the same unit as input temperature.
    
    Notes
    -----
    This function uses the North American wind chill formula, which is
    most accurate for temperatures at or below 10°C (50°F) and wind speeds
    above 4.8 km/h (3 mph).
    
    The formula used depends on the unit system:
    - Celsius: WC = 13.12 + 0.6215*T - 11.37*V^0.16 + 0.3965*T*V^0.16
    - Fahrenheit: WC = 35.74 + 0.6215*T - 35.75*V^0.16 + 0.4275*T*V^0.16
    
    Where T is temperature and V is wind speed.
    """
    
    if unit == "celsius":
        # Wind chill formula for Celsius and km/h
        wind_chill = (13.12 + 0.6215 * temperature - 
                     11.37 * (wind_speed ** 0.16) + 
                     0.3965 * temperature * (wind_speed ** 0.16))
    elif unit == "fahrenheit":
        # Wind chill formula for Fahrenheit and mph
        wind_chill = (35.74 + 0.6215 * temperature - 
                     35.75 * (wind_speed ** 0.16) + 
                     0.4275 * temperature * (wind_speed ** 0.16))
    else:
        raise ValueError("Unit must be either 'celsius' or 'fahrenheit'")
    
    # Wind chill is only meaningful for low temperatures and significant wind
    if unit == "celsius":
        temp_threshold = 10.0  # °C
        wind_threshold = 4.8   # km/h
    else:
        temp_threshold = 50.0  # °F
        wind_threshold = 3.0   # mph
    
    # Only apply wind chill when conditions are appropriate
    if np.isscalar(temperature):
        if temperature > temp_threshold or wind_speed < wind_threshold:
            return temperature
        else:
            return wind_chill
    else:
        return np.where((temperature > temp_threshold) | (wind_speed < wind_threshold),
                       temperature, wind_chill)
                       

def calculate_specific_humidity(temperature, relative_humidity, pressure=1013.25):
    """
    Calculate specific humidity from temperature, relative humidity, and pressure.
    
    Specific humidity is the ratio of water vapor mass to the total mass
    of the air parcel (dry air + water vapor).
    
    Parameters
    ----------
    temperature : numpy.ndarray | pandas.Series | float
        Temperature in degrees Celsius.
    relative_humidity : numpy.ndarray | pandas.Series | float
        Relative humidity as a percentage (0-100).
    pressure : numpy.ndarray | pandas.Series | float, default 1013.25
        Atmospheric pressure in hPa (hectopascals).
    
    Returns
    -------
    numpy.ndarray | pandas.Series | float
        Specific humidity in kg/kg (dimensionless).
    
    Notes
    -----
    The specific humidity is calculated using:
    q = 0.622 * e_a / (p - 0.378 * e_a)
    
    Where:
    - q is specific humidity in kg/kg
    - e_a is actual vapor pressure in hPa
    - p is atmospheric pressure in hPa
    - 0.622 is the ratio of molecular weights (water vapor / dry air)
    """
    e_a = calculate_actual_vapor_pressure(temperature, relative_humidity)
    return 0.622 * e_a / (pressure - 0.378 * e_a)
