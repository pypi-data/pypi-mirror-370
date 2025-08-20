#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

from typing import Callable

import numpy as np
import scipy.interpolate as scintp
import scipy.optimize as scopt

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_caller_args, get_type_str

#------------------#
# Define functions #
#------------------#

# General purpose #
#-----------------#

def polynomial_fitting(y: list | np.ndarray, 
                       poly_ord: int, 
                       fix_edges: bool = False, 
                       poly_func: Callable | None = None, 
                       poly_params: list | dict | None = None) -> np.ndarray:
    """
    Fits a polynomial to 1D data using least squares or a custom function.

    This function fits a polynomial of specified order to the data and 
    optionally allows for a custom polynomial function using curve fitting.
    It can also fix the edges of the data to preserve original values.

    Parameters
    ----------
    y : list | numpy.ndarray
        The y-coordinates (dependent variable) of the sample points.
    poly_ord : int
        The order of the polynomial to fit.
    fix_edges : bool, optional, default: False
        If True, fixes the first and last values of the fitted data 
        to match the original edges.
    poly_func : callable | None, optional
        A custom polynomial function to use for fitting. If provided, 
        `scipy.optimize.curve_fit` will be used instead of `numpy.polyfit`.
    poly_params : list | dict | None, optional
        Parameters for the custom polynomial function.

    Returns
    -------
    numpy.ndarray
        The fitted data based on the polynomial.

    Notes
    -----
    - If a custom polynomial function is provided, its parameters must 
      be compatible with `scipy.optimize.curve_fit`.
    - For large datasets, consider using polynomial fitting methods that 
      handle edge cases like fixed boundaries or specific parameter tuning.
    """
    # Flatten the input array if it's multi-dimensional
    y = np.ravel(y)
    x = np.arange(len(y))

    # Polynomial fitting using numpy or custom function
    if poly_func is None:
        coefficients = np.polyfit(x, y, poly_ord)
        polynomial = np.poly1d(coefficients)
        fitted_y = polynomial(np.linspace(x[0], x[-1], len(y)))
    else:
        popt, _ = scopt.curve_fit(poly_func, x, y, p0=poly_params)
        fitted_y = poly_func(x, *popt)

    # Optionally fix the edges to original values
    if fix_edges:
        fitted_y[0], fitted_y[-1] = y[0], y[-1]

    return fitted_y


# Data interpolation #
#--------------------#

# NumPy objects #
#-#-#-#-#-#-#-#-#

def interp_np(data: np.ndarray, 
              method: str = 'linear', 
              order: int | None = None, 
              kind: str | int = "nearest", 
              fill_value: np.ndarray | float | tuple | str = "extrapolate") -> np.ndarray:
    """
    Perform interpolation on NumPy arrays.

    Parameters
    ----------
    data : numpy.ndarray
        1D or 2D array with missing data to interpolate.
    method : {'linear', 'nearest', 'polynomial', 'spline'}, default 'linear'
        Interpolation method.
    order : int | None, optional
        Order of interpolation if using polynomial or spline methods.
    kind : str | int, optional
        Specifies the kind of interpolation as a string or as an integer 
        specifying the order of the spline interpolator to use. 
        The string has to be one of:
        - 'linear', 'nearest', 'nearest-up', 'zero', 'slinear', 'quadratic', 
          'cubic', 'previous', or 'next'. 
            - 'zero', 'slinear', 'quadratic' and 'cubic' refer to a spline
              interpolation of zeroth, first, second or third order.
            - 'previous' and 'next' simply return the previous or next value of the point.
    fill_value : array-like | (array-like, array_like) | "extrapolate", optional
        - If a ndarray (or float), this value will be used to fill in for requested 
          points outside of the data range. If not provided, then the default is NaN.
        - If a two-element tuple, then the first element is used as a fill value 
        for x_new < x[0] and the second element is used for x_new > x[-1]. 
        Anything that is not a 2-element tuple (e.g., list or ndarray, regardless of the shape) 
        is taken to be a single array-like argument meant to be used for both bounds as
        `below`, `above` = `fill_value`, `fill_value`.
        
        - Default value is 'extrapolate'
        
    Returns
    -------
    data_interpolated : numpy.ndarray
        Array with interpolated values.
    """
    # Input validations #
    #####################
    
    # General, arguments #
    param_keys = get_caller_args()
    kind_arg_pos = param_keys.index("kind")
    fillval_arg_pos = param_keys.index("fill_value")
    
    # Input data type #
    obj_type = get_type_str(data)
    if obj_type != "ndarray":
        raise TypeError("Unsupported data type. The date provided must be a NumPy array.")
    
    # Interpolation method #
    if method not in NP_XR_INTERP_METHODS:
        raise ValueError(UNSUPPORTED_OPTION_ERROR_TEMPLATE.format("interpolation method for NumPy arrays", method, NP_XR_INTERP_METHODS))
        
    # Kind (scipy's interp1D class) #
    if not isinstance(kind, int) or kind not in KIND_OPTIONS:
        raise TypeError(f"Kind of interpolation (position {kind_arg_pos}) "
                        f"must be an integer or one of {KIND_OPTIONS}.")
        
    # Fill value (scipy's interp1D class) #
    fillval_type = get_type_str(fill_value)
    if fillval_type not in FILLVAL_TYPES or fill_value != "extrapolate":
        raise TypeError(f"Fill value (position {fillval_arg_pos}) "
                        f"must be one of {FILLVAL_TYPES} or 'extrapolate'.")
          
    # Program progression #
    #######################
    
    x = np.arange(data.shape[0])
    
    if method == "linear":
        return np.interp(x, x[~np.isnan(data)], data[~np.isnan(data)])
    
    elif method == "nearest":
        f = scintp.interp1d(x[~np.isnan(data)], 
                            data[~np.isnan(data)],
                            kind="nearest",
                            fill_value="extrapolate")
        return f(x)    
    
    elif method == "polynomial":
        if order is None:
            raise ValueError("Order must be specified for polynomial interpolation.")
        coeffs = np.polyfit(x[~np.isnan(data)], data[~np.isnan(data)], order)
        return np.polyval(coeffs, x)
    
    elif method == "spline":
        if order is None:
            raise ValueError("Order must be specified for spline interpolation.")
        f = scintp.UnivariateSpline(x[~np.isnan(data)], data[~np.isnan(data)], k=order)
        return f(x)

# Pandas objects #
#-#-#-#-#-#-#-#-#-

def interp_pd(data, method: str = 'linear', order: int | None = None, axis: int = 0):
    """
    Perform interpolation on Pandas DataFrames or Series.

    Parameters
    ----------
    data : pandas.DataFrame | pandas.Series
        Data with missing values to interpolate.
    method : str
        Interpolation method, e.g., 'linear', 'polynomial', 'pad', 'bfill', 'spline'.
        Defaults to 'linear'.
    order : int | None, optional
        Order of interpolation for polynomial or spline methods.
    axis : int, optional
        Axis along which to interpolate (default is 0 for rows).

    Returns
    -------
    data_interpolated : pandas.DataFrame | pandas.Series
        Data with interpolated values.
    """
    # Input validations #
    #####################
    
    # Object type #
    obj_type = get_type_str(data, lowercase=True)
    
    if obj_type not in ["dataframe", "series"]:
        raise TypeError("Unsupported data type. The date provided must be a "
                        "pandas.DataFrame or pandas.Series object.")
    
    # Interpolation methods #
    if method not in PD_INTERP_METHODS:
        raise ValueError("Unsupported interpolation method for pandas objects: '{method}'."
                         "\nOptions are {PD_INTERP_METHODS}.")
    
    # Order specification for particular methods
    if method in ["polynomial", "spline"]:
        if order is None:
            raise ValueError(f"Order must be specified for '{method}' interpolation.")
    
    # Program progression #
    #######################
    
    return data.interpolate(method=method, order=order, axis=axis)

# Xarray objects #
#-#-#-#-#-#-#-#-#-

def interp_xr(data, method: str = 'linear', order: int | None = None, dim: str | None = None):
    """
    Perform interpolation on Xarray DataArrays or Datasets.

    Parameters
    ----------
    data : xarray.DataArray | xarray.Dataset
        Data with missing values to interpolate.
    method : {'linear', 'nearest', 'spline', 'polyfit'}, default 'linear'
        Interpolation method.
    order : int | None, optional
        Order for 'spline' or 'polyfit' interpolation.
    dim : str | None, optional
        Dimension along which to interpolate (required for Xarray).

    Returns
    -------
    data_interpolated : xarray.DataArray | xarray.Dataset
        Interpolated data.
    """
    # Input validations #
    #####################
    
    # Object type #
    obj_type = get_type_str(data, lowercase=True)
    if obj_type not in ["dataset", "dataarray"]:
        raise TypeError("Unsupported data type. The date provided must be a "
                        "xarray.Dataset or xarray.DataArray object.")
        
        
    # Interpolation method #
    if method not in NP_XR_INTERP_METHODS:
        raise ValueError(UNSUPPORTED_OPTION_ERROR_TEMPLATE.format("interpolation method for Xarray objects", method, NP_XR_INTERP_METHODS))
        
    # Dimension #
    if dim is None:
        raise ValueError("For Xarray objects, the dimension ('dim') must be "
                         "specified for interpolation.")
        
    # Program progression #
    #######################
    
    if method in ['linear', 'nearest', 'spline']:
        return data.interpolate_na(dim=dim, method=method)
    
    elif method == 'polyfit':
        if order is None:
            raise ValueError("Order must be specified for polynomial interpolation.")
        return data.polyfit(dim=dim, deg=order)
        
#--------------------------#
# Parameters and constants #
#--------------------------#

# Supported interpolation methods #
#---------------------------------#

# NumPy and Xarray objects #
NP_XR_INTERP_METHODS = ["linear", "nearest", "polynomial", "spline"]

# NumPy objects #
KIND_OPTIONS = ["linear", "nearest", "nearest-up", "zero", "slinear", "quadratic", "cubic", "previous", "next"]
FILLVAL_TYPES = ["ndarray", "float", "tuple"]

# Pandas objects #
PD_INTERP_METHODS = [
    "linear", "time", "index", "pad", 
    "ffill", "bfill",
    "nearest", "zero", "slinear", "quadratic", "cubic", "barycentric", "polynomial",
    "krogh", "piecewise_polynomial", "spline", "pchip", "akima", "cubicspline",
    "from_derivatives"
]

# Template strings #
#------------------#

UNSUPPORTED_OPTION_ERROR_TEMPLATE = "Unsupported {} '{}'. Options are {}."