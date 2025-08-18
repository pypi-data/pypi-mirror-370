import numpy as np
import pandas as pd
import warnings
import dask.array as da
from dask import delayed, compute
from tqdm.dask import TqdmCallback
from scipy.sparse.csgraph import floyd_warshall
from scipy.spatial import KDTree
from scipy.sparse import lil_matrix
from functools import lru_cache
from skimage.measure import regionprops_table, regionprops
from skimage.segmentation import find_boundaries
from scipy.spatial.distance import cdist

def _legacy_extract_mean_intensities(numpy_timelapse:np.ndarray, masks:np.ndarray) -> np.ndarray:
    """
    This function computes the mean intensity of each cell across all frames in a timelapse, given a label image that identifies 
    the regions. It returns a 2D numpy array where each row corresponds to a cell and each column corresponds to a frame, containing the
    mean intensity of each cell per frame. 

    Note: If the input timelapse has multiple channels, only the first channel (C=0) will be used for intensity calculations. 
    
    It expectes the 4D-numpy array with order "TCYX" to be fully loaded into memory. Loading the dataframe into memory and running this function takes more memory and longer than the lazy version.

    :param numpy_timelapse: A 4D-numpy array with order "TCYX", fully loaded into memory. 
    :type numpy_timelapse: np.ndarray
    :param masks: A 2D numpy array containing labels for each region as label image.
    :type masks: np.ndarray

    :return: a cell x time numpy ndarray containing the mean intensity of each cell per frame of shape (n_cells, T).
    :rtype: np.ndarray
    """
    if not isinstance(numpy_timelapse, np.ndarray):
        raise TypeError("Input must be a numpy array.")
    if numpy_timelapse.ndim != 4:
        raise ValueError("Input timelapse must be a 4D array with shape TCYX.")
    if masks.ndim != 2:
        raise ValueError("Masks must be a 2D array representing the label image.")
    if masks.shape[0] != numpy_timelapse.shape[2] or masks.shape[1] != numpy_timelapse.shape[3]:
        raise ValueError("Masks shape (Y,X: {}, {}) must match the spatial dimensions of the timelapse (Y,X: {}, {}).".format(
            masks.shape[0], masks.shape[1], numpy_timelapse.shape[2], numpy_timelapse.shape[3]))
    
    # check that the timelapse is in TCYX order
    T, C, Y, X = numpy_timelapse.shape
    if T < C or T > Y or T > X or C > Y or C > X:
        warnings.warn(f"Input array shape of {numpy_timelapse.shape} is unusual. Is it in TCYX order?", UserWarning)
    if C > 1:
        warnings.warn("Input timelapse has multiple channels. Only the first channel (C=0) will be used for intensity calculations.", UserWarning)
    
    video = numpy_timelapse[:,0,:,:].squeeze()  # Ensure it's 3D (T, Y, X)

    roi_properties = regionprops_table(label_image=masks,
                                       intensity_image=video.transpose(1,2,0),
                                       properties=("label", "intensity_mean"),
                                       separator=",")
    intensity_array = np.array(list(roi_properties.values())[1:])
    
    return intensity_array


def _compute_mean_for_frame(frame:np.ndarray, masks:np.array) -> np.ndarray:
    """Helper function to compute the mean intensity of each cell for a single frame.
    It uses regionprops_table from skimage.measure to compute the mean intensities.

    :param frame: A 4D dask array with order "TCYX", fully loaded into memory.
    :type frame: np.ndarray
    :param masks: The label image for the frame.
    :type masks: np.ndarray    

    :return: a numpy array containing the mean intensity of each cell for the specified timepoint.
    :rtype: np.ndarray
    """
    props = regionprops_table(label_image=masks, intensity_image=frame, properties=("label", "intensity_mean"))
    return np.array(props["intensity_mean"])


def extract_mean_intensities(dask_timelapse:da.Array, masks:np.ndarray, verbose:bool=True) -> np.ndarray:
    """
    This function computes the mean intensity of each cell across all frames in a timelapse, given a label image that identifies 
    the regions.

    Note: If the input timelapse has multiple channels, only the first channel (C=0) will be used for intensity calculations.  
    It uses dask to lazily compute the mean intensities for each ROI and timepoint and does not load the entire timelapse into memory.

    :param dask_timelapse: A 4D dask array with order "TCYX", fully loaded into memory.
    :type dask_timelapse: da.Array
    :param masks: A 2D numpy array containing labels for each region as label image.
    :type masks: np.ndarray
    :param verbose: if True, shows the progress bar for the computation.
    :type verbose: bool
    :raises TypeError: If the input is not a dask array.
    :raises ValueError: If the input timelapse is not a 4D array or if the masks do not match the spatial dimensions of the timelapse. 

    :return: a T x n_rois numpy array containing the mean intensity of each cell per frame
    :rtype: np.ndarray
    """
    if not isinstance(dask_timelapse, da.Array):
        raise TypeError("Input must be a dask array.")
    if dask_timelapse.ndim != 4:
        raise ValueError("Input timelapse must be a 4D array with shape TCYX and not shape {}.".format(dask_timelapse.shape))
    if masks.ndim != 2:
        raise ValueError("Masks must be a 2D array representing the label image and not shape {}.",format(masks.shape))
    if masks.shape[0] != dask_timelapse.shape[2] or masks.shape[1] != dask_timelapse.shape[3]:
        raise ValueError("Masks shape (Y,X: {}, {}) must match the spatial dimensions of the timelapse (Y,X: {}, {}).".format(
            masks.shape[0], masks.shape[1], dask_timelapse.shape[2], dask_timelapse.shape[3]))
    # check that the timelapse is in TCYX order
    T, C, Y, X = dask_timelapse.shape
    if T < C or T > Y or T > X or C > Y or C > X:
        warnings.warn(f"Input array shape of {dask_timelapse.shape} is unusual. Is it in TCYX order?", UserWarning)
    if C > 1:
        warnings.warn("Input timelapse has multiple channels. Only the first channel (C=0) will be used for intensity calculations.", UserWarning)

    dask_timelapse = dask_timelapse.rechunk({0: 1, 1: 1})
    n_rois = np.max(masks)

    dask_frames = dask_timelapse[:, 0, :, :]  # shape: (T, Y, X)

    def block_func(block):  # block has shape (1, Y, X)
        frame = block[0]  # shape (Y, X)
        means = _compute_mean_for_frame(frame, masks)  # shape (n_rois,)
        return means[np.newaxis, :]  # shape (1, n_rois)

    mean_dask = da.map_blocks(
        block_func,
        dask_frames,
        dtype=np.float32,
        chunks=(1, n_rois),   # Must match output shape per block
        drop_axis=(1, 2),     # Drop Y, X axes
        new_axis=1            # Add n_rois axis
    )

    if verbose:
        with TqdmCallback(desc="Computing mean intensities"):
            mean_intensities = mean_dask.compute(scheduler="threads")
    else:
        mean_intensities = mean_dask.compute(scheduler="threads")

    return mean_intensities  # shape: (T, n_rois)


def extract_cell_properties(masks:np.ndarray) -> tuple:
    """
    Returns cell properties (area, axis lengths, perimeter) and positions (centroid coordinates) of each cell in the label image.

    
    :param masks: input label image
    :type masks: np.ndarray

    :return cell_properties: pandas dataframe of cell properties
    :rtype cell_properties: pd.DataFrame
    :return cell_positions: (nd.array of size len(roi) x 2, np.uint16): pixel positions of every roi
    :rtype cell_positions: np.ndarray
    """

    cell_properties = regionprops_table(label_image=masks,
                                        intensity_image=masks,
                                        properties=("label", "centroid",
                                                    "intensity_max", "area", 
                                                    "axis_major_length", 
                                                    "axis_minor_length", 
                                                    "perimeter"),
                                        separator=",")
    # to get the 0-indexed index array of labels
    cell_indices = cell_properties['intensity_max'].astype(int) - 1

    cell_properties['label'] = cell_indices
    cell_properties = pd.DataFrame(cell_properties)

    ypos = cell_properties['centroid,0']
    xpos = cell_properties['centroid,1']

    # maximum pixel value of masks is number of labels/cells
    cell_positions = np.zeros((masks.max(), 2), dtype=np.uint16)
    cell_positions[:, 0] = xpos[cell_indices].astype(np.uint16)
    cell_positions[:, 1] = ypos[cell_indices].astype(np.uint16)

    return cell_properties, cell_positions


def _legacy_get_adjacency_matrix(masks: np.ndarray, neighbour_tolerance: int) -> tuple[np.ndarray, np.ndarray]:
    """Computes the adjacency matrix and shortest path matrix for the given mask with ROIs using pairwise distances between all boundary pixels.

    :param masks: _description_
    :type masks: np.ndarray
    :param neighbour_tolerance: _description_
    :type neighbour_tolerance: int
    :return: _description_
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    n_labels = masks.max()
    adjacency_matrix = np.zeros((n_labels, n_labels), dtype=np.uint8)

    props = regionprops(masks)
    all_boundary_pixels = []
    pixel_labels = []

    for region in props:
        label = region.label
        region_mask = (masks == label)
        boundary = find_boundaries(region_mask, mode="outer")
        coords = np.argwhere(boundary)
        all_boundary_pixels.append(coords)
        pixel_labels.extend([label - 1] * len(coords))

    if len(all_boundary_pixels) == 0:
        shortest_path_matrix = np.triu(floyd_warshall(adjacency_matrix), k=1)
        return adjacency_matrix, shortest_path_matrix

    all_boundary_pixels = np.vstack(all_boundary_pixels)
    pixel_labels = np.array(pixel_labels)

    tree = KDTree(all_boundary_pixels)
    pairs = tree.query_pairs(r=neighbour_tolerance)

    for idx1, idx2 in pairs:
        label1 = pixel_labels[idx1]
        label2 = pixel_labels[idx2]
        if label1 != label2:
            adjacency_matrix[label1, label2] = 1
            adjacency_matrix[label2, label1] = 1

    shortest_path_matrix = np.triu(floyd_warshall(adjacency_matrix), k=1)
    return adjacency_matrix, shortest_path_matrix


@lru_cache(maxsize=32)
def _generate_distance_kernel(neighbour_tolerance: int) -> np.ndarray:
    """Generates a circular distance kernel for the given neighbour tolerance to identify pixels within bounds

    :param neighbour_tolerance: integer defining the maximum distance between two pixels to be considered neighbours.
    :type neighbour_tolerance: int
    :return: returns a 2D numpy array of shape (2 * neighbour_tolerance + 1, 2 * neighbour_tolerance + 1) where each pixel is either 0 or 1, indicating whether the pixel is within the neighbour tolerance.
    :rtype: np.ndarray
    """
    size = 2 * neighbour_tolerance + 1
    coords = np.indices((size, size)).reshape(2, -1).T
    center = np.array([[neighbour_tolerance, neighbour_tolerance]])
    distances = cdist(center, coords).reshape(size, size)
    return (distances <= neighbour_tolerance).astype(np.uint8)


def _process_region(region, masks: np.ndarray, circular_kernel: np.ndarray, kernel_radius:int) -> list:
    """Helper function to process each region and find pairs of adjacent masks

    :param region: region object from skimage.measure.regionprops
    :type region: _type_
    :param masks: label image containing the ROIs for each cell
    :type masks: np.ndarray
    :param circular_kernel: kernel used to identify pixels within the neighbour tolerance
    :type circular_kernel: np.ndarray
    :param kernel_radius: _description_
    :type kernel_radius: int
    :return: returns a list of tuples, where each tuple contains the indices of two adjacent regions (i, j) such that i < j.
    :rtype: list
    """
    h, w = masks.shape
    label = region.label
    region_mask = masks == label
    boundary = find_boundaries(region_mask, mode='outer')
    ys, xs = np.argwhere(boundary).T

    found_pairs = set()

    for y, x in zip(ys, xs):
        y_start = max(0, y - kernel_radius)
        y_end = min(h, y + kernel_radius + 1)
        x_start = max(0, x - kernel_radius)
        x_end = min(w, x + kernel_radius + 1)

        patch = masks[y_start:y_end, x_start:x_end]

        ky_start = kernel_radius - (y - y_start)
        ky_end = ky_start + (y_end - y_start)
        kx_start = kernel_radius - (x - x_start)
        kx_end = kx_start + (x_end - x_start)

        mask_patch = circular_kernel[ky_start:ky_end, kx_start:kx_end]
        visible_labels = np.unique(patch[mask_patch > 0])

        for neighbor_label in visible_labels:
            if neighbor_label == 0 or neighbor_label == label:
                continue
            i, j = label - 1, neighbor_label - 1
            found_pairs.add((min(i, j), max(i, j)))  # Sort to avoid duplicates

    return list(found_pairs)


def get_adjacency_matrix(masks: np.ndarray, neighbour_tolerance: int, verbose: bool=True) -> tuple[np.ndarray, np.ndarray]:
    """Computes the adjacency matrix and shortest path matrix for ROIs within the neighbour_tolerance in the given mask.

    :param masks: 2D label image where the value of every ROI is equal to its index. A pixel value of 0 indicates the image background.
    :type masks: np.ndarray
    :param neighbour_tolerance: maximum distance between two ROIs to still be considered neighbours, in pixels.
    :type neighbour_tolerance: int
    :param verbose: if true, prints a progress bar for adjacency matrix construction, defaults to True
    :type verbose: bool, optional
    :return: returns a ROI x ROI adjacency matrix, where the element at (i, j) is 1 if ROI i and ROI j are neighbours, and 0 otherwise. Also returns a shortest path matrix, where the element at (i, j) is the length of the shortest path between ROI i and ROI j.
    :rtype: tuple[np.ndarray, np.ndarray]

    In benchmarking, this function is about 25x faster than the legacy version _legacy_get_adjacency_matrix, which uses cdist to compute the distances between all pairs of ROIs. However, they do not produce exactly the same adjacency matrix. 
    _legacy_get_adjacency_matrix identifies ca. 1.7% more pairs of adjacent ROIs than this function, which is likely due to edge cases around the kernel radius and the way boundaries are defined here.
    """
    n_labels = masks.max()
    kernel_radius = neighbour_tolerance
    circular_mask = _generate_distance_kernel(neighbour_tolerance)

    props = regionprops(masks)

    tasks = [
        delayed(_process_region)(region, masks, circular_mask, kernel_radius)
        for region in props
    ]

    # If verbose is True, use TqdmCallback to show progress
    if verbose:
        with TqdmCallback(desc="Computing adjacency matrix"):
            region_pairs = compute(*tasks)
    else:
        region_pairs = compute(*tasks)

    adjacency_matrix = lil_matrix((n_labels, n_labels), dtype=np.uint8)
    for pairs in region_pairs:
        for i, j in pairs:
            adjacency_matrix[i, j] = 1
            adjacency_matrix[j, i] = 1

    shortest_path_matrix = floyd_warshall(adjacency_matrix, directed=False, unweighted=True)
    return adjacency_matrix.toarray(), np.triu(shortest_path_matrix, k=1)