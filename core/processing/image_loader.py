"""
Comprehensive microscopy image loader with support for multiple formats.

Supports:
- TIFF/BigTIFF (via tifffile)
- Zeiss CZI (via aicspylibczi)
- Nikon ND2 (via nd2)
- Leica LIF (via readlif)
- Lazy loading via dask for large files

Features:
- Rich metadata extraction
- Multi-channel, multi-position, time-series support
- Physical units and calibration
- Robust error handling
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union, List
import logging
from datetime import datetime
from functools import partial

import numpy as np
import dask.array as da

# Microscopy format readers
try:
    import tifffile
    TIFFFILE_AVAILABLE = True
except ImportError:
    TIFFFILE_AVAILABLE = False

try:
    from aicspylibczi import CziFile
    CZI_AVAILABLE = True
except ImportError:
    CZI_AVAILABLE = False

try:
    import nd2
    ND2_AVAILABLE = True
except ImportError:
    ND2_AVAILABLE = False

try:
    from readlif.reader import LifFile
    LIF_AVAILABLE = True
except ImportError:
    LIF_AVAILABLE = False

from core.processing.metadata import (
    ImageMetadata,
    ChannelInfo,
    ObjectiveInfo,
    MicroscopeInfo,
    PhysicalSize,
    PhysicalUnit,
    TimeUnit,
    DimensionOrder,
)

logger = logging.getLogger(__name__)


class ImageLoadError(Exception):
    """Custom exception for image loading errors"""
    pass


class UnsupportedFormatError(ImageLoadError):
    """Raised when file format is not supported"""
    pass


class MissingDependencyError(ImageLoadError):
    """Raised when required library is not installed"""
    pass


class ImageLoader:
    """
    Comprehensive image loader for microscopy file formats.

    Automatically selects the appropriate reader based on file extension
    and provides unified interface for metadata extraction and image loading.
    """

    # File size threshold for lazy loading (1GB)
    LAZY_LOAD_THRESHOLD_BYTES = 1024 * 1024 * 1024

    def __init__(self):
        self.supported_formats = {
            '.tif': ('TIFF', TIFFFILE_AVAILABLE, 'tifffile'),
            '.tiff': ('TIFF', TIFFFILE_AVAILABLE, 'tifffile'),
            '.czi': ('CZI', CZI_AVAILABLE, 'aicspylibczi'),
            '.nd2': ('ND2', ND2_AVAILABLE, 'nd2'),
            '.lif': ('LIF', LIF_AVAILABLE, 'readlif'),
        }

    def _check_format_support(self, file_path: str) -> Tuple[str, str]:
        """
        Check if file format is supported and library is available.

        Returns:
            Tuple of (format_name, required_package)

        Raises:
            UnsupportedFormatError: If format not supported
            MissingDependencyError: If required library not installed
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension not in self.supported_formats:
            raise UnsupportedFormatError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(self.supported_formats.keys())}"
            )

        format_name, is_available, package = self.supported_formats[extension]

        if not is_available:
            raise MissingDependencyError(
                f"Library '{package}' is required to read {format_name} files. "
                f"Install it with: pip install {package}"
            )

        return format_name, package

    async def get_metadata(self, file_path: str) -> ImageMetadata:
        """
        Extract comprehensive metadata from microscopy file.

        Args:
            file_path: Path to the image file

        Returns:
            ImageMetadata object with standardized metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            ImageLoadError: If metadata extraction fails
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ImageLoadError(f"Path is not a file: {file_path}")

        try:
            format_name, _ = self._check_format_support(file_path)
            extension = path.suffix.lower()

            # Run metadata extraction in executor to avoid blocking
            loop = asyncio.get_event_loop()

            if extension in {'.tif', '.tiff'}:
                metadata = await loop.run_in_executor(None, self._get_tiff_metadata, file_path)
            elif extension == '.czi':
                metadata = await loop.run_in_executor(None, self._get_czi_metadata, file_path)
            elif extension == '.nd2':
                metadata = await loop.run_in_executor(None, self._get_nd2_metadata, file_path)
            elif extension == '.lif':
                metadata = await loop.run_in_executor(None, self._get_lif_metadata, file_path)
            else:
                raise UnsupportedFormatError(f"No metadata reader for {extension}")

            return metadata

        except (UnsupportedFormatError, MissingDependencyError):
            raise
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}", exc_info=True)
            raise ImageLoadError(f"Metadata extraction failed: {str(e)}") from e

    async def load_image(
        self,
        file_path: str,
        lazy: bool = None,
        position: int = 0,
        timepoint: int = 0,
    ) -> Tuple[Union[np.ndarray, da.Array], ImageMetadata]:
        """
        Load image data from microscopy file.

        Args:
            file_path: Path to the image file
            lazy: Force lazy loading (dask array). If None, auto-decide based on size
            position: Position/scene index for multi-position data
            timepoint: Time point index for time series

        Returns:
            Tuple of (image_array, metadata)
            Image array is numpy array or dask array depending on lazy parameter

        Raises:
            ImageLoadError: If loading fails
        """
        path = Path(file_path)

        try:
            # Get metadata first
            metadata = await self.get_metadata(file_path)

            # Determine if lazy loading should be used
            if lazy is None:
                lazy = metadata.should_use_lazy_loading(self.LAZY_LOAD_THRESHOLD_BYTES / (1024 * 1024))

            # Run loading in executor
            loop = asyncio.get_event_loop()
            extension = path.suffix.lower()

            load_func = partial(
                self._load_by_format,
                file_path=file_path,
                extension=extension,
                lazy=lazy,
                position=position,
                timepoint=timepoint,
            )

            image_data = await loop.run_in_executor(None, load_func)

            return image_data, metadata

        except Exception as e:
            logger.error(f"Failed to load image from {file_path}: {e}", exc_info=True)
            raise ImageLoadError(f"Image loading failed: {str(e)}") from e

    def _load_by_format(
        self,
        file_path: str,
        extension: str,
        lazy: bool,
        position: int,
        timepoint: int,
    ) -> Union[np.ndarray, da.Array]:
        """Load image using appropriate format reader"""
        if extension in {'.tif', '.tiff'}:
            return self._load_tiff(file_path, lazy)
        elif extension == '.czi':
            return self._load_czi(file_path, lazy, position, timepoint)
        elif extension == '.nd2':
            return self._load_nd2(file_path, lazy, position, timepoint)
        elif extension == '.lif':
            return self._load_lif(file_path, lazy, position)
        else:
            raise UnsupportedFormatError(f"No loader for {extension}")

    # TIFF Format
    def _get_tiff_metadata(self, file_path: str) -> ImageMetadata:
        """Extract metadata from TIFF/BigTIFF file"""
        path = Path(file_path)

        with tifffile.TiffFile(file_path) as tif:
            # Get first series
            series = tif.series[0]

            # Get basic dimensions
            shape = series.shape
            axes = series.axes

            # Parse axes string to get dimensions
            dims = self._parse_tiff_axes(axes, shape)

            # Get pixel type
            dtype = series.dtype
            bits_per_pixel = dtype.itemsize * 8

            # Extract physical spacing from metadata
            pixel_sizes = self._extract_tiff_pixel_sizes(tif)

            # Extract channel information
            channels = self._extract_tiff_channels(tif, dims['c'])

            # Extract microscope information
            objective, microscope = self._extract_tiff_hardware_info(tif)

            # Get acquisition time
            acquisition_date = self._extract_tiff_acquisition_date(tif)

            return ImageMetadata(
                filename=path.name,
                file_format="TIFF",
                file_size_bytes=path.stat().st_size,
                size_x=dims['x'],
                size_y=dims['y'],
                size_z=dims['z'],
                size_c=dims['c'],
                size_t=dims['t'],
                size_p=1,  # TIFF typically single position
                dimension_order=self._get_tiff_dimension_order(axes),
                pixel_size_x=pixel_sizes.get('x'),
                pixel_size_y=pixel_sizes.get('y'),
                pixel_size_z=pixel_sizes.get('z'),
                dtype=str(dtype),
                bits_per_pixel=bits_per_pixel,
                is_signed=np.issubdtype(dtype, np.signedinteger),
                channels=channels,
                objective=objective,
                microscope=microscope,
                acquisition_date=acquisition_date,
                vendor_metadata=self._extract_tiff_vendor_metadata(tif),
            )

    def _parse_tiff_axes(self, axes: str, shape: tuple) -> Dict[str, int]:
        """Parse TIFF axes string and shape"""
        dims = {'x': 1, 'y': 1, 'z': 1, 'c': 1, 't': 1}

        axes_map = {
            'X': 'x', 'Y': 'y', 'Z': 'z',
            'C': 'c', 'S': 'c',  # S is samples (channels)
            'T': 't', 'I': 'z',  # I is images (z-stack)
        }

        for axis, size in zip(axes.upper(), shape):
            if axis in axes_map:
                dims[axes_map[axis]] = size

        return dims

    def _get_tiff_dimension_order(self, axes: str) -> DimensionOrder:
        """Determine dimension order from TIFF axes"""
        axes_upper = axes.upper().replace('S', 'C').replace('I', 'Z')

        order_map = {
            'TZCYX': DimensionOrder.TZCYX,
            'TZYXC': DimensionOrder.TZYXC,
            'ZCYX': DimensionOrder.ZCYX,
            'ZYXC': DimensionOrder.ZYXC,
            'CYX': DimensionOrder.CYX,
            'YXC': DimensionOrder.YXC,
            'ZYX': DimensionOrder.ZYX,
        }

        # Try to match order
        for pattern, order in order_map.items():
            if all(c in axes_upper for c in pattern):
                return order

        # Default to ZCYX
        return DimensionOrder.ZCYX

    def _extract_tiff_pixel_sizes(self, tif: tifffile.TiffFile) -> Dict[str, PhysicalSize]:
        """Extract pixel sizes from TIFF metadata"""
        pixel_sizes = {}

        try:
            # Try OME-XML metadata first
            if tif.is_ome:
                ome_metadata = tif.ome_metadata
                # Parse OME-XML for PhysicalSizeX, PhysicalSizeY, PhysicalSizeZ
                # This is simplified - full OME-XML parsing would be more complex
                pass

            # Try ImageJ metadata
            if tif.is_imagej:
                ij_metadata = tif.imagej_metadata
                if ij_metadata:
                    # ImageJ stores spacing in various ways
                    if 'spacing' in ij_metadata:
                        pixel_sizes['z'] = PhysicalSize(
                            value=ij_metadata['spacing'],
                            unit=PhysicalUnit.MICROMETER
                        )

            # Try reading from tags
            page = tif.pages[0]
            tags = page.tags

            # X and Y resolution
            if 'XResolution' in tags and 'YResolution' in tags:
                x_res = tags['XResolution'].value
                y_res = tags['YResolution'].value

                # Resolution is pixels per unit
                if isinstance(x_res, tuple):
                    x_res = x_res[0] / x_res[1]
                if isinstance(y_res, tuple):
                    y_res = y_res[0] / y_res[1]

                # Convert to micrometers per pixel
                if x_res > 0:
                    pixel_sizes['x'] = PhysicalSize(value=1.0 / x_res, unit=PhysicalUnit.MICROMETER)
                if y_res > 0:
                    pixel_sizes['y'] = PhysicalSize(value=1.0 / y_res, unit=PhysicalUnit.MICROMETER)

        except Exception as e:
            logger.warning(f"Failed to extract pixel sizes from TIFF: {e}")

        return pixel_sizes

    def _extract_tiff_channels(self, tif: tifffile.TiffFile, num_channels: int) -> List[ChannelInfo]:
        """Extract channel information from TIFF"""
        channels = []

        for i in range(num_channels):
            channels.append(ChannelInfo(
                name=f"Channel {i + 1}",
            ))

        return channels

    def _extract_tiff_hardware_info(
        self, tif: tifffile.TiffFile
    ) -> Tuple[Optional[ObjectiveInfo], Optional[MicroscopeInfo]]:
        """Extract hardware information from TIFF"""
        objective = None
        microscope = None

        # Try to extract from ImageJ or OME metadata
        if tif.is_imagej:
            ij_metadata = tif.imagej_metadata
            if ij_metadata and 'Info' in ij_metadata:
                # Parse info string for objective data
                pass

        return objective, microscope

    def _extract_tiff_acquisition_date(self, tif: tifffile.TiffFile) -> Optional[datetime]:
        """Extract acquisition date from TIFF"""
        try:
            page = tif.pages[0]
            if 'DateTime' in page.tags:
                date_str = page.tags['DateTime'].value
                # Parse TIFF DateTime format (YYYY:MM:DD HH:MM:SS)
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        except Exception as e:
            logger.warning(f"Failed to parse TIFF acquisition date: {e}")

        return None

    def _extract_tiff_vendor_metadata(self, tif: tifffile.TiffFile) -> Dict[str, Any]:
        """Extract vendor-specific metadata from TIFF"""
        vendor_metadata = {}

        if tif.is_ome:
            vendor_metadata['ome'] = True

        if tif.is_imagej:
            vendor_metadata['imagej'] = True
            vendor_metadata['imagej_metadata'] = tif.imagej_metadata

        return vendor_metadata

    def _load_tiff(self, file_path: str, lazy: bool) -> Union[np.ndarray, da.Array]:
        """Load TIFF image data"""
        if lazy:
            # Use dask for lazy loading
            return da.from_delayed(
                dask.delayed(tifffile.imread)(file_path),
                shape=self._get_tiff_shape(file_path),
                dtype=self._get_tiff_dtype(file_path),
            )
        else:
            return tifffile.imread(file_path)

    def _get_tiff_shape(self, file_path: str) -> tuple:
        """Get TIFF shape without loading data"""
        with tifffile.TiffFile(file_path) as tif:
            return tif.series[0].shape

    def _get_tiff_dtype(self, file_path: str) -> np.dtype:
        """Get TIFF dtype without loading data"""
        with tifffile.TiffFile(file_path) as tif:
            return tif.series[0].dtype

    # CZI Format
    def _get_czi_metadata(self, file_path: str) -> ImageMetadata:
        """Extract metadata from Zeiss CZI file"""
        path = Path(file_path)

        with CziFile(file_path) as czi:
            # Get dimensions
            dims = czi.dims_shape()
            size_dict = {dim: size for dim, size in dims}

            # Extract physical spacing
            pixel_sizes = {}
            metadata_xml = czi.meta
            # Parse XML for physical sizes
            # Simplified - full XML parsing would extract actual values

            # Get pixel type
            pixel_type = czi.pixel_type
            dtype = self._czi_pixel_type_to_numpy(pixel_type)
            bits_per_pixel = dtype.itemsize * 8

            # Extract channel information
            channels = self._extract_czi_channels(czi)

            return ImageMetadata(
                filename=path.name,
                file_format="CZI",
                file_size_bytes=path.stat().st_size,
                size_x=size_dict.get('X', 1),
                size_y=size_dict.get('Y', 1),
                size_z=size_dict.get('Z', 1),
                size_c=size_dict.get('C', 1),
                size_t=size_dict.get('T', 1),
                size_p=size_dict.get('S', 1),  # S is scenes/positions
                dimension_order=DimensionOrder.TZCYX,
                dtype=str(dtype),
                bits_per_pixel=bits_per_pixel,
                channels=channels,
                vendor_metadata={'czi_metadata': str(metadata_xml)[:1000]},
            )

    def _czi_pixel_type_to_numpy(self, pixel_type: str) -> np.dtype:
        """Convert CZI pixel type to numpy dtype"""
        type_map = {
            'Gray8': np.uint8,
            'Gray16': np.uint16,
            'Gray32Float': np.float32,
            'Bgr24': np.uint8,
            'Bgr48': np.uint16,
        }
        return np.dtype(type_map.get(pixel_type, np.uint16))

    def _extract_czi_channels(self, czi: CziFile) -> List[ChannelInfo]:
        """Extract channel information from CZI"""
        channels = []
        dims = czi.dims_shape()
        num_channels = next((size for dim, size in dims if dim == 'C'), 1)

        for i in range(num_channels):
            channels.append(ChannelInfo(name=f"Channel {i + 1}"))

        return channels

    def _load_czi(
        self, file_path: str, lazy: bool, position: int, timepoint: int
    ) -> Union[np.ndarray, da.Array]:
        """Load CZI image data"""
        with CziFile(file_path) as czi:
            # Read specific position and timepoint
            if lazy:
                # For lazy loading, return a dask array
                # This is simplified - proper implementation would create dask chunks
                data = czi.read_image(S=position, T=timepoint)
                return da.from_array(data, chunks='auto')
            else:
                return czi.read_image(S=position, T=timepoint)

    # ND2 Format
    def _get_nd2_metadata(self, file_path: str) -> ImageMetadata:
        """Extract metadata from Nikon ND2 file"""
        path = Path(file_path)

        with nd2.ND2File(file_path) as f:
            # Get dimensions
            shape = f.shape
            ndim = len(shape)

            # ND2 shape is typically (T, Z, C, Y, X) or subset
            dims = self._parse_nd2_dimensions(f, shape)

            # Get pixel sizes
            pixel_sizes = {}
            if f.voxel_size():
                voxel = f.voxel_size()
                if voxel.x:
                    pixel_sizes['x'] = PhysicalSize(value=voxel.x, unit=PhysicalUnit.MICROMETER)
                if voxel.y:
                    pixel_sizes['y'] = PhysicalSize(value=voxel.y, unit=PhysicalUnit.MICROMETER)
                if voxel.z:
                    pixel_sizes['z'] = PhysicalSize(value=voxel.z, unit=PhysicalUnit.MICROMETER)

            # Extract channel information
            channels = self._extract_nd2_channels(f)

            # Get dtype
            dtype = f.dtype
            bits_per_pixel = dtype.itemsize * 8

            return ImageMetadata(
                filename=path.name,
                file_format="ND2",
                file_size_bytes=path.stat().st_size,
                size_x=dims['x'],
                size_y=dims['y'],
                size_z=dims['z'],
                size_c=dims['c'],
                size_t=dims['t'],
                size_p=1,
                dimension_order=DimensionOrder.TZCYX,
                pixel_size_x=pixel_sizes.get('x'),
                pixel_size_y=pixel_sizes.get('y'),
                pixel_size_z=pixel_sizes.get('z'),
                dtype=str(dtype),
                bits_per_pixel=bits_per_pixel,
                channels=channels,
                vendor_metadata={'nd2_attributes': str(f.attributes)[:1000]},
            )

    def _parse_nd2_dimensions(self, f: nd2.ND2File, shape: tuple) -> Dict[str, int]:
        """Parse ND2 dimensions"""
        dims = {'x': shape[-1], 'y': shape[-2], 'z': 1, 'c': 1, 't': 1}

        # ND2 typically uses (T, Z, C, Y, X) or subset
        if len(shape) >= 3:
            dims['c'] = shape[-3]
        if len(shape) >= 4:
            dims['z'] = shape[-4]
        if len(shape) >= 5:
            dims['t'] = shape[-5]

        return dims

    def _extract_nd2_channels(self, f: nd2.ND2File) -> List[ChannelInfo]:
        """Extract channel information from ND2"""
        channels = []

        try:
            if hasattr(f, 'metadata') and f.metadata:
                channel_meta = f.metadata.channels
                for ch in channel_meta:
                    channels.append(ChannelInfo(
                        name=ch.channel.name if hasattr(ch.channel, 'name') else f"Channel {len(channels) + 1}",
                    ))
        except Exception as e:
            logger.warning(f"Failed to extract ND2 channel info: {e}")

        if not channels:
            # Fallback
            channels.append(ChannelInfo(name="Channel 1"))

        return channels

    def _load_nd2(
        self, file_path: str, lazy: bool, position: int, timepoint: int
    ) -> Union[np.ndarray, da.Array]:
        """Load ND2 image data"""
        with nd2.ND2File(file_path) as f:
            if lazy:
                return f.to_dask()
            else:
                return f.asarray()

    # LIF Format
    def _get_lif_metadata(self, file_path: str) -> ImageMetadata:
        """Extract metadata from Leica LIF file"""
        path = Path(file_path)

        lif = LifFile(file_path)
        # LIF files contain multiple images
        img_list = [img for img in lif.get_iter_image()]

        if not img_list:
            raise ImageLoadError("No images found in LIF file")

        # Use first image
        img = img_list[0]

        return ImageMetadata(
            filename=path.name,
            file_format="LIF",
            file_size_bytes=path.stat().st_size,
            size_x=img.dims.x,
            size_y=img.dims.y,
            size_z=img.dims.z,
            size_c=img.channels,
            size_t=img.dims.t,
            size_p=len(img_list),
            dimension_order=DimensionOrder.ZCYX,
            dtype="uint8",  # LIF typically 8-bit
            bits_per_pixel=8,
            channels=[ChannelInfo(name=f"Channel {i+1}") for i in range(img.channels)],
            vendor_metadata={'lif_image_count': len(img_list)},
        )

    def _load_lif(self, file_path: str, lazy: bool, position: int) -> Union[np.ndarray, da.Array]:
        """Load LIF image data"""
        lif = LifFile(file_path)
        img_list = [img for img in lif.get_iter_image()]

        if position >= len(img_list):
            raise ImageLoadError(f"Position {position} not available in LIF file")

        img = img_list[position]

        # Read all frames
        frames = []
        for frame in img.get_iter_t():
            frames.append(np.array(frame))

        data = np.stack(frames) if len(frames) > 1 else frames[0]

        if lazy:
            return da.from_array(data, chunks='auto')
        else:
            return data
