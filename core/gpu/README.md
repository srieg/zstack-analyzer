# GPU-Accelerated Microscopy Analysis Module

Production-quality GPU acceleration for 3D confocal microscopy analysis using **tinygrad**.

## Overview

This module implements state-of-the-art algorithms for microscopy image processing, optimized for GPU execution with support for both CUDA (NVIDIA) and Metal (Apple Silicon/AMD on macOS).

### Key Features

- **Device-agnostic**: Automatically detects and utilizes CUDA or Metal GPUs
- **Production-ready**: Comprehensive error handling, logging, and benchmarking
- **Real-time progress**: Callbacks for UI integration
- **Memory-efficient**: Optimized for large 3D volumes
- **Type-safe**: Full type annotations for Python 3.11+

## Module Structure

```
core/gpu/
├── __init__.py              # Public API exports
├── device_manager.py        # GPU device detection and management
├── kernels.py              # Core image processing kernels
├── segmentation.py         # Segmentation algorithms
├── analysis.py             # Quantitative analysis functions
├── deconvolution.py        # Deconvolution algorithms
└── README.md               # This file
```

## Quick Start

```python
from core.gpu import (
    DeviceManager,
    gaussian_blur_3d,
    threshold_segmentation,
    colocalization_analysis,
    richardson_lucy_deconvolution,
)

# Check GPU availability
device_manager = DeviceManager()
print(f"Using device: {device_manager.device}")  # CUDA, METAL, or CPU

# Load your 3D microscopy data
volume = load_tiff_stack("data.tif")  # shape: (z, y, x)

# Apply Gaussian smoothing
smoothed = gaussian_blur_3d(volume, sigma=1.5)

# Segment cells/nuclei
labels, metadata = threshold_segmentation(
    smoothed,
    method="otsu",
    min_object_size=100,
    fill_holes=True
)

print(f"Detected {metadata['num_objects']} objects")

# Deconvolve using Richardson-Lucy
from core.gpu import generate_psf

psf = generate_psf(
    shape=(31, 31, 31),
    psf_type="airy",
    wavelength=0.52,      # green (μm)
    numerical_aperture=1.4
)

deconvolved = richardson_lucy_deconvolution(
    volume,
    psf,
    iterations=15
)
```

## Algorithms Implemented

### Core Kernels (`kernels.py`)

- **`gaussian_blur_3d`**: Separable 3D Gaussian blur (O(n·k) complexity)
- **`sobel_3d`**: 3D edge detection using Sobel operators
- **`otsu_threshold`**: GPU histogram-based Otsu thresholding
- **`connected_components_3d`**: 3D connected component labeling
- **`rolling_ball_background`**: Rolling ball background subtraction

### Segmentation (`segmentation.py`)

- **`threshold_segmentation`**: Otsu or manual thresholding with morphological cleanup
- **`watershed_segmentation_3d`**: Marker-based 3D watershed
- **`blob_detection_3d`**: Laplacian of Gaussian blob detection across scales
- **`UNet3D`**: Lightweight 3D U-Net architecture (requires training)

### Analysis (`analysis.py`)

- **`colocalization_analysis`**:
  - Pearson correlation coefficient
  - Manders' M1 and M2 coefficients
  - Overlap coefficient
  - Costes' automatic thresholding

- **`intensity_statistics`**: Global and per-object intensity stats

- **`object_measurements`**:
  - Volume and voxel count
  - 3D centroid coordinates
  - Bounding box dimensions
  - Surface area (marching cubes)
  - Sphericity index

- **`z_profile_analysis`**:
  - Z-axis intensity profiles
  - Photobleaching detection
  - Per-object Z-distribution

### Deconvolution (`deconvolution.py`)

- **`richardson_lucy_deconvolution`**: Iterative blind deconvolution (standard for fluorescence)
- **`wiener_deconvolution`**: Frequency-domain deconvolution with noise suppression
- **`generate_psf`**:
  - Gaussian PSF
  - Airy disk PSF (diffraction-limited)
  - Theoretical PSF from microscope parameters
- **`estimate_psf_from_beads`**: Empirical PSF from fluorescent bead images

## Device Management

The `DeviceManager` singleton handles automatic GPU detection:

```python
from core.gpu import DeviceManager

dm = DeviceManager()

# Device info
print(dm.device)              # "CUDA", "METAL", or "CPU"
print(dm.device_info)         # {'name': 'Apple M1 Max', 'type': 'METAL'}
print(dm.is_gpu)              # True if GPU available

# Memory management
memory = dm.get_device_memory_info()
print(f"Available: {memory['available'] / 1e9:.1f} GB")

# Estimate maximum volume size
max_dims = dm.estimate_max_volume_size()
print(f"Max volume: {max_dims}")  # (z, y, x) dimensions
```

## Performance Optimization

### Benchmarking

All algorithms include automatic benchmarking:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Will log: "gaussian_blur_3d completed in 234.56ms on METAL"
result = gaussian_blur_3d(volume, sigma=2.0)
```

### Progress Callbacks

Integrate with UI progress bars:

```python
def progress_callback(progress: float):
    """Progress from 0.0 to 1.0"""
    print(f"Progress: {progress * 100:.1f}%")

result = richardson_lucy_deconvolution(
    volume,
    psf,
    iterations=20,
    progress_callback=progress_callback
)
```

### Memory Considerations

For large volumes (>2GB):

1. **Check available memory**:
   ```python
   dm = DeviceManager()
   max_dims = dm.estimate_max_volume_size(safety_factor=0.7)
   ```

2. **Process in chunks** for very large datasets
3. **Use dtype=float32** (default) - float16 saves memory but reduces precision

## Integration with Analyzer

The main `ZStackAnalyzer` class automatically uses GPU acceleration:

```python
from core.processing.analyzer import ZStackAnalyzer

analyzer = ZStackAnalyzer()

# All algorithms use GPU when available
results = await analyzer.analyze(
    "image.tif",
    algorithm="segmentation_3d",
    parameters={
        "method": "watershed",
        "min_object_size": 200,
    }
)

print(f"GPU: {results['gpu_device']}")
print(f"Time: {results['processing_time_ms']}ms")
```

## Supported Algorithms

| Algorithm | Method | GPU | Progress | Async |
|-----------|--------|-----|----------|-------|
| Segmentation | Threshold/Watershed | ✅ | ✅ | ✅ |
| Blob Detection | LoG Multi-scale | ✅ | ✅ | ✅ |
| Colocalization | Pearson/Manders | ✅ | ✅ | ✅ |
| Intensity Stats | Per-object | ✅ | ✅ | ✅ |
| Object Measurements | 3D Morphology | ✅ | ✅ | ✅ |
| Deconvolution | Richardson-Lucy/Wiener | ✅ | ✅ | ✅ |
| Z-Profile | Photobleaching | ✅ | ✅ | ✅ |

## Development

### Requirements

- Python 3.11+
- tinygrad (latest)
- numpy >= 1.24
- scipy >= 1.11
- scikit-image >= 0.22

### Testing

```bash
pytest tests/test_gpu/ -v
```

### Adding New Algorithms

1. Implement in appropriate module (`kernels.py`, `segmentation.py`, etc.)
2. Add `@benchmark` decorator for performance logging
3. Include `progress_callback: Optional[Callable[[float], None]]` parameter
4. Export in `__init__.py`
5. Integrate with `ZStackAnalyzer` if user-facing

## Known Limitations

1. **Connected Components**: Currently uses scipy for labeling (hybrid GPU/CPU). Full GPU version planned.
2. **Morphological Operations**: Some operations fall back to scipy (e.g., rolling ball). Will be replaced with pure tinygrad.
3. **U-Net Training**: Model architecture defined but training loop not implemented. Use pretrained models or implement training.

## Future Enhancements

- [ ] Full GPU connected components (parallel label propagation)
- [ ] Pure tinygrad morphological operations
- [ ] Multi-GPU support for large volumes
- [ ] Mixed precision (FP16/FP32) for memory savings
- [ ] Additional deconvolution methods (Total Variation, Blind deconvolution)
- [ ] Pretrained U-Net models for common cell types

## Citation

If you use this module in research, please cite:

```bibtex
@software{zstack_analyzer_gpu,
  title = {GPU-Accelerated Microscopy Analysis Module},
  author = {Z-Stack Analyzer Team},
  year = {2024},
  url = {https://github.com/your-org/zstack-analyzer}
}
```

## License

Apache 2.0 - See LICENSE file for details.

---

**Questions?** Open an issue or check the [documentation](../docs/).
