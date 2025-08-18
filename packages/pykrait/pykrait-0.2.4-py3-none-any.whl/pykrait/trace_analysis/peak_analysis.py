from scipy.signal import find_peaks as scipy_find_peaks
import numpy as np

def find_peaks(peak_min_width:int, peak_max_width:int, peak_prominence:float, peak_min_height:float, detrended_timeseries:np.ndarray) -> np.ndarray:
    """wrapper function for scipy's find_peaks function
    
    :param peak_min_width: minimum width at half-maximum of peak in frames
    :type peak_min_width: int
    :param peak_max_width: maximum width at half-maxumim of peak in frames
    :type peak_max_width: int
    :param peak_prominence: minimum prominence of peak
    :type peak_prominence: float
    :param min_peak_height: minimum height of peak
    :type min_peak_height: float
    :param timeseries: the timeseries to find the peaks on
    :type timeseries: ndarray

    :return: returns a (T x n_roi) np.ndarray with 1s at the peak locations and 0s elsewhere
    :rtype: np.ndarray
    """
    
    peak_series = np.zeros(detrended_timeseries.shape)

    for i in range(0, detrended_timeseries.shape[1]):
        peaks, _ = scipy_find_peaks(detrended_timeseries[:,i], width = (peak_min_width, peak_max_width), height=peak_min_height, prominence = peak_prominence)
        peak_series[peaks,i] = 1

    return peak_series

def calculate_normalized_peaks(peaks:np.ndarray, frame_interval:float) -> float:
    """
    calculates the normalized peaks (peaks per 100 cells per 10 minutes)

    :param peaks: binary array of shape (T x n_cells) with 1s at the peak locations and 0s elsewhere
    :type peaks: np.ndarray
    :param frame_interval: frame interval in seconds
    :type frame_interval: float
    :return: normalized peaks per 100 cells per 10 minutes
    :rtype: float
    """    
    n_frames, n_cells = peaks.shape
    n_peaks = np.sum(peaks)
    normalized_peaks = (n_peaks / (n_cells / 100)) / ((n_frames * frame_interval) / 600) # normalize to 100 cells and 10 minutes of recording

    return normalized_peaks
