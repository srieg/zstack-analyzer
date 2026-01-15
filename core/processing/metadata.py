"""
Unified metadata model for microscopy images.

Converts vendor-specific metadata formats (TIFF, CZI, ND2, LSM, LIF)
into a common, standardized format with physical units and acquisition info.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class PhysicalUnit(str, Enum):
    """Physical units for spatial measurements"""
    METER = "m"
    MILLIMETER = "mm"
    MICROMETER = "µm"
    NANOMETER = "nm"
    PICOMETER = "pm"


class TimeUnit(str, Enum):
    """Time units for temporal measurements"""
    SECOND = "s"
    MILLISECOND = "ms"
    MICROSECOND = "µs"
    NANOSECOND = "ns"


class DimensionOrder(str, Enum):
    """Dimension ordering conventions"""
    TZCYX = "TZCYX"  # Time, Z, Channel, Y, X
    TZYXC = "TZYXC"  # Time, Z, Y, X, Channel
    ZCYX = "ZCYX"    # Z, Channel, Y, X
    ZYXC = "ZYXC"    # Z, Y, X, Channel
    CYX = "CYX"      # Channel, Y, X
    YXC = "YXC"      # Y, X, Channel
    ZYX = "ZYX"      # Z, Y, X (grayscale)


class ChannelInfo(BaseModel):
    """Information about a single channel"""
    name: str
    wavelength: Optional[float] = None  # nm
    emission_wavelength: Optional[float] = None  # nm
    exposure_time: Optional[float] = None  # ms
    gain: Optional[float] = None
    contrast_method: Optional[str] = None  # e.g., "fluorescence", "brightfield"
    dye_name: Optional[str] = None
    color: Optional[str] = None  # hex color for visualization


class ObjectiveInfo(BaseModel):
    """Microscope objective information"""
    name: Optional[str] = None
    magnification: Optional[float] = None
    numerical_aperture: Optional[float] = None  # NA
    immersion: Optional[str] = None  # e.g., "air", "oil", "water"
    working_distance: Optional[float] = None  # µm
    correction: Optional[str] = None  # e.g., "plan-apochromat"


class MicroscopeInfo(BaseModel):
    """Microscope system information"""
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    microscope_type: Optional[str] = None  # e.g., "confocal", "widefield", "light-sheet"


class PhysicalSize(BaseModel):
    """Physical size with unit"""
    value: float
    unit: PhysicalUnit = PhysicalUnit.MICROMETER

    def to_micrometers(self) -> float:
        """Convert to micrometers"""
        conversion = {
            PhysicalUnit.METER: 1e6,
            PhysicalUnit.MILLIMETER: 1e3,
            PhysicalUnit.MICROMETER: 1.0,
            PhysicalUnit.NANOMETER: 1e-3,
            PhysicalUnit.PICOMETER: 1e-6,
        }
        return self.value * conversion[self.unit]


class ImageMetadata(BaseModel):
    """
    Unified metadata model for microscopy images.

    This model provides a consistent interface across different file formats,
    converting vendor-specific metadata into a standardized format.
    """
    # File information
    filename: str
    file_format: str  # e.g., "TIFF", "CZI", "ND2", "LSM", "LIF"
    file_size_bytes: int

    # Image dimensions
    size_x: int = Field(..., description="Width in pixels")
    size_y: int = Field(..., description="Height in pixels")
    size_z: int = Field(default=1, description="Number of Z slices")
    size_c: int = Field(default=1, description="Number of channels")
    size_t: int = Field(default=1, description="Number of time points")
    size_p: int = Field(default=1, description="Number of positions/scenes")

    # Dimension ordering
    dimension_order: DimensionOrder = DimensionOrder.ZCYX

    # Physical spacing
    pixel_size_x: Optional[PhysicalSize] = None
    pixel_size_y: Optional[PhysicalSize] = None
    pixel_size_z: Optional[PhysicalSize] = None

    # Pixel type information
    dtype: str  # numpy dtype string
    bits_per_pixel: int
    is_signed: bool = False

    # Channel information
    channels: List[ChannelInfo] = []

    # Hardware information
    objective: Optional[ObjectiveInfo] = None
    microscope: Optional[MicroscopeInfo] = None

    # Acquisition information
    acquisition_date: Optional[datetime] = None
    acquisition_software: Optional[str] = None
    acquisition_software_version: Optional[str] = None

    # Time series information
    time_increment: Optional[float] = None  # seconds between frames
    time_unit: TimeUnit = TimeUnit.SECOND

    # Multi-position information
    stage_positions: Optional[List[Dict[str, float]]] = None  # X, Y, Z coordinates

    # Additional vendor-specific metadata
    vendor_metadata: Dict[str, Any] = {}

    # Processing metadata
    is_rgb: bool = False
    is_indexed: bool = False
    compression: Optional[str] = None

    class Config:
        use_enum_values = True

    def get_voxel_size_micrometers(self) -> tuple[float, float, float]:
        """Get voxel size in micrometers (X, Y, Z)"""
        x = self.pixel_size_x.to_micrometers() if self.pixel_size_x else 1.0
        y = self.pixel_size_y.to_micrometers() if self.pixel_size_y else 1.0
        z = self.pixel_size_z.to_micrometers() if self.pixel_size_z else 1.0
        return (x, y, z)

    def get_physical_dimensions_micrometers(self) -> tuple[float, float, float]:
        """Get total physical dimensions in micrometers (X, Y, Z)"""
        voxel_x, voxel_y, voxel_z = self.get_voxel_size_micrometers()
        return (
            self.size_x * voxel_x,
            self.size_y * voxel_y,
            self.size_z * voxel_z
        )

    def get_total_pixels(self) -> int:
        """Get total number of pixels in the image"""
        return self.size_x * self.size_y * self.size_z * self.size_c * self.size_t * self.size_p

    def get_memory_size_mb(self) -> float:
        """Estimate memory size in MB"""
        bytes_per_pixel = self.bits_per_pixel // 8
        total_bytes = self.get_total_pixels() * bytes_per_pixel
        return total_bytes / (1024 * 1024)

    def should_use_lazy_loading(self, threshold_mb: float = 1024) -> bool:
        """Determine if lazy loading should be used based on size"""
        return self.get_memory_size_mb() > threshold_mb

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "filename": self.filename,
            "file_format": self.file_format,
            "file_size_bytes": self.file_size_bytes,
            "dimensions": {
                "x": self.size_x,
                "y": self.size_y,
                "z": self.size_z,
                "c": self.size_c,
                "t": self.size_t,
                "p": self.size_p,
                "order": self.dimension_order,
            },
            "physical_size": {
                "x": self.pixel_size_x.dict() if self.pixel_size_x else None,
                "y": self.pixel_size_y.dict() if self.pixel_size_y else None,
                "z": self.pixel_size_z.dict() if self.pixel_size_z else None,
            },
            "voxel_size_um": {
                "x": self.get_voxel_size_micrometers()[0],
                "y": self.get_voxel_size_micrometers()[1],
                "z": self.get_voxel_size_micrometers()[2],
            },
            "physical_dimensions_um": {
                "x": self.get_physical_dimensions_micrometers()[0],
                "y": self.get_physical_dimensions_micrometers()[1],
                "z": self.get_physical_dimensions_micrometers()[2],
            },
            "pixel_type": {
                "dtype": self.dtype,
                "bits_per_pixel": self.bits_per_pixel,
                "is_signed": self.is_signed,
            },
            "channels": [ch.dict() for ch in self.channels],
            "objective": self.objective.dict() if self.objective else None,
            "microscope": self.microscope.dict() if self.microscope else None,
            "acquisition": {
                "date": self.acquisition_date.isoformat() if self.acquisition_date else None,
                "software": self.acquisition_software,
                "software_version": self.acquisition_software_version,
            },
            "time_series": {
                "increment": self.time_increment,
                "unit": self.time_unit,
            },
            "stage_positions": self.stage_positions,
            "memory_size_mb": self.get_memory_size_mb(),
            "use_lazy_loading": self.should_use_lazy_loading(),
            "vendor_metadata": self.vendor_metadata,
        }
