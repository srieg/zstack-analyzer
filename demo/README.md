# Demo System - Synthetic Z-Stack Data Generator

This directory contains the synthetic data generation system for creating compelling demo datasets that showcase the platform's capabilities.

## Overview

The demo system generates realistic-looking microscopy data with:
- **Biological accuracy**: Structures that mimic real cellular components
- **Controlled parameters**: Adjustable noise, SNR, and complexity
- **Validated results**: Each dataset includes expected outcomes
- **Performance optimization**: Cached generation for fast loading

## Components

### 1. **generator.py** - Synthetic Data Generator

Core generator class with methods for creating:

#### Cellular Structures
- `generate_nuclei()` - 3D spheroidal nuclei with chromatin texture
- `generate_filaments()` - Microtubules, actin fibers with curvature
- `generate_puncta()` - Vesicles, spots, synaptic markers

#### Image Quality
- `add_poisson_noise()` - Shot noise from photon detection
- `add_gaussian_noise()` - Readout noise from camera
- `add_background()` - Realistic background with gradient
- `apply_psf_blur()` - Anisotropic point spread function

#### Advanced Features
- `generate_colocalization()` - Two channels with controlled overlap
- `generate_time_series()` - 4D data with cell migration

### 2. **datasets.json** - Dataset Configurations

Defines 6 pre-configured demo datasets:

| Dataset | Difficulty | Key Features |
|---------|-----------|--------------|
| Cell Division | Intermediate | Mitotic cells, chromosomes, spindle fibers |
| Neuron Network | Advanced | Branching dendrites, synaptic puncta |
| Colocalization Study | Beginner | Protein interactions, quantitative metrics |
| Low SNR Challenge | Expert | Heavy noise, denoising demonstration |
| Large Volume | Advanced | 200 Z-slices, performance showcase |
| Time Series | Advanced | 4D tracking, cell migration |

Each dataset includes:
- Detailed description and use case
- Expected analysis results
- Showcase features list
- Generation parameters
- Difficulty level and categories

### 3. **API Routes** (`/api/v1/demo/`)

#### `GET /datasets`
List all available demo datasets with metadata.

#### `GET /datasets/{id}/info`
Get detailed information about a specific dataset.

#### `POST /datasets/{id}/load`
Load a demo dataset (generates if needed, caches for performance).
Creates database entry like a real upload.

#### `POST /generate`
Generate custom synthetic data with specified parameters:
```json
{
  "shape": [60, 512, 512],
  "channels": 2,
  "nuclei_count": 20,
  "filament_count": 15,
  "puncta_count": 100,
  "noise_level": "medium",
  "add_background": true,
  "apply_psf": true,
  "seed": 42
}
```

#### `DELETE /cache`
Clear all cached demo datasets.

#### `GET /cache/stats`
Get cache statistics (size, count).

### 4. **Frontend Components**

#### `DemoSelector.tsx`
- Beautiful card grid for dataset selection
- Animated previews and hover effects
- Difficulty indicators and category badges
- One-click loading with progress feedback
- Detailed modal with expected results

#### `Demo.tsx` - Demo Page
- Guided tour with step-by-step walkthrough
- Progress tracking through tour steps
- Dataset loading and result viewing
- Educational features showcase

#### `DemoBanner.tsx`
- Demo mode indicator banner
- Quick exit to real data mode
- Dataset info display
- Comparison widget for demo vs real data

## Usage

### Backend Setup

1. **Start the API server:**
```bash
cd /Users/samriegel/zstack-analyzer
python -m api.main
```

2. **Access demo endpoints:**
```bash
# List datasets
curl http://localhost:8000/api/v1/demo/datasets

# Load a dataset
curl -X POST http://localhost:8000/api/v1/demo/datasets/cell-division/load

# Generate custom data
curl -X POST http://localhost:8000/api/v1/demo/generate \
  -H "Content-Type: application/json" \
  -d '{"shape": [50, 512, 512], "nuclei_count": 20}'
```

### Frontend Usage

1. **Navigate to demo page:**
```
http://localhost:5173/demo
```

2. **Embed demo selector:**
```tsx
import { DemoSelector } from '@/components/DemoSelector';

function MyPage() {
  const handleLoad = (dataset) => {
    console.log('Loaded:', dataset);
    // Navigate to viewer or analysis
  };

  return <DemoSelector onLoad={handleLoad} />;
}
```

3. **Add demo banner:**
```tsx
import { DemoBanner } from '@/components/DemoBanner';

function ViewerPage() {
  return (
    <>
      <DemoBanner
        datasetName="Cell Division"
        onExitDemo={() => navigate('/upload')}
      />
      {/* Your viewer content */}
    </>
  );
}
```

## Generation Parameters

### Nuclei
- **num_nuclei**: Number of cell nuclei (5-200)
- **radius_range**: Min/max radius in pixels
- **intensity_range**: Min/max intensity values
- Creates ellipsoidal Gaussians with chromatin texture

### Filaments
- **num_filaments**: Number of fiber structures (5-100)
- **length_range**: Min/max length in pixels
- **thickness_range**: Min/max thickness in pixels
- Creates curved filaments with Gaussian cross-section

### Puncta
- **num_puncta**: Number of spot-like structures (10-500)
- **radius_range**: Min/max radius in pixels
- Creates small Gaussian spots (vesicles, synapses)

### Noise
- **gaussian_sigma**: Standard deviation of Gaussian noise (200-1200)
- **background_mean**: Mean background intensity (300-800)
- **poisson_scaling**: Poisson noise strength (0.01-0.1)
- **gradient_strength**: Background gradient intensity (0.1-0.5)

### PSF
- **sigma_xy**: Lateral blur (1.0-2.0 pixels)
- **sigma_z**: Axial blur (2.0-4.0 pixels)
- Simulates confocal microscope point spread function

## Cache System

Generated datasets are cached in `demo/cache/` as `.npy` files:

- **Location**: `demo/cache/`
- **Format**: NumPy binary (`.npy`)
- **Naming**: `{dataset-id}.npy` or `custom_{timestamp}.npy`
- **Persistence**: Survives server restarts
- **Management**: Clear via API endpoint or manually delete files

Cache benefits:
- ✅ Instant loading on subsequent requests
- ✅ Reduced CPU usage
- ✅ Consistent data across sessions
- ✅ Fast demo experience

## Performance

### Generation Time
- **Small dataset** (50×512×512): ~1-2 seconds
- **Medium dataset** (100×512×512): ~3-5 seconds
- **Large dataset** (200×512×512): ~8-12 seconds
- **Time series** (10 timepoints): ~10-15 seconds

### Memory Usage
- **Generation**: ~500MB-2GB depending on size
- **Cache storage**: ~10-100MB per dataset (compressed)
- **Total cache**: Typically <1GB for all demo datasets

## Best Practices

1. **First Demo**: Start with "Cell Division" (intermediate, high SNR)
2. **Feature Showcase**: Use "Neuron Network" for complex analysis
3. **Validation**: Use "Colocalization Study" for quantitative metrics
4. **Stress Test**: Use "Large Volume" for performance
5. **Custom Data**: Generate with `seed` parameter for reproducibility

## Adding New Datasets

1. **Define in datasets.json:**
```json
{
  "id": "my-dataset",
  "name": "My Custom Dataset",
  "description": "Description here",
  "difficulty": "intermediate",
  "categories": ["category1", "category2"],
  "shape": [60, 512, 512],
  "channels": 1,
  "channel_names": ["Channel 1"],
  "snr": "high",
  "expected_results": {
    "key": "value"
  },
  "showcase_features": ["feature1", "feature2"],
  "generation_params": {
    // Parameters here
  }
}
```

2. **Test generation:**
```python
from demo.generator import SyntheticDataGenerator

gen = SyntheticDataGenerator(seed=42)
data = gen.generate_nuclei(shape=(60, 512, 512))
# Verify output
```

3. **Update API and frontend** if new structure types needed

## Troubleshooting

### Issue: Slow generation
**Solution**: Check if caching is enabled. First load is slow, subsequent loads use cache.

### Issue: Out of memory
**Solution**: Reduce dataset size or number of structures in generation params.

### Issue: Unrealistic appearance
**Solution**: Adjust noise parameters and PSF blur to match real microscopy.

### Issue: Cache not clearing
**Solution**: Use API endpoint or manually delete `demo/cache/*.npy` files.

## Future Enhancements

- [ ] GPU-accelerated generation (CuPy/Numba)
- [ ] Real microscope PSF models
- [ ] Photobleaching simulation for time series
- [ ] More cell types (neurons, bacteria, yeast)
- [ ] Experimental artifacts (drift, bleaching, vignetting)
- [ ] Integration with real dataset statistics

## Contributing

When adding new synthetic structures:

1. Add generation method to `SyntheticDataGenerator`
2. Document parameters and expected output
3. Add example dataset to `datasets.json`
4. Include expected results for validation
5. Update this README

## References

- **Microscopy noise models**: [Poisson-Gaussian noise in fluorescence microscopy](https://doi.org/10.1109/TIP.2008.2008223)
- **PSF modeling**: [Born and Wolf, Principles of Optics](https://doi.org/10.1017/CBO9781139644181)
- **Synthetic biology images**: [DeepBacs](https://doi.org/10.1101/2020.12.01.407742)
