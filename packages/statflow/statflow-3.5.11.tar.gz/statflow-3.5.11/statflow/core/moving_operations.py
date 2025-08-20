#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for moving operations in statistical analysis.

This module provides functions to compute the moving sum and moving average
of arrays, supporting operations on both one-dimensional and multi-dimensional arrays.
These functions are designed to facilitate analysis across various
domains, including finance, climate science, and more.
"""

#----------------#
# Import modules #
#----------------#

import numpy as np
from scipy.signal import convolve

#------------------#
# Define functions #
#------------------#

def window_sum(x: np.ndarray, N: int) -> np.ndarray:
    """
    Computes the sum of elements in an array using a sliding window (moving sum).
    Applicable to any multidimensional array.
    
    Parameters
    ----------
    x : numpy.ndarray
        Input array containing data.
    N : int
        Window size.
    
    Returns
    -------
    sum_window : numpy.ndarray
        The moving sum of the elements.
    
    Notes
    -----
    Designed for general use cases, including climate science, where typical array 
    shape could be (time, lat, lon). Uses numpy for 1D arrays and switches to 
    scipy.convolve for n-dimensional arrays.
    """
    dims = x.ndim
    
    if dims == 1:
        try:
            sum_window = np.convolve(x, np.ones(N, np.int64), mode="valid")
        except:
            sum_window = np.convolve(x, np.ones(N, np.float64), mode="valid")

    elif dims > 1:   
        number_of_ones = np.append(N, np.repeat(1, dims-1))
        ones_size_tuple = tuple(number_of_ones)
             
        try:
            sum_window = convolve(x, np.ones(ones_size_tuple, np.int64), mode="same")[1:]
        except:
            sum_window = convolve(x, np.ones(ones_size_tuple, np.float64), mode="same")[1:]
            
    else:
        raise ValueError("Scalar given, must be an array of N >= 1")
        
    return sum_window

    
def moving_average(x: np.ndarray, N: int) -> np.ndarray:
    """
    Returns the moving average of an array, irrespective of dimension.
    Uses the moving sum function and divides by the window size N.
    
    Parameters
    ----------
    x : numpy.ndarray
        Input array containing data.
    N : int
        Window size.
    
    Returns
    -------
    numpy.ndarray
        The moving average of the array.
    """
    return window_sum(x, N) / N