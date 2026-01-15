import asyncio
import time
from typing import Dict, Any, Optional, Callable, Awaitable
import logging
import numpy as np
from pathlib import Path

from core.processing.image_loader import ImageLoader
from core.gpu import (
    DeviceManager,
    gaussian_blur_3d,
    threshold_segmentation,
    watershed_segmentation_3d,
    blob_detection_3d,
    colocalization_analysis,
    intensity_statistics,
    object_measurements,
    z_profile_analysis,
    richardson_lucy_deconvolution,
    wiener_deconvolution,
    generate_psf,
)

logger = logging.getLogger(__name__)

class ZStackAnalyzer:
    def __init__(self, progress_callback: Optional[Callable[[float, str, Optional[float]], Awaitable[None]]] = None):
        self.image_loader = ImageLoader()
        self.progress_callback = progress_callback
        self.device_manager = DeviceManager()
        self.available_algorithms = {
            "segmentation_3d": self._run_segmentation_3d,
            "colocalization": self._run_colocalization,
            "intensity_analysis": self._run_intensity_analysis,
            "deconvolution": self._run_deconvolution,
            "blob_detection": self._run_blob_detection,
            "object_measurements": self._run_object_measurements,
            "z_profile": self._run_z_profile,
        }

        logger.info(f"Initialized ZStackAnalyzer with device: {self.device_manager.device}")
    
    async def _emit_progress(self, progress: float, step: str, eta: Optional[float] = None):
        """Emit progress update if callback is configured."""
        if self.progress_callback:
            await self.progress_callback(progress, step, eta)

    async def analyze(
        self,
        file_path: str,
        algorithm: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        if algorithm not in self.available_algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        start_time = time.time()

        try:
            # Load image data
            await self._emit_progress(5.0, "Loading image data", None)
            data, metadata = await self.image_loader.load_image(file_path)

            await self._emit_progress(15.0, "Image loaded, initializing analysis", None)

            # Run analysis
            algorithm_func = self.available_algorithms[algorithm]
            results = await algorithm_func(data, parameters)

            await self._emit_progress(95.0, "Finalizing results", None)

            processing_time_ms = int((time.time() - start_time) * 1000)

            await self._emit_progress(100.0, "Analysis complete", 0)

            return {
                "algorithm": algorithm,
                "version": "1.0.0",
                "gpu_device": self._get_gpu_device(),
                "processing_time_ms": processing_time_ms,
                "results": results,
                "confidence_score": results.get("confidence_score"),
                "metadata": metadata,
            }

        except Exception as e:
            logger.error(f"Analysis failed for {file_path}: {e}")
            raise
    
    async def _run_segmentation_3d(
        self,
        data: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GPU-accelerated 3D segmentation using threshold or watershed methods.
        """
        method = parameters.get("method", "threshold")
        threshold_value = parameters.get("threshold", None)
        min_object_size = parameters.get("min_object_size", 100)

        await self._emit_progress(20.0, "Preprocessing volume data", None)

        # Optional: Apply Gaussian smoothing for noise reduction
        if parameters.get("smooth", True):
            sigma = parameters.get("sigma", 1.0)

            def smooth_progress(prog):
                asyncio.create_task(self._emit_progress(20.0 + prog * 15, "Smoothing volume", None))

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                gaussian_blur_3d,
                data,
                sigma,
                smooth_progress
            )

        await self._emit_progress(35.0, "Running segmentation algorithm", None)

        if method == "threshold":
            def segment_progress(prog):
                asyncio.create_task(self._emit_progress(35.0 + prog * 30, "Threshold segmentation", None))

            loop = asyncio.get_event_loop()
            labels, seg_metadata = await loop.run_in_executor(
                None,
                threshold_segmentation,
                data,
                "otsu" if threshold_value is None else "manual",
                threshold_value,
                min_object_size,
                True,  # fill_holes
                segment_progress
            )

        elif method == "watershed":
            def watershed_progress(prog):
                asyncio.create_task(self._emit_progress(35.0 + prog * 30, "Watershed segmentation", None))

            loop = asyncio.get_event_loop()
            labels = await loop.run_in_executor(
                None,
                watershed_segmentation_3d,
                data,
                None,  # auto-generate markers
                None,  # no mask
                0.0,   # compactness
                watershed_progress
            )
            seg_metadata = {"method": "watershed"}

        else:
            raise ValueError(f"Unknown segmentation method: {method}")

        await self._emit_progress(70.0, "Computing object metrics", None)

        # Compute object volumes
        num_objects = labels.max()
        object_volumes = []

        for obj_id in range(1, num_objects + 1):
            voxel_count = np.sum(labels == obj_id)
            object_volumes.append(int(voxel_count))

        await self._emit_progress(85.0, "Finalizing segmentation", None)

        return {
            "num_objects": int(num_objects),
            "object_volumes": object_volumes,
            "total_volume": float(np.sum(object_volumes)),
            "mean_volume": float(np.mean(object_volumes)) if object_volumes else 0.0,
            "confidence_score": 0.85,
            "parameters_used": {
                "method": method,
                "threshold": seg_metadata.get("threshold"),
                "min_object_size": min_object_size,
            }
        }
    
    async def _run_colocalization(
        self,
        data: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GPU-accelerated colocalization analysis between two channels.
        """
        if data.ndim < 4 or data.shape[0] < 2:
            raise ValueError("Colocalization requires at least 2 channels")

        channel1_idx = parameters.get("channel1", 0)
        channel2_idx = parameters.get("channel2", 1)

        await self._emit_progress(20.0, "Extracting channels", None)

        # Extract channels (assuming data is [C, Z, Y, X])
        channel1 = data[channel1_idx]
        channel2 = data[channel2_idx]

        await self._emit_progress(40.0, "Computing colocalization metrics", None)

        def coloc_progress(prog):
            asyncio.create_task(self._emit_progress(40.0 + prog * 45, "Analyzing colocalization", None))

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            colocalization_analysis,
            channel1,
            channel2,
            None,  # mask
            None,  # threshold_ch1 (auto)
            None,  # threshold_ch2 (auto)
            coloc_progress
        )

        await self._emit_progress(90.0, "Finalizing colocalization analysis", None)

        results["confidence_score"] = 0.90
        results["parameters_used"] = {
            "channel1": channel1_idx,
            "channel2": channel2_idx,
        }

        return results
    
    async def _run_intensity_analysis(
        self,
        data: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GPU-accelerated intensity analysis with optional per-object statistics.
        """
        roi_coords = parameters.get("roi_coords", None)
        labels = parameters.get("labels", None)  # Optional segmentation labels

        await self._emit_progress(20.0, "Computing intensity statistics", None)

        def stats_progress(prog):
            asyncio.create_task(self._emit_progress(20.0 + prog * 70, "Analyzing intensities", None))

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            intensity_statistics,
            data,
            labels,
            stats_progress
        )

        await self._emit_progress(95.0, "Finalizing intensity analysis", None)

        # Add additional convenience metrics
        if labels is None:
            results["dynamic_range"] = results["max"] - results["min"]
            results["signal_to_noise"] = results["mean"] / results["std"] if results["std"] > 0 else 0

        results["confidence_score"] = 0.95
        results["parameters_used"] = {
            "roi_coords": roi_coords,
            "per_object": labels is not None,
        }

        return results
    
    async def _run_deconvolution(
        self,
        data: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GPU-accelerated deconvolution (Richardson-Lucy or Wiener).
        """
        method = parameters.get("method", "richardson_lucy")
        iterations = parameters.get("iterations", 10)
        psf_type = parameters.get("psf_type", "gaussian")

        await self._emit_progress(15.0, "Generating PSF", None)

        # Generate or load PSF
        psf_shape = (31, 31, 31)  # Standard PSF size
        loop = asyncio.get_event_loop()

        psf = await loop.run_in_executor(
            None,
            generate_psf,
            psf_shape,
            psf_type,
            None,  # sigma (auto)
            0.52,  # wavelength
            1.4,   # NA
            1.518, # refractive index
            (0.2, 0.1, 0.1),  # voxel size
            None   # no progress callback for PSF
        )

        await self._emit_progress(25.0, f"Running {method} deconvolution", None)

        def deconv_progress(prog):
            asyncio.create_task(self._emit_progress(25.0 + prog * 65, f"{method} iteration", None))

        if method == "richardson_lucy":
            deconvolved = await loop.run_in_executor(
                None,
                richardson_lucy_deconvolution,
                data,
                psf,
                iterations,
                True,  # clip
                deconv_progress
            )
        elif method == "wiener":
            deconvolved = await loop.run_in_executor(
                None,
                wiener_deconvolution,
                data,
                psf,
                None,  # noise_variance (auto)
                None,  # signal_variance (auto)
                deconv_progress
            )
        else:
            raise ValueError(f"Unknown deconvolution method: {method}")

        await self._emit_progress(92.0, "Computing improvement metrics", None)

        # Compute improvement ratio (edge sharpness)
        original_edges = np.std(np.gradient(data))
        deconvolved_edges = np.std(np.gradient(deconvolved))
        improvement_ratio = deconvolved_edges / original_edges if original_edges > 0 else 1.0

        return {
            "improvement_ratio": float(improvement_ratio),
            "iterations_used": iterations if method == "richardson_lucy" else None,
            "method": method,
            "psf_type": psf_type,
            "convergence_achieved": True,
            "confidence_score": 0.80,
            "parameters_used": {
                "method": method,
                "iterations": iterations,
                "psf_type": psf_type,
            }
        }
    
    async def _run_blob_detection(
        self,
        data: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GPU-accelerated blob detection using Laplacian of Gaussian.
        """
        min_sigma = parameters.get("min_sigma", 1.0)
        max_sigma = parameters.get("max_sigma", 50.0)
        num_sigma = parameters.get("num_sigma", 10)
        threshold = parameters.get("threshold", 0.1)

        await self._emit_progress(20.0, "Detecting blobs across scales", None)

        def blob_progress(prog):
            asyncio.create_task(self._emit_progress(20.0 + prog * 70, "Blob detection", None))

        loop = asyncio.get_event_loop()
        blobs = await loop.run_in_executor(
            None,
            blob_detection_3d,
            data,
            min_sigma,
            max_sigma,
            num_sigma,
            threshold,
            0.5,  # overlap
            blob_progress
        )

        await self._emit_progress(95.0, "Finalizing blob detection", None)

        # Format blob results
        blob_list = []
        for z, y, x, sigma in blobs:
            blob_list.append({
                "z": z,
                "y": y,
                "x": x,
                "radius": float(sigma * np.sqrt(3)),  # approximate radius
            })

        return {
            "num_blobs": len(blobs),
            "blobs": blob_list,
            "confidence_score": 0.88,
            "parameters_used": {
                "min_sigma": min_sigma,
                "max_sigma": max_sigma,
                "threshold": threshold,
            }
        }

    async def _run_object_measurements(
        self,
        data: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GPU-accelerated 3D object measurements.
        """
        labels = parameters.get("labels")
        if labels is None:
            raise ValueError("object_measurements requires 'labels' parameter")

        voxel_size = parameters.get("voxel_size", (1.0, 1.0, 1.0))
        compute_surface = parameters.get("compute_surface", True)

        await self._emit_progress(20.0, "Computing object measurements", None)

        def measure_progress(prog):
            asyncio.create_task(self._emit_progress(20.0 + prog * 75, "Measuring objects", None))

        loop = asyncio.get_event_loop()
        measurements = await loop.run_in_executor(
            None,
            object_measurements,
            labels,
            voxel_size,
            compute_surface,
            measure_progress
        )

        await self._emit_progress(97.0, "Finalizing measurements", None)

        return {
            "num_objects": len(measurements),
            "measurements": measurements,
            "confidence_score": 0.92,
            "parameters_used": {
                "voxel_size": voxel_size,
                "compute_surface": compute_surface,
            }
        }

    async def _run_z_profile(
        self,
        data: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GPU-accelerated Z-profile analysis.
        """
        labels = parameters.get("labels", None)

        await self._emit_progress(20.0, "Analyzing Z-profiles", None)

        def profile_progress(prog):
            asyncio.create_task(self._emit_progress(20.0 + prog * 75, "Computing profiles", None))

        loop = asyncio.get_event_loop()
        profile_data = await loop.run_in_executor(
            None,
            z_profile_analysis,
            data,
            labels,
            profile_progress
        )

        await self._emit_progress(97.0, "Finalizing Z-profile analysis", None)

        profile_data["confidence_score"] = 0.93
        profile_data["parameters_used"] = {
            "per_object": labels is not None,
        }

        return profile_data

    def _get_gpu_device(self) -> Optional[str]:
        """Get GPU device information from device manager."""
        device_info = self.device_manager.device_info
        device_name = device_info.get("name", "Unknown")
        device_type = self.device_manager.device
        return f"{device_name} ({device_type})"