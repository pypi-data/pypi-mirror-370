"""
Module: cryoblob
---------------------------

JAX based, JIT compiled, scalable codes for
detection of amorphous blobs in low SNR cryo-EM
images.

Submodules
----------
- `adapt`:
    Adaptive image processing methods that take
    advantage of JAX's automatic differentiation capabilities.
    The functions are:
    - `adaptive_wiener`:
        Adaptive Wiener filter that optimizes the noise estimate using gradient descent.
    - `adaptive_threshold`:
        Adaptively optimizes thresholding parameters using gradient descent
        to produce a differentiably thresholded image.

- `blobs`:
    Contains the core blob detection algorithms.
    The functions are:
    - `find_connected_components`:
        Pure JAX implementation of 3D connected components labeling.
    - `center_of_mass_3d`:
        Calculate center of mass for each labeled region in a 3D image.
    - `find_particle_coords`:
        Find particle coordinates using connected components and center of mass.
    - `preprocessing`:
        Pre-processes low SNR images to improve contrast of blobs.
    - `blob_list_log`:
        Detects blobs in an input image using the Laplacian of Gaussian (LoG) method.

- `files`:
    Interfacing with data files.
    The functions are:
    - `file_params`:
        Get the parameters for the file organization.
    - `load_mrc`:
        Reads an MRC-format cryo-EM file, extracting image data and metadata.
    - `process_single_file`:
        Process a single file for blob detection with memory optimization.
    - `process_batch_of_files`:
        Process a batch of files in parallel with memory optimization.
    - `folder_blobs`:
        Process a folder of images for blob detection with memory optimization.
    - `estimate_batch_size`:
        Estimate optimal batch size for processing MRC files based on available memory.
    - `estimate_memory_usage`:
        Estimate memory usage in GB for processing a single MRC file.
    - `get_optimal_batch_size`:
        Get optimal batch size by sampling multiple files from the list.

- `image`:
    Utility functions for image processing.
    The functions are:
    - `image_resizer`:
        Resize an image using a fast resizing algorithm implemented in JAX.
    - `resize_x`:
        Resize image along y-axis by independently resampling each column.
    - `gaussian_kernel`:
        Create a normalized 2D Gaussian kernel.
    - `apply_gaussian_blur`:
        Apply Gaussian blur to an image using convolution in JAX.
    - `difference_of_gaussians`:
        Applies Difference of Gaussians (DoG) filtering to enhance circular blobs.
    - `laplacian_of_gaussian`:
        Applies Laplacian of Gaussian (LoG) filtering to an input image.
    - `laplacian_kernel`:
        Create a Laplacian kernel for edge detection in a JAX-compatible manner.
    - `exponential_kernel`:
        Create an exponential kernel for image processing.
    - `perona_malik`:
        Perform edge-preserving denoising using the Perona-Malik anisotropic diffusion.
    - `histogram`:
        Calculate the histogram of an image.
    - `equalize_hist`:
        Perform histogram equalization on an image using JAX.
    - `equalize_adapthist`:
        Perform adaptive histogram equalization on an image using JAX.
    - `wiener`:
        Perform Wiener filtering on an image using JAX.

- `multi`:
    Multi-method blob detection for elongated objects and overlapping blobs.
    The functions are:
    - `hessian_matrix_2d`:
        Compute Hessian matrix components for 2D image at given scale.
    - `determinant_of_hessian`:
        Compute Determinant of Hessian for blob detection with better boundary detection.
    - `ridge_detection`:
        Detect elongated objects using ridge detection with eigenvalue analysis.
    - `multi_scale_ridge_detector`:
        Multi-scale ridge detection for various elongated object sizes.
    - `distance_transform_euclidean`:
        Compute Euclidean distance transform for watershed marker generation.
    - `watershed_segmentation`:
        Segment overlapping blobs using marker-based watershed algorithm.
    - `adaptive_marker_generation`:
        Generate watershed markers using distance transform and local maxima.
    - `hessian_blob_detection`:
        Detect blobs using Determinant of Hessian for better boundary detection.
    - `enhanced_blob_detection`:
        Combined approach using Hessian, ridge detection, and watershed segmentation.

- `plots`:
    Plotting functions for visualizing MRC images
    and blob detection results.
    The functions are:
    - `plot_mrc`:
        Plot an MRC image using Matplotlib with an optional scaling mode and scalebar.

- `types`:
    Type aliases and PyTrees.
    The types are:
    - `scalar_float`:
        Zero dimensional floating point number
    - `scalar_int`:
        Zero dimensional integer.
    - `scalar_num`:
        Zero dimensional number, that can either be a
        floating point number or an integer.
    - `non_jax_number`:
        A number that is not a JAX array. This is because
        even single number are stored as 0D JAX arrays.
    The PyTrees are:
    - `MRC_Image`:
        A PyTree structure for MRC images.
        Contains the image data and metadata.
    The factory functions are:
    - `make_MRC_Image`:
        Factory function to create an MRC_Image instance.

- `valid`:
    Pydantic models for data validation and configuration management.
    The classes are:
    - `PreprocessingConfig`:
        Configuration for image preprocessing parameters
    - `BlobDetectionConfig`:
        Configuration for blob detection parameters
    - `FileProcessingConfig`:
        Configuration for file processing and batch operations
    - `MRCMetadata`:
        Validation for MRC file metadata
    - `ValidationPipeline`:
        Main pipeline class for validating all configurations
    - `RidgeDetectionConfig`:
        Configuration for ridge detection parameters
    - `WatershedConfig`:
        Configuration for watershed segmentation parameters
    - `EnhancedBlobDetectionConfig`:
        Configuration for enhanced multi-method blob detection
    - `HessianBlobConfig`:
        Configuration for Hessian-based blob detection

"""

from .adapt import adaptive_wiener, adaptive_threshold
from .blobs import (
    find_connected_components,
    center_of_mass_3d,
    find_particle_coords,
    preprocessing,
    blob_list_log,
)
from .files import (
    file_params,
    load_mrc,
    process_single_file,
    process_batch_of_files,
    folder_blobs,
    estimate_batch_size,
    estimate_memory_usage,
    get_optimal_batch_size,
)
from .image import (
    image_resizer,
    resize_x,
    gaussian_kernel,
    apply_gaussian_blur,
    difference_of_gaussians,
    laplacian_of_gaussian,
    laplacian_kernel,
    exponential_kernel,
    perona_malik,
    histogram,
    equalize_hist,
    equalize_adapthist,
    wiener,
)
from .multi import (
    hessian_matrix_2d,
    determinant_of_hessian,
    ridge_detection,
    multi_scale_ridge_detector,
    distance_transform_euclidean,
    watershed_segmentation,
    adaptive_marker_generation,
    hessian_blob_detection,
    enhanced_blob_detection,
)
from .plots import plot_mrc
from .types import scalar_float, scalar_int, scalar_num, non_jax_number, MRC_Image
from .valid import (
    PreprocessingConfig,
    BlobDetectionConfig,
    FileProcessingConfig,
    MRCMetadata,
    ValidationPipeline,
    RidgeDetectionConfig,
    WatershedConfig,
    EnhancedBlobDetectionConfig,
    HessianBlobConfig,
)

__all__: list[str] = [
    "adaptive_wiener",
    "adaptive_threshold",
    "find_connected_components",
    "center_of_mass_3d",
    "find_particle_coords",
    "preprocessing",
    "blob_list_log",
    "file_params",
    "load_mrc",
    "process_single_file",
    "process_batch_of_files",
    "folder_blobs",
    "estimate_batch_size",
    "estimate_memory_usage",
    "get_optimal_batch_size",
    "image_resizer",
    "resize_x",
    "gaussian_kernel",
    "apply_gaussian_blur",
    "difference_of_gaussians",
    "laplacian_of_gaussian",
    "laplacian_kernel",
    "exponential_kernel",
    "perona_malik",
    "histogram",
    "equalize_hist",
    "equalize_adapthist",
    "wiener",
    "hessian_matrix_2d",
    "determinant_of_hessian",
    "ridge_detection",
    "multi_scale_ridge_detector",
    "distance_transform_euclidean",
    "watershed_segmentation",
    "adaptive_marker_generation",
    "hessian_blob_detection",
    "enhanced_blob_detection",
    "plot_mrc",
    "scalar_float",
    "scalar_int",
    "scalar_num",
    "non_jax_number",
    "MRC_Image",
    "PreprocessingConfig",
    "BlobDetectionConfig",
    "FileProcessingConfig",
    "MRCMetadata",
    "ValidationPipeline",
    "RidgeDetectionConfig",
    "WatershedConfig",
    "EnhancedBlobDetectionConfig",
    "HessianBlobConfig",
]
