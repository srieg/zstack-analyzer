# Demo System Quick Start

Get the demo system running in 5 minutes!

## Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend)
- numpy, scipy, fastapi installed

## Step 1: Verify Installation

```bash
cd /Users/samriegel/zstack-analyzer
python demo/setup.py
```

This will check all dependencies and create necessary directories.

## Step 2: Start the Backend

```bash
# From project root
python -m api.main
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 3: Test the API

Open a new terminal:

```bash
# List available datasets
curl http://localhost:8000/api/v1/demo/datasets

# Load a dataset
curl -X POST http://localhost:8000/api/v1/demo/datasets/cell-division/load
```

Expected response:
```json
{
  "message": "Demo dataset loaded successfully",
  "image_stack": { ... },
  "data_shape": [2, 60, 512, 512],
  "cached": false
}
```

## Step 4: Start the Frontend

```bash
cd frontend
npm install  # If not already installed
npm run dev
```

You should see:
```
VITE ready in 500ms
Local: http://localhost:5173
```

## Step 5: Open the Demo Page

Navigate to: http://localhost:5173/demo

You should see:
- Beautiful card grid with 6 datasets
- Animated cards with hover effects
- Difficulty indicators
- "Load" buttons

## Step 6: Try a Demo

1. Click "Load" on "Cell Division"
2. Wait 1-2 seconds (first time generates data)
3. See success message with dataset info
4. Click "View in 3D" (if implemented)

## Troubleshooting

### "Module not found: demo"
**Solution**: Make sure you're in the project root directory:
```bash
cd /Users/samriegel/zstack-analyzer
```

### "Port 8000 already in use"
**Solution**: Kill existing process:
```bash
lsof -ti:8000 | xargs kill -9
```

### "Failed to fetch demo datasets"
**Solution**: Check that backend is running:
```bash
curl http://localhost:8000/health
```

### Slow generation
**Solution**: Normal for first load. Subsequent loads use cache (<100ms).

### Frontend not loading
**Solution**: Check for errors:
```bash
cd frontend
npm run build  # Check for TypeScript errors
```

## Next Steps

### Try All Datasets

1. **Beginner**: Start with "Colocalization Study"
2. **Intermediate**: Try "Cell Division"
3. **Advanced**: Explore "Neuron Network" or "Large Volume"
4. **Expert**: Challenge yourself with "Low SNR Challenge"

### Customize Generation

Create custom datasets via API:

```bash
curl -X POST http://localhost:8000/api/v1/demo/generate \
  -H "Content-Type: application/json" \
  -d '{
    "shape": [50, 512, 512],
    "channels": 2,
    "nuclei_count": 25,
    "filament_count": 15,
    "noise_level": "medium"
  }'
```

### Integrate with Your App

See `INTEGRATION.md` for detailed integration patterns.

### Add Custom Datasets

1. Edit `demo/datasets.json`
2. Add your dataset configuration
3. Restart backend
4. New dataset appears in UI

## Quick Reference

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/demo/datasets` | GET | List all |
| `/api/v1/demo/datasets/{id}/info` | GET | Get details |
| `/api/v1/demo/datasets/{id}/load` | POST | Load/generate |
| `/api/v1/demo/generate` | POST | Custom generation |
| `/api/v1/demo/cache/stats` | GET | Cache stats |
| `/api/v1/demo/cache` | DELETE | Clear cache |

### File Locations

```
/Users/samriegel/zstack-analyzer/
├── demo/
│   ├── generator.py          # Synthetic data generator
│   ├── datasets.json          # Dataset configs
│   ├── cache/                 # Generated data cache
│   └── *.md                   # Documentation
├── api/
│   └── routes/
│       └── demo.py            # API endpoints
└── frontend/
    └── src/
        ├── components/
        │   ├── DemoSelector.tsx
        │   └── DemoBanner.tsx
        └── pages/
            └── Demo.tsx
```

### Component Usage

```tsx
// In your React component
import { DemoSelector, DemoBanner } from '@/components';

function MyPage() {
  return (
    <>
      <DemoBanner datasetName="Cell Division" />
      <DemoSelector onLoad={(dataset) => console.log(dataset)} />
    </>
  );
}
```

## Performance Tips

1. **Preload cache**: Run popular datasets once
2. **Use production build**: `npm run build` for frontend
3. **Enable compression**: gzip responses
4. **Use CDN**: Serve static assets
5. **Cache headers**: Set appropriate cache TTL

## Support

- **Documentation**: See `README.md`, `INTEGRATION.md`, `SHOWCASE.md`
- **Setup issues**: Run `python demo/setup.py`
- **API issues**: Check `curl http://localhost:8000/docs`
- **Frontend issues**: Check browser console

## Success Indicators

✅ Backend running on port 8000
✅ Frontend running on port 5173
✅ API returns dataset list
✅ Demo page loads with cards
✅ Dataset loads in <2 seconds
✅ Cache working (second load <100ms)

If all above are true, you're ready to demo! 🎉

---

**Pro tip**: Keep both terminal windows open (backend + frontend) for easy debugging.
