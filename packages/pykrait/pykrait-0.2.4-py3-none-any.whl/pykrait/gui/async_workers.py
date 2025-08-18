from PySide6.QtCore import QObject, Signal, Slot
import traceback
import numpy as np

from skimage.measure import find_contours

from pykrait.io.io import read_label_image, read_Txnrois
from pykrait.preprocessing.timeseries_extraction import extract_mean_intensities
from pykrait.trace_analysis.filtering import detrend_with_sinc_filter
from pykrait.trace_analysis.peak_analysis import find_peaks
from pykrait.pipeline.pipeline import AnalysisParameters, AnalysisOutput, create_analysis_folder, load_timelapse, create_masks, calculate_periodic_cells, save_analysis_results

def get_pixel_contour_from_label_img(label_img:np.ndarray, orig_shape:tuple, target_shape:tuple) -> list:
    """
    Generates pixel contours from a labeled image, scaled to a target shape.

    :param label_img: a label image where each pixel is labeled with an integer representing the ROI it belongs to
    :type label_img: np.ndarray
    :param orig_shape: original shape of the image (height, width)
    :type orig_shape: tuple
    :param target_shape: target shape to which the contours should be scaled (height, width)
    :type target_shape: tuple
    :return: returns a list of polygons representing the scaled contours of each ROI
    :rtype: list
    """ 
    roi_polygons = []
    orig_height, orig_width = orig_shape
    target_height, target_width = target_shape
    scale_y = target_height / orig_height
    scale_x = target_width / orig_width
    for index in range(1, label_img.max() + 1):  # skip background (0)
        contours = find_contours(label_img == index, 0.5)
        if contours:
            contour = contours[0]
            y, x = contour.T
            y, x = y * scale_y, x * scale_x # rescales coordinates to target shape
            polygon = list(zip(x, y))
            roi_polygons.append(polygon)
    return roi_polygons

class ExtractIntensitiesWorker(QObject):
    """
    Worker for extracting mean intensities from a timelapse dataset, using either Cellpose segmentation or a label image.
    """
    progress_changed = Signal(int, str)    # progress percent, status message
    finished = Signal(dict)                # analysis results
    error = Signal(str)                    # error message

    def __init__(self, analysis_params:AnalysisParameters, output_params:AnalysisOutput, mode:str, mean_intensities_path:str=None):
        super().__init__()
        self.analysis_parameters = analysis_params
        self.analysis_output = output_params
        self.mode = mode
        self.mean_intensities_path = mean_intensities_path

    @Slot()
    def run(self):
        try:
            
            self.analysis_output = create_analysis_folder(self.analysis_output)
            print(f"Running analysis on {self.analysis_output.filename}")
            # loading the timelapse data and analysing frame interval
            self.timelapse_data, self.analysis_output = load_timelapse(self.analysis_output, self.analysis_parameters)

            if self.mode == "cellpose":
                # perform the tproj
                self.progress_changed.emit(10, "Performing T Projection and Cellpose Segmentation...")
                # creating the masks and saving them to the analysis folder
                self.masks, self.analysis_output = create_masks(self.timelapse_data, self.analysis_output, self.analysis_parameters)
                # extracts the mean intensities of the masks
                self.progress_changed.emit(60, "Extracting intensities...") 
                mean_intensities = extract_mean_intensities(self.timelapse_data, self.masks)
            elif self.mode == "label_image":
                self.progress_changed.emit(20, "Loading label image...")
                self.masks = read_label_image(self.analysis_output.masks_path)
                # extracts the mean intensities of the masks
                self.progress_changed.emit(60, "Extracting intensities...") 
                mean_intensities = extract_mean_intensities(self.timelapse_data, self.masks)
            elif self.mode == "csv":
                self.progress_changed.emit(20, "Loading label image...")
                self.masks = read_label_image(self.analysis_output.masks_path)
                self.progress_changed.emit(60, "Reading intensities...") 
                mean_intensities = read_Txnrois(self.mean_intensities_path, n_frames=self.timelapse_data.shape[0], n_rois=self.masks.max())
            else:
                raise ValueError("Unknown mode.")

            self.analysis_output.number_of_frames, self.analysis_output.number_of_cells = mean_intensities.shape

            # All done
            self.progress_changed.emit(90, "Calculating ROI boundaries...")
            rois = get_pixel_contour_from_label_img(self.masks, orig_shape=self.masks.shape, target_shape=(512, 512))

            self.progress_changed.emit(100, "Done.")
            
            results = {
                'frames': self.timelapse_data,
                'analysis_output': self.analysis_output,
                'analysis_parameters': self.analysis_parameters,
                'masks': self.masks,
                'rois': rois,
                'mean_intensities': mean_intensities
            }
            self.finished.emit(results)

        except Exception as e:
            tb = traceback.format_exc()
            print(f"Error during analysis: {e}\n{tb}")
            self.error.emit(str(e))

class DetrendWorker(QObject):
    """
    _summary_

    :param QObject: _description_
    :type QObject: _type_
    """    
    finished = Signal(np.ndarray)
    error = Signal(Exception)

    def __init__(self, intensities, sinc_window, frame_interval):
        super().__init__()
        self.intensities = intensities
        self.sinc_window = sinc_window
        self.frame_interval = frame_interval

    def run(self):
        try:
            # Call your actual function here
            detrended = detrend_with_sinc_filter(signals=self.intensities, 
                                                 cutoff_period=self.sinc_window,
                                                 sampling_interval=self.frame_interval)
            self.finished.emit(detrended)
        except Exception as e:
            self.error.emit(e)

class PeakDetectionWorker(QObject):
    """
    Worker for detecting peaks in detrended traces, wraps the `find_peaks` function.
    """    
    finished = Signal(np.ndarray)
    error = Signal(Exception)

    def __init__(self, detrended_traces, min_width, max_width, prominence, min_height):
        super().__init__()
        self.traces = detrended_traces
        self.min_width = min_width
        self.max_width = max_width
        self.prominence = prominence
        self.min_height = min_height

    def run(self):
        try:
            peaks = find_peaks(
                peak_min_width=self.min_width,
                peak_max_width=self.max_width,
                peak_prominence=self.prominence,
                peak_min_height=self.min_height,
                detrended_timeseries=self.traces
            )
            self.finished.emit(peaks)
        except Exception as e:
            self.error.emit(e)

class PeriodicCellWorker(QObject):
    """
    Worker for finding oscillating ROIs in the peak series, wraps the `find_oscillating_rois` function.
    """
    finished = Signal(AnalysisOutput, np.ndarray, np.ndarray)
    error = Signal(Exception)

    def __init__(self, peaks: np.ndarray, analysis_params, analysis_output):
        super().__init__()
        self.peaks = peaks
        self.analysis_output = analysis_output
        self.analysis_params = analysis_params

    def run(self):
        try:
            periodicity_results, stds, covs = calculate_periodic_cells(self.peaks, self.analysis_params, self.analysis_output)
            self.finished.emit(periodicity_results, stds, covs)
        except Exception as e:
            self.error.emit(e)

class AnalysisSaveWorker(QObject):
    """
    Worker for saving the analysis results, wraps the `save_analysis_results` function.
    """
    finished = Signal(str)  # emit output file path or summary message
    error = Signal(Exception)

    def __init__(self, analysis_output, analysis_params, peaks: np.ndarray, detrended_intensities: np.ndarray, intensities: np.ndarray,
                stds: np.ndarray = None, covs: np.ndarray = None, overwrite: bool = False):
        super().__init__()
        self.analysis_output = analysis_output
        self.analysis_params = analysis_params
        self.peaks = peaks
        self.detrended_intensities = detrended_intensities
        self.intensities = intensities
        self.overwrite = overwrite
        self.stds = stds
        self.covs = covs

    def run(self):
        try:
            save_analysis_results(
                analysis_output=self.analysis_output,
                analysis_params=self.analysis_params,
                detrended_intensities=self.detrended_intensities,
                peaks=self.peaks,
                intensities=self.intensities,
                stds=self.stds,
                covs=self.covs,
                overwrite=self.overwrite
            )
            self.finished.emit(f"Saved to {self.analysis_output.analysis_folder}")

        except Exception as e:
            self.error.emit(e)