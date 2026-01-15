"""
Thumbnail generation for microscopy images.

Features:
- Efficient preview generation
- Max intensity projection (MIP)
- Multi-channel composite rendering
- Disk caching
- Multiple output sizes
"""

import asyncio
from pathlib import Path
from typing import Optional, Tuple, Union, List
import logging
import hashlib
from io import BytesIO

import numpy as np
from PIL import Image
import dask.array as da

logger = logging.getLogger(__name__)


class ThumbnailGenerator:
    """
    Generate and cache thumbnail images for microscopy data.

    Supports:
    - Single slice thumbnails
    - Maximum intensity projections (MIP)
    - Multi-channel composite images
    - Automatic contrast adjustment
    - Disk caching
    """

    def __init__(self, cache_dir: str = "thumbnails"):
        """
        Initialize thumbnail generator.

        Args:
            cache_dir: Directory for caching thumbnails
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)

    def _get_cache_path(
        self,
        file_path: str,
        thumbnail_type: str,
        size: Tuple[int, int],
        z_slice: Optional[int] = None,
        channels: Optional[List[int]] = None,
    ) -> Path:
        """Generate cache file path based on parameters"""
        # Create a unique hash for the thumbnail parameters
        params = f"{file_path}_{thumbnail_type}_{size}_{z_slice}_{channels}"
        cache_hash = hashlib.md5(params.encode()).hexdigest()

        return self.cache_dir / f"{cache_hash}.png"

    async def generate_thumbnail(
        self,
        image_data: Union[np.ndarray, da.Array],
        size: Tuple[int, int] = (256, 256),
        z_slice: Optional[int] = None,
        channels: Optional[List[int]] = None,
        normalize: bool = True,
    ) -> Image.Image:
        """
        Generate thumbnail from image data.

        Args:
            image_data: Image array (Z, C, Y, X) or (Z, Y, X) or (C, Y, X) or (Y, X)
            size: Target thumbnail size (width, height)
            z_slice: Specific Z slice (None for MIP)
            channels: List of channels to include (None for all)
            normalize: Apply automatic contrast normalization

        Returns:
            PIL Image object
        """
        loop = asyncio.get_event_loop()

        # Process in executor to avoid blocking
        thumbnail = await loop.run_in_executor(
            None,
            self._generate_thumbnail_sync,
            image_data,
            size,
            z_slice,
            channels,
            normalize,
        )

        return thumbnail

    def _generate_thumbnail_sync(
        self,
        image_data: Union[np.ndarray, da.Array],
        size: Tuple[int, int],
        z_slice: Optional[int],
        channels: Optional[List[int]],
        normalize: bool,
    ) -> Image.Image:
        """Synchronous thumbnail generation (runs in executor)"""
        # Convert dask array to numpy if needed
        if isinstance(image_data, da.Array):
            image_data = image_data.compute()

        # Normalize dimensions to (C, Z, Y, X)
        image_data = self._normalize_dimensions(image_data)

        # Select Z slice or compute MIP
        if z_slice is not None:
            # Single slice
            slice_data = image_data[:, z_slice, :, :]
        else:
            # Maximum intensity projection
            slice_data = np.max(image_data, axis=1)

        # Select channels
        if channels is not None:
            slice_data = slice_data[channels, :, :]

        # Create composite image
        composite = self._create_composite(slice_data, normalize)

        # Resize to thumbnail size
        thumbnail = Image.fromarray(composite)
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)

        return thumbnail

    def _normalize_dimensions(self, data: np.ndarray) -> np.ndarray:
        """
        Normalize array to (C, Z, Y, X) format.

        Handles:
        - (Y, X) -> (1, 1, Y, X)
        - (Z, Y, X) -> (1, Z, Y, X)
        - (C, Y, X) -> (C, 1, Y, X)
        - (Z, C, Y, X) -> (C, Z, Y, X)
        - (C, Z, Y, X) -> (C, Z, Y, X)
        """
        if data.ndim == 2:
            # Grayscale single slice
            return data[np.newaxis, np.newaxis, :, :]
        elif data.ndim == 3:
            # Could be (Z, Y, X) or (C, Y, X)
            # Heuristic: if first dim is small (<10), assume channels
            if data.shape[0] < 10:
                # (C, Y, X)
                return data[:, np.newaxis, :, :]
            else:
                # (Z, Y, X)
                return data[np.newaxis, :, :, :]
        elif data.ndim == 4:
            # (Z, C, Y, X) or (C, Z, Y, X) or (T, Z, Y, X)
            # Heuristic: smaller first dimension is likely channels
            if data.shape[0] < data.shape[1]:
                # (C, Z, Y, X) - already correct
                return data
            else:
                # (Z, C, Y, X) - swap axes
                return np.transpose(data, (1, 0, 2, 3))
        elif data.ndim == 5:
            # (T, C, Z, Y, X) or similar - take first timepoint
            return data[0, :, :, :, :]
        else:
            raise ValueError(f"Unsupported number of dimensions: {data.ndim}")

    def _create_composite(self, data: np.ndarray, normalize: bool) -> np.ndarray:
        """
        Create RGB composite from multi-channel data.

        Args:
            data: Channel data (C, Y, X)
            normalize: Apply contrast normalization

        Returns:
            RGB image (Y, X, 3) as uint8
        """
        num_channels = data.shape[0]

        if num_channels == 1:
            # Grayscale
            channel_data = data[0, :, :]
            if normalize:
                channel_data = self._normalize_contrast(channel_data)
            else:
                channel_data = self._scale_to_uint8(channel_data)

            # Convert to RGB by repeating
            return np.stack([channel_data] * 3, axis=-1)

        elif num_channels == 2:
            # Two channels: map to green and magenta
            green = self._normalize_contrast(data[0, :, :]) if normalize else self._scale_to_uint8(data[0, :, :])
            magenta = self._normalize_contrast(data[1, :, :]) if normalize else self._scale_to_uint8(data[1, :, :])

            rgb = np.stack([
                magenta,  # R
                green,    # G
                magenta,  # B (for magenta)
            ], axis=-1)

            return rgb

        elif num_channels == 3:
            # Three channels: map to RGB
            channels_processed = []
            for i in range(3):
                ch = data[i, :, :]
                if normalize:
                    ch = self._normalize_contrast(ch)
                else:
                    ch = self._scale_to_uint8(ch)
                channels_processed.append(ch)

            return np.stack(channels_processed, axis=-1)

        else:
            # More than 3 channels: use first 3
            logger.warning(f"Image has {num_channels} channels, using first 3 for composite")
            return self._create_composite(data[:3, :, :], normalize)

    def _normalize_contrast(self, data: np.ndarray) -> np.ndarray:
        """
        Normalize contrast using percentile-based stretching.

        Uses 1st and 99th percentiles to avoid outliers.
        """
        p1, p99 = np.percentile(data, [1, 99])

        if p99 == p1:
            # Constant image
            return np.zeros_like(data, dtype=np.uint8)

        # Stretch to 0-255 range
        normalized = np.clip((data - p1) / (p99 - p1) * 255, 0, 255)

        return normalized.astype(np.uint8)

    def _scale_to_uint8(self, data: np.ndarray) -> np.ndarray:
        """Scale data to uint8 range without normalization"""
        # Get data type range
        if data.dtype == np.uint8:
            return data
        elif data.dtype == np.uint16:
            return (data / 256).astype(np.uint8)
        elif data.dtype == np.float32 or data.dtype == np.float64:
            # Assume 0-1 range
            return (np.clip(data, 0, 1) * 255).astype(np.uint8)
        else:
            # Generic normalization
            data_min = data.min()
            data_max = data.max()
            if data_max == data_min:
                return np.zeros_like(data, dtype=np.uint8)
            return ((data - data_min) / (data_max - data_min) * 255).astype(np.uint8)

    async def generate_mip_thumbnail(
        self,
        image_data: Union[np.ndarray, da.Array],
        size: Tuple[int, int] = (512, 512),
        channels: Optional[List[int]] = None,
        axis: int = 0,
    ) -> Image.Image:
        """
        Generate maximum intensity projection thumbnail.

        Args:
            image_data: Image array
            size: Target thumbnail size
            channels: Channels to include
            axis: Projection axis (0=Z, 1=Y, 2=X)

        Returns:
            PIL Image object
        """
        loop = asyncio.get_event_loop()

        thumbnail = await loop.run_in_executor(
            None,
            self._generate_mip_thumbnail_sync,
            image_data,
            size,
            channels,
            axis,
        )

        return thumbnail

    def _generate_mip_thumbnail_sync(
        self,
        image_data: Union[np.ndarray, da.Array],
        size: Tuple[int, int],
        channels: Optional[List[int]],
        axis: int,
    ) -> Image.Image:
        """Synchronous MIP thumbnail generation"""
        # Convert dask array to numpy if needed
        if isinstance(image_data, da.Array):
            image_data = image_data.compute()

        # Normalize dimensions
        image_data = self._normalize_dimensions(image_data)  # (C, Z, Y, X)

        # Adjust axis for normalized dimensions
        # axis 0 -> Z (axis 1 in normalized)
        # axis 1 -> Y (axis 2 in normalized)
        # axis 2 -> X (axis 3 in normalized)
        projection_axis = axis + 1

        # Select channels
        if channels is not None:
            image_data = image_data[channels, :, :, :]

        # Compute maximum intensity projection
        mip = np.max(image_data, axis=projection_axis)

        # mip shape is now (C, Y, X) if axis was Z
        # or (C, Z, X) if axis was Y, etc.

        # For non-Z projections, we need to handle dimensions differently
        if axis == 1:  # Y projection
            # Result is (C, Z, X) - treat Z as Y
            pass
        elif axis == 2:  # X projection
            # Result is (C, Z, Y) - treat as normal
            pass

        # Create composite
        composite = self._create_composite(mip, normalize=True)

        # Resize
        thumbnail = Image.fromarray(composite)
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)

        return thumbnail

    async def save_thumbnail(
        self,
        thumbnail: Image.Image,
        output_path: Union[str, Path],
        format: str = "PNG",
    ):
        """
        Save thumbnail to disk.

        Args:
            thumbnail: PIL Image object
            output_path: Output file path
            format: Image format (PNG, JPEG, etc.)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True, parents=True)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, thumbnail.save, str(output_path), format)

    async def get_thumbnail_bytes(
        self,
        thumbnail: Image.Image,
        format: str = "PNG",
    ) -> bytes:
        """
        Get thumbnail as bytes.

        Args:
            thumbnail: PIL Image object
            format: Image format

        Returns:
            Image bytes
        """
        loop = asyncio.get_event_loop()

        def _save_to_bytes():
            buffer = BytesIO()
            thumbnail.save(buffer, format=format)
            return buffer.getvalue()

        return await loop.run_in_executor(None, _save_to_bytes)

    async def generate_multi_view_thumbnail(
        self,
        image_data: Union[np.ndarray, da.Array],
        size: Tuple[int, int] = (768, 256),
    ) -> Image.Image:
        """
        Generate multi-view thumbnail showing XY, XZ, and YZ projections.

        Args:
            image_data: Image array
            size: Total thumbnail size (width, height)

        Returns:
            PIL Image with three views side by side
        """
        # Calculate individual view size
        individual_width = size[0] // 3
        individual_size = (individual_width, size[1])

        # Generate three projections
        xy_thumb = await self.generate_mip_thumbnail(image_data, individual_size, axis=0)  # Z projection
        xz_thumb = await self.generate_mip_thumbnail(image_data, individual_size, axis=1)  # Y projection
        yz_thumb = await self.generate_mip_thumbnail(image_data, individual_size, axis=2)  # X projection

        # Combine horizontally
        combined = Image.new('RGB', size)
        combined.paste(xy_thumb, (0, 0))
        combined.paste(xz_thumb, (individual_width, 0))
        combined.paste(yz_thumb, (individual_width * 2, 0))

        return combined

    def clear_cache(self, file_path: Optional[str] = None):
        """
        Clear thumbnail cache.

        Args:
            file_path: Clear cache for specific file, or None to clear all
        """
        if file_path is None:
            # Clear all cached thumbnails
            for cached_file in self.cache_dir.glob("*.png"):
                cached_file.unlink()
            logger.info(f"Cleared all thumbnail cache in {self.cache_dir}")
        else:
            # Clear cache for specific file (all variants)
            # This would require tracking which cache files belong to which source file
            # For simplicity, we'll clear all if file_path is provided
            logger.warning("Selective cache clearing not implemented, clearing all cache")
            self.clear_cache()
