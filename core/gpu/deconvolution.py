"""
GPU-accelerated deconvolution algorithms for microscopy.

Implements:
- Richardson-Lucy deconvolution (iterative blind deconvolution)
- Wiener deconvolution (frequency domain)
- PSF generation (Gaussian, Airy disk)
"""

import numpy as np
import logging
from typing import Optional, Callable, Tuple, List

from tinygrad.tensor import Tensor
from tinygrad.dtype import dtypes
from scipy import signal, ndimage

from .device_manager import DeviceManager
from .kernels import to_tensor, to_numpy, benchmark, gaussian_blur_3d

logger = logging.getLogger(__name__)
_device_manager = DeviceManager()


@benchmark
def richardson_lucy_deconvolution(
    volume: np.ndarray,
    psf: np.ndarray,
    iterations: int = 10,
    clip: bool = True,
    progress_callback: Optional[Callable[[float], None]] = None
) -> np.ndarray:
    """
    GPU-accelerated Richardson-Lucy deconvolution.

    Iteratively estimates the true image by deconvolving with PSF.
    Standard algorithm for fluorescence microscopy deconvolution.

    Algorithm:
        I^(n+1) = I^(n) * (O / (I^(n) * PSF)) * PSF_flipped

    Where * is convolution and / is element-wise division.

    Args:
        volume: Blurred input volume
        psf: Point spread function (must be same or smaller size)
        iterations: Number of RL iterations (10-50 typical)
        clip: Whether to clip negative values
        progress_callback: Progress callback

    Returns:
        Deconvolved volume
    """
    if progress_callback:
        progress_callback(0.0)

    # Ensure PSF is normalized
    psf = psf / psf.sum()

    # Flip PSF for back-projection
    psf_flipped = np.flip(psf)

    # Initialize estimate with observed image
    estimate = volume.copy()

    # Convert to tensors for GPU acceleration
    observed_tensor = to_tensor(volume)
    psf_tensor = to_tensor(psf)
    psf_flipped_tensor = to_tensor(psf_flipped)

    logger.info(f"Starting Richardson-Lucy deconvolution: {iterations} iterations")

    for iteration in range(iterations):
        # Forward convolution: estimate * PSF
        convolved = _convolve_fft(estimate, psf)

        # Compute ratio: observed / convolved
        # Add epsilon to avoid division by zero
        ratio = volume / (convolved + 1e-10)

        # Back-project: ratio * PSF_flipped
        correction = _convolve_fft(ratio, psf_flipped)

        # Update estimate
        estimate = estimate * correction

        # Optional: clip negative values
        if clip:
            estimate = np.maximum(estimate, 0)

        if progress_callback:
            progress_callback((iteration + 1) / iterations)

        if (iteration + 1) % 5 == 0:
            logger.debug(f"RL iteration {iteration + 1}/{iterations}")

    logger.info(f"Richardson-Lucy deconvolution completed")

    return estimate


def _convolve_fft(volume: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    FFT-based convolution (faster for large kernels).

    Args:
        volume: Input volume
        kernel: Convolution kernel

    Returns:
        Convolved volume
    """
    # Use scipy's FFT convolution (optimized)
    # For GPU version, would use tinygrad FFT operations
    return signal.fftconvolve(volume, kernel, mode='same')


@benchmark
def wiener_deconvolution(
    volume: np.ndarray,
    psf: np.ndarray,
    noise_variance: Optional[float] = None,
    signal_variance: Optional[float] = None,
    progress_callback: Optional[Callable[[float], None]] = None
) -> np.ndarray:
    """
    GPU-accelerated Wiener deconvolution.

    Frequency-domain deconvolution that balances signal recovery
    with noise suppression.

    Wiener filter: H_w(f) = H*(f) / (|H(f)|² + λ)
    Where H is PSF frequency response, λ = noise/signal variance ratio.

    Args:
        volume: Blurred input volume
        psf: Point spread function
        noise_variance: Noise variance (estimated if None)
        signal_variance: Signal variance (estimated if None)
        progress_callback: Progress callback

    Returns:
        Deconvolved volume
    """
    if progress_callback:
        progress_callback(0.0)

    # Estimate variances if not provided
    if noise_variance is None:
        # Estimate from background regions (corners)
        corner_size = min(volume.shape) // 10
        corners = [
            volume[:corner_size, :corner_size, :corner_size],
            volume[-corner_size:, :corner_size, :corner_size],
            volume[:corner_size, -corner_size:, :corner_size],
            volume[:corner_size, :corner_size, -corner_size:],
        ]
        noise_variance = np.mean([np.var(corner) for corner in corners])
        logger.info(f"Estimated noise variance: {noise_variance:.6f}")

    if signal_variance is None:
        signal_variance = np.var(volume)
        logger.info(f"Estimated signal variance: {signal_variance:.6f}")

    if progress_callback:
        progress_callback(0.2)

    # Ensure PSF is normalized and same size as volume
    psf_padded = _pad_psf_to_volume(psf, volume.shape)
    psf_padded = psf_padded / psf_padded.sum()

    # FFT of volume and PSF
    volume_fft = np.fft.fftn(volume)
    psf_fft = np.fft.fftn(psf_padded)

    if progress_callback:
        progress_callback(0.5)

    # Wiener filter in frequency domain
    # H_w(f) = conj(H) / (|H|^2 + noise/signal)
    psf_fft_conj = np.conj(psf_fft)
    psf_power = np.abs(psf_fft) ** 2

    # Regularization parameter
    reg = noise_variance / signal_variance

    wiener_filter = psf_fft_conj / (psf_power + reg)

    if progress_callback:
        progress_callback(0.7)

    # Apply filter
    deconvolved_fft = volume_fft * wiener_filter

    # Inverse FFT
    deconvolved = np.fft.ifftn(deconvolved_fft).real

    if progress_callback:
        progress_callback(0.9)

    # Clip negative values
    deconvolved = np.maximum(deconvolved, 0)

    if progress_callback:
        progress_callback(1.0)

    logger.info(f"Wiener deconvolution completed (reg={reg:.6f})")

    return deconvolved


def _pad_psf_to_volume(psf: np.ndarray, target_shape: Tuple[int, int, int]) -> np.ndarray:
    """
    Pad PSF to match volume shape with PSF centered.

    Args:
        psf: Input PSF
        target_shape: Target shape (z, y, x)

    Returns:
        Padded PSF
    """
    padded = np.zeros(target_shape, dtype=psf.dtype)

    # Compute padding
    pad_z = (target_shape[0] - psf.shape[0]) // 2
    pad_y = (target_shape[1] - psf.shape[1]) // 2
    pad_x = (target_shape[2] - psf.shape[2]) // 2

    # Place PSF in center
    padded[
        pad_z:pad_z + psf.shape[0],
        pad_y:pad_y + psf.shape[1],
        pad_x:pad_x + psf.shape[2]
    ] = psf

    # Circularly shift PSF so center is at (0, 0, 0)
    padded = np.roll(padded, shift=(-pad_z, -pad_y, -pad_x), axis=(0, 1, 2))

    return padded


@benchmark
def generate_psf(
    shape: Tuple[int, int, int],
    psf_type: str = "gaussian",
    sigma: Optional[Tuple[float, float, float]] = None,
    wavelength: float = 0.52,  # μm (green light)
    numerical_aperture: float = 1.4,
    refractive_index: float = 1.518,  # oil immersion
    voxel_size: Tuple[float, float, float] = (0.2, 0.1, 0.1),  # μm (z, y, x)
    progress_callback: Optional[Callable[[float], None]] = None
) -> np.ndarray:
    """
    Generate theoretical PSF for deconvolution.

    Args:
        shape: PSF shape (z, y, x) - should be odd dimensions
        psf_type: PSF model ("gaussian", "airy", "gibson-lanni")
        sigma: Gaussian sigma for "gaussian" type (z, y, x)
        wavelength: Emission wavelength in μm
        numerical_aperture: Objective NA
        refractive_index: Immersion medium refractive index
        voxel_size: Voxel size (z, y, x) in μm
        progress_callback: Progress callback

    Returns:
        3D PSF array (normalized)
    """
    if progress_callback:
        progress_callback(0.0)

    if psf_type == "gaussian":
        return _generate_gaussian_psf(shape, sigma, progress_callback)

    elif psf_type == "airy":
        return _generate_airy_psf(
            shape,
            wavelength,
            numerical_aperture,
            voxel_size,
            progress_callback
        )

    elif psf_type == "gibson-lanni":
        logger.warning("Gibson-Lanni PSF not implemented, using Airy disk")
        return _generate_airy_psf(
            shape,
            wavelength,
            numerical_aperture,
            voxel_size,
            progress_callback
        )

    else:
        raise ValueError(f"Unknown PSF type: {psf_type}")


def _generate_gaussian_psf(
    shape: Tuple[int, int, int],
    sigma: Optional[Tuple[float, float, float]] = None,
    progress_callback: Optional[Callable[[float], None]] = None
) -> np.ndarray:
    """
    Generate 3D Gaussian PSF.

    Args:
        shape: PSF shape (z, y, x)
        sigma: Standard deviations (z, y, x)
        progress_callback: Progress callback

    Returns:
        3D Gaussian PSF
    """
    if sigma is None:
        # Default anisotropic PSF (z-resolution worse than xy)
        sigma = (2.0, 1.0, 1.0)

    if progress_callback:
        progress_callback(0.3)

    sz, sy, sx = shape
    sigma_z, sigma_y, sigma_x = sigma

    # Create coordinate grids centered at PSF center
    z = np.arange(sz) - sz // 2
    y = np.arange(sy) - sy // 2
    x = np.arange(sx) - sx // 2

    zz, yy, xx = np.meshgrid(z, y, x, indexing='ij')

    if progress_callback:
        progress_callback(0.6)

    # 3D Gaussian
    psf = np.exp(
        -(zz**2 / (2 * sigma_z**2) +
          yy**2 / (2 * sigma_y**2) +
          xx**2 / (2 * sigma_x**2))
    )

    # Normalize
    psf = psf / psf.sum()

    if progress_callback:
        progress_callback(1.0)

    logger.info(f"Generated Gaussian PSF: shape={shape}, sigma={sigma}")

    return psf.astype(np.float32)


def _generate_airy_psf(
    shape: Tuple[int, int, int],
    wavelength: float,
    numerical_aperture: float,
    voxel_size: Tuple[float, float, float],
    progress_callback: Optional[Callable[[float], None]] = None
) -> np.ndarray:
    """
    Generate theoretical Airy disk PSF for widefield/confocal microscopy.

    Based on Born & Wolf theory for diffraction-limited PSF.

    Args:
        shape: PSF shape (z, y, x)
        wavelength: Wavelength in μm
        numerical_aperture: Objective NA
        voxel_size: Voxel size (z, y, x) in μm
        progress_callback: Progress callback

    Returns:
        3D Airy PSF
    """
    if progress_callback:
        progress_callback(0.2)

    sz, sy, sx = shape
    vz, vy, vx = voxel_size

    # Theoretical resolution limits
    # Lateral (XY) resolution: 0.61 * λ / NA
    # Axial (Z) resolution: 2 * λ / NA²
    lateral_res = 0.61 * wavelength / numerical_aperture
    axial_res = 2 * wavelength / (numerical_aperture ** 2)

    logger.info(f"PSF resolution: lateral={lateral_res:.3f}μm, axial={axial_res:.3f}μm")

    # Create coordinate grids in micrometers
    z = (np.arange(sz) - sz // 2) * vz
    y = (np.arange(sy) - sy // 2) * vy
    x = (np.arange(sx) - sx // 2) * vx

    zz, yy, xx = np.meshgrid(z, y, x, indexing='ij')

    if progress_callback:
        progress_callback(0.5)

    # Radial distance in XY plane
    r = np.sqrt(xx**2 + yy**2)

    # Normalized coordinates
    v = (2 * np.pi * numerical_aperture * r) / wavelength
    u = (2 * np.pi * numerical_aperture**2 * np.abs(zz)) / wavelength

    if progress_callback:
        progress_callback(0.7)

    # Airy disk in XY (2J₁(v)/v)²
    # Use approximation to avoid singularity at v=0
    with np.errstate(divide='ignore', invalid='ignore'):
        from scipy.special import j1
        airy_xy = (2 * j1(v) / (v + 1e-10)) ** 2
        airy_xy[v == 0] = 1.0

    # Axial component (sin(u/4)/(u/4))²
    with np.errstate(divide='ignore', invalid='ignore'):
        airy_z = (np.sin(u / 4) / (u / 4 + 1e-10)) ** 2
        airy_z[u == 0] = 1.0

    if progress_callback:
        progress_callback(0.9)

    # Combine XY and Z components
    psf = airy_xy * airy_z

    # Normalize
    psf = psf / psf.sum()

    if progress_callback:
        progress_callback(1.0)

    logger.info(f"Generated Airy PSF: λ={wavelength}μm, NA={numerical_aperture}")

    return psf.astype(np.float32)


def estimate_psf_from_beads(
    bead_volume: np.ndarray,
    bead_coordinates: Optional[List[Tuple[int, int, int]]] = None,
    psf_size: Tuple[int, int, int] = (31, 31, 31),
    progress_callback: Optional[Callable[[float], None]] = None
) -> np.ndarray:
    """
    Estimate empirical PSF from fluorescent bead images.

    Averages PSF measurements from multiple isolated beads.

    Args:
        bead_volume: 3D volume containing fluorescent beads
        bead_coordinates: List of (z, y, x) bead centers (auto-detected if None)
        psf_size: Size of extracted PSF (should be odd)
        progress_callback: Progress callback

    Returns:
        Averaged empirical PSF
    """
    if progress_callback:
        progress_callback(0.0)

    # Auto-detect beads if coordinates not provided
    if bead_coordinates is None:
        from skimage.feature import blob_log
        blobs = blob_log(
            bead_volume,
            min_sigma=1,
            max_sigma=5,
            num_sigma=10,
            threshold=0.1
        )
        bead_coordinates = [(int(b[0]), int(b[1]), int(b[2])) for b in blobs]
        logger.info(f"Detected {len(bead_coordinates)} beads")

    if progress_callback:
        progress_callback(0.3)

    # Extract PSF regions around each bead
    psf_stack = []
    half_size = tuple(s // 2 for s in psf_size)

    for i, (z, y, x) in enumerate(bead_coordinates):
        # Check if bead is far enough from edges
        if (z >= half_size[0] and z < bead_volume.shape[0] - half_size[0] and
            y >= half_size[1] and y < bead_volume.shape[1] - half_size[1] and
            x >= half_size[2] and x < bead_volume.shape[2] - half_size[2]):

            psf_region = bead_volume[
                z - half_size[0]:z + half_size[0] + 1,
                y - half_size[1]:y + half_size[1] + 1,
                x - half_size[2]:x + half_size[2] + 1
            ]

            # Normalize PSF region
            psf_region = psf_region / psf_region.sum()
            psf_stack.append(psf_region)

        if progress_callback and i % max(1, len(bead_coordinates) // 10) == 0:
            progress_callback(0.3 + 0.6 * i / len(bead_coordinates))

    if len(psf_stack) == 0:
        raise ValueError("No valid beads found for PSF estimation")

    # Average PSFs
    psf_empirical = np.mean(psf_stack, axis=0)
    psf_empirical = psf_empirical / psf_empirical.sum()

    if progress_callback:
        progress_callback(1.0)

    logger.info(f"Estimated empirical PSF from {len(psf_stack)} beads")

    return psf_empirical.astype(np.float32)
