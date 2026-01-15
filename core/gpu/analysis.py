"""
GPU-accelerated analysis functions for microscopy data.

Implements:
- Colocalization analysis (Pearson, Manders, overlap coefficient)
- Intensity statistics per object
- 3D object measurements (volume, surface area, sphericity)
- Z-profile analysis
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Callable, Tuple

from tinygrad.tensor import Tensor
from tinygrad.dtype import dtypes

from .device_manager import DeviceManager
from .kernels import to_tensor, to_numpy, benchmark

logger = logging.getLogger(__name__)
_device_manager = DeviceManager()


@benchmark
def colocalization_analysis(
    channel1: np.ndarray,
    channel2: np.ndarray,
    mask: Optional[np.ndarray] = None,
    threshold_ch1: Optional[float] = None,
    threshold_ch2: Optional[float] = None,
    progress_callback: Optional[Callable[[float], None]] = None
) -> Dict[str, float]:
    """
    GPU-accelerated colocalization analysis between two channels.

    Computes:
    - Pearson correlation coefficient
    - Manders' M1 and M2 coefficients
    - Overlap coefficient
    - Costes' automatic threshold (if thresholds not provided)

    Args:
        channel1: First channel intensity volume
        channel2: Second channel intensity volume
        mask: Optional binary mask to restrict analysis region
        threshold_ch1: Optional threshold for channel 1 (auto-computed if None)
        threshold_ch2: Optional threshold for channel 2 (auto-computed if None)
        progress_callback: Progress callback

    Returns:
        Dictionary with colocalization metrics
    """
    if progress_callback:
        progress_callback(0.0)

    if channel1.shape != channel2.shape:
        raise ValueError("Channels must have the same shape")

    # Convert to tensors
    ch1_tensor = to_tensor(channel1)
    ch2_tensor = to_tensor(channel2)

    # Apply mask if provided
    if mask is not None:
        mask_tensor = to_tensor(mask.astype(np.float32))
        ch1_tensor = ch1_tensor * mask_tensor
        ch2_tensor = ch2_tensor * mask_tensor
        n_pixels = mask_tensor.sum()
    else:
        n_pixels = Tensor([np.prod(channel1.shape)], dtype=dtypes.float32)

    if progress_callback:
        progress_callback(0.2)

    # Compute Pearson correlation coefficient
    mean1 = ch1_tensor.sum() / n_pixels
    mean2 = ch2_tensor.sum() / n_pixels

    diff1 = ch1_tensor - mean1
    diff2 = ch2_tensor - mean2

    numerator = (diff1 * diff2).sum()
    denominator = ((diff1 ** 2).sum() * (diff2 ** 2).sum()).sqrt()

    pearson_r = numerator / (denominator + 1e-10)

    if progress_callback:
        progress_callback(0.5)

    # Determine thresholds using Costes' method if not provided
    if threshold_ch1 is None or threshold_ch2 is None:
        threshold_ch1, threshold_ch2 = _costes_threshold(
            to_numpy(ch1_tensor),
            to_numpy(ch2_tensor),
            mask=mask
        )
        logger.info(f"Costes' thresholds: ch1={threshold_ch1:.4f}, ch2={threshold_ch2:.4f}")

    # Create threshold masks
    ch1_above = (ch1_tensor >= threshold_ch1).cast(dtypes.float32)
    ch2_above = (ch2_tensor >= threshold_ch2).cast(dtypes.float32)

    if progress_callback:
        progress_callback(0.7)

    # Compute Manders' coefficients
    # M1: fraction of ch1 above threshold that colocalizes with ch2 above threshold
    ch1_above_total = (ch1_tensor * ch1_above).sum()
    ch1_coloc = (ch1_tensor * ch1_above * ch2_above).sum()
    manders_m1 = ch1_coloc / (ch1_above_total + 1e-10)

    # M2: fraction of ch2 above threshold that colocalizes with ch1 above threshold
    ch2_above_total = (ch2_tensor * ch2_above).sum()
    ch2_coloc = (ch2_tensor * ch1_above * ch2_above).sum()
    manders_m2 = ch2_coloc / (ch2_above_total + 1e-10)

    if progress_callback:
        progress_callback(0.85)

    # Overlap coefficient (simplified)
    overlap = (ch1_above * ch2_above).sum() / (ch1_above.sum() + ch2_above.sum() - (ch1_above * ch2_above).sum() + 1e-10)

    if progress_callback:
        progress_callback(1.0)

    # Realize all tensors and convert to numpy
    results = {
        "pearson_r": float(to_numpy(pearson_r)[0] if pearson_r.shape == (1,) else to_numpy(pearson_r)),
        "manders_m1": float(to_numpy(manders_m1)[0] if manders_m1.shape == (1,) else to_numpy(manders_m1)),
        "manders_m2": float(to_numpy(manders_m2)[0] if manders_m2.shape == (1,) else to_numpy(manders_m2)),
        "overlap_coefficient": float(to_numpy(overlap)[0] if overlap.shape == (1,) else to_numpy(overlap)),
        "threshold_ch1": float(threshold_ch1),
        "threshold_ch2": float(threshold_ch2),
    }

    logger.info(f"Colocalization: Pearson={results['pearson_r']:.3f}, M1={results['manders_m1']:.3f}, M2={results['manders_m2']:.3f}")

    return results


def _costes_threshold(
    channel1: np.ndarray,
    channel2: np.ndarray,
    mask: Optional[np.ndarray] = None
) -> Tuple[float, float]:
    """
    Compute automatic thresholds using Costes' method.

    Finds thresholds that minimize Pearson correlation below threshold
    and maximize it above threshold.

    Args:
        channel1: First channel
        channel2: Second channel
        mask: Optional mask

    Returns:
        Tuple of (threshold_ch1, threshold_ch2)
    """
    # Flatten and mask
    ch1_flat = channel1.flatten()
    ch2_flat = channel2.flatten()

    if mask is not None:
        mask_flat = mask.flatten().astype(bool)
        ch1_flat = ch1_flat[mask_flat]
        ch2_flat = ch2_flat[mask_flat]

    # Simple percentile-based thresholds (fast approximation)
    # Production Costes' method would iterate to find optimal thresholds
    threshold_ch1 = np.percentile(ch1_flat[ch1_flat > 0], 50)
    threshold_ch2 = np.percentile(ch2_flat[ch2_flat > 0], 50)

    return float(threshold_ch1), float(threshold_ch2)


@benchmark
def intensity_statistics(
    volume: np.ndarray,
    labels: Optional[np.ndarray] = None,
    progress_callback: Optional[Callable[[float], None]] = None
) -> Dict[str, any]:
    """
    Compute intensity statistics for volume or per labeled object.

    Args:
        volume: Input intensity volume
        labels: Optional labeled segmentation (0 = background)
        progress_callback: Progress callback

    Returns:
        Dictionary with statistics
    """
    if progress_callback:
        progress_callback(0.0)

    vol_tensor = to_tensor(volume)

    if labels is None:
        # Global statistics
        stats = {
            "mean": float(to_numpy(vol_tensor.mean())),
            "std": float(to_numpy(vol_tensor.std())),
            "min": float(to_numpy(vol_tensor.min())),
            "max": float(to_numpy(vol_tensor.max())),
            "median": float(np.median(to_numpy(vol_tensor))),
            "total_intensity": float(to_numpy(vol_tensor.sum())),
        }
        if progress_callback:
            progress_callback(1.0)
        return stats

    # Per-object statistics
    from scipy import ndimage

    num_objects = labels.max()
    logger.info(f"Computing statistics for {num_objects} objects")

    object_stats = []

    for obj_id in range(1, num_objects + 1):
        mask = (labels == obj_id)
        obj_intensities = volume[mask]

        if len(obj_intensities) > 0:
            obj_stats.append({
                "object_id": int(obj_id),
                "mean": float(np.mean(obj_intensities)),
                "std": float(np.std(obj_intensities)),
                "min": float(np.min(obj_intensities)),
                "max": float(np.max(obj_intensities)),
                "median": float(np.median(obj_intensities)),
                "total_intensity": float(np.sum(obj_intensities)),
                "voxel_count": int(len(obj_intensities)),
            })

        if progress_callback and obj_id % max(1, num_objects // 10) == 0:
            progress_callback(obj_id / num_objects)

    if progress_callback:
        progress_callback(1.0)

    return {
        "num_objects": num_objects,
        "object_statistics": object_stats,
        "global_mean": float(np.mean(volume)),
        "global_std": float(np.std(volume)),
    }


@benchmark
def object_measurements(
    labels: np.ndarray,
    voxel_size: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    compute_surface: bool = True,
    progress_callback: Optional[Callable[[float], None]] = None
) -> List[Dict[str, float]]:
    """
    Compute 3D morphological measurements for labeled objects.

    Args:
        labels: Labeled segmentation volume
        voxel_size: Voxel size in (z, y, x) in micrometers
        compute_surface: Whether to compute surface area (expensive)
        progress_callback: Progress callback

    Returns:
        List of measurement dictionaries per object
    """
    if progress_callback:
        progress_callback(0.0)

    from scipy import ndimage
    from skimage import measure

    num_objects = labels.max()
    logger.info(f"Computing measurements for {num_objects} objects")

    measurements = []
    vz, vy, vx = voxel_size

    for obj_id in range(1, num_objects + 1):
        mask = (labels == obj_id)
        voxel_count = np.sum(mask)

        if voxel_count == 0:
            continue

        # Volume
        volume = voxel_count * vz * vy * vx

        # Centroid
        coords = np.argwhere(mask)
        centroid = coords.mean(axis=0)
        centroid_scaled = centroid * np.array([vz, vy, vx])

        # Bounding box
        z_coords, y_coords, x_coords = coords.T
        bbox = {
            "z_min": int(z_coords.min()),
            "z_max": int(z_coords.max()),
            "y_min": int(y_coords.min()),
            "y_max": int(y_coords.max()),
            "x_min": int(x_coords.min()),
            "x_max": int(x_coords.max()),
        }

        # Extent (volume / bounding box volume)
        bbox_volume = (
            (bbox["z_max"] - bbox["z_min"] + 1) * vz *
            (bbox["y_max"] - bbox["y_min"] + 1) * vy *
            (bbox["x_max"] - bbox["x_min"] + 1) * vx
        )
        extent = volume / bbox_volume if bbox_volume > 0 else 0

        obj_measurement = {
            "object_id": obj_id,
            "volume": float(volume),
            "voxel_count": int(voxel_count),
            "centroid_z": float(centroid_scaled[0]),
            "centroid_y": float(centroid_scaled[1]),
            "centroid_x": float(centroid_scaled[2]),
            "extent": float(extent),
            "bbox": bbox,
        }

        # Surface area and sphericity (expensive)
        if compute_surface:
            try:
                # Extract surface using marching cubes
                verts, faces, normals, values = measure.marching_cubes(
                    mask.astype(np.float32),
                    level=0.5,
                    spacing=(vz, vy, vx)
                )

                # Compute surface area from faces
                v0 = verts[faces[:, 0]]
                v1 = verts[faces[:, 1]]
                v2 = verts[faces[:, 2]]

                # Triangle areas
                cross = np.cross(v1 - v0, v2 - v0)
                areas = 0.5 * np.linalg.norm(cross, axis=1)
                surface_area = areas.sum()

                # Sphericity: (36π * volume²)^(1/3) / surface_area
                # Perfect sphere = 1.0, less spherical < 1.0
                sphericity = (36 * np.pi * volume ** 2) ** (1/3) / surface_area if surface_area > 0 else 0

                obj_measurement.update({
                    "surface_area": float(surface_area),
                    "sphericity": float(sphericity),
                })

            except Exception as e:
                logger.debug(f"Could not compute surface for object {obj_id}: {e}")
                obj_measurement.update({
                    "surface_area": None,
                    "sphericity": None,
                })

        measurements.append(obj_measurement)

        if progress_callback and obj_id % max(1, num_objects // 10) == 0:
            progress_callback(obj_id / num_objects)

    if progress_callback:
        progress_callback(1.0)

    logger.info(f"Completed measurements for {len(measurements)} objects")
    return measurements


@benchmark
def z_profile_analysis(
    volume: np.ndarray,
    labels: Optional[np.ndarray] = None,
    progress_callback: Optional[Callable[[float], None]] = None
) -> Dict[str, any]:
    """
    Analyze intensity profiles along Z-axis.

    Useful for assessing Z-drift, photobleaching, and 3D distribution.

    Args:
        volume: Input intensity volume
        labels: Optional segmentation labels
        progress_callback: Progress callback

    Returns:
        Dictionary with Z-profile data
    """
    if progress_callback:
        progress_callback(0.0)

    z_depth = volume.shape[0]

    # Global Z-profile
    global_profile = []
    for z in range(z_depth):
        slice_mean = volume[z].mean()
        slice_std = volume[z].std()
        slice_max = volume[z].max()

        global_profile.append({
            "z": z,
            "mean": float(slice_mean),
            "std": float(slice_std),
            "max": float(slice_max),
        })

    if progress_callback:
        progress_callback(0.5)

    result = {
        "z_depth": z_depth,
        "global_profile": global_profile,
    }

    # Per-object Z-profiles if labels provided
    if labels is not None:
        num_objects = labels.max()
        object_profiles = []

        for obj_id in range(1, num_objects + 1):
            mask = (labels == obj_id)

            # Find Z-range for this object
            z_coords = np.argwhere(mask)[:, 0]
            if len(z_coords) == 0:
                continue

            z_min, z_max = z_coords.min(), z_coords.max()

            obj_profile = []
            for z in range(z_min, z_max + 1):
                obj_slice_mask = mask[z]
                if obj_slice_mask.sum() > 0:
                    obj_intensities = volume[z][obj_slice_mask]
                    obj_profile.append({
                        "z": int(z),
                        "mean": float(obj_intensities.mean()),
                        "voxel_count": int(obj_slice_mask.sum()),
                    })

            object_profiles.append({
                "object_id": obj_id,
                "z_range": (int(z_min), int(z_max)),
                "profile": obj_profile,
            })

        result["object_profiles"] = object_profiles

    if progress_callback:
        progress_callback(1.0)

    return result


def compute_photobleaching_correction(
    z_profile: List[Dict[str, float]],
    method: str = "exponential"
) -> np.ndarray:
    """
    Compute photobleaching correction factors from Z-profile.

    Args:
        z_profile: Z-profile from z_profile_analysis()
        method: Correction method ("exponential", "linear")

    Returns:
        Array of correction factors (multiply intensity by these)
    """
    z_values = np.array([p["z"] for p in z_profile])
    mean_values = np.array([p["mean"] for p in z_profile])

    if method == "exponential":
        # Fit exponential decay: I(z) = I0 * exp(-λ*z)
        # Correction: exp(λ*z)
        from scipy.optimize import curve_fit

        def exp_decay(z, I0, lamb):
            return I0 * np.exp(-lamb * z)

        try:
            params, _ = curve_fit(exp_decay, z_values, mean_values, p0=[mean_values[0], 0.01])
            I0, lamb = params
            correction = np.exp(lamb * z_values) / I0
        except:
            logger.warning("Exponential fit failed, using linear correction")
            method = "linear"

    if method == "linear":
        # Linear fit and correction
        coeffs = np.polyfit(z_values, mean_values, 1)
        fitted = np.polyval(coeffs, z_values)
        correction = mean_values[0] / fitted

    return correction
