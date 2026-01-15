"""
Device management for GPU-accelerated operations.

Handles automatic device detection (CUDA, Metal, CPU fallback) and
provides utilities for optimal device configuration.
"""

import logging
from typing import Optional, Dict, Any
from functools import lru_cache

from tinygrad.device import Device
from tinygrad.tensor import Tensor
from tinygrad.dtype import dtypes

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages GPU device selection and configuration for tinygrad operations."""

    _instance: Optional['DeviceManager'] = None
    _device: Optional[str] = None
    _device_info: Dict[str, Any] = {}

    def __new__(cls):
        """Singleton pattern to ensure single device manager instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize device manager with automatic device detection."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._detect_device()

    def _detect_device(self) -> None:
        """
        Detect and configure the best available GPU device.

        Priority order:
        1. CUDA (NVIDIA GPUs)
        2. METAL (Apple Silicon / AMD on macOS)
        3. CPU (fallback)
        """
        try:
            # Try CUDA first (most common in research environments)
            try:
                Device.DEFAULT = "CUDA"
                test = Tensor([1.0], device="CUDA").realize()
                self._device = "CUDA"
                self._device_info = self._get_cuda_info()
                logger.info(f"Using CUDA device: {self._device_info.get('name', 'Unknown')}")
                return
            except Exception:
                pass

            # Try Metal (Apple Silicon, AMD on macOS)
            try:
                Device.DEFAULT = "METAL"
                test = Tensor([1.0], device="METAL").realize()
                self._device = "METAL"
                self._device_info = self._get_metal_info()
                logger.info(f"Using Metal device: {self._device_info.get('name', 'Unknown')}")
                return
            except Exception:
                pass

            # Fallback to CPU
            Device.DEFAULT = "CPU"
            self._device = "CPU"
            self._device_info = {"name": "CPU", "compute_capability": None}
            logger.warning("No GPU detected, falling back to CPU (performance will be degraded)")

        except Exception as e:
            logger.error(f"Device detection failed: {e}")
            Device.DEFAULT = "CPU"
            self._device = "CPU"
            self._device_info = {"name": "CPU", "compute_capability": None}

    def _get_cuda_info(self) -> Dict[str, Any]:
        """Get CUDA device information."""
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,compute_cap", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(",")
                return {
                    "name": parts[0].strip(),
                    "compute_capability": parts[1].strip() if len(parts) > 1 else None,
                    "type": "CUDA"
                }
        except Exception as e:
            logger.debug(f"Could not get detailed CUDA info: {e}")

        return {"name": "NVIDIA GPU", "compute_capability": None, "type": "CUDA"}

    def _get_metal_info(self) -> Dict[str, Any]:
        """Get Metal device information."""
        try:
            import subprocess
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse GPU name from system_profiler output
                for line in result.stdout.split("\n"):
                    if "Chipset Model" in line or "GPU" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            gpu_name = parts[1].strip()
                            return {"name": gpu_name, "compute_capability": None, "type": "METAL"}
        except Exception as e:
            logger.debug(f"Could not get detailed Metal info: {e}")

        return {"name": "Apple GPU", "compute_capability": None, "type": "METAL"}

    @property
    def device(self) -> str:
        """Get the current device name."""
        return self._device or "CPU"

    @property
    def device_info(self) -> Dict[str, Any]:
        """Get detailed device information."""
        return self._device_info.copy()

    @property
    def is_gpu(self) -> bool:
        """Check if a GPU device is available."""
        return self._device in ("CUDA", "METAL")

    @property
    def is_cuda(self) -> bool:
        """Check if using CUDA device."""
        return self._device == "CUDA"

    @property
    def is_metal(self) -> bool:
        """Check if using Metal device."""
        return self._device == "METAL"

    def get_optimal_dtype(self) -> dtypes:
        """
        Get optimal data type for current device.

        Returns:
            dtypes.float32 for GPU (best performance/precision tradeoff)
            dtypes.float32 for CPU
        """
        # float32 is optimal for most microscopy operations
        # float16 could be used for memory-constrained scenarios but
        # microscopy quantitative analysis needs float32 precision
        return dtypes.float32

    @lru_cache(maxsize=1)
    def get_device_memory_info(self) -> Dict[str, Any]:
        """
        Get available device memory information.

        Returns:
            Dictionary with memory stats (in bytes):
            - total: Total device memory
            - available: Available device memory
            - used: Used device memory
        """
        if self.is_cuda:
            try:
                import subprocess
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=memory.total,memory.free,memory.used",
                     "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    total, free, used = map(int, result.stdout.strip().split(","))
                    return {
                        "total": total * 1024 * 1024,  # Convert MB to bytes
                        "available": free * 1024 * 1024,
                        "used": used * 1024 * 1024,
                    }
            except Exception as e:
                logger.debug(f"Could not get CUDA memory info: {e}")

        elif self.is_metal:
            try:
                import subprocess
                result = subprocess.run(
                    ["sysctl", "hw.memsize"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Metal uses unified memory, get system memory
                    total = int(result.stdout.split(":")[1].strip())
                    return {
                        "total": total,
                        "available": total // 2,  # Conservative estimate
                        "used": total // 2,
                    }
            except Exception as e:
                logger.debug(f"Could not get Metal memory info: {e}")

        # Fallback values
        return {
            "total": 0,
            "available": 0,
            "used": 0,
        }

    def estimate_max_volume_size(self, dtype=dtypes.float32, safety_factor: float = 0.7) -> tuple[int, int, int]:
        """
        Estimate maximum 3D volume dimensions that can fit in device memory.

        Args:
            dtype: Data type for computation
            safety_factor: Use only this fraction of available memory (0.0-1.0)

        Returns:
            Tuple of (z, y, x) maximum dimensions
        """
        memory_info = self.get_device_memory_info()
        available_bytes = memory_info.get("available", 4 * 1024**3)  # Default 4GB

        # Account for safety factor and intermediate buffers (3x for processing overhead)
        usable_bytes = available_bytes * safety_factor / 3

        # float32 = 4 bytes per element
        bytes_per_element = 4 if dtype == dtypes.float32 else 2

        # Estimate cubic volume
        elements = usable_bytes / bytes_per_element
        side_length = int(elements ** (1/3))

        # Return reasonable bounds
        max_side = min(side_length, 2048)  # Cap at 2048 per dimension
        return (max_side, max_side, max_side)

    def __repr__(self) -> str:
        """String representation of device manager."""
        device_name = self._device_info.get("name", "Unknown")
        return f"DeviceManager(device='{self._device}', name='{device_name}')"


# Global instance
_device_manager = DeviceManager()


def get_device() -> str:
    """Get current GPU device name."""
    return _device_manager.device


def get_device_info() -> Dict[str, Any]:
    """Get detailed device information."""
    return _device_manager.device_info


def is_gpu_available() -> bool:
    """Check if GPU is available."""
    return _device_manager.is_gpu
