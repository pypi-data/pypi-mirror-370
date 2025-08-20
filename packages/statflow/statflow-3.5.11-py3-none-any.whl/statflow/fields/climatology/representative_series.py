#!/usr/bin/env python3
# -*- coding: utf-8 

#----------------#
# Import modules #
#----------------#

import numpy as np
import pandas as pd

#------------------------#
# Import project modules #
#------------------------#

from paramlib.global_parameters import COMMON_DELIMITER_LIST
from statflow.core.interpolation_methods import polynomial_fitting
from statflow.core.time_series import periodic_statistics

#-------------------------#
# Define custom functions #
#-------------------------#

# Hourly Design Year #
#--------------------#

# Main function #
#-#-#-#-#-#-#-#-#

def calculate_HDY(hourly_df: pd.DataFrame, 
                  varlist: list[str], 
                  varlist_primary: list[str], 
                  drop_new_idx_col: bool = False) -> tuple[pd.DataFrame, list[int]]:
    """
    Calculate the Hourly Design Year (HDY) using ISO 15927-4:2005 (E) standard.
    
    The HDY is a representative year constructed by selecting the most typical
    month from each calendar month across the historical record, based on
    statistical ranking of primary meteorological variables.
    
    Parameters
    ----------
    hourly_df : pd.DataFrame
        DataFrame containing hourly climatological data with a 'date' column
        and meteorological variables.
    varlist : list[str]
        List of all variables (column names) to be included in the HDY DataFrame.
        Must include 'date' as the first element.
    varlist_primary : list[str]
        Primary variables to be used for ranking calculations. These variables
        determine which year's data is selected for each month.
        Must include 'date' as the first element.
    drop_new_idx_col : bool, default False
        Whether to drop the reset index column during processing.
        
    Returns
    -------
    tuple[pd.DataFrame, list[int]]
        hdy_dataframe : pd.DataFrame
            Complete HDY DataFrame with hourly data for the representative year.
        selected_years : list[int]
            List of selected years for each month (12 elements).
    
    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> 
    >>> # Create sample hourly data
    >>> dates = pd.date_range('2020-01-01', '2023-12-31 23:00', freq='H')
    >>> hourly_data = {
    ...     'date': dates,
    ...     'temperature': np.random.normal(15, 10, len(dates)),
    ...     'humidity': np.random.normal(70, 20, len(dates)),
    ...     'wind_speed': np.random.exponential(3, len(dates))
    ... }
    >>> hourly_df = pd.DataFrame(hourly_data)
    >>> 
    >>> # Define variable lists
    >>> varlist = ['date', 'temperature', 'humidity', 'wind_speed']
    >>> varlist_primary = ['date', 'temperature', 'humidity']
    >>> 
    >>> # Calculate HDY
    >>> hdy_df, selected_years = calculate_HDY(hourly_df, varlist, varlist_primary)
    >>> print(f"Selected years: {selected_years}")
    >>> print(f"HDY shape: {hdy_df.shape}")
    
    Raises
    ------
    ValueError
        If the primary variables are not found in the DataFrame columns.
    KeyError
        If the 'date' column is missing from the DataFrame.
    IndexError
        If insufficient data is available for any month.
        
    Notes
    -----
    The HDY calculation follows these steps for each calendar month:
    
    1. **Daily Aggregation**: Calculate daily means for each primary variable
    2. **Ranking**: Rank each day within the month for each variable
    3. **Probability Calculation**: Convert ranks to cumulative probabilities (φ)
    4. **Annual Evaluation**: For each year, calculate the sum of absolute 
       deviations from the overall monthly φ values
    5. **Year Selection**: Choose the year with the minimum total deviation
    
    The mathematical foundation uses cumulative probability:
    φ = (rank - 0.5) / number_of_days
    
    For each year y and variable v:
    F_s(y,v) = Σ|φ_actual(d,v) - φ_monthly(d,v)|
    
    The selected year minimizes: F_s_total(y) = Σ F_s(y,v)
    
    **Data Requirements:**
    - Continuous hourly data for multiple years
    - At least one complete year of data
    - Primary variables should be meteorologically relevant
    
    **Limitations:**
    - The method assumes stationarity in climate statistics
    - Extreme years may be under-represented
    - Requires sufficient data for robust statistics
    
    References
    ----------
    ISO 15927-4:2005(E) - Hygrothermal performance of buildings - Calculation 
    and presentation of climatic data - Part 4: Hourly data for assessing the 
    annual energy use for heating and cooling.
    """
    # Initialise the HDY DataFrame to store results
    hdy_df = pd.DataFrame(columns=varlist)

    # Extract unique years and months
    hist_years = pd.unique(hourly_df.date.dt.year)
    months = pd.unique(hourly_df.date.dt.month)

    # List to store selected years for each month
    hdy_years = []

    for m in months:
        try:
            # Filter data for the current month and calculate monthly statkit
            hdata_MONTH = hourly_df[hourly_df.date.dt.month == m].filter(items=varlist_primary).reset_index(drop=drop_new_idx_col)
            hdata_MONTH_rank_phi = hdata_MONTH.copy()
            
            # Step a: Calculate daily means for the primary variables
            hdata_MONTH_dm_bymonth = periodic_statistics(hourly_df[hourly_df.date.dt.month == m], varlist_primary, 'day', 'mean')
            
            

        except ValueError as e:
            print(f"Error in periodic_statistics for month {m}: {e}")
            continue  # Skip the current month if there's an error

        # Get unique days for the current month
        no_of_days = len(pd.unique(hdata_MONTH_rank_phi.date.dt.day))

        # Step a: Calculate rankings for each day by each primary variable
        dict_rank = {}
        dict_phi = {}
        
        for var in varlist_primary[1:]:
            var_orig = hdata_MONTH_dm_bymonth[var].to_numpy()
            var_rank = np.argsort(np.argsort(var_orig)) + 1
            dict_rank[var] = var_rank

            # Step b: Calculate cumulative probabilities (phi)
            phi = (var_rank - 0.5) / no_of_days
            dict_phi[var] = phi

            # Store calculated phi values
            hdata_MONTH_rank_phi[var] = phi
        
        # Step c: Group data by year and calculate year-specific ranks
        dict_rank_per_year = {}
        for year in hist_years:
            year_data = hdata_MONTH_rank_phi[hdata_MONTH_rank_phi.date.dt.year == year]
            dict_rank_per_year[year] = {
                var: np.sum(np.abs(year_data[var] - dict_phi[var]))
                for var in varlist_primary[1:]
            }

        # Step d: Calculate total sum of deviations (Fs_sum) for each year
        Fs_sum = {}
        for year, ranks in dict_rank_per_year.items():
            Fs_sum[year] = sum(ranks.values())

        # Step e: Rank the years based on the Fs_sum and choose the best year for the current month
        selected_year = min(Fs_sum, key=Fs_sum.get)
        hdy_years.append(selected_year)

        # Extract the hourly data for the selected year and append it to the HDY DataFrame
        hourly_data_sel = \
        hourly_df[(hourly_df.date.dt.year == selected_year) 
                  & (hourly_df.date.dt.month == m)].filter(items=varlist)\
                 .reset_index(drop=drop_new_idx_col)
        hdy_df = pd.concat([hdy_df, hourly_data_sel], axis=0)

    return hdy_df, hdy_years


# Helpers #
#-#-#-#-#-#

def hdy_interpolation(hdy_df: pd.DataFrame,
                      hdy_years: list[int],
                      previous_month_last_time_range: str,
                      next_month_first_time_range: str,
                      varlist_to_interpolate: list[str],
                      polynomial_order: int,
                      drop_date_idx_col: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Interpolates variables between months in an HDY to smooth transitions.

    Since the HDY is composed of 'fragments' from different years, there are
    unavoidable discontinuities at month boundaries. This function applies
    polynomial interpolation to smooth these transitions between consecutive months.

    Parameters
    ----------
    hdy_df : pd.DataFrame
        DataFrame containing the HDY hourly data with a 'date' column.
    hdy_years : list[int]
        List of selected years corresponding to each month in HDY (12 elements).
    previous_month_last_time_range : str
        Time range for the last hours of the previous month (format: "HH:MM").
        Example: "20:23" for hours 20, 21, 22, 23.
    next_month_first_time_range : str
        Time range for the first hours of the next month (format: "HH:MM").
        Example: "0:3" for hours 0, 1, 2, 3.
    varlist_to_interpolate : list[str]
        Variables to be interpolated between months. Should not include 'date'.
        Wind speed ('ws10') is automatically excluded as it's derived from u10, v10.
    polynomial_order : int
        Order of the polynomial to use for fitting (1=linear, 2=quadratic, 3=cubic, etc.).
    drop_date_idx_col : bool, default False
        Whether to drop the index column during processing.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        hdy_interp : pd.DataFrame
            HDY DataFrame with interpolated variables and smoothed transitions.
        wind_dir_meteo_interp : pd.DataFrame
            Interpolated meteorological wind direction data.

    Examples
    --------
    >>> # Assuming you have an HDY DataFrame and selected years
    >>> varlist_interp = ['temperature', 'humidity', 'u10', 'v10']
    >>> 
    >>> hdy_smooth, wind_dir = hdy_interpolation(
    ...     hdy_df=hdy_dataframe,
    ...     hdy_years=selected_years,
    ...     previous_month_last_time_range="20:23",
    ...     next_month_first_time_range="0:3",
    ...     varlist_to_interpolate=varlist_interp,
    ...     polynomial_order=3
    ... )
    >>> 
    >>> print("Interpolation completed successfully")
    >>> print(f"Original shape: {hdy_dataframe.shape}")
    >>> print(f"Smoothed shape: {hdy_smooth.shape}")

    Raises
    ------
    ValueError
        If the time range format is incorrect or polynomial_order < 1.
    KeyError
        If required variables are not found in the DataFrame.
    IndexError
        If insufficient data is available for interpolation.

    Notes
    -----
    **Interpolation Process:**
    
    1. **Time Range Extraction**: For each consecutive month pair, extract
       data from the specified time ranges at month boundaries
    2. **Polynomial Fitting**: Apply polynomial fitting to smooth the transition
       using the `polynomial_fitting` function with edge preservation
    3. **Wind Speed Calculation**: Recalculate wind speed modulus from
       interpolated u10 and v10 components
    4. **Wind Direction**: Calculate meteorological wind direction using
       the meteorological convention (0° = North, clockwise positive)

    **Wind Direction Convention:**
    - u component: positive when wind is westerly (blows from west to east)
    - v component: positive when wind is northerly (blows from south to north)
    - Direction: antiparallel to wind vector (direction wind comes FROM)
    - 0° corresponds to wind from North, increasing clockwise

    **Time Range Format:**
    The time range strings should be in "HH:MM" format where:
    - Single hours: "0:3" means hours 0, 1, 2, 3
    - Multiple hours: "20:23" means hours 20, 21, 22, 23

    **Polynomial Orders:**
    - Order 1: Linear interpolation
    - Order 2: Quadratic interpolation  
    - Order 3: Cubic interpolation (recommended for smooth transitions)
    - Higher orders: May cause overfitting with oscillations

    **Performance Considerations:**
    - Processing time increases with polynomial order
    - Memory usage scales with the number of variables interpolated
    - For large datasets, consider interpolating only essential variables

    **Limitations:**
    - Assumes monotonic time progression within each month
    - May not preserve physical relationships between variables
    - Edge effects at the beginning and end of the time series

    See Also
    --------
    calculate_HDY : Generate the initial HDY data
    polynomial_fitting : Core polynomial interpolation function
    """
    hdy_interp = hdy_df.copy()

    # Remove 'ws10' from interpolation list since it's derived from u10, v10
    if "ws10" in varlist_to_interpolate:
        varlist_to_interpolate.remove("ws10")

    for i in range(len(hdy_years) - 1):
        # Extract time slices for interpolation between consecutive months
        days_slice_prev = hdy_interp[(hdy_interp.date.dt.year == hdy_years[i]) &
                                     (hdy_interp.date.dt.month == hdy_interp.date.dt.month[i])]

        days_slice_next = hdy_interp[(hdy_interp.date.dt.year == hdy_years[i + 1]) &
                                     (hdy_interp.date.dt.month == hdy_interp.date.dt.month[i + 1])]

        # Handle time ranges as integers (hours), split the input range strings
        pml1, pml2 = map(int, previous_month_last_time_range.split(SPLIT_DELIM))
        nmf1, nmf2 = map(int, next_month_first_time_range.split(SPLIT_DELIM))

        # Extract the time slices based on the provided ranges
        df_slice1 = days_slice_prev[(days_slice_prev.date.dt.hour >= pml1) & (days_slice_prev.date.dt.hour <= pml2)]
        df_slice2 = days_slice_next[(days_slice_next.date.dt.hour >= nmf1) & (days_slice_next.date.dt.hour <= nmf2)]

        # Concatenate and reset indices for interpolation
        df_slice_to_fit = pd.concat([df_slice1, df_slice2]).reset_index(drop=drop_date_idx_col)

        # Polynomial fitting for each variable in varlist_to_interpolate
        for var in varlist_to_interpolate:
            y_var = df_slice_to_fit[var].to_numpy()  # Dependent variable (data values)
            fitted_values = polynomial_fitting(y_var, polynomial_order, fix_edges=True)

            # Apply the interpolated values back into the DataFrame
            df_slice_to_fit[var] = fitted_values

            # Update the main HDY DataFrame
            hdy_interp.loc[df_slice_to_fit.index, var] = fitted_values

    # Calculate wind speed modulus based on interpolated u10 and v10
    """
    On the wind direction calculus
    ------------------------------
    
    ·The sign of both components follow the standard convention:
        * u is positive when the wind is westerly,
          i.e wind blows from the west and is eastwards.
        * v is positive when the wind is northwards,
          i.e wind blows from the south.
          
    ·From the meteorological point of view,
     the direction of the wind speed vector is taken as
     the antiparallel image vector.
     The zero-degree angle is set 90º further than the
     default unit circle, so that 0º means wind blowing from the North. 
    """   
    hdy_interp["ws10"] = np.sqrt(hdy_interp.u10 ** 2 + hdy_interp.v10 ** 2)

    # Calculate wind direction using meteorological convention
    print("\nCalculating the wind direction from the meteorological point of view...")
    # Import here to avoid circular imports
    from climalab.meteorological_variables import meteorological_wind_direction
    wind_dir_meteo_interp = meteorological_wind_direction(hdy_interp.u10.values, hdy_interp.v10.values)

    return hdy_interp, wind_dir_meteo_interp


#--------------------------#
# Parameters and constants #
#--------------------------#

SPLIT_DELIM = COMMON_DELIMITER_LIST[3]
