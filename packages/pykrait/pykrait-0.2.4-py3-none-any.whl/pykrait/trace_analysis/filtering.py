import numpy as np
from math import pi
from scipy.signal import fftconvolve
from scipy.ndimage import gaussian_filter1d

def _blackman_sinc_filter_kernel(kernel_window: int, cutoff_freq: float) -> list[float]:
    """Generates a Blackman windowed sinc filter kernel

    :param kernel_window: window size for the kernel, must be even
    :type kernel_window: int
    :param cutoff_freq: cut-off frequency, oscillations of lower frequencies will be blocked
    :type cutoff_freq: float
    :return: returns the filter kernel as a list of floats
    :rtype: list

    See the pyBOAT paper (https://www.biorxiv.org/content/10.1101/2020.04.29.067744v2) and Chapter 16 of the The Scientist and Engineer's Guide to Digital Signal Processing (https://www.dspguide.com/ch16/1.htm) for more details.
    """
    if kernel_window % 2 != 0:
        raise ValueError("Filter kernel window must be even")
    
    kernel = np.zeros(kernel_window + 1, dtype=float)
    midpoint = kernel_window / 2

    for n in range(kernel_window + 1):
        if n == midpoint:
            val = 2 * pi * cutoff_freq
        else:
            val = np.sin(2 * pi * cutoff_freq * (n - midpoint)) / (n - midpoint)
        # Apply Blackman window
        val *= (0.42 - 0.5 * np.cos(2 * pi * n / kernel_window) + 0.08 * np.cos(4 * pi * n / kernel_window))
        kernel[n] = val

    kernel /= np.sum(kernel)
    return kernel

def _convolve_signals_with_kernel(signals: np.ndarray, filter_kernel: list) -> np.ndarray:
    """Convolve a 2D array of signals with a filter kernel using FFT convolution. 

    :param signals: 2D numpy array of shape (T x n_rois)
    :type signals: np.ndarray
    :param filter_kernel: kernel to convolve with, must be odd length
    :type filter_kernel: list
    :raises ValueError: raises a ValueError if the filter kernel length is not odd
    :return: 2D numpy array of convolved signals in the shape (T x n_rois)
    :rtype: np.ndarray
    """
    kernel_length = len(filter_kernel)
    if kernel_length % 2 == 0:
        raise ValueError("Filter kernel length must be odd")

    # Convert to 1D array if needed
    filter_kernel = np.asarray(filter_kernel).flatten()

    # Pad signals along time axis (axis=0)
    left_padding = signals[kernel_length - 1:0:-1, :]
    right_padding = signals[-2:-kernel_length - 1:-1, :]
    padded_signals = np.concatenate([left_padding, signals, right_padding], axis=0)

    # Apply convolution along axis=0 (time)
    convolved = fftconvolve(padded_signals, filter_kernel[:, None], mode='valid', axes=0)

    # Extract center portion to match input shape
    start = (kernel_length - 1) // 2
    end = start + signals.shape[0]
    result = convolved[start:end, :]

    return result

def detrend_with_sinc_filter(
    signals: np.ndarray,
    cutoff_period: float,
    sampling_interval: float
) -> np.ndarray:
    """Applies a Blackman-windowd sinc filter to a 2D array of signals to detrend them. Frequencies lower than the cutoff frequency will be blocked, while higher frequencies will pass through unaffected. 
    
    See the pyBOAT paper (https://www.biorxiv.org/content/10.1101/2020.04.29.067744v2) and Chapter 16 of the The Scientist and Engineer's Guide to Digital Signal Processing (https://www.dspguide.com/ch16/1.htm) for more details.

    :param signals: 2D numpy array of shape (T x n_rois)
    :type signals: np.ndarray
    :param cutoff_period: cutoff period in [time units], lower frequencies will be blocked
    :type cutoff_period: float
    :param sampling_interval: sampling interval in [time units] of the signals
    :type sampling_interval: float
    :return: returns the detrended signals as a 2D numpy array of shape (T x n_rois)
    :rtype: np.ndarray
    """
    signal_length, _ = signals.shape

    kernel_window = signal_length - 1
    if kernel_window % 2 != 0:
        kernel_window -= 1  # Make kernel window even

    cutoff_frequency = sampling_interval / cutoff_period  # Cutoff freq in sampling units

    filter_kernel = _blackman_sinc_filter_kernel(kernel_window, cutoff_frequency)
    smoothed_signals = _convolve_signals_with_kernel(signals, filter_kernel)

    detrended_signals = signals - smoothed_signals
    return detrended_signals

def smooth_gauss(signal:np.ndarray, sigma:float) -> np.ndarray:
    """Applies a Gaussian smoothing filter to the 2D input signal.

    :param signal: 2D numpy array of shape (T x n_rois)
    :type signal: np.ndarray
    :param sigma: Standard deviation for the Gaussian kernel.
    :type sigma: float
    :return: The smoothed signal of shape (T x n_rois).
    :rtype: np.ndarray
    """
    if sigma <= 0:
        return signal

    return gaussian_filter1d(signal, sigma, axis=0)
