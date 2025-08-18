import dask.array as da
import numpy as np
import warnings
import os
from cellpose import models
from tqdm.dask import TqdmCallback
from typing import Literal
from skimage import exposure

def _scale_to_uint16(arr: np.ndarray) -> np.ndarray:
    """Wraps skimage's rescale_intensity to convert an array to 16-bit unsigned integer format.

    :param arr: input array
    :type arr: np.ndarray
    :return: returns the input array scaled to 16-bit unsigned integer format.
    :rtype: np.ndarray
    """
    return exposure.rescale_intensity(arr, out_range='uint16').astype(np.uint16)

def _fast_time_sum(timelapse: da.Array) -> np.ndarray:
    T, C, Y, X = timelapse.shape

    # Rechunk T so blocks are as large as memory allows
    rechunked = timelapse.rechunk({0: "auto"})

    # Reduce each T-chunk to (1, C, Y, X)
    partial_sums = rechunked.map_blocks(
        lambda block: block.sum(axis=0, keepdims=True),
        dtype=timelapse.dtype,
        chunks=(1, C, Y, X)
    )

    # Sum across all (1, C, Y, X) blocks
    final_sum = partial_sums.sum(axis=0)

    return final_sum

def _fast_time_std(timelapse: da.Array) -> np.ndarray:
    """
    Efficiently computes standard deviation over the time axis (axis=0) of a T,C,Y,X dask array.
    Uses Dask-native operations for parallel execution and memory efficiency.
    
    :param timelapse: Dask array with shape (T, C, Y, X)
    :return: Dask array of shape (C, Y, X) with std computed over T
    """
    T, C, Y, X = timelapse.shape

    # Rechunk T to optimize chunk sizes
    rechunked = timelapse.rechunk({0: "auto"})

    # First pass: compute mean per block and total sum
    partial_sums = rechunked.map_blocks(
        lambda block: block.sum(axis=0, keepdims=True),
        dtype=timelapse.dtype,
        chunks=(1, C, Y, X)
    )
    total_sum = partial_sums.sum(axis=0)
    mean = total_sum / T

    # Second pass: compute squared differences from mean per block
    def squared_diff_block(block, mean):
        return ((block - mean) ** 2).sum(axis=0, keepdims=True)

    # Broadcast mean to match chunk shapes
    partial_squared_diffs = rechunked.map_blocks(
        squared_diff_block,
        mean,
        dtype=timelapse.dtype,
        chunks=(1, C, Y, X)
    )

    # Sum all squared diffs and divide by T (or T-1 for sample std)
    total_squared_diff = partial_squared_diffs.sum(axis=0)
    std = da.sqrt(total_squared_diff / T)

    return std

def timelapse_projection(lazy_timelapse: da.array, normalize:bool=True, method: Literal["std", "sum"] = "std", verbose: bool = True) -> np.ndarray:
    """
    Computes a T-projection of a timelapse to be used for cell segmentation. 

    :param lazy_timelapse: 4D dask array representing the timelapse, with shape order "TCYX".
    :type lazy_timelapse: da.array
    :param normalize: If True, applies CLAHE normalization.
    :type normalize: bool, optional
    :param method: method to be used for the projection, either "std" or "sum" for sum, defaults to "std"
    :type method: Literal["std", "sum"], optional, optional
    :param verbose: whether to output progress bar, defaults to True
    :type verbose: bool, optional
    :raises TypeError: if input is not a dask array
    :raises ValueError: if input does not have 4 dimensions
    :raises ValueError: if unknown T-proj method
    :return: 3D "CYX" numpy array containing the standard deviation for each pixel across all frames in 16-bit.
    :rtype: np.ndarray
    """    

    # Check if the input is a 4D dask array
    if not isinstance(lazy_timelapse, da.Array):
        raise TypeError("Input must be a dask array.")

    if lazy_timelapse.ndim != 4:
        raise ValueError("Input timelapse must be a 4D array with shape TCYX.")
    
    T, C, Y, X = lazy_timelapse.shape
    if T < C or T > Y or T > X or C > Y or C > X:
        warnings.warn(f"Input array shape of {lazy_timelapse.shape} is unusual. Is it in TCYX order?", UserWarning)
    
    #lazy_timelapse = lazy_timelapse.rechunk({0: -1, 2: "auto", 3: "auto"})
    if method == "std":
        if verbose:
            with TqdmCallback(desc="Computing STD projection"):
                t_proj = _fast_time_std(lazy_timelapse).compute(scheduler='threads')
        else:
            t_proj = _fast_time_std(lazy_timelapse).compute(scheduler='threads')
        t_proj = np.nan_to_num(t_proj, nan=0.0)  # Replace NaNs with 0
        t_proj = _scale_to_uint16(t_proj)  # Scale to uint16
    elif method == "sum":
        if verbose:
            with TqdmCallback(desc="Computing SUM projection"):
                t_proj = _fast_time_sum(lazy_timelapse).compute(scheduler='threads')
        else:
            t_proj = _fast_time_sum(lazy_timelapse).compute(scheduler='threads')
    else:
        raise ValueError("T-Projection Method must be either 'std' or 'sum'.")

    if normalize:
        # Enhance contrast per channel (C, Y, X)
        enhanced = np.empty_like(t_proj)
        for c in range(t_proj.shape[0]):
            enhanced[c] = _scale_to_uint16(exposure.equalize_adapthist(t_proj[c]))
    else:
        enhanced = _scale_to_uint16(t_proj)

    return enhanced

def create_cellpose_segmentation(image:np.ndarray, cellpose_model_path:str) -> np.ndarray:
    """
    Wrapper function to create a label image from an input image using a prespecified cellpose model.
    
    :param image: image to be processed with cellpose.
    :type image: ndarray
    :param cellpose_model_path: path to the cellpose model file. Can also be cpsam if using cellpose-4 and the standard builtin model.
    :type cellpose_model_path: str

    :return label_img: The generated label image.
    :rtype: np.ndarray
    
    :raises FileNotFoundError: If the Cellpose model path does not exist.
    :raises ValueError: If the input std image is not a 2D array.
    :raises RuntimeError: If the Cellpose model fails to load with both GPU and CPU backends.
    """

    # check if the model path exists
    if cellpose_model_path != "cpsam" and not os.path.isfile(cellpose_model_path):
        raise FileNotFoundError("Cellpose model not found at {}".format(cellpose_model_path))
    #TODO: check if the model was trained using the same cellpose version

    if image.ndim > 3:
        raise ValueError("Input image must be a 2D (YX) or 3D (CYX) array but got shape {}".format(image.shape))
    
    # setting up the cellpose segmentation, trying GPU first and falling back to CPU if it fails
    try:
        model = models.CellposeModel(gpu=True, pretrained_model = cellpose_model_path)
    except Exception as e:
        print(f"Error loading Cellpose model wiht GPU backend due to: {e}")
        try:
            model = models.CellposeModel(gpu=False, pretrained_model=cellpose_model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load Cellpose model with CPU backend due to: {e}")
        
    mask, _, _ = model.eval(image)

    if np.max(mask) == 0:
        warnings.warn("The generated mask contains only zeros. No cells were detected.", UserWarning)

    return mask