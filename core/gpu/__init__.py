"""
GPU-accelerated image processing module using tinygrad.

This module provides production-quality implementations of microscopy
image analysis algorithms optimized for GPU execution via tinygrad.
Supports both CUDA and Metal backends.
"""

from .kernels import (
    gaussian_blur_3d,
    sobel_3d,
    otsu_threshold,
    connected_components_3d,
    rolling_ball_background,
)
from .segmentation import (
    watershed_segmentation_3d,
    blob_detection_3d,
    threshold_segmentation,
    UNet3D,
)
from .analysis import (
    colocalization_analysis,
    intensity_statistics,
    object_measurements,
    z_profile_analysis,
)
from .deconvolution import (
    richardson_lucy_deconvolution,
    wiener_deconvolution,
    generate_psf,
)
from .device_manager import DeviceManager

__all__ = [
    # Kernels
    "gaussian_blur_3d",
    "sobel_3d",
    "otsu_threshold",
    "connected_components_3d",
    "rolling_ball_background",
    # Segmentation
    "watershed_segmentation_3d",
    "blob_detection_3d",
    "threshold_segmentation",
    "UNet3D",
    # Analysis
    "colocalization_analysis",
    "intensity_statistics",
    "object_measurements",
    "z_profile_analysis",
    # Deconvolution
    "richardson_lucy_deconvolution",
    "wiener_deconvolution",
    "generate_psf",
    # Device management
    "DeviceManager",
]
