import numpy as np
from typing import Tuple
from scipy.stats import percentileofscore
from typing import Literal

def calculate_std_cov(peak_series: np.ndarray, frame_interval: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    calculates the standard deviation and coefficient of variation of the peak intervals for each ROI. If a cell has less than 4 peaks
    it will return NaN for the standard deviation and coefficient of variation.

    :param peak_series: peak series of shape (T, n_roi) where T is the number of time points and n_roi is the number of ROIs
    :type peak_series: np.ndarray
    :param frame_interval: frame interval of the recording in seconds
    :type frame_interval: float
    :return: returns the standard deviation and coefficient of variation of the peak intervals for each ROI
    :rtype: Tuple[np.ndarray, np.ndarray]
    """    
    peak_indices = [np.flatnonzero(col) for col in peak_series.T]
    peak_diff = [np.diff(indices) * frame_interval for indices in peak_indices]

    peak_std = []
    peak_cov = []

    for diffs in peak_diff:
        if len(diffs) < 4:  # <2 intervals → not enough to compute variability
            peak_std.append(np.nan)
            peak_cov.append(np.nan)
        else:
            std_val = np.std(diffs)
            mean_val = np.mean(diffs)
            peak_std.append(std_val)
            peak_cov.append(std_val / mean_val if mean_val != 0 else np.nan)

    return np.array(peak_std), np.array(peak_cov)


def get_random_std_covs(filtered_peak_series:np.ndarray, frame_interval:float, n_iter:int=100) -> Tuple[np.ndarray, np.ndarray]:
    """
    randomly shuffles the peak series across the time axis (individually per ROI) and returns n_iter times the random standard deviations and coefficients of variation.

    :param filtered_peak_series: (T x n_roi) binary array with 1s at the peak locations and 0s elsewhere, where n_roi are ROIs with at least 4 peaks
    :type filtered_peak_series: np.ndarray
    :param n_iter: number of iterations for random control
    :type n_iter: 100
    :param frame_interval: frame interval of the recording in seconds
    :type frame_interval: float
    :return: returns the standard deviation and coefficient of variation thresholds for the random control data
    :rtype: Tuple[np.ndarray, np.ndarray]
    """
    # for the random control, generate a stacked peak series
    stacked_peak_series = np.hstack([filtered_peak_series] * n_iter)
    
    # shuffle each column independently
    T, n = stacked_peak_series.shape
    idx = np.argsort(np.random.rand(T, n), axis=0)
    stacked_peak_series = np.take_along_axis(stacked_peak_series, idx, axis=0)

    # calculate std and cv for each column
    return calculate_std_cov(stacked_peak_series, frame_interval)

def find_oscillating_rois(periodicity_method: Literal['cutoff', 'quantile'], peak_series: np.ndarray, std_threshold: float, cov_threshold: float, frame_interval: float, n_iter: int = 100) -> Tuple[dict, np.ndarray, np.ndarray]:
    """
    Calculates the periodicity of the ROIs based on the peak series, using either a cutoff or quantile method.

    :param periodicity_method: whether to use "cutoff" or "quantile" method for periodicity detection
    :type periodicity_method: str, "cutoff" or "quantile"
    :param peak_series: T x nroi binary peak series, where 1s indicate peaks and 0s indicate no peaks
    :type peak_series: np.ndarray
    :param std_threshold: threshold for standard deviation (can be both a cutoff or a quantile depending on the periodicity_method)
    :type std_threshold: float
    :param cov_threshold: threshold for standard deviation (can be both a cutoff or a quantile depending on the periodicity_method)
    :type cov_threshold: float
    :param frame_interval: frame interval of the recording in seconds
    :type frame_interval: float
    :param n_iter: number of iterations for random data, defaults to 100
    :type n_iter: int, optional
    :return: returns a dictionary with the periodicity results, and the standard deviations and coefficients of variation for the experimental data
    :rtype: Tuple[dict, np.ndarray, np.ndarray]
    """    
    if not (0 <= cov_threshold <= 1):
        raise ValueError("cov_threshold must be between 0 and 1.")

    if periodicity_method == "cutoff":

        std_cutoff = std_threshold
        cov_cutoff = cov_threshold

        # generates a large random control dataset to calculate the quantiles
        random_stds_for_quantile, random_covs_for_quantile = get_random_std_covs(peak_series, frame_interval, n_iter=n_iter)
        random_stds_for_quantile = random_stds_for_quantile[~np.isnan(random_stds_for_quantile)]
        random_covs_for_quantile = random_covs_for_quantile[~np.isnan(random_covs_for_quantile)]

        std_quantile = percentileofscore(random_stds_for_quantile, std_threshold) / 100
        cov_quantile = percentileofscore(random_covs_for_quantile, cov_threshold) / 100

    elif periodicity_method == "quantile":
        if not (0 <= std_threshold <= 1):
            raise ValueError("std_threshold must be between 0 and 1.")

        std_quantile = std_threshold
        cov_quantile = cov_threshold

        # calculates a large random control dataset to calculate the cutoffs
        random_stds_for_quantile, random_covs_for_quantile = get_random_std_covs(peak_series, frame_interval, n_iter=n_iter) 
        # calculates the cutoff threshold that correspond to the quantile
        # nanquantile ignores NaN values, so can be used directly
        std_cutoff = np.nanquantile(random_stds_for_quantile, std_quantile)
        cov_cutoff = np.nanquantile(random_covs_for_quantile, cov_quantile)
    
        
    else:
        raise ValueError(f"Unknown periodicity method: {periodicity_method}, expected 'cutoff' or 'quantile'.")

    # calculate the distribution of standard deviations and coefficients of variation for the random control data
    experimental_stds, experimental_covs = calculate_std_cov(peak_series, frame_interval)
    random_stds, random_covs = get_random_std_covs(peak_series, frame_interval, n_iter=1)  

    periodicity_results = {
        "std_cutoff": std_cutoff,
        "std_quantile": std_quantile,
        "experimental_below_std": np.sum(experimental_stds <= std_cutoff), #calculates the number of ROIs below the threshold, inores NaN values so can be used directly
        "random_below_std": np.sum(random_stds <= std_cutoff),
        "cov_cutoff": cov_cutoff,
        "cov_quantile": cov_quantile,
        "experimental_below_cov": np.sum(experimental_covs <= cov_cutoff),
        "random_below_cov": np.sum(random_covs <= cov_cutoff),
    }

    return periodicity_results, experimental_stds, experimental_covs