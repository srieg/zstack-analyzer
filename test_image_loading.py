#!/usr/bin/env python3
"""
Quick test script for microscopy image loading system.

Tests:
- Format detection
- Metadata extraction
- Image loading
- Thumbnail generation
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from core.processing.image_loader import (
    ImageLoader,
    ImageLoadError,
    UnsupportedFormatError,
    MissingDependencyError,
)
from core.processing.thumbnail import ThumbnailGenerator
from core.processing.metadata import ImageMetadata


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_section(text: str):
    """Print formatted section"""
    print(f"\n>>> {text}")


async def test_format_detection():
    """Test 1: Format detection and availability"""
    print_header("Test 1: Format Detection")

    loader = ImageLoader()

    print_section("Checking supported formats...")
    all_available = True

    for ext, (name, available, package) in loader.supported_formats.items():
        status = "✓" if available else "✗"
        print(f"  {status} {ext.ljust(6)} {name.ljust(12)} (requires {package})")
        if not available:
            all_available = False

    if all_available:
        print("\n✓ All format readers are installed and available!")
    else:
        print("\n⚠ Some format readers are missing. Install with:")
        print("  pip install tifffile aicspylibczi nd2 readlif")

    return all_available


async def test_error_handling():
    """Test 2: Error handling"""
    print_header("Test 2: Error Handling")

    loader = ImageLoader()

    print_section("Testing unsupported format...")
    try:
        await loader.get_metadata("test.xyz")
        print("✗ Should have raised UnsupportedFormatError")
    except UnsupportedFormatError as e:
        print(f"✓ Correctly raised UnsupportedFormatError: {e}")

    print_section("Testing non-existent file...")
    try:
        await loader.get_metadata("nonexistent.tif")
        print("✗ Should have raised FileNotFoundError")
    except FileNotFoundError as e:
        print(f"✓ Correctly raised FileNotFoundError")


async def test_with_sample_file():
    """Test 3: Create and load sample file"""
    print_header("Test 3: Sample File Creation and Loading")

    print_section("Creating synthetic TIFF file...")

    try:
        import numpy as np
        import tifffile
    except ImportError as e:
        print(f"✗ Missing required packages: {e}")
        print("  Install with: pip install numpy tifffile")
        return False

    # Create synthetic z-stack
    print("  - Generating synthetic Z-stack (3 channels, 10 slices, 256x256)...")
    data = np.random.randint(0, 65535, (3, 10, 256, 256), dtype=np.uint16)

    # Add some structure
    for z in range(10):
        for c in range(3):
            y, x = np.ogrid[:256, :256]
            center_y, center_x = 128, 128
            radius = 50 + z * 3
            mask = (x - center_x)**2 + (y - center_y)**2 < radius**2
            data[c, z, mask] = 50000 + c * 5000

    sample_path = Path("test_sample.tif")

    # Save with metadata
    print("  - Saving with metadata...")
    tifffile.imwrite(
        str(sample_path),
        data,
        metadata={
            'axes': 'CZYX',
            'spacing': 0.2,  # Z spacing in micrometers
        },
        resolution=(10.0, 10.0),  # 0.1 um/pixel
        imagej=True,
    )

    print(f"✓ Created {sample_path} ({sample_path.stat().st_size / 1024:.1f} KB)")

    # Test metadata extraction
    print_section("Testing metadata extraction...")
    loader = ImageLoader()

    try:
        metadata: ImageMetadata = await loader.get_metadata(str(sample_path))

        print(f"✓ Metadata extracted successfully!")
        print(f"  - Format: {metadata.file_format}")
        print(f"  - Dimensions: {metadata.size_x} x {metadata.size_y} x {metadata.size_z}")
        print(f"  - Channels: {metadata.size_c}")
        print(f"  - Data type: {metadata.dtype}")
        print(f"  - Bits per pixel: {metadata.bits_per_pixel}")

        voxel_size = metadata.get_voxel_size_micrometers()
        print(f"  - Voxel size (µm): {voxel_size[0]:.3f} x {voxel_size[1]:.3f} x {voxel_size[2]:.3f}")

        phys_dims = metadata.get_physical_dimensions_micrometers()
        print(f"  - Physical size (µm): {phys_dims[0]:.1f} x {phys_dims[1]:.1f} x {phys_dims[2]:.1f}")

        print(f"  - Memory size: {metadata.get_memory_size_mb():.2f} MB")
        print(f"  - Use lazy loading: {metadata.should_use_lazy_loading()}")

    except Exception as e:
        print(f"✗ Metadata extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test image loading
    print_section("Testing image loading...")

    try:
        image_data, metadata = await loader.load_image(str(sample_path), lazy=False)

        print(f"✓ Image loaded successfully!")
        print(f"  - Array shape: {image_data.shape}")
        print(f"  - Array dtype: {image_data.dtype}")
        print(f"  - Memory size: {image_data.nbytes / (1024 * 1024):.2f} MB")

    except Exception as e:
        print(f"✗ Image loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test thumbnail generation
    print_section("Testing thumbnail generation...")

    try:
        thumb_gen = ThumbnailGenerator(cache_dir="test_thumbnails")

        # Generate standard thumbnail
        thumbnail = await thumb_gen.generate_thumbnail(
            image_data,
            size=(256, 256),
        )
        thumb_path = Path("test_thumbnail.png")
        await thumb_gen.save_thumbnail(thumbnail, thumb_path)
        print(f"✓ Standard thumbnail saved to {thumb_path}")

        # Generate MIP
        mip = await thumb_gen.generate_mip_thumbnail(
            image_data,
            size=(256, 256),
            axis=0,
        )
        mip_path = Path("test_mip.png")
        await thumb_gen.save_thumbnail(mip, mip_path)
        print(f"✓ MIP thumbnail saved to {mip_path}")

        # Generate multi-view
        multi_view = await thumb_gen.generate_multi_view_thumbnail(
            image_data,
            size=(768, 256),
        )
        multi_path = Path("test_multiview.png")
        await thumb_gen.save_thumbnail(multi_view, multi_path)
        print(f"✓ Multi-view thumbnail saved to {multi_path}")

    except Exception as e:
        print(f"✗ Thumbnail generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print_section("Cleaning up test files...")
    sample_path.unlink()
    print(f"✓ Deleted {sample_path}")

    return True


async def main():
    """Run all tests"""
    print_header("Microscopy Image Loading System - Test Suite")

    # Test 1: Format detection
    all_formats_available = await test_format_detection()

    # Test 2: Error handling
    await test_error_handling()

    # Test 3: Sample file loading (only if formats available)
    if all_formats_available:
        success = await test_with_sample_file()
    else:
        print("\n⚠ Skipping sample file test due to missing dependencies")
        success = False

    # Summary
    print_header("Test Summary")

    if all_formats_available and success:
        print("\n✓ All tests passed!")
        print("\nNext steps:")
        print("  1. Start the server: uvicorn api.main:app --reload")
        print("  2. Test API: curl http://localhost:8000/api/images/formats/supported")
        print("  3. Upload a file: curl -X POST http://localhost:8000/api/images/upload -F 'file=@sample.tif'")
        return 0
    else:
        print("\n⚠ Some tests failed or dependencies are missing")
        print("\nInstall missing dependencies:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
