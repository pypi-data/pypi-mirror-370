#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.strings.text_formatters import format_string

#------------------#
# Define functions #
#------------------#

# Signal processing #
#-------------------#

# Forcing #
#~~~~~~~~~#

# Noise handling #
#-#-#-#-#-#-#-#-#-
    
def signal_whitening(data: np.ndarray, method: str = "classic") -> np.ndarray:
    """
    Function to perform signal whitening (decorrelation) on the input data.

    Parameters
    ----------
    data : numpy.ndarray
        The input signal data that requires whitening. It should be a 1D or 2D array.
    method : str, optional
        The whitening method to apply. Supported options are:
        - "classic": Uses the covariance matrix method to decorrelate the data.
        - "sklearn": Uses PCA (Principal Component Analysis) for whitening via sklearn.
        - "zca": Uses ZCA whitening which is a form of whitening that retains
          more resemblance to the original data.

    Returns
    -------
    whitened_data : numpy.ndarray
        The whitened version of the input data.
    
    Notes
    -----
    - Classic whitening: It ensures that the data has unit variance, and no correlations between dimensions.
    - sklearn whitening: This uses PCA from the sklearn library to perform decorrelation.
    - ZCA whitening: Zero Component Analysis whitening retains data structure while decorrelating.
    """
    
    from scipy import linalg
    from sklearn.decomposition import PCA
    
    # Classic whitening method using covariance matrix
    if method == "classic":
        data_mean = data - np.mean(data, axis=0)
        cov_matrix = np.cov(data_mean, rowvar=False)
        eigvals, eigvecs = linalg.eigh(cov_matrix)
        whitening_matrix = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T
        whitened_data = data_mean @ whitening_matrix
        return whitened_data
    
    # Whitening using PCA from sklearn
    elif method == "sklearn":
        pca = PCA(whiten=True)
        whitened_data = pca.fit_transform(data)
        return whitened_data
    
    # ZCA whitening
    elif method == "zca":
        data_mean = data - np.mean(data, axis=0)
        cov_matrix = np.cov(data_mean, rowvar=False)
        eigvals, eigvecs = linalg.eigh(cov_matrix)
        whitening_matrix = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T
        zca_whitening_matrix = eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.T
        whitened_data = data_mean @ zca_whitening_matrix
        return whitened_data
    
    else:
        format_args_whitening = ("whitening method", method, SIGNAL_FORCING_METHODS)
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_whitening))
        
# Filtering #
#~~~~~~~~~~~#

def low_pass_filter(data: np.ndarray, window_size: int = 3) -> np.ndarray:
    """
    Applies a simple moving average (SMA) low-pass filter to the input data.
    
    This function smooths the input signal by averaging over a sliding window,
    effectively filtering out high-frequency noise.
    
    Parameters
    ----------
    data : array-like
        The input time series data to be filtered.
    window_size : int, optional, default=3
        The size of the moving window over which to average the signal.
        A larger window will provide more smoothing but may reduce important signal details.
        
    Returns
    -------
    filtered_data : np.ndarray
        The filtered time series with reduced high-frequency noise.
    
    Notes
    -----
    The simple moving average filter is a basic low-pass filter
    and is useful for removing short-term fluctuations in data.
    """
    
    if window_size < 1:
        raise ValueError("Window size must be a positive integer.")
    
    window = np.ones(window_size) / window_size
    filtered_data = np.convolve(data, window, mode='valid')
    
    return filtered_data


def high_pass_filter(data: np.ndarray) -> np.ndarray:
    """
    Applies a simple high-pass filter by taking the difference between consecutive points in the time series.
    
    This function is useful for extracting high-frequency components and removing slow trends from the data.
    
    Parameters
    ----------
    data : array-like
        The input time series data to be filtered.
    
    Returns
    -------
    filtered_data : np.ndarray
        The high-pass filtered data, emphasizing rapid changes and removing slow trends.
    
    Notes
    -----
    High-pass filtering is used to isolate high-frequency changes in the data,
    which can be useful for detecting sudden events or fluctuations.
    """
    
    filtered_data = np.diff(data, n=1)
    return filtered_data


def band_pass1(original: np.ndarray, timestep: float, low_freq: float, high_freq: float) -> np.ndarray:
    """
    Band-pass filter, method 1.

    This filter works in the frequency domain by selecting a desired frequency range
    and zeroing out the Fourier coefficients for frequencies outside that range.

    The signal is then converted back to the time domain.

    Parameters
    ----------
    original : np.ndarray
        The original time series data to be filtered.
    timestep : float
        Time step between successive data points in the time series.
    low_freq : float
        The lower frequency bound for the band-pass filter.
    high_freq : float
        The upper frequency bound for the band-pass filter.

    Returns
    -------
    band_filtered : np.ndarray
        The band-pass filtered signal in the time domain.

    Notes
    -----
    This function processes the data entirely in the frequency domain. 
    Do not work directly with the time-domain signal.
    """

    # Convert original time series to frequency domain
    fourier_orig = np.fft.fft(original)
    n = len(fourier_orig)

    # Get the corresponding frequency values
    freqs_orig = np.fft.fftfreq(n, timestep)

    # Create a mask for the desired frequency range
    freq_mask = (freqs_orig >= low_freq) & (freqs_orig <= high_freq)

    # Zero out Fourier coefficients outside the desired frequency range
    new_fourier = np.zeros_like(fourier_orig)
    new_fourier[freq_mask] = fourier_orig[freq_mask]

    # Convert the filtered signal back to the time domain
    band_filtered = np.real(np.fft.ifft(new_fourier))
    return band_filtered


def band_pass2(original: np.ndarray, low_filtered_all_highfreq: np.ndarray, low_filtered_all_lowfreq: np.ndarray) -> np.ndarray:
    """
    Band-pass filter, method 2.

    This filter creates a band-pass filter by subtracting the results of 
    two low-pass filters: one with a higher cutoff frequency and another
    with a lower cutoff frequency.

    Parameters
    ----------
    original : np.ndarray
        The original time series data to be filtered.
    low_filtered_all_highfreq : np.ndarray
        The result of applying a low-pass filter with a higher cutoff frequency.
    low_filtered_all_lowfreq : np.ndarray
        The result of applying a low-pass filter with a lower cutoff frequency.

    Returns
    -------
    band_filtered : np.ndarray
        The band-pass filtered signal in the time domain.

    Notes
    -----
    This function requires pre-filtered signals using low-pass filters.
    """

    # Convert time series and low-pass filtered signals to frequency domain
    fourier_orig = np.fft.fft(original)
    fourier_low_high = np.fft.fft(low_filtered_all_highfreq)
    fourier_low_low = np.fft.fft(low_filtered_all_lowfreq)

    # Create the band-pass filter in the frequency domain
    RL1 = fourier_low_high / fourier_orig
    RL2 = fourier_low_low / fourier_orig
    RB = RL1 - RL2

    # Convert the band-pass filtered signal back to time domain
    band_filtered = np.real(np.fft.ifft(RB))
    return band_filtered


def band_pass3(original: np.ndarray, low_filtered_all: np.ndarray, high_filtered_all: np.ndarray) -> np.ndarray:
    """
    Band-pass filter, method 3.

    This filter combines a high-pass filter and a low-pass filter to create
    a band-pass filter. The signal is processed in the frequency domain and
    then converted back to the time domain.

    Parameters
    ----------
    original : np.ndarray
        The original time series data to be filtered.
    low_filtered_all : np.ndarray
        The result of applying a low-pass filter.
    high_filtered_all : np.ndarray
        The result of applying a high-pass filter.

    Returns
    -------
    band_filtered : np.ndarray
        The band-pass filtered signal in the time domain.

    Notes
    -----
    This function works entirely in the frequency domain. Do not manipulate
    the time-domain signal directly.
    """

    # Convert time series and filtered signals to frequency domain
    fourier_orig = np.fft.fft(original)
    fourier_low = np.fft.fft(low_filtered_all)
    fourier_high = np.fft.fft(high_filtered_all)

    # Create the band-pass filter by combining the high-pass and low-pass filters
    RL = fourier_low / fourier_orig
    RH = fourier_high / fourier_orig
    RB = RH * RL

    # Convert the band-pass filtered signal back to time domain
    band_filtered = np.real(np.fft.ifft(RB))
    return band_filtered


#--------------------------#
# Parameters and constants #
#--------------------------#

SIGNAL_FORCING_METHODS = ["classic", "sklearn", "zca"]
UNSUPPORTED_OPTION_ERROR_TEMPLATE = "Unsupported {}. Choose one from {}."