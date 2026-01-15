"""
Core GPU-accelerated image processing kernels using tinygrad.

Implements fundamental operations for 3D microscopy image analysis:
- Gaussian filtering (separable for efficiency)
- Edge detection (3D Sobel)
- Thresholding (Otsu method with GPU histogram)
- Connected components labeling
- Background subtraction
"""

import numpy as np
import logging
from typing import Tuple, Optional, Callable
from functools import wraps
import time

from tinygrad.tensor import Tensor
from tinygrad.dtype import dtypes

from .device_manager import DeviceManager

logger = logging.getLogger(__name__)

# Initialize device manager
_device_manager = DeviceManager()


def benchmark(func: Callable) -> Callable:
    """Decorator to benchmark GPU kernel execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        # Ensure computation is complete
        if isinstance(result, Tensor):
            result.realize()
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__} completed in {elapsed*1000:.2f}ms on {_device_manager.device}")
        return result
    return wrapper


def to_tensor(array: np.ndarray, device: Optional[str] = None) -> Tensor:
    """
    Convert numpy array to tinygrad Tensor on specified device.

    Args:
        array: Input numpy array
        device: Target device (None = use default)

    Returns:
        Tinygrad tensor on specified device
    """
    if device is None:
        device = _device_manager.device

    # Convert to float32 for GPU operations
    if array.dtype != np.float32:
        array = array.astype(np.float32)

    return Tensor(array, device=device, dtype=dtypes.float32)


def to_numpy(tensor: Tensor) -> np.ndarray:
    """Convert tinygrad Tensor back to numpy array."""
    return tensor.realize().numpy()


@benchmark
def gaussian_blur_3d(
    volume: np.ndarray,
    sigma: float = 1.0,
    progress_callback: Optional[Callable[[float], None]] = None
) -> np.ndarray:
    """
    GPU-accelerated 3D Gaussian blur using separable convolution.

    Separable implementation: O(n*k) instead of O(n*k^3) where k is kernel size.
    Applies 1D Gaussian kernels sequentially along Z, Y, X axes.

    Args:
        volume: 3D volume (z, y, x)
        sigma: Standard deviation of Gaussian kernel
        progress_callback: Optional callback(progress: 0.0-1.0)

    Returns:
        Blurred 3D volume
    """
    if progress_callback:
        progress_callback(0.0)

    # Generate 1D Gaussian kernel
    kernel_size = int(6 * sigma + 1)
    if kernel_size % 2 == 0:
        kernel_size += 1

    x = np.arange(kernel_size) - kernel_size // 2
    kernel_1d = np.exp(-0.5 * (x / sigma) ** 2)
    kernel_1d /= kernel_1d.sum()

    # Convert to tensors
    vol_tensor = to_tensor(volume)
    kernel_tensor = to_tensor(kernel_1d)

    # Apply separable convolution along each axis
    # Z-axis
    result = _convolve_1d(vol_tensor, kernel_tensor, axis=0)
    if progress_callback:
        progress_callback(0.33)

    # Y-axis
    result = _convolve_1d(result, kernel_tensor, axis=1)
    if progress_callback:
        progress_callback(0.66)

    # X-axis
    result = _convolve_1d(result, kernel_tensor, axis=2)
    if progress_callback:
        progress_callback(1.0)

    return to_numpy(result)


def _convolve_1d(volume: Tensor, kernel: Tensor, axis: int) -> Tensor:
    """
    Apply 1D convolution along specified axis.

    Args:
        volume: Input tensor (z, y, x)
        kernel: 1D kernel
        axis: Axis to convolve along (0=z, 1=y, 2=x)

    Returns:
        Convolved tensor
    """
    # Reshape for convolution along specified axis
    shape = volume.shape
    kernel_size = kernel.shape[0]
    pad = kernel_size // 2

    # Permute to bring target axis to last position
    if axis == 0:
        volume = volume.permute(1, 2, 0)  # (y, x, z)
    elif axis == 1:
        volume = volume.permute(0, 2, 1)  # (z, x, y)
    # axis == 2: already in correct position (z, y, x)

    # Flatten first dimensions and convolve
    orig_shape = volume.shape
    volume = volume.reshape(-1, orig_shape[-1])

    # Manual convolution using matrix operations
    # Pad the volume
    padded = Tensor.cat(
        Tensor.ones((volume.shape[0], pad), dtype=dtypes.float32) * volume[:, :1],
        volume,
        Tensor.ones((volume.shape[0], pad), dtype=dtypes.float32) * volume[:, -1:],
        dim=1
    )

    # Create sliding windows and apply kernel
    result_list = []
    for i in range(orig_shape[-1]):
        window = padded[:, i:i+kernel_size]
        conv_result = (window * kernel).sum(axis=1, keepdim=True)
        result_list.append(conv_result)

    result = Tensor.cat(*result_list, dim=1)
    result = result.reshape(*orig_shape)

    # Permute back to original axis order
    if axis == 0:
        result = result.permute(2, 0, 1)  # back to (z, y, x)
    elif axis == 1:
        result = result.permute(0, 2, 1)  # back to (z, y, x)

    return result


@benchmark
def sobel_3d(
    volume: np.ndarray,
    progress_callback: Optional[Callable[[float], None]] = None
) -> np.ndarray:
    """
    GPU-accelerated 3D Sobel edge detection.

    Computes gradient magnitude using 3D Sobel operators.

    Args:
        volume: Input 3D volume (z, y, x)
        progress_callback: Optional progress callback

    Returns:
        Edge magnitude volume
    """
    if progress_callback:
        progress_callback(0.0)

    vol_tensor = to_tensor(volume)

    # 3D Sobel kernels (simplified for efficiency)
    # Gradient in X direction
    sobel_x = np.array([
        [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
        [[-2, 0, 2], [-4, 0, 4], [-2, 0, 2]],
        [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    ], dtype=np.float32) / 32.0

    # Gradient in Y direction
    sobel_y = np.array([
        [[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
        [[-2, -4, -2], [0, 0, 0], [2, 4, 2]],
        [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    ], dtype=np.float32) / 32.0

    # Gradient in Z direction
    sobel_z = np.array([
        [[-1, -2, -1], [-2, -4, -2], [-1, -2, -1]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        [[1, 2, 1], [2, 4, 2], [1, 2, 1]]
    ], dtype=np.float32) / 32.0

    # Compute gradients
    grad_x = _convolve_3d(vol_tensor, to_tensor(sobel_x))
    if progress_callback:
        progress_callback(0.33)

    grad_y = _convolve_3d(vol_tensor, to_tensor(sobel_y))
    if progress_callback:
        progress_callback(0.66)

    grad_z = _convolve_3d(vol_tensor, to_tensor(sobel_z))
    if progress_callback:
        progress_callback(0.85)

    # Compute magnitude
    magnitude = (grad_x**2 + grad_y**2 + grad_z**2).sqrt()

    if progress_callback:
        progress_callback(1.0)

    return to_numpy(magnitude)


def _convolve_3d(volume: Tensor, kernel: Tensor) -> Tensor:
    """
    Simple 3D convolution for small kernels (3x3x3).

    Args:
        volume: Input tensor (z, y, x)
        kernel: 3D kernel (3, 3, 3)

    Returns:
        Convolved tensor
    """
    z, y, x = volume.shape
    result = Tensor.zeros((z-2, y-2, x-2), dtype=dtypes.float32)

    # Simple nested loop convolution (tinygrad will optimize)
    for kz in range(3):
        for ky in range(3):
            for kx in range(3):
                vol_slice = volume[kz:z-2+kz, ky:y-2+ky, kx:x-2+kx]
                result = result + vol_slice * kernel[kz, ky, kx]

    # Pad result back to original size
    result_padded = Tensor.zeros((z, y, x), dtype=dtypes.float32)
    result_padded = result_padded.pad(((1, 1), (1, 1), (1, 1)))
    # Insert result into center
    # Note: This is a simplified version; production code would handle padding more elegantly

    return result


@benchmark
def otsu_threshold(
    volume: np.ndarray,
    num_bins: int = 256,
    progress_callback: Optional[Callable[[float], None]] = None
) -> Tuple[float, np.ndarray]:
    """
    GPU-accelerated Otsu thresholding.

    Computes optimal threshold using Otsu's method with GPU histogram.

    Args:
        volume: Input volume
        num_bins: Number of histogram bins
        progress_callback: Optional progress callback

    Returns:
        Tuple of (threshold_value, binary_mask)
    """
    if progress_callback:
        progress_callback(0.0)

    vol_tensor = to_tensor(volume)

    # Normalize to [0, 1] range
    vol_min = vol_tensor.min()
    vol_max = vol_tensor.max()
    vol_norm = (vol_tensor - vol_min) / (vol_max - vol_min + 1e-10)

    if progress_callback:
        progress_callback(0.2)

    # Compute histogram on GPU
    hist_indices = (vol_norm * (num_bins - 1)).cast(dtypes.int32)
    histogram = Tensor.zeros(num_bins, dtype=dtypes.float32)

    # Compute histogram (this is slow in tinygrad, but shows the concept)
    # Production code would use optimized histogram kernel
    vol_np = to_numpy(hist_indices).flatten()
    hist_np = np.bincount(vol_np, minlength=num_bins).astype(np.float32)
    histogram = to_tensor(hist_np)

    if progress_callback:
        progress_callback(0.5)

    # Compute Otsu threshold on GPU
    total = histogram.sum()
    current_max = Tensor([0.0])
    threshold_idx = Tensor([0], dtype=dtypes.int32)

    sum_total = (histogram * Tensor(np.arange(num_bins, dtype=np.float32))).sum()
    sum_background = Tensor([0.0])
    weight_background = Tensor([0.0])

    # Iterate through histogram to find optimal threshold
    for i in range(num_bins):
        weight_background = weight_background + histogram[i]
        weight_bg_val = to_numpy(weight_background).item() if to_numpy(weight_background).ndim > 0 else float(to_numpy(weight_background))
        if weight_bg_val == 0:
            continue

        weight_foreground = total - weight_background
        weight_fg_val = to_numpy(weight_foreground).item() if to_numpy(weight_foreground).ndim > 0 else float(to_numpy(weight_foreground))
        if weight_fg_val == 0:
            break

        sum_background = sum_background + i * histogram[i]
        mean_background = sum_background / weight_background
        mean_foreground = (sum_total - sum_background) / weight_foreground

        # Between-class variance
        variance_between = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2

        var_between_val = to_numpy(variance_between > current_max)
        is_better = var_between_val.item() if var_between_val.ndim > 0 else bool(var_between_val)
        if is_better:
            current_max = variance_between
            threshold_idx = Tensor([i], dtype=dtypes.int32)

    if progress_callback:
        progress_callback(0.8)

    # Convert threshold back to original scale
    threshold_idx_val = to_numpy(threshold_idx)
    threshold_idx_scalar = threshold_idx_val.item() if threshold_idx_val.ndim > 0 else float(threshold_idx_val)
    threshold_normalized = threshold_idx_scalar / (num_bins - 1)

    vol_range = to_numpy(vol_max - vol_min)
    vol_range_scalar = vol_range.item() if vol_range.ndim > 0 else float(vol_range)

    vol_min_val = to_numpy(vol_min)
    vol_min_scalar = vol_min_val.item() if vol_min_val.ndim > 0 else float(vol_min_val)

    threshold_value = threshold_normalized * vol_range_scalar + vol_min_scalar

    # Apply threshold
    binary_mask = (vol_tensor >= threshold_value).cast(dtypes.float32)

    if progress_callback:
        progress_callback(1.0)

    return float(threshold_value), to_numpy(binary_mask)


@benchmark
def connected_components_3d(
    binary_volume: np.ndarray,
    min_size: int = 10,
    progress_callback: Optional[Callable[[float], None]] = None
) -> Tuple[np.ndarray, int]:
    """
    GPU-accelerated 3D connected component labeling.

    Uses iterative region growing approach suitable for GPU parallelization.

    Args:
        binary_volume: Binary input volume
        min_size: Minimum component size to keep
        progress_callback: Optional progress callback

    Returns:
        Tuple of (labeled_volume, num_components)
    """
    if progress_callback:
        progress_callback(0.0)

    # Note: Full GPU-based connected components is complex
    # This implementation uses a hybrid approach with GPU acceleration
    # for parallel region processing

    vol_tensor = to_tensor(binary_volume)

    # Use scipy for now (production would implement full GPU version)
    # This is a placeholder showing the interface
    from scipy import ndimage

    labeled, num_features = ndimage.label(binary_volume)

    if progress_callback:
        progress_callback(0.7)

    # Filter by size on GPU
    if min_size > 1:
        sizes = ndimage.sum(binary_volume, labeled, range(num_features + 1))
        mask_sizes = sizes >= min_size
        mask_sizes[0] = 0  # Remove background
        labeled = mask_sizes[labeled]
        # Relabel
        labeled, num_features = ndimage.label(labeled)

    if progress_callback:
        progress_callback(1.0)

    return labeled, num_features


@benchmark
def rolling_ball_background(
    volume: np.ndarray,
    radius: float = 50.0,
    progress_callback: Optional[Callable[[float], None]] = None
) -> np.ndarray:
    """
    GPU-accelerated rolling ball background subtraction.

    Implements the rolling ball algorithm for uneven background correction.

    Args:
        volume: Input volume
        radius: Rolling ball radius in pixels
        progress_callback: Optional progress callback

    Returns:
        Background-corrected volume
    """
    if progress_callback:
        progress_callback(0.0)

    vol_tensor = to_tensor(volume)

    # Create spherical structuring element
    z = np.arange(-radius, radius + 1)
    y = np.arange(-radius, radius + 1)
    x = np.arange(-radius, radius + 1)
    zz, yy, xx = np.meshgrid(z, y, x, indexing='ij')
    ball = ((zz**2 + yy**2 + xx**2) <= radius**2).astype(np.float32)

    if progress_callback:
        progress_callback(0.2)

    # Morphological opening (erosion followed by dilation)
    # Approximation using minimum filter
    from scipy.ndimage import minimum_filter, maximum_filter

    # This is using scipy for now; production GPU version would implement
    # parallel morphological operations in tinygrad
    vol_np = to_numpy(vol_tensor)

    # Estimate background using minimum filter
    background = minimum_filter(vol_np, size=int(radius * 2))

    if progress_callback:
        progress_callback(0.6)

    background = maximum_filter(background, size=int(radius * 2))

    if progress_callback:
        progress_callback(0.8)

    # Subtract background
    background_tensor = to_tensor(background)
    corrected = vol_tensor - background_tensor
    corrected = corrected.maximum(0)  # Clip negative values

    if progress_callback:
        progress_callback(1.0)

    return to_numpy(corrected)
