# Demo System Integration Guide

This guide shows how to integrate the demo system into the existing Z-Stack Analyzer application.

## Quick Start

### 1. Update App Router

Add the Demo page to your routing:

```tsx
// frontend/src/App.tsx
import { Demo } from './pages/Demo';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/demo" element={<Demo />} />  {/* Add this */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/upload" element={<ImageUpload />} />
      <Route path="/viewer/:id" element={<ImageViewer />} />
      <Route path="/analysis/:id" element={<AnalysisResults />} />
    </Routes>
  );
}
```

### 2. Add Demo Link to Navigation

```tsx
// frontend/src/components/Layout.tsx
<nav>
  <Link to="/">Home</Link>
  <Link to="/demo">Try Demo</Link>  {/* Add this */}
  <Link to="/dashboard">Dashboard</Link>
  <Link to="/upload">Upload</Link>
</nav>
```

### 3. Add Demo Banner to Viewer

Show demo mode indicator when viewing synthetic data:

```tsx
// frontend/src/pages/ImageViewer.tsx
import { DemoBanner } from '../components/DemoBanner';
import { useState, useEffect } from 'react';

function ImageViewer() {
  const [imageStack, setImageStack] = useState(null);
  const isDemoData = imageStack?.image_metadata?.demo_dataset === true;

  return (
    <>
      {isDemoData && (
        <DemoBanner
          datasetName={imageStack.image_metadata.dataset_name}
          onExitDemo={() => navigate('/upload')}
          onViewRealData={() => navigate('/upload')}
        />
      )}
      <VolumeViewer data={imageStack} />
    </>
  );
}
```

## Integration Patterns

### Pattern 1: Landing Page CTA

Add a "Try Demo" call-to-action to your landing page:

```tsx
// frontend/src/pages/Landing.tsx
import { DemoComparisonWidget } from '../components/DemoBanner';

function Landing() {
  return (
    <div>
      <h1>Z-Stack Analyzer</h1>
      <p>GPU-accelerated confocal microscopy analysis</p>

      <DemoComparisonWidget
        onChooseDemo={() => navigate('/demo')}
        onChooseReal={() => navigate('/upload')}
      />
    </div>
  );
}
```

### Pattern 2: Inline Demo Selector

Embed the demo selector in your dashboard:

```tsx
// frontend/src/pages/Dashboard.tsx
import { DemoSelector } from '../components/DemoSelector';
import { useState } from 'react';

function Dashboard() {
  const [showDemo, setShowDemo] = useState(false);

  const handleDemoLoad = (dataset) => {
    // Navigate to viewer with loaded demo data
    navigate(`/viewer/${dataset.image_stack.id}`);
  };

  return (
    <div>
      <h2>Your Data</h2>
      {/* Your existing data list */}

      <button onClick={() => setShowDemo(!showDemo)}>
        Try Demo Datasets
      </button>

      {showDemo && (
        <DemoSelector onLoad={handleDemoLoad} />
      )}
    </div>
  );
}
```

### Pattern 3: Demo Mode Indicator

Add a persistent demo indicator when viewing demo data:

```tsx
// frontend/src/App.tsx
import { DemoIndicator } from '../components/DemoBanner';
import { useLocation } from 'react-router-dom';

function App() {
  const location = useLocation();
  const [isDemoMode, setIsDemoMode] = useState(false);

  useEffect(() => {
    // Check if current page is viewing demo data
    const checkDemoMode = async () => {
      if (location.pathname.includes('/viewer/')) {
        const id = location.pathname.split('/').pop();
        const response = await fetch(`/api/v1/images/${id}`);
        const data = await response.json();
        setIsDemoMode(data.image_metadata?.demo_dataset === true);
      }
    };
    checkDemoMode();
  }, [location]);

  return (
    <>
      {isDemoMode && (
        <DemoIndicator
          position="top-right"
          onClick={() => navigate('/demo')}
        />
      )}
      <Routes>
        {/* Your routes */}
      </Routes>
    </>
  );
}
```

## API Integration

### Check if Data is Demo

```typescript
// frontend/src/utils/demo.ts
export const isDemoData = (imageStack: any): boolean => {
  return imageStack?.image_metadata?.demo_dataset === true;
};

export const getDemoDatasetName = (imageStack: any): string | null => {
  if (!isDemoData(imageStack)) return null;
  return imageStack.image_metadata?.dataset_name || 'Demo Dataset';
};

export const getExpectedResults = (imageStack: any): Record<string, string> | null => {
  if (!isDemoData(imageStack)) return null;
  return imageStack.image_metadata?.expected_results || null;
};
```

### Load Demo Dataset Programmatically

```typescript
// frontend/src/services/demo.ts
export class DemoService {
  static async listDatasets() {
    const response = await fetch('/api/v1/demo/datasets');
    if (!response.ok) throw new Error('Failed to fetch datasets');
    return response.json();
  }

  static async loadDataset(datasetId: string) {
    const response = await fetch(`/api/v1/demo/datasets/${datasetId}/load`, {
      method: 'POST'
    });
    if (!response.ok) throw new Error('Failed to load dataset');
    return response.json();
  }

  static async generateCustom(params: CustomGenerationRequest) {
    const response = await fetch('/api/v1/demo/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!response.ok) throw new Error('Failed to generate dataset');
    return response.json();
  }

  static async getCacheStats() {
    const response = await fetch('/api/v1/demo/cache/stats');
    if (!response.ok) throw new Error('Failed to get cache stats');
    return response.json();
  }

  static async clearCache() {
    const response = await fetch('/api/v1/demo/cache', {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to clear cache');
    return response.json();
  }
}
```

### Usage Example

```typescript
import { DemoService } from '../services/demo';

// List all demo datasets
const datasets = await DemoService.listDatasets();

// Load a specific dataset
const result = await DemoService.loadDataset('cell-division');
console.log('Loaded:', result.image_stack.id);

// Navigate to viewer
navigate(`/viewer/${result.image_stack.id}`);

// Generate custom dataset
const custom = await DemoService.generateCustom({
  shape: [60, 512, 512],
  channels: 2,
  nuclei_count: 25,
  filament_count: 15,
  noise_level: 'medium'
});
```

## Result Validation

Show expected vs actual results for demo data:

```tsx
// frontend/src/pages/AnalysisResults.tsx
import { useState, useEffect } from 'react';
import { isDemoData, getExpectedResults } from '../utils/demo';

function AnalysisResults() {
  const [imageStack, setImageStack] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const expectedResults = getExpectedResults(imageStack);

  return (
    <div>
      <h2>Analysis Results</h2>

      {/* Your actual results */}
      <div>
        <h3>Detected</h3>
        <p>Nuclei: {analysisResults.nuclei_count}</p>
        <p>Filaments: {analysisResults.filament_length} px</p>
      </div>

      {/* Expected results for demo data */}
      {expectedResults && (
        <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg mt-4">
          <h3>Expected Results (Demo Data)</h3>
          {Object.entries(expectedResults).map(([key, value]) => (
            <p key={key}>
              {key}: <span className="font-semibold">{value}</span>
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
```

## Advanced: Custom Demo Datasets

Create your own demo datasets programmatically:

```python
# scripts/create_custom_demo.py
from demo.generator import SyntheticDataGenerator
import numpy as np

gen = SyntheticDataGenerator(seed=42)

# Generate multi-structure dataset
shape = (80, 512, 512)
nuclei = gen.generate_nuclei(shape, num_nuclei=30)
filaments = gen.generate_filaments(shape, num_filaments=20)
puncta = gen.generate_puncta(shape, num_puncta=150)

# Combine structures
channel1 = nuclei + filaments
channel2 = puncta

# Add realistic artifacts
channel1 = gen.add_background(channel1, mean=500)
channel1 = gen.add_gaussian_noise(channel1, sigma=400)
channel1 = gen.apply_psf_blur(channel1)

channel2 = gen.add_background(channel2, mean=450)
channel2 = gen.add_gaussian_noise(channel2, sigma=350)
channel2 = gen.apply_psf_blur(channel2)

# Stack and save
data = np.stack([channel1, channel2], axis=0)
np.save('demo/cache/my-custom-dataset.npy', data)

print(f"Created dataset with shape: {data.shape}")
print(f"Data type: {data.dtype}")
print(f"Value range: {data.min()} - {data.max()}")
```

Add to `datasets.json`:

```json
{
  "id": "my-custom-dataset",
  "name": "My Custom Dataset",
  "description": "Custom synthetic dataset with specific structures",
  "difficulty": "intermediate",
  "categories": ["nuclei", "filaments", "puncta"],
  "shape": [80, 512, 512],
  "channels": 2,
  "channel_names": ["DAPI + Tubulin", "Synapsin"],
  "snr": "medium",
  "expected_results": {
    "nuclei_count": "~30 cells",
    "filament_length": "~2000 pixels",
    "puncta_count": "~150 spots"
  },
  "showcase_features": [
    "Multi-structure analysis",
    "Channel separation",
    "Quantitative metrics"
  ]
}
```

## Testing

### Frontend Testing

```typescript
// frontend/src/components/__tests__/DemoSelector.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { DemoSelector } from '../DemoSelector';

test('loads and displays demo datasets', async () => {
  const mockOnLoad = jest.fn();

  render(<DemoSelector onLoad={mockOnLoad} />);

  await waitFor(() => {
    expect(screen.getByText('Cell Division')).toBeInTheDocument();
    expect(screen.getByText('Neuron Network')).toBeInTheDocument();
  });
});
```

### Backend Testing

```python
# tests/test_demo_api.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_list_demo_datasets():
    response = client.get("/api/v1/demo/datasets")
    assert response.status_code == 200
    datasets = response.json()
    assert len(datasets) > 0
    assert "cell-division" in [d["id"] for d in datasets]

def test_load_demo_dataset():
    response = client.post("/api/v1/demo/datasets/cell-division/load")
    assert response.status_code == 200
    data = response.json()
    assert "image_stack" in data
    assert data["image_stack"]["processing_status"] == "demo_loaded"

def test_generate_custom():
    params = {
        "shape": [50, 512, 512],
        "channels": 1,
        "nuclei_count": 15,
        "noise_level": "medium"
    }
    response = client.post("/api/v1/demo/generate", json=params)
    assert response.status_code == 200
```

## Performance Optimization

### Lazy Loading

```tsx
// Only load demo components when needed
const DemoSelector = lazy(() => import('../components/DemoSelector'));

function Dashboard() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <DemoSelector onLoad={handleLoad} />
    </Suspense>
  );
}
```

### Preload Popular Datasets

```python
# scripts/preload_demo_cache.py
import asyncio
from demo.generator import SyntheticDataGenerator
import numpy as np
import json

async def preload_cache():
    """Preload popular demo datasets into cache."""
    with open('demo/datasets.json') as f:
        config = json.load(f)

    popular = ['cell-division', 'neuron-network', 'colocalization-study']

    for dataset_id in popular:
        dataset = next(d for d in config['datasets'] if d['id'] == dataset_id)
        print(f"Generating {dataset_id}...")

        # Generate dataset using config
        # ... (generation code)

        cache_file = f"demo/cache/{dataset_id}.npy"
        np.save(cache_file, data)
        print(f"✓ Cached {dataset_id}")

if __name__ == "__main__":
    asyncio.run(preload_cache())
```

Run on deployment:

```bash
# In Dockerfile or startup script
python scripts/preload_demo_cache.py
```

## Troubleshooting

### Issue: Demo components not rendering
**Check**: Are framer-motion and lucide-react installed?
```bash
npm install framer-motion lucide-react
```

### Issue: API 404 on demo endpoints
**Check**: Is demo router registered in `api/main.py`?
```python
app.include_router(demo.router, prefix="/api/v1/demo", tags=["demo"])
```

### Issue: Slow first load
**Expected**: First generation takes 3-10 seconds. Subsequent loads use cache.
**Solution**: Preload cache on deployment (see above).

### Issue: Demo banner not showing
**Check**: Is `demo_dataset: true` in image metadata?
```typescript
console.log(imageStack.image_metadata?.demo_dataset);
```

## Best Practices

1. **Always validate demo data**: Check `demo_dataset` flag before showing demo UI
2. **Provide exit path**: Always offer way to switch to real data upload
3. **Show expected results**: Help users validate that analysis is working correctly
4. **Cache aggressively**: Demo data is deterministic, cache everything
5. **Progressive disclosure**: Start with simple demos, offer advanced as needed

## Next Steps

- Add more demo datasets for specific use cases
- Integrate with analysis pipeline to show real-time processing
- Add export functionality to download demo results
- Create video tutorials using demo data
- Build interactive tour system with tooltips
