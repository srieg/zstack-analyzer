#!/usr/bin/env python3
"""
Quick test script to verify GPU module implementation.

Tests device detection, basic kernels, and integration with analyzer.
"""

import sys
import logging
import numpy as np
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_device_detection():
    """Test GPU device detection."""
    logger.info("=" * 60)
    logger.info("TEST 1: Device Detection")
    logger.info("=" * 60)

    from core.gpu.device_manager import DeviceManager

    dm = DeviceManager()

    logger.info(f"Device: {dm.device}")
    logger.info(f"Is GPU: {dm.is_gpu}")
    logger.info(f"Device info: {dm.device_info}")

    if dm.is_gpu:
        memory = dm.get_device_memory_info()
        logger.info(f"Total memory: {memory['total'] / 1e9:.2f} GB")
        logger.info(f"Available memory: {memory['available'] / 1e9:.2f} GB")

        max_dims = dm.estimate_max_volume_size()
        logger.info(f"Estimated max volume: {max_dims}")

    logger.info("✓ Device detection test passed\n")
    return True


def test_basic_kernels():
    """Test basic GPU kernels."""
    logger.info("=" * 60)
    logger.info("TEST 2: Basic Kernels")
    logger.info("=" * 60)

    from core.gpu import gaussian_blur_3d, sobel_3d, otsu_threshold

    # Create synthetic test volume
    volume = np.random.randn(50, 100, 100).astype(np.float32)
    volume = np.abs(volume)  # Make positive

    logger.info(f"Test volume shape: {volume.shape}")
    logger.info(f"Test volume dtype: {volume.dtype}")

    # Test Gaussian blur
    logger.info("\nTesting gaussian_blur_3d...")
    blurred = gaussian_blur_3d(volume, sigma=2.0)
    assert blurred.shape == volume.shape, "Shape mismatch after blur"
    logger.info(f"✓ Gaussian blur: {blurred.shape}")

    # Test Sobel edge detection
    logger.info("\nTesting sobel_3d...")
    edges = sobel_3d(volume)
    assert edges.shape[0] == volume.shape[0], "Z-dimension mismatch"
    logger.info(f"✓ Sobel edges: {edges.shape}")

    # Test Otsu thresholding
    logger.info("\nTesting otsu_threshold...")
    threshold_value, binary = otsu_threshold(volume)
    logger.info(f"✓ Otsu threshold: {threshold_value:.4f}")
    logger.info(f"  Binary mask shape: {binary.shape}")
    logger.info(f"  Foreground pixels: {binary.sum() / binary.size * 100:.1f}%")

    logger.info("\n✓ Basic kernels test passed\n")
    return True


def test_segmentation():
    """Test segmentation algorithms."""
    logger.info("=" * 60)
    logger.info("TEST 3: Segmentation")
    logger.info("=" * 60)

    from core.gpu import threshold_segmentation, blob_detection_3d

    # Create synthetic volume with blobs
    volume = np.zeros((50, 100, 100), dtype=np.float32)

    # Add some Gaussian blobs
    for _ in range(5):
        z, y, x = np.random.randint(10, 40), np.random.randint(20, 80), np.random.randint(20, 80)
        zz, yy, xx = np.ogrid[:50, :100, :100]
        blob = np.exp(-((zz - z)**2 + (yy - y)**2 + (xx - x)**2) / (10**2))
        volume += blob * np.random.uniform(0.5, 1.0)

    # Add noise
    volume += np.random.randn(*volume.shape) * 0.1
    volume = np.clip(volume, 0, None)

    logger.info(f"Synthetic volume: {volume.shape}, range: [{volume.min():.3f}, {volume.max():.3f}]")

    # Test threshold segmentation
    logger.info("\nTesting threshold_segmentation...")
    labels, metadata = threshold_segmentation(
        volume,
        method="otsu",
        min_object_size=50
    )
    logger.info(f"✓ Threshold segmentation:")
    logger.info(f"  Objects detected: {metadata['num_objects']}")
    logger.info(f"  Threshold: {metadata['threshold']:.4f}")

    # Test blob detection
    logger.info("\nTesting blob_detection_3d...")
    blobs = blob_detection_3d(
        volume,
        min_sigma=2.0,
        max_sigma=10.0,
        num_sigma=5,
        threshold=0.1
    )
    logger.info(f"✓ Blob detection:")
    logger.info(f"  Blobs detected: {len(blobs)}")
    if blobs:
        logger.info(f"  First blob: z={blobs[0][0]}, y={blobs[0][1]}, x={blobs[0][2]}, σ={blobs[0][3]:.2f}")

    logger.info("\n✓ Segmentation test passed\n")
    return True


def test_analysis():
    """Test analysis functions."""
    logger.info("=" * 60)
    logger.info("TEST 4: Analysis Functions")
    logger.info("=" * 60)

    from core.gpu import colocalization_analysis, intensity_statistics

    # Create two correlated channels
    np.random.seed(42)
    channel1 = np.random.randn(30, 64, 64).astype(np.float32)
    channel1 = np.abs(channel1)

    # Channel 2 partially correlated with channel 1
    channel2 = 0.7 * channel1 + 0.3 * np.random.randn(*channel1.shape).astype(np.float32)
    channel2 = np.abs(channel2)

    logger.info(f"Channel 1: {channel1.shape}, mean={channel1.mean():.3f}")
    logger.info(f"Channel 2: {channel2.shape}, mean={channel2.mean():.3f}")

    # Test colocalization
    logger.info("\nTesting colocalization_analysis...")
    coloc_results = colocalization_analysis(channel1, channel2)
    logger.info(f"✓ Colocalization:")
    logger.info(f"  Pearson R: {coloc_results['pearson_r']:.3f}")
    logger.info(f"  Manders M1: {coloc_results['manders_m1']:.3f}")
    logger.info(f"  Manders M2: {coloc_results['manders_m2']:.3f}")
    logger.info(f"  Overlap: {coloc_results['overlap_coefficient']:.3f}")

    # Test intensity statistics
    logger.info("\nTesting intensity_statistics...")
    stats = intensity_statistics(channel1)
    logger.info(f"✓ Intensity statistics:")
    logger.info(f"  Mean: {stats['mean']:.3f}")
    logger.info(f"  Std: {stats['std']:.3f}")
    logger.info(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}]")

    logger.info("\n✓ Analysis test passed\n")
    return True


def test_deconvolution():
    """Test deconvolution algorithms."""
    logger.info("=" * 60)
    logger.info("TEST 5: Deconvolution")
    logger.info("=" * 60)

    from core.gpu import generate_psf, richardson_lucy_deconvolution

    # Create synthetic blurred volume
    volume = np.zeros((30, 64, 64), dtype=np.float32)

    # Add a few point sources
    for _ in range(3):
        z, y, x = np.random.randint(10, 20), np.random.randint(20, 44), np.random.randint(20, 44)
        volume[z, y, x] = 1.0

    # Generate PSF
    logger.info("Generating Gaussian PSF...")
    psf = generate_psf(
        shape=(11, 11, 11),
        psf_type="gaussian",
        sigma=(2.0, 1.0, 1.0)
    )
    logger.info(f"✓ PSF generated: {psf.shape}, sum={psf.sum():.6f}")

    # Convolve to simulate blur
    from scipy.signal import fftconvolve
    blurred = fftconvolve(volume, psf, mode='same')

    logger.info(f"Original peaks: {(volume > 0.5).sum()}")
    logger.info(f"Blurred volume: mean={blurred.mean():.6f}, max={blurred.max():.6f}")

    # Test Richardson-Lucy deconvolution (only 3 iterations for speed)
    logger.info("\nTesting richardson_lucy_deconvolution...")
    deconvolved = richardson_lucy_deconvolution(
        blurred,
        psf,
        iterations=3,
        clip=True
    )
    logger.info(f"✓ Deconvolution completed")
    logger.info(f"  Deconvolved: mean={deconvolved.mean():.6f}, max={deconvolved.max():.6f}")

    logger.info("\n✓ Deconvolution test passed\n")
    return True


def test_analyzer_integration():
    """Test integration with ZStackAnalyzer."""
    logger.info("=" * 60)
    logger.info("TEST 6: Analyzer Integration")
    logger.info("=" * 60)

    from core.processing.analyzer import ZStackAnalyzer

    analyzer = ZStackAnalyzer()
    logger.info(f"✓ ZStackAnalyzer initialized")
    logger.info(f"  GPU device: {analyzer._get_gpu_device()}")
    logger.info(f"  Available algorithms: {list(analyzer.available_algorithms.keys())}")

    logger.info("\n✓ Analyzer integration test passed\n")
    return True


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 60)
    logger.info("GPU IMPLEMENTATION TEST SUITE")
    logger.info("=" * 60 + "\n")

    tests = [
        ("Device Detection", test_device_detection),
        ("Basic Kernels", test_basic_kernels),
        ("Segmentation", test_segmentation),
        ("Analysis Functions", test_analysis),
        ("Deconvolution", test_deconvolution),
        ("Analyzer Integration", test_analyzer_integration),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"✗ {name} failed: {e}", exc_info=True)
            results.append((name, False))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status:8} - {name}")

    logger.info("\n" + "=" * 60)
    logger.info(f"RESULT: {passed}/{total} tests passed")
    logger.info("=" * 60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
