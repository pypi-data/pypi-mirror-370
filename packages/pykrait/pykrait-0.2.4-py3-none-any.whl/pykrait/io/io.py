import os
import dask.array as da
import numpy as np
import pandas as pd
import warnings
import re
from importlib.metadata import version
from typing import List
from bioio import BioImage
import bioio_tifffile

ALLOWED_IMAGE_EXTENSIONS =[".czi", ".tif", ".tiff"]

def load_timelapse_lazy(
    file_path: str,
) -> list[da.Array, float, float, float]:
    """Load a timelapse image file lazily using AICSImageIO, returning a Dask array of the image data along with the frame interval and pixel sizes.

    Currently supports CZI and TIF/TIFF files. The image data is returned as a Dask array with shape (T, C, Y, X) where T is time, C is channels, Y is height, and X is width. The Z dimension is dropped if it has only one slice.

    :param file_path: input file path to the timelapse image file
    :type file_path: str
    :raises TypeError: if filepath is not a string
    :raises FileNotFoundError: if the file does not exist
    :raises ValueError: if the extension is not supported
    :raises ValueError: if the image does not have the expected 5D shape (TCZYX)
    :raises ValueError: if the image has more than one Z slice and Z cannot be automatically dropped
    :return: returns a list of a Dask array containing the image data, the frame interval in seconds, and pixel sizes in micrometers (Y, X)
    :rtype: list[da.Array, float, float, float]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = os.path.splitext(file_path)[-1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(f"Image to load has the unsupported file format '{ext}'. Supported file formats are: {ALLOWED_IMAGE_EXTENSIONS}")

    # Load with BioImage using Dask
    if ext == ".czi":
        print("Using bioio_czi with aicspylibczi as backend to read")
        img = BioImage(file_path, reconstruct_mosaic=False, use_aicspylibczi=True)
    elif ext in [".tif", ".tiff"]:
        print("Using bioio_tifffile.Reader to read")
        img = BioImage(file_path, reconstruct_mosaic=False, reader=bioio_tifffile.Reader)
    # extract the relevant metadata
    pixel_sizes = img.physical_pixel_sizes  # Units are in micrometers (µm)
    y_um = round(pixel_sizes.Y, 2) if pixel_sizes else None
    x_um = round(pixel_sizes.X, 2) if pixel_sizes else None

    frame_interval = None

    # accessing frame interval from tif/tiff meadata
    if ext == ".tiff" or ext == ".tif":
        try:
                match = re.search(r"finterval=([0-9.]+)", img.metadata)
                raw_finterval = float(match.group(1))
                frame_interval = round(raw_finterval, 2) # Output: 1.26
        except Exception as e:
            warnings.warn(
                f"Failed to extract frame interval from metadata: {type(e).__name__}: {e}", 
                UserWarning
            )
    elif ext == ".czi":
        try:
            frame_interval = img.time_interval.total_seconds()
        except Exception as e:
            warnings.warn(
                f"Failed to extract frame interval from metadata: {type(e).__name__}: {e}", 
                UserWarning
            )
    dask_img = img.dask_data  # TCZYX

    if dask_img.ndim != 5:
        raise ValueError(f"Expected 5D image (TCZYX), but got shape {dask_img.shape}")

    T, C, Z, Y, X = dask_img.shape

    if T > 1 and Z == 1:
        dask_img = dask_img[:, :, 0, :, :]  # shape: (T, C, Z, Y, X)
    elif len([dim for dim in dask_img.shape if dim != 1]) == 3: #
        print("Image has three non-singleton dimensions, presuming order is (T, Y, X).")
        dask_img = _reorder_dask_array(dask_img)  # reorder to (T, C, Y, X)
        dask_img = dask_img[:, :, 0, :, :]  # shape: (T, C, Z, Y, X)
    else:
        raise ValueError(f"Cannot drop Z dimension automatically: Z={Z}. Consider handling it explicitly. Image shape: {dask_img.shape}")


    print(f"Returning lazy array of shape {dask_img.shape} (T, C, Y, X)")
    return dask_img, frame_interval, y_um, x_um

def get_files_from_folder(
    folder: str,
    extension: str = ".czi",
) -> list[str]:
    """returns all files from a folder with specified extensions.

    :param folder: path to the folder
    :type folder: str
    :param extensions: str of file extension (default is ".czi")
    :type extensions: str
    :return: list of file paths with the specified extensions
    :rtype: list[str]
    """
    if not os.path.isdir(folder):
        raise NotADirectoryError(f"Provided path is not a directory: {folder}")

    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and os.path.splitext(f)[-1].lower() == extension]
    return files

def get_pykrait_version() -> str:
    """returns the current version of pykrait."""
    try:
        __version__ = version("pykrait")
        return __version__
    except Exception as e:
        print(f"Could not retrieve pykrait version: {e}")
        return None  # Default version if not found

def _reorder_dask_array(
    dask_img: da.Array,
) -> da.Array:
    """Reorders a Dask array to the specified order.

    :param dask_array: input Dask array
    :type dask_array: da.Array
    :return: reordered Dask array
    :rtype: da.Array
    """
    shape = dask_img.shape
    non_1_axes = [i for i, dim in enumerate(shape) if dim != 1]

    if len(non_1_axes) < 3:
        raise ValueError(f"Expected at least 3 non-1 dimensions in {shape}")

    # Identify T, Y, X from non-1 dimensions
    non1_indices = [i for i, d in enumerate(dask_img.shape) if d != 1]

    T_axis = non1_indices[0]  # First non-singleton = T
    Y_axis = non1_indices[-2] # Second last non-singleton = Y
    X_axis = non1_indices[-1] # Last non-singleton = X

    # Fill in dummy axes for C and Z
    all_axes = list(range(5))
    used_axes = {T_axis, Y_axis, X_axis}
    unused_axes = [a for a in all_axes if a not in used_axes]

    # Fix order to (T, C, Z, Y, X)
    axis_map = {
        'T': T_axis,
        'C': unused_axes[0],
        'Z': unused_axes[1],
        'Y': Y_axis,
        'X': X_axis
    }

    perm = [axis_map[k] for k in ['T', 'C', 'Z', 'Y', 'X']]

    return dask_img.transpose(*perm)

def read_label_image(
    file_path: str,
) -> np.ndarray:
    """Reads a label image from a file and returns it as a Dask array.

    :param file_path: path to the label image file
    :type file_path: str
    :return: Dask array of the label image
    :rtype: da.Array
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        img = BioImage(file_path, reconstruct_mosaic=True).dask_data.compute()
        return img[0,0,0,:,:]  # Assuming the label image is single-channel, return as (Y, X)
    except Exception as e:
        raise ValueError(f"Failed to read label image from {file_path}: {type(e).__name__}: {e}")
        return None

def save_Txnrois(array:np.ndarray, frame_interval: float, filepath:str) -> None:
    """
    Saves a T x n_roi array to a CSV file with a header to denote the ROIs and a time index

    :param array: T x n_roi array to save
    :type array: np.ndarray
    :param filename: name of the output file
    :type filename: str
    :param frame_interval: frame interval in seconds
    :type frame_interval: float
    """
    if not isinstance(array, np.ndarray):
        raise TypeError("Input must be a numpy ndarray")
    
    if array.ndim != 2:
        raise ValueError("Input array must be 2D (T x n_roi)")

    n_frames, n_rois = array.shape
    timepoints = np.round((np.arange(n_frames) * frame_interval), 2)
    columns = [f"ROI_{i}" for i in range(n_rois)]

    df = pd.DataFrame(array, columns=columns, index=timepoints)
    df.index.name = "Time (s)"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=True, compression="zstd")

def read_Txnrois(filepath: str, n_frames:int=None, n_rois:int=None) -> np.ndarray:
    """
    loads a T x n_roi array to a CSV file with a header to denote the ROIs and a time index

    :param filepath: path to the CSV file
    :type filepath: str
    :param n_frames: number of frames in the timelapse
    :type n_frames: int
    :return: numpy array of shape (n_frames, n_rois)
    :rtype: np.ndarray
    """
    df = pd.read_csv(filepath, index_col=0)

    if n_frames is not None and df.shape[0] != n_frames:
        raise ValueError(f"Expected {n_frames} frames, but got {df.shape[0]} in {filepath}")
    if n_rois is not None and df.shape[1] != n_rois:
        raise ValueError(f"Expected {n_rois} ROIs, but got {df.shape[1]} in {filepath}")
    
    return df.to_numpy()

def save_NroisxF(array:np.ndarray, filepath:str, header:List[str]=None, ) -> None:
    """
    Saves a Nrois x F array to a CSV file with an index to denote the ROIs and a header for the features
    :param array: T x n_roi array to save
    :type array: np.ndarray
    :param filename: name of the output file
    :type filename: str
    :param frame_interval: frame interval in seconds
    :type frame_interval: float
    """
    if not isinstance(array, np.ndarray):
        raise TypeError("Input must be a numpy ndarray")
    if len(header) != array.shape[1]:
        raise ValueError("Header length must match the number of columns in the array")
    df = pd.DataFrame(array, columns=header)
    df.index.name = "ROIs"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=True, compression="zstd")

    
